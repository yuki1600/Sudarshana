import unittest

from core_logic.sahams_library import compute_all_50_sahams, saham_coverage, SAHAMA_NAMES
from core_logic.tajika import compute_sahams


def dm(d, m):
    return d + m / 60.0


class TestSahamCoverage(unittest.TestCase):
    def test_numbers_documented_in_audit(self):
        r = saham_coverage()
        self.assertEqual(len(SAHAMA_NAMES), 36)
        self.assertEqual(r["missing"], [])
        self.assertEqual(len(r["present"]), 36)
        self.assertEqual(len(r["not_in_main_list"]), 17)

    def test_worked_example(self):
        """A worked example (PVR 28.8): night chart, Lagna 10Cp50, Saturn 19Ar10, Mars 24Pi58,
        Moon 15Pi14, Mercury 11Aq28 -> Artha 2Sc30, Samartha 5Pi02, Vanik 7Sg04."""
        lons = {"Sun": 100.0, "Moon": dm(345, 14), "Mars": dm(354, 58), "Mercury": dm(311, 28),
                "Jupiter": 50.0, "Venus": 300.0, "Saturn": dm(19, 10), "Rahu": 10.0}
        r = compute_all_50_sahams(lons, dm(280, 50), is_night=True)
        self.assertAlmostEqual(r["Artha (Wealth / Money)"]["longitude"], dm(212, 30), places=3)
        self.assertAlmostEqual(r["Samartha (Enterprise / Capability)"]["longitude"], dm(335, 2), places=3)
        self.assertAlmostEqual(r["Vanik (Commerce)"]["longitude"], dm(247, 4), places=3)
        self.assertTrue(r["Vanik (Commerce)"]["in_main_list"])
        self.assertFalse(r["Kanya (Bride / Virgin)"]["in_main_list"])
        # tajika.compute_sahams takes is_day_birth and must not invert it
        self.assertEqual(compute_sahams(lons, dm(280, 50), is_day_birth=False), r)

    def test_c_term_and_exceptions(self):
        lons = {"Sun": 10.0, "Moon": 100.0, "Mars": 200.0, "Mercury": 250.0,
                "Jupiter": 40.0, "Venus": 70.0, "Saturn": 300.0, "Rahu": 0.0}
        day = compute_all_50_sahams(lons, 0.0, is_night=False)
        # Gaurava = Jupiter - Moon + Sun; Sun (10) lies on the arc Moon(100)->Jupiter(40)
        self.assertAlmostEqual(day["Gaurava (Respect / Status)"]["longitude"], (40 - 100 + 10) % 360)
        # Jalapatana = Cancer 15 - Saturn + Lagna; lagna 0 lies on the arc 300 -> 105, so no +30
        self.assertAlmostEqual(day["Jalapatha (Voyage / Crossing Waters)"]["longitude"], (105 - 300 + 0) % 360)
        # Asha = Saturn - Mars + Lagna; lagna 0 is not on the arc Mars(200) -> Saturn(300): +30
        self.assertAlmostEqual(day["Asha (Desire / Hope)"]["longitude"], (300 - 200 + 0) + 30)
        # Samartha with Mars owning the lagna (Aries) -> Jupiter - Mars + Lagna
        self.assertEqual(day["Samartha (Enterprise / Capability)"]["formula"], "Jupiter - Mars + Lagna")
        night = compute_all_50_sahams(lons, 0.0, is_night=True)
        self.assertEqual(night["Karyasiddhi (Success in Undertakings)"]["formula"], "Saturn - Moon + MoonSignLord")


if __name__ == "__main__":
    unittest.main()
