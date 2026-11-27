"""Transits > Jamakkol: a Jamakkol Prasanam chart for the moment of the question (core_logic/jamakkol.py). The grahas inside are where
they are at that moment; Udayam, Aarudam, Kavippu, Rahu Kalam, Yamakandam, Mrithyu and Maandi go in their boxes; the eight Jama grahas
round the outside. Sunrise, sunset and the ayanamsa are the user's settings. The lagna is drawn too, and a bhava chart counts its houses from it, not from Udayam."""
import math

from core_logic import ephemeris as E, jamakkol as J

from .basics import PLANET_ABBR, PLANETS, _hms12, _tables

POINTS = {"Udayam": "UD", "Aarudam": "AR", "Kavippu": "KV", "Rahu Kalam": "RK", "Yamakandam": "YK", "Mrithyu": "MR", "Maandi": "Md"}
VEETHI = ["Mesha", "Rishabha", "Mithuna"]
WEEKDAYS = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]


def _clock_weekday(birth):
    """The weekday (0 Sunday) of the Jama grahas' day: the date's, the day before's until 6 am."""
    jd = E.julian_day_ut(birth.year, birth.month, birth.day, 12.0, birth.gregorian) - (1 if birth.hour_local < 6.0 else 0)
    return int(math.floor(jd + 1.5)) % 7


def chart(birth, cfg, ch, box=None):
    """``box``: longitude -> box; a bhava chart's from the lagna (service.jamakkol), else the sign. The Jama grahas keep their boxes."""
    box = box or (lambda x: int(x // 30))
    nak = _tables()[0]["nakshatra_abbr"]
    corr = ch.get("nakshatra_correction", 0.0)     # as Key Info: the sidereal nakshatras of a tropical chart

    def star(lon):
        x = (lon + corr) % 360.0
        return {"nakshatra": nak[int(x * 0.075)], "pada": int(x * 0.3) % 4 + 1}
    sun = ch["planet_longitudes"]["Sun"]
    span = E.day_night_span(birth, cfg)
    sunrise = E.sunrise_sunset(birth, cfg)
    points = {**J.points(sun, span["start_hours"], span["end_hours"], birth.hour_local), **J.kalam_points(sun, span["weekday"], span["is_night"])}
    boxes = {g: [] for g in range(12)}
    longitudes = {"As": ch["lagna_lon"], **{a: ch["planet_longitudes"][p] for p, a in zip(PLANETS, PLANET_ABBR)}, **{a: points[n] for n, a in POINTS.items()}}
    for a, lon in longitudes.items():
        retro = a in PLANET_ABBR and ch["retrograde"].get(PLANETS[PLANET_ABBR.index(a)])
        boxes[box(lon)].append(a + ("R" if retro else ""))
    degrees = {a: lon % 30 for a, lon in longitudes.items()}
    weekday = _clock_weekday(birth)
    k, _ = J.jamam(birth.hour_local)
    jama = [{"name": g, "abbr": PLANET_ABBR[PLANETS.index(g)], "box": box, "lon": lon, **star(lon)} for g, box, lon in J.jama_grahas(weekday, birth.hour_local)]
    return {
        "boxes": boxes, "degrees": degrees, "longitudes": longitudes, "lagna": box(ch["lagna_lon"]), "udayam": box(points["Udayam"]), "jama": jama,
        "points": [{"name": n, "abbr": a, "lon": points[n], **star(points[n])} for n, a in POINTS.items()],
        "grahas": [{"name": "Lagna", "abbr": "As", "lon": ch["lagna_lon"], "retrograde": False, **star(ch["lagna_lon"])}] + [{"name": p, "abbr": a, "lon": ch["planet_longitudes"][p], "retrograde": bool(ch["retrograde"].get(p)), **star(ch["planet_longitudes"][p])} for p, a in zip(PLANETS, PLANET_ABBR)],
        "facts": [["Weekday", WEEKDAYS[span["weekday"]]], ["Sunrise", _hms12(sunrise["sunrise_hours"], True)], ["Sunset", _hms12(sunrise["sunset_hours"], True)],
                  ["Jamam", "%d of the %s, %s's" % (k + 1, "night" if birth.hour_local % 24 >= 18 or birth.hour_local < 6 else "day", WEEKDAYS[weekday])],
                  ["Veethi", VEETHI[J.veethi(int(sun // 30))]]],
    }
