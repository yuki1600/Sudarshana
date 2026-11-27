"""
tests/test_tier7_engines.py
===========================
Automated test suite verifying 33 classical calculation engines:

1. Horoscope Matching & Ashta Kuta Engine (36 Gunas, Ancillary Kutas, Kuja Dosha)
2. KP Astrology (Krishnamurti Paddhati: 249 Subs, Cuspal Sub-Lords, 4-tier Significators, Ruling Planets, Horary-249)
3. Varga Deities (D60 Shashtiamsa, D10 Digpalas, D9/D16/D20, D150 Nadi Amsas)
4. Classical Mathematical Ayurdaya (Pindayu, Amsayu, Nisargayu, Harana & Bharana)
5. Graha Arudhas (Planetary Arudha Padas for 9 planets + dual signs)
6. 4 Conditional Nakshatra Dasas (Chaturaseeti 84y, Dwi-saptati 72y, Shashti-hayani 60y, Sataabdika 100y)
7. Classical Rasi & Special Dasas (Drigdasa, Patyayini, Mudda, Naisargika, Tara, Niryana Shoola, Brahma)
8. Specialized Chakras (Tripataki 3-Flag Wheel, Shoola Trident Wheel, Unified Kota Chakra)
9. Dasa Chronometry (Savana 360d, Sidereal solar, Tropical, and alternative starting seeds)
"""

import unittest
from datetime import datetime

import core_logic as cl


class TestTier7Engines(unittest.TestCase):

    def setUp(self):
        # Sample planetary longitudes (Swami Vivekananda chart degrees)
        self.swami_lons = {
            "Sun": 279.18,       # Capricorn 9° 11' (House 2 from Sg)
            "Moon": 167.54,      # Virgo 17° 32' (Hasta, Nakshatra 12)
            "Mars": 276.32,      # Capricorn 6° 19' (Exalted)
            "Mercury": 281.78,   # Capricorn 11° 47'
            "Jupiter": 199.98,   # Libra 19° 59'
            "Venus": 277.12,     # Capricorn 7° 7'
            "Saturn": 193.58,    # Libra 13° 35' (Exalted)
            "Rahu": 22.25,       # Aries 22° 15'
            "Ketu": 202.25       # Libra 22° 15'
        }
        self.lagna_lon = 265.05  # Sagittarius 25° 3' (Sign 8)
        self.birth_dt = datetime(1863, 1, 12, 6, 33)

        # Placidus cusps for Kolkata
        self.cusps = [
            265.05, 296.2, 328.4, 0.5, 30.8, 59.2,
            85.05, 116.2, 148.4, 180.5, 210.8, 239.2
        ]

    # -----------------------------------------------------------------------
    # 1. Horoscope Matching & Compatibility (CHoroscopeMatchView)
    # -----------------------------------------------------------------------
    def test_horoscope_matching_and_kutas(self):
        # Bride: Moon at Rohini (Taurus 15° = 45.0°, Nakshatra 3, Rasi 1, Vashya=Quadruped, Yoni=Serpent, Nadi=Antya)
        # Groom: Moon at Hasta (Virgo 17.5° = 167.54°, Nakshatra 12, Rasi 5, Vashya=Human, Yoni=Buffalo, Nadi=Adi)
        bride = {
            "name": "Bride Test",
            "moon_longitude": 45.0,
            "lagna_longitude": 30.0,
            "planet_longitudes": {"Mars": 45.0, "Moon": 45.0, "Jupiter": 200.0}
        }
        groom = {
            "name": "Groom Test",
            "moon_longitude": 167.54,
            "lagna_longitude": 265.05,
            "planet_longitudes": {"Mars": 276.32, "Moon": 167.54, "Jupiter": 199.98}
        }

        match = cl.evaluate_horoscope_matching(bride, groom)
        self.assertIn("gunanka_score", match)
        self.assertIn("match_level", match)
        self.assertTrue(0.0 <= match["gunanka_score"] <= 36.0)
        self.assertIn(match["match_level"], ["Inauspicious", "Middling", "Very Good", "Excellent"])

        # Check individual Kutas
        bk = match["ashta_kuta_breakdown"]
        self.assertEqual(bk["varna"]["max_points"], 1.0)
        self.assertEqual(bk["vashya"]["max_points"], 2.0)
        self.assertEqual(bk["tara"]["max_points"], 3.0)
        self.assertEqual(bk["yoni"]["max_points"], 4.0)
        self.assertEqual(bk["graha_maitri"]["max_points"], 5.0)
        self.assertEqual(bk["gana"]["max_points"], 6.0)
        self.assertEqual(bk["bhakoota"]["max_points"], 7.0)
        self.assertEqual(bk["nadi"]["max_points"], 8.0)

        # Check Ancillary Kutas
        anc = match["ancillary_kootas"]
        self.assertIn("mahendra_kuta", anc)
        self.assertIn("stree_deergha", anc)
        self.assertIn("rajju_kuta", anc)
        self.assertIn("vedha_kuta", anc)

        # Kuja Dosha
        kuja = cl.evaluate_kuja_dosha(self.swami_lons, self.lagna_lon)
        self.assertIn("has_kuja_dosha", kuja)
        self.assertIn("is_cancelled", kuja)
        # Mars in Capricorn 6° is Exalted -> Should be Cancelled!
        self.assertTrue(kuja["is_cancelled"])
        # by bhava: the houses given win over the signs; Jupiter's 7th aspect on Mars cancels too
        lons = {"Mars": 95.0, "Moon": 5.0, "Venus": 200.0, "Jupiter": 275.0}     # Mars in Cancer, Jupiter in Capricorn
        k = cl.evaluate_kuja_dosha(lons, 10.0, {"Lagna": 3, "Moon": 3, "Venus": 10})
        self.assertFalse(k["has_kuja_dosha"])
        k = cl.evaluate_kuja_dosha(lons, 10.0)          # by sign: 4th from the lagna and the Moon
        self.assertEqual((k["has_kuja_dosha"], [(c["kind"], c["aspect"], c["pct"]) for c in k["cancel"]]), (True, [("drishti", 7, 100)]))
        k = cl.evaluate_kuja_dosha({**lons, "Jupiter": 335.0}, 10.0)     # Jupiter in Pisces: 5th from it, aspected
        self.assertTrue(k["is_cancelled"])
        k = cl.evaluate_kuja_dosha({**lons, "Jupiter": 35.0}, 10.0)      # Jupiter in Taurus: Mars 3rd from it
        self.assertFalse(k["is_cancelled"])
        # Jupiter's drishti and yuti only within the orb (Ma 8°, Ju 9°: the smaller), across a sign's edge too
        k = cl.evaluate_kuja_dosha({**lons, "Jupiter": 260.0}, 10.0)     # Jupiter in Sagittarius 20°: 7th by sign, 15° short of exact
        self.assertFalse(k["is_cancelled"])
        k = cl.evaluate_kuja_dosha({**lons, "Mars": 92.0, "Jupiter": 118.0}, 10.0)     # Mars Cancer 2°, Jupiter Cancer 28°: same sign, 26° apart
        self.assertFalse(k["is_cancelled"])
        k = cl.evaluate_kuja_dosha({**lons, "Mars": 118.0, "Jupiter": 122.0}, 10.0)    # Mars Cancer 28°, Jupiter Leo 2°: 4° apart
        self.assertEqual([c["kind"] for c in k["cancel"]], ["yuti"])
        k = cl.evaluate_kuja_dosha({**lons, "Mars": 5.0}, 300.0)     # Mars in Aries 5°: moolatrikona
        self.assertEqual(k["cancel"][0], {"kind": "dignity", "dig": "Moolatrikona", "text": "Mars moolatrikona"})

    # -----------------------------------------------------------------------
    # 2. KP Astrology Engine (CKPView)
    # -----------------------------------------------------------------------
    def test_kp_astrology(self):
        # 249 table size
        self.assertEqual(len(cl.KP_249_TABLE), 249)

        # Test planetary sub-lord resolution
        # Swami Moon at 167.54° (Virgo 17° 32' -> Hasta, Star lord = Moon)
        moon_kp = cl.get_kp_sub_lords(167.54)
        self.assertEqual(moon_kp["sign_name"], "Virgo")
        self.assertEqual(moon_kp["sign_lord"], "Mercury")
        self.assertEqual(moon_kp["nakshatra_name"], "Hasta")
        self.assertEqual(moon_kp["star_lord"], "Moon")
        self.assertTrue(len(moon_kp["sub_lord"]) > 0)
        self.assertTrue(1 <= moon_kp["sub_number_249"] <= 249)

        # Test cuspal sub-lords (12 cusps)
        cusp_kp = cl.compute_cuspal_sub_lords(self.cusps)
        self.assertEqual(len(cusp_kp), 12)
        for c in cusp_kp:
            self.assertIn("sub_lord", c)
            self.assertIn("star_lord", c)

        # Test 4-level house significators
        sigs = cl.compute_kp_significators(self.swami_lons, self.cusps)
        self.assertEqual(len(sigs["house_significators"]), 12)
        self.assertIn("Sun", sigs["planet_significations"])

        # Test Ruling Planets
        rp = cl.get_kp_ruling_planets(self.lagna_lon, self.swami_lons["Moon"], weekday_idx=1)
        self.assertIn("day_lord", rp)
        self.assertEqual(rp["day_lord"], "Moon")

        # Test Horary seed resolver
        horary_100 = cl.resolve_kp_horary_number(100)
        self.assertEqual(horary_100["horary_number"], 100)
        self.assertIn("star_lord", horary_100)
        self.assertIn("sub_lord", horary_100)

    # -----------------------------------------------------------------------
    # 4. Classical Mathematical Ayurdaya (Longevity Engine)
    # -----------------------------------------------------------------------
    def test_mathematical_ayurdaya(self):
        # Sun in deep exaltation (Aries 10.0°) gives 19.0 years, in deep debilitation (Libra 10.0°) 9.5
        self.assertAlmostEqual(cl.arc_years(1, 10.0), 19.0, places=6)
        self.assertAlmostEqual(cl.arc_years(1, 190.0), 9.5, places=6)

        # The rules themselves are in test_ayurdaya: here, that they run on this chart through the package's names
        lons = [self.lagna_lon] + [self.swami_lons[p] for p in ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu")]
        n = cl.Natal(lons, hora_lagna=261.6)
        self.assertGreater(cl.spans(n)["pinda"]["total"], 20.0)
        self.assertIn(cl.three_pairs(n)["base"], cl.ayurdaya.SPAN_YEARS)

    # -----------------------------------------------------------------------
    # 5. Graha Arudhas (Planetary Arudha Padas)
    # -----------------------------------------------------------------------
    def test_graha_arudhas(self):
        # Sun in Capricorn (9) owning Leo (4):
        # dist from 9 to 4 is 7 signs. 4 + 7 = 11 (Pisces).
        # raw is 11. 11 is not 9 or 9+6=3 -> Arudha is Pisces (11).
        sun_arudha = cl.compute_graha_arudha("Sun", planet_sign_idx=9, target_owned_sign_idx=4)
        self.assertEqual(sun_arudha, 11)

        # Full pipeline across all planets
        signs = {p: int(lon // 30.0) for p, lon in self.swami_lons.items()}
        all_ga = cl.compute_all_graha_arudhas(signs)
        self.assertIn("Sun", all_ga)
        self.assertIn("Mars", all_ga)
        self.assertEqual(len(all_ga["Mars"]["all_arudhas"]), 2)  # Mars owns 2 signs (Aries & Scorpio)

    # -----------------------------------------------------------------------
    # 6. The 4 Missing Conditional Nakshatra Dasas
    # -----------------------------------------------------------------------
    # -----------------------------------------------------------------------
    # 8. Specialized Chakras (Tripataki & Shoola)
    # -----------------------------------------------------------------------
    def test_specialized_chakras(self):
        transits = {"Sun": 10, "Mars": 13, "Saturn": 13, "Jupiter": 3, "Rahu": 20}

        # Tripataki Chakra (3 Flags)
        trip = cl.compute_tripataki_chakra(
            natal_moon_nak_idx=12,
            natal_lagna_nak_idx=19,
            natal_sun_nak_idx=20,
            transit_nakshatras=transits
        )
        self.assertEqual(trip["chakra_type"], "Tripataki Chakra (3-Flag Varshaphal Wheel)")
        self.assertIn("Moon Flag (Health & Mind)", trip["flags"])

        # Shoola Chakra (Trident Bodily Wheel)
        shoola = cl.compute_shoola_chakra(janma_nakshatra_idx=12, transit_nakshatras=transits)
        self.assertEqual(shoola["chakra_type"], "Shoola Chakra (Trident Bodily Affliction Wheel)")
        self.assertIn("Left Prong (Vama Shoola)", shoola["prongs"])

        # Unified Kota Chakra
        kota = cl.compute_kota_chakra_placement(transit_nakshatra_idx=12, janma_nakshatra_idx=12)
        self.assertEqual(kota["zone"], "Stambha")
        self.assertTrue(kota["is_critical"])

    # -----------------------------------------------------------------------
    # 9. Dasa Chronometry & Starting Seeds
    # -----------------------------------------------------------------------
    def test_dasa_chronometry(self):
        # Savana 360-day year
        tree_savana = cl.compute_vimshottari_tree(
            self.swami_lons["Moon"],
            birth_dt=self.birth_dt,
            year_type="SAVANA"
        )
        self.assertEqual(len(tree_savana), 9)

        # Kshema Tara seed (+3 nakshatras)
        bal_kshema = cl.compute_vimshottari_balance(self.swami_lons["Moon"], seed_type="KSHEMA")
        self.assertEqual(bal_kshema["seed_type"], "KSHEMA")
        self.assertNotEqual(bal_kshema["nakshatra_index"], int(self.swami_lons["Moon"] // (360.0 / 27.0)))


if __name__ == "__main__":
    unittest.main()
