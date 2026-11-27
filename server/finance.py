"""Market OHLC (Yahoo stocks + CCXT crypto) and astrology event overlays for the Finance tab."""
from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Any, Optional
from urllib.parse import quote

import httpx

from core_logic import ephemeris as E, time_search as JS

from .basics import PLANETS, SIGNS

# bodies that station (Sun/Moon/nodes do not give useful stations here)
STATION_BODIES = (("Mercury", 4), ("Venus", 6), ("Mars", 3), ("Jupiter", 5), ("Saturn", 7))
OUTER = ("Uranus", "Neptune", "Pluto")
YAHOO_RANGES = {"1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"}
YAHOO_INTERVALS = {"1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo"}
# fixed window length for each Yahoo/CCXT range label (pan slides this window; duration stays put)
RANGE_MS = {
    "1d": 86_400_000,
    "5d": 5 * 86_400_000,
    "1mo": 30 * 86_400_000,
    "3mo": 90 * 86_400_000,
    "6mo": 180 * 86_400_000,
    "1y": 365 * 86_400_000,
    "2y": 730 * 86_400_000,
    "5y": 1825 * 86_400_000,
    "10y": 3650 * 86_400_000,
    "ytd": 365 * 86_400_000,
    "max": 3650 * 86_400_000,
}
# shortcut: Yahoo chart endpoint is unofficial and may rate-limit or change; swap to a keyed provider when that breaks
YAHOO_CHART = "https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
UA = "Mozilla/5.0 (compatible; Sudarshana/0.1; +https://github.com/)"


def _iso(jd: float, tz_east: float) -> str:
    y, m, d, h = E.jd_to_calendar(jd + tz_east / 24.0, True)
    secs = int(round(h * 3600)) % 86400
    return "%04d-%02d-%02dT%02d:%02d:%02d" % (y, m, d, secs // 3600, secs % 3600 // 60, secs % 60)


def _ms(jd: float) -> int:
    """Unix ms from JD UT (J2000 epoch bridge via calendar)."""
    y, m, d, h = E.jd_to_calendar(jd, True)
    secs = int(round(h * 3600))
    return int(datetime(y, m, d, secs // 3600, (secs % 3600) // 60, secs % 60, tzinfo=timezone.utc).timestamp() * 1000)


def _parse_symbol(symbol: str) -> tuple[str, Optional[str], str]:
    """Return (source, exchange_or_None, market_symbol). ``binance:BTC/USDT`` or ``BTC/USDT`` → ccxt; else yahoo."""
    s = symbol.strip()
    if not s:
        raise ValueError("Enter a symbol (e.g. AAPL or BTC/USDT).")
    if ":" in s and "/" in s.split(":", 1)[1]:
        ex, pair = s.split(":", 1)
        return "ccxt", ex.lower(), pair.upper()
    if "/" in s:
        return "ccxt", None, s.upper()
    return "yahoo", None, s.upper()


def _window_bounds(range_: str, end_ms: Optional[int], buffer: int = 1) -> tuple[int, int]:
    """Start/end (ms) for a range window ending at end_ms (or now). ``buffer`` multiplies the span so the UI can pan locally."""
    now = int(time.time() * 1000)
    end = min(int(end_ms), now) if end_ms is not None else now
    span = RANGE_MS.get(range_, 365 * 86_400_000) * max(1, min(int(buffer or 1), 10))
    return end - span, end


def yahoo_ohlc(symbol: str, range_: str = "1y", interval: str = "1d", end_ms: Optional[int] = None,
               buffer: int = 1) -> dict[str, Any]:
    if range_ not in YAHOO_RANGES:
        raise ValueError("range must be one of: %s" % ", ".join(sorted(YAHOO_RANGES)))
    if interval not in YAHOO_INTERVALS:
        raise ValueError("interval must be one of: %s" % ", ".join(sorted(YAHOO_INTERVALS)))
    start_ms, end = _window_bounds(range_, end_ms, buffer)
    url = YAHOO_CHART.format(symbol=quote(symbol, safe="^=."))
    p1 = max(0, start_ms // 1000)
    p2 = max(p1 + 1, end // 1000 + 1)  # Yahoo's period2 is exclusive
    params = {"period1": p1, "period2": p2, "interval": interval, "events": "div,splits"}
    with httpx.Client(timeout=30.0, headers={"User-Agent": UA}) as client:
        r = client.get(url, params=params)
    if r.status_code == 404:
        raise ValueError("Yahoo has no data for %s." % symbol)
    if r.status_code == 429:
        raise ValueError("Yahoo rate-limited the request; try again shortly.")
    r.raise_for_status()
    payload = r.json()
    result = (payload.get("chart") or {}).get("result")
    if not result:
        err = ((payload.get("chart") or {}).get("error") or {}).get("description") or "no chart data"
        raise ValueError("Yahoo: %s" % err)
    meta, ts = result[0].get("meta") or {}, result[0].get("timestamp") or []
    q = ((result[0].get("indicators") or {}).get("quote") or [{}])[0]
    o, h, l, c, v = q.get("open") or [], q.get("high") or [], q.get("low") or [], q.get("close") or [], q.get("volume") or []
    bars = []
    for i, t in enumerate(ts):
        if i >= len(c) or c[i] is None:
            continue
        bars.append({
            "t": int(t) * 1000,
            "o": o[i] if i < len(o) else None,
            "h": h[i] if i < len(h) else None,
            "l": l[i] if i < len(l) else None,
            "c": c[i],
            "v": v[i] if i < len(v) else None,
        })
    return {
        "source": "yahoo",
        "symbol": meta.get("symbol") or symbol,
        "name": meta.get("longName") or meta.get("shortName") or symbol,
        "currency": meta.get("currency"),
        "exchange": meta.get("exchangeName") or meta.get("fullExchangeName"),
        "range": range_,
        "interval": interval,
        "end_ms": end,
        "bars": bars,
    }


def ccxt_ohlc(symbol: str, exchange: Optional[str] = None, range_: str = "1y", interval: str = "1d",
              end_ms: Optional[int] = None, buffer: int = 1) -> dict[str, Any]:
    try:
        import ccxt  # type: ignore
    except ImportError as e:
        raise ValueError("Install ccxt for crypto data: pip install ccxt") from e
    # map our interval labels to ccxt timeframes
    tf = {"1m": "1m", "5m": "5m", "15m": "15m", "30m": "30m", "60m": "1h", "1h": "1h", "1d": "1d", "1wk": "1w", "1mo": "1M"}.get(interval)
    if not tf:
        raise ValueError("CCXT interval must be one of 1m, 5m, 15m, 30m, 1h, 1d, 1wk, 1mo")
    start_ms, end = _window_bounds(range_, end_ms, buffer)
    name = (exchange or "binance").lower()
    if name not in ccxt.exchanges:   # an exchange's id only: getattr would reach anything else the module holds
        raise ValueError("Unknown CCXT exchange %r." % exchange)
    ex = getattr(ccxt, name)({"enableRateLimit": True})
    if not ex.has.get("fetchOHLCV"):
        raise ValueError("%s does not support OHLCV." % name)
    try:
        raw = ex.fetch_ohlcv(symbol, timeframe=tf, since=start_ms, limit=1000)
    except Exception as e:  # ccxt raises many typed errors
        raise ValueError("CCXT %s: %s" % (name, e)) from e
    bars = [{"t": int(row[0]), "o": row[1], "h": row[2], "l": row[3], "c": row[4], "v": row[5]}
            for row in raw if int(row[0]) <= end]
    return {
        "source": "ccxt",
        "symbol": symbol,
        "name": symbol,
        "currency": symbol.split("/")[-1] if "/" in symbol else None,
        "exchange": name,
        "range": range_,
        "interval": interval,
        "end_ms": end,
        "bars": bars,
    }


def ohlc(symbol: str, range_: str = "1y", interval: str = "1d", exchange: Optional[str] = None,
         end_ms: Optional[int] = None, buffer: int = 1) -> dict[str, Any]:
    source, ex, market = _parse_symbol(symbol)
    if exchange:
        source, ex = "ccxt", exchange.lower()
    if source == "ccxt":
        return ccxt_ohlc(market, ex, range_, interval, end_ms, buffer)
    return yahoo_ohlc(market, range_, interval, end_ms, buffer)


# common crypto pairs for typeahead when the query looks like a coin ticker
CRYPTO_HINTS = (
    ("BTC", "BTC/USDT", "Bitcoin"),
    ("ETH", "ETH/USDT", "Ethereum"),
    ("SOL", "SOL/USDT", "Solana"),
    ("XRP", "XRP/USDT", "XRP"),
    ("BNB", "BNB/USDT", "BNB"),
    ("DOGE", "DOGE/USDT", "Dogecoin"),
    ("ADA", "ADA/USDT", "Cardano"),
    ("AVAX", "AVAX/USDT", "Avalanche"),
    ("DOT", "DOT/USDT", "Polkadot"),
    ("LINK", "LINK/USDT", "Chainlink"),
    ("MATIC", "MATIC/USDT", "Polygon"),
    ("LTC", "LTC/USDT", "Litecoin"),
)
YAHOO_SEARCH = "https://query1.finance.yahoo.com/v1/finance/search"


def search_symbols(q: str, limit: int = 8) -> list[dict[str, Any]]:
    """Typeahead: Yahoo equity/ETF/index hits plus matching crypto pairs."""
    q = (q or "").strip()
    if len(q) < 1:
        return []
    limit = max(1, min(limit, 12))
    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    uq = q.upper()

    for coin, pair, name in CRYPTO_HINTS:
        if uq in coin or uq in pair or uq in name.upper():
            if pair not in seen:
                seen.add(pair)
                out.append({"symbol": pair, "name": name, "exchange": "binance", "type": "crypto", "source": "ccxt"})
            if len(out) >= limit:
                return out

    try:
        with httpx.Client(timeout=8.0, headers={"User-Agent": UA}) as client:
            r = client.get(YAHOO_SEARCH, params={"q": q, "quotesCount": limit, "newsCount": 0, "listsCount": 0})
        if r.status_code == 200:
            for row in (r.json().get("quotes") or []):
                sym = (row.get("symbol") or "").strip()
                if not sym or sym in seen:
                    continue
                seen.add(sym)
                out.append({
                    "symbol": sym,
                    "name": row.get("shortname") or row.get("longname") or sym,
                    "exchange": row.get("exchDisp") or row.get("exchange") or "",
                    "type": row.get("quoteType") or row.get("typeDisp") or "equity",
                    "source": "yahoo",
                })
                if len(out) >= limit:
                    break
    except httpx.HTTPError:
        pass  # crypto hints alone still help
    return out[:limit]


def _ingresses(birth, cfg, jd0: float, jd1: float) -> list[dict]:
    out = []
    for i, p in enumerate(PLANETS):
        if p == "Moon":
            continue
        lon = JS.body_longitude(i + 1, cfg, birth)
        for ahead, shown in ((1, 0), (0, -1)):
            j = jd0
            while True:
                at = (int(lon(j) // 30.0) + ahead) % 12
                j = JS.longitude_event(j, i + 1, at * 30.0, cfg=cfg, birth=birth, stop=jd1)
                if j > jd1:
                    break
                sign = SIGNS[(at + shown) % 12]
                out.append({
                    "kind": "ingress",
                    "jd": j,
                    "t": _ms(j),
                    "iso": _iso(j, birth.tz_east_hours),
                    "bodies": [p],
                    "sign": sign,
                    "label": "Entry into %s" % sign,
                    "detail": "%s enters %s" % (p, sign),
                })
    return out


def _conjunctions(birth, cfg, jd0: float, jd1: float) -> list[dict]:
    """Exact conjunctions and oppositions between the nine (skip Rahu–Ketu and unreachable pairs)."""
    skip = {(1, 4), (1, 6), (4, 6), (8, 9)}

    def hits(a, b, target):
        j = jd0
        while True:
            j = JS.longitude_event(j, a, target, b, cfg=cfg, birth=birth, stop=jd1)
            if j > jd1:
                return
            yield j

    out = []
    for a in range(1, 10):
        for b in range(a + 1, 10):
            if (a, b) == (8, 9):
                continue
            for j in hits(a, b, 0.0):
                out.append({
                    "kind": "conjunction",
                    "jd": j,
                    "t": _ms(j),
                    "iso": _iso(j, birth.tz_east_hours),
                    "bodies": [PLANETS[a - 1], PLANETS[b - 1]],
                    "sign": None,
                    "label": "Conjunction",
                    "detail": "%s conjunct %s" % (PLANETS[a - 1], PLANETS[b - 1]),
                })
            if (a, b) not in skip:
                for j in hits(a, b, 180.0):
                    out.append({
                        "kind": "opposition",
                        "jd": j,
                        "t": _ms(j),
                        "iso": _iso(j, birth.tz_east_hours),
                        "bodies": [PLANETS[a - 1], PLANETS[b - 1]],
                        "sign": None,
                        "label": "Opposition",
                        "detail": "%s opposite %s" % (PLANETS[a - 1], PLANETS[b - 1]),
                    })
    return out


def _stations(birth, cfg, jd0: float, jd1: float) -> list[dict]:
    out = []
    for name, p in STATION_BODIES:
        j = jd0
        while j <= jd1:
            try:
                j, retro_after = JS.retrograde_station(j, p, True, cfg)
            except (ValueError, OverflowError):
                break
            if j > jd1:
                break
            out.append({
                "kind": "station",
                "jd": j,
                "t": _ms(j),
                "iso": _iso(j, birth.tz_east_hours),
                "bodies": [name],
                "sign": None,
                "label": "Retrogression" if retro_after else "Direct",
                "detail": "%s turns %s" % (name, "retrograde" if retro_after else "direct"),
                "retrograde": bool(retro_after),
            })
            j += 1.0 / 1440.0  # nudge past the station
    return out


def _combustions(birth, cfg, jd0: float, jd1: float) -> list[dict]:
    """Crossings of the 6° Sun orb for Mars..Saturn (the fixed-orb combustion boundary)."""
    out = []
    for p, name in ((3, "Mars"), (4, "Mercury"), (5, "Jupiter"), (6, "Venus"), (7, "Saturn")):
        for target in (6.0, 354.0):
            j = jd0
            while True:
                j = JS.longitude_event(j, p, target, 1, cfg=cfg, birth=birth, stop=jd1)
                if j > jd1:
                    break
                # after the crossing: inside orb ⇒ combustion begins; outside ⇒ ends
                sun = JS.body_longitude(1, cfg, birth)(j + 1.0 / 1440.0)
                pl = JS.body_longitude(p, cfg, birth)(j + 1.0 / 1440.0)
                sep = min((pl - sun) % 360.0, (sun - pl) % 360.0)
                into = sep <= 6.0 + 1e-6
                out.append({
                    "kind": "combustion",
                    "jd": j,
                    "t": _ms(j),
                    "iso": _iso(j, birth.tz_east_hours),
                    "bodies": [name, "Sun"],
                    "sign": None,
                    "label": "Combustion" if into else "Leaves combustion",
                    "detail": ("%s becomes combust" if into else "%s leaves combustion") % name,
                })
    return out


def _outer_lon(name: str, cfg):
    return lambda jd: E.planet_positions(jd, cfg, include_outer=True)[name]["lon"]


def _outer_speed(name: str, cfg):
    return lambda jd: E.planet_positions(jd, cfg, include_outer=True)[name]["speed"]


def _named_event(lon_fn, jd0: float, target: float, jd1: float, step: float = 40.0) -> float:
    """Crossing search for bodies outside the 0..9 index set (outer planets)."""
    f = lambda t: (lon_fn(t) - target) % 360.0  # noqa: E731
    return JS._crossing(f, jd0, step, JS.SECOND, jd1)


def _outer_ingresses(birth, cfg, jd0: float, jd1: float) -> list[dict]:
    out = []
    for name in OUTER:
        lon = _outer_lon(name, cfg)
        for ahead, shown in ((1, 0), (0, -1)):
            j = jd0
            while True:
                at = (int(lon(j) // 30.0) + ahead) % 12
                j = _named_event(lon, j, at * 30.0, jd1, step=60.0)
                if j > jd1:
                    break
                sign = SIGNS[(at + shown) % 12]
                out.append({
                    "kind": "ingress",
                    "jd": j,
                    "t": _ms(j),
                    "iso": _iso(j, birth.tz_east_hours),
                    "bodies": [name],
                    "sign": sign,
                    "label": "Entry into %s" % sign,
                    "detail": "%s enters %s" % (name, sign),
                })
    return out


def _outer_stations(birth, cfg, jd0: float, jd1: float) -> list[dict]:
    out = []
    for name in OUTER:
        speed = _outer_speed(name, cfg)
        j = jd0
        while j <= jd1:
            s0 = speed(j) < 0.0
            lo, hi, step = j, j + 40.0, 40.0
            found = False
            for _ in range(200):
                if hi > jd1 + step:
                    break
                if (speed(hi) < 0.0) != s0:
                    found = True
                    break
                lo, hi = hi, hi + step
            if not found:
                break
            while abs(hi - lo) > JS.SECOND:
                m = 0.5 * (lo + hi)
                if (speed(m) < 0.0) == s0:
                    lo = m
                else:
                    hi = m
            j = hi
            if j > jd1:
                break
            retro_after = not s0
            out.append({
                "kind": "station",
                "jd": j,
                "t": _ms(j),
                "iso": _iso(j, birth.tz_east_hours),
                "bodies": [name],
                "sign": None,
                "label": "Retrogression" if retro_after else "Direct",
                "detail": "%s turns %s" % (name, "retrograde" if retro_after else "direct"),
                "retrograde": bool(retro_after),
            })
            j += 1.0
    return out


def _outer_aspects(birth, cfg, jd0: float, jd1: float) -> list[dict]:
    """Conjunctions / oppositions of Uranus/Neptune/Pluto with Sun..Saturn."""
    out = []
    for name in OUTER:
        fa = _outer_lon(name, cfg)
        for b, other in enumerate(PLANETS[:7], start=1):
            fb = JS.body_longitude(b, cfg, birth)
            for target, kind, word in ((0.0, "conjunction", "conjunct"), (180.0, "opposition", "opposite")):
                j = jd0
                while True:
                    f = lambda t, _fa=fa, _fb=fb, _tg=target: (_fa(t) - _fb(t) - _tg) % 360.0  # noqa: E731
                    j = JS._crossing(f, j, 40.0, JS.SECOND, jd1)
                    if j > jd1:
                        break
                    out.append({
                        "kind": kind,
                        "jd": j,
                        "t": _ms(j),
                        "iso": _iso(j, birth.tz_east_hours),
                        "bodies": [name, other],
                        "sign": None,
                        "label": kind.capitalize(),
                        "detail": "%s %s %s" % (name, word, other),
                    })
    return out


def _eclipses(birth, jd0: float, jd1: float) -> list[dict]:
    out = []
    for kind in ("solar", "lunar"):
        j = jd0
        for _ in range(40):  # hard cap; ~2 eclipses/year/kind
            try:
                e = E.next_eclipse(j, kind, birth=None, backward=False)
            except Exception:
                break
            jmax = e["max_jd"]
            if jmax > jd1:
                break
            if jmax >= jd0:
                sign = SIGNS[int(e["sun_lon"] // 30)] if kind == "solar" else SIGNS[int(e["moon_lon"] // 30)]
                out.append({
                    "kind": "eclipse",
                    "jd": jmax,
                    "t": _ms(jmax),
                    "iso": _iso(jmax, birth.tz_east_hours),
                    "bodies": ["Sun", "Moon"] if kind == "solar" else ["Moon"],
                    "sign": sign,
                    "label": "%s eclipse" % kind.capitalize(),
                    "detail": "%s %s eclipse in %s" % (e["type"].capitalize(), kind, sign),
                    "eclipse": kind,
                    "type": e["type"],
                })
            j = jmax + 1.0 / 24.0
    return out


def events(birth, cfg, start_ms: int, end_ms: int,
           kinds: Optional[list[str]] = None) -> list[dict]:
    """Astrology events in [start_ms, end_ms] (unix ms UTC), for chart overlays."""
    if end_ms <= start_ms:
        raise ValueError("end must be after start")
    # ~3 years max — event search is O(planets × crossings)
    if end_ms - start_ms > 3 * 365.25 * 86400_000:
        raise ValueError("Overlay span is capped at 3 years.")
    start = datetime.fromtimestamp(start_ms / 1000.0, tz=timezone.utc)
    end = datetime.fromtimestamp(end_ms / 1000.0, tz=timezone.utc)
    jd0 = E.julian_day_ut(start.year, start.month, start.day, start.hour + start.minute / 60.0 + start.second / 3600.0, True)
    jd1 = E.julian_day_ut(end.year, end.month, end.day, end.hour + end.minute / 60.0 + end.second / 3600.0, True)
    want = set(kinds or ["ingress", "conjunction", "opposition", "station", "eclipse", "combustion"])
    out: list[dict] = []
    if "ingress" in want:
        out += _ingresses(birth, cfg, jd0, jd1)
        out += _outer_ingresses(birth, cfg, jd0, jd1)
    if want & {"conjunction", "opposition"}:
        for ev in _conjunctions(birth, cfg, jd0, jd1):
            if ev["kind"] in want:
                out.append(ev)
        for ev in _outer_aspects(birth, cfg, jd0, jd1):
            if ev["kind"] in want:
                out.append(ev)
    if "station" in want:
        out += _stations(birth, cfg, jd0, jd1)
        out += _outer_stations(birth, cfg, jd0, jd1)
    if "combustion" in want:
        out += _combustions(birth, cfg, jd0, jd1)
    if "eclipse" in want:
        out += _eclipses(birth, jd0, jd1)
    out.sort(key=lambda e: e["jd"])
    return out
