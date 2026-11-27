import random
import unittest

from core_logic.kp_astrology import get_kp_sub_levels, get_kp_sub_lords


class TestKpLevels(unittest.TestCase):
    def test_first_two_levels_agree_with_existing_engine(self):
        rng = random.Random(7)
        for _ in range(500):
            lon = rng.uniform(0, 360)
            a, b = get_kp_sub_levels(lon, 2), get_kp_sub_lords(lon)
            self.assertEqual(a["star_lord"], b["star_lord"])
            self.assertEqual(a["sub_lord"], b["sub_lord"], lon)
            self.assertEqual(a["prati_sub_lord"], b["sub_sub_lord"], lon)

    def test_five_levels_present_and_valid(self):
        r = get_kp_sub_levels(123.456)
        self.assertEqual(set(r) - {"longitude", "star_lord"},
                         {"sub_lord", "prati_sub_lord", "sookshma_sub_lord", "praana_sub_lord", "deha_sub_lord"})
        # start of Ashwini: Ketu all the way down
        z = get_kp_sub_levels(0.0)
        self.assertTrue(all(v == "Ketu" for k, v in z.items() if k.endswith("lord")))


if __name__ == "__main__":
    unittest.main()
