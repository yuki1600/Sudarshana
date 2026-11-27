"""Jamakkol Prasanam (Tamil horary): its three points, Udayam, Aarudam and Kavippu, as longitudes.

Udayam goes once round the zodiac in the day (sunrise to sunset) and once in the night (sunset to next sunrise), starting from
the Sun; Aarudam goes round once an hour, 5 minutes a sign from Aries at the top of the hour; Kavippu counts from Udayam as far as
Aarudam is from the Sun's veethi, and moves backward through its sign as Aarudam moves forward."""


def udayam(sun_lon, start_hours, end_hours, hour_local):
    """The Sun's longitude plus the part of the day (or night) gone by, at 360° a day and 360° a night."""
    part = (hour_local - start_hours) / (end_hours - start_hours)
    return (sun_lon + 360.0 * part) % 360.0


def aarudam(hour_local):
    """Minute 0-4 of the clock hour Aries, 5-9 Taurus .. 55-59 Pisces; 30° over its 5 minutes."""
    secs = round(hour_local * 3600.0) % 3600
    return secs / 300.0 * 30.0


def veethi(sun_sign):
    """The Sun's veethi (sign 0 Aries): Mesha with the Sun in Taurus to Leo, Mithuna in Scorpio to Aquarius, Rishabha otherwise."""
    return 0 if 1 <= sun_sign <= 4 else 2 if 7 <= sun_sign <= 10 else 1


def kavippu(sun_lon, udayam_lon, aarudam_lon):
    """As many signs from Udayam as Aarudam's sign is from the veethi (both counted inclusively), at 30° less Aarudam's degrees in its sign."""
    count = (veethi(int(sun_lon // 30)) - int(aarudam_lon // 30)) % 12          # signs from Aarudam to the veethi, less one
    sign = (int(udayam_lon // 30) + count) % 12
    return (sign * 30.0 + (30.0 - aarudam_lon % 30.0) % 30.0) % 360.0


def points(sun_lon, start_hours, end_hours, hour_local):
    """{"Udayam", "Aarudam", "Kavippu"}: longitudes, for a moment ``hour_local`` in the day or night from ``start_hours`` to ``end_hours``."""
    ud, ar = udayam(sun_lon, start_hours, end_hours, hour_local), aarudam(hour_local)
    return {"Udayam": ud, "Aarudam": ar, "Kavippu": kavippu(sun_lon, ud, ar)}


# The eight Jama grahas, in their fixed order, and the eight boxes they sit in, from Pisces backward round the chart: the four corners
# and the box after each (Pisces, Capricorn, Sagittarius, Libra, Virgo, Cancer, Gemini, Aries). The weekday's lord is in Pisces at 6 am
# and 6 pm; at each 90-minute jamam the order moves one box on, and every Jama graha goes back 45° through the jamam.
JAMA_ORDER = ("Sun", "Mars", "Jupiter", "Mercury", "Venus", "Saturn", "Moon", "Rahu")
JAMA_BOXES = (11, 9, 8, 6, 5, 3, 2, 0)
WEEKDAY_LORDS = ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn")     # 0 Sunday


def jamam(hour_local):
    """(jamam 0-7, the part of it gone by): 90 minutes each from 6 am, the night's from 6 pm the same way."""
    m = (hour_local * 60.0 - 360.0) % 720.0
    return int(m // 90.0), (m % 90.0) / 90.0


def jama_grahas(weekday, hour_local):
    """[(graha, box, longitude)] in box order. ``weekday``: 0 Sunday, of the clock's day, which for this begins at 6 am."""
    k, part = jamam(hour_local)
    lord = JAMA_ORDER.index(WEEKDAY_LORDS[weekday])
    base = 360.0 - 45.0 * part
    return [(JAMA_ORDER[(lord + i - k) % 8], box, (base - 45.0 * i) % 360.0) for i, box in enumerate(JAMA_BOXES)]


# Rahu Kalam and Yamakandam: which eighth of the day each weekday's is (Sunday first), put in that eighth's Jama box at the Sun's degrees in its sign
RAHU_KALAM = (8, 2, 7, 5, 6, 4, 3)
YAMAKANDAM = (5, 4, 3, 2, 1, 7, 6)
# Mrithyu and Maandi: so far from the Sun, by weekday, by day and by night
MRITHYU = ((60, 312), (36, 288), (12, 264), (156, 240), (132, 216), (108, 192), (84, 336))
MAANDI = ((156, 240), (132, 216), (108, 192), (84, 336), (60, 312), (36, 288), (12, 264))


def kalam_points(sun_lon, weekday, night):
    """{"Rahu Kalam", "Yamakandam", "Mrithyu", "Maandi"}: longitudes. ``weekday``: 0 Sunday, the Vedic one (from sunrise)."""
    deg = sun_lon % 30.0
    return {"Rahu Kalam": JAMA_BOXES[RAHU_KALAM[weekday] - 1] * 30.0 + deg, "Yamakandam": JAMA_BOXES[YAMAKANDAM[weekday] - 1] * 30.0 + deg,
            "Mrithyu": (sun_lon + MRITHYU[weekday][night]) % 360.0, "Maandi": (sun_lon + MAANDI[weekday][night]) % 360.0}
