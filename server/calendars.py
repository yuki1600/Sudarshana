"""Lunar months and eras for the Muhurta tab: Amanta and Purnimanta names, Adhika months, Shaka and Vikram years."""
from __future__ import annotations

from core_logic import ephemeris as E, time_search as JS
from core_logic.natal_chart import RASI_NAMES_SA

LUNAR_MONTHS = ["Chaitra", "Vaishakha", "Jyeshtha", "Ashadha", "Shravana", "Bhadrapada",
                "Ashwina", "Kartika", "Margashirsha", "Pausha", "Magha", "Phalguna"]
SUN, MOON = 1, 2


def eras(g_year: int, g_month: int, m: int) -> dict:
    """Years of the lunar eras for a Gregorian date in Amanta month ``m`` (0 = Chaitra).
    Chaitradi Vikram and Shaka turn at Chaitra Shukla 1, the Gujarati Vikram at Kartika Shukla 1."""
    # Pausha..Phalguna (and a Margashirsha running into January) fall in the next Gregorian year of the era
    vikram = g_year + (56 if (m >= 9 and g_month <= 5) or (m == 8 and g_month <= 2) else 57)
    gujarati = g_year + (57 if m >= 7 and g_month >= 6 else 56)
    return {"vikram": vikram, "shaka": vikram - 135, "gujarati": gujarati}


def lunar_month(sunrise_jd: float, tithi: int, cfg: E.EphemerisConfig, g_year: int, g_month: int) -> dict:
    """The lunar month of the day that begins at ``sunrise_jd`` (``tithi``: 0..29 at that moment).
    A month holding no Sankranti (the Sun in one sign at both its new moons) is Adhika and takes the name of the next.
    A month holding two (the Sun two signs on) is named by the first and the second month is Kshaya, lost from the year:
    ``kshaya`` is its name, else ""."""
    sun = JS.body_longitude(SUN, cfg)
    start = JS.lunar_month(sunrise_jd, True, 2, cfg)
    end = JS.lunar_month(sunrise_jd, False, 2, cfg)
    s0, s1 = int(sun(start) // 30), int(sun(end) // 30)
    m = (s0 + 1) % 12
    adhika = s0 == s1
    kshaya = LUNAR_MONTHS[(s0 + 2) % 12] if (s1 - s0) % 12 == 2 else ""
    krishna = tithi >= 15
    # Purnimanta: the dark half takes the next Amanta month's name, the one its Sankranti s1 opens: an Adhika month
    # keeps its own, a Kshaya month skips the lost one
    p = (s1 + 1) % 12 if krishna else m
    # Sauramana: the solar month is the Sun's sidereal sign at sunrise
    sign = int(sun(sunrise_jd) // 30)
    return {"amanta": LUNAR_MONTHS[m], "purnimanta": LUNAR_MONTHS[p], "saura": RASI_NAMES_SA[sign], "adhika": adhika, "kshaya": kshaya,
            "paksha": "Krishna" if krishna else "Shukla", "start_jd": start, "end_jd": end,
            **eras(g_year, g_month, m)}
