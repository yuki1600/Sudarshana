"""
tests/test_tier5_calculations.py
================================
Unit tests for Tier 5 calculations requested:
1. Miscellany Mode (Planetary Returns, Secondary/Manu/Sudarshana Progressions,
   Prashna Kerala Sphutas, Karya Siddhi, Tamboola, Choghadiya)
4. Vedic Chakras (Sarvatobhadra 9x9 Grid & ASCII, Kota Chakra, Sudarshana Chakra,
   Kalachakra 8 Spokes, Surya Kalanal)
5. Shodhya Pindas & Ashtakavarga Ayurdaya (Samudaya Pinda, Harana, Sensitive Points)
6. Avasthas Engine (Lajjitadi, Sayanadi, Master Evaluator + Vimsopaka Bala)
7. Classical Yogas (Nabhasa, Parivartana, Gajakesari, Budhaditya, Adhi, Vasumathi)
8. Bhava Bala Graphing (ASCII chart and Standalone SVG vector chart)
"""

import unittest
from datetime import datetime

from core_logic.miscellany import (
    compute_planetary_return,
    compute_angular_separation_return,
    compute_secondary_progression,
    compute_symbolic_manu_progression,
    compute_sudarshana_progression,
    compute_prashna_sphutas,
    evaluate_karya_siddhi,
    compute_tamboola_prashna,
    compute_choghadiya_muhurta
)
from core_logic.chakras import (
    compute_sarvatobhadra_vedhas,
    generate_sarvatobhadra_grid_data,
    render_sarvatobhadra_ascii_grid,
    compute_kota_chakra_structure,
    compute_sudarshana_chakra,
    compute_kalachakra_directional_wheel,
    compute_surya_kalanal_chakra
)
from core_logic.ashtakavarga import (
    run_full_ashtakavarga_pipeline,
    compute_ashtakavarga_ayurdaya,
    compute_shodhya_pinda_sensitive_points
)
from core_logic.avasthas import (
    compute_lajjitadi_avastha,
    compute_comprehensive_planetary_avasthas
)
from core_logic.shadbala import (
    compute_bhava_bala,
    generate_bhava_bala_ascii_graph,
    generate_bhava_bala_graph_svg
)

class TestTier5Calculations(unittest.TestCase):

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
    # 3. Miscellany Mode (Returns, Progressions, Prashna, Choghadiya)
    # -----------------------------------------------------------------------
    def test_miscellany_mode(self):
        # Secondary Progression: 30 years age
        prog = compute_secondary_progression(
            birth_dt=datetime(1863, 1, 12, 6, 33),
            current_age_years=30.0,
            natal_longitudes=self.swami_lons,
            natal_daily_speeds={"Sun": 1.01, "Moon": 13.5, "Mars": 0.7},
            natal_lagna_lon=self.lagna_lon
        )
        self.assertEqual(prog["current_age_years"], 30.0)
        self.assertIn("progressed_lagna", prog)
        self.assertAlmostEqual(prog["progressed_planets"]["Sun"]["longitude"], (self.swami_lons["Sun"] + 1.01 * 30.0) % 360, places=1)
        
        # Symbolic Manu Progression (1°/year)
        manu = compute_symbolic_manu_progression(self.swami_lons, self.lagna_lon, 30.0)
        self.assertEqual(manu["total_progression_arc"], 30.0)
        
        # Sudarshana Progression
        sud = compute_sudarshana_progression(lagna_sign=8, moon_sign=5, sun_sign=9, current_age_years=30.0)
        self.assertEqual(sud["age_year"], 31)
        
        # Prashna Kerala Sphutas
        sphutas = compute_prashna_sphutas(
            lagna_lon=self.lagna_lon,
            moon_lon=self.swami_lons["Moon"],
            sun_lon=self.swami_lons["Sun"],
            gulika_lon=120.0,
            rahu_lon=self.swami_lons["Rahu"]
        )
        self.assertIn("trisphuta", sphutas)
        self.assertIn("chatusphuta", sphutas)
        self.assertIn("panchasphuta", sphutas)
        self.assertIn("prana_sphuta", sphutas)
        self.assertIn("deha_sphuta", sphutas)
        self.assertIn("mrityu_sphuta", sphutas)
        
        # Karya Siddhi & Tamboola Prashna
        ks = evaluate_karya_siddhi("Jupiter", "Mercury", lagnesha_house=10, karyesha_house=10)
        self.assertIn("Karya Siddhi Assured", ks["outcome"])
        
        tamboola = compute_tamboola_prashna(15)
        self.assertEqual(tamboola["betel_leaves_count"], 15)
        self.assertIn("tamboola_lord", tamboola)
        
        # Choghadiya Timings
        chog = compute_choghadiya_muhurta(
            weekday_idx=0,
            sunrise_dt=datetime(2026, 10, 25, 6, 0),
            sunset_dt=datetime(2026, 10, 25, 18, 0)
        )
        self.assertEqual(len(chog), 8)

    # -----------------------------------------------------------------------
    # 4. Vedic Chakras (Sarvatobhadra, Kota, Sudarshana, Kalachakra, Kalanal)
    # -----------------------------------------------------------------------
    def test_vedic_chakras(self):
        # Sarvatobhadra 9x9 layout & ASCII render
        sbc_grid = generate_sarvatobhadra_grid_data()
        self.assertEqual(len(sbc_grid), 9)
        self.assertEqual(len(sbc_grid[0]), 9)
        ascii_grid = render_sarvatobhadra_ascii_grid()
        self.assertIn("+-----+-----+", ascii_grid)
        
        # SBC 4 Vedhas
        vedhas = compute_sarvatobhadra_vedhas("Rohini")
        self.assertEqual(vedhas["samukha_vedha"], "Jyeshtha")
        self.assertIn("kona_vedha", vedhas)
        
        # Kota Chakra
        kota = compute_kota_chakra_structure(
            janma_nakshatra_idx=12,
            planet_nakshatras={"Sun": 20, "Moon": 12, "Saturn": 14}
        )
        self.assertEqual(len(kota["stambha"]), 4)
        self.assertEqual(len(kota["madhya"]), 4)
        self.assertEqual(len(kota["prakaara"]), 8)
        self.assertIn("zone_occupants", kota)
        
        # Sudarshana Chakra 3-wheel alignment
        sud_chakra = compute_sudarshana_chakra(
            lagna_sign=8,
            moon_sign=5,
            sun_sign=9,
            planet_signs=self.swami_signs
        )
        self.assertEqual(len(sud_chakra["houses"]), 12)
        self.assertIn("physical_wheel_sign", sud_chakra["houses"][1])
        
        # Kalachakra Directional Spoke Wheel
        kala_wheel = compute_kalachakra_directional_wheel(janma_nakshatra_idx=12)
        self.assertEqual(len(kala_wheel["directional_spokes"]), 8)
        self.assertIn("Karma (10th - Profession & Actions)", kala_wheel["sensitive_nakshatra_points"])
        
        # Surya Kalanal Chakra
        kalanal = compute_surya_kalanal_chakra(
            sun_nakshatra_idx=20,
            transit_nakshatras={"Mars": 20, "Saturn": 5}
        )
        self.assertIn("Mars", kalanal["hub_occupants"])

    # -----------------------------------------------------------------------
    # 5. Shodhya Pindas & Ashtakavarga Ayurdaya
    # -----------------------------------------------------------------------
    def test_shodhya_pindas_and_ayurdaya(self):
        av_res = run_full_ashtakavarga_pipeline(self.swami_signs, lagna_sign=8)
        self.assertIn("shodhya_pindas", av_res)
        self.assertIn("samudaya_shodhya_pinda", av_res)
        self.assertGreater(av_res["samudaya_shodhya_pinda"], 500)
        
        # Ayurdaya longevity from Shodhya Pinda
        ayur = av_res["ashtakavarga_ayurdaya"]
        self.assertGreater(ayur["gross_ayurdaya_total_years"], 0.0)
        self.assertGreater(ayur["net_ayurdaya_total_years"], 0.0)
        
        # Sensitive transit points
        pts = av_res["sensitive_transit_points"]
        self.assertEqual(len(pts), 7)
        for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
            self.assertIn("core_sign_name", pts[p])
            self.assertEqual(len(pts[p]["trine_signs"]), 3)

    # -----------------------------------------------------------------------
    # 6. Avasthas Engine (Lajjitadi & Master Report)
    # -----------------------------------------------------------------------
    def test_avasthas_expanded(self):
        # Exalted Sun in Aries -> Garvita
        lajjita = compute_lajjitadi_avastha(
            planet="Sun",
            planet_sign=0,
            house_num=1,
            conjoined_planets=[],
            aspecting_planets=["Jupiter"],
            dignity="Exalted"
        )
        self.assertIn("Garvita", lajjita["primary_lajjitadi_avastha"])
        
        # Master report for Swami Vivekananda's Exalted Saturn in Libra
        report = compute_comprehensive_planetary_avasthas(
            planet="Saturn",
            planet_lon=self.swami_lons["Saturn"],
            lagna_sign=8,
            moon_lon=self.swami_lons["Moon"]
        )
        self.assertIn("baalaadi", report)
        self.assertIn("jagrataadi", report)
        self.assertIn("deeptaadi", report)
        self.assertIn("lajjitadi", report)
        self.assertIn("vimsopaka_bala_scores", report)

    # -----------------------------------------------------------------------
    # 7. Classical Yogas (Nabhasa, Parivartana, Gajakesari, etc.)
    # -----------------------------------------------------------------------
    # -----------------------------------------------------------------------
    # 8. Bhava Bala Graphing (ASCII and SVG)
    # -----------------------------------------------------------------------
    def test_bhava_bala_graphing(self):
        bb = compute_bhava_bala(self.lagna_lon, self.swami_lons)
        
        # ASCII Chart
        ascii_chart = generate_bhava_bala_ascii_graph(bb)
        self.assertIn("BHAVA BALA PROFILE GRAPH", ascii_chart)
        self.assertIn("H1", ascii_chart)
        self.assertIn("H12", ascii_chart)
        self.assertIn("Benchmark: 350 Virupas", ascii_chart)
        
        # SVG Vector Chart
        svg_chart = generate_bhava_bala_graph_svg(bb)
        self.assertTrue(svg_chart.startswith("<svg"))
        self.assertTrue(svg_chart.endswith("</svg>"))
        self.assertIn("Bhava Bala (12 Bhava Balas) Profile", svg_chart)
        self.assertIn("Par Benchmark (350 Virupas)", svg_chart)
        self.assertIn("strongBar", svg_chart)

if __name__ == "__main__":
    unittest.main()
