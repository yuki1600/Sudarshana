"""Quadrant house systems (closed forms) must agree with Swiss Ephemeris' swe_houses."""
import glob
import os
import unittest

from core_logic import house_systems as H
from core_logic import jhd_io

try:
    from core_logic import ephemeris as E
    import swisseph  # noqa: F401
    HAVE_SWE = True
except ImportError:  # pragma: no cover
    HAVE_SWE = False

SAMPLES = sorted(glob.glob(os.path.join(os.path.dirname(__file__), "..", "..", "data", "sample_charts", "*.jhd")))


@unittest.skipUnless(HAVE_SWE, "pyswisseph not installed")
class TestHouseSystemsAgainstSwe(unittest.TestCase):
    def test_closed_forms_match_swe_within_obliquity_tolerance(self):
        cfg = E.EphemerisConfig(ayanamsa="TROPICAL")
        fns = {"PLACIDUS": H.compute_placidus_houses, "KOCH": H.compute_koch_houses,
               "CAMPANUS": H.compute_campanus_houses, "REGIOMONTANUS": H.compute_regiomontanus_houses}
        for path in SAMPLES:
            b = jhd_io.to_birth_data(jhd_io.parse_jhd_file(path))
            for name, fn in fns.items():
                ref = E.house_cusps(b.jd_ut, b.latitude, b.longitude_east, name, cfg)
                mine = fn(ref["ascendant"], ref["mc"], b.latitude)
                for i, (x, y) in enumerate(zip(mine, ref["cusps"])):
                    self.assertLess(abs(((x - y + 180) % 360) - 180), 0.03, (os.path.basename(path), name, i + 1))

    def test_dispatcher_with_ephemeris_supports_every_menu_system(self):
        b = jhd_io.to_birth_data(jhd_io.parse_jhd_file(SAMPLES[0]))
        for name in ("Alcabitus", "Axial_Rotation", "Polich_Page", "Equal_Pada", "Rasi", "Porphyry"):
            c = H.compute_house_cusps(name, 0.0, None, b.latitude, jd_ut=b.jd_ut, longitude_east=b.longitude_east)
            self.assertEqual(len(c), 12, name)

    def test_geometry_only_systems_without_ephemeris(self):
        with self.assertRaises(ValueError):
            H.compute_house_cusps("Alcabitus", 10.0, 280.0, 20.0)


if __name__ == "__main__":
    unittest.main()
