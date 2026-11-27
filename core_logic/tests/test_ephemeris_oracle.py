"""
Validate the ephemeris layer against the positions stored in five legacy
sample charts (cached sidereal longitudes of Sun..mean Rahu and the lagna).
Skipped when pyswisseph is not installed.
"""
import glob
import os
import unittest

from core_logic import jhd_io

try:
    from core_logic import ephemeris as E
    import swisseph  # noqa: F401
    HAVE_SWE = True
except ImportError:  # pragma: no cover
    HAVE_SWE = False

SAMPLES = sorted(glob.glob(os.path.join(os.path.dirname(__file__), "..", "..", "data", "sample_charts", "*.jhd")))


def diff(a, b):
    return abs(((a - b + 180.0) % 360.0) - 180.0)


@unittest.skipUnless(HAVE_SWE, "pyswisseph not installed")
class TestEphemerisOracle(unittest.TestCase):
    def oracle_charts(self):
        out = [jhd_io.parse_jhd_file(p) for p in SAMPLES]
        return [c for c in out if c["cached_longitudes"]]

    def test_five_oracle_charts_found(self):
        self.assertEqual(len(self.oracle_charts()), 5)

    def test_planets_and_lagna_match_stored(self):
        for c in self.oracle_charts():
            # legacy charts were cached with apparent positions (max residual 0.023 deg
            # vs 0.033 with true positions); True Lahiri, mean node
            chart = E.build_chart(jhd_io.to_birth_data(c), E.EphemerisConfig(true_positions=False))
            for name, ref in c["cached_longitudes"].items():
                self.assertLess(diff(chart["planet_longitudes"][name], ref), 0.03, (c["name"], name))
            self.assertLess(diff(chart["lagna_lon"], c["cached_lagna"]), 0.03, c["name"])

    def test_legacy_mask_is_retrograde_flags(self):
        order = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
        for c in self.oracle_charts():
            chart = E.build_chart(jhd_io.to_birth_data(c))
            expect = "".join("1" if chart["retrograde"][n] else "0" for n in order) + "00"
            self.assertEqual(c["legacy_flags"], expect, c["name"])

    def test_ketu_is_opposite_rahu(self):
        chart = E.build_chart(jhd_io.to_birth_data(self.oracle_charts()[0]))
        self.assertAlmostEqual(diff(chart["planet_longitudes"]["Rahu"], chart["planet_longitudes"]["Ketu"]), 180.0, places=6)

    def test_ayanamsa_star_definitions(self):
        jd = E.julian_day_ut(1990, 5, 17, 6.0)
        from core_logic.utils import norm360
        swe = E._require_swe()     # the app's own paths: setting one here would drop JPL's DE442 file for every later test
        for key, star, target in (("TRUE_LAHIRI", "SE2Spica", 180.0), ("ROHINI_PAKSHA", "SE2Aldebaran", 46 + 40 / 60),
                                  ("PUSHYA_PAKSHA", ",se2deCnc", 106.0)):
            ay = E.ayanamsa_value(jd, E.EphemerisConfig(ayanamsa=key))
            trop = swe.fixstar_ut(star, jd, swe.FLG_SWIEPH | swe.FLG_TRUEPOS | swe.FLG_NONUT)[0][0]
            self.assertAlmostEqual(norm360(trop - ay), target, places=6, msg=key)
        # True Lahiri must agree with Swiss Ephemeris' own Spica-based mode
        swe.set_sid_mode(swe.SIDM_TRUE_CITRA, 0, 0)
        self.assertAlmostEqual(E.ayanamsa_value(jd), swe.get_ayanamsa_ut(jd), delta=0.005)

    def test_all_supported_ayanamsas_run(self):
        jd = E.julian_day_ut(1990, 5, 17, 6.0)
        n = 0
        for a in E.AYANAMSAS:
            if a["kind"] in ("unsupported", "custom"):
                continue
            v = E.ayanamsa_value(jd, E.EphemerisConfig(ayanamsa=a["key"]))
            self.assertTrue(-1.0 < v < 60.0, a["key"])
            n += 1
        self.assertEqual(n, 21)   # all but the custom star (Deva-datta and Chandra Hari ported 2026-10-27)

    def test_sunrise_is_sane_and_ordered(self):
        for c in self.oracle_charts():
            chart = E.build_chart(jhd_io.to_birth_data(c))
            self.assertTrue(4.5 < chart["sunrise_hours"] < 7.5, c["name"])
            self.assertTrue(16.5 < chart["sunset_hours"] < 20.0, c["name"])

    def test_all_house_systems_return_12_ascending_cusps(self):
        b = jhd_io.to_birth_data(self.oracle_charts()[0])
        for sysname in E.HOUSE_SYSTEM_CODES:
            h = E.house_cusps(b.jd_ut, b.latitude, b.longitude_east, sysname)
            self.assertEqual(len(h["cusps"]), 12, sysname)
            self.assertLess(diff(h["cusps"][0], h["ascendant"]) if sysname in ("PLACIDUS", "KOCH", "PORPHYRY", "EQUAL", "REGIOMONTANUS", "CAMPANUS") else 0.0, 1e-6, sysname)

    def test_engines_accept_chart_output(self):
        """The 'connection': ephemeris output feeds the calculation engines unchanged."""
        from core_logic import dashas, ashtakavarga
        from datetime import datetime
        c = self.oracle_charts()[-1]
        chart = E.build_chart(jhd_io.to_birth_data(c))
        tree = dashas.compute_vimshottari_tree(chart["planet_longitudes"]["Moon"], datetime(c["year"], c["month"], c["day"]))
        self.assertEqual(len(tree), 9)
        av = ashtakavarga.run_full_ashtakavarga_pipeline(
            {k: v for k, v in chart["planet_signs"].items() if k in E.CLASSICAL_PLANETS}, chart["lagna_sign"])
        self.assertEqual(sum(av["sav"]), 337)


if __name__ == "__main__":
    unittest.main()
