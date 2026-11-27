"""The Basics > Key Info screen: points table, Core Info lines, small ashtakavarga and chart placements.

Names come from data/string_tables.json and data/point_names.csv.
"""
import copy
import csv
import functools
import json
import os

from core_logic import ashtakavarga, ephemeris as E, time_search as JS, varga_charts as V, natal_chart as N, sahams_library as SL, sign_strength as SS, special_lagnas_upagrahas as U

from . import settings as S

_DATA = os.path.join(os.path.dirname(__file__), "..", "data")
PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
PLANET_ABBR = ["Su", "Mo", "Ma", "Me", "Ju", "Ve", "Sa", "Ra", "Ke"]
SIGNS = "Ar Ta Ge Cn Le Vi Li Sc Sg Cp Aq Pi".split()
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
          "November", "December"]
# the order of the Body table
POINT_ORDER = ["Lagna"] + PLANETS + [
    "Maandi", "Gulika", "Bhava Lagna", "Hora Lagna", "Ghati Lagna", "Vighati Lagna", "Varnada Lagna", "Sree Lagna",
    "Pranapada Lagna", "Indu Lagna", "Bhrigu Bindu", "Dhooma", "Vyatipata", "Parivesha", "Indra Chapa", "Upaketu",
    "Kaala", "Mrityu", "Artha Prahara", "Yama Ghantaka", "Prana Sphuta", "Deha Sphuta", "Mrityu Sphuta",
    "Sookshma TriSphuta", "Tithi Sphuta", "Yoga Sphuta (Sun-Moon)", "Rahu Tithi Sphuta", "Kshetra Sphuta",
    "Beeja Sphuta", "TriSphuta", "ChatusSphuta", "PanchaSphuta"] + ["V%d" % i for i in range(2, 13)] + [
    "Kunda", "Yoga Sphuta", "Avayoga Sphuta"]


@functools.lru_cache(maxsize=1)
def _tables():
    with open(os.path.join(_DATA, "string_tables.json"), encoding="utf-8") as f:
        t = json.load(f)
    with open(os.path.join(_DATA, "point_names.csv"), encoding="utf-8", newline="") as f:
        ab = [r["english_2"] for r in csv.DictReader(f)]
    return t, ab


def _points(ch):
    sl, up, sp = ch["special_lagnas"], ch["upagrahas"], ch["sphutas"]
    m = {"Lagna": ch["lagna_lon"], "Maandi": up["Mandi"], "Gulika": up["Gulika"], "Bhava Lagna": sl["Bhava_Lagna"],
         "Hora Lagna": sl["Hora_Lagna"], "Ghati Lagna": sl["Ghati_Lagna"], "Vighati Lagna": sl["Vighati_Lagna"],
         "Varnada Lagna": ch["varnada_lagnas"][0], "Sree Lagna": sl["Sree_Lagna"], "Pranapada Lagna": sl["Pranapada"],
         "Indu Lagna": sl["Indu_Lagna"], "Bhrigu Bindu": sl["Bhrigu_Bindu"], "Dhooma": up["Dhuma"],
         "Vyatipata": up["Vyatipata"], "Parivesha": up["Parivesha"], "Indra Chapa": up["Indra Chapa"],
         "Upaketu": up["Upaketu"], "Kaala": up["Kaala"], "Mrityu": up["Mrityu"], "Artha Prahara": up["Artha_Prahara"],
         "Yama Ghantaka": up["Yama_Ghantaka"], "Prana Sphuta": sp["prana_sphuta"], "Deha Sphuta": sp["deha_sphuta"],
         "Mrityu Sphuta": sp["mrityu_sphuta"], "Sookshma TriSphuta": sp["sookshma_trisphuta"],
         "Tithi Sphuta": sp["tithi_sphuta"], "Yoga Sphuta (Sun-Moon)": sp["yoga_sphuta"],
         "Rahu Tithi Sphuta": sp["rahu_tithi_sphuta"], "Kshetra Sphuta": sp["kshetra_sphuta"],
         "Beeja Sphuta": sp["beeja_sphuta"], "TriSphuta": sp["trisphuta"], "ChatusSphuta": sp["chatusphuta"],
         "PanchaSphuta": sp["panchasphuta"], "Kunda": sl["Kunda"], "Yoga Sphuta": sp["yogi_sphuta"],
         "Avayoga Sphuta": sp["avayogi_sphuta"]}
    m.update({"V%d" % (i + 1): ch["varnada_lagnas"][i] for i in range(12)})
    m.update(ch["planet_longitudes"])
    return m


KARAKA_SLOTS = ["AK", "AmK", "BK", "MK", "PiK", "PK", "GK", "DK"]


def body_group(name):
    """Which box of "Select the bodies to show" a row of the list answers to."""
    if name in PLANETS or name in ("Lagna", "Prasna Lagna", "Muntha"):
        return "planets"
    if name in ("Uranus", "Neptune", "Pluto"):
        return "outer"
    return {"Bhava Lagna": "lagnas", "Hora Lagna": "lagnas", "Ghati Lagna": "lagnas", "Vighati Lagna": "vighati", "Varnada Lagna": "varnada", "Sree Lagna": "sree", "Pranapada Lagna": "pranapada", "Indu Lagna": "indu",
            "Bhrigu Bindu": "bb", "Maandi": "mandi", "Gulika": "gulika", "Kunda": "kunda", "Yoga Sphuta": "yoga", "Avayoga Sphuta": "yoga", "Yoga Sphuta (Sun-Moon)": "sphutas", "AL": "al"}.get(name) or (
        "varnadas" if name[0] == "V" and name[1:].isdigit() else "upagrahas" if name in ("Dhooma", "Vyatipata", "Parivesha", "Indra Chapa", "Upaketu", "Kaala", "Mrityu", "Artha Prahara", "Yama Ghantaka")
        else "bhava_arudhas" if name[0] in "AU" and (name == "UL" or name[1:].isdigit()) else "graha_arudhas" if name.startswith("Arudha of") else "user" if name.startswith("User:") else "sphutas")


def user_points(birth, ch, cfg, s):
    """The user's special point and planetary special lagna, by their symbols."""
    out = {}
    nine = [ch["lagna_lon"]] + [ch["planet_longitudes"][p] for p in PLANETS]
    if s.special_point_on:
        kw = {"planet": {"planet": s.special_point_planet}, "sign": {"sign": s.special_point_sign}, "midpoint": {"midpoint": (s.special_point_planet, s.special_point_planet2)},
              "saham": {"saham": SL.saham_longitudes(nine[:8], E.day_lords(birth, cfg)["is_day"])[s.special_point_saham]}}[s.special_point_kind]
        out[s.special_point_symbol] = JS.special_point(nine, s.special_point_offset, after=s.special_point_after, **kw) % 360.0
    if s.special_lagna_on:
        lon = JS.special_lagna(birth, s.special_lagna_planet, s.special_lagna_speed, s.special_lagna_nodes_reverse, s.sunrise_definition, cfg)
        out[PLANET_ABBR[s.special_lagna_planet - 1] + str(s.special_lagna_speed)] = lon
    return out


def extra_points(ch, s, d, birth, cfg):
    """The bodies of "Select the bodies to show" beyond the default list: outer planets, house and graha arudhas (as the charts draw them)."""
    out = dict(ch.get("outer", {}))
    opt = S.varga_options(s)
    nine = [ch["lagna_lon"]] + [ch["planet_longitudes"][p] for p in PLANETS]
    signs = [V.varga_sign(x, d, opt) for x in nine]
    names = ["AL", "A2", "A3", "A4", "A5", "A6", "A7", "A8", "A9", "A10", "A11", "UL"]
    out.update({n: g * 30.0 for n, g in zip(names, SS.bhava_arudhas(signs, nine, s.arudha_exceptions_bhava, s.arudha_nodes))})
    out.update({"Arudha of " + PLANETS[p - 1]: SS.graha_arudha(p, signs, nine, s.arudha_exceptions_graha) * 30.0 for p in range(1, 10)})
    return out


def points_table(ch, s, d=1, users=None, extras=None):
    """The Key Info list; in D-``d`` the same bodies at their longitudes in that chart. ``users`` and ``extras`` add rows that are in the sign already (arudhas) or plain points."""
    nak_abbr = _tables()[0]["nakshatra_abbr"]
    lons = _points(ch)
    opt = S.varga_options(s)
    corr = ch.get("nakshatra_correction", 0.0)     # the sidereal nakshatras of a tropical chart
    star = lambda x: (x + corr) % 360.0  # noqa: E731
    nine = [ch["lagna_lon"]] + [ch["planet_longitudes"][p] for p in PLANETS]
    if d != 1:      # the chara karakas by the degrees the grahas have in this varga
        nine = [V.varga_longitude(x, d, opt) for x in nine]
    karaka_of = {}
    for slot, i in zip(KARAKA_SLOTS, N.chara_karaka_slots(nine, [int(x // 30) for x in nine], s.chara_karakas)):
        if i:       # a planet can hold two (PK merged with MK)
            name = (["Lagna"] + PLANETS)[i]
            karaka_of[name] = karaka_of[name] + "/" + slot if name in karaka_of else slot
    nav_of = lambda lon: V.varga_sign(lon, 9, opt)  # noqa: E731
    nav_lagna = nav_of(ch["lagna_lon"]) * 30.0
    nav_hora = nav_of(ch["special_lagnas"]["Hora_Lagna"]) * 30.0
    rows = []

    def row(name, lon, nav, retro=False, karaka=None, already_varga=False):
        x = lon if d == 1 or already_varga else V.varga_longitude(lon, d, opt)
        rows.append({"name": name, "lon": x, "nakshatra": nak_abbr[int(star(x) * 0.075)], "pada": int(star(x) * 0.3) % 4 + 1, "rasi": int(x // 30), "navamsa": nav if d == 1 else nav_of(x),
                     "retrograde": retro, "karaka": karaka, "group": body_group(name)})
    for name in POINT_ORDER:
        lon = lons[name]
        if name == "Varnada Lagna" or name[0] == "V" and name[1:].isdigit():
            house = 0 if name == "Varnada Lagna" else int(name[1:]) - 1
            nav = int(U.compute_varnada_lagnas(nav_lagna, nav_hora)[house] // 30)  # per-varga lagnas
        else:
            nav = nav_of(lon)
        row(name, lon, nav, bool(ch["retrograde"].get(name)), karaka_of.get(name))
    if ch.get("prasna_lagna") is not None:
        row("Prasna Lagna", ch["prasna_lagna"], nav_of(ch["prasna_lagna"]))
    if ch.get("muntha") is not None:      # the last row of a Tajaka chart
        row("Muntha", ch["muntha"], nav_of(ch["muntha"]))
    for name, lon in (users or {}).items():
        row("User: " + name, lon, nav_of(lon))
    for name, lon in (extras or {}).items():
        row(name, lon, nav_of(lon), already_varga=name not in ("Uranus", "Neptune", "Pluto"))
        if name in ("Uranus", "Neptune", "Pluto"):
            rows[-1]["dignity"] = outer_dignity(name, rows[-1]["rasi"], s)
    return rows


def outer_dignity(name, sign, s):
    """Uranus, Neptune or Pluto in ``sign``: exalted where the settings put it (the outer grahas' options), debilitated opposite, or in its own sign (also a setting)."""
    ex, own = getattr(s, name.lower() + "_exalted"), getattr(s, name.lower() + "_own")
    return "Exalted" if sign == ex else "Debilitated" if ex >= 0 and sign == (ex + 6) % 12 else "Own" if sign == own else None


def adjusted(ch, adj, base=None):
    """A chart with its bodies moved, for the charts that are not a moment: ``base`` (a chart whose longitudes this one takes),
    ``adj.arc`` added to every point; ``adj.lons`` in place of some planets; ``adj.lagna`` for the lagna, ``adj.prasna_lagna`` beside it."""
    ch = copy.deepcopy(ch)
    if base is not None:
        for k in ("lagna_lon", "planet_longitudes", "special_lagnas", "upagrahas", "sphutas", "varnada_lagnas"):
            ch[k] = copy.deepcopy(base[k])
    if adj.arc:
        move = lambda x: (x + adj.arc) % 360.0  # noqa: E731
        ch["lagna_lon"] = move(ch["lagna_lon"])
        ch["varnada_lagnas"] = [move(x) for x in ch["varnada_lagnas"]]
        for k in ("planet_longitudes", "special_lagnas", "upagrahas", "sphutas"):
            ch[k] = {n: move(x) for n, x in ch[k].items()}
    ch["planet_longitudes"].update(adj.lons)
    if adj.lagna is not None:
        ch["lagna_lon"] = adj.lagna
    ch["prasna_lagna"] = adj.prasna_lagna
    ch["muntha"], ch["muntha_signs"] = adj.muntha, adj.muntha_signs
    ch["lagna_sign"] = int(ch["lagna_lon"] // 30)
    ch["planet_signs"] = {n: int(x // 30) for n, x in ch["planet_longitudes"].items()}
    for n, x in ch["planet_longitudes"].items():
        ch["positions"][n] = {**ch["positions"][n], "lon": x, "sign_index": int(x // 30)}
    return ch


def _hms(hours, wrap=False):
    s = round(hours * 3600)
    if wrap:
        s %= 86400
    return "%d:%02d:%02d" % (s // 3600, s % 3600 // 60, s % 60)


def _hms12(hours, wrap=False):
    s = round(hours * 3600)
    if wrap:
        s %= 86400
    h24 = s // 3600
    m, sec = s % 3600 // 60, s % 60
    return "%d:%02d:%02d %s" % (h24 % 12 or 12, m, sec, "AM" if h24 < 12 else "PM")


def _ordinal(n):
    if 10 <= n % 100 <= 20:
        suf = "th"
    else:
        suf = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return "%d%s" % (n, suf)


def _dms(deg):
    s = round(abs(deg) * 3600)
    return s // 3600, s % 3600 // 60, s % 60


def core_info(birth, ch, cfg, s):
    """[label, value] lines of the Core Info text."""
    t, ab = _tables()
    p, d = E.panchanga(birth, ch, cfg), E.day_lords(birth, cfg, **S.day_kw(s))
    planet = ["", "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu"]
    left = lambda tab, k: "%s (%s) (%.2f%% left)" % (t[tab][p[k]], ab[p[k + "_lord"]], p[k + "_left"] * 100)
    span = E.day_night_span(birth, cfg)
    shifted = span["vedic_sunrise_hours"] < 0  # born before that day's sunrise: the previous day's is shown
    sun = E.sunrise_sunset(E._shifted_day(birth, -1 if shifted else 0), cfg)
    day_label = ""
    if shifted:
        import datetime as dt
        prev = dt.date(birth.year, birth.month, birth.day) - dt.timedelta(days=1)
        day_label = " (%s %d)" % (MONTHS[prev.month - 1], prev.day)
    lon_d, lon_m, lon_s = _dms(birth.longitude_east)
    lat_d, lat_m, lat_s = _dms(birth.latitude)
    ay_s = abs(ch["ayanamsa"]) * 3600
    tz = "%s (%s of GMT)" % (_hms(abs(birth.tz_east_hours)), "East" if birth.tz_east_hours >= 0 else "West")
    return [
        ["Date", "%s %s %d" % (_ordinal(birth.day), MONTHS[birth.month - 1], birth.year)],
        ["Time", _hms12(birth.hour_local)],     # the zone has its own row
        ["Time Zone", tz],
        ["Place", "%d %s %02d' %02d\", %d %s %02d' %02d\"" % (
            lon_d, "E" if birth.longitude_east >= 0 else "W", lon_m, lon_s,
            lat_d, "N" if birth.latitude >= 0 else "S", lat_m, lat_s)],
        ["Altitude", "%.2f meters" % birth.altitude_m],
        ["Lunar Yr-Mo", "%s - %s%s" % (t["samvatsaras"][p["samvatsara"]], ["", "Nija ", "Adhika "][p["adhika"]],
                                       t["lunar_months"][p["lunar_month"]])],
        ["Tithi", left("tithis", "tithi")],
        ["Vedic Weekday", "%s (%s)" % (t["weekdays"][d["weekday"]], ab[d["weekday"] + 1])],
        ["Nakshatra", left("nakshatras", "nakshatra")],
        ["Yoga", left("yogas", "yoga")],
        ["Karana", left("karanas", "karana")],
        ["Hora Lord", "%s (5 min sign: %s)" % (planet[d["hora_lord"]], SIGNS[d["hora_5min_sign"]])],
        ["Mahakala Hora", "%s (5 min sign: %s)" % (planet[d["mahakala_hora_lord"]], SIGNS[d["mahakala_hora_5min_sign"]])],
        ["Kaala Lord", "%s (Mahakala: %s)" % (planet[d["kaala_lord"]], planet[d["mahakala_kaala_lord"]])],
        ["Sunrise", _hms12(sun["sunrise_hours"], True) + day_label],
        ["Sunset", _hms12(sun["sunset_hours"], True) + day_label],
        ["Janma Ghatis", "%.4f" % d["janma_ghatis"]],
        ["Ayanamsa", "%d-%02d-%05.2f" % (ay_s // 3600, ay_s % 3600 // 60, ay_s % 60)],
        ["Sidereal Time", _hms(ch["local_sidereal_time_hours"], True)],
    ]


def small_av(ch, s):
    signs = [ch["lagna_sign"]] + [ch["planet_signs"][p] for p in PLANETS[:7]]
    r = ashtakavarga.ashtakavarga_tables(signs, **S.ashtakavarga_kw(s))
    return {"signs": signs, "bav": r["bav"], "sav": r["sav"]}


def sign_boxes(ch):
    """Chart placements for the Rasi (D-1) chart: sign index -> labels; lagna is 'As'."""
    boxes = {s: [] for s in range(12)}
    boxes[ch["lagna_sign"]].append("As")
    for i, (p, a) in enumerate(zip(PLANETS, PLANET_ABBR)):
        retro = ch["retrograde"].get(p)  # Mars..Saturn, and the nodes too, while they move backwards (the true ones not always)
        boxes[ch["planet_signs"][p]].append(a + ("R" if retro else ""))
    if ch.get("prasna_lagna") is not None:
        boxes[int(ch["prasna_lagna"] // 30)].append("PLag")
    return boxes


# Chakras > Many Vargas, in the order of its panels: title, division
MANY_VARGAS = [("Rasi", 1), ("Navamsa", 9), ("Trimsamsa", 30), ("Drekkana", 3), ("Dasamsa", 10), ("Shashtyamsa", 60),
               ("Saptamsa", 7), ("Dwadasamsa", 12), ("Vimsamsa", 20), ("Siddhamsa", 24), ("Shodasamsa", 16), ("Hora", 2)]


VARGA_NAMES = {**{n: t for t, n in MANY_VARGAS}, 4: "Chaturthamsa", 5: "Panchamsa", 6: "Shashthamsa", 8: "Ashtamsa", 11: "Rudramsa",
               27: "Nakshatramsa", 40: "Khavedamsa", 45: "Akshavedamsa", 81: "Navanavamsa", 108: "Ashtottaramsa", 144: "Dwadasa-Dwadasamsa"}


def many_vargas(ch, s, divisions=None):
    """The lagna and nine planets in each panel, in the default scheme of each division."""
    lons = [("As", ch["lagna_lon"])] + [(a, ch["planet_longitudes"][p]) for p, a in zip(PLANETS, PLANET_ABBR)]
    panels = []
    opt = S.varga_options(s)
    for n in divisions or [n for _, n in MANY_VARGAS]:
        title = VARGA_NAMES[n]
        boxes = {s: [] for s in range(12)}
        for label, lon in lons:
            boxes[V.varga_sign(lon, n, opt)].append(label)
        panels.append({"title": title if n == 1 else "%s D-%d" % (title, n), "lagna": V.varga_sign(ch["lagna_lon"], n, opt), "boxes": boxes})
    return panels


# Basics > Amsa rulers: the division -> its varga index
AMSA_DIVISIONS = {n: V.DIVISIONS.index(n) for n in (9, 2, 3, 4, 7, 10, 12, 16, 20, 24, 27, 30, 40, 45, 60)}
AMSA_DIVISIONS[150] = 25


def amsa_rulers(ch, division, s):
    """Which ruler's part each body falls in. A Varnada Lagna's D-150 part is computed here."""
    lons = _points(ch)
    rows = []
    opt = S.varga_options(s)
    for name in POINT_ORDER:
        part, idx, ruler = V.amsa_ruler(lons[name], AMSA_DIVISIONS[division], opt, s.d150_names)
        row = {"name": name, "division": part + 1, "index": idx + 1, "ruler": ruler}
        if division == 60:
            row.update(tone="bad" if idx + 1 in V.D60_MALEFIC else "good", meaning=V.D60_MEANINGS[idx])
        elif ruler in V.AMSA_NATURE.get(AMSA_DIVISIONS[division], {}):
            row["tone"], row["meaning"] = V.AMSA_NATURE[AMSA_DIVISIONS[division]][ruler]
        rows.append(row)
    return rows


def basics(birth, ch, cfg, s, name=""):
    pts = points_table(ch, s, 1, user_points(birth, ch, cfg, s))
    by = {r["name"]: r for r in pts}
    nav = {s: [] for s in range(12)}
    nav[by["Lagna"]["navamsa"]].append("As")
    for p, a in zip(PLANETS, PLANET_ABBR):
        nav[by[p]["navamsa"]].append(a)
    if ch.get("prasna_lagna") is not None:
        nav[by["Prasna Lagna"]["navamsa"]].append("PLag")
    return {"name": name, "points": pts, "core": core_info(birth, ch, cfg, s), "av": small_av(ch, s),
            "rasi": sign_boxes(ch), "navamsa": nav}
