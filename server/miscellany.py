"""The Miscellany tabs that are not modes: Panchanga and Laghu Parasari."""
import dataclasses
import math

from core_logic import ephemeris as E, longitude_sums as L, daily_panchanga as JP, time_search as JS, varga_charts as V, kp_astrology as KP

from .basics import MONTHS, PLANET_ABBR, PLANETS, SIGNS, _points, _tables

# point numbers of longitude_sums.rows, by the names of basics.POINT_ORDER
POINTS = {"Lagna": 0, "Sun": 1, "Moon": 2, "Mars": 3, "Mercury": 4, "Jupiter": 5, "Venus": 6, "Saturn": 7, "Rahu": 8,
          "Ketu": 9, "Bhava Lagna": 13, "Hora Lagna": 14, "Ghati Lagna": 15, "Vighati Lagna": 16, "Pranapada Lagna": 17,
          "Sree Lagna": 18, "Indu Lagna": 19, "Dhooma": 22, "Vyatipata": 23, "Parivesha": 24, "Indra Chapa": 25,
          "Upaketu": 26, "Kaala": 27, "Mrityu": 28, "Artha Prahara": 29, "Yama Ghantaka": 30, "Maandi": 31, "Gulika": 32}


def panchanga_day(birth, y, m, d, cfg):
    """One day as the Panchanga tab prints it; a '*' marks a time after midnight."""
    t = _tables()[0]
    r = JP.civil_day_panchanga(birth, y, m, d, cfg)
    midnight = E.julian_day_ut(y, m, d, -birth.tz_east_hours, birth.gregorian)

    def text(mins):
        return "%d:%02d%s" % (mins // 60 % 24, mins % 60, "*" if mins >= 1440 else "")

    def at(jd):         # kalams, muhurtas, rises and sets: rounded to the minute
        return text(round((jd - midnight) * 1440.0))

    def cut(jd):        # ends of the five elements, horas and choghadiyas: cut to the minute (panchanga_month.txt, 62 of 62 tithis)
        return text(math.floor((jd - midnight) * 1440.0))
    span = lambda v: "%s - %s" % (at(v[0]), at(v[1]))  # noqa: E731

    def ends(key, name, suffix=""):
        now = r[key + "_ends"]
        if not now:
            return ["%s%s (whole day)" % (name(r[key]), suffix)]
        return ["%s%s till %s" % (name(i), suffix, cut(end)) for i, end in now]
    karana = lambda i: t["karanas"][E._karana_index(i)]  # noqa: E731
    moon = ends("moon_sign", lambda s: "Moon in " + SIGNS[s])
    lines = [
        [t["weekdays"][r["weekday"]]] + ends("tithi", lambda i: t["tithis"][i]),
        ends("nakshatra", lambda i: t["nakshatras"][i]) + ends("yoga", lambda i: t["yogas"][i], " yoga"),
        ends("karana", karana, " karana"),
        ["RahuK: " + span(r["rahu_kala"]), "GulikaK: " + span(r["gulika_kala"]), "YamaG: " + span(r["yamaganda"])],
        (["Varjya: " + ", ".join(span(v) for v in r["varjya"])] if r["varjya"] else [])
        + ["Durmuhurta: " + ", ".join(span(v) for v in r["durmuhurta"])],
        ["Sunrise at " + at(r["sunrise"]), "Sunset at " + at(r["sunset"]), "Moonrise at " + at(r["moonrise"]),
         "Moonset at " + at(r["moonset"])] + moon]
    return {"date": "%s %d, %d" % (MONTHS[m - 1], d, y), "lines": [", ".join(ln) for ln in lines],
            "horas": [[PLANET_ABBR[lord - 1], cut(end)] for lord, _, end in r["horas"]],
            "gouri": [[t["gouri_periods"][i], cut(end)] for i, _, end in r["day_parts"]]}


def panchanga(birth, cfg, offset, days):
    """``days`` days, from ``offset`` days after the chart's date."""
    noon = E.julian_day_ut(birth.year, birth.month, birth.day, 12.0, birth.gregorian) + offset
    out = []
    for k in range(days):
        y, m, d, _ = E.jd_to_calendar(noon + k, birth.gregorian)
        out.append(panchanga_day(birth, y, m, d, cfg))
    return out


def laghu_parasari(birth, ch, cfg, mode, added, span_days=None, division=1, count_signs=True, one_cycle=False):
    """The longitude-sum explorer: dates and ages of the combinations of ``mode`` bodies, each sum with the lagna ``added``
    (a name of longitude_sums.ADDED_LAGNAS, or None), in D-``division`` by counting signs or finding longitudes. Ages of an event chart fit into its span; ``one_cycle`` keeps its first column only."""
    lons = {i: lon for name, lon in _points(ch).items() if (i := POINTS.get(name)) is not None}
    to_date = E.dasa_year_mapper(birth, cfg) if span_days is None else (
        lambda years: KP.kp_period_date(birth, years, cfg, span_days=span_days))
    rows = L.rows(lons, to_date, mode, None if added is None else L.ADDED_LAGNAS[added], V.DIVISIONS.index(division), count_signs)
    point = None if added is None else L.ADDED_LAGNAS[added]
    keep = 1 if one_cycle and span_days is not None else None
    return [{"label": L.label(combo, point), "cells": [[date.date(), round(age, 2)] for age, date in cols[:keep]]} for combo, cols in rows]


def _clock(hours):
    secs = round(hours * 3600) % 86400
    return "%d:%02d:%02d" % (secs // 3600, secs % 3600 // 60, secs % 60)


def _ephemeris(birth, cfg, year, month, day, days):
    """Copy monthly ephemeris: each day at 5:30 am of the chart's zone, tab-separated."""
    out = ["", "Monthly Ephemeris for %s, %d (at 5:30 am everyday):" % (MONTHS[month - 1], year), "", "Date\tDay\tSunrise\tSunset   \tSidTime    \tSun    \tMoon   \tMars   \tMercury \tJupiter  \tVenus   \tSaturn   \tRahu"]
    first = E.julian_day_ut(year, month, day, 5.5 - birth.tz_east_hours, birth.gregorian)
    weekdays = _tables()[0]["weekdays"]
    for k in range(days):
        y, m, d, _ = E.jd_to_calendar(first + k + birth.tz_east_hours / 24.0, birth.gregorian)
        at = dataclasses.replace(birth, year=y, month=m, day=d, hour_local=5.5)
        sun, pos = E.sunrise_sunset(at, cfg), E.planet_positions(at.jd_ut, cfg)
        sid = E.house_cusps(at.jd_ut, birth.latitude, birth.longitude_east, "PORPHYRY", cfg).get("armc", 0.0) / 15.0
        cells = []
        for p in PLANETS[:8]:
            secs = round(pos[p]["lon"] * 3600)
            cells.append("%03d:%02d:%02d" % (secs // 3600 % 360, secs % 3600 // 60, secs % 60))
        out.append("\t".join(["%d" % d, weekdays[E.day_lords(at, cfg)["weekday"]], _clock(sun["sunrise_hours"]), _clock(sun["sunset_hours"]), _clock(sid)] + cells))
    return "\n".join(out)


def _when(birth, jd):
    y, mo, d, h = E.jd_to_calendar(jd + birth.tz_east_hours / 24.0, birth.gregorian)
    return "%d\t%s" % (d, _clock(h))


def _entries(birth, cfg, jd0, jd1, part, names):
    """Each planet's "%s enters %s %d %s" lines of the monthly movements, planet by planet and without the Moon: its moves on into the next part from the start of the span, then from the start again its moves back over the start of the part it is in."""
    n, out = len(names), []
    for i, p in enumerate(PLANETS):
        if p == "Moon":
            continue
        lon = JS.body_longitude(i + 1, cfg, birth)
        for ahead, shown in ((1, 0), (0, -1)):
            j = jd0
            while True:
                at = (int(lon(j) // part) + ahead) % n
                j = JS.longitude_event(j, i + 1, at * part, cfg=cfg, birth=birth, stop=jd1)
                if j > jd1:
                    break
                out.append("%s\tenters\t%s\t%s" % (p, names[(at + shown) % n], _when(birth, j)))
    return out


# the body pairs the movements skip: Rahu and Ketu are always opposite, and the Sun, Mercury and Venus cannot get far enough apart
NO_ASPECT = {(1, 4), (1, 6), (4, 6), (8, 9)}
# lon(a) - lon(b), and the label for b counted from a, then for a counted from b (only the 4/10 and 5/9 pairs list the second)
ASPECTS = ((270.0, "[4]", "[10]"), (150.0, "[8]", None), (240.0, "[5]", "[9]"), (120.0, "[9]", "[5]"), (300.0, "[3]", None), (90.0, "[10]", "[4]"))


def _aspects(birth, cfg, jd0, jd1):
    """"Planetary aspects of Jyotish" of the monthly movements: every moment in the span two of the nine are exactly conjunct [C], opposite [S] or in the angles of ASPECTS, by time. Each 4/10 and 5/9 is found once from each body of the pair, and listed both times."""
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
            out += [(j, "%s\t[C]\t%s\t%s" % (PLANET_ABBR[a - 1], PLANET_ABBR[b - 1], _when(birth, j))) for j in hits(a, b, 0.0)]
            if (a, b) not in NO_ASPECT:
                out += [(j, "%s\t[S]\t%s\t%s" % (PLANET_ABBR[a - 1], PLANET_ABBR[b - 1], _when(birth, j))) for j in hits(a, b, 180.0)]
    for a in range(1, 10):
        for target, first, second in ASPECTS:
            for b in range(1, 10):
                if a == b or (min(a, b), max(a, b)) in NO_ASPECT:
                    continue
                for j in hits(a, b, target):
                    out.append((j, "%s\t%s\t%s\t%s" % (PLANET_ABBR[a - 1], first, PLANET_ABBR[b - 1], _when(birth, j))))
                    if second:
                        out.append((j, "%s\t%s\t%s\t%s" % (PLANET_ABBR[b - 1], second, PLANET_ABBR[a - 1], _when(birth, j))))
    return [ln for _, ln in sorted(out, key=lambda r: r[0])]


def _movements(birth, cfg, year, month, day, days):
    """Copy monthly planetary movements."""
    jd0 = E.julian_day_ut(year, month, day, -birth.tz_east_hours, birth.gregorian)
    jd1 = jd0 + days
    t = _tables()[0]
    return "\n".join(["", "Graha Movements for %s, %d:" % (MONTHS[month - 1], year), "", "Entry of grahas into signs", "", *_entries(birth, cfg, jd0, jd1, 30.0, t["signs"]),
                      "", "Entry of grahas in nakshatras", "", *_entries(birth, cfg, jd0, jd1, 360.0 / 27.0, t["nakshatras"]),
                      "", "Graha aspects of Jyotish:", "", *_aspects(birth, cfg, jd0, jd1)])


# The monthly panchanga, DP format: one tab-separated line a day
DP_HEAD = ("Gregorian Date\tYear\tMonth\tFullDate\tYearName\tAyana\tRitu\tSidSolarMonth\tLunarMonth\tPaksha\tTithi\tTithiEndTime\tRahuKala\tDay\tNakshatra\tNakshatraEndTime\tYoga\tKarana\t"
           "Varjya1Start\tVarjya1End\tVarjya2Start\tVarjya2End\tDurMuhurta1Start\tDurMuhurta1End\tDurMuhurta2Start\tDurMuhurta2End\tSunrise\tSunset\t"
           "R1\tL1\tR2\tL2\tR3\tL3\tR4\tL4\tR5\tL5\tR6\tL6\tR7\tL7\tR8\tL8\tR9\tL9\tR10\tL10\tR11\tL11\tR12\tL12\t")
RITUS = ["Vasanta", "Grishma", "Varsha", "Sharad", "Hemanta", "Sisira"]


def _dp_line(birth, y, m, d, cfg):
    """shortcut: the columns read from the same tables as the Panchanga tab; R1 .. L12 are taken as the rising signs and their end times."""
    t = _tables()[0]
    r = JP.civil_day_panchanga(birth, y, m, d, cfg)
    midnight = E.julian_day_ut(y, m, d, -birth.tz_east_hours, birth.gregorian)
    at = lambda jd: "%d:%02d" % (round((jd - midnight) * 1440.0) // 60 % 24, round((jd - midnight) * 1440.0) % 60)  # noqa: E731
    noon = dataclasses.replace(birth, year=y, month=m, day=d, hour_local=12.0)
    ch = E.build_chart(noon, cfg, "PORPHYRY")
    p = E.panchanga(noon, ch, cfg)
    sun = ch["planet_longitudes"]["Sun"]
    trop = (sun + ch["ayanamsa"]) % 360.0
    ayana = "Uttarayana" if trop >= 270.0 or trop < 90.0 else "Dakshinayana"
    pairs = lambda v, n: [at(x) for s in v[:n] for x in s] + [""] * (2 * n - 2 * min(n, len(v)))  # noqa: E731
    tithi = r["tithi_ends"][0] if r["tithi_ends"] else (r["tithi"], None)
    star = r["nakshatra_ends"][0] if r["nakshatra_ends"] else (r["nakshatra"], None)
    cells = ["%d-%02d-%04d" % (m, d, y), "%04d" % y, MONTHS[m - 1], str(d), t["samvatsaras"][p["samvatsara"]], ayana, RITUS[int(((trop + 30.0) % 360.0) // 60)], SIGNS[int(sun // 30)], t["lunar_months"][p["lunar_month"]],
             "Sukla" if tithi[0] < 15 else "Krishna", t["tithis"][tithi[0]], at(tithi[1]) if tithi[1] else "", "%s - %s" % (at(r["rahu_kala"][0]), at(r["rahu_kala"][1])), t["weekdays"][r["weekday"]],
             t["nakshatras"][star[0]], at(star[1]) if star[1] else "", t["yogas"][r["yoga_ends"][0][0] if r["yoga_ends"] else r["yoga"]], t["karanas"][E._karana_index(r["karana_ends"][0][0] if r["karana_ends"] else r["karana"])],
             *pairs(r["varjya"], 2), *pairs(r["durmuhurta"], 2), at(r["sunrise"]), at(r["sunset"])]
    j, end = midnight, midnight + 1.0
    rises = []
    for _ in range(14):
        if j >= end:
            break
        b = dataclasses.replace(noon, hour_local=(j - midnight) * 24.0)
        sign = E.build_chart(b, cfg, "PORPHYRY")["lagna_sign"]
        j += JS.varga_window(j, 0, 1, cfg, b)[1] + 1.0 / 1440.0
        rises += [SIGNS[sign], at(min(j, end))]
    return "\t".join(cells + (rises + [""] * 24)[:24])


def monthly_text(birth, ch, cfg, kind, year, month, day, days):
    """What Copy puts on the clipboard from the Panchanga menu, from a date: the panchanga, its DP format, the ephemeris at 5:30 am and the planetary movements."""
    if kind == "ephemeris":
        return _ephemeris(birth, cfg, year, month, day, days)
    if kind == "movements":
        return _movements(birth, cfg, year, month, day, days)
    noon = E.julian_day_ut(year, month, day, 12.0, birth.gregorian)
    out = [DP_HEAD] if kind == "dp" else []
    for k in range(days):
        y, m, d, _ = E.jd_to_calendar(noon + k, birth.gregorian)
        if kind == "dp":
            out.append(_dp_line(birth, y, m, d, cfg))
        else:
            r = panchanga_day(birth, y, m, d, cfg)
            out.append("%s:\n" % r["date"] + "\n".join("    %s," % ln for ln in r["lines"]) + "\n    Horas: " + ", ".join("%s %s" % (a, b) for a, b in r["horas"]) + "\n    Gouri Panchanga: " + ", ".join("%s %s" % (a, b) for a, b in r["gouri"]))
    return "\n".join(out) if kind == "dp" else "\n\n".join(out)
