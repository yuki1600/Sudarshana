"""
tests/test_tier2_calculations.py
================================
Unit tests for Special Lagnas, Upagrahas, Avasthas, and Classical Yogas.
"""

import unittest
from core_logic import (
    compute_sree_lagna,
    compute_indu_lagna,
    compute_bhrigu_bindu,
    compute_kunda,
    compute_aprakash_grahas,
    compute_baalaadi_avastha,
    compute_jagrataadi_avastha,
    compute_deeptaadi_avastha
)

class TestTier2AstrologyCalculations(unittest.TestCase):

    def test_special_lagnas_and_upagrahas(self):
        # 1. Sree Lagna: Lagna = 10°, Moon = 13°20' (exact 1 nakshatra = 0 fraction) => 10°
        sl = compute_sree_lagna(lagna_lon=10.0, moon_lon=13.333333)
        self.assertAlmostEqual(sl, 10.0, places=2)

        # 2. Indu Lagna: Lagna in Aries (sign 0), 9th is Sag (lord Jupiter = 10 rays).
        # Moon in Cancer (sign 3), 9th is Pisces (lord Jupiter = 10 rays).
        # Total rays = 20. 20 % 12 = 8th from Moon => Cancer (3) + 7 = Aquarius (10).
        indu_sign, indu_name, rays = compute_indu_lagna(lagna_lon=15.0, moon_lon=105.0)
        self.assertEqual(rays, 20)
        self.assertEqual(indu_sign, 10)
        self.assertEqual(indu_name, "Aquarius")

        # 3. Bhrigu Bindu: forward from Rahu (120°) to Moon (0°) is 240°, midpoint 240° (Sagittarius 0°)
        bb = compute_bhrigu_bindu(moon_lon=0.0, rahu_lon=120.0)
        self.assertAlmostEqual(bb, 240.0)

        # 4. Kunda: Lagna = 10.0° * 81 = 810° % 360° = 90° (Cancer 0°)
        k_lon, nak, sign = compute_kunda(10.0)
        self.assertAlmostEqual(k_lon, 90.0)
        self.assertEqual(sign, "Cancer")

        # 5. Aprakash Grahas: Sun = 0° (Aries 0°)
        # Dhuma = 0 + 133°20' = 133°20'
        # Vyatipata = 360 - 133°20' = 226°40'
        # Parivesha = 226°40' + 180° = 406°40' % 360 = 46°40'
        # Indra Chapa = 360 - 46°40' = 313°20'
        # Upaketu = 313°20' + 16°40' = 330°00'
        aprakash = compute_aprakash_grahas(sun_lon=0.0)
        self.assertAlmostEqual(aprakash["Dhuma"]["longitude"], 133.3333, places=2)
        self.assertAlmostEqual(aprakash["Vyatipata"]["longitude"], 226.6667, places=2)
        self.assertAlmostEqual(aprakash["Parivesha"]["longitude"], 46.6667, places=2)
        self.assertAlmostEqual(aprakash["Indra Chapa"]["longitude"], 313.3333, places=2)
        self.assertAlmostEqual(aprakash["Upaketu"]["longitude"], 330.0, places=2)

    def test_avasthas(self):
        # 1. Baalaadi:
        # Aries 15° (Odd sign, segment 2): Yuva (Adult - Peak)
        b_yuva = compute_baalaadi_avastha(15.0)
        self.assertEqual(b_yuva["avastha_name"], "Yuva (Adult - Peak)")
        self.assertEqual(b_yuva["potency_fraction"], 1.0)

        # 2. Jagrataadi:
        # Jupiter Exalted => Jagrata (Awake)
        jag = compute_jagrataadi_avastha("Jupiter", "Exalted")
        self.assertEqual(jag["avastha_name"], "Jagrata (Awake / Alert)")
        self.assertEqual(jag["potency_fraction"], 1.0)

        # 3. Deeptaadi:
        # Sun in Aries (exaltation) => Deepta
        deep = compute_deeptaadi_avastha("Sun", 0)
        self.assertIn("Deepta", deep["avastha"])

if __name__ == "__main__":
    unittest.main()
