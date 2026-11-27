"""
tests/test_advanced_calculations.py
===================================
Comprehensive Unit Test Suite for Advanced Astrological Calculations:
- Mrityu Bhagas & Orbs
- Pushkara Bhagas & Pushkaramshas
- 22nd Drekkana (5 Variations) & 64th Navamsha
- Aspects (Graha Drishti Virupas & Percentages, Rasi Drishti, Sambandha)
- Friendships (Naisargika, Tatkalika, Panchadha Maitri)
- Mundane Engine (Mesha Sankranti, Chaitra Pratipat, Solar Months, Stations, Conjunctions)
"""

import unittest
import math
from core_logic import (
    evaluate_mrityu_bhaga,
    get_mrityu_bhaga_degree,
    evaluate_pushkara_bhaga,
    get_pushkara_bhaga_degree,
    is_in_pushkaramsha,
    compute_drekkana,
    compute_22nd_drekkana,
    compute_64th_navamsha,
    compute_all_malicious_divisions,
    get_natural_relationship,
    compute_tatkalika_relationship,
    compute_panchadha_maitri,
    compute_all_planetary_friendships,
    compute_parasara_drik_virupas,
    compute_aspect_details,
    compute_rasi_drishti,
    evaluate_planetary_sambandha,
    compute_solar_new_year,
    compute_lunar_new_year,
    compute_solar_month_ingress,
    compute_fortnight_ingress,
    find_planetary_aspect_event,
    find_planetary_station_event,
    compute_year_lords
)

class TestAdvancedAstrologyCalculations(unittest.TestCase):

    def test_mrityu_bhaga(self):
        # Sun in Aries (sign 0): fatal degree is 20°
        deg = get_mrityu_bhaga_degree("Sun", 0)
        self.assertEqual(deg, 20.0)

        # Sun at 20.4° in Aries should be in orb (distance 0.4°)
        eval_res = evaluate_mrityu_bhaga("Sun", 20.4, orb_deg=1.0)
        self.assertTrue(eval_res["is_in_orb"])
        self.assertAlmostEqual(eval_res["distance_from_center"], 0.4, places=4)
        self.assertEqual(eval_res["sign_name"], "Aries")

        # Moon in Cancer (sign 3): Parasara = 22°, Saravali = 25°
        self.assertEqual(get_mrityu_bhaga_degree("Moon", 3, scheme="parasara"), 22.0)
        self.assertEqual(get_mrityu_bhaga_degree("Moon", 3, scheme="saravali"), 25.0)

        # Lagna in Scorpio (sign 7): fatal degree is 23°
        self.assertEqual(get_mrityu_bhaga_degree("Lagna", 7), 23.0)

    def test_pushkara_bhagas_and_navamshas(self):
        # Pushkara Bhaga Scheme 1 (Vidyamadhaviyam): Aries = 21°, Cancer = 8°
        self.assertEqual(get_pushkara_bhaga_degree(0, scheme="vidyamadhaviyam"), 21.0)
        self.assertEqual(get_pushkara_bhaga_degree(3, scheme="vidyamadhaviyam"), 8.0)

        # Scheme 2 (Jataka Parijata): Gemini = 24°, Cancer = 7°
        self.assertEqual(get_pushkara_bhaga_degree(2, scheme="jataka_parijata"), 24.0)
        self.assertEqual(get_pushkara_bhaga_degree(3, scheme="jataka_parijata"), 7.0)

        # Pushkaramsha in Fire sign (Leo = 120° + 21° = 141°):
        # 21° is 7th navamsa (Libra, index 6) -> Pushkaramsha!
        is_pushk, nav_idx, nav_name = is_in_pushkaramsha(141.0)
        self.assertTrue(is_pushk)
        self.assertEqual(nav_name, "Libra")

        # Earth sign (Taurus = 30° + 8° = 38°): 3rd navamsa is Pisces -> Pushkaramsha!
        is_pushk, nav_idx, nav_name = is_in_pushkaramsha(38.0)
        self.assertTrue(is_pushk)
        self.assertEqual(nav_name, "Pisces")

        # Full evaluation
        eval_pushk = evaluate_pushkara_bhaga(21.2)  # Aries 21.2°
        self.assertTrue(eval_pushk["is_in_pushkara_bhaga"])
        self.assertTrue(eval_pushk["is_in_pushkaramsha"])

    def test_drekkana_5_variations(self):
        # Test degree in Aries 15° (sign 0, decanate 1)
        lon = 15.0
        # 1. Parasara: decanate 1 -> 5th sign = Leo (index 4), lord = Sun
        p_sign, dec_num, lord = compute_drekkana(lon, method="parasara")
        self.assertEqual(p_sign, 4)
        self.assertEqual(lord, "Sun")

        # 2. Parivritti: 0*3 + 1 = 1 (Taurus), lord = Venus
        pv_sign, _, lord_pv = compute_drekkana(lon, method="parivritti")
        self.assertEqual(pv_sign, 1)
        self.assertEqual(lord_pv, "Venus")

        # 3. Somanatha: odd sign direct -> 4 (Leo)
        som_sign, _, _ = compute_drekkana(lon, method="somanatha")
        self.assertEqual(som_sign, 4)

        # 4. Jagannatha: movable sign starts from self -> (0 + 4) % 12 = 4 (Leo)
        jag_sign, _, _ = compute_drekkana(lon, method="jagannatha")
        self.assertEqual(jag_sign, 4)

        # 5. Uma-Shambhu: Parasara sign 4 mapped through table -> map[4] = 4 (Leo)
        uma_sign, _, _ = compute_drekkana(lon, method="uma_shambhu")
        self.assertEqual(uma_sign, 4)

    def test_22nd_drekkana_and_64th_navamsha(self):
        lagna_lon = 10.0   # Aries 10°
        moon_lon = 45.0    # Taurus 15°

        res = compute_all_malicious_divisions(lagna_lon, moon_lon)
        # 22nd drekkana target for Lagna: 10 + 210 = 220° (Scorpio 10°)
        self.assertIn("parasara", res["lagna_22nd_drekkanas"])
        self.assertEqual(res["lagna_22nd_drekkanas"]["parasara"]["drekkana_number"], 22)
        self.assertAlmostEqual(res["lagna_22nd_drekkanas"]["parasara"]["target_longitude"], 220.0)

        # 64th navamsha target for Moon: 45 + 210 = 255° (Sagittarius 15°)
        self.assertAlmostEqual(res["moon_64th_navamsha"]["target_longitude"], 255.0)
        self.assertEqual(res["moon_64th_navamsha"]["navamsha_number"], 64)
        self.assertIsNotNone(res["moon_64th_navamsha"]["lord"])

    def test_aspects_and_friendships(self):
        # 1. Natural Friendships: Sun to Moon = Friend, Sun to Saturn = Enemy
        self.assertEqual(get_natural_relationship("Sun", "Moon"), "Friend")
        self.assertEqual(get_natural_relationship("Sun", "Saturn"), "Enemy")
        self.assertEqual(get_natural_relationship("Jupiter", "Mars"), "Friend")

        # 2. Temporary Friendship: Sun in Aries (sign 0), Moon in Gemini (sign 2)
        # Gemini is 3rd house from Aries -> Temporary Friend!
        self.assertEqual(compute_tatkalika_relationship(0, 2), "Temporary Friend")
        # Saturn in Libra (sign 6) -> 7th house -> Temporary Enemy!
        self.assertEqual(compute_tatkalika_relationship(0, 6), "Temporary Enemy")

        # 3. Panchadha Maitri:
        # Sun & Moon: Natural Friend + Temporary Friend = Great Friend (Ati-Mitra)
        pancha = compute_panchadha_maitri("Sun", "Moon", 0, 2)
        self.assertEqual(pancha["compound_score"], 2)
        self.assertEqual(pancha["compound_name_en"], "Great Friend")

        # Sun & Saturn: Natural Enemy + Temporary Enemy = Great Enemy (Ati-Satru)
        pancha_sat = compute_panchadha_maitri("Sun", "Saturn", 0, 6)
        self.assertEqual(pancha_sat["compound_score"], -2)
        self.assertEqual(pancha_sat["compound_name_en"], "Great Enemy")

        # 4. Aspect Virupas:
        # Mars special aspect on 4th house (90°): full aspect (60 virupas)
        virupas_mars_4th = compute_parasara_drik_virupas(90.0, planet="Mars")
        self.assertAlmostEqual(virupas_mars_4th, 60.0)

        # Jupiter special aspect on 5th house (120°): full aspect (60 virupas)
        virupas_jup_5th = compute_parasara_drik_virupas(120.0, planet="Jupiter")
        self.assertAlmostEqual(virupas_jup_5th, 60.0)

        # Saturn special aspect on 3rd house (60°): full aspect (60 virupas)
        virupas_sat_3rd = compute_parasara_drik_virupas(60.0, planet="Saturn")
        self.assertAlmostEqual(virupas_sat_3rd, 60.0)

        # 5. Jaimini Rasi Drishti:
        # Aries (Movable 0) aspects Fixed signs Leo (4), Scorpio (7), Aquarius (10), NOT Taurus (1)
        aspected_by_aries = compute_rasi_drishti(0)
        self.assertEqual(aspected_by_aries, [4, 7, 10])

    def test_mundane_engine(self):
        # Simulated linear ephemeris motion functions for testing root finders
        # Sun moves 1.0 deg/day starting from 350.0° at JD 2450000.0
        def sun_lon(jd: float) -> float:
            return (350.0 + (jd - 2450000.0) * 1.0) % 360.0

        # Moon moves 13.0 deg/day starting from 338.0° at JD 2450000.0
        def moon_lon(jd: float) -> float:
            return (338.0 + (jd - 2450000.0) * 13.0) % 360.0

        # 1. Solar New Year: Sun reaches 0° after 10 days
        sny = compute_solar_new_year(sun_lon, approx_jd=2450000.0)
        self.assertAlmostEqual(sny["exact_jd"], 2450010.0, places=3)

        # 2. Solar Month Ingress into Taurus (30°): reaches 30° after 40 days
        sankranti = compute_solar_month_ingress(sun_lon, sign_index=1, approx_jd=2450030.0)
        self.assertAlmostEqual(sankranti["exact_jd"], 2450040.0, places=3)

        # 3. Lunar New Year / Chaitra Pratipat: Moon catches Sun (diff = 0°)
        # diff starts at (338 - 350) % 360 = 348° (-12°). Speed diff = 12°/day => 1.0 day!
        lny = compute_lunar_new_year(sun_lon, moon_lon, approx_jd=2450000.0)
        self.assertAlmostEqual(lny["exact_jd"], 2450001.0, places=3)

        # 4. Planetary Stations (Zero velocity):
        # Planet speed model: v(t) = 1.0 - (jd - 2450000) * 0.1 => v = 0 at jd = 2450010
        def test_speed(jd: float) -> float:
            return 1.0 - (jd - 2450000.0) * 0.1

        station = find_planetary_station_event("Mars", test_speed, start_jd=2450000.0)
        self.assertAlmostEqual(station["exact_jd"], 2450010.0, places=3)
        self.assertEqual(station["direction_transition"], "Direct -> Retrograde")

        # Rahu mean node rejection
        rahu_station = find_planetary_station_event("Rahu", test_speed, start_jd=2450000.0, is_true_node=False)
        self.assertIn("error", rahu_station)

        # 5. Year Lords (King & Minister)
        # Chaitra Pratipat on Monday (1 = Moon), Mesha Sankranti on Thursday (4 = Jupiter)
        lords = compute_year_lords(chaitra_pratipat_weekday=1, mesha_sankranti_weekday=4)
        self.assertEqual(lords["King (Raja)"], "Moon")
        self.assertEqual(lords["Minister (Mantri)"], "Jupiter")

if __name__ == "__main__":
    unittest.main()
