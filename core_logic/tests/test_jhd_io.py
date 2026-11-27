"""Every sample chart in data/sample_charts must parse and round-trip."""
import glob
import os
import unittest

from core_logic import jhd_io

SAMPLES = sorted(glob.glob(os.path.join(os.path.dirname(__file__), "..", "..", "data", "sample_charts", "*.jhd")))


class TestJhdIo(unittest.TestCase):
    def test_samples_exist(self):
        self.assertEqual(len(SAMPLES), 18)

    def test_all_samples_parse_with_sane_values(self):
        for path in SAMPLES:
            c = jhd_io.parse_jhd_file(path)
            self.assertTrue(1 <= c["month"] <= 12 and 1 <= c["day"] <= 31, path)
            self.assertTrue(0 <= c["hour_local"] < 24, path)
            self.assertTrue(4.0 <= c["tz_east_hours"] <= 7.0, (path, c["tz_east_hours"]))   # all charts are Indian
            self.assertTrue(65 <= c["longitude_east"] <= 95, path)
            self.assertTrue(5 <= c["latitude"] <= 35, path)
            self.assertEqual(c["name"], os.path.splitext(os.path.basename(path))[0])

    def test_known_values(self):
        by = {os.path.basename(p): jhd_io.parse_jhd_file(p) for p in SAMPLES}
        viv = by["Swami Vivekananda.jhd"]            # legacy: time 6.33 means 6h33m, tz -5.54 means 5h54m east
        self.assertAlmostEqual(viv["hour_local"], 6 + 33 / 60, places=6)
        self.assertAlmostEqual(viv["tz_east_hours"], 5 + 54 / 60, places=6)
        self.assertAlmostEqual(viv["longitude_east"], 88 + 30 / 60, places=6)
        self.assertEqual(viv["layout"], "legacy_ephemeris")
        self.assertAlmostEqual(viv["cached_longitudes"]["Sun"], 269.439396, places=6)
        gandhi = by["Mahatma Gandhi.jhd"]            # time is H.MM in every layout: 7.20 = 7h20m
        self.assertAlmostEqual(gandhi["hour_local"], 7 + 20 / 60, places=6)
        self.assertAlmostEqual(gandhi["tz_east_hours"], 4.654444, places=5)  # line 5, H.MM
        self.assertEqual(gandhi["city"], "Unknown")
        author = by["Author of this software.jhd"]   # 17.506666... = 17h50m40s (seconds / 6000)
        self.assertAlmostEqual(author["hour_local"], 17 + 50 / 60 + 40 / 3600, places=6)
        self.assertEqual(author["country_index"], 105)  # India in the atlas country table
        self.assertTrue(author["gregorian"])
        self.assertEqual(author["atmosphere"], {"pressure": 1013.25, "temperature": 20.0})
        india = by["India.jhd"]
        self.assertEqual((india["city"], india["country"]), ("Delhi", "India"))
        self.assertAlmostEqual(india["hour_local"], 1 / 3600, places=5)  # 0.000167 = 00:00:01

    def test_round_trip(self):
        for path in SAMPLES:
            a = jhd_io.parse_jhd_file(path)
            b = jhd_io.parse_jhd_string(jhd_io.serialize_to_jhd(a))
            for k in ("year", "month", "day"):
                self.assertEqual(a[k], b[k], path)
            for k, tol in (("hour_local", 1e-5), ("tz_east_hours", 1e-5), ("longitude_east", 1e-5), ("latitude", 1e-5)):
                self.assertAlmostEqual(a[k], b[k], delta=tol, msg=(path, k))

    def test_hm_codec(self):
        for v in (-5.5, 5.5, 88.5, -81.1333333, 0.0, 5.8833333):
            self.assertAlmostEqual(jhd_io.decode_hm("%.6f" % jhd_io.encode_hm(v)), v, places=5)


if __name__ == "__main__":
    unittest.main()
