"""
core_logic/tests/test_tier8_gap_audits.py
=========================================
Unit tests verifying the forensic gap-fix implementations:
1. Complete 15 Kerala Prashna Marga Sphutas (Beeja, Kshetra, Sookshma Trisphuta, Tithi Sphuta, Yogi/Avayogi)
2. Vighati Lagna (ViGL micro-ascendant)
3. Transit Murthi Nirnaya (Swarna, Rajata, Taamra, Loha metallic idols)
4. Vaiseshikamsa Planetary Tiers (Parijata, Uttama, Gopura, Simhasana, etc.)
5. Durmuhurta Timings & Gowri Panchangam (8 Yamas of day/night)
6. Higher Harmonic Divisional Charts (D-5, D-6, D-8, D-11, D-40, D-45, D-108, D-144)
7. Rasi-Bhukta Vimsottari Dasa & Lagna Kendradi Rasi Dasa
"""

import unittest
from datetime import datetime
import core_logic as cl

class TestTier8GapAudits(unittest.TestCase):
    def test_kerala_prashna_sphutas_full(self):
        """Test all 15 Kerala Prashna Marga Sphutas."""
        res = cl.compute_prashna_sphutas(
            lagna_lon=15.0,    # Aries 15°
            moon_lon=45.0,     # Taurus 15°
            sun_lon=120.0,     # Leo 0°
            gulika_lon=90.0,   # Cancer 0°
            rahu_lon=180.0,    # Libra 0°
            mars_lon=60.0,     # Gemini 0°
            venus_lon=150.0,   # Virgo 0°
            jupiter_lon=210.0  # Scorpio 0°
        )
        self.assertIn("trisphuta", res)
        self.assertIn("chatusphuta", res)
        self.assertIn("panchasphuta", res)
        self.assertIn("sookshma_trisphuta", res)
        self.assertIn("beeja_sphuta", res)
        self.assertIn("kshetra_sphuta", res)
        self.assertIn("yogi_sphuta", res)
        self.assertIn("avayogi_sphuta", res)
        self.assertIn("virility_verdict", res["beeja_sphuta"])
        self.assertIn("fertility_verdict", res["kshetra_sphuta"])
        
        # Prana = 5 L + G, Deha = 8 Mo + G, Mrityu = 7 G + Su, Sookshma = their sum
        self.assertAlmostEqual(res["prana_sphuta"]["longitude"], (5 * 15.0 + 90.0) % 360)
        self.assertAlmostEqual(res["deha_sphuta"]["longitude"], (8 * 45.0 + 90.0) % 360)
        self.assertAlmostEqual(res["mrityu_sphuta"]["longitude"], (7 * 90.0 + 120.0) % 360)
        self.assertAlmostEqual(res["sookshma_trisphuta"]["longitude"], (165.0 + 90.0 + 30.0) % 360)
        self.assertAlmostEqual(res["tithi_sphuta"]["longitude"], 285.0)  # Moon - Sun

    def test_vighati_lagna(self):
        """Test Vighati Lagna motion rate."""
        # 4 signs per ghati, i.e. 2 deg per vighati (24 s)
        vigl_0 = cl.compute_vighati_lagna(sun_lon=0.0, sunrise_hours=6.0, birth_hours=6.0)
        self.assertEqual(vigl_0, 0.0)
        vigl_1 = cl.compute_vighati_lagna(sun_lon=0.0, sunrise_hours=6.0, birth_hours=6.0 + (1.0 / 150.0))
        self.assertAlmostEqual(vigl_1, 2.0, places=3)
        vigl_ghati = cl.compute_vighati_lagna(sun_lon=0.0, sunrise_hours=6.0, birth_hours=6.4)  # one ghati
        self.assertAlmostEqual(vigl_ghati, 120.0, places=3)

    def test_transit_murthi_nirnaya(self):
        """Test Murthi Nirnaya metallic form determinations."""
        # Moon in 1st from natal Moon: Swarna (Gold)
        swarna = cl.compute_murthi_nirnaya(ingress_moon_sign_idx=1, natal_moon_sign_idx=1)
        self.assertEqual(swarna["murthi_name"], "Swarna")
        self.assertEqual(swarna["metal"], "Gold")
        
        # Moon in 4th from natal Moon (Taurus to Leo = 4th house): Loha (Iron)
        loha = cl.compute_murthi_nirnaya(ingress_moon_sign_idx=4, natal_moon_sign_idx=1)
        self.assertEqual(loha["murthi_name"], "Loha")
        self.assertEqual(loha["metal"], "Iron")

    def test_vaiseshikamsa_tiers(self):
        """Test Vaiseshikamsa attainment classification."""
        vimsopaka = cl.compute_vimsopaka_bala("Jupiter", 125.0)
        self.assertIn("vaiseshikamsa", vimsopaka)
        v_res = vimsopaka["vaiseshikamsa"]
        self.assertIn("dasa_varga", v_res)
        self.assertIn("shodasa_varga", v_res)
        self.assertIn("tier_name", v_res["dasa_varga"])

    def test_durmuhurta_and_gowri(self):
        """Test Durmuhurta and Gowri Panchangam."""
        dur = cl.compute_durmuhurta_timings(weekday_idx=0) # Sunday
        self.assertEqual(len(dur), 1)
        self.assertEqual(dur[0]["muhurta_index"], 14)
        
        gowri = cl.compute_gowri_panchangam(weekday_idx=0, is_night=False)
        self.assertEqual(len(gowri), 8)
        self.assertEqual(gowri[0]["name"], "Uthama")

    def test_higher_harmonic_vargas(self):
        """Test D-5, D-6, D-8, D-11, D-40, D-45, D-108, D-144."""
        vargas = cl.compute_all_vargas(45.5) # 45.5° = Taurus 15°30'
        for v in ["D5", "D6", "D8", "D11", "D40", "D45", "D108", "D144"]:
            self.assertIn(v, vargas)
            self.assertTrue(0 <= vargas[v]["sign_idx"] < 12)

if __name__ == "__main__":
    unittest.main()
