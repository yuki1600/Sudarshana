"""Modes: a mode finds a derived chart and returns its birth data; the client makes it the current chart, so every
view recalculates for it (one chart, many views). ``event`` says how the dasas of that chart are
fitted into its span."""
import dataclasses
import functools
from datetime import datetime, timedelta

from core_logic import ephemeris as E, dasa_systems as J, time_search as S, varga_charts as V, miscellany as MS, sahams_library as SL, tajika as T
from core_logic import tithi_pravesha as TP, workflows as W

from . import calendars as CAL, dasas as D, settings as ST

STEP = 0.0035          # days: a search from a derived chart starts this many days away from it, so it moves on
ABBR = ["As", "Su", "Mo", "Ma", "Me", "Ju", "Ve", "Sa", "Ra", "Ke"]    # time_search's point numbers
TAJAKA, PRAVESHA, OTHER = 1, 2, 5    # chart kinds of dasa_systems.event_year_definition


def _at(birth: E.BirthData, when: datetime) -> E.BirthData:
    return dataclasses.replace(
        birth, year=when.year, month=when.month, day=when.day,
        hour_local=when.hour + when.minute / 60 + (when.second + when.microsecond / 1e6) / 3600)


def _local(birth: E.BirthData, jd: float) -> E.BirthData:
    y, m, d, h = E.jd_to_calendar(jd + birth.tz_east_hours / 24.0, birth.gregorian)
    return dataclasses.replace(birth, year=y, month=m, day=d, hour_local=h)


def _when(b: E.BirthData) -> datetime:
    return datetime(b.year, b.month, b.day) + timedelta(hours=b.hour_local)


def _chart(birth: E.BirthData, start: float, end: float, title: str, kind: int = OTHER) -> dict:
    """The chart at UT ``start`` in the zone of ``birth``, in effect until ``end``."""
    eb = _local(birth, start)
    return {"title": title, "birth": dataclasses.asdict(eb), "start": _when(eb), "end": _when(_local(birth, end)),
            "event": {"kind": kind, "name": title, "span_days": end - start}}


def _sunrise(birth, when, cfg):
    """The sunrise that begins the Vedic day of a moment."""
    b = _at(birth, when)
    hours = E.day_night_span(b, cfg)["vedic_sunrise_hours"]
    return datetime(b.year, b.month, b.day) + timedelta(hours=hours)


_SUNRISE_TITLE = {"Tajaka": "Taj ann sunrise", "Tajaka monthly": "Taj mon sunrise", "Tajaka 2.5 day": "Taj 2.5d sunrise", "Tajaka 5 hr": "Taj 5hr sunrise", "Tajaka 25 min": "Taj 25min sunrise", "Tajaka 2 min": "Taj 2min sunrise"}


def tajaka(birth, cfg, ch, s, year, month=0, d25=0, h5=0, m25=0, m2=0, sunrise=False):
    """The Tajaka chart of ``year``; ``month`` (calendar month, 0 = none) and the finer
    periods (1-12, 0 = none, each needs the one above) narrow it. Also its Muntha, method 1 (the default). ``sunrise``:
    "Find Tajaka Sunrise Chart": from the sunrise of that day to the sunrise of the end's day."""
    if not birth.year <= year <= 9000:
        raise ValueError("year must be %d to 9000" % birth.year)
    name, start, end, counts = T.tajaka_period(year - birth.year, month - birth.month if month else 0, d25, h5, m25, m2)
    to_date = ST.year_mapper(birth, cfg, s, T.tajaka_year_definition(s.tajaka_tropical, s.tajaka_true_year))
    natal = ST.jchart(ch, None, s)
    lon, signs = T.muntha_position(natal.lons[0], [v[0] for v in natal.signs], counts, method=s.muntha_method)
    begin, finish = to_date(start), to_date(end)
    title = "Tajaka" if name == "annual" else "Tajaka " + name   # the year chart is just "Tajaka"
    if sunrise:
        begin, finish, title = _sunrise(birth, begin, cfg), _sunrise(birth, finish, cfg), _SUNRISE_TITLE.get(title, title)
    # the birth carries the Muntha, so the chart panels and the points table show it
    return {"title": title, "birth": {**dataclasses.asdict(_at(birth, begin)), "adjust": {"muntha": lon, "muntha_signs": signs}}, "start": begin, "end": finish,
            "muntha": {"lon": lon, "sign": int(lon // 30)},
            "event": {"kind": TAJAKA, "name": title, "span_days": (finish - begin).total_seconds() / 86400.0,
                      "counts": list(counts)}}


def tithi_pravesha(birth, cfg, s, year, month=0, day=0):
    """Route (1) of the form: the annual chart of ``year``; with ``month`` (1st .. 13th) the ``month``-th recurrence of the tithi after it;
    with ``day`` (1 .. 30) the ``day``-th tithi counted from that."""
    if not birth.year <= year <= 9000:
        raise ValueError("year must be %d to 9000" % birth.year)
    start, end = TP.annual_tithi_pravesha(birth, year - birth.year, cfg, s.tp_solar_month)
    if not month:
        return _chart(birth, start, end, "Annual TP", PRAVESHA)
    target, event = _tithi_return(birth, cfg)
    jd = start
    for _ in range(month - 1):
        jd = event(jd + STEP, target)
    if not day:
        return _chart(birth, jd, event(jd + STEP, target), "Monthly TP", PRAVESHA)
    a = event(jd - STEP, (target + (day - 1) * 12.0) % 360.0)
    return _chart(birth, a, event(a + STEP, (target + day * 12.0) % 360.0), "Daily TP", PRAVESHA)


_PRAVESHA = {"tithi": "TP", "nakshatra": "NP", "yoga": "YP"}
def _tithi_return(birth, cfg):
    """The natal Moon - Sun angle and the search for the next moment it recurs."""
    p = E.planet_positions(birth.jd_ut, cfg)
    return (p["Moon"]["lon"] - p["Sun"]["lon"]) % 360.0, lambda j, t: S.longitude_event(j, 2, t, 1, "diff", False, cfg)


def tithi_pravesha_months(birth, cfg, s, year):
    """The Amanta lunar month of each monthly chart of the Tithi Pravesha year ``year``: 12, or 13 with an Adhika month."""
    if not birth.year <= year <= 9000:
        raise ValueError("year must be %d to 9000" % birth.year)
    start, end = TP.annual_tithi_pravesha(birth, year - birth.year, cfg, s.tp_solar_month)
    target, event = _tithi_return(birth, cfg)
    names, jd = [], start
    while jd < end - 1 and len(names) < 13:   # end is the next annual chart; a day's slack for the search
        m = CAL.lunar_month(jd, 0, cfg, 2000, 1)   # only the name is used, so the tithi and Gregorian date (for the eras) are moot
        names.append(("Adhika " if m["adhika"] else "") + m["amanta"] + (" (Kshaya %s)" % m["kshaya"] if m["kshaya"] else ""))
        jd = event(jd + STEP, target)
    return names


_PERIOD = {"annual": "Annual %s", "monthly": "Monthly %s", "fortnightly": "Fortntly%s", "daily": "Daily %s"}


# how far back a chart of each period surely lies (a year, 2 months, 3 weeks, 3 days)
_BACK = {"annual": 400.0, "monthly": 62.0, "fortnightly": 21.0, "daily": 3.0}


def pravesha(birth, cfg, jd_from, kind, period, before=False):
    """Route (2): the first chart of the kind and period after ``jd_from`` (``before``: the last one before it), until the next one."""
    start = TP.next_pravesha(birth, jd_from - _BACK[period] if before else jd_from, kind, period, cfg)
    while before:       # next_pravesha only searches forward: walk up to the date
        following = TP.next_pravesha(birth, start + STEP, kind, period, cfg)
        if following >= jd_from:
            break
        start = following
    end = TP.next_pravesha(birth, start + STEP, kind, period, cfg)
    return _chart(birth, start, end, _PERIOD[period] % _PRAVESHA[kind], PRAVESHA)


def angular_return(birth, cfg, jd_from, a, b, backward):
    """The moment bodies ``a`` and ``b`` (1 Sun .. 9 Ketu) are again as far apart as at birth."""
    if a == b:
        raise ValueError("choose two different bodies")
    p = E.planet_positions(birth.jd_ut, cfg)
    target = (p[S.NAMES[a]]["lon"] - p[S.NAMES[b]]["lon"]) % 360.0
    return _chart(birth, *S.event_period(jd_from, a, target, b, "diff", backward, cfg), "Ang Ret %s-%s" % (ABBR[a], ABBR[b]))


# Which Eclipse Mode combo (1032) -> next_eclipse's arguments, and the chart's name by type
_ECLIPSE_NAMES = {
    "lunar": {"total": "Tot Lun Ecli", "partial": "Part Lun Ecli", "penumbral": "Pen Lun Ecli"},
    "solar": {"total": "Tot Solar Ecli", "annular": "Annular Solar Ecli", "partial": "Part Solar Ecli"},
    "local": {"total": "Total Solar Ecli", "annular": "Annular Solar Ecli", "partial": "Part Solar Ecli"}}


def _eclipse(birth, cfg, jd, which, backward, at_max):
    kind, place = ("lunar", None) if which == "lunar" else ("solar", birth if which == "local" else None)

    def moment(e):      # a local contact the place does not see comes back as 0
        return e["max_jd"] if at_max else (e["begin_jd"] or e["max_jd"])
    e = E.next_eclipse(jd, kind, place, backward, cfg)
    if not backward and moment(e) <= jd:     # it stays on an eclipse whose start is already behind; "Next" moves on
        e = E.next_eclipse(e["max_jd"] + 1.0, kind, place, False, cfg)
    after = E.next_eclipse(moment(e) + 1.0, kind, place, False, cfg)    # swe_*_eclipse_when from the chart + a day
    return _chart(birth, moment(e), moment(after), _ECLIPSE_NAMES[which].get(e["type"], "Ann Tot S Ecli"))


# Combo 1004 of the Planetary Transit form: the part of the zodiac -> the parts in a sign, for varga_window
DIVISIONS = {"Rasi": 1.0, "Nakshatra": 2.25, "Navamsa": 9.0, **{"D-%d" % n: float(n) for n in (
    2, 3, 4, 5, 6, 7, 8, 10, 11, 12, 16, 20, 24, 27, 30, 40, 45, 60, 108, 144)}}


def _body(i):
    if not 0 <= i <= 9:
        raise ValueError("no such body: %d" % i)
    return i


def mundane(birth, cfg, s, kind, backward=True, in_mode=False, body=1, other=7, angle=0.0, division="Rasi",
            eclipse="lunar", at_max=False, years=1.0, days=0.0):
    """A button of the Mundane form: the event before or after the current chart ``birth``, in effect
    until the next one. The combos start on the previous event, Jupiter-Saturn and the Sun by rasi."""
    jd = birth.jd_ut
    lunar_def = 2 * s.lunar_month_kind + int(s.lunar_tropical)      # LunarYrDef
    if in_mode:
        jd += -STEP if backward else STEP
    if kind == "eclipse":
        return _eclipse(birth, cfg, jd, eclipse, backward, at_max)
    if kind == "stationary":
        return _stationary(birth, cfg, body, jd, backward)
    if kind == "swearing_in":
        return swearing_in(birth, years, days)
    if kind == "planet_transit":
        _body(body)
        parts = DIVISIONS[division]

        def find(j, back):
            since, until = S.varga_window(j, body, parts, cfg, birth)
            return j - since if back else j + until
        title = "%s change (%s)" % (division, ABBR[body])
    elif kind == "conjunction":
        if _body(body) == _body(other):
            raise ValueError("choose two different bodies")
        find = lambda j, back: S.longitude_event(j, body, angle % 360.0, other, "diff", back, cfg, birth)  # noqa: E731
        title = "%s-%s %s" % (ABBR[body], ABBR[other], "Opp" if angle == 180.0 else "Conj")     # any other angle too
    else:
        title, find = {
            "solar_year": ("Solar Month", lambda j, b: S.solar_year(j, b, s.solar_year_sign, s.solar_tropical, cfg)),    # the New Year chart's name in this list
            "solar_month": ("Solar Month", lambda j, b: S.solar_month(j, b, s.solar_tropical, cfg)),
            "lunar_year": ("Lunar Year", lambda j, b: S.lunar_year(j, b, lunar_def, s.lunar_year_sign, cfg)),
            "lunar_month": ("Lunar Month", lambda j, b: S.lunar_month(j, b, lunar_def, cfg)),
            "lunar_day": ("Lunar Day", lambda j, b: S.lunar_day(j, b, cfg=cfg)),
            "fortnight": ("Fortnight Chart", lambda j, b: S.fortnight(j, b, cfg=cfg)),
            "ardra": ("Meteorological Yr", lambda j, b: S.longitude_event(j, 1, 200.0 / 3.0, backward=b, cfg=cfg)),
        }[kind]
    start = find(jd, backward)
    return _chart(birth, start, find(start + STEP, False), title)


# The builders of these run on; the view of an event chart lists one cycle
EVENT_VIEW = {"yogini_dasa": 8, "shat_trimsa_sama_dasa": 8, "tithi_yogini_dasa_of_janma_tithi": 8,
              "saptarshi_nakshatra_dasa": 10, "chara_dasa_of_d_1": 12}


def _stationary(birth, cfg, body, jd, backward):
    """Stationary Transit Mode: the next (previous) station of Mars .. Ketu and the one after it."""
    if body < 3:
        raise ValueError("only Mars to Ketu have stations")
    if body >= 8 and cfg.nodes == "mean":      # time_search.retrograde_station would step forever: the mean nodes never turn
        raise ValueError("the mean nodes never change direction; use the true nodes in Preferences")
    start, end = S.retrograde_period(jd, body, not backward, cfg)
    return _chart(birth, start, end, "Retro change (%s)" % ABBR[body])


def swearing_in(birth, years, days):
    """"Treat the current chart as a mundane chart": the same moment, its dasas fitted into the period of effect."""
    span = years * 365.24219 + days
    if span <= 0:
        raise ValueError("the period of effect must be longer than zero")
    when = birth.jd_ut
    return _chart(birth, when, when + span, "Swearing-in")


def entry_chart(birth, start, end, title):
    """Entry chart of a dasa period: the chart at its start, in effect until its end."""
    b = _at(birth, start)
    return {"title": title, "birth": dataclasses.asdict(b), "start": start, "end": end,
            "event": {"kind": OTHER, "name": title, "span_days": (end - start).total_seconds() / 86400.0}}


def add_months(birth, months):
    """A step of the stepping buttons by Month or Year: the same day and time, that many calendar months on (the day cut to the month's end)."""
    y, m = divmod(birth.year * 12 + birth.month - 1 + months, 12)
    m += 1
    last = E.jd_to_calendar(E.julian_day_ut(y + (m == 12), m % 12 + 1, 1, 0.0, birth.gregorian) - 1.0, birth.gregorian)[2]
    return dataclasses.replace(birth, year=y, month=m, day=min(birth.day, last))


def nisheka(birth, cfg, ch):
    """The conception chart, its dasas fitted into its count of days."""
    start = W.nisheka_moment(birth, ch, cfg)
    return _chart(birth, start, start + (birth.jd_ut - start) * 365.0 / 360.0, "Nisheka/Adhana")   # the moment is days x 360/365; the span the days


def lifecycle(birth, cfg, s, n):
    """The chart ``n`` lifecycles (144 years by default) on or back, a birth chart of its own."""
    b = _at(birth, W.lifecycle_moment(birth, n, cfg, s.lifecycle_years, s.lifecycle_kind))
    return {"title": "Natal Chart (cycle %d)" % (n + 1), "birth": dataclasses.asdict(b), "start": _when(b)}


def _varga_event(jd, body, goal, division, backward, cfg, birth, opt):
    """When ``body``'s longitude in D-``division`` reaches ``goal``: steps of a sixth of the smallest part at the body's speed, then bisection on the jump over the goal. A part's end jumps by up to 360 degrees; a crossing is a small move only."""
    f = lambda j: V.varga_longitude(S.body_longitude(body, cfg, birth)(j), division, opt)  # noqa: E731
    speed = max(abs(E.planet_positions(jd, cfg)[S.NAMES[max(body, 1)]]["speed"]), 0.02) if body else 360.0
    step = (-1 if backward else 1) * (30.0 / division / 6.0) / speed
    gap = lambda x: (x - goal + 180.0) % 360.0 - 180.0  # noqa: E731
    a, ga = jd, gap(f(jd))
    limit = 366.0 * 30 / abs(step)
    n = 0
    while n < limit:
        b = a + step
        gb = gap(f(b))
        if ga * gb <= 0 and abs(ga - gb) < 90.0:
            for _ in range(50):
                m = (a + b) / 2.0
                gm = gap(f(m))
                if ga * gm <= 0:
                    b, gb = m, gm
                else:
                    a, ga = m, gm
            return (a + b) / 2.0
        a, ga = b, gb
        n += 1
    raise ValueError("no such moment within 30 years")


def special_search(birth, cfg, ch, jd_from, body, offset, ahead, target, value, backward, division=1, s=None):
    """Transits > Special Search: ``body`` exactly ``offset`` degrees behind or ahead of a natal planet or saham, or the
    start of a sign, in D-``division``, before or after ``jd_from``."""
    if target == "planet":
        lon = ch["lagna_lon"] if value == 0 else ch["planet_longitudes"][S.NAMES[value]]
    elif target == "saham":
        lons = [ch["lagna_lon"]] + [ch["planet_longitudes"][p] for p in S.NAMES[1:8]]
        lon = SL.saham_longitudes(lons, E.day_lords(birth, cfg)["is_day"])[value]
    else:
        lon = value * 30.0
    if division != 1:
        opt = ST.varga_options(s)
        if target != "sign":
            lon = V.varga_longitude(lon, division, opt)
        goal = (lon + (offset if ahead else -offset)) % 360.0
        find = lambda j, back: _varga_event(j, body, goal, division, back, cfg, birth, opt)  # noqa: E731
        start = find(jd_from, backward)
        return _chart(birth, start, find(start + STEP, False), "Transit Search")
    goal = (lon + (offset if ahead else -offset)) % 360.0
    find = lambda j, back: S.longitude_event(j, body, goal, backward=back, cfg=cfg, birth=birth)  # noqa: E731
    start = find(jd_from, backward)
    return _chart(birth, start, find(start + STEP, False), "Transit Search")


# the form's seed choices: Lagna .. Ketu as a dasa seed (settings.SEEDS)
SEED_OF_POINT = [4, 8, 0, 9, 10, 11, 12, 13, 14, 15]


def progression(birth, cfg, ch, kind, at, division=1, dasa="vimsottari_dasa", seed=2, s=None):
    """A button of the Progressions form to the moment ``at`` (the form has no zone: the chart's), in D-``division`` and, for the
    nakshatra progression, the chosen dasa from the chosen point. The dasas stay the natal ones."""
    pc = E.build_chart(at, cfg)
    natal_sun, now = ch["planet_longitudes"]["Sun"], pc["planet_longitudes"]["Sun"]
    years, days = at.year - birth.year, at.jd_ut - birth.jd_ut
    out = {"natal_dasas": True, "start": _when(at)}
    if kind == "solar":
        b = _at(birth, E.dasa_year_mapper(birth, cfg)(MS.solar_progression_years(natal_sun, now, years, days, division)))
        deg = 30.0 / division     # the chart's name: "Progressed (%d deg)" or "Progressed (%d-%02d deg)"
        title = "Progressed (%d deg)" % deg if deg == int(deg) else "Progressed (%d-%02d deg)" % (deg, round((deg % 1) * 60))
        return {**out, "title": title, "birth": dataclasses.asdict(b), "start": _when(b)}
    if kind == "bhrigu":
        opt = ST.varga_options(s) if s else V.DEFAULT
        seven = {p: V.varga_longitude(ch["planet_longitudes"][p], division, opt) for p in S.NAMES[1:8]}
        lons = MS.compute_bhrigu_pada_progression(seven, natal_sun, now, years, days)
        return {**out, "title": "Progressed (Bhrigu)", "birth": {**dataclasses.asdict(at), "adjust": {"lons": lons}}}
    if kind == "sudarsana":
        arc, title = MS.sudarsana_progression_arc(natal_sun, now, years, days), "Progressed (SCD)"
    else:
        jc = J.JChart(ch)
        opt = ST.varga_options(s) if s else V.DEFAULT
        point = [V.varga_longitude(x, division, opt) for x in jc.lons]
        to_date = E.dasa_year_mapper(birth, cfg)
        d = D.BY_KEY[dasa]
        if division != 1:       # the seed's longitude in the chosen varga
            jc.lons = point
        mds = d.build(jc, to_date, seed=SEED_OF_POINT[seed]) if dasa in D.NAK_FAMILY else d.build(jc, to_date)
        arc = J.nakshatra_progression_arc(mds, to_date, _when(at), point[seed])
        title = "Prog (NaksDasa)"
    return {**out, "title": title, "birth": {**dataclasses.asdict(at), "adjust": {"base": dataclasses.asdict(birth), "arc": arc}}}


_PRASNA = {"108": (108, "Prasna-108 (%d)"), "249": (249, "Prasna-249 (%d)"), "nadi": (1800, "Nadi Prasna (%d)")}


def prasna(birth, kind, n, replace, years=0.0, days=0.0):
    """The Prasna form: the chart keeps its moment; the number fixes the Prasna Lagna, shown as a body of its own or
    in place of the lagna. The dasas stay the natal ones, unless compressed into ``years`` and ``days`` (group "Dasa Compression")."""
    top, title = _PRASNA[kind]
    if not 1 <= n <= top:
        raise ValueError("enter a number from 1 to %d" % top)
    lon = W.prasna_lagna(kind, n)
    out = {"title": title % n, "natal_dasas": True, "start": _when(birth),
           "birth": {**dataclasses.asdict(birth), "adjust": {"lagna" if replace else "prasna_lagna": lon}}}
    span = years * 365.24219 + days
    if span > 0:
        out = {**out, "natal_dasas": False, "end": _when(birth) + timedelta(days=span), "event": {"kind": OTHER, "name": title % n, "span_days": span}}
    return out


def fit_dasa(d, event, natal, birth, cfg, s, ev):
    """Dasa ``d`` of a derived chart: (to_date, its periods, year definition, its options). ``event``, ``natal``: its JChart and the
    natal one. Each period is scaled so the whole dasa fills the span; Tajaka charts take their seeds from the natal chart."""
    fn = d.build
    kw = D.options(d.key, s)
    if getattr(fn, "func", None) is J.group_dasa:
        fn = functools.partial(fn, past_table=True)    # past its table, without wrapping
    seed = s.per_dasa.get(d.key, {}).get("tajaka_seed", "default")      # the dasa's options, per dasa
    if ev.kind == TAJAKA and seed == "event":     # not from the natal chart: the Tajaka chart's own seed
        build = lambda td: J.event_dasa(fn, event, td, natal, **kw)  # noqa: E731
    elif ev.kind == TAJAKA and seed == "natal" and J._builder_key(fn) in J.TAJAKA_NATAL:     # from the natal chart, not moved on a star a year
        build = lambda td: J.event_dasa(fn, natal, td, **kw)  # noqa: E731
    elif ev.kind == TAJAKA:
        _, signs = T.muntha_position(natal.lons[0], [v[0] for v in natal.signs], ev.counts, method=s.muntha_method)
        build = lambda td: J.tajaka_dasa(fn, natal, event, signs, sum(ev.counts), td, **kw)  # noqa: E731
    else:
        build = lambda td: J.event_dasa(fn, event, td, natal, **kw)  # noqa: E731
    definition = J.event_year_definition(s.year_definition, ev.kind, ev.name, s.special_year_tajaka, s.special_year_tp)
    plain = ST.year_mapper(birth, cfg, s, definition)
    to_date = J.fitted_to_span(plain, ev.span_days, J.event_years(fn, build(plain), **kw))
    mds = build(to_date)
    if ev.kind == OTHER and not s.dasa_sesham_mundane:
        mds = J.without_sesham(mds, to_date)
    return to_date, mds[:EVENT_VIEW.get(d.key)], definition, kw
