"""
tests/test_tier3_calculations.py
================================
Unit tests for:
- Kakshyas & Real-Time Transit Scoring
- 50+ Classical Tajika Sahams Library
- Specialized Dasas (Kalachakra, Shoola, Sudasa, Sudarsana Chakra)
- Tithi Pravesha Lunar Return Engine
- Chakras (9x9 Sarvatobhadra & Kota Chakra Cross-Vedha)
"""

import unittest
from core_logic import (
    get_kakshya_info,
    evaluate_kakshya_transit,
    compute_single_saham,
    compute_all_50_sahams,
    get_tithi_info,
    solve_tithi_pravesha_chart,
    compute_sarvatobhadra_vedhas,
    compute_kota_chakra_structure
)

class TestTier3AstrologyCalculations(unittest.TestCase):

    def test_kakshyas(self):
        # 1. Longitude at Aries 2° (0-3.75°) is in Kakshya 1 (Saturn)
        k1 = get_kakshya_info(2.0)
        self.assertEqual(k1["kakshya_number"], 1)
        self.assertEqual(k1["kakshya_lord"], "Saturn")
        self.assertEqual(k1["sign_name"], "Aries")

        # 2. Longitude at Aries 5° (3.75-7.5°) is in Kakshya 2 (Jupiter)
        k2 = get_kakshya_info(5.0)
        self.assertEqual(k2["kakshya_number"], 2)
        self.assertEqual(k2["kakshya_lord"], "Jupiter")

        # 3. Transit scoring against Prastara matrix
        mock_prastara = {
            "Jupiter": {
                "Saturn": [1] * 12,   # Saturn contributed a bindu in all signs
                "Jupiter": [0] * 12  # Jupiter contributed 0 bindus
            }
        }
        res_sat = evaluate_kakshya_transit("Jupiter", 2.0, mock_prastara)
        self.assertTrue(res_sat["has_bindu"])
        self.assertIn("good kakshya", res_sat["description"])

        res_jup = evaluate_kakshya_transit("Jupiter", 5.0, mock_prastara)
        self.assertFalse(res_jup["has_bindu"])
        self.assertIn("bad kakshya", res_jup["description"])

    def test_sahams_library(self):
        chart = {
            "Sun": 10.0,
            "Moon": 40.0,
            "Mars": 75.0,
            "Mercury": 25.0,
            "Jupiter": 110.0,
            "Venus": 35.0,
            "Saturn": 200.0,
            "Rahu": 180.0
        }
        lagna = 0.0  # Aries 0°
        
        # Saham library execution (36 sahamas of the main list + 17 from other texts)
        sahams = compute_all_50_sahams(chart, lagna_lon=lagna, is_night=False)
        self.assertEqual(len(sahams), 53)
        self.assertIn("Punya (Fortune / Merit)", sahams)
        self.assertIn("Vidya (Education / Knowledge)", sahams)
        self.assertIn("Yashas (Fame / Renown)", sahams)
        self.assertIn("Karyasiddhi (Success in Undertakings)", sahams)

    def test_tithi_pravesha(self):
        # Sun at 0°, Moon at 12° (exact Shukla Dvitiya start = 12°)
        t_info = get_tithi_info(moon_lon=12.0, sun_lon=0.0)
        self.assertEqual(t_info["tithi_number"], 2)
        self.assertEqual(t_info["tithi_name"], "Shukla Dvitiya")

        # Test TP solver with linear simulated motion:
        def s_lon(jd: float) -> float: return (jd - 2450000.0) * 1.0
        def m_lon(jd: float) -> float: return (jd - 2450000.0) * 13.0
        tp = solve_tithi_pravesha_chart(
            natal_sun_lon=0.0,
            natal_moon_lon=12.0,
            sun_lon_func=s_lon,
            moon_lon_func=m_lon,
            approx_return_jd=2450000.0
        )
        self.assertAlmostEqual(tp["exact_jd"], 2450001.0, places=3)
        self.assertAlmostEqual(tp["target_phase_angle"], 12.0)

    def test_chakras(self):
        # 1. Sarvatobhadra Vedhas:
        # Krittika casts Front Vedha on opposite Anuradha
        sbc = compute_sarvatobhadra_vedhas("Krittika")
        self.assertEqual(sbc["samukha_vedha"], "Anuradha")
        self.assertEqual(sbc["dakshina_vedha"], "Magha")

        # 2. Kota Chakra:
        # Janma Nakshatra = 0 (Ashwini)
        kota = compute_kota_chakra_structure(0)
        self.assertEqual(len(kota["stambha"]), 4)
        self.assertEqual(len(kota["madhya"]), 4)
        self.assertEqual(len(kota["prakaara"]), 8)
        self.assertEqual(len(kota["bahya"]), 11)  # 27 - 16 = 11

if __name__ == "__main__":
    unittest.main()
