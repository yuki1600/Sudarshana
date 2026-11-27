"""Option branches (R1–R5), each case worked on a hand-built chart."""
import unittest
from datetime import datetime

from core_logic.avasthas import graha_avasthas
from core_logic.ephemeris import BirthData, EphemerisConfig, planet_positions, sunrise_sunset
from core_logic.dasa_systems import event_year_definition
from core_logic.kp_astrology import kp_period_date
from core_logic.shadbala import VARGA_ORDER, AmsaBala, vaiseshikamsa_counts
from core_logic.sign_strength import bhava_arudhas

NINE_SIGNS = {
    "cancer": [0, 1, 3, 2, 4, 5, 6, 7, 8],   # Mars (index 2) in Cancer; lagna Aries → AL Cancer
    "virgo_sun": [5, 1, 0, 2, 4, 1, 6, 7, 8],  # Sun in Virgo, Venus in Taurus; lagna Taurus → AL Aquarius
}


def _vargas(signs):
    return {v: list(signs) for v in VARGA_ORDER}


def _amsa(signs, lons, lagna_sign, swarudha, **flags):
    off = dict(combustion=False, defeat=False, neecha=False, poor_vimsopaka=False, sayanadi=False)
    off.update(flags)
    return AmsaBala(swarudha=swarudha, rasi_lons=lons, lagna_signs=[lagna_sign] * 20,
                    lagna_lon=lons[0], **off)


class TestVaiseshikamsaOptions(unittest.TestCase):
    def test_default_ignores_a_kendra_from_the_arudha_lagna(self):
        signs = NINE_SIGNS["cancer"]
        self.assertEqual(bhava_arudhas([0] + signs, (10.0,) + tuple(range(10, 100, 10)))[0], 3)
        vai = vaiseshikamsa_counts(_vargas(signs))
        self.assertEqual(vai["Mars"]["shad"], 0)
        same = vaiseshikamsa_counts(_vargas(signs), AmsaBala(swarudha=0))
        self.assertEqual(same["Mars"]["shad"], 0)

    def test_swarudha_kendra_and_the_debilitation_cancel(self):
        signs, lons = NINE_SIGNS["cancer"], [10, 40, 100, 70, 130, 160, 190, 220, 250]
        on = vaiseshikamsa_counts(_vargas(signs), _amsa(signs, lons, 0, 1))
        self.assertEqual(on["Mars"]["shad"], 6)
        neecha = vaiseshikamsa_counts(_vargas(signs), _amsa(signs, lons, 0, 1, neecha=True))
        self.assertEqual(neecha["Mars"]["shad"], 0)

    def test_own_sign_is_not_cancelled_by_combustion(self):
        # Mars in its own sign, 4 deg from the Sun. Own / exaltation / moolatrikona return before the bad flags.
        signs = [8, 1, 0, 2, 4, 5, 6, 7, 8]
        lons = [8.0, 40, 12.0, 70, 130, 160, 190, 220, 250]
        vai = vaiseshikamsa_counts(_vargas(signs), _amsa(signs, lons, 0, 1, combustion=True))
        self.assertEqual(vai["Mars"]["shad"], 6)

    def test_combustion_and_defeat_cancel_the_rasi_only(self):
        signs = NINE_SIGNS["cancer"]
        close = [90.0, 40, 94.0, 70, 130, 160, 190, 220, 250]   # Mars 4 deg from the Sun
        burnt = vaiseshikamsa_counts(_vargas(signs), _amsa(signs, close, 0, 1, combustion=True))
        self.assertEqual(burnt["Mars"]["shad"], 5)
        ahead = [10.0, 40, 94.0, 70, 94.5, 160, 190, 220, 250]  # Jupiter 0.5 deg ahead of Mars
        lost = vaiseshikamsa_counts(_vargas(signs), _amsa(signs, ahead, 0, 1, defeat=True))
        self.assertEqual(lost["Mars"]["shad"], 5)

    def test_ruling_a_kendra_from_the_arudha_lagna(self):
        signs, lons = NINE_SIGNS["virgo_sun"], [150, 40, 10, 70, 130, 40, 190, 220, 250]
        self.assertEqual(bhava_arudhas([1] + signs, (40.0,) + tuple(lons))[0], 10)
        mode6 = vaiseshikamsa_counts(_vargas(signs), _amsa(signs, lons, 1, 6))
        mode1 = vaiseshikamsa_counts(_vargas(signs), _amsa(signs, lons, 1, 1))
        self.assertEqual(mode6["Sun"]["shad"], 6)
        self.assertEqual(mode1["Sun"]["shad"], 0)


class TestAvasthaCompound(unittest.TestCase):
    def test_alertness_uses_the_compound_table_when_asked(self):
        # Saturn in Aries, Mars (its lord) in Taurus: natural enemy, asleep; compound neutral, dreaming.
        lons = [100.0, 70, 40.0, 100, 130, 160, 10.0, 220, 250]
        natural = graha_avasthas(lons, 10.0, 0.0)
        compound = graha_avasthas(lons, 10.0, 0.0, compound=True)
        self.assertEqual(natural["Saturn"]["alertness"], 2)
        self.assertEqual(compound["Saturn"]["alertness"], 1)
        self.assertEqual(natural["Saturn"]["activity"], compound["Saturn"]["activity"])


class TestEventYearDefinition(unittest.TestCase):
    def test_tajaka_and_tithi_pravesha_force_the_year(self):
        self.assertEqual(event_year_definition(6, 1), 3)
        self.assertEqual(event_year_definition(6, 2), 4)
        self.assertEqual(event_year_definition(6, 5, "Solar return"), 3)
        self.assertEqual(event_year_definition(6, 5, "Lunar return"), 4)
        self.assertEqual(event_year_definition(6, 5, "Moon"), 4)
        self.assertEqual(event_year_definition(6, 5, "Solar Moon"), 4)
        self.assertEqual(event_year_definition(6, 0, "Solar"), 6)
        self.assertEqual(event_year_definition(6, 1, special_year_tajaka=False), 6)
        self.assertEqual(event_year_definition(6, 2, special_year_tp=False), 6)


class TestMeridianAndRefraction(unittest.TestCase):
    def test_upper_transit_is_the_local_noon(self):
        sun = sunrise_sunset(BirthData(1990, 6, 21, 12.0, 5.5, 77.2, 28.6))
        self.assertLess(sun["sunrise_hours"], sun["upper_transit_hours"])
        self.assertLess(sun["upper_transit_hours"], sun["sunset_hours"])
        # the lower transit is searched from the sunrise: the midnight after the sunset
        self.assertLess(sun["sunset_hours"], sun["lower_transit_hours"])

    def test_refraction_moves_an_apparent_position_only(self):
        birth = BirthData(1990, 6, 21, 6.5, 5.5, 77.2, 28.6)
        jd = birth.jd_ut
        true = EphemerisConfig(true_positions=True, apparent_refraction=True)
        plain = EphemerisConfig(true_positions=True, apparent_refraction=False)
        apparent = EphemerisConfig(true_positions=False, apparent_refraction=True)
        off = EphemerisConfig(true_positions=False, apparent_refraction=False)
        self.assertEqual(planet_positions(jd, true, birth)["Sun"]["lon"],
                         planet_positions(jd, plain, birth)["Sun"]["lon"])
        self.assertNotEqual(planet_positions(jd, apparent, birth)["Sun"]["lon"],
                            planet_positions(jd, off, birth)["Sun"]["lon"])


class TestKpPeriodDate(unittest.TestCase):
    def test_span_of_one_mean_year_is_one_solar_year(self):
        birth = BirthData(1990, 1, 1, 6.5, 5.5, 77.2, 28.6)
        one = kp_period_date(birth, 1.0)
        fitted = kp_period_date(birth, 120.0, span_days=365.24219)
        self.assertLess(abs((fitted - one).total_seconds()), 2.0)
        self.assertLess(abs((kp_period_date(birth, 0.0) - datetime(1990, 1, 1, 6, 30)).total_seconds()), 1.0)


if __name__ == "__main__":
    unittest.main()
