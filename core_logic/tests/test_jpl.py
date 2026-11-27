"""
NASA JPL's DE442 under both ephemerides: the Swiss Ephemeris on JPL's binary file (config.py ``_ephe_flag``, built by
jpl.py ``asc2eph``) and Settings > Ephemeris "XALEN" (jpl.py, native/jpl_kernel) on its SPK kernel, under every
position flag the app sets. Skipped without the files or the native module (./start.sh builds and fetches them).

On the same data the two differ only in how they turn it into a place of date (measured 2026-11-26, 1560-2640): the
Sun, Moon and planets by under 0.01", the true node 0.08". The mean node is a formula in each, the IAU polynomial
against Swiss Ephemeris' own series: 0.25" over 1550-2200, 1.4" by 2640. The topocentric Moon differs by 0.07-0.17":
Swiss Ephemeris' observer sits on a slightly tilted equator, while XALEN's agrees with the IAU SOFA routines (c2t06a,
gd2gc, pmat06) to 0.003" (checked with pyerfa and jplephem on DE442; the kernel reading agrees with jplephem to 1e-12),
and by 2640 the two sidereal-time models part by over a second (0.5").
"""
import os
import struct
import unittest
from dataclasses import replace

from core_logic import ephemeris as E
from core_logic.ephemeris import jpl

try:
    import swisseph as swe
except ImportError:  # pragma: no cover
    swe = None

HAVE = swe is not None and jpl.jpl_kernel is not None and os.path.isfile(jpl.KERNEL_PATH) and E._jpl_span() is not None
HAVE_EPH = swe is not None and E._jpl_span() is not None
XALEN = E.EphemerisConfig(ephemeris="xalen")
DELHI = (77.209, 28.6139, 216.0)


def arcsec(a, b):
    return abs((a - b + 180.0) % 360.0 - 180.0) * 3600.0


@unittest.skipUnless(HAVE, "the JPL files or the native module are missing (run ./start.sh)")
class TestJplKernel(unittest.TestCase):
    def setUp(self):
        self.k = E.engine(XALEN)
        self.s = E._require_swe()

    def test_the_kernel(self):
        start, end, label = jpl.jpl_kernel.load(jpl.KERNEL_PATH)
        self.assertEqual(label, "DE442")
        self.assertEqual((start, end), (2287184.5, 2688976.5))     # 31 Dec 1549 to 25 Jan 2650 (de442_tech-comments.txt)

    def test_positions_match_the_swiss_ephemeris(self):
        s, k = self.s, self.k
        flag_sets = [s.FLG_TRUEPOS | s.FLG_NONUT, s.FLG_TRUEPOS, 0, s.FLG_NONUT, s.FLG_NOABERR, s.FLG_NOGDEFL, s.FLG_EQUATORIAL,
                     s.FLG_TOPOCTR, s.FLG_TOPOCTR | s.FLG_TRUEPOS | s.FLG_NONUT | s.FLG_EQUATORIAL]
        with E._SWE_LOCK:
            k.set_topo(*DELHI)
            for year in (1560, 1700, 1872, 1947, 1990, 2024, 2100, 2400, 2640):
                for month in (2, 6, 10):
                    jd = s.julday(year, month, 11, 7.25)
                    for flags in flag_sets:
                        f = E._ephe_flag(s, jd) | s.FLG_SPEED | flags
                        for body in range(12):
                            a, b = s.calc_ut(jd, body, f)[0], k.calc_ut(jd, body, f)[0]
                            tol = {10: 1.5, 11: 0.15}.get(body, 0.02)
                            if body == 1 and flags & s.FLG_TOPOCTR:
                                tol = 0.25 if year <= 2400 else 0.6   # Swiss Ephemeris' observer; the sidereal times by 2640
                            where = (year, month, hex(flags), body)
                            self.assertLess(arcsec(a[0], b[0]), tol, where)
                            self.assertLess(abs(a[1] - b[1]) * 3600.0, tol, where)
                            self.assertLess(abs(a[2] - b[2]) / a[2], 1e-5, where)
                            # Swiss Ephemeris' speeds of apparent places, and its observer's, are its own approximations
                            if flags & s.FLG_TRUEPOS and not flags & s.FLG_TOPOCTR:
                                self.assertLess(abs(a[3] - b[3]) * 3600.0, 0.2, where)

    def test_outside_the_kernel_the_swiss_ephemeris_answers(self):
        s, f = self.s, self.s.FLG_SWIEPH | self.s.FLG_SPEED
        for y in (1500, 2700):
            jd = s.julday(y, 1, 1, 0.0)
            self.assertEqual([self.k.calc_ut(jd, b, f) for b in range(12)], [s.calc_ut(jd, b, f) for b in range(12)])

    def test_other_bodies_and_calls_are_the_swiss_ephemeris(self):
        s, jd = self.s, 2460640.5
        self.assertEqual(self.k.calc_ut(jd, s.MEAN_APOG)[0], s.calc_ut(jd, s.MEAN_APOG)[0])
        self.assertEqual(self.k.calc_ut(jd, s.ECL_NUT)[0], s.calc_ut(jd, s.ECL_NUT)[0])
        self.assertEqual(self.k.houses(jd, 28.6, 77.2, b"P"), s.houses(jd, 28.6, 77.2, b"P"))
        with self.assertRaises(ValueError):
            self.k.calc_ut(jd, s.MARS, s.FLG_SWIEPH | s.FLG_HELCTR)

    def test_a_chart_under_each_setting(self):
        b = E.BirthData(1947, 8, 15, 0.0, 5.5, *DELHI)
        for kw in ({}, {"ayanamsa": "JAGANNATHA"}, {"topocentric": True}, {"true_positions": False, "apparent_refraction": True},
                   {"nodes": "mean"}, {"swisseph_202": False}, {"ayanamsa": "TROPICAL"}):
            cfg = replace(E.EphemerisConfig(ayanamsa="PUSHYA_PAKSHA", nodes="true"), **kw)
            a, x = E.planet_positions(b.jd_ut, cfg, b, True), E.planet_positions(b.jd_ut, replace(cfg, ephemeris="xalen"), b, True)
            self.assertNotEqual(a, x, kw)
            for name in a:
                self.assertLess(arcsec(a[name]["lon"], x[name]["lon"]), 0.1, (kw, name))
                self.assertEqual(a[name]["retrograde"], x[name]["retrograde"], (kw, name))


@unittest.skipUnless(HAVE_EPH, "JPL's DE442 file is missing (run ./start.sh)")
class TestSwissOnDE442(unittest.TestCase):
    def test_the_file(self):
        self.assertEqual(E._jpl_span(), (2287184.5, 2688976.5))
        with open(os.path.join(E.JPL_EPHE_PATH, E.JPL_FILE), "rb") as f:
            head = f.read(2848)
        self.assertEqual(head[:35], b"JPL Planetary Ephemeris DE442/LE442")
        self.assertEqual(struct.unpack("<i", head[2840:2844])[0], 442)

    def test_the_swiss_ephemeris_reads_it_inside_its_span_and_its_own_files_outside(self):
        s = E._require_swe()
        for year, used in ((1500, s.FLG_SWIEPH), (1551, s.FLG_JPLEPH), (2024, s.FLG_JPLEPH), (2649, s.FLG_JPLEPH), (2700, s.FLG_SWIEPH)):
            jd = s.julday(year, 3, 1, 0.0)
            ret = s.calc_ut(jd, s.MOON, E._ephe_flag(s, jd) | s.FLG_SPEED)[1]
            self.assertEqual(ret & (s.FLG_JPLEPH | s.FLG_SWIEPH | s.FLG_MOSEPH), used, year)   # never the Moshier model

    def test_delta_t_does_not_follow_the_last_file_read(self):
        s, old = E._require_swe(), 2268924.5     # 1500, before DE442: the .se1 files
        first = s.deltat_ex(old, s.FLG_SWIEPH)
        s.calc_ut(2460640.5, s.SUN, s.FLG_JPLEPH)
        s.calc_ut(2460640.5, s.SUN, s.FLG_SWIEPH)
        self.assertEqual(s.deltat_ex(old, s.FLG_SWIEPH), first)
        self.assertEqual(s.get_tid_acc(), s.TIDAL_DE441)

    def test_a_chart_is_de442s(self):
        b = E.BirthData(1990, 6, 15, 10.5, 5.5, *DELHI)
        x = E.planet_positions(b.jd_ut, E.EphemerisConfig(ayanamsa="TROPICAL", true_positions=True), b)
        s = E._require_swe()
        for name, body in (("Moon", s.MOON), ("Mars", s.MARS)):
            self.assertEqual(x[name]["lon"], s.calc_ut(b.jd_ut, body, s.FLG_JPLEPH | s.FLG_SPEED | s.FLG_TRUEPOS)[0][0])


@unittest.skipUnless(swe is not None, "pyswisseph not installed")
class TestSwissIsTheDefault(unittest.TestCase):
    def test_default(self):
        self.assertEqual(E.EphemerisConfig().ephemeris, "swiss")
        self.assertIs(E.engine(E.EphemerisConfig()), E._require_swe())


if __name__ == "__main__":
    unittest.main()
