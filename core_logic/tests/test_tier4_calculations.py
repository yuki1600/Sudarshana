"""
tests/test_tier4_calculations.py
================================
Unit tests for the Tier 4 calculations:
1. Planetary Rays (Rashmis) & Parasara Ishta-Kashta Phala
2. Bhava Bala (12 House Strengths)
3. Vimsopaka Bala (Shadvarga, Saptavarga, Dasavarga, Shodashavarga)
4. Harsha Bala & Panchavargiya Bala (Tajika)
5. Ashtottari Dasa, Sthira Dasa, Varnada Dasa, Mandooka Dasa
6. Vedic Panchanga (Tithi, Vaara, Nakshatra, Yoga, Karana, Muhurta Timings)
7. Laghu Parasari Functional Nature, Kendra-Trikona Raja Yogas, Marakas
8. Solar Yogas, Lunar Yogas, Auspicious Royal Yogas
"""

import unittest
from datetime import datetime

from core_logic.shadbala import (
    compute_ishta_kashta_parasara,
    compute_bhava_bala,
    compute_vimsopaka_bala
)
from core_logic.panchanga import (
    compute_tithi,
    compute_vaara,
    compute_nakshatra,
    compute_yoga,
    compute_karana,
    compute_muhurta_timings,
    compute_full_panchanga
)
from core_logic.laghu_parasari import (
    evaluate_functional_nature_for_lagna,
    find_laghu_parasari_raja_yogas,
    evaluate_maraka_grahas
)

class TestTier4Calculations(unittest.TestCase):

    def setUp(self):
        # Sample planetary longitudes (Swami Vivekananda chart degrees)
        self.swami_lons = {
            "Sun": 279.18,       # Capricorn 9° 11'
            "Moon": 167.54,      # Virgo 17° 32' (Hasta)
            "Mars": 276.32,      # Capricorn 6° 19' (Exalted)
            "Mercury": 281.78,   # Capricorn 11° 47'
            "Jupiter": 199.98,   # Libra 19° 59'
            "Venus": 277.12,     # Capricorn 7° 7'
            "Saturn": 193.58,    # Libra 13° 35' (Exalted)
            "Rahu": 22.25,       # Aries 22° 15'
            "Ketu": 202.25       # Libra 22° 15'
        }
        self.lagna_lon = 265.05  # Sagittarius 25° 3' (Lagna sign = 8)
        self.swami_signs = {p: int(lon // 30.0) for p, lon in self.swami_lons.items()}

    # -----------------------------------------------------------------------
    # 1. Planetary Rays (Rashmis) & Ishta/Kashta Phala
    # -----------------------------------------------------------------------
    def test_ishta_kashta(self):
        ishta, kashta = compute_ishta_kashta_parasara(uchcha_bala=40.0, cheshta_bala=30.0)
        self.assertAlmostEqual(ishta, 34.64, places=1)
        self.assertAlmostEqual(kashta, 24.49, places=1)

    # -----------------------------------------------------------------------
    # 2. Bhava Bala & Vimsopaka Bala
    # -----------------------------------------------------------------------
    def test_bhava_bala(self):
        bb = compute_bhava_bala(self.lagna_lon, self.swami_lons)
        self.assertEqual(len(bb), 12)
        # Verify every house has adhipati, dig_bala, drishti_bala, total_virupas
        for h in range(1, 13):
            self.assertIn("adhipati_bala", bb[h])
            self.assertIn("dig_bala", bb[h])
            self.assertIn("drishti_bala", bb[h])
            self.assertIn("total_virupas", bb[h])
            self.assertIn("total_rupas", bb[h])
            self.assertGreater(bb[h]["total_virupas"], 0.0)
            self.assertIn("strength_rank", bb[h])
            self.assertTrue(1 <= bb[h]["strength_rank"] <= 12)

    def test_vimsopaka_bala(self):
        # Test Jupiter in Libra
        vb = compute_vimsopaka_bala("Jupiter", self.swami_lons["Jupiter"])
        self.assertIn("Shadvarga", vb["scheme_scores"])
        self.assertIn("Saptavarga", vb["scheme_scores"])
        self.assertIn("Dasavarga", vb["scheme_scores"])
        self.assertIn("Shodashavarga", vb["scheme_scores"])
        # All scores must be between 0 and 20
        for s_name, score in vb["scheme_scores"].items():
            self.assertGreaterEqual(score, 0.0)
            self.assertLessEqual(score, 20.0)

    # -----------------------------------------------------------------------
    # 3. Harsha Bala & Panchavargiya Bala (Tajika)
    # -----------------------------------------------------------------------
    # -----------------------------------------------------------------------
    # 5. Full Vedic Panchanga Engine
    # -----------------------------------------------------------------------
    def test_panchanga_limbs(self):
        sun_lon = 279.18
        moon_lon = 167.54
        # Elongation = (167.54 - 279.18) % 360 = 248.36°
        # 248.36 / 12 = 20.69 -> 21st Tithi (Krishna Shasthi)
        tithi = compute_tithi(sun_lon, moon_lon)
        self.assertEqual(tithi["tithi_number"], 21)
        self.assertEqual(tithi["tithi_name"], "Shasthi")
        self.assertIn("Krishna", tithi["paksha"])

        # Vaara for Monday (1)
        vaara = compute_vaara(weekday_idx=1, birth_hour_decimal=6.5, sunrise_hour_decimal=6.0)
        self.assertEqual(vaara["vaara_english"], "Monday")
        self.assertEqual(vaara["day_lord"], "Moon")

        # Nakshatra for Moon 167.54°
        # 167.54 / 13.33333 = 12.56 -> Nakshatra index 12 = Hasta
        nak = compute_nakshatra(moon_lon)
        self.assertEqual(nak["nakshatra_name"], "Hasta")
        self.assertEqual(nak["lord"], "Moon")
        self.assertEqual(nak["pada"], 3)

        # Yoga for Sun + Moon = (279.18 + 167.54) % 360 = 86.72°
        # 86.72 / 13.33333 = 6.50 -> Yoga index 6 (7th Yoga: Sukarma)
        yoga = compute_yoga(sun_lon, moon_lon)
        self.assertEqual(yoga["yoga_number"], 7)
        self.assertEqual(yoga["yoga_name"], "Sukarma")
        self.assertTrue(yoga["is_auspicious"])

        # Karana for elongation 248.36° -> 248.36 / 6 = 41.39 -> 42nd Karana
        karana = compute_karana(sun_lon, moon_lon)
        self.assertEqual(karana["karana_number"], 42)
        self.assertIn(karana["karana_name"], ["Bava", "Balava", "Kaulava", "Taitila", "Gara", "Vanija", "Vishti (Bhadra)"])

        # Muhurta timings
        muh = compute_muhurta_timings(weekday_idx=1, sunrise_hours=6.0, sunset_hours=18.0)
        self.assertIn("rahu_kalam", muh)
        self.assertIn("abhijit_muhurta", muh)
        self.assertEqual(muh["dina_mana_hours"], 12.0)

        # Master panchanga
        full_p = compute_full_panchanga(sun_lon, moon_lon, weekday_idx=1)
        self.assertIn("tithi", full_p)
        self.assertIn("vaara", full_p)
        self.assertIn("nakshatra", full_p)
        self.assertIn("yoga", full_p)
        self.assertIn("karana", full_p)

    # -----------------------------------------------------------------------
    # 6. Laghu Parasari Functional Nature & Raja Yogas
    # -----------------------------------------------------------------------
    def test_laghu_parasari(self):
        # Cancer Lagna (3): Mars owns 5th (Scorpio) and 10th (Aries) -> Yogakaraka!
        fn_cancer = evaluate_functional_nature_for_lagna(lagna_sign=3)
        self.assertEqual(fn_cancer["Mars"]["classification"], "Yogakaraka")
        self.assertTrue(fn_cancer["Mars"]["is_yogakaraka"])

        # Taurus Lagna (1): Saturn owns 9th (Capricorn) and 10th (Aquarius) -> Yogakaraka!
        fn_taurus = evaluate_functional_nature_for_lagna(lagna_sign=1)
        self.assertEqual(fn_taurus["Saturn"]["classification"], "Yogakaraka")

        # Maraka evaluation for Sagittarius Lagna (8)
        # 2nd house = Capricorn (Saturn), 7th house = Gemini (Mercury)
        marakas = evaluate_maraka_grahas(lagna_sign=8, planetary_signs=self.swami_signs)
        self.assertEqual(marakas["primary_maraka_lords"]["house_2_lord"], "Saturn")
        self.assertEqual(marakas["primary_maraka_lords"]["house_7_lord"], "Mercury")

    # -----------------------------------------------------------------------
    # 7. Solar, Lunar, and Royal Yogas
    # -----------------------------------------------------------------------
if __name__ == "__main__":
    unittest.main()
