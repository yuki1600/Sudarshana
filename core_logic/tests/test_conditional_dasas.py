"""The conditional nakshatra dasa methodology on hand-built charts; each case states the rule it checks."""
import unittest

from core_logic import conditional_dasas as C
from core_logic import dasa_systems as J


def sign(name):
    return J.SIGN_ABBR.index(name) * 30.0


# Aries lagna, no condition met, each planet alone in its sign and Taurus, Cancer and Capricorn free; each test moves what it is about
QUIET = {"Sun": 75.0, "Moon": 165.0, "Mars": 135.0, "Mercury": 225.0, "Jupiter": 255.0, "Venus": 315.0,
         "Saturn": 345.0, "Rahu": 195.0, "Ketu": 15.0}


def chart(lagna=15.0, is_day=True, **moved):
    return J.JChart({"planet_longitudes": {**QUIET, **moved}, "lagna_lon": lagna}, {"is_day": is_day})


def result(jc, **kw):
    return C.best_dasa(jc, [False] * 10, **kw)


def row(jc, key):
    return next(r for r in result(jc)["rows"] if r["key"] == key)


class TestConditions(unittest.TestCase):
    def met(self, key, **kw):
        return row(chart(**kw), key)["met"]

    def test_lagna_hora_with_paksha(self):
        sukla, krishna = {"Sun": 0.0, "Moon": 90.0}, {"Sun": 90.0, "Moon": 0.0}
        self.assertTrue(self.met("shodasottari_dasa", lagna=5.0, **sukla))          # odd sign, first half: Sun's hora
        self.assertFalse(self.met("shodasottari_dasa", lagna=5.0, **krishna))
        self.assertTrue(self.met("shodasottari_dasa", lagna=20.0, **krishna))       # odd sign, second half: Moon's
        self.assertTrue(self.met("shodasottari_dasa", lagna=sign("Ta") + 20.0, **sukla))    # even sign, second half: Sun's
        self.assertFalse(self.met("shodasottari_dasa", lagna=sign("Ta") + 5.0, **sukla))

    def test_lagna_hora_with_day_or_night(self):
        self.assertTrue(self.met("shat_trimsa_sama_dasa", lagna=5.0, is_day=True))
        self.assertFalse(self.met("shat_trimsa_sama_dasa", lagna=5.0, is_day=False))
        self.assertTrue(self.met("shat_trimsa_sama_dasa", lagna=20.0, is_day=False))

    def test_navamsa_and_dwadasamsa(self):
        self.assertTrue(self.met("dwadasottari_dasa", lagna=5.0))       # Aries 3:20 - 6:40 is Taurus navamsa
        self.assertFalse(self.met("dwadasottari_dasa", lagna=8.0))
        self.assertTrue(self.met("sataabdika_dasa", lagna=1.0))         # Aries navamsa of Aries
        self.assertFalse(self.met("sataabdika_dasa", lagna=5.0))
        self.assertTrue(self.met("panchottari_dasa", lagna=8.0))        # Aries 7:30 - 10:00 is Cancer dwadasamsa
        self.assertFalse(self.met("panchottari_dasa", lagna=5.0))

    def test_rahu_from_the_lagna_lord(self):
        mars_cn = {"Mars": sign("Cn") + 5.0}
        self.assertTrue(self.met("ashtottari_dasa", Rahu=sign("Li") + 5.0, **mars_cn))      # 4th from Mars
        self.assertTrue(self.met("ashtottari_dasa", Rahu=sign("Sc") + 5.0, **mars_cn))      # 5th from Mars
        self.assertTrue(self.met("ashtottari_dasa", Rahu=sign("Cn") + 9.0, **mars_cn))      # with Mars
        self.assertFalse(self.met("ashtottari_dasa", Rahu=sign("Le") + 5.0, **mars_cn))     # 2nd from Mars
        self.assertFalse(self.met("ashtottari_dasa", Rahu=5.0, **mars_cn))                  # 10th from Mars, but in lagna

    def test_rahu_house_is_counted_by_degree(self):
        # PVR paper Examples 15 and 28: Rahu in a quadrant by sign, yet the 8th / 3rd house from the lord by degree
        self.assertFalse(self.met("ashtottari_dasa", Mars=sign("Sg") + 1.2, Rahu=sign("Ge") + 25.1))
        self.assertFalse(self.met("ashtottari_dasa", Mars=sign("Ge") + 28.6, Rahu=sign("Vi") + 5.2))
        self.assertTrue(self.met("ashtottari_dasa", Mars=sign("Ge") + 28.6, Rahu=sign("Vi") + 15.0))

    def test_houses_are_counted_by_degree_from_the_lagna(self):
        # Aries 29° lagna: houses run from the lagna's degree, not from the sign boundary
        self.assertFalse(self.met("shashti_hayani_dasa", lagna=29.0, Sun=5.0))                  # same sign, 24° behind: the 12th
        self.assertTrue(self.met("shashti_hayani_dasa", lagna=29.0, Sun=sign("Ta") + 5.0))      # next sign, 6° ahead: the 1st
        self.assertFalse(self.met("chaturaseeti_sama_dasa", lagna=29.0, Saturn=sign("Cp") + 5.0))   # Capricorn, yet the 9th
        self.assertTrue(self.met("chaturaseeti_sama_dasa", lagna=29.0, Saturn=sign("Aq") + 5.0))    # Aquarius, yet the 10th
        self.assertFalse(self.met("dwi_saptati_sama_dasa", lagna=29.0, Mars=sign("Li") + 5.0))      # Libra, yet the 6th
        self.assertTrue(self.met("dwi_saptati_sama_dasa", lagna=29.0, Mars=sign("Sc") + 5.0))       # Scorpio, yet the 7th
        self.assertFalse(self.met("ashtottari_dasa", lagna=29.0, Rahu=sign("Ta") + 5.0, Mars=sign("Cn") + 5.0))   # Taurus, yet in lagna: 10th from Mars but excluded

    def test_lords_and_sun(self):
        self.assertTrue(self.met("chaturaseeti_sama_dasa", Saturn=sign("Cp") + 5.0))
        self.assertTrue(self.met("dwi_saptati_sama_dasa", Mars=sign("Li") + 5.0))
        self.assertTrue(self.met("dwi_saptati_sama_dasa", Venus=5.0))
        self.assertTrue(self.met("shashti_hayani_dasa", Sun=5.0))
        self.assertFalse(self.met("shashti_hayani_dasa"))


class TestStrength(unittest.TestCase):
    JUPITER = "shodasottari_dasa"

    def test_the_order_of_dignities(self):
        got = {s: row(chart(Jupiter=sign(s) + 15.0), self.JUPITER)["dignity"] for s in ("Cn", "Sg", "Pi", "Cp")}
        self.assertEqual(got, {"Cn": "exalted", "Sg": "moolatrikona", "Pi": "own sign", "Cp": "debilitated"})

    def test_compound_relationship_with_the_sign_lord(self):
        # Jupiter's natural friend Mars: temporal friend when 2/3/4/10/11/12 from Jupiter, else only neutral
        close = row(chart(Jupiter=sign("Ar") + 15.0, Mars=sign("Ta") + 15.0), self.JUPITER)
        self.assertEqual((close["score"], close["dignity"]), (2, "great friend's sign"))
        far = row(chart(Jupiter=sign("Ar") + 15.0, Mars=sign("Le") + 15.0), self.JUPITER)
        self.assertEqual((far["score"], far["dignity"]), (0, "neutral sign"))

    def test_shadbala_below_the_minimum_is_weak(self):
        jc = chart(Jupiter=sign("Cn") + 15.0)                      # exalted: 5
        weak = C.best_dasa(jc, [False] * 10, shadbala=[0, 0, 0, 0, 0, 99.0, 0, 0])["rows"][0]
        self.assertEqual((weak["score"], weak["notes"]), (0, ["Shadbala 99% of the minimum"]))
        enough = C.best_dasa(jc, [False] * 10, shadbala=[0, 0, 0, 0, 0, 100.0, 0, 0])["rows"][0]
        self.assertEqual((enough["score"], enough["notes"]), (5, []))
        node = C.best_dasa(jc, [False] * 10, shadbala=[0] * 8)["rows"][6]      # Rahu has no Shadbala entry
        self.assertNotIn("Shadbala", " ".join(node["notes"]))

    def test_the_edge_of_a_sign_is_weak(self):
        self.assertEqual(row(chart(Jupiter=sign("Cn") + 0.5), self.JUPITER)["score"], 0)
        self.assertEqual(row(chart(Jupiter=sign("Cn") + 29.5), self.JUPITER)["score"], 0)
        self.assertEqual(row(chart(Jupiter=sign("Cn") + 1.5), self.JUPITER)["score"], 5)

    def test_combust_is_weak(self):
        got = row(chart(Jupiter=sign("Cn") + 15.0, Sun=sign("Cn") + 13.0), self.JUPITER)
        self.assertEqual(got["score"], 0)
        self.assertIn("combust", got["notes"])

    def test_with_an_enemy_or_a_6th_or_8th_lord_is_weak(self):
        got = row(chart(Jupiter=sign("Cn") + 15.0, Venus=sign("Cn") + 25.0), self.JUPITER)      # Venus: Jupiter's enemy, not 9th / 10th lord for Aries
        self.assertEqual(got["score"], 0)
        self.assertIn("with its enemy Venus", got["notes"])
        # Virgo lagna: Saturn is 6th lord and not Jupiter's enemy
        got = row(chart(lagna=sign("Vi") + 15.0, Jupiter=sign("Cn") + 15.0, Saturn=sign("Cn") + 25.0), self.JUPITER)
        self.assertEqual(got["score"], 0)
        self.assertIn("with Saturn (6th lord)", got["notes"])

    def test_with_the_9th_or_10th_lord_is_half_a_step(self):
        got = row(chart(Jupiter=sign("Cn") + 15.0, Saturn=sign("Cn") + 25.0), self.JUPITER)     # Aries lagna: Saturn is 10th lord
        self.assertEqual(got["score"], 5.5)
        self.assertIn("with Saturn (10th lord)", got["notes"])
        got = row(chart(Jupiter=sign("Ar") + 15.0, Mars=sign("Le") + 15.0, Saturn=sign("Ar") + 25.0), self.JUPITER)
        self.assertEqual(got["score"], 0.5)     # a weak planet just comes into consideration

    def test_a_9th_or_10th_lord_that_is_an_enemy_does_not_afflict(self):
        # Aquarius lagna: Venus is 9th lord and Jupiter's enemy
        got = row(chart(lagna=sign("Aq") + 15.0, Jupiter=sign("Cn") + 15.0, Venus=sign("Cn") + 25.0), self.JUPITER)
        self.assertEqual(got["score"], 5.5)

    def test_a_node_is_strong_with_any_planet(self):
        key = "dwi_saptati_sama_dasa"
        alone = row(chart(Rahu=sign("Le") + 15.0, Mars=15.0), key)
        self.assertEqual(alone["score"], 0)                                     # Rahu in the Sun's sign: no friend's
        joined = row(chart(Rahu=sign("Le") + 15.0, Mars=15.0, Sun=sign("Le") + 25.0), key)
        self.assertEqual(joined["score"], 0.5)                                  # the Sun is its enemy, yet "any planets"
        self.assertEqual(joined["notes"], ["with Sun"])

    def test_the_nodal_exaltation_setting_is_followed(self):
        C.S.set_nodal_exaltation(False)
        self.addCleanup(C.S.set_nodal_exaltation, False)
        self.assertEqual(row(chart(Rahu=sign("Ge") + 15.0), "dwi_saptati_sama_dasa")["dignity"], "exalted")
        C.S.set_nodal_exaltation(True)
        self.assertEqual(row(chart(Rahu=sign("Ta") + 15.0), "dwi_saptati_sama_dasa")["dignity"], "exalted")


class TestSelection(unittest.TestCase):
    # Both apply: 10th lord Saturn in the 10th (Capricorn, own sign), and Sun in lagna with the Moon
    TWO = {"Saturn": sign("Cp") + 15.0, "Sun": 15.0}

    def test_the_strongest_controlling_planet_wins(self):
        got = result(chart(Moon=sign("Ta") + 15.0, **self.TWO))     # Moon exalted beats Saturn in own sign
        self.assertEqual(got["best"], ["shashti_hayani_dasa"])

    def test_a_planet_of_an_unmet_condition_does_not_count(self):
        got = result(chart(Moon=sign("Ta") + 15.0, Saturn=sign("Cp") + 15.0))   # Moon exalted, but the Sun is not in lagna
        self.assertNotIn("shashti_hayani_dasa", got["best"])

    def test_ties_are_reported(self):
        # Saturn and the Moon both in their own signs
        got = result(chart(Moon=sign("Cn") + 15.0, **self.TWO))
        self.assertEqual(sorted(got["best"]), ["chaturaseeti_sama_dasa", "shashti_hayani_dasa"])

    def test_no_strong_planet_means_vimsottari(self):
        got = result(chart(Saturn=sign("Cp") + 15.0, Sun=sign("Cp") + 25.0, Moon=345.0))     # only the 10th lord's condition; Saturn with its enemy
        self.assertEqual([r["key"] for r in got["rows"] if r["met"]], ["chaturaseeti_sama_dasa"])
        self.assertEqual(got["best"], ["vimsottari_dasa"])

    def test_no_condition_met_means_vimsottari(self):
        got = result(chart())
        self.assertFalse(any(r["met"] for r in got["rows"]))
        self.assertEqual(got["best"], ["vimsottari_dasa"])


if __name__ == "__main__":
    unittest.main()
