"""core_logic.ayurdaya against its verses, each expected value worked by hand from BPHS."""
import unittest

from core_logic import ayurdaya as A

# A chart with nothing special: Virgo lagna, Sun .. Ketu spread over the houses; each test moves what it needs
BASE = {0: 150.0, 1: 40.0, 2: 70.0, 3: 100.0, 4: 130.0, 5: 160.0, 6: 190.0, 7: 220.0, 8: 250.0, 9: 70.0}


def chart(hora_lagna=0.0, **kw):
    """``p1=..`` moves point 1; the other keywords go to Natal."""
    lons = dict(BASE)
    for k in [k for k in kw if k[0] == "p" and k[1:].isdigit()]:
        lons[int(k[1:])] = kw.pop(k)
    return A.Natal([lons[p] for p in range(10)], hora_lagna, **kw)


def row(span, p):
    return next(r for r in span["rows"] if r["point"] == p)


class TestYears(unittest.TestCase):
    def test_arc_runs_from_full_at_exaltation_to_half_at_debilitation(self):
        self.assertAlmostEqual(A.arc_years(1, 10.0), 19.0)
        self.assertAlmostEqual(A.arc_years(1, 190.0), 9.5)
        self.assertAlmostEqual(A.arc_years(1, 100.0), 14.25)       # a quarter of the way round, from either side
        self.assertAlmostEqual(A.arc_years(1, 280.0), 14.25)
        self.assertAlmostEqual(A.arc_years(7, 200.0, A.NISARGA_YEARS), 50.0)

    def test_nisarga_years_add_to_120(self):
        self.assertEqual(sum(A.NISARGA_YEARS), 120)

    def test_navamsa_years_expunge_twelves(self):
        self.assertAlmostEqual(A.navamsa_years(0.0), 0.0)
        self.assertAlmostEqual(A.navamsa_years(10.0 / 3.0), 1.0)
        self.assertAlmostEqual(A.navamsa_years(40.0), 0.0)         # 12 navamsas
        self.assertAlmostEqual(A.navamsa_years(50.0), 3.0)

    def test_classes_of_years(self):
        self.assertEqual([A.class_of_years(y) for y in (31.9, 32.0, 63.9, 64.0, 100.0, 100.1)], [A.SHORT, A.MEDIUM, A.MEDIUM, A.LONG, A.LONG, A.EXTREME])

    def test_ashtakavarga_rekhas(self):
        t = A.ashtakavarga_years([[0, 1, 2, 3, 4, 5, 6, 7, 8, 0, 0, 0]])
        self.assertAlmostEqual(t["rows"][0], 20.0 + (2.0 + 1.5 + 1.0 + 0.5 + 7.5 + 2.0 * 3) / 360.0)
        self.assertAlmostEqual(t["years"], t["rows"][0] / 2.0)

    def test_saturn_ashtakavarga_counts_both_end_signs(self):
        bav = [1, 2, 3, 4, 5, 6, 7, 8, 1, 2, 3, 4]
        t = A.saturn_ashtakavarga(bav, 10, 0, 2)     # lagna Aries, Saturn Gemini
        self.assertEqual((t["lagna_to_saturn"], t["saturn_to_lagna"], t["total"]), (1 + 2 + 3, sum(bav[2:]) + 1, 6 + sum(bav[2:]) + 1))
        self.assertEqual(t["rekhas"], bav[9])        # the 8th from Gemini is Capricorn
        self.assertEqual(t["product"], 20)
        self.assertEqual(t["stars"], [19, 1, 10])    # remainder 20 is the 20th star, then its trines
        self.assertEqual(t["signs"], [7, 11, 3])     # remainder 8 is the 8th sign, then its trines
        self.assertEqual(A.saturn_ashtakavarga([0] * 12, 10, 0, 2)["stars"], [])


class TestReductions(unittest.TestCase):
    def test_combust_and_enemy_together_only_halve(self):
        # Mars and the Sun in Gemini within 6 degrees, Mercury's sign is Mars's enemy's
        n = chart(p1=70.0, p3=72.0, p2=10.0, p9=250.0)
        r = row(A.spans(n)["pinda"], 3)
        self.assertTrue(r["combust"] and r["enemy"])
        self.assertAlmostEqual(r["after"], r["gross"] * (1.0 - r["visible"]) * 0.5)

    def test_retrograde_escapes_the_enemy_sign(self):
        retro = [False] * 10
        retro[3] = True
        self.assertTrue(row(A.spans(chart(p3=70.0, p1=40.0))["pinda"], 3)["enemy"])
        self.assertFalse(row(A.spans(chart(p3=70.0, p1=40.0, retro=retro))["pinda"], 3)["enemy"])

    def test_venus_and_saturn_are_not_halved(self):
        n = chart(p1=190.0, p6=191.0, p7=192.0, p3=250.0, p4=250.0)
        spans = A.spans(n)["pinda"]
        self.assertFalse(row(spans, 6)["combust"])
        self.assertFalse(row(spans, 7)["combust"])

    def test_visible_half_by_house_and_nature(self):
        # lagna Virgo: Saturn in Leo is the 12th, Jupiter in Taurus the 9th, Mars in Pisces the 7th
        s = A.spans(chart(p7=130.0, p4=160.0, p5=40.0, p3=340.0, p1=40.0))["pinda"]
        self.assertAlmostEqual(row(s, 7)["visible"], 1.0)
        self.assertAlmostEqual(row(s, 3)["visible"], 1 / 6)

    def test_a_waning_moon_loses_as_a_benefic(self):
        n = chart(p2=130.0, p1=250.0)        # the Moon in the 12th, 240 degrees from the Sun: waning
        self.assertFalse(n.waxing)
        self.assertAlmostEqual(row(A.spans(n)["pinda"], 2)["visible"], 0.5)

    def test_only_the_strongest_in_a_house_takes_the_visible_half(self):
        # the Sun has more virupas, Saturn more against its minimum
        s = A.spans(chart(p1=130.0, p7=131.0, bala=[0.0, 500.0] + [0.0] * 5 + [400.0, 0.0, 0.0], percent=[0.0, 100.0] + [0.0] * 5 + [133.0, 0.0, 0.0]))["pinda"]
        self.assertEqual(row(s, 1)["visible"], 0.0)
        self.assertAlmostEqual(row(s, 7)["visible"], 1.0)

    def test_malefic_in_the_lagna(self):
        # Saturn in the lagna at 150: no benefic aspects Virgo once Jupiter is moved off its 5th, 7th and 9th
        n = chart(p7=151.0, p5=70.0, p2=70.0, p4=70.0, p6=70.0, p1=100.0)
        r = row(A.spans(n)["pinda"], 7)
        self.assertAlmostEqual(r["lagna_cut"], r["after"] * 150.0 * 60.0 / 21600.0)
        # a benefic's drishti on the lagna halves the loss: Venus in Pisces
        n = chart(p7=151.0, p5=70.0, p2=70.0, p4=70.0, p6=340.0, p1=100.0)
        r = row(A.spans(n)["pinda"], 7)
        self.assertAlmostEqual(r["lagna_cut"], r["after"] * 150.0 * 60.0 / 21600.0 / 2.0)

    def test_lagna_share_by_rasi_or_navamsa(self):
        # lagna 150.0: 5 rasis gained; its navamsa is Capricorn's, Saturn, against Mercury
        self.assertEqual(A.lagna_years(chart()), (5.0, "rasis"))
        percent = [0.0] * 10
        percent[7] = 10.0
        years, basis = A.lagna_years(chart(percent=percent))
        self.assertEqual(basis, "navamsas")
        self.assertAlmostEqual(years, 150.0 * 0.3 % 12)

    def test_amsayu_trebles_and_doubles(self):
        s = A.spans(chart(p3=10.0))["amsa"]           # Mars in its own Aries: trebled over any doubling
        self.assertEqual(row(s, 3)["factor"], 3)
        s = A.spans(chart(p7=32.0))["amsa"]           # Saturn in Taurus 2: the navamsa of Capricorn
        self.assertEqual(row(s, 7)["factor"], 2)
        self.assertAlmostEqual(row(s, 7)["net"], A.navamsa_years(32.0) * 2 * (1.0 - row(s, 7)["visible"]))

    def test_the_strongest_picks_the_span_and_equals_average(self):
        # the Lagna has the most virupas (504 = 120% of 7 rupas) but the Sun stands higher over its minimum
        sp = A.spans(chart(bala=[0.0, 390.0, 300.0] + [0] * 7, percent=[0.0, 130.0, 100.0] + [0] * 7, lagna_bala=504.0))
        self.assertEqual(sp["chosen"], ["pinda"])
        sp = A.spans(chart(bala=[0.0, 360.0, 300.0] + [0] * 7, percent=[0.0, 120.0, 100.0] + [0] * 7, lagna_bala=504.0))
        self.assertEqual(sorted(sp["chosen"]), ["amsa", "pinda"])
        self.assertAlmostEqual(sp["years"], (sp["amsa"]["total"] + sp["pinda"]["total"]) / 2.0)


class TestThreePairs(unittest.TestCase):
    def test_the_nine_pairs_of_modes(self):
        table = {(0, 0): A.LONG, (1, 2): A.LONG, (2, 1): A.LONG, (0, 1): A.MEDIUM, (1, 0): A.MEDIUM, (2, 2): A.MEDIUM, (0, 2): A.SHORT, (2, 0): A.SHORT, (1, 1): A.SHORT}
        for (a, b), c in table.items():
            self.assertEqual(A.pair_class(a + 3, b + 6), c)

    def test_years_by_agreement(self):
        self.assertEqual(A.SPAN_YEARS[A.LONG], {3: 120, 2: 108, 1: 96})
        self.assertEqual(A.SPAN_YEARS[A.MEDIUM], {3: 80, 2: 72, 1: 64})
        self.assertEqual(A.SPAN_YEARS[A.SHORT], {3: 32, 2: 36, 1: 40})

    def test_three_agreeing(self):
        # Leo lagna (fixed): lord the Sun, 8th Pisces's lord Jupiter
        n = chart(hora_lagna=65.0, p0=125.0, p1=35.0, p5=65.0, p2=95.0, p7=5.0)    # Sun fixed + Jupiter dual, Moon movable + Saturn movable, fixed + dual
        r = A.three_pairs(n)
        self.assertEqual(r["classes"], [A.LONG] * 3)
        self.assertEqual(r["votes"], 3)
        self.assertEqual(r["base"], A.LONG)

    def test_all_differ_lagna_and_hora_lagna_decide(self):
        # Leo lagna: Sun fixed + Jupiter fixed = short; Moon movable + Saturn fixed = medium; Lagna fixed + Hora Lagna dual = long
        n = chart(hora_lagna=65.0, p0=125.0, p1=35.0, p5=215.0, p2=95.0, p7=35.0)
        r = A.three_pairs(n)
        self.assertEqual(r["classes"], [A.SHORT, A.MEDIUM, A.LONG])
        self.assertEqual((r["votes"], r["base"]), (1, A.LONG))
        self.assertEqual(r["contributors"], ["Lagna", "Hora Lagna"])

    def test_all_differ_with_the_moon_in_the_7th_saturn_and_moon_decide(self):
        # Leo lagna, the Moon in Aquarius (fixed, the 7th) with Saturn in Cancer: medium; Lagna + Hora Lagna dual: long
        n = chart(hora_lagna=65.0, p0=125.0, p1=35.0, p5=215.0, p2=305.0, p7=95.0)
        r = A.three_pairs(n)
        self.assertEqual(r["classes"], [A.SHORT, A.MEDIUM, A.LONG])
        self.assertEqual((r["votes"], r["base"]), (1, A.MEDIUM))
        self.assertEqual(r["contributors"], ["Saturn", "Moon"])

    def test_saturn_as_contributor_lowers_the_class_unless_exempt(self):
        # Leo lagna: Moon dual + Saturn dual = medium, Lagna fixed + Hora Lagna movable = medium, the lords short
        kw = dict(hora_lagna=95.0, p0=125.0, p1=35.0, p5=215.0, p2=65.0, p7=155.0, p4=10.0, p6=10.0, p8=10.0, p9=190.0, saturn_rule=1)
        r = A.three_pairs(chart(p3=10.0, **kw))
        self.assertEqual(r["base"], A.MEDIUM)
        self.assertTrue(r["falls"])
        self.assertEqual((r["class"], r["years"]), (A.SHORT, 36))
        # influenced only by a malefic: Mars with Saturn
        r = A.three_pairs(chart(p3=156.0, **kw))
        self.assertFalse(r["falls"])
        self.assertEqual((r["class"], r["years"]), (A.MEDIUM, 72))
        # in its own Capricorn, all three pairs long
        r = A.three_pairs(chart(hora_lagna=65.0, p0=125.0, p1=35.0, p5=65.0, p2=95.0, p7=275.0))
        self.assertEqual(r["votes"], 3)
        self.assertFalse(r["falls"])
        self.assertEqual((r["class"], r["years"]), (A.LONG, 120))

    def test_saturn_settings_and_the_outer_years(self):
        # Leo lagna: the lords (Sun Taurus, Jupiter Scorpio) and Saturn (Leo) with the Moon (Taurus) short; Saturn, in his own pair, lowers it
        kw = dict(hora_lagna=95.0, p0=125.0, p1=35.0, p5=215.0, p2=40.0, p7=140.0, p4=10.0, p6=10.0, p3=10.0, p8=190.0, p9=10.0)
        r = A.three_pairs(chart(saturn_rule=1, **kw))
        self.assertEqual((r["base"], r["class"], r["years"]), (A.SHORT, A.VERY_SHORT, None))
        # Yogarishta's 20 years when asked, rectified from 0 like short life: average 10 deg leaves two thirds
        r = A.three_pairs(chart(outer_years=True, saturn_rule=1, **kw))
        self.assertEqual(r["years"], 20)
        self.assertAlmostEqual(r["rectified"], 20 * (1 - r["average"] / 30))
        # Saturn neither lagna lord nor 8th lord here: the stricter reading (the default), and never, leave the class short
        # a malefic 26 deg off in the same rasi is not touching him by the orbs
        self.assertFalse(chart(p7=2.0, p3=28.0, orbs=True).touched_by(7, [3]))
        for rule in (0, 2):
            self.assertEqual(A.three_pairs(chart(saturn_rule=rule, **kw))["class"], A.SHORT)

    def test_jupiter_in_the_7th_with_only_benefics_raises_the_class(self):
        # Leo lagna: Sun fixed + Jupiter fixed = short, Lagna fixed + Hora Lagna fixed = short, and Saturn's pair (long) not a contributor. Jupiter in the 7th with Venus
        kw = dict(hora_lagna=35.0, p0=125.0, p1=35.0, p5=305.0, p6=306.0, p2=65.0, p3=10.0, p4=100.0, p8=10.0, p9=190.0)
        r = A.three_pairs(chart(p7=215.0, **kw))
        self.assertEqual(r["base"], A.SHORT)
        self.assertTrue(r["rises"])
        self.assertEqual((r["class"], r["years"]), (A.MEDIUM, 72))
        # Saturn in Taurus aspects Jupiter by its 10th: no longer only benefics
        self.assertFalse(A.three_pairs(chart(p7=35.0, **kw))["rises"])

    def test_rectification_by_compartment_and_literally(self):
        # every contributor at 5 degrees of its sign, with Saturn exempt in Capricorn
        r = A.three_pairs(chart(hora_lagna=65.0, p0=125.0, p1=35.0, p5=65.0, p2=95.0, p7=275.0))
        self.assertAlmostEqual(r["average"], 5.0)
        self.assertAlmostEqual(r["literal"], 120 * 25 / 30)
        self.assertAlmostEqual(r["rectified"], 120 - 40 * 5 / 30)
        self.assertAlmostEqual(r["floor"], 80)


class TestPlacement(unittest.TestCase):
    def test_kendra_panaphara_apoklima(self):
        # Leo lagna. The Sun in its moolatrikona beats Jupiter in its own sign: the 1st, a kendra
        r = A.placement(chart(p0=125.0, p1=125.0, p5=340.0))
        self.assertEqual((r["stronger"], r["class"]), (1, A.LONG))
        # Jupiter in its own Pisces beats the Sun in Virgo: the 8th, a panaphara
        r = A.placement(chart(p0=125.0, p1=155.0, p5=340.0))
        self.assertEqual((r["stronger"], r["class"]), (5, A.MEDIUM))
        # Jupiter exalted in Cancer: the 12th, an apoklima
        r = A.placement(chart(p0=125.0, p1=35.0, p5=95.0))
        self.assertEqual((r["stronger"], r["class"]), (5, A.SHORT))

    def test_the_bhava_not_the_rasi(self):
        # Jupiter exalted in Cancer is the 12th rasi from Leo, but in the 1st bhava of the house system: a kendra
        bhavas = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        r = A.placement(chart(p0=125.0, p1=35.0, p5=95.0, bhavas=bhavas))
        self.assertEqual((r["stronger"], r["house"], r["class"]), (5, 1, A.LONG))

    def test_shadbala_picks_the_stronger_lord(self):
        # the first chart above, but Jupiter stands higher over its minimum: it wins over the Sun's moolatrikona,
        # though the Sun has more virupas
        bala = [0.0, 450.0, 0.0, 0.0, 0.0, 400.0, 0.0, 0.0, 0.0, 0.0]
        percent = [0.0, 150.0, 0.0, 0.0, 0.0, 170.0, 0.0, 0.0, 0.0, 0.0]
        self.assertEqual(A.placement(chart(p0=125.0, p1=125.0, p5=340.0, bala=bala, percent=percent))["stronger"], 5)

    def test_the_lagna_lord_and_the_sun(self):
        # no planet is neutral towards the Sun in the natural table, so medium life never comes from this rule
        self.assertEqual(A.sun_relation(chart(p0=5.0))["class"], A.LONG)       # Mars: friend
        self.assertEqual(A.sun_relation(chart(p0=65.0))["class"], A.LONG)      # Mercury: friend
        self.assertEqual(A.sun_relation(chart(p0=35.0))["class"], A.SHORT)     # Venus: enemy
        self.assertEqual(A.sun_relation(chart(p0=275.0))["class"], A.SHORT)    # Saturn: enemy
        self.assertIsNone(A.sun_relation(chart(p0=125.0))["class"])            # the Sun itself


class TestMarakas(unittest.TestCase):
    def test_lords_and_malefics_of_the_2nd_and_7th(self):
        # Virgo lagna: the 2nd Libra's lord Venus, the 7th Pisces's lord Jupiter
        n = chart(p3=190.0)
        why = A.marakas(n)
        self.assertIn("Lord of the 2nd (44.3)", why[6])
        self.assertIn("Lord of the 7th (44.3)", why[5])
        self.assertIn("Malefic in the 2nd (44.3)", why[3])

    def test_rahu_ketu_as_marakas(self):
        # Scorpio lagna: Rahu is a maraka by lagna; Rahu in the 8th (Gemini) also
        n = chart(p0=215.0, p8=70.0, p9=250.0, p3=10.0)
        why = A.marakas(n)
        self.assertTrue(any("Scorpio or Capricorn lagna" in t for t in why[8]))
        self.assertTrue(any("Node in the 8th" in t for t in why[8]))

    def test_exclusive_malefic(self):
        # Aries lagna: Mercury owns only the 3rd and 6th, Jupiter the 9th and 12th; a malefic with no benefic on it no longer counts by itself
        why = A.marakas(chart(p0=5.0, p7=280.0, p5=125.0, p6=125.0, p4=125.0, p2=125.0))
        self.assertIn("Exclusive malefic (44.6-7)", why[4])
        self.assertNotIn("Exclusive malefic (44.6-7)", why.get(5, []))
        self.assertNotIn("Exclusive malefic (44.6-7)", why.get(7, []))

    def test_rahu_in_the_6th_troubles_but_does_not_kill(self):
        # Virgo lagna, Rahu in Aquarius (the 6th), no benefic on it: 44.22-24 gives difficulties, not death
        why = A.marakas(chart(p8=310.0, p9=130.0))
        self.assertFalse(any("dusthana" in t for t in why.get(8, [])))

    def test_prime_and_other_marakas(self):
        self.assertTrue(A.prime(["Lord of the 2nd (44.3)"]))
        self.assertTrue(A.prime(["Node in the 12th (44.22-24)", "Lord of the 6th (44.15-21)"]))
        self.assertFalse(A.prime(["Lord of the 8th (44.6)", "Exclusive malefic (44.6-7)"]))

    def test_stars_count_from_the_birth_star(self):
        stars = A.maraka_stars(0.0)     # Aswini, lord Ketu
        self.assertEqual([(x["star"], x["lord"]) for x in stars], [(2, "Sun"), (4, "Mars"), (6, "Jupiter"), (22, "Mars")])

    def test_death_circumstances_from_the_3rd_and_8th(self):
        # Virgo lagna: a strong Sun in the 3rd (Scorpio) → king; Mars in the 8th (Aries) → weapons
        strong_sun = [0.0, 120.0] + [0.0] * 8
        d = A.death_circumstances(chart(p1=220.0, p3=10.0, p2=70.0, p5=160.0, p6=160.0, p4=160.0, p7=160.0, p8=250.0, p9=70.0, percent=strong_sun))
        self.assertTrue(any("King" in m for m in d["manners"]))
        self.assertTrue(any("Weapons" in m for m in d["manners"]))
        self.assertIn("Own home", d["place"])  # Scorpio is fixed
        self.assertIn("Unconsciousness", d["consciousness"])     # the Sun, not Jupiter or Venus, in the 3rd
        # the same Sun without strength, and Mars aspecting the 3rd from Taurus, give no manner: they must occupy it
        d = A.death_circumstances(chart(p1=220.0, p3=40.0, p2=70.0, p5=160.0, p6=160.0, p4=160.0, p7=160.0, p8=250.0, p9=70.0))
        self.assertFalse(any("King" in m or "Wounds" in m for m in d["manners"]))

    def test_an_empty_3rd_gives_no_consciousness_reading(self):
        d = A.death_circumstances(chart(p1=40.0, p2=70.0, p3=100.0, p4=130.0, p5=160.0, p6=190.0, p7=250.0, p8=250.0, p9=70.0))
        self.assertIn("No reading", d["consciousness"])

    def test_the_9th_lord_must_be_yuti_for_a_shrine(self):
        # Virgo lagna, Jupiter in the 8th (Aries); the 9th lord Venus in Taurus, aspected by Mercury from Scorpio but with no benefic
        alone = A.death_circumstances(chart(p5=10.0, p6=40.0, p4=220.0))
        self.assertNotIn("Shrine (", alone["shrine_8th"])
        joined = A.death_circumstances(chart(p5=10.0, p6=40.0, p4=40.0))     # Mercury, a benefic, with Venus
        self.assertIn("Shrine (", joined["shrine_8th"])


class TestRules(unittest.TestCase):
    def present(self, table, n):
        return {x["verse"] for x in A.rules(n, table) if x["present"]}

    def test_limitless_life(self):
        # 43.55: Cancer lagna with Jupiter and the Moon, Venus and Mercury in kendras, the rest in the 3rd, 6th, 11th
        n = chart(p0=95.0, p5=95.0, p2=100.0, p6=185.0, p4=185.0, p1=155.0, p3=245.0, p7=35.0, p8=0.0, p9=180.0)
        self.assertIn("43.55", self.present(A.LONG_LIFE, n))

    def test_a_retrograde_benefic_in_a_dusthana(self):
        # 9.4: Jupiter in the 8th (Aries), Mars in Libra aspecting it; Virgo lagna empty of benefics
        retro = [False] * 10
        retro[5] = True
        lons = dict(p5=5.0, p3=190.0, p2=250.0, p1=280.0, p4=70.0, p6=70.0)
        self.assertIn("9.4", self.present(A.BALARISHTA, chart(retro=retro, **lons)))
        self.assertNotIn("9.4", self.present(A.BALARISHTA, chart(**lons)))

    def test_saturn_moon_and_mars_placed(self):
        # 9.8: Saturn in the 10th, the Moon in the 6th, Mars in the 7th, from Virgo
        n = chart(p7=70.0, p2=310.0, p3=340.0)
        self.assertIn("9.8", self.present(A.BALARISHTA, n))

    def test_short_life_with_the_lagna_lord_in_a_dusthana(self):
        # 43.75: Virgo lagna, Mercury in the 8th (Aries) with Mars; no benefic on it: keep Venus, Jupiter and the Moon off
        n = chart(p4=5.0, p3=6.0, p2=250.0, p1=280.0, p5=70.0, p6=70.0, p7=220.0, p8=130.0, p9=310.0)
        self.assertIn("43.75", self.present(A.SHORT_LIFE, n))

    def test_short_life_by_mars_and_saturn_unless_a_benefic_relieves(self):
        # 43.74: Virgo lagna, the 8th lord Mars in Scorpio with Saturn; Jupiter there too relieves them (as 43.75-77)
        self.assertIn("43.74", self.present(A.SHORT_LIFE, chart(p3=220.0, p7=222.0)))
        self.assertNotIn("43.74", self.present(A.SHORT_LIFE, chart(p3=220.0, p7=222.0, p5=221.0)))
        # by the deeptamsas Jupiter 15 deg off Mars is not with him (Ma 8, Ju 9: within 8.5), so no relief
        self.assertIn("43.74", self.present(A.SHORT_LIFE, chart(p3=220.0, p7=222.0, p5=235.0, orbs=True)))

    def test_yuti_and_drishti_within_the_deeptamsas(self):
        n = chart(p3=10.0, p7=25.0)
        self.assertTrue(n.joins(7, 3))                                      # same rasi
        self.assertFalse(chart(p3=10.0, p7=25.0, orbs=True).joins(7, 3))    # 15 deg apart, Ma 8 and Sa 9 allow 8.5
        self.assertTrue(chart(p3=28.0, p7=33.0, orbs=True).joins(7, 3))     # across the sign's edge
        self.assertTrue(chart(p7=0.0, p5=62.0, orbs=True).sees(7, 5))       # Saturn's 3rd, 2 deg off 60
        self.assertFalse(chart(p7=0.0, p5=75.0, orbs=True).sees(7, 5))      # in the 3rd rasi, 15 deg off
        self.assertTrue(chart(p7=0.0, p5=75.0).sees(7, 5))
        self.assertFalse(chart(p9=0.0, p5=180.0, orbs=True).sees(9, 5))     # Ketu has no drishti
        self.assertFalse(chart(p1=0.0, p3=10.0, orbs=True).joins(1, 3))     # Su 15, Ma 8: the smaller, 8, not their mean 11.5

    def test_drishti_on_a_bhava_lands_on_its_cusp(self):
        cusps = [(150.0 + 30.0 * i) % 360.0 for i in range(12)]
        cusps[2] = 230.0                                                    # the 3rd's cusp at 20 Scorpio
        n = chart(p7=50.0, orbs=True, cusps=cusps)                          # Saturn at 20 Taurus: its 7th, 180 deg, on the cusp
        self.assertTrue(n.sees_house(7, 3))
        self.assertFalse(chart(p7=35.0, orbs=True, cusps=cusps).sees_house(7, 3))   # 15 deg off, past Saturn's 9
        self.assertTrue(chart(p7=35.0, cusps=cusps).sees_house(7, 3))       # by rasi, Taurus aspects Scorpio

    def test_antidote_a_benefic_in_a_kendra(self):
        self.assertIn("10.2", self.present(A.ANTIDOTES, chart(p5=250.0)))
        self.assertNotIn("10.2", self.present(A.ANTIDOTES, chart(p4=40.0, p5=40.0, p6=40.0)))

    def test_every_rule_runs_with_a_node_as_lord(self):
        # Scorpio lagna: its co-lord rule gives Mars or, with Mars in the sign and Ketu out of it, Ketu
        n = chart(p0=215.0, p9=216.0, p8=36.0, p3=10.0)
        self.assertEqual(n.lord(1), 3)
        for table in (A.LONG_LIFE, A.SHORT_LIFE, A.BALARISHTA, A.ANTIDOTES):
            A.rules(n, table)
        n = chart(p0=215.0, p3=216.0, p9=36.0, p8=216.0)
        self.assertEqual(n.lord(1), 9)
        for table in (A.LONG_LIFE, A.SHORT_LIFE, A.BALARISHTA, A.ANTIDOTES):
            A.rules(n, table)
        A.three_pairs(n)
        A.sun_relation(n)
        A.marakas(n)


if __name__ == "__main__":
    unittest.main()
