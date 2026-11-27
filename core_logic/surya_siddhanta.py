"""The Sri Surya Siddhanta planetary model (Settings > Graha model, Siddhanta = 1) and its ayanamsa, in the
"generalized Makaranda" form: the Surya Siddhanta's mean motions with the bija corrections of the Makaranda tables.
Verses are cited from Burgess's translation (docs/SOURCES.md section 1.2):

* ``precession``        libration of the equinoxes, 27 deg amplitude, 600 librations a yuga = 7200 years (SS 3.9-10)
* ``mean_and_true``     mean planet from the ahargana (days since the Kali epoch, local mean time; SS 1.45-53), its
                        apsis (SS 1.41-44) and anomaly, then the true planet by ``_sun_manda``, ``_moon_manda`` or
                        the four-step ``_star_planet`` (SS 2.39-45)
* ``_equation_of_time``, ``true_days``: local mean -> true solar time
* ``sunrise_hours``     sunrise in local true hours (ascensional difference, SS 2.60-63)
* ``_ascension`` / ``_rising_minutes``: right ascension and oblique ascension at Lanka / the place (SS 3.42-45),
                        ``_horizon_point`` (lagna, SS 3.46-49; meridian), ``_day_arc`` (sunset and the day length)
* ``chart``, ``ayanamsa`` planets, lagna, house cusps and the SSS ayanamsa in this model

Days count from the Kali epoch (JD 588465.5, midnight at Ujjain; Burgess's note to SS 1.34) in local time;
``desantara`` is the longitude east of Ujjain (75.7684565 deg, SS 1.62) in degrees.  The Sun's mean longitude is
computed first in a chart and read by the other planets (their anomaly is reckoned from it), which
``mean_and_true`` does too.
"""
import math
from fractions import Fraction

from .utils import norm360

KALI_OFFSET = 2415022.0 - 1826556.5        # JD - days since the Kali epoch (JD 588465.5)
UJJAIN = 75.7684565                        # the prime meridian of SS 1.62, degrees east
_D2R = 0.017453292519943295
_R2D = 57.29577951308232
_RADIUS = 3437.746770784939               # radius in arc minutes (SS 2.15-22: 3438')
_EPS = 1e-11                              # replaces an anomaly of exactly 0

# revolutions in a mahayuga, Sun .. Saturn, Moon's node (SS 1.29-34; index = body 1..8); apsides in a kalpa (SS 1.41-44)
_REVOLUTIONS = [0.0, 4320000.0, 57753336.0, 2296832.0, 17937060.0, 364220.0, 7022376.0, 146568.0, -232238.0]
# bija corrections (x 1e-10 deg per year since creation), same index
_BIJA = [0.0, 0.0, 0.0, 7.1151017357437, 31.215202568113, -15.6076012840565, -23.4114019260847, 23.4114019260847,
         -7.80380064202824]
_APOGEE_REVOLUTIONS = [0.0, 387.0, 488203000.0, 204.0, 368.0, 900.0, 535.0, 39.0, 0.0]
# Mars, Mercury, Jupiter, Venus, Saturn (body 3..7): sighra / manda epicycles at the end of the odd and even
# quadrants (degrees), the manda "sin" factor and the sighra anomaly range in which the planet is retrograde
_EPI_EVEN = {3: (235.0, 75.0, 75.0, 235.0), 4: (133.0, 30.0, 30.0, 133.0), 5: (70.0, 33.0, 33.0, 70.0),
             6: (262.0, 12.0, 12.0, 262.0), 7: (39.0, 49.0, 49.0, 39.0)}
_EPI_ODD = {3: (232.0, 72.0, 72.0, 232.0), 4: (132.0, 28.0, 28.0, 132.0), 5: (72.0, 32.0, 32.0, 72.0),
            6: (260.0, 11.0, 11.0, 260.0), 7: (40.0, 48.0, 48.0, 40.0)}
_SIN_FACTOR = {3: 5.769713121, 4: 2.229731213, 5: 2.547318183, 6: 0.8753862433, 7: 3.822553729}
_RETRO = {3: (169.392457108346, 190.607542891654), 4: (145.003089170517, 214.996910829483),
          5: (123.999650368356, 236.000349631644), 6: (167.0, 193.0), 7: (114.8, 245.2)}


def precession(days: float) -> float:
    """The SSS ayanamsa (SS 3.9-10; with the sign the model uses) at ``days`` since the Kali epoch."""
    x = days * 0.002737785151635915 * (1.0 / 7200.0)
    v = (x - math.trunc(x)) * 108.0
    if v > 0:
        if v <= 27.0:
            return -v
        if v <= 81.0:
            return v - 54.0
        return 108.0 - v if v <= 108.0 else v
    if v < 0:
        if v >= -27.0:
            return -v
        if v >= -81.0:
            return v + 54.0
        return -(v + 108.0) if v >= -108.0 else v
    return v


def _equation_of_time(mean_sun: float, anomaly: float, ayanamsa: float) -> float:
    """Equation of time in days of the tropical mean Sun: Smart's series (Meeus, Astronomical Algorithms eq. 28.3)
    with y = tan^2 12 deg (the SS obliquity of 24 deg, SS 2.28) and e = 0.018984."""
    s = norm360(mean_sun + ayanamsa) * _D2R
    m = norm360(anomaly) * _D2R
    y = math.tan(0.20943951023931953) ** 2
    e = (y * math.sin(2 * s) - 0.5 * y * y * math.sin(4 * s) - 0.037968001610174 * math.sin(m)
         - 4.504903582094299e-4 * math.sin(2 * m) + 0.075936003220348 * math.sin(m) * y * math.cos(2 * s))
    return e * _R2D * (1.0 / 360.0)


def _sighra_like(x_deg: float, factor: float, even: float, odd: float, s: float) -> float:
    """atan(r sin u / (R + r cos u)) in degrees, u = x + factor * sin x, r = (even - (even - odd) sin x) / 360 R."""
    u = (s * factor + x_deg) * _D2R
    r = (even - (even - odd) * s) * (1.0 / 360.0) * _RADIUS
    return math.atan2(math.sin(u) * r / (math.cos(u) * r + _RADIUS), 1.0) * _R2D


def _sun_manda(mean: float, anomaly: float, sign: int) -> float:
    """The Sun's equation of centre (manda correction, SS 2.39; epicycle 14 deg .. 13 deg 40', SS 2.34)."""
    a = anomaly * _D2R
    k = 6383.39600310841 / (1.0 - math.cos(a) * 0.8860136684023698) * 1.5665642543765852e-4
    c = k * (13.962634015954622 - anomaly * 0.003325821600036921) + (anomaly * 0.02276247586910956
                                                                     + 4904.05431317952)
    r = c * math.sin(a) * 7.71604938271605e-6
    return norm360(math.atan2(r / math.sqrt(1.0 - r * r), 1.0) * _R2D * sign + mean)


def _moon_manda(mean: float, anomaly: float, sign: int) -> float:
    """The Moon's equation of centre (epicycle 32 deg .. 31 deg 40', SS 2.34)."""
    x = anomaly if anomaly != 0.0 else _EPS
    s = math.sin(x * _D2R)
    u = (x + s * 5.046428631) * _D2R
    r = (32.0 - s * 0.33333333333333215) * (1.0 / 360.0) * _RADIUS
    return norm360(math.atan2(math.sin(u) * r / (math.cos(u) * r + _RADIUS), 1.0) * _R2D * sign + mean)


def _fold(d: float, sign: int):
    """The anomaly folded after a correction: (folded anomaly, sign)."""
    if d <= 180.0:
        return d, 1
    if d < 360.0:
        sign = -1
    return 360.0 - d, sign


def _star_planet(body: int, base: float, sighrocca: float, mandocca: float, anomaly: float, sign: int):
    """Half sighra, half manda, full manda, full sighra (SS 2.43-45); (true longitude, retrograde)."""
    even, odd, f = _EPI_EVEN[body], _EPI_ODD[body], _SIN_FACTOR[body]
    x = anomaly if anomaly != 0.0 else _EPS
    s = math.sin(x * _D2R)
    v1 = norm360(_sighra_like(x, 0.0, even[0], odd[0], s) * 0.5 * sign + base)
    d = mandocca - v1
    if d < 0:
        d += 360.0
    d, sign = _fold(d, sign)
    x = d if d != 0.0 else _EPS
    s = math.sin(x * _D2R)
    d = mandocca - (_sighra_like(x, f, even[1], odd[1], s) * sign * 0.5 + v1)
    if d >= 360.0:
        d -= 360.0
    if d < 0:
        d += 360.0
    d, sign = _fold(d, sign)
    x = d if d != 0.0 else _EPS
    s = math.sin(x * _D2R)
    v3 = _sighra_like(x, f, even[2], odd[2], s) * sign + base
    if v3 >= 360.0:
        v3 -= 360.0
    if v3 < 0:
        v3 += 360.0
    d = sighrocca - v3
    if d < 0:
        d += 360.0
    d, sign = _fold(d, sign)
    lo, hi = _RETRO[body]
    retro = lo <= d < hi
    x = d if d != 0.0 else _EPS
    s = math.sin(x * _D2R)
    return norm360(_sighra_like(x, 0.0, even[3], odd[3], s) * sign + v3), retro


def _mean_sun(days: float, desantara: float) -> float:
    return _mean(days, desantara, 1)[0]


def _mean(days: float, desantara: float, body: int):
    """(mean longitude, years since creation, desantara / 360): the mean planet with its bija and the correction
    for longitude (SS 1.53, 1.60-61)."""
    y = days * 0.002737785151635919
    n = math.trunc(y - 3179.0)
    rev = _REVOLUTIONS[body]
    revs = days / (1577917828.0 / rev) if rev else 0.0
    years = (y - (n + 3179.0)) + n + 1955883179.0
    dd = desantara * (1.0 / 360.0)
    m = norm360((revs - math.trunc(revs)) * 360.0 + _BIJA[body] * years * 1e-10) - rev * 2.3148148148148148e-7 * dd
    return m, y, years, dd


def mean_and_true(days: float, desantara: float, body: int):
    """Mean and true planet for body 1..8 (Sun .. Saturn, 8 = the node, Rahu = node + 180 deg):
    dict(true, retrograde, mean, apogee, anomaly)."""
    mean, y, years, dd = _mean(days, desantara, body)
    sun = mean if body == 1 else _mean_sun(days, desantara)
    # ~2e8 revolutions for the Moon's apsis since creation: exact arithmetic keeps the fraction, a double would not
    a = Fraction(_APOGEE_REVOLUTIONS[body]) * ((Fraction(y) + 1955880000) * Fraction(2.3148148148148147e-10))
    apogee = norm360(float((a - math.trunc(a)) * 360))
    if body == 2:
        apogee = apogee - years * 7.80380064202824e-10 - dd * 0.1130099537037037
    if body in (1, 2, 8):
        k = apogee - mean
    elif body in (3, 5, 7):
        k = sun - mean
    else:
        k = mean - sun
    k = norm360(k)
    folded, sign = k, 0
    if body in (1, 2, 8):
        if k <= 180.0:
            sign = 1
            if k > 90.0:
                folded = 180.0 - k
        elif k <= 270.0:
            sign, folded = -1, k - 180.0
        else:
            sign, folded = -1, 360.0 - k
    elif k <= 180.0 or k > 360.0:
        sign = 1
    else:
        sign, folded = -1, 360.0 - k
    retro = False
    if body == 1:
        true = _sun_manda(mean, folded, sign)
    elif body == 2:
        true = _moon_manda(mean, folded, sign)
    elif body in (3, 5, 7):
        true, retro = _star_planet(body, mean, sun, apogee, folded, sign)
    elif body in (4, 6):
        true, retro = _star_planet(body, sun, mean, apogee, folded, sign)
    else:
        true = mean
    return {"true": true, "retrograde": retro, "mean": mean, "apogee": apogee, "anomaly": k}


def true_days(days: float, desantara: float, ayanamsa: float) -> float:
    """Local mean time -> local true time (days since the Kali epoch), two equation-of-time passes."""
    sun = mean_and_true(days, desantara, 1)
    e = _equation_of_time(sun["mean"], sun["anomaly"], ayanamsa)
    sun = mean_and_true(e + days, desantara, 1)
    return _equation_of_time(sun["mean"], sun["anomaly"], ayanamsa) + days


def sunrise_hours(days: float, desantara: float, latitude: float) -> float:
    """Sunrise of the day ``trunc(days)`` in local true hours (SS 2.60-63), iterated to 0.004 s."""
    s24 = math.sin(0.41887902047863906)
    tan_lat = math.tan(latitude * _D2R)
    out = 6.0
    while True:
        days = math.trunc(days) + out * (1.0 / 24.0)
        lon = mean_and_true(days, desantara, 1)["true"] + precession(days)
        if lon > 360.0:
            lon -= 360.0
        if lon <= 90.0:
            b = lon
        elif lon <= 180.0:
            b = 180.0 - lon
        elif lon <= 270.0:
            b = lon - 180.0
        else:
            b = 360.0 - lon if lon <= 360.0 else lon
        sign = 1 if lon <= 180.0 else -1
        sd = math.sin(b * _D2R) * s24
        dec = math.atan2(sd / math.sqrt(1.0 - sd * sd), 1.0) * _R2D * _D2R
        x = math.tan(dec) * tan_lat
        c = math.atan2(x / math.sqrt(1.0 - x * x), 1.0) * 572.9577951308232 if x < 1.0 else 900.0
        old, out = out, (60.0 - (c * (1.0 / 60.0) * sign + 45.0)) * 0.4
        if abs(out - old) <= 1.1574074074074074e-06:   # 0.1 s
            return out


def _asin(x: float) -> float:
    return math.atan2(x / math.sqrt(1.0 - x * x), 1.0)


def _ascension(latitude: float, lon: float, sign: float, equatorial: bool) -> float:
    """Right ascension of ``lon`` (< 90 deg) in time minutes (SS 3.42-45), plus ``sign`` x the ascensional
    difference unless ``equatorial`` (declination 24 deg obliquity; cos(decl) taken as cos(24 sin lon))."""
    r = 57.29577951308232
    s = math.sin(lon / r)
    sd = math.sin(24.0 / r) * s
    dec = math.atan2(sd / math.sqrt(1.0 - sd * sd), 1.0)
    x = math.tan(dec * r / r) * math.tan(latitude / r)
    asc_diff = _asin(x)
    c = math.cos(24.0 / r) * s / math.cos(s * 24.0 / r)
    if c == 1.0:
        ra = 360.0
    elif c == -1.0:
        ra = -360.0
    else:
        ra = _asin(c) * r * 4.0
    return ra if equatorial else ra + asc_diff * r * 4.0 * sign


_QUADRANT = [(-1.0, True, 0), (1.0, False, 1), (1.0, True, 1), (-1.0, False, 2), (-1.0, True, 2)]


def _rising_minutes(latitude: float, lon: float, ayanamsa: float, equatorial: bool) -> float:
    """Time (minutes, 0..1440) for the ecliptic from 0 deg to ``lon`` + ayanamsa to rise (or to
    culminate when ``equatorial``)."""
    x = norm360(lon + ayanamsa)
    half = _ascension(latitude, 90.0, -1.0, equatorial) + _ascension(latitude, 90.0, 1.0, equatorial)
    i = math.trunc(x * 0.011111111111111112)
    y = {1: 180.0 - x, 2: x - 180.0, 3: 360.0 - x, 4: x - 360.0}.get(i, x)
    sign, add, k = _QUADRANT[i]
    t = _ascension(latitude, y, sign, equatorial)
    t = k * half + t if add else k * half - t
    return norm360(t * 0.25) * 4.0


def _angdist(a: float, b: float) -> float:
    """|a - b| folded to [0, 180]."""
    d = abs(a - b)
    while d >= 360.0:
        d -= 360.0
    return d if d <= 180.0 else 360.0 - d


def _horizon_point(latitude: float, sun_now: float, sun_rise: float, ayanamsa: float, minutes: float,
                   equatorial: bool) -> float:
    """The lagna (SS 3.46-49) / the meridian: the point that rose / culminated ``minutes`` after the Sun at
    sunrise, moved by the Sun's motion since sunrise."""
    target = _rising_minutes(latitude, sun_rise, ayanamsa, equatorial) + minutes
    guess = norm360(minutes * 0.25 + sun_rise)
    r = _rising_minutes(latitude, guess, ayanamsa, equatorial)
    while _angdist(r * 0.25, target * 0.25) > 2.0833333333333335e-4:
        guess = norm360((target - r) * 0.25 + guess)
        r = _rising_minutes(latitude, guess, ayanamsa, equatorial)
    return norm360(guess) + sun_now - sun_rise


def _true_sun_at(days: float, desantara: float):
    """The Sun's mean longitude / anomaly at ``days`` and the precession (one step of ``_day_arc``)."""
    prec = precession(days)
    sun = mean_and_true(days, desantara, 1)
    e = _equation_of_time(sun["mean"], sun["anomaly"], prec)
    sun = mean_and_true(e + days, desantara, 1)
    days = _equation_of_time(sun["mean"], sun["anomaly"], prec) + days
    return mean_and_true(days, desantara, 1)["true"], prec


def _day_arc(latitude: float, days: float, desantara: float, arc: float):
    """From sunrise of the day of ``days``, the minutes for the ecliptic arc ``arc`` (180: the day) to
    rise; returns (Sun at the end, Sun + arc, minutes)."""
    s0 = sunrise_hours(days, desantara, latitude)
    s1 = sunrise_hours(days + 1.0, desantara, latitude)
    rate = 34560.0 / (s1 + 24.0 - s0)
    rise = math.trunc(days) + s0 * (1.0 / 24.0)
    prec = precession(rise)
    sun = mean_and_true(rise, desantara, 1)
    rise -= _equation_of_time(sun["mean"], sun["anomaly"], prec)
    want = arc * 4.0
    while True:
        sun, prec = _true_sun_at(want / rate + rise, desantara)
        r1 = _rising_minutes(latitude, norm360(sun), prec, False)
        span = _rising_minutes(latitude, norm360(sun + arc), prec, False) - r1
        if span < 0:
            span += rate
        if _angdist(span * 0.25, want * 0.25) <= 2.0833333333333335e-4:
            return sun, norm360(sun + arc), span
        want = (span - want) * 0.5 + want


def ayanamsa(jd_ut: float, longitude_east: float = UJJAIN, delta: float = 0.0) -> float:
    """The SSS ayanamsa: the precession (SS 3.9-10) at the place's local true time, + ``delta``."""
    days = jd_ut - KALI_OFFSET + longitude_east * (1.0 / 360.0)
    desantara = longitude_east - UJJAIN
    return precession(true_days(days, desantara, precession(days) + delta)) + delta


def _sunrise_jd(local_jd: float, hours: float) -> float:
    """The local date of ``local_jd`` at ``hours`` (swe_revjul + swe_julday)."""
    return math.floor(local_jd + 0.5) - 0.5 + hours / 24.0


def chart(jd_ut: float, longitude_east: float, latitude: float, ayanamsa_value=None, delta: float = 0.0,
          ayanamsa_first=None):
    """The bodies and houses in the SSS model.

    ``ayanamsa_value``: the chosen ayanamsa (``ephemeris.ayanamsa_value``) or None for the SSS ayanamsa
    (precession + ``delta``).  Returns dict(lagna, mc, cusps (12, Porphyry split of the SSS lagna and meridian),
    positions {Sun .. Ketu: (longitude, retrograde)}, ayanamsa, sidereal_time = 6.5 h, the value shown in SSS
    mode)."""
    desantara = longitude_east - UJJAIN
    days = jd_ut - KALI_OFFSET + longitude_east * (1.0 / 360.0)
    ayan = precession(days) + delta if ayanamsa_value is None else ayanamsa_value
    t = true_days(days, desantara, ayan if ayanamsa_first is None else ayanamsa_first)
    prec = precession(t)
    if ayanamsa_value is None:
        ayan = prec + delta
    shift = prec - ayan
    local_jd = jd_ut + longitude_east * (1.0 / 360.0) + (t - days)
    n = math.trunc(t)
    rise = sunrise_hours(n + 0.5, desantara, latitude)
    rise_jd = _sunrise_jd(local_jd, rise)
    if local_jd < rise_jd:
        rise_next, rise = rise, sunrise_hours(n - 0.5, desantara, latitude)
        rise_jd = _sunrise_jd(local_jd - 1.0, rise)
    else:
        rise_next = sunrise_hours(n + 1.5, desantara, latitude)
    minutes = (local_jd - rise_jd) * 34560.0 / (rise_next + 24.0 - rise)
    sun_rise = mean_and_true(rise_jd - local_jd + t, desantara, 1)["true"]
    sun_now = mean_and_true(t, desantara, 1)["true"]
    asc = _horizon_point(latitude, sun_now, sun_rise, prec, minutes, False)
    day = _day_arc(latitude, t, desantara, 180.0)[2]
    if minutes < day * 0.5:   # before local noon: the meridian is timed from the previous sunrise
        rise_next, rise = rise, sunrise_hours(n - 0.5, desantara, latitude)
        minutes = (local_jd - _sunrise_jd(local_jd - 1.0, rise)) * 34560.0 / (rise_next + 24.0 - rise)
        day = _day_arc(latitude, t - 1.0, desantara, 180.0)[2]
    mc = _horizon_point(latitude, sun_now, sun_rise, prec, minutes - day * 0.5, True)
    asc, mc = asc + shift, mc + shift
    h4 = norm360(mc + 180.0)
    q = norm360(h4 - asc)
    h2 = norm360(q / 3.0 + asc)
    h3 = norm360(q / 3.0 + h2)
    h5 = norm360((30.0 - q / 6.0) * 2.0 + h4)
    h6 = norm360((30.0 - q / 6.0) * 2.0 + h5)
    first = [norm360(asc), h2, h3, h4, h5, h6]
    cusps = first + [norm360(c + 180.0) for c in first[:3]] + [norm360(mc)] + [norm360(c + 180.0) for c in first[4:]]
    positions = {}
    for name, body in (("Sun", 1), ("Moon", 2), ("Mars", 3), ("Mercury", 4), ("Jupiter", 5), ("Venus", 6),
                       ("Saturn", 7), ("Rahu", 8), ("Ketu", 9)):
        p = mean_and_true(t, desantara, min(body, 8))
        lon = p["true"] + (180.0 if body == 8 else 0.0) + shift
        positions[name] = (norm360(lon), p["retrograde"])
    return {"lagna": norm360(asc), "mc": norm360(mc), "cusps": cusps, "positions": positions, "ayanamsa": ayan,
            "sidereal_time": 6.5}
