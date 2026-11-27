"""The Basics > Houses and KP tabs, at their defaults: equal houses with the cusp at the lagna's degree (HouseTypeWanted=1,
HouseCuspsInMiddle=1), the nine grahas and the outer planets."""
from core_logic import ephemeris as E, house_systems as H, time_search as JS, kp_astrology as K

ABBR = {"Sun": "Su", "Moon": "Mo", "Mars": "Ma", "Mercury": "Me", "Jupiter": "Ju", "Venus": "Ve", "Saturn": "Sa",
        "Rahu": "Ra", "Ketu": "Ke", "Uranus": "Ur", "Neptune": "Ne", "Pluto": "Pl"}
KP_KEYS = ("star_lord", "sub_lord", "prati_sub_lord", "sookshma_sub_lord", "praana_sub_lord", "deha_sub_lord")
ORDINAL = ["1st", "2nd", "3rd"] + ["%dth" % i for i in range(4, 13)]


def _bodies(birth, ch, cfg):
    out = {"As": ch["lagna_lon"]}
    out.update({ABBR[n]: x for n, x in {**ch["planet_longitudes"], **ch.get("outer", {})}.items() if n in ABBR})    # an adjusted chart's own positions
    return out


REFS = ["Lagna", "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
SYSTEMS = {3: "PORPHYRY", 4: "PLACIDUS", 5: "KOCH", 6: "REGIOMONTANUS", 7: "CAMPANUS", 8: "AXIAL_ROTATION", 9: "POLICH_PAGE", 10: "ALCABITUS"}


def _bhavas(birth, ch, cfg, s, ref=0):
    """(start, middle, end) of the houses in the chosen system (swe_houses from 3 on), from the lagna or, with ``ref``, Sun .. Ketu."""
    point = ch["lagna_lon"] if not ref else ch["planet_longitudes"][REFS[ref]]
    t = house_type(s, ref)
    if t < 3:
        if s.bhava_nodes_reversed and ref in (8, 9):     # counted backward: the houses of the mirrored point, mirrored back (start above end)
            return [tuple(-x % 360.0 for x in b) for b in H.bhava_spans(-point % 360.0, t, [(30.0 * i - point) % 360.0 for i in range(12)], s.house_cusp_in_middle)]
        return H.bhava_spans(point, t, [point + 30.0 * i for i in range(12)], s.house_cusp_in_middle)
    # the houses of the moment the lagna reaches the reference's longitude
    hc = JS.cusps_by_reference(birth, point, SYSTEMS[t], cfg) if ref else E.house_cusps(birth.jd_ut, birth.latitude, birth.longitude_east, SYSTEMS[t], cfg)
    return H.bhava_spans(hc["ascendant"], t, hc["cusps"], s.house_cusp_in_middle)


def mars_bhavas(birth, ch, cfg, s):
    """Mars's bhava (1-12) from the lagna, the Moon and Venus, each in its own bhava chakra (the cusps of the chosen systems), for Kuja dosha."""
    mars = ch["planet_longitudes"]["Mars"]
    return {n: H.house_of(mars, _bhavas(birth, ch, cfg, s, REFS.index(n))) + 1 for n in ("Lagna", "Moon", "Venus")}


def house_type(s, ref):
    """The house system from ``ref``: the lagna's is the House system option; a graha's has its own, equal houses unless changed."""
    return s.house_type_graha if ref else s.house_type


def houses(birth, ch, cfg, s, ref=0):
    bh = _bhavas(birth, ch, cfg, s, ref)
    bodies = _bodies(birth, ch, cfg)
    rows = [{"house": ORDINAL[i], "start": s, "cusp": c, "end": e, "occupants": []} for i, (s, c, e) in enumerate(bh)]
    for label, lon in bodies.items():
        rows[H.house_of(lon, bh)]["occupants"].append(label)
    return rows


def kp(birth, ch, cfg, s, ref=0):
    bodies = _bodies(birth, ch, cfg)
    bh = _bhavas(birth, ch, cfg, s, ref)
    # the house's cusp: its middle, or its start when the ascendant starts the first house
    bodies.update({"%s bhava" % ORDINAL[i]: b[1 if s.house_cusp_in_middle else 0] for i, b in enumerate(bh)})
    rows = []
    for label, lon in bodies.items():
        lv = K.get_kp_sub_levels(lon, 5)
        rows.append({"label": label, "lon": lon, "lords": [ABBR[lv[k]] for k in KP_KEYS]})
    return rows
