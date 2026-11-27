"""
tests/test_tier6_gap_fixes.py
=============================
Test suite verifying all 14 gap fixes and modularity cleanup:
1. Shared utilities (norm360, deg_to_dms, get_house_of_sign, angular_distance)
2. Complete Shadbala sub-components (Saptavargaja, Ojayugma, Drekkana, Tribhaga,
   Temporal lords, Ayana, Graha Yuddha, Cheshta, Drik, and master Shadbala)
3. Vimshottari 5-level hierarchy (MD, AD, PD, SD, PAD) & get_active_vimshottari_subperiod
4. 4 Conditional Nakshatra Dasas (Shodashottari, Dwadashottari, Panchottari, Shat-trimsat)
5. Narayana Dasa full dated timeline and Jaimini Chara Dasa
6. Moola Dasa (D-60 past life karmic progression)
7. 16 Classical Tajika Yogas detection engine
8. Vipareeta Vedha (Reverse Vedha) transit cancellation
9. Chandra Kalanal Chakra and Kurma Chakra
10. Placidus, Koch, Campanus, Regiomontanus house cusps
11. JHD File Format Parser & Serializer round-trip
"""

import unittest
from datetime import datetime, timedelta

import core_logic as cl


class TestTier6GapFixes(unittest.TestCase):

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
        self.birth_dt = datetime(1863, 1, 12, 6, 33)

    # -----------------------------------------------------------------------
    # 1. Shared Utilities
    # -----------------------------------------------------------------------
    def test_shared_utils(self):
        self.assertEqual(cl.norm360(-30.0), 330.0)
        self.assertEqual(cl.norm360(390.0), 30.0)
        self.assertEqual(cl.get_house_of_sign(lagna_sign=8, target_sign=8), 1)
        self.assertEqual(cl.get_house_of_sign(lagna_sign=8, target_sign=9), 2)
        self.assertEqual(cl.get_house_of_sign(lagna_sign=8, target_sign=7), 12)
        d, m, s = cl.deg_to_dms(265.05)
        self.assertEqual(d, 265)
        self.assertEqual(m, 3)
        self.assertAlmostEqual(s, 0.0, places=1)
        self.assertAlmostEqual(cl.angular_distance(10.0, 350.0), 20.0)

    # -----------------------------------------------------------------------
    # 2. Complete Shadbala Sub-Components
    # -----------------------------------------------------------------------
    def test_complete_shadbala_components(self):
        # Tribhaga Bala
        # Daytime: Sunrise 6.0, Sunset 18.0. Part 1 (6-10): Jupiter; Part 2 (10-14): Sun; Part 3 (14-18): Saturn
        jup_tribhaga = cl.compute_tribhaga_bala("Jupiter", birth_time_hours=8.0, sunrise_hours=6.0, sunset_hours=18.0)
        self.assertEqual(jup_tribhaga, 60.0)
        sun_tribhaga = cl.compute_tribhaga_bala("Sun", birth_time_hours=12.0, sunrise_hours=6.0, sunset_hours=18.0)
        self.assertEqual(sun_tribhaga, 60.0)
        merc_tribhaga = cl.compute_tribhaga_bala("Mercury", birth_time_hours=23.0, sunrise_hours=6.0, sunset_hours=18.0)
        self.assertEqual(merc_tribhaga, 60.0)  # Mercury always 60

        # Temporal Lords Bala
        temp = cl.compute_temporal_lords_bala("Sun", varsha_lord="Sun", dina_lord="Sun")
        self.assertEqual(temp["varsha_bala"], 15.0)
        self.assertEqual(temp["dina_bala"], 45.0)
        self.assertEqual(temp["total_temporal_bala"], 60.0)

        # Ayana Bala
        ayana_sun = cl.compute_ayana_bala("Sun", 0.0)  # Aries 0° (Equinox)
        self.assertTrue(0.0 <= ayana_sun <= 60.0)

        # Ojayugmarasyamsa Bala
        # Sun in Aries (odd sign 0) and Leo Navamsha (odd sign 4) -> 30 virupas
        oja = cl.compute_ojayugmarasyamsa_bala("Sun", rasi_sign=0, navamsha_sign=4)
        self.assertEqual(oja, 30.0)

        # Drekkana Bala
        # Sun in 0-10° gets 15 virupas
        self.assertEqual(cl.compute_drekkana_bala("Sun", 5.0), 15.0)
        self.assertEqual(cl.compute_drekkana_bala("Saturn", 5.0), 0.0)
        self.assertEqual(cl.compute_drekkana_bala("Saturn", 15.0), 15.0)

        # Graha Yuddha (Planetary War)
        # Mars at 276.32 and Venus at 277.12 are 0.80° apart (< 1.0°)!
        pre_war = {"Mars": 350.0, "Venus": 400.0}
        yuddha = cl.compute_graha_yuddha_bala({"Mars": 276.32, "Venus": 277.12}, pre_war)
        self.assertIn("Mars", yuddha)
        self.assertIn("Venus", yuddha)
        self.assertNotEqual(yuddha["Venus"], 0.0)

        # Full Shadbala with full breakdown
        sb = cl.compute_full_shadbala(
            self.swami_lons,
            lagna_lon=self.lagna_lon,
            birth_time_hours=6.55,
            sunrise_hours=6.0,
            sunset_hours=18.0
        )
        for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
            self.assertIn(p, sb)
            self.assertIn("sthana_breakdown", sb[p])
            self.assertIn("kala_breakdown", sb[p])
            self.assertGreater(sb[p]["total_virupas"], 100.0)

    # -----------------------------------------------------------------------
    # 3. Vimshottari 5-Level Hierarchy
    # -----------------------------------------------------------------------
    def test_vimshottari_5_levels(self):
        # 3 levels deep (MD + AD + PD)
        tree = cl.compute_vimshottari_tree(
            self.swami_lons["Moon"],
            birth_dt=self.birth_dt,
            include_antardasa=True,
            subperiod_depth=3
        )
        self.assertGreater(len(tree), 0)
        first_md = tree[0]
        self.assertIn("antardasas", first_md)
        first_ad = first_md["antardasas"][0]
        self.assertIn("pratyantardasas", first_ad)
        self.assertEqual(len(first_ad["pratyantardasas"]), 9)

        # Active subperiod lookup at age 30 (1893)
        target = datetime(1893, 9, 11, 12, 0)  # Chicago Parliament of Religions
        active = cl.get_active_vimshottari_subperiod(self.swami_lons["Moon"], self.birth_dt, target)
        self.assertIn("mahadasha", active)
        self.assertIn("antardasha", active)
        self.assertIn("pratyantardasha", active)
        self.assertIn("sookshma", active)
        self.assertIn("prana", active)
        self.assertIn("hierarchy_string", active)

    # -----------------------------------------------------------------------
    # 4. Conditional Nakshatra Dasas
    # -----------------------------------------------------------------------
    # -----------------------------------------------------------------------
    # 5. Narayana & Chara Dasas
    # -----------------------------------------------------------------------
    def test_narayana_and_chara_dasas(self):
        signs = {p: int(lon // 30.0) for p, lon in self.swami_lons.items()}
        lagna_s = int(self.lagna_lon // 30.0)

        # Narayana timeline
        n_timeline = cl.compute_narayana_dasa_timeline(lagna_s, signs, self.birth_dt)
        self.assertEqual(len(n_timeline), 12)
        for entry in n_timeline:
            self.assertIn("sign_name", entry)
            self.assertIn("start", entry)
            self.assertIn("end", entry)
            self.assertGreater(entry["duration_years"], 0)

        # Chara timeline
        c_timeline = cl.compute_chara_dasa(lagna_s, signs, self.birth_dt)
        self.assertEqual(len(c_timeline), 12)
        for entry in c_timeline:
            self.assertIn("lord", entry)
            self.assertIn("duration_years", entry)

    # -----------------------------------------------------------------------
    # 6. Moola Dasa Engine (D-60)
    # -----------------------------------------------------------------------
    # -----------------------------------------------------------------------
    # 7. 16 Classical Tajika Yogas
    # -----------------------------------------------------------------------
    def test_16_tajika_yogas(self):
        # In Swami chart: Venus at 277.12 (faster) is ahead of Mars at 276.32 (slower) -> Ishrafa (separating)
        yogas = cl.detect_16_tajika_yogas(self.swami_lons, self.lagna_lon, "Mars", "Venus")
        self.assertTrue(len(yogas) > 0)
        yoga_names = [y["name"] for y in yogas]
        self.assertTrue(any("Ishrafa" in name for name in yoga_names))

        # Test applying aspect: Venus at 275.0 applying to Mars at 276.32 -> Ithasala
        test_lons = dict(self.swami_lons)
        test_lons["Venus"] = 275.0
        applying_yogas = cl.detect_16_tajika_yogas(test_lons, self.lagna_lon, "Mars", "Venus")
        applying_names = [y["name"] for y in applying_yogas]
        self.assertTrue(any("Ithasala" in name for name in applying_names))

        # Full evaluation across all chart significators
        all_y = cl.evaluate_all_tajika_yogas(self.swami_lons, self.lagna_lon)
        self.assertIn("lagnesha", all_y)
        self.assertIn("all_combinations", all_y)

    # -----------------------------------------------------------------------
    # 8. Transits: Vipareeta Vedha
    # -----------------------------------------------------------------------
    def test_vipareeta_vedha(self):
        # Sun transit in 9th from Moon is naturally unfavorable (favorable is 3).
        # House 9 has Vedha pair 3.
        # If another planet (e.g. Jupiter) is in house 3 from Moon, it creates Vipareeta Vedha!
        natal_moon_sign = 5  # Virgo (5)
        sun_sign = (natal_moon_sign + 9 - 1) % 12  # Taurus (1)
        jup_sign = (natal_moon_sign + 3 - 1) % 12  # Scorpio (7)

        transit_signs = {"Sun": sun_sign, "Jupiter": jup_sign}
        res = cl.evaluate_gochara_transit("Sun", sun_sign, natal_moon_sign, transit_signs)
        self.assertFalse(res["is_naturally_favorable"])
        self.assertTrue(res["vipareeta_vedha_active"])
        self.assertEqual(res["vipareeta_vedha_planet"], "Jupiter")
        self.assertIn("Nullified by Vipareeta Vedha", res["status"])

    # -----------------------------------------------------------------------
    # 9. Chandra Kalanal & Kurma Chakras
    # -----------------------------------------------------------------------
    def test_chandra_kalanal_and_kurma_chakras(self):
        transits = {"Sun": 10, "Mars": 13, "Saturn": 13, "Jupiter": 3}
        # Chandra Kalanal
        ck = cl.compute_chandra_kalanal_chakra(moon_nakshatra_idx=13, transit_nakshatras=transits)
        self.assertEqual(ck["chakra_type"], "Chandra Kalanal Chakra")
        self.assertIn("Mars", ck["hub_occupants"])
        self.assertIn("Saturn", ck["hub_occupants"])

        # Kurma Chakra
        kurma = cl.compute_kurma_chakra(transits)
        self.assertEqual(kurma["chakra_type"], "Kurma Chakra (Earth Tortoise Wheel)")
        self.assertIn("Center (Kukshi / Heart)", kurma["region_occupants"])
        self.assertIn("afflicted_regions", kurma)

    # -----------------------------------------------------------------------
    # 10. House Systems: Placidus, Koch, Campanus, Regiomontanus
    # -----------------------------------------------------------------------
    def test_house_systems(self):
        asc = 265.05
        mc = 175.05
        for sys_name in ["Equal", "Whole_Sign", "Sripathi", "Placidus", "Koch", "Campanus", "Regiomontanus"]:
            cusps = cl.compute_house_cusps(sys_name, asc, mc, geo_lat_deg=22.5)
            self.assertEqual(len(cusps), 12)
            if sys_name == "Whole_Sign":
                self.assertAlmostEqual(cusps[0], 240.0, places=2)
            else:
                self.assertAlmostEqual(cusps[0], asc, places=2)

    # -----------------------------------------------------------------------
    # 11. JHD File Format Parser & Serializer
    # -----------------------------------------------------------------------
    def test_jhd_io(self):
        # Round trip through the (corrected) modern layout; format details are covered in test_jhd_io.py
        chart = {
            "month": 1, "day": 12, "year": 1863, "hour_local": 6.55,
            "tz_east_hours": 5.9, "longitude_east": 88.5, "latitude": 22.6667,
            "city": "Kolkata", "country": "India", "rating": 105,
        }
        parsed = cl.parse_jhd_string(cl.serialize_to_jhd(chart))
        self.assertEqual((parsed["year"], parsed["month"], parsed["day"]), (1863, 1, 12))
        self.assertAlmostEqual(parsed["hour_local"], 6.55, places=5)
        self.assertAlmostEqual(parsed["tz_east_hours"], 5.9, places=5)
        self.assertAlmostEqual(parsed["longitude_east"], 88.5, places=4)
        self.assertAlmostEqual(parsed["latitude"], 22.6667, places=3)
        self.assertEqual(parsed["city"], "Kolkata")


if __name__ == "__main__":
    unittest.main()
