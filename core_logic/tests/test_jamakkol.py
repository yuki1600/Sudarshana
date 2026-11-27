import unittest

from core_logic import jamakkol as J


class TestJamakkol(unittest.TestCase):
    def test_aarudam_is_five_minutes_a_sign_from_aries(self):
        self.assertAlmostEqual(J.aarudam(10 + 7.5 / 60), 45.0)            # 10:07:30: halfway through Taurus
        self.assertAlmostEqual(J.aarudam(23 + 59 / 60), 354.0)            # 23:59: Pisces 24°
        self.assertAlmostEqual(J.aarudam(6.0), 0.0)

    def test_udayam_goes_round_once_a_day_and_once_a_night(self):
        self.assertAlmostEqual(J.udayam(100.0, 6.0, 18.0, 12.0), 280.0)
        self.assertAlmostEqual(J.udayam(100.0, 18.0, 30.0, 18.0), 100.0)  # at sunset it is back at the Sun
        self.assertAlmostEqual(J.udayam(100.0, -6.0, 6.0, 3.0), 10.0)     # a night that began the evening before

    def test_kavippu_counts_from_udayam_as_far_as_aarudam_is_from_the_veethi(self):
        self.assertEqual([J.veethi(g) for g in range(12)], [1, 0, 0, 0, 0, 1, 1, 2, 2, 2, 2, 1])
        # Sun in Cancer (Mesha veethi), Aarudam Taurus 15°: Taurus to Aries is 12 signs, so the 12th from Udayam in Capricorn
        self.assertAlmostEqual(J.kavippu(100.0, 280.0, 45.0), 255.0)
        self.assertAlmostEqual(J.kavippu(100.0, 280.0, 0.0), 270.0)       # Aarudam on Aries 0°: Kavippu at Udayam's sign, 0°


    # jamakkolprasannam.com's chart for Sunday 22 November 2026, 8:14:57 pm, with the Sun in Scorpio 6°04'
    def test_jama_grahas_as_the_tamil_calculator(self):
        got = [(g, box, round(lon * 60)) for g, box, lon in J.jama_grahas(0, 20 + 14 / 60 + 57 / 3600)]
        want = [("Rahu", 11, 337 * 60 + 31), ("Sun", 9, 292 * 60 + 31), ("Mars", 8, 247 * 60 + 31), ("Jupiter", 6, 202 * 60 + 31),
                ("Mercury", 5, 157 * 60 + 31), ("Venus", 3, 112 * 60 + 31), ("Saturn", 2, 67 * 60 + 31), ("Moon", 0, 22 * 60 + 31)]
        self.assertEqual([(g, b) for g, b, _ in got], [(g, b) for g, b, _ in want])
        for (_, _, a), (_, _, b) in zip(got, want):
            self.assertLessEqual(abs(a - b), 1)
        self.assertEqual(J.jama_grahas(1, 6.0)[0][:2], ("Moon", 11))          # the weekday's lord in Pisces at 6 am
        self.assertEqual(J.jama_grahas(1, 18.0)[0][:2], ("Moon", 11))         # and again at 6 pm

    def test_kalam_points_as_the_tamil_calculator(self):
        got = J.kalam_points(216 + 4 / 60, 0, True)
        self.assertEqual({k: int(x // 30) for k, x in got.items()}, {"Rahu Kalam": 0, "Yamakandam": 5, "Mrithyu": 5, "Maandi": 3})
        self.assertAlmostEqual(got["Mrithyu"] % 30, 18 + 4 / 60)
        self.assertAlmostEqual(got["Rahu Kalam"] % 30, 6 + 4 / 60)

    def test_kavippu_and_aarudam_as_the_tamil_calculator(self):
        ar = J.aarudam(20 + 14 / 60 + 57 / 3600)
        self.assertAlmostEqual(ar, 89.7)                                    # Gemini 29°42'
        self.assertAlmostEqual(J.kavippu(216 + 4 / 60, 288 + 4 / 60, ar), 270.3)   # Capricorn 0°18'


if __name__ == "__main__":
    unittest.main()
