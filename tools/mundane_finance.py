"""Build data/mundane/finance.json, the Research tab's Finance database: the world's listed companies by market value and the
largest private ones (unicorns), each with its listings (exchange, ticker, first trading day), its founding and a short biography.

Re-runnable: .venv/bin/python -I tools/mundane_finance.py [stage]. Every download is cached in databases/raw/finance/ (git-ignored);
delete a file there to fetch it again. Wikimedia rate-limits hard (the query service to one query a minute), so a first run takes
about an hour; later runs only rebuild. Stages: fetch-yahoo, fetch-wiki, fetch-exchanges, build (default: all of them in turn).

A listing's first trading day comes from, in order of trust: the exchange's own list (NSE, TWSE, KRX, SSE, SZSE), Wikidata (the
listing's start time, day precision only), then Yahoo Finance's first trading day, only for the exchanges and years where it agrees
with the other two (calibrate()). Its time is the exchange's opening time; the minute of the first trade is seldom recorded.
"""
from __future__ import annotations

import csv
import hashlib
import html
import http.cookiejar
import io
import json
import re
import sqlite3
import sys
import threading
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timezone
from pathlib import Path
from xml.etree import ElementTree as ET
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "databases" / "raw" / "finance"
OUT = ROOT / "data" / "mundane" / "finance.json"
REPORT = ROOT / "data" / "mundane" / "FINANCE.md"
UA = "SudarshanaResearch/0.1 (research database builder; python-urllib)"
GAP = {"query.wikidata.org": 65.0, "en.wikipedia.org": 4.0, "www.wikidata.org": 4.0}   # seconds between calls to a host
CMC = "https://companiesmarketcap.com/?download=csv"
CBI = "https://www.cbinsights.com/research-unicorn-companies"
WIKI_API = "https://en.wikipedia.org/w/api.php"
WDQS = "https://query.wikidata.org/sparql"
MAJOR = "https://en.wikipedia.org/wiki/List_of_major_stock_exchanges"

# --- downloads --------------------------------------------------------------------------------------------------------

_last: dict[str, float] = {}
_lock = threading.Lock()


def get(url: str, data: bytes | None = None, headers: dict | None = None, opener=None, tries: int = 7) -> bytes:
    """A polite GET (or POST with ``data``): one host's calls spaced by GAP, a 429 or 5xx waited out and retried."""
    host = urllib.parse.urlsplit(url).hostname or ""
    for i in range(tries):
        with _lock:
            wait = GAP.get(host, 0.0) - (time.time() - _last.get(host, 0.0))
            _last[host] = time.time() + max(wait, 0.0)
        if wait > 0:
            time.sleep(wait)
        req = urllib.request.Request(url, data=data, headers={"User-Agent": UA, **(headers or {})})
        try:
            with (opener or urllib.request.build_opener()).open(req, timeout=300) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504) and i < tries - 1:
                time.sleep(min(float(e.headers.get("Retry-After") or 0) or 20.0 * (i + 1), 300))
                continue
            raise
        except (urllib.error.URLError, TimeoutError, ConnectionError):
            if i < tries - 1:
                time.sleep(10.0 * (i + 1))
                continue
            raise
    raise RuntimeError(url)


def cached(name: str, url: str, **kw) -> bytes:
    path = RAW / name
    if not path.exists():
        RAW.mkdir(parents=True, exist_ok=True)
        body = get(url, **kw)
        path.write_bytes(body)
    return path.read_bytes()


def sparql(name: str, query: str) -> list[dict]:
    body = cached(f"wd_{name}.csv", WDQS, data=urllib.parse.urlencode({"query": query}).encode(), headers={"Accept": "text/csv"})
    if body.lstrip().startswith(b"<"):
        (RAW / f"wd_{name}.csv").unlink()
        raise RuntimeError(f"query service refused {name}: {body[:200]!r}")
    return list(csv.DictReader(io.StringIO(body.decode("utf-8"))))


def wiki_page(title: str) -> str:
    """A Wikipedia page's rendered HTML."""
    q = urllib.parse.urlencode({"action": "parse", "page": title, "prop": "text", "format": "json", "formatversion": 2, "redirects": 1})
    name = "wiki_" + re.sub(r"[^A-Za-z0-9]+", "_", title) + ".json"
    body = json.loads(cached(name, f"{WIKI_API}?{q}"))
    if "parse" not in body:
        (RAW / name).unlink()
        raise RuntimeError(f"Wikipedia: {title}: {body}")
    return body["parse"]["text"]


def wiki_qids(titles: list[str]) -> dict[str, str]:
    """Wikipedia titles to their Wikidata items, following redirects; a disambiguation page has none."""
    path = RAW / "wiki_qids.json"
    known: dict[str, str | None] = json.loads(path.read_text()) if path.exists() else {}
    todo = [t for t in dict.fromkeys(titles) if t and t not in known]
    for i in range(0, len(todo), 50):
        batch = todo[i:i + 50]
        q = urllib.parse.urlencode({"action": "query", "titles": "|".join(batch), "redirects": 1, "prop": "pageprops",
                                    "ppprop": "wikibase_item|disambiguation", "format": "json", "formatversion": 2})
        body = json.loads(get(f"{WIKI_API}?{q}"))["query"]
        hop = {}
        for k in ("normalized", "redirects"):
            for x in body.get(k, []):
                hop[x["from"]] = x["to"]
        item = {p["title"]: (None if "disambiguation" in p.get("pageprops", {}) else p.get("pageprops", {}).get("wikibase_item")) for p in body.get("pages", [])}
        for t in batch:
            u = t
            for _ in range(3):
                u = hop.get(u, u)
            known[t] = item.get(u)
        path.write_text(json.dumps(known, ensure_ascii=False))
    return {t: known[t] for t in titles if known.get(t)}


# --- sources ------------------------------------------------------------------------------------------------------------

def market_caps() -> list[dict]:
    """companiesmarketcap.com's list of every listed company it tracks, largest first: rank, name, Yahoo symbol, market value, country."""
    rows = csv.DictReader(io.StringIO(cached("companiesmarketcap.csv", CMC).decode("utf-8-sig")))
    return [{"rank": int(r["Rank"]), "name": r["Name"].strip(), "symbol": r["Symbol"].strip(), "mcap": float(r["marketcap"] or 0),
             "country": r["country"].strip()} for r in rows if r.get("Symbol")]


def unicorns() -> list[dict]:
    """CB Insights' list of private companies valued at $1 billion or more."""
    t = cached("cbinsights_unicorns.html", CBI).decode("utf-8", "replace")
    out = []
    for row in re.findall(r"<tr[^>]*>(.*?)</tr>", t, re.S)[1:]:
        c = [_text(x) for x in re.findall(r"<td[^>]*>(.*?)</td>", row, re.S)]
        if len(c) >= 7 and c[0]:
            m, d, y = (int(x) for x in c[2].split("/")) if re.fullmatch(r"\d+/\d+/\d{4}", c[2]) else (0, 0, 0)
            out.append({"name": c[0], "valuation": float(re.sub(r"[^\d.]", "", c[1]) or 0) * 1e9, "joined": f"{y:04d}-{m:02d}-{d:02d}" if y else None,
                        "country": c[3], "city": c[4], "industry": c[5], "investors": c[6]})
    return out


def _text(s: str) -> str:
    s = re.sub(r"<sup[^>]*>.*?</sup>", "", s, flags=re.S)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s))).strip()


def _link(s: str) -> str | None:
    m = re.search(r'<a href="/wiki/[^"#]+"[^>]*title="([^"]+)"', s)
    return html.unescape(m.group(1)) if m else None


def wiki_tables(page_html: str) -> list[list[list[tuple[str, str | None]]]]:
    """Every wikitable: rows of (text, first link title) cells, the header row first."""
    out = []
    for tb in re.findall(r"<table[^>]*wikitable.*?</table>", page_html, re.S):
        rows = [[(_text(c), _link(c)) for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", r, re.S)] for r in re.findall(r"<tr[^>]*>(.*?)</tr>", tb, re.S)]
        out.append([r for r in rows if r])
    return out


# index: (page, how its members are listed); a table's company column holds the link, a navbox's list items do
INDICES = {
    "S&P 500": ("List of S&P 500 companies", "table"), "Nasdaq-100": ("Template:Nasdaq-100", "navbox"),
    "Dow Jones": ("Template:Dow Jones Industrial Average companies", "navbox"), "FTSE 100": ("FTSE 100 Index", "table"),
    "DAX": ("DAX", "table"), "CAC 40": ("CAC 40", "table"), "Euro Stoxx 50": ("Euro Stoxx 50", "table"), "Hang Seng": ("Hang Seng Index", "table"),
    "Nifty 50": ("NIFTY 50", "table"), "Sensex": ("BSE SENSEX", "table"), "S&P/TSX 60": ("S&P/TSX 60", "table"), "S&P/ASX 50": ("S&P/ASX 50", "table"),
    "SMI": ("Swiss Market Index", "table"), "AEX": ("AEX index", "table"), "IBEX 35": ("IBEX 35", "table"), "FTSE MIB": ("FTSE MIB", "table"),
    "OMX Stockholm 30": ("OMX Stockholm 30", "table"), "Nikkei 225": ("Template:Nikkei 225", "navbox"),
}
COMPANY_COL = ("company", "security", "name", "constituent", "company name")
# the Yahoo suffixes an index's bare tickers are on ('' the US markets; a Canadian company may be listed by its US ticker)
INDEX_MARKETS = {"S&P 500": ("",), "FTSE 100": ("L",), "Nifty 50": ("NS",), "Sensex": ("NS", "BO"), "S&P/TSX 60": ("TO", ""),
                 "S&P/ASX 50": ("AX",), "SMI": ("SW",), "AEX": ("AS",), "IBEX 35": ("MC",), "FTSE MIB": ("MI",),
                 "OMX Stockholm 30": ("ST",), "Hang Seng": ("HK",), "DAX": ("DE",), "CAC 40": ("PA",)}


def index_members() -> dict[str, list[dict]]:
    """Each index's members as {title, ticker, founded (S&P 500, DAX), sector}: from its constituents table or its navbox."""
    out = {}
    for name, (page, how) in INDICES.items():
        try:
            text = wiki_page(page)
        except (RuntimeError, urllib.error.HTTPError) as e:
            print(f"  {name}: {e}", file=sys.stderr)
            continue
        members = []
        if how == "navbox":
            box = text.split('class="navbox-list', 1)[-1]
            members = [{"title": html.unescape(t)} for t in re.findall(r'<li><a href="/wiki/[^"#]+"[^>]*title="([^"]+)"', box)]
        else:
            best = None
            for tb in wiki_tables(text):
                head = [h.lower() for h, _ in tb[0]]
                col = next((i for i, h in enumerate(head) if h.split("[")[0].strip() in COMPANY_COL), None)
                if col is not None and len(tb) > 20 and (best is None or len(tb) > len(best[0])):
                    best = (tb, col, head)
            if best:
                tb, col, head = best
                tick = next((i for i, h in enumerate(head) if h.startswith(("symbol", "ticker", "epic", "code"))), None)
                found = next((i for i, h in enumerate(head) if h.startswith("founded")), None)
                for r in tb[1:]:
                    if len(r) == len(head) and r[col][1]:
                        members.append({"title": r[col][1], "ticker": r[tick][0] if tick is not None else None,
                                        "founded": r[found][0] if found is not None else None})
        print(f"  {name}: {len(members)} members", file=sys.stderr)
        if members:
            out[name] = members
    return out


BIG_LISTS = ("List of largest companies by revenue", "List of largest private non-governmental companies by revenue")


def big_companies() -> list[dict]:
    """The largest companies by revenue, and the largest private ones: name, article, industry, revenue in US$, headquarters."""
    out = []
    for page in BIG_LISTS:
        for tb in wiki_tables(wiki_page(page)):
            head = [h.lower() for h, _ in tb[0]]
            col = next((i for i, h in enumerate(head) if h.split("[")[0].strip() in COMPANY_COL), None)
            rev = next((i for i, h in enumerate(head) if h.startswith("revenue")), None)
            if col is None or rev is None or len(tb) < 10:
                continue
            unit = 1e6 if "million" in head[rev] else 1e9
            ind = next((i for i, h in enumerate(head) if h.startswith("industry")), None)
            hq = next((i for i, h in enumerate(head) if h.startswith("headquarters")), None)
            for r in tb[1:]:
                if len(r) == len(head) and r[col][1]:
                    n = re.sub(r"[^\d.]", "", r[rev][0].split("[")[0])
                    out.append({"name": r[col][0], "title": r[col][1], "industry": r[ind][0] if ind is not None else None,
                                "revenue": float(n) * unit if n else None, "hq": r[hq][0] if hq is not None else None, "list": page})
    return out


def unicorn_titles() -> list[dict]:
    """Wikipedia's list of unicorn startups: the companies' articles."""
    out = []
    for tb in wiki_tables(wiki_page("List of unicorn startup companies")):
        head = [h.lower() for h, _ in tb[0]]
        if head and head[0].startswith("company"):
            out += [{"name": r[0][0], "title": r[0][1]} for r in tb[1:] if r and r[0][1]]
    return out


def official_dates() -> dict[tuple[str, str], tuple[str, str]]:
    """(MIC, code) -> (first trading day, source) from the exchanges' own lists."""
    out: dict[tuple[str, str], tuple[str, str]] = {}
    nse = cached("nse_equity_l.csv", "https://archives.nseindia.com/content/equities/EQUITY_L.csv", headers={"User-Agent": "Mozilla/5.0"})
    for r in csv.DictReader(io.StringIO(nse.decode("utf-8", "replace"))):
        r = {k.strip(): (v or "").strip() for k, v in r.items()}
        try:
            out[("XNSE", r["SYMBOL"])] = (datetime.strptime(r["DATE OF LISTING"], "%d-%b-%Y").date().isoformat(), "NSE equity list")
        except ValueError:
            pass
    # shortcut: the TPEx list (strMode=4) takes minutes to send, so its few companies rely on Wikidata and Yahoo; add it if they matter
    page = cached("twse_2.html", "https://isin.twse.com.tw/isin/C_public.jsp?strMode=2", headers={"User-Agent": "Mozilla/5.0"}).decode("big5", "replace")
    for row in re.findall(r"<tr>(.*?)</tr>", page, re.S):
        c = [_text(x) for x in re.findall(r"<td[^>]*>(.*?)</td>", row, re.S)]
        m = re.match(r"(\w+)[\s　]", c[0]) if c else None
        if m and len(c) > 3 and re.fullmatch(r"\d{4}/\d\d/\d\d", c[2]):
            out[("XTAI", m.group(1))] = (c[2].replace("/", "-"), "TWSE ISIN list")
    kind = cached("krx_kind.html", "https://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13", headers={"User-Agent": "Mozilla/5.0"}).decode("euc-kr", "replace")
    for row in re.findall(r"<tr>(.*?)</tr>", kind, re.S):
        c = [_text(x) for x in re.findall(r"<td[^>]*>(.*?)</td>", row, re.S)]
        if len(c) >= 6 and re.fullmatch(r"\d{4}-\d\d-\d\d", c[5]):
            mic = {"유가": "XKRX", "유가증권": "XKRX", "코스닥": "XKOS"}.get(c[1])
            if mic:
                out[(mic, c[2])] = (c[5], "KRX KIND list")
    for kind_ in ("1", "8"):   # main board, STAR market
        url = ("https://query.sse.com.cn/sseQuery/commonQuery.do?STOCK_TYPE=" + kind_ + "&REG_PROVINCE=&CSRC_CODE=&STOCK_CODE=&sqlId=COMMON_SSE_CP_GPJCTPZ_GPLB_GP_L"
               "&COMPANY_STATUS=2,4,5,7,8&type=inParams&isPagination=true&pageHelp.cacheSize=1&pageHelp.beginPage=1&pageHelp.pageSize=5000&pageHelp.pageNo=1&pageHelp.endPage=1")
        for r in json.loads(cached(f"sse_{kind_}.json", url, headers={"User-Agent": "Mozilla/5.0", "Referer": "https://www.sse.com.cn/"}))["result"]:
            d = r.get("LIST_DATE", "")
            if re.fullmatch(r"\d{8}", d):
                out[("XSHG", r["A_STOCK_CODE"])] = (f"{d[:4]}-{d[4:6]}-{d[6:]}", "SSE company list")
    for r in xlsx_rows(cached("szse.xlsx", "https://www.szse.cn/api/report/ShowReport?SHOWTYPE=xlsx&CATALOGID=1110&TABKEY=tab1", headers={"User-Agent": "Mozilla/5.0"}))[1:]:
        if len(r) > 6 and re.fullmatch(r"\d{4}-\d\d-\d\d", r[6]):
            out[("XSHE", r[4])] = (r[6], "SZSE company list")
    return {(mic, norm_ticker(code)): v for (mic, code), v in out.items() if not v[0].endswith("-01-01")}   # 1 January: a placeholder


def xlsx_rows(body: bytes) -> list[list[str]]:
    """The first sheet of an .xlsx as rows of strings (no openpyxl here)."""
    ns = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
    z = zipfile.ZipFile(io.BytesIO(body))
    shared = ["".join(t.text or "" for t in si.iter(ns + "t")) for si in ET.fromstring(z.read("xl/sharedStrings.xml")).iter(ns + "si")] \
        if "xl/sharedStrings.xml" in z.namelist() else []
    rows = []
    for r in ET.fromstring(z.read("xl/worksheets/sheet1.xml")).iter(ns + "row"):
        cells = []
        for c in r.iter(ns + "c"):
            v = c.find(ns + "v")
            cells.append(shared[int(v.text)] if c.get("t") == "s" and v is not None else "".join(t.text or "" for t in c.iter(ns + "t")) if c.get("t") == "inlineStr" else (v.text if v is not None else ""))
        rows.append(cells)
    return rows


# --- Yahoo Finance profiles ------------------------------------------------------------------------------------------------

def yahoo_profiles(symbols: list[str], workers: int = 4, fetch: bool = True) -> dict[str, dict]:
    """Each symbol's Yahoo profile: name, exchange, zone, first trading day, sector, industry, city, employees, website, summary.
    Without ``fetch``, only the profiles already cached."""
    path = RAW / "yahoo.jsonl"
    have = {}
    if path.exists():
        for line in path.read_text().splitlines():
            x = json.loads(line)
            have[x["sym"]] = x
    todo = [s for s in dict.fromkeys(symbols) if s not in have] if fetch else []
    if todo:
        jar = http.cookiejar.CookieJar()
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
        hdr = {"User-Agent": "Mozilla/5.0"}
        try:
            opener.open(urllib.request.Request("https://fc.yahoo.com", headers=hdr), timeout=30)
        except urllib.error.HTTPError:
            pass   # a 404 that still sets the cookie
        crumb = opener.open(urllib.request.Request("https://query2.finance.yahoo.com/v1/test/getcrumb", headers=hdr), timeout=30).read().decode()
        out = open(path, "a")

        def one(sym: str) -> None:
            url = (f"https://query2.finance.yahoo.com/v10/finance/quoteSummary/{urllib.parse.quote(sym)}"
                   f"?modules=assetProfile,quoteType&crumb={urllib.parse.quote(crumb)}")
            rec = {"sym": sym}
            for attempt in range(6):
                try:
                    d = json.loads(opener.open(urllib.request.Request(url, headers=hdr), timeout=60).read())["quoteSummary"]["result"][0]
                    a, q = d.get("assetProfile") or {}, d.get("quoteType") or {}
                    first = q.get("firstTradeDateEpochUtc")
                    rec.update({"name": q.get("longName") or q.get("shortName"), "exchange": q.get("exchange"), "zone": q.get("timeZoneFullName"),
                                "first": first, "city": a.get("city"), "state": a.get("state"), "country": a.get("country"),
                                "sector": a.get("sector"), "industry": a.get("industry"), "employees": a.get("fullTimeEmployees"),
                                "website": a.get("website"), "summary": _sentences(a.get("longBusinessSummary") or "", 2)})
                    break
                except urllib.error.HTTPError as e:
                    if e.code == 404:
                        rec["error"] = 404
                        break
                    time.sleep(15 * (attempt + 1))
                except (urllib.error.URLError, TimeoutError, ConnectionError, json.JSONDecodeError, KeyError, IndexError, TypeError):
                    time.sleep(5 * (attempt + 1))
            else:
                return   # left for the next run
            with _lock:
                out.write(json.dumps(rec, ensure_ascii=False) + "\n")
                out.flush()
                have[sym] = rec
                if len(have) % 500 == 0:
                    print(f"  yahoo: {len(have)} of {len(symbols)}", file=sys.stderr)

        with ThreadPoolExecutor(workers) as pool:
            list(pool.map(one, todo))
        out.close()
    return have


def _sentences(s: str, n: int, cap: int = 320) -> str:
    """The first n sentences, at most ``cap`` characters."""
    parts = re.split(r"(?<=[a-z0-9)][.!?])\s+(?=[A-Z])", s.strip())
    out = " ".join(parts[:n])
    return out if len(out) <= cap else out[:cap].rsplit(" ", 1)[0] + "…"


# --- Wikidata ---------------------------------------------------------------------------------------------------------------

LISTED = "{ SELECT DISTINCT ?c WHERE { ?c p:P414 [] } }"


def wd_queries(subject: str) -> dict[str, str]:
    """The detail queries for a set of items (``subject`` binds ?c)."""
    return {
        "basics": f"""SELECT ?c ?label ?desc ?article WHERE {{ {subject}
            OPTIONAL {{ ?c rdfs:label ?label FILTER(LANG(?label) = "en") }}
            OPTIONAL {{ ?c schema:description ?desc FILTER(LANG(?desc) = "en") }}
            OPTIONAL {{ ?article schema:about ?c ; schema:isPartOf <https://en.wikipedia.org/> }} }}""",
        "founding": f"""SELECT ?c ?inc ?prec ?fl ?flLabel ?flCoord ?diss WHERE {{ {subject}
            OPTIONAL {{ ?c p:P571 ?s . ?s a wikibase:BestRank ; psv:P571 [ wikibase:timeValue ?inc ; wikibase:timePrecision ?prec ] }}
            OPTIONAL {{ ?c wdt:P740 ?fl . OPTIONAL {{ ?fl wdt:P625 ?flCoord }} OPTIONAL {{ ?fl rdfs:label ?flLabel FILTER(LANG(?flLabel) = "en") }} }}
            OPTIONAL {{ ?c wdt:P576 ?diss }} }}""",
        "hq": f"""SELECT ?c ?hq ?hqLabel ?hqCoord ?iso ?countryLabel WHERE {{ {subject}
            OPTIONAL {{ ?c wdt:P159 ?hq . OPTIONAL {{ ?hq wdt:P625 ?hqCoord }} OPTIONAL {{ ?hq rdfs:label ?hqLabel FILTER(LANG(?hqLabel) = "en") }} }}
            OPTIONAL {{ ?c wdt:P17 ?country . OPTIONAL {{ ?country wdt:P297 ?iso }} OPTIONAL {{ ?country rdfs:label ?countryLabel FILTER(LANG(?countryLabel) = "en") }} }} }}""",
        "people": f"""SELECT ?c (GROUP_CONCAT(DISTINCT ?indL; separator="|") AS ?industries) (GROUP_CONCAT(DISTINCT ?fL; separator="|") AS ?founders)
            (GROUP_CONCAT(DISTINCT ?typeL; separator="|") AS ?types) WHERE {{ {subject}
            OPTIONAL {{ ?c wdt:P452 ?ind . ?ind rdfs:label ?indL FILTER(LANG(?indL) = "en") }}
            OPTIONAL {{ ?c wdt:P112 ?f . ?f rdfs:label ?fL FILTER(LANG(?fL) = "en") }}
            OPTIONAL {{ ?c wdt:P31 ?type . ?type rdfs:label ?typeL FILTER(LANG(?typeL) = "en") }} }} GROUP BY ?c""",
        "misc": f"""SELECT ?c (MAX(?e) AS ?emp) (SAMPLE(?s) AS ?site) WHERE {{ {subject}
            OPTIONAL {{ ?c wdt:P1128 ?e }} OPTIONAL {{ ?c wdt:P856 ?s }} }} GROUP BY ?c""",
    }


def wd_listings() -> list[dict]:
    return sparql("listings", """SELECT ?c ?ex ?ticker ?start ?prec ?end WHERE { ?c p:P414 ?st . ?st ps:P414 ?ex .
        OPTIONAL { ?st pq:P249 ?ticker } OPTIONAL { ?st pqv:P580 ?tv . ?tv wikibase:timeValue ?start ; wikibase:timePrecision ?prec }
        OPTIONAL { ?st pq:P582 ?end } }""")


def wd_mics() -> dict[str, str]:
    """Wikidata's exchange items to their ISO 10383 market identifier codes (P7534)."""
    rows = sparql("exchanges", """SELECT ?ex ?mic ?label WHERE { { SELECT DISTINCT ?ex WHERE { ?c p:P414/ps:P414 ?ex } }
        OPTIONAL { ?ex wdt:P7534 ?mic } OPTIONAL { ?ex rdfs:label ?label FILTER(LANG(?label) = "en") } }""")
    out = {}
    for r in rows:
        if r["mic"]:
            out.setdefault(_qid(r["ex"]), r["mic"].strip().upper())
    return {**out, **EXTRA_MICS}


def wd_details(name: str, qids: list[str] | None = None) -> dict[str, dict]:
    """The facts of the listed items (``qids`` None) or of the given ones: label, description, article, founding, HQ, country, industries, founders."""
    if qids is not None:
        qids = sorted(set(qids))
        if not qids:
            return {}
    subject = LISTED if qids is None else "VALUES ?c { " + " ".join(f"wd:{q}" for q in qids) + " }"
    out: dict[str, dict] = {}
    for part, q in wd_queries(subject).items():
        for r in sparql(f"{name}_{part}", q):
            d = out.setdefault(_qid(r["c"]), {})
            if part == "basics":
                d.setdefault("label", r["label"] or None)
                d.setdefault("desc", r["desc"] or None)
                if r["article"]:
                    d.setdefault("article", r["article"])
            elif part == "founding":
                if r["inc"] and int(r["prec"] or 0) > d.get("inc_prec", 0):
                    d["inc"], d["inc_prec"] = r["inc"], int(r["prec"])
                if r["fl"] and "fl" not in d:
                    d["fl"] = {"name": r["flLabel"] or None, "coord": _coord(r["flCoord"])}
                if r["diss"]:
                    d["dissolved"] = r["diss"][:10]
            elif part == "hq":
                if r["hq"] and "hq" not in d:
                    d["hq"] = {"name": r["hqLabel"] or None, "coord": _coord(r["hqCoord"])}
                if r["iso"] and "iso" not in d:
                    d["iso"], d["country"] = r["iso"].upper(), r["countryLabel"]
            elif part == "people":
                d["industries"] = [x for x in r["industries"].split("|") if x]
                d["founders"] = [x for x in r["founders"].split("|") if x]
                d["types"] = [x for x in r["types"].split("|") if x]
            else:
                d["employees"] = int(float(r["emp"])) if r["emp"] else None
                d["site"] = r["site"] or None
    return out


def _qid(uri: str) -> str:
    return uri.rsplit("/", 1)[-1]


def _coord(wkt: str) -> tuple[float, float] | None:
    m = re.match(r"Point\(([-\d.eE]+) ([-\d.eE]+)\)", wkt or "")
    return (float(m.group(2)), float(m.group(1))) if m else None   # (lat, lon)


# --- exchanges ---------------------------------------------------------------------------------------------------------------

# MIC: (name, city as places.db spells it, ISO country, opening time today). Times from Wikipedia's "List of major stock exchanges"
# for the exchanges it lists (CITED); the others are the exchange's published regular session. The zone comes from places.db.
EXCHANGES = {
    "XNYS": ("New York Stock Exchange", "New York City", "US", "09:30"), "XNAS": ("Nasdaq", "New York City", "US", "09:30"),
    "XASE": ("NYSE American", "New York City", "US", "09:30"), "ARCX": ("NYSE Arca", "New York City", "US", "09:30"),
    "OTCM": ("OTC Markets", "New York City", "US", "09:30"), "XTSE": ("Toronto Stock Exchange", "Toronto", "CA", "09:30"),
    "XTSX": ("TSX Venture Exchange", "Toronto", "CA", "09:30"), "XLON": ("London Stock Exchange", "London", "GB", "08:00"),
    "XPAR": ("Euronext Paris", "Paris", "FR", "09:00"), "XAMS": ("Euronext Amsterdam", "Amsterdam", "NL", "09:00"),
    "XBRU": ("Euronext Brussels", "Brussels", "BE", "09:00"), "XLIS": ("Euronext Lisbon", "Lisbon", "PT", "08:00"),
    "XDUB": ("Euronext Dublin", "Dublin", "IE", "08:00"), "XMIL": ("Borsa Italiana", "Milan", "IT", "09:00"),
    "XOSL": ("Oslo Børs", "Oslo", "NO", "09:00"), "XETR": ("Xetra", "Frankfurt am Main", "DE", "09:00"),
    "XFRA": ("Frankfurt Stock Exchange", "Frankfurt am Main", "DE", "09:00"), "XSWX": ("SIX Swiss Exchange", "Zürich", "CH", "09:00"),
    "XMAD": ("Bolsa de Madrid", "Madrid", "ES", "09:00"), "XSTO": ("Nasdaq Stockholm", "Stockholm", "SE", "09:00"),
    "XCSE": ("Nasdaq Copenhagen", "Copenhagen", "DK", "09:00"), "XHEL": ("Nasdaq Helsinki", "Helsinki", "FI", "10:00"),
    "XWBO": ("Vienna Stock Exchange", "Vienna", "AT", "09:00"), "XWAR": ("Warsaw Stock Exchange", "Warsaw", "PL", "09:00"),
    "XPRA": ("Prague Stock Exchange", "Prague", "CZ", "09:00"), "XBUD": ("Budapest Stock Exchange", "Budapest", "HU", "09:00"),
    "ASEX": ("Athens Stock Exchange", "Athens", "GR", "10:00"), "XIST": ("Borsa Istanbul", "Istanbul", "TR", "10:00"),
    "MISX": ("Moscow Exchange", "Moscow", "RU", "10:00"), "XTKS": ("Tokyo Stock Exchange", "Tokyo", "JP", "09:00"),
    "XNGO": ("Nagoya Stock Exchange", "Nagoya", "JP", "09:00"), "XOSE": ("Osaka Exchange", "Osaka", "JP", "09:00"),
    "XHKG": ("Hong Kong Stock Exchange", "Hong Kong", "HK", "09:30"), "XSHG": ("Shanghai Stock Exchange", "Shanghai", "CN", "09:30"),
    "XSHE": ("Shenzhen Stock Exchange", "Shenzhen", "CN", "09:30"), "XKRX": ("Korea Exchange", "Seoul", "KR", "09:00"),
    "XKOS": ("KOSDAQ", "Seoul", "KR", "09:00"), "XTAI": ("Taiwan Stock Exchange", "Taipei", "TW", "09:00"),
    "ROCO": ("Taipei Exchange", "Taipei", "TW", "09:00"), "XNSE": ("National Stock Exchange of India", "Mumbai", "IN", "09:15"),
    "XBOM": ("BSE", "Mumbai", "IN", "09:15"), "XSES": ("Singapore Exchange", "Singapore", "SG", "09:00"),
    "XKLS": ("Bursa Malaysia", "Kuala Lumpur", "MY", "09:00"), "XBKK": ("Stock Exchange of Thailand", "Bangkok", "TH", "10:00"),
    "XIDX": ("Indonesia Stock Exchange", "Jakarta", "ID", "09:00"), "XPHS": ("Philippine Stock Exchange", "Taguig", "PH", "09:30"),
    "XSTC": ("Ho Chi Minh Stock Exchange", "Ho Chi Minh City", "VN", "09:00"), "HSTC": ("Hanoi Stock Exchange", "Hanoi", "VN", "09:00"),
    "XASX": ("Australian Securities Exchange", "Sydney", "AU", "10:00"), "XNZE": ("NZX", "Wellington", "NZ", "10:00"),
    "XSAU": ("Saudi Exchange", "Riyadh", "SA", "10:00"), "XADS": ("Abu Dhabi Securities Exchange", "Abu Dhabi", "AE", "10:00"),
    "XDFM": ("Dubai Financial Market", "Dubai", "AE", "10:00"), "DSMD": ("Qatar Stock Exchange", "Doha", "QA", "09:30"),
    "XKUW": ("Boursa Kuwait", "Kuwait City", "KW", "09:00"), "XTAE": ("Tel Aviv Stock Exchange", "Tel Aviv", "IL", "09:59"),
    "XCAI": ("Egyptian Exchange", "Cairo", "EG", "10:00"), "XJSE": ("Johannesburg Stock Exchange", "Johannesburg", "ZA", "09:00"),
    "BVMF": ("B3", "São Paulo", "BR", "10:00"), "XMEX": ("Mexican Stock Exchange", "Mexico City", "MX", "08:30"),
    "XSGO": ("Santiago Stock Exchange", "Santiago", "CL", "09:30"), "XBOG": ("Colombia Stock Exchange", "Bogotá", "CO", "09:30"),
    "XBUE": ("Bolsas y Mercados Argentinos", "Buenos Aires", "AR", "11:00"),
    "XLIM": ("Lima Stock Exchange", "Lima", "PE", None), "XKAR": ("Pakistan Stock Exchange", "Karachi", "PK", None),
    "XBAH": ("Bahrain Bourse", "Manama", "BH", None), "XMUS": ("Muscat Stock Exchange", "Muscat", "OM", None),
    "XICE": ("Nasdaq Iceland", "Reykjavík", "IS", None), "XDHA": ("Dhaka Stock Exchange", "Dhaka", "BD", None),
    "XCOL": ("Colombo Stock Exchange", "Colombo", "LK", None), "XNAI": ("Nairobi Securities Exchange", "Nairobi", "KE", None),
    "XNSA": ("Nigerian Exchange", "Lagos", "NG", None), "XAMM": ("Amman Stock Exchange", "Amman", "JO", None),
    "XCAS": ("Casablanca Stock Exchange", "Casablanca", "MA", None), "XLIT": ("Nasdaq Vilnius", "Vilnius", "LT", None),
    "XTAL": ("Nasdaq Tallinn", "Tallinn", "EE", None), "XRIS": ("Nasdaq Riga", "Riga", "LV", None),
    "XNEP": ("Nepal Stock Exchange", "Kathmandu", "NP", None), "BATS": ("Cboe BZX", "New York City", "US", "09:30"),
}
CITED = {"XNAS", "XNYS", "XSHG", "XPAR", "XAMS", "XBRU", "XLIS", "XDUB", "XMIL", "XOSL", "XTKS", "XSHE", "XHKG", "XBOM", "XNSE", "XTAI",
         "XKRX", "XKOS", "XTSE", "XLON", "XFRA", "XETR", "XSAU", "XASX", "XSWX", "XSTO", "XCSE", "XHEL", "XJSE", "BVMF", "XTAE"}
# Wikidata items of exchanges that carry no MIC (or a segment's): the market they trade on
EXTRA_MICS = {"Q495372": "XKRX", "Q495364": "XKRX", "Q491503": "XKOS", "Q478720": "XAMS", "Q151139": "XFRA", "Q936563": "XMIL",
              "Q1930860": "OTCM", "Q2227403": "HSTC", "Q6529599": "XNEP", "Q11249728": "XTKS", "Q796297": "BVMF", "Q1683760": "XTKS",
              "Q11340130": "XTKS", "Q438511": "XLON", "Q3642744": "XMIL", "Q1391676": "OTCM"}
# Yahoo symbol suffix -> the MICs its listings are on (no suffix: the US markets)
SUFFIX = {"": ("XNYS", "XNAS", "XASE", "ARCX", "OTCM"), "T": ("XTKS",), "NS": ("XNSE",), "BO": ("XBOM",), "L": ("XLON",), "IL": ("XLON",),
          "AX": ("XASX",), "PA": ("XPAR",), "TO": ("XTSE",), "V": ("XTSX",), "SR": ("XSAU",), "DE": ("XETR", "XFRA"), "F": ("XFRA", "XETR"),
          "HK": ("XHKG",), "ST": ("XSTO",), "SW": ("XSWX",), "SS": ("XSHG",), "SZ": ("XSHE",), "MI": ("XMIL",), "KS": ("XKRX",), "KQ": ("XKOS",),
          "AE": ("XADS", "XDFM"), "AD": ("XADS",), "DU": ("XDFM",), "KW": ("XKUW",), "OL": ("XOSL",), "WA": ("XWAR",), "TA": ("XTAE",),
          "MC": ("XMAD",), "TW": ("XTAI",), "TWO": ("ROCO",), "HE": ("XHEL",), "OM": ("XMUS",), "BR": ("XBRU",), "SA": ("BVMF",),
          "BK": ("XBKK",), "QA": ("DSMD",), "CO": ("XCSE",), "SI": ("XSES",), "NZ": ("XNZE",), "JK": ("XIDX",), "AS": ("XAMS",),
          "IS": ("XIST",), "KL": ("XKLS",), "VI": ("XWBO",), "PK": ("XKAR",), "KA": ("XKAR",), "JO": ("XJSE",), "VN": ("XSTC", "HSTC"),
          "BH": ("XBAH",), "AT": ("ASEX",), "IC": ("XICE",), "LS": ("XLIS",), "IR": ("XDUB",), "ME": ("MISX",), "MX": ("XMEX",),
          "SN": ("XSGO",), "BA": ("XBUE",), "CL": ("XBOG",), "LM": ("XLIM",), "PR": ("XPRA",), "BD": ("XBUD",), "CA": ("XCAI",),
          "PS": ("XPHS",), "VS": ("XLIT",), "TL": ("XTAL",), "RG": ("XRIS",)}


def suffix_of(sym: str) -> tuple[str, str]:
    """('7203', 'T') from '7203.T'; a US class share keeps its dot or dash ('BRK-B', '')."""
    m = re.match(r"^(.+)\.([A-Z]{1,3})$", sym)
    if m and m.group(2) in SUFFIX:
        return m.group(1), m.group(2)
    return sym, ""


def norm_ticker(t: str) -> str:
    """A ticker in one spelling: exchange prefix, punctuation and a number's leading zeros gone."""
    t = re.sub(r"^[A-Z]+\s*:\s*", "", (t or "").upper().strip())
    m = re.match(r"^(\d+|[A-Z0-9]+(?=\.[A-Z]{2,3}$))\.([A-Z]{1,3})$", t)
    if m and m.group(2) in SUFFIX:   # '7203.T', 'SAP.DE'; a class share ('BRK.B') keeps its letter
        t = m.group(1)
    t = re.sub(r"[^A-Z0-9]", "", t)
    return str(int(t)) if t.isdigit() else t


# --- places and zones ------------------------------------------------------------------------------------------------------

class Places:
    """places.db: a city by name and country, the nearest city to a point, and country names to ISO codes."""

    def __init__(self) -> None:
        db = ROOT / "databases" / "places.db"
        if not db.exists():
            sys.exit("databases/places.db is missing: build it with databases/build_places_db.py first")
        with sqlite3.connect(db) as c:
            self.rows = list(c.execute("select name, asciiname, country_iso2, lat, lon, timezone, population from places"))
            self.names = dict(c.execute("select iso2, name from countries"))
        self.countries = {n.lower(): iso for iso, n in self.names.items()}
        self.countries.update(COUNTRY_ALIAS)
        self.by_name: dict[tuple[str, str], tuple] = {}
        self.grid: dict[tuple[int, int], list[tuple]] = {}
        for r in sorted(self.rows, key=lambda r: -(r[6] or 0)):
            for n in {r[0].lower(), (r[1] or "").lower()}:
                self.by_name.setdefault((n, r[2]), r)
            self.grid.setdefault((int(r[3] // 1), int(r[4] // 1)), []).append(r)

    def city(self, name: str, iso2: str) -> tuple | None:
        return self.by_name.get((name.lower(), iso2))

    def near(self, lat: float, lon: float) -> tuple | None:
        best, dist = None, 9.0
        for i in range(-1, 2):
            for j in range(-1, 2):
                for r in self.grid.get((int(lat // 1) + i, int(lon // 1) + j), ()):
                    d = (r[3] - lat) ** 2 + ((r[4] - lon) * 0.7) ** 2
                    if d < dist:
                        best, dist = r, d
        return best

    def iso(self, country: str) -> str | None:
        return self.countries.get((country or "").strip().lower())


COUNTRY_ALIAS = {"usa": "US", "united states": "US", "uk": "GB", "united kingdom": "GB", "south korea": "KR", "korea": "KR", "taiwan": "TW",
                 "hong kong": "HK", "netherlands": "NL", "the netherlands": "NL", "uae": "AE", "united arab emirates": "AE", "russia": "RU",
                 "czech republic": "CZ", "czechia": "CZ", "turkey": "TR", "türkiye": "TR", "vietnam": "VN", "macau": "MO", "macao": "MO",
                 "ivory coast": "CI", "côte d'ivoire": "CI", "bahamas": "BS", "the bahamas": "BS", "cayman islands": "KY", "bermuda": "BM",
                 "british virgin islands": "VG", "isle of man": "IM", "jersey": "JE", "guernsey": "GG", "curacao": "CW", "curaçao": "CW",
                 "palestine": "PS", "iran": "IR", "syria": "SY", "laos": "LA", "moldova": "MD", "bolivia": "BO", "venezuela": "VE",
                 "tanzania": "TZ", "democratic republic of the congo": "CD", "republic of the congo": "CG", "brunei": "BN"}


def zone(tzname: str, d: str, hhmm: str) -> float:
    """Hours east of UTC on that local date and time, from the tz database (local mean time before standard zones)."""
    y, m, dd = (int(x) for x in d.split("-"))
    h, mi = (int(x) for x in hhmm.split(":"))
    off = datetime(y, m, dd, h, mi, tzinfo=ZoneInfo(tzname)).utcoffset()
    return round(off.total_seconds() / 3600, 4) if off is not None else 0.0


def open_time(mic: str, d: str) -> str | None:
    """The exchange's opening time on a day: today's hours, with the changes known for New York and Hong Kong."""
    t = EXCHANGES[mic][3]
    if mic in ("XNYS", "XNAS", "XASE", "ARCX", "OTCM") and d < "1985-09-30":
        return "10:00"   # the NYSE (and Nasdaq with it) opened at 10:00 until 30 September 1985
    if mic == "XHKG" and d < "2011-03-07":
        return "10:00"   # HKEX's morning session began at 10:00 until 7 March 2011
    return t


# --- calibrating Yahoo -----------------------------------------------------------------------------------------------------

def calibrate(pairs: dict[str, list[tuple[str, str]]]) -> dict[str, str]:
    """Per MIC, the date from which Yahoo's first trading day can stand for a listing date: the earliest day after which at least
    90% of its dates (of 8 or more checked) agree within 3 days with the exchange's list or Wikidata. A MIC never checked gets none."""
    out = {}
    agree = lambda p: abs((date.fromisoformat(p[0]) - date.fromisoformat(p[1])).days) <= 3
    for mic, ps in pairs.items():
        ps = sorted(ps)   # (yahoo, reference)
        for i, p in enumerate(ps):
            rest = ps[i:]
            if len(rest) < 8:
                break
            if agree(p) and sum(map(agree, rest)) >= 0.9 * len(rest):
                out[mic] = p[0]
                break
    return out


# --- building ---------------------------------------------------------------------------------------------------------------

SECTOR_OF_CB = {"Enterprise Tech": "Technology", "Fintech": "Financial Services", "Financial Services": "Financial Services", "Insurance": "Financial Services",
                "Healthcare & Life Sciences": "Healthcare", "Consumer & Retail": "Consumer Cyclical", "Media & Entertainment": "Communication Services",
                "Industrials": "Industrials"}
# an industry's words to Yahoo's eleven sectors, for the companies Yahoo has no profile of; the first match wins
SECTOR_WORDS = [("Utilities", r"electric|utilit|\bpower\b|\bwater\b"), ("Energy", r"\boil\b|\bgas\b|petro|energy|\bcoal\b|refin"),
                ("Financial Services", r"bank|financ|insur|invest|asset manag|brokerage|payment|\bcredit\b"),
                ("Healthcare", r"pharma|health|medic|biotech|hospital|drug"),
                ("Communication Services", r"telecom|media|broadcast|internet|social network|entertainment|advertis|publish|video game|gaming"),
                ("Technology", r"techn|software|semiconductor|electronic|computer|information|\bit\b"),
                ("Consumer Defensive", r"food|beverage|agri|tobacco|grocer|supermarket|household|cosmetic|drink|brew|dairy"),
                ("Consumer Cyclical", r"retail|e-commerce|apparel|cloth|fashion|automo|\bcars?\b|vehicle|hotel|restaurant|travel|luxury|furniture"),
                ("Basic Materials", r"chemical|steel|metal|mining|commodit|paper|forest|cement"),
                ("Real Estate", r"real estate|property|\breit\b"),
                ("Industrials", r"construct|engineer|aerospace|defen[cs]e|logistic|transport|shipping|airline|rail|conglomerate|industr|machin|manufactur")]


def sector_of(*texts: str | None) -> str | None:
    for t in texts:
        for sector, words in SECTOR_WORDS:
            if t and re.search(words, t, re.I):
                return sector
    return None


SUFFIX_WORDS = r"\b(inc|incorporated|corp|corporation|co|company|ltd|limited|plc|sa|s a|ag|se|nv|n v|ab|asa|as|a s|spa|s p a|oyj|holdings?|group|the|llc|lp|bhd|berhad|tbk|pt|sab de cv|de cv|kk|kabushiki kaisha|co ltd)\b"


def norm_name(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()
    s = re.sub(r"\(.*?\)", " ", s)
    s = re.sub(r"[^a-z0-9]+", " ", s)
    return re.sub(r"\s+", " ", re.sub(SUFFIX_WORDS, " ", s)).strip()


def slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()).strip("-")


def iso_day(v: str | None) -> str | None:
    """'1976-04-01T00:00:00Z' -> '1976-04-01' (CE only)."""
    return v[:10] if v and re.match(r"^\d{4}-\d\d-\d\d", v) else None


# Yahoo's exchange codes for the US markets and Germany's two venues
YAHOO_MIC = {"NMS": "XNAS", "NGM": "XNAS", "NCM": "XNAS", "NAS": "XNAS", "NYQ": "XNYS", "NYS": "XNYS", "ASE": "XASE", "PCX": "ARCX",
             "PNK": "OTCM", "OQB": "OTCM", "OQX": "OTCM", "OEM": "OTCM", "OGM": "OTCM", "BTS": "BATS", "GER": "XETR", "FRA": "XFRA"}


# First trading days looked up by hand for large companies the sources above leave without one, or with a doubtful one:
# Wikidata item -> (MIC, day or year, publisher, address). A year alone leaves the listing undated: Coca-Cola went public on
# the NYSE in 1919, so Wikidata's 1929-02-20 is not its first trade.
CURATED = {
    "Q248": ("XNAS", "1971-10-13", "Intel's investor FAQ", "https://www.intc.com/stock-info/faq"),
    "Q333718": ("XNYS", "1944-09-25", "The Motley Fool (J&J dates its IPO the 24th, a Sunday)",
                "https://www.fool.com/investing/general/2013/09/25/2-legendary-beginnings-a-disastrous-bank-failure-a.aspx"),
    "Q459965": ("XNYS", "1929-12-02", "Caterpillar",
                "https://www.caterpillar.com/en/news/corporate-press-releases/h/caterpillar-celebrates-85-years-on-the-new-york-stock-exchange.html"),
    "Q193412": ("XNYS", "1953-10-01", "TI's investor FAQ", "https://investor.ti.com/node/5941"),
    "Q44504": ("XMAD", "2001-05-23", "BBC News", "http://news.bbc.co.uk/2/hi/business/1346473.stm"),
    "Q1485061": ("XNYS", "1892-06-23", "The Motley Fool", "https://www.fool.com/investing/general/2013/04/15/the-dawn-of-the-dows-most-durable-company.aspx"),
    "Q156077": ("XPAR", "1963-10-08", "L'Oréal Finance", "https://www.loreal-finance.com/fr/laction"),
    "Q160746": ("XSWX", "1905-10-25", "Nestlé's investor FAQ (Zurich Stock Exchange)", "https://www.nestle.com/investors/faqs"),
    "Q159433": ("XNYS", "1946-01-14", "3M's investor FAQ", "https://investors.3m.com/resources/faq"),
    "Q194360": ("XNYS", "1977-05-18", "AInvest and Moomoo listing dates", "https://www.ainvest.com/stocks/NYSE-AXP/profile/"),
    "Q3295867": ("XNYS", "1919", "Coca-Cola, via 11Alive",
                 "https://11alive.com/article/money/business/world-of-coca-cola-free-admission-100-years/85-3e5edddf-a123-46b4-8281-bd260afaf0b8"),
}
US = set(SUFFIX[""])
YAHOO_SINCE = "2016-01-01"   # pooled over the exchanges off the US, Yahoo's days from 2016 agree within 3 days 90% of the time
# days many companies really did list together: the Tokyo Stock Exchange's reopening after the war
MASS_LISTING_DAYS = {("XTKS", "1949-05-16")}


def group(mic: str) -> str:
    """The US markets count as one: a company moves between them, and they share New York and their hours."""
    return "US" if mic in US else mic


def aliases(name: str) -> list[str]:
    """'Alphabet (Google)' -> ['Alphabet (Google)', 'Google']: companiesmarketcap puts a better-known name in brackets."""
    return [name] + re.findall(r"\(([^)]+)\)", name)


def similar(a: str, b: str) -> bool:
    x, y = set(norm_name(a).split()), set(norm_name(b).split())
    return bool(x and y) and len(x & y) / min(len(x), len(y)) >= 0.5


def build(fetch_yahoo: bool = True) -> None:
    P = Places()
    missing = [mic for mic, (_, city, iso, _) in EXCHANGES.items() if not P.city(city, iso)]
    if missing:
        sys.exit(f"exchange cities not in places.db: {missing}")
    caps = market_caps()
    prof = yahoo_profiles([c["symbol"] for c in caps], fetch=fetch_yahoo)
    official = official_dates()
    mics = wd_mics()
    facts = wd_details("listed")
    wl: dict[str, list[dict]] = {}
    by_ticker: dict[tuple[str, str], set[str]] = {}
    for r in wd_listings():
        q, mic = _qid(r["c"]), mics.get(_qid(r["ex"]))
        x = {"mic": mic if mic in EXCHANGES else None, "ticker": (r["ticker"] or "").strip() or None, "start": r["start"] or None,
             "prec": int(r["prec"] or 0), "end": iso_day(r["end"])}
        wl.setdefault(q, []).append(x)
        if x["mic"] and x["ticker"]:
            by_ticker.setdefault((x["mic"], norm_ticker(x["ticker"])), set()).add(q)
    # a start day many of a market's Wikidata listings share is a bulk import's date, not theirs (1990-01-02 on 112 NYSE listings)
    shared = Counter((group(x["mic"]), iso_day(x["start"])) for xs in wl.values() for x in xs if x["mic"] and x["prec"] >= 11 and iso_day(x["start"]))
    bulk = {k for k, n in shared.items() if n >= 10 and k not in MASS_LISTING_DAYS}
    for xs in wl.values():
        for x in xs:
            if x["mic"] and (group(x["mic"]), iso_day(x["start"])) in bulk:
                x["prec"] = 0
    by_name: dict[str, set[str]] = {}
    for q, d in facts.items():
        if d.get("label"):
            by_name.setdefault(norm_name(d["label"]), set()).add(q)
    report: dict[str, list] = {"conflicts": [], "before_founding": [], "unmatched_index": [], "lent": [], "bulk": sorted(bulk), "floors": []}

    def match(c: dict) -> str | None:
        """The Wikidata item of a companiesmarketcap line: by its ticker on its exchange, else by a name only one item has there."""
        base, suf = suffix_of(c["symbol"])
        t = norm_ticker(base)
        names = aliases(c["name"]) + [prof.get(c["symbol"], {}).get("name") or ""]
        hits = set().union(*(by_ticker.get((m, t), set()) for m in SUFFIX[suf]))
        named = {q for q in hits if any(similar(n, facts.get(q, {}).get("label") or "") for n in names if n)}
        label = lambda q: norm_name(facts.get(q, {}).get("label") or "")
        # several items hold the ticker (Samsung Group has Samsung Electronics' 005930): narrow by the legal name Yahoo gives,
        # then by the listing still current (Google's GOOG ended in 2016, Alphabet's goes on), then by the name itself
        for keep in (lambda q: bool(names[-1]) and label(q) == norm_name(names[-1]),
                     lambda q: any(x["mic"] in SUFFIX[suf] and norm_ticker(x["ticker"] or "") == t and not x["end"] for x in wl[q]),
                     lambda q: label(q) == norm_name(c["name"])):
            if len(named) > 1:
                named = {q for q in named if keep(q)} or named
        if len(named) == 1:
            return next(iter(named))
        if len(hits) == 1:   # one item has the ticker: right if it still trades under it (a ticker is often reused)
            q = next(iter(hits))
            if any(x["mic"] in SUFFIX[suf] and norm_ticker(x["ticker"] or "") == t and not x["end"] for x in wl[q]):
                return q
        iso = P.iso(c["country"])
        cand = {q for n in names if n for q in by_name.get(norm_name(n), ())}
        cand = {q for q in cand if facts.get(q, {}).get("iso") in (iso, None)}
        return next(iter(cand)) if len(cand) == 1 else None

    comps: dict[str, dict] = {}
    for c in caps:   # largest first, so a company's second share line is dropped
        q = match(c)
        comps.setdefault(q or "sym:" + c["symbol"], {"qid": q, "cap": c, "y": prof.get(c["symbol"]) or {}})

    def yahoo_day(y: dict) -> str | None:
        if not y.get("first") or not y.get("zone"):
            return None
        try:
            return datetime.fromtimestamp(int(y["first"]), ZoneInfo(y["zone"])).date().isoformat()
        except (ValueError, KeyError, OSError):
            return None

    def home(comp: dict) -> str | None:
        """The MIC of the companiesmarketcap symbol's market."""
        base, suf = suffix_of(comp["cap"]["symbol"])
        ym = YAHOO_MIC.get(comp["y"].get("exchange") or "")
        if ym in SUFFIX[suf]:
            return ym
        if suf:
            return SUFFIX[suf][0]
        t = norm_ticker(base)
        return next((x["mic"] for x in wl.get(comp["qid"] or "", []) if x["mic"] in SUFFIX[""] and norm_ticker(x["ticker"] or "") == t), None)

    def reference(comp: dict, mic: str) -> tuple[str, str] | None:
        """The listing day the exchange's list or Wikidata gives the symbol's own listing."""
        base, suf = suffix_of(comp["cap"]["symbol"])
        t = norm_ticker(base)
        same = SUFFIX[suf] if mic in SUFFIX[suf] else (mic,)
        for m in same:
            if (m, t) in official:
                return official[(m, t)]
        for x in wl.get(comp["qid"] or "", []):
            if x["mic"] in same and x["prec"] >= 11 and iso_day(x["start"]) and (not x["ticker"] or norm_ticker(x["ticker"]) == t):
                return iso_day(x["start"]), "Wikidata"
        return None

    # the days Yahoo's price histories start on: many symbols of a market (or of the world) sharing a first day that is no listing's
    per, world, size = Counter(), Counter(), Counter()
    for comp in comps.values():
        mic, yd = home(comp), yahoo_day(comp["y"])
        if mic and yd:
            per[(group(mic), yd)] += 1
            world[yd] += 1
            size[group(mic)] += 1
    floors = {k for k, n in per.items() if n >= (8 if k[0] == "US" else max(6, 0.01 * size[k[0]])) or world[k[1]] >= 15}
    report["floors"] = sorted((g, d, per[(g, d)]) for g, d in floors)

    # how far Yahoo's first trading day can be trusted off the US markets, exchange by exchange
    pairs: dict[str, list[tuple[str, str]]] = {}
    for comp in comps.values():
        mic, yd = home(comp), yahoo_day(comp["y"])
        ref = reference(comp, mic) if mic and yd and (group(mic), yd) not in floors else None
        if ref:
            pairs.setdefault(mic, []).append((yd, ref[0]))
    cutoff = calibrate(pairs)

    def trusted(mic: str, yd: str | None) -> bool:
        """Yahoo's first day stands for a listing day: on the US markets unless it is a start of data (Wikidata is the weaker
        source there, see FINANCE.md), elsewhere from the date the exchange's own list and Wikidata agree with it, or, on an
        exchange too little checked to say, from YAHOO_SINCE, from which 90% of all the other exchanges' days agree."""
        return bool(yd) and (group(mic), yd) not in floors and (mic in US or yd >= cutoff.get(mic, YAHOO_SINCE))

    def listings(comp: dict) -> list[dict]:
        q, c, y = comp["qid"], comp["cap"], comp["y"]
        out: dict[tuple[str, str], dict] = {}
        for x in wl.get(q or "", []):
            if not x["mic"]:
                continue
            t = norm_ticker(x["ticker"] or "")
            off = official.get((x["mic"], t)) if t else None
            wd = iso_day(x["start"]) if x["prec"] >= 11 and not x["start"].startswith("01-01", 5) else None   # 1 January: a year, the markets are shut
            if off and wd and off[0] != wd:
                report["conflicts"].append((c["name"], EXCHANGES[x["mic"]][0], off[1], off[0], "Wikidata", wd))
            d, src = off or ((wd, "Wikidata") if wd else (None, None))
            year = x["start"][:4] if x["start"] and x["prec"] >= 9 and not d and re.match(r"\d{4}", x["start"]) else None
            prev = out.get((x["mic"], t))
            if prev is None or (d and not prev["date"]):
                out[(x["mic"], t)] = {"mic": x["mic"], "ticker": x["ticker"], "date": d, "year": year, "source": src, "ended": x["end"]}
        mic = home(comp)
        if mic:
            base, suf = suffix_of(c["symbol"])
            t = norm_ticker(base)
            same = SUFFIX[suf] if mic in SUFFIX[suf] else (mic,)
            key = next((k for k in out if k[0] in same and (k[1] == t or not k[1])), (mic, t))
            cur = out.pop(key, None) or {"mic": mic, "ticker": base, "date": None, "year": None, "source": None, "ended": None}
            yd = yahoo_day(y)
            yahoo = [("Yahoo Finance", yd)] if trusted(mic, yd) else []
            known = [(cur["source"], cur["date"])] if cur["date"] else []
            off = [(official[(mic, t)][1], official[(mic, t)][0])] if (mic, t) in official else []
            cands = off + (yahoo + known if mic in US else known + yahoo)   # in order of trust
            if cands:
                src, day = cands[0]
                for s2, d2 in cands[1:]:
                    if abs((date.fromisoformat(day) - date.fromisoformat(d2)).days) > 3:
                        report["conflicts"].append((c["name"], EXCHANGES[mic][0], src, day, s2, d2))
                if src.startswith("Yahoo") and mic in US:
                    # the US market it traded on that day: a Wikidata listing begun by then and not yet ended, Yahoo's own market
                    # first (Walmart's 1972 first trade was on the NYSE, its move to Nasdaq came in 2024)
                    fit = [x for x in wl.get(q or "", []) if x["mic"] in US and (x["prec"] < 9 or x["start"][:10] <= day) and (not x["end"] or x["end"] >= day)]
                    cur["mic"] = min(fit, key=lambda x: x["mic"] != mic)["mic"] if fit else mic
                cur.update(date=day, source=src, year=None)
            out[(cur["mic"], t)] = cur
        if q in CURATED:   # looked up by hand: it replaces that exchange's listing, or adds it (TI's NYSE years before Nasdaq)
            mic, day, who, url = CURATED[q]
            key = next((k for k in out if k[0] == mic), (mic, ""))
            x = out.pop(key, None) or {"mic": mic, "ticker": None, "ended": None}
            out[key] = {**x, "date": day if len(day) == 10 else None, "year": None if len(day) == 10 else day, "source": who, "url": url}
        order = list(EXCHANGES)   # a tie (Toyota listed in Tokyo, Osaka and Nagoya on one day) goes to the larger exchange
        return sorted(out.values(), key=lambda x: (x["date"] or (x["year"] + "-99") if (x["date"] or x["year"]) else "9999", order.index(x["mic"])))

    # index members
    members = index_members()
    tq = wiki_qids([m["title"] for ms in members.values() for m in ms])
    index_of: dict[str, set[str]] = {}
    founded_year: dict[str, str] = {}
    for name, ms in members.items():
        for m in ms:
            q = tq.get(m["title"])
            if q:
                index_of.setdefault(q, set()).add(name)
                y = re.search(r"\b(1[5-9]\d\d|20\d\d)\b", m.get("founded") or "")
                if y:
                    founded_year.setdefault(q, y.group(1))
    have = {comp["qid"] for comp in comps.values() if comp["qid"]}
    report["unmatched_index"] = sorted({(name, m["title"]) for name, ms in members.items() for m in ms if tq.get(m["title"]) not in have})
    rodden = [r for r in json.loads((OUT.parent / "rodden_events.json").read_text())["records"] if r.get("type") == "business" and r.get("time")]

    def founding(q: str | None, d: dict, iso: str | None, city: str | None) -> dict:
        """founded (YYYY, YYYY-MM or YYYY-MM-DD), the place, and the founding day's chart place when the day is known."""
        out: dict = {}
        inc, prec = d.get("inc"), d.get("inc_prec", 0)
        if inc and re.match(r"^\d{4}-", inc) and prec >= 9:
            out["founded"] = inc[:10] if prec >= 11 else inc[:7] if prec == 10 else inc[:4]
        elif q in founded_year:
            out["founded"] = founded_year[q]
        places = [p for p in (d.get("fl"), d.get("hq")) if p]   # where it was formed, else its headquarters
        if places and places[0].get("name"):
            out["founded_place"] = places[0]["name"]
        place = next((p for p in places if p.get("coord")), {})
        at = place.get("coord")
        near = P.near(*at) if at else (P.city(city, iso) if city and iso else None)
        f = out.get("founded", "")
        if len(f) == 10 and f >= "1583-01-01" and near:
            lat, lon = at or (near[3], near[4])
            out["founded_at"] = {"place": place.get("name") or near[0], "lat": round(lat, 4), "lon": round(lon, 4), "tz_east": zone(near[5], f, "12:00")}
        if d.get("founders"):
            out["founders"] = d["founders"][:6]
        return out

    def moment_of_listing(rec: dict, first: dict) -> None:
        mic, d = first["mic"], first["date"]
        ex, city, iso, _ = EXCHANGES[mic]
        pl = P.city(city, iso)
        t = open_time(mic, d)
        rec.update(date=d, time=t, tz_east=zone(pl[5], d, t or "12:00"), gregorian=True, time_confidence="approx" if t else "date",
                   time_source=("The opening bell that day" if mic in US or mic == "XHKG" else "The opening bell (today's hours)") if t else "",
                   place=pl[0], place_country=P.names.get(iso, iso), lat=round(pl[3], 4), lon=round(pl[4], 4), chart="listing")
        # a Rodden AA or A chart of this first trade lends its minute
        names = aliases(rec["name"]) + [rec.get("legal_name") or ""]
        ro = [r for r in rodden if r["date"] == d and rodden_of(names, r["name"])]
        ro.sort(key=lambda r: "first trade" not in r["name"].lower())
        if ro and pl and abs(ro[0]["lat"] - pl[3]) < 1 and abs(ro[0]["lon"] - pl[4]) < 1:
            rec.update(time=ro[0]["time"][:5], tz_east=ro[0]["tz_east"], time_confidence="reported",
                       time_source=f"{ro[0]['time_source']} ({ro[0]['name']})", rodden_source=ro[0]["source"])
            report["lent"].append((rec["name"], d, ro[0]["time"][:5], ro[0]["name"]))

    records = []
    for comp in comps.values():
        q, c, y = comp["qid"], comp["cap"], comp["y"]
        d = facts.get(q or "", {})
        iso = P.iso(c["country"])
        ls = listings(comp)
        legal = y.get("name") or d.get("label")
        rec = {"id": "fi-" + (q.lower() if q else slug(c["symbol"])), "name": c["name"], "legal_name": legal if norm_name(legal or "") != norm_name(c["name"]) else None,
               "status": "listed", "sector": y.get("sector") or sector_of(*(d.get("industries") or [])),
               "industry": y.get("industry") or _cap((d.get("industries") or [None])[0]),
               "country": c["country"], "iso2": iso,
               "hq": ", ".join(x for x in (y.get("city"), y.get("state")) if x) or (d.get("hq") or {}).get("name"),
               "rank": c["rank"], "market_cap": c["mcap"], "symbol": c["symbol"],
               "listings": [[EXCHANGES[x["mic"]][0], x["ticker"], x["date"] or x["year"], x["source"], x["ended"]] for x in ls],
               "indices": sorted(index_of.get(q or "", ())) or None,
               **founding(q, d, iso, y.get("city")),
               "employees": y.get("employees") or d.get("employees"), "website": y.get("website") or d.get("site"),
               "about": _sentences(y.get("summary") or "", 1, 220) or _cap(d.get("desc")), "wikipedia": d.get("article"),
               "yahoo": 1 if y and not y.get("error") else None,   # Yahoo knows the symbol: the Finance tab can chart its price
               "source": f"https://www.wikidata.org/wiki/{q}" if q else f"https://finance.yahoo.com/quote/{urllib.parse.quote(c['symbol'])}"}
        first = next((x for x in ls if x["date"]), None) or rodden_listing(c["name"], legal, iso, rodden, P)
        if first and first not in ls:
            rec["listings"].insert(0, [EXCHANGES[first["mic"]][0], None, first["date"], first["source"], None])
        mic = first["mic"] if first else home(comp)   # the exchange of the chart, else of the symbol
        if mic:
            rec.update(exchange=EXCHANGES[mic][0], mic=mic)
        if first:
            rec["listed"] = first["date"]
            if first.get("url"):
                rec["listed_ref"] = first["url"]
            moment_of_listing(rec, first)
            f = rec.get("founded")
            if f and f[:4] > first["date"][:4]:
                report["before_founding"].append((c["name"], first["date"], rec["exchange"], f))
        elif rec.get("founded_at"):
            founding_moment(rec)
        records.append(_clean(rec))

    # an index member whose article is not the listed company's item (PayPal's, Norfolk Southern Railway's) is found by its ticker
    by_symbol = {(suffix_of(r["symbol"])[1], norm_ticker(suffix_of(r["symbol"])[0])): r for r in reversed(records)}
    tagged = set()
    for name, ms in members.items():
        for m in ms:
            tick = re.sub(r"\[.*?\]", "", m.get("ticker") or "").split(":")[-1].strip()   # 'SEHK: 5', 'ADS.DE', 'BRK.B'
            if not tick:
                continue
            base, suf = suffix_of(tick)
            markets = ([suf] if suf else []) + list(INDEX_MARKETS.get(name, ()))   # Sensex writes ADANIPORTS.BO, the list has .NS
            hit = next((by_symbol[(s, norm_ticker(base))] for s in markets if (s, norm_ticker(base)) in by_symbol), None)
            if hit:
                tagged.add((name, m["title"]))
                if name not in hit.get("indices", []):
                    hit["indices"] = sorted(hit.get("indices", []) + [name])
    report["unmatched_index"] = [x for x in report["unmatched_index"] if x not in tagged]

    # the unicorns: private companies valued at $1 billion or more
    cb = unicorns()
    on_list = {norm_name(x["name"]): x["title"] for x in unicorn_titles()}
    for u in cb:
        t = on_list.get(norm_name(u["name"]))
        u["_titles"] = [t] if t else [f"{u['name']} (company)", u["name"]]
    uq = wiki_qids([t for u in cb for t in u["_titles"]])
    want = sorted({uq[t] for u in cb for t in u["_titles"] if uq.get(t)} - set(facts))
    sfacts = {**wd_details("startups_" + hashlib.sha1(" ".join(want).encode()).hexdigest()[:8], want), **facts}
    taken = {comp["qid"] for comp in comps.values() if comp["qid"]}
    for u in cb:
        q = next((uq[t] for t in u["_titles"] if uq.get(t) and companyish(sfacts.get(uq[t], {}))), None)
        if q in taken:
            continue   # listed since, or the item of a listed parent
        if q:
            taken.add(q)
        d = sfacts.get(q or "", {})
        iso = P.iso(u["country"])
        rec = {"id": "fi-" + (q.lower() if q else "u-" + slug(u["name"])), "name": u["name"], "legal_name": d.get("label"), "status": "startup",
               "sector": SECTOR_OF_CB.get(u["industry"]) or sector_of(u["industry"], *(d.get("industries") or [])), "industry": u["industry"],
               "country": u["country"], "iso2": iso, "hq": u["city"],
               "valuation": u["valuation"], "unicorn_since": u["joined"], "investors": u["investors"],
               **founding(q, d, iso, u["city"]), "employees": d.get("employees"), "website": d.get("site"), "about": _cap(d.get("desc")),
               "wikipedia": d.get("article"), "wikidata": q, "source": CBI}
        if rec.get("founded_at"):
            founding_moment(rec)
        records.append(_clean(rec))

    # the largest companies that are not listed: state-owned and private, from Wikipedia's lists by revenue
    big = big_companies()
    bq = wiki_qids([b["title"] for b in big])
    want = sorted({bq[b["title"]] for b in big if bq.get(b["title"])} - set(sfacts))
    pfacts = {**wd_details("private_" + hashlib.sha1(" ".join(want).encode()).hexdigest()[:8], want), **sfacts}
    for b in big:
        q = bq.get(b["title"])
        if not q or q in taken or not companyish(pfacts.get(q, {})):
            continue   # listed (its listed arm is), or already in
        taken.add(q)
        d = pfacts[q]
        iso = d.get("iso")
        hq = (d.get("hq") or {}).get("name")
        rec = {"id": "fi-" + q.lower(), "name": b["name"], "legal_name": d.get("label"), "status": "private",
               "sector": sector_of(b["industry"], *(d.get("industries") or [])),
               "industry": b["industry"] or _cap((d.get("industries") or [None])[0]), "country": P.names.get(iso or "", d.get("country")),
               "iso2": iso, "hq": hq, "revenue": b["revenue"], "revenue_from": b["list"],
               **founding(q, d, iso, hq), "employees": d.get("employees"), "website": d.get("site"), "about": _cap(d.get("desc")),
               "wikipedia": d.get("article"), "wikidata": q, "source": f"https://www.wikidata.org/wiki/{q}"}
        if rec.get("founded_at"):
            founding_moment(rec)
        records.append(_clean(rec))

    write(records, pairs, cutoff, report)


SHARES = r"\b(shares?|stock|first trade|market start)\b"


def rodden_of(names: list[str], chart: str) -> bool:
    """Whether a Rodden chart ('Apple, Shares', 'Google First Trade', 'Disney stock') is of this company's shares: every word of
    the company in the chart's name is in one of its names (Disney in Walt Disney; Cisco Systems not in BAE Systems)."""
    if not re.search(SHARES, chart, re.I):
        return False
    core = set(norm_name(re.sub(SHARES, " ", chart.split(",")[0], flags=re.I)).split())
    return bool(core) and min(map(len, core)) >= 3 and any(core <= set(norm_name(n).split()) for n in names)


def rodden_listing(name: str, legal: str | None, iso: str | None, rodden: list[dict], P: Places) -> dict | None:
    """A first trade the Rodden library charts ('Disney stock', 'Infineon, Shares') at an exchange's city in the company's own
    country (not Oracle's for Oracle Japan), for a company no other source gives a listing day."""
    names = aliases(name) + [legal or ""]
    for r in rodden:
        if r.get("iso2") != iso or not rodden_of(names, r["name"]):
            continue
        for mic, (_, city, iso, _) in EXCHANGES.items():
            pl = P.city(city, iso)
            if abs(r["lat"] - pl[3]) < 1 and abs(r["lon"] - pl[4]) < 1:
                return {"mic": mic, "ticker": None, "date": r["date"], "year": None, "source": r["time_source"], "ended": None}
    return None


def founding_moment(rec: dict) -> None:
    """A record with no listing day is cast for its founding day, at local noon (the hour is unknown)."""
    f = rec["founded_at"]
    rec.update(date=rec["founded"], time=None, tz_east=f["tz_east"], gregorian=True, time_confidence="date", time_source="",
               place=f["place"], lat=f["lat"], lon=f["lon"], chart="founding")


def companyish(d: dict) -> bool:
    """A Wikidata item that is a company, not a word that happens to share its name."""
    return bool(d.get("industries") or d.get("hq") or d.get("founders")
                or any(re.search(r"compan|business|enterprise|startup|firm|corporation|bank|organi|unicorn", t, re.I) for t in d.get("types", [])))


def _cap(s: str | None) -> str | None:
    return s[0].upper() + s[1:] if s else s


def _clean(rec: dict) -> dict:
    return {k: v for k, v in rec.items() if v not in (None, "", [], {})}


def write(records: list[dict], pairs: dict, cutoff: dict, report: dict) -> None:
    seen: set[str] = set()
    records = [r for r in records if not (r["id"] in seen or seen.add(r["id"]))]   # a company twice on a list (CB has Invoca twice): the first
    listed = [r for r in records if r["status"] == "listed"]
    uni = [r for r in records if r["status"] == "startup"]
    priv = [r for r in records if r["status"] == "private"]
    by_src: dict[str, int] = {}
    for r in listed:
        if r.get("listed"):
            src = next(x[3] for x in r["listings"] if x[2] == r["listed"] and x[3])
            by_src[src] = by_src.get(src, 0) + 1
    about = ("The world's listed companies by market value (companiesmarketcap.com, " + date.today().isoformat() + "), the private companies "
             "valued at $1 billion or more (CB Insights' unicorn list) and the largest unlisted companies by revenue (Wikipedia's lists). "
             "status: listed, startup (a unicorn) or private (state-owned or private, revenue in US$). A listed company's moment (date, time, "
             "tz_east, place) is its first listing's first trading day (listed, exchange) at the exchange, timed at the exchange's opening: the minute of "
             "the first trade is seldom recorded, so time_confidence is approx (reported where a Rodden AA or A chart of the first trade gives "
             "it). The day comes from the exchange's own list (NSE, TWSE, KRX, SSE, SZSE), else Wikidata's start time of the listing, else "
             "Yahoo Finance's first trading day where it agrees with those for that exchange and era (on the US markets before Wikidata, "
             "and the market named is Yahoo's today). listings: every listing known [exchange, ticker, day or year, source, ended]. "
             "A company with no listing day, and every unlisted one, is cast for its founding "
             "day at local noon (time_confidence date) when Wikidata gives the day; founded is YYYY, YYYY-MM or YYYY-MM-DD as precise as known, "
             "and a startup without one is still listed. Biography: Yahoo Finance's profile, Wikidata, Wikipedia's index tables. "
             "Built by tools/mundane_finance.py; data/mundane/FINANCE.md has the checks.")
    OUT.write_text(json.dumps({"_about": about, "records": records}, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    lines = ["# Finance database: how it was built and checked", "", f"Built {date.today().isoformat()} by `tools/mundane_finance.py`.", "",
             f"- {len(listed):,} listed companies; {sum(1 for r in listed if 'wikidata.org' in r['source']):,} matched to a Wikidata item; "
             f"{sum(1 for r in listed if r.get('listed')):,} with a first trading day "
             f"({', '.join(f'{k}: {v:,}' for k, v in sorted(by_src.items(), key=lambda kv: -kv[1]))}), "
             f"{sum(1 for r in listed if r.get('time')):,} of them timed",
             f"- founding: {sum(1 for r in records if len(r.get('founded', '')) == 10):,} to the day, "
             f"{sum(1 for r in records if 0 < len(r.get('founded', '')) < 10):,} to the month or year, {sum(1 for r in records if not r.get('founded')):,} unknown",
             f"- {len(uni):,} unicorns; {sum(1 for r in uni if r.get('wikidata')):,} matched to Wikidata; {sum(1 for r in uni if r.get('date')):,} cast for their founding day",
             f"- {len(priv):,} of the largest unlisted companies by revenue (state-owned or private); {sum(1 for r in priv if r.get('date')):,} cast for their founding day",
             "", "## Yahoo Finance's first trading day, exchange by exchange", "",
             "Yahoo's first trading day is its price history's first day: the listing day for a company listed after Yahoo's data for the "
             "exchange begins, the start of its data for one listed before. A day many symbols share is such a start and never used "
             "(below). On the US markets the rest are used before Wikidata: checked against it, Yahoo had Microsoft's, Home Depot's, "
             "Amgen's and FedEx's IPO days where Wikidata's start time was a later move between exchanges, a renaming or a bulk import. "
             "Elsewhere Yahoo stands for a listing day only from the date below on, from which 90% of its days agree within 3 days with "
             "the exchange's list or Wikidata. An exchange with too few days checked to find that date takes " + YAHOO_SINCE + ", from "
             "which the days of all the exchanges off the US, pooled, agree 90% of the time (most of the rest are Yahoo counting a "
             "company's trading on another board before its move, or missing its first few days).", "",
             "| MIC | exchange | checked | trusted from | agree after |", "|---|---|---|---|---|"]
    for mic in sorted(pairs, key=lambda m: -len(pairs[m])):
        ps = pairs[mic]
        after = [p for p in ps if mic in cutoff and p[0] >= cutoff[mic]]
        good = sum(abs((date.fromisoformat(a) - date.fromisoformat(b)).days) <= 3 for a, b in after)
        lines.append(f"| {mic} | {EXCHANGES[mic][0]} | {len(ps)} | {'always (US)' if mic in US else cutoff.get(mic, YAHOO_SINCE + ' (pooled)')} | {f'{good}/{len(after)}' if after else '—'} |")
    lines += ["", "Days Yahoo's histories start on, not used (market, day, symbols): " +
              "; ".join(f"{g} {d} ({n})" for g, d, n in report["floors"]) + ".",
              "", "Wikidata start times shared by 10 or more listings of a market, taken for bulk imports and not used: " +
              "; ".join(f"{g} {d}" for g, d in report["bulk"]) + ". Tokyo's 1949-05-16, the exchange's reopening, is kept.",
              "", f"## Listing days the sources disagree on ({len(report['conflicts'])})", "", "The first source is the one kept.", "",
              "| company | exchange | kept | day | other | day |", "|---|---|---|---|---|---|"]
    lines += [f"| {a} | {b} | {c} | {d} | {e} | {f} |" for a, b, c, d, e, f in report["conflicts"]]
    named = {r["source"].rsplit("/", 1)[-1]: r["name"] for r in records if "wikidata.org" in r["source"]}
    lines += ["", f"## First trading days looked up by hand ({len(CURATED)})", ""]
    lines += [f"- {named.get(q, q)}: {EXCHANGES[m][0]}, {d} ([{who}]({url}))" for q, (m, d, who, url) in CURATED.items()]
    lines += ["", f"## First trades timed by the Rodden library ({len(report['lent'])})", ""] + [f"- {a}, {b} {c} ({d})" for a, b, c, d in report["lent"]]
    lines += ["", f"## Listed before the founding year Wikidata gives ({len(report['before_founding'])})", "",
              "Usually a predecessor's listing or an inception that is a later re-founding.", ""]
    lines += [f"- {a}: listed {b} ({c}), founded {d}" for a, b, c, d in report["before_founding"]]
    lines += ["", f"## Index members not found among the companies ({len(report['unmatched_index'])})", ""]
    lines += [f"- {a}: {b}" for a, b in report["unmatched_index"]]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {len(records):,} records to {OUT.relative_to(ROOT)} ({OUT.stat().st_size / 1e6:.1f} MB)", file=sys.stderr)


def main() -> None:
    stage = sys.argv[1] if len(sys.argv) > 1 else "all"
    if stage in ("fetch-yahoo", "all"):
        yahoo_profiles([c["symbol"] for c in market_caps()])
    if stage in ("fetch-exchanges", "all"):
        official_dates()
    if stage in ("fetch-wiki", "all"):
        wd_listings(), wd_mics(), wd_details("listed")
        index_members(), unicorn_titles(), unicorns()
    if stage in ("build", "all"):
        build(fetch_yahoo=stage == "all")   # "build" alone uses the Yahoo profiles cached so far


if __name__ == "__main__":
    main()
