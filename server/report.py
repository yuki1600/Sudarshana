"""Edit > Copy basic calculations and Copy complete calculations: the whole chart as text."""
from core_logic import ephemeris as E, dasa_systems as J

from . import basics as B, charts as CH, dasas as D, settings as S, strengths as ST, tables as TB


def _lon(x):
    h = round((x % 360.0) * 360000) % 129600000
    return "%2d %s %02d' %05.2f\"" % (h // 360000 % 30, B.SIGNS[h // 10800000], h % 360000 // 6000, h % 6000 / 100.0)


def header(b, ch, cfg, s, name, title, place=""):
    core = dict(B.core_info(b, ch, cfg, s))
    line = lambda k: "%-14s %s" % (k + ":", core[k])  # noqa: E731
    return [name, "", title, "", *[line(k) for k in ("Date", "Time", "Time Zone", "Place")], *(["%-14s %s" % ("", place)] if place else []), line("Altitude"), "",
            *[line(k) for k in ("Lunar Yr-Mo", "Tithi", "Vedic Weekday", "Nakshatra", "Yoga", "Karana", "Hora Lord", "Mahakala Hora", "Kaala Lord")], "",
            *[line(k) for k in ("Sunrise", "Sunset", "Janma Ghatis")], "", *[line(k) for k in ("Ayanamsa", "Sidereal Time")], ""]


def points(ch, s):
    rows = []
    for r in B.points_table(ch, s):
        label = r["name"] + (" (R)" if r["retrograde"] else "") + (" - %s" % r["karaka"] if r["karaka"] else "")     # the nodes too, by their motion
        rows.append("%-24s%-17s%-10s%-5d%-5s%s" % (label, _lon(r["lon"]), r["nakshatra"], r["pada"], B.SIGNS[r["rasi"]], B.SIGNS[r["navamsa"]]))
    return ["Body                    Longitude        Nakshatra Pada Rasi Navamsa", "", *rows, ""]


def chart_box(ch, s, d):
    p = CH.panel(ch, s, CH.ChartSpec(kind="varga", d=d), retro_all=True)
    return CH.text_south(p).split("\n") + [" "]


def _short(label):
    return {"Me": "Merc", "Ma": "Mars", "Ju": "Jup", "Ve": "Ven", "Sa": "Sat", "Su": "Sun", "Mo": "Moon", "Ra": "Rah", "Ke": "Ket", "Asc": "Asc"}.get(label, label)


TITLES = {"vimsottari_dasa": "Vimsottari Dasa ()", "moola_dasa": "Moola Dasa (dasa showing the root of events - past karma)", "ashtottari_dasa": "Ashtottari Dasa (conditional nakshatra dasa)",
          "narayana_dasa_of_d_1_chart": "Narayana Dasa of D-1 chart (a versatile phalita rasi dasa)", "sudasa": "Sudasa (phalita dasa showing Lakshmi's blessings)"}


def kalachakra_title(ch, rohini_4_leo=True):
    """The Kalachakra dasa's heading (BPHS 46.52-95): the seed's row of the table, its years, and the signs that start and end it."""
    moon = ch["planet_longitudes"]["Moon"]
    p = int(moon / J.PADA) % 108
    e0 = J._kc_table_row(p, rohini_4_leo) * 9
    row = [e0 // 9 * 9 + j for j in range(9)]
    years = sum(J.KALACHAKRA_YEARS[J.KALACHAKRA_SIGNS[(p + i) % 108]] for i in range(9))     # the nine periods listed (the default method's), not the row
    deha, jiva = (row[0], row[-1]) if e0 < 108 else (row[-1], row[0])       # an apasavya row runs backward
    return "Kalachakra Dasa (From Moon of D-1, %s, Paramayush: %d yr, Deha: %s, Jiva: %s)" % ("Savya" if e0 < 108 else "Apasavya", years, B.SIGNS[J.KALACHAKRA_SIGNS[deha]], B.SIGNS[J.KALACHAKRA_SIGNS[jiva]])


def dasa_block(b, ch, cfg, s, key, title=None, cycle=None):
    d = D.BY_KEY[key]
    jc = S.jchart(ch, E.day_lords(b, cfg, **S.day_kw(s)), s)
    to_date = S.year_mapper(b, cfg, s)
    kw = D.options(key, s)
    mds = d.build(jc, to_date, **kw)
    rule = d.rule(jc, kw) if d.rule else None
    out = ["%s:" % (title or TITLES.get(key, d.title + " Dasa")), ""]
    for i, m in enumerate(mds[:cycle]):
        subs = J.sub_periods(mds, to_date, [i], rule)
        head = _short(d.label(m))
        pad = " " * (len(head) + 2)
        cells = ["%s %s" % (_short(d.label(a)), a["start"].strftime("%Y-%m-%d") if a["start"].year >= 1000 else a["start"].isoformat()[:10]) for a in subs]
        for k in range(0, len(cells), 3):
            out.append((head + "  " if k == 0 else pad) + "".join(c + "  " for c in cells[k:k + 3]))
    return out + [""]


def basic(b, ch, cfg, s, name, title="Natal Chart", place=""):
    return "\n".join(header(b, ch, cfg, s, name, title, place) + points(ch, s) + chart_box(ch, s, 1) + dasa_block(b, ch, cfg, s, "vimsottari_dasa")) + "\n"


def _table_text(t):
    width = [max(len(c), *(len(r[i]) for r in t["rows"])) for i, c in enumerate(t["columns"])]
    line = lambda cells: " ".join(c.ljust(w) for c, w in zip(cells, width)).rstrip()  # noqa: E731
    return [line(t["columns"]), "", *[line(r) for r in t["rows"]], ""]


COMPLETE_CHARTS = (1, 9, 2, 3, 4, 5, 6, 7, 8, 10, 11, 12, 16, 20, 24, 27, 30, 40, 45, 60, 81, 108, 144)
COMPLETE_DASAS = (("vimsottari_dasa", 9), ("moola_dasa", 9), ("ashtottari_dasa", 8), ("kalachakra_dasa", 9), ("narayana_dasa_of_d_1_chart", 12), ("sudasa", 12))     # one cycle of each


def _av(ch, s):
    av = ST.ashtakavarga_of(ch, s)
    rows = ["Ashtakavarga of Rasi Chart:", "", "      " + "  ".join(B.SIGNS)]
    for i, a in enumerate(["As"] + B.PLANET_ABBR[:7]):
        rows.append("%-5s" % a + "".join(("%d%s" % (n, "*" if g == av["signs"][i] else "")).ljust(4) for g, n in enumerate(av["bav"][i])))
    rows += ["", "      Sodhya Pinda  Rasi Pinda  Graha Pinda"]
    for i, a in enumerate(["As"] + B.PLANET_ABBR[:7]):
        rows.append("%-3s          %3d         %3d          %3d" % (a, *av["pindas"][i]))
    return rows + [""]


def _strengths(b, ch, cfg, s):
    sb = ST.shadbala_of(b, ch, cfg)["planets"]
    out = _table_text({"columns": ["Graha", "Shadbala", "In rupas", "% Bala", "IshtaPhala", "KashtaPhala"], "rows": [[p["name"], "%.2f" % p["total"], "%.2f" % p["rupas"], "%.2f" % p["percent"], "%.2f" % p["ishta"], "%.2f" % p["kashta"]] for p in sb]})
    v = TB.vaiseshikamsa(b, ch, cfg, s)
    out += _table_text({"columns": ["Vaiseshikamsas", "Dasa Varga (10)", "Shodasa Varga (16)"], "rows": [r[:3] for r in v["rows"]]})
    vim = ST.vimsopaka_of(ch, s)
    cell = lambda x: "%.2f  (%.2f%%)" % (x, x * 5.0)  # noqa: E731
    out += _table_text({"columns": ["Vimsopaka", "Dasa Varga (10)", "Shodasa Varga (16)", "Sapta Varga (7)", "Shad Varga (6)"], "rows": [[r["name"], cell(r["dasa"]), cell(r["shodasa"]), cell(r["sapta"]), cell(r["shad"])] for r in vim]})
    out += _table_text(TB.avasthas(b, ch, cfg, s))
    act = TB.sayanadi(b, ch, cfg, s)
    out += _table_text({"columns": act["columns"][:2], "rows": [r[:2] for r in act["rows"]]})
    return out


def complete(b, ch, cfg, s, name, title="Natal Chart", place=""):
    lines = header(b, ch, cfg, s, name, title, place) + points(ch, s) + _table_text(TB.karakas(b, ch, cfg, s)) + _av(ch, s) + _strengths(b, ch, cfg, s)
    for d in COMPLETE_CHARTS:
        lines += chart_box(ch, s, d)
    for key, cycle in COMPLETE_DASAS:
        lines += dasa_block(b, ch, cfg, s, key, kalachakra_title(ch) if key == "kalachakra_dasa" else None, cycle)
    return "\n".join(lines) + "\n"
