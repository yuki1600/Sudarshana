"""Checks for the items closed by the second remediation pass (2026-10-26)."""
import glob
import os
import unittest
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from datetime import datetime, timedelta

from core_logic import dashas as D
from core_logic.aspects_friendships import compute_parasara_drik_virupas
from core_logic.mundane import solve_longitude_crossing
from core_logic.special_lagnas_upagrahas import compute_kalavela_time, kalavela_part

try:
    import swisseph  # noqa: F401
    from core_logic import ephemeris as E, jhd_io, workflows as W
    HAVE_SWE = True
except ImportError:  # pragma: no cover
    HAVE_SWE = False

SAMPLES = sorted(glob.glob(os.path.join(os.path.dirname(__file__), "..", "..", "data", "sample_charts", "*.jhd")))


class TestKalavelas(unittest.TestCase):
    def test_help_table_7(self):
        """The kalavela table: Thursday day Jup Ven Sat - Sun Moon Mars Merc; night Moon Mars Merc Jup Ven Sat - Sun."""
        day = {lord: kalavela_part(4, False, lord) for lord in ("Jupiter", "Venus", "Saturn", "Sun", "Moon", "Mars", "Mercury")}
        self.assertEqual(day, {"Jupiter": 1, "Venus": 2, "Saturn": 3, "Sun": 5, "Moon": 6, "Mars": 7, "Mercury": 8})
        night = {lord: kalavela_part(4, True, lord) for lord in ("Moon", "Jupiter", "Saturn", "Sun")}
        self.assertEqual(night, {"Moon": 1, "Jupiter": 4, "Saturn": 6, "Sun": 8})
        self.assertEqual(kalavela_part(0, True, "Jupiter"), 1)        # Sunday night starts with Jupiter

    def test_help_worked_example(self):
        """Thursday night 6 pm - 6 am: Yama Ghantaka rises at 11:15 pm (middle of the 4th part)."""
        self.assertAlmostEqual(compute_kalavela_time(6.0, 18.0, 4, True, "Yama_Ghantaka"), 23.25)
        # the defaults: Gulika at the beginning and Maandi at the middle of
        # Saturn's part (6th: 1:30-3:00 am)
        self.assertAlmostEqual(compute_kalavela_time(6.0, 18.0, 4, True, "Gulika"), 1.5)
        self.assertAlmostEqual(compute_kalavela_time(6.0, 18.0, 4, True, "Mandi"), 2.25)
        self.assertAlmostEqual(compute_kalavela_time(6.0, 18.0, 4, True, "Mandi", point="end"), 3.0)


class TestDrikVirupas(unittest.TestCase):
    def test_seventh_aspect_is_full(self):
        for p in ("Sun", "Moon", "Venus", "Mars", "Jupiter", "Saturn"):
            self.assertEqual(compute_parasara_drik_virupas(180.0, p), 60.0, p)
        self.assertEqual(compute_parasara_drik_virupas(150.0, "Sun"), 0.0)
        self.assertEqual(compute_parasara_drik_virupas(240.0, "Sun"), 30.0)
        self.assertEqual(compute_parasara_drik_virupas(300.0, "Sun"), 0.0)
        for p, d in (("Mars", 210.0), ("Jupiter", 240.0), ("Saturn", 270.0)):
            self.assertEqual(compute_parasara_drik_virupas(d, p), 60.0, p)
        self.assertEqual(compute_parasara_drik_virupas(180.0, "Sun", full_aspect=100.0), 100.0)


class TestCrossingSolver(unittest.TestCase):
    def test_retrograde_motion(self):
        f = lambda jd: (100.0 - 0.5 * jd) % 360.0      # noqa: E731
        self.assertAlmostEqual(solve_longitude_crossing(f, 95.0, 0.0), 10.0, places=3)
        self.assertIsNone(solve_longitude_crossing(f, 120.0, 0.0))   # never reached going backwards


class TestVimshottari(unittest.TestCase):
    birth = datetime(1990, 1, 1, 12, 0)

    def test_first_dasa_true_dates_and_balance(self):
        tree = D.compute_vimshottari_tree(100.0, self.birth)          # Pushya, half gone -> Saturn 9.5 y left
        md = tree[0]
        self.assertEqual(md["lord"], "Saturn")
        self.assertAlmostEqual(md["balance_years"], 9.5)
        self.assertLess(datetime.fromisoformat(md["start"]), self.birth)
        self.assertAlmostEqual(sum(a["duration_years"] for a in md["antardasas"]), 19.0)
        self.assertEqual(md["antardasas"][0]["start"], md["start"])

    def test_locator_agrees_with_tree(self):
        tree = D.compute_vimshottari_tree(217.3, self.birth, subperiod_depth=5)
        for days in (1, 400, 9000, 30000):
            target = self.birth + timedelta(days=days)
            active = D.get_active_vimshottari_subperiod(217.3, self.birth, target)
            path = D.locate_dasa_period(tree, target)
            self.assertEqual(active["hierarchy_string"], " - ".join(p["lord"] for p in path))

    def test_tribhagi(self):
        tree = D.compute_vimshottari_tree(0.0, self.birth, tribhagi=True)
        self.assertEqual(len(tree), 27)
        self.assertAlmostEqual(sum(m["duration_years"] for m in tree), 120.0)
        self.assertAlmostEqual(tree[1]["duration_years"], 20.0 / 3)

    def test_custom_year_mapper_and_shift(self):
        tree = D.compute_vimshottari_tree(0.0, self.birth, to_date=lambda y: self.birth + timedelta(days=360 * y))
        self.assertEqual(tree[0]["end"], (self.birth + timedelta(days=360 * 7)).isoformat())
        moved = D.shift_dasa_timeline(tree, timedelta(days=1))
        self.assertEqual(moved[0]["antardasas"][0]["start"],
                         (datetime.fromisoformat(tree[0]["antardasas"][0]["start"]) + timedelta(days=1)).isoformat())

    def test_locate_rasi_dasa(self):
        nd = D.compute_narayana_dasa_timeline(0, {"Mars": 4, "Venus": 1}, self.birth)
        path = D.locate_dasa_period(nd, self.birth + timedelta(days=1))
        self.assertEqual(path[0]["sign_index"], 0)

    def test_seed_comparison(self):
        r = D.compare_vimshottari_seeds({"Moon": 10.0, "Lagna": 100.0}, {"Sun": 95.0, "Mars": 280.0, "Venus": 40.0})
        self.assertEqual(r, {"Moon": ["Sun", "Mars"], "Lagna": ["Sun", "Mars"]})
        # 9-pada houses from the seed's pada: Venus at 40 is 30..60 deg ahead of Moon's pada start (10) -> house 2
        self.assertNotIn("Venus", D.compare_vimshottari_seeds({"Moon": 10.0}, {"Venus": 40.0}, pada_houses=True)["Moon"])


@unittest.skipUnless(HAVE_SWE, "pyswisseph not installed")
class TestEphemerisAdditions(unittest.TestCase):
    def birth(self, name="Swami Vivekananda.jhd"):
        return jhd_io.to_birth_data(jhd_io.parse_jhd_file(next(p for p in SAMPLES if p.endswith(name))))

    def test_flags_change_positions_slightly(self):
        jd = E.julian_day_ut(2000, 1, 1, 12.0)
        # apparent positions: with SEFLG_TRUEPOS (the default) aberration and deflection are not applied
        base = E.planet_positions(jd, E.EphemerisConfig(true_positions=False))["Venus"]["lon"]  # the Sun does not deflect its own light
        for flag in ("no_aberration", "no_gravitational_deflection"):
            other = E.planet_positions(jd, E.EphemerisConfig(true_positions=False, **{flag: True}))["Venus"]["lon"]
            self.assertTrue(0.0 < abs(other - base) < 0.01, flag)
        # sidereal positions are always mean-equinox (SEFLG_SIDEREAL), so NoNutation shows only in the tropical zodiac
        trop = dict(true_positions=False, ayanamsa="TROPICAL")
        base = E.planet_positions(jd, E.EphemerisConfig(**trop))["Venus"]["lon"]
        other = E.planet_positions(jd, E.EphemerisConfig(no_nutation=True, **trop))["Venus"]["lon"]
        self.assertTrue(0.0 < abs(other - base) < 0.01)

    def test_topocentric_matches_swe(self):
        b = self.birth()
        geo = E.planet_positions(b.jd_ut)["Moon"]["lon"]
        cfg = E.EphemerisConfig(topocentric=True)
        topo = E.planet_positions(b.jd_ut, cfg, b)["Moon"]["lon"]
        self.assertTrue(0.01 < abs(geo - topo) < 1.1)                 # lunar parallax is up to ~1 deg
        swisseph.set_topo(b.longitude_east, b.latitude, b.altitude_m)
        trop = swisseph.calc_ut(b.jd_ut, swisseph.MOON, E._ephe_flag(swisseph, b.jd_ut) | swisseph.FLG_TOPOCTR | swisseph.FLG_TRUEPOS | swisseph.FLG_NONUT)[0][0]
        self.assertAlmostEqual((trop - E.ayanamsa_value(b.jd_ut, cfg)) % 360, topo, places=6)

    def test_pressure_and_temperature_reach_sunrise(self):
        b = self.birth()
        apparent = E.EphemerisConfig(sunrise_definition=2)   # refraction only matters for the apparent horizon
        cold = E.sunrise_sunset(replace(b, pressure_hpa=1050.0, temperature_c=-20.0), apparent)["sunrise_hours"]
        self.assertNotAlmostEqual(cold, E.sunrise_sunset(b, apparent)["sunrise_hours"], places=5)

    def test_eclipse_search(self):
        sol = E.next_eclipse(E.julian_day_ut(2024, 1, 1, 0.0), "solar")
        self.assertEqual((sol["type"], E.jd_to_calendar(sol["max_jd"])[:3]), ("total", (2024, 4, 8)))
        lun = E.next_eclipse(E.julian_day_ut(2025, 1, 1, 0.0), "lunar")
        self.assertEqual((lun["type"], E.jd_to_calendar(lun["max_jd"])[:3]), ("total", (2025, 3, 14)))

    def test_zone_offsets(self):
        self.assertEqual(E.zone_offset_hours("Asia/Kolkata", 2000, 1, 1, 12.0), 5.5)
        self.assertEqual(E.zone_offset_hours("America/New_York", 2024, 7, 1, 12.0), -4.0)
        self.assertEqual(E.lmt_offset_hours(82.5), 5.5)

    def test_build_chart_special_points_and_kalavelas(self):
        b = self.birth()
        chart = E.build_chart(b)
        for key in ("Hora_Lagna", "Ghati_Lagna", "Bhava_Lagna", "Sree_Lagna", "Indu_Lagna_sign"):
            self.assertIn(key, chart["special_lagnas"])
        kal = E.kalavela_longitudes(b)
        g = kal["Gulika"]
        self.assertAlmostEqual(g["longitude"], E.lagna_at(g["jd_ut"], b), places=9)
        self.assertEqual(chart["upagrahas"]["Gulika"], g["longitude"])
        self.assertLess(g["rising_hour"], kal["Mandi"]["rising_hour"])      # beginning vs middle of the part
        lon, seed_type = E.vimsottari_seed_longitude(chart, "TRISPHUTA")
        self.assertAlmostEqual(lon, (chart["lagna_lon"] + chart["planet_longitudes"]["Moon"] + g["longitude"]) % 360)

    def test_solar_dasa_year(self):
        b = self.birth()
        to_date = E.dasa_year_mapper(b, kind="SOLAR")
        one = to_date(1.0)
        jd = E.julian_day_ut(one.year, one.month, one.day,
                             one.hour + one.minute / 60 + one.second / 3600 - b.tz_east_hours)
        natal = E.planet_positions(b.jd_ut)["Sun"]["lon"]
        self.assertAlmostEqual(E.planet_positions(jd)["Sun"]["lon"], natal, places=4)
        tree = D.compute_vimshottari_tree(E.build_chart(b)["planet_longitudes"]["Moon"],
                                          datetime(b.year, b.month, b.day) + timedelta(hours=b.hour_local), to_date=to_date)
        self.assertEqual(len(tree), 9)

    def test_thread_safety(self):
        jd = E.julian_day_ut(1990, 5, 17, 6.0)
        cfgs = [E.EphemerisConfig(ayanamsa=k) for k in ("TRUE_LAHIRI", "RAMAN", "KP", "FAGAN")] * 10
        serial = [E.planet_positions(jd, c)["Moon"]["lon"] for c in cfgs]
        with ThreadPoolExecutor(8) as pool:
            parallel = list(pool.map(lambda c: E.planet_positions(jd, c)["Moon"]["lon"], cfgs))
        self.assertEqual(serial, parallel)


@unittest.skipUnless(HAVE_SWE, "pyswisseph not installed")
class TestWorkflows(unittest.TestCase):
    def birth(self):
        return jhd_io.to_birth_data(jhd_io.parse_jhd_file(next(p for p in SAMPLES if p.endswith("Swami Vivekananda.jhd"))))

    def test_saturn_enters_pisces_2025(self):
        r = W.next_sign_change("Saturn", E.julian_day_ut(2024, 1, 1, 0.0))
        self.assertEqual((r["from_sign"], r["to_sign"]), (10, 11))
        self.assertEqual(E.jd_to_calendar(r["jd_ut"])[:3], (2025, 3, 29))

    def test_retrograde_sign_change(self):
        r = W.next_sign_change("Rahu", E.julian_day_ut(2024, 1, 1, 0.0))   # mean node moves backwards
        self.assertEqual((r["from_sign"], r["to_sign"]), (11, 10))

    def test_ardra_pravesha(self):
        jd = W.ardra_pravesha(2024)
        self.assertAlmostEqual(E.planet_positions(jd)["Sun"]["lon"], 5 * 360 / 27, places=4)
        self.assertEqual(E.jd_to_calendar(jd)[:2], (2024, 6))

    def test_lagna_change(self):
        b = self.birth()
        sign = int(E.lagna_at(b.jd_ut, b) // 30)
        for back in (False, True):
            jd = W.lagna_sign_change(b, backward=back)["jd_ut"]
            inside, outside = (jd + 1e-4, jd - 1e-4) if back else (jd - 1e-4, jd + 1e-4)
            self.assertEqual(int(E.lagna_at(inside, b) // 30), sign)
            self.assertNotEqual(int(E.lagna_at(outside, b) // 30), sign)

    def test_returns_and_tithi_pravesha(self):
        b = self.birth()
        natal = E.planet_positions(b.jd_ut)
        sr = W.solar_return(b, 30)
        self.assertAlmostEqual(E.planet_positions(sr)["Sun"]["lon"], natal["Sun"]["lon"], places=4)
        tp = W.tithi_pravesha(b, 30)
        p = E.planet_positions(tp["exact_jd"])
        self.assertAlmostEqual((p["Moon"]["lon"] - p["Sun"]["lon"]) % 360,
                               (natal["Moon"]["lon"] - natal["Sun"]["lon"]) % 360, places=3)
        self.assertEqual(int(p["Sun"]["lon"] // 30), int(natal["Sun"]["lon"] // 30))

    def test_calendar_entry_chart_matching(self):
        b = self.birth()
        chart = E.build_chart(b)
        cal = W.transit_calendar(chart, b.jd_ut, rows=500)
        self.assertEqual(len(cal), 100)
        self.assertEqual(cal[0]["bodies"]["Moon"]["house_from_moon"], 1)
        tree = D.compute_vimshottari_tree(chart["planet_longitudes"]["Moon"],
                                          datetime(b.year, b.month, b.day) + timedelta(hours=b.hour_local))
        entry = W.entry_chart(b, tree[1], with_special_points=False)
        start = datetime.fromisoformat(tree[1]["start"])
        self.assertEqual((entry["config"].ayanamsa, E.jd_to_calendar(entry["jd_ut"] + b.tz_east_hours / 24)[:3]),
                         ("TRUE_LAHIRI", (start.year, start.month, start.day)))
        self.assertIn("gunanka_score", W.match_charts(chart, chart))


if __name__ == "__main__":
    unittest.main()
