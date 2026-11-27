"""Parashara's nine moods (BPHS 45.8-10) on a hand-built chart."""
import unittest

from core_logic.avasthas import graha_avasthas

# Sun 10 Ar, Moon 10 Cn, Mars 15 Ar, Mercury 10 Vi, Jupiter 10 Sg, Venus 10 Pi, Saturn 20 Li, Rahu 0 Aq, Ketu 0 Le
LONS = [10, 100, 15, 160, 250, 340, 200, 300, 120]


class TestParasharaMoods(unittest.TestCase):
    def test_moods(self):
        burnt = [False, False, True] + [False] * 6       # Mars eclipsed by the Sun
        av = {k: v["parashara_mood_names"] for k, v in graha_avasthas(LONS, 0.0, 0.0, combust=burnt).items()}
        self.assertEqual(av["Moon"], "Swastha (comfortable)")                                          # own sign only
        self.assertEqual(av["Mars"], "Swastha (comfortable), Vikala (crippled), Kopa (angry)")          # own, with the Sun, eclipsed
        self.assertEqual(av["Sun"], "Deepta (glowing), Deena (sad), Vikala (crippled)")                # exalted; Mars natural friend, temporal enemy
        self.assertEqual(av["Venus"], "Deepta (glowing), Saanta (peaceful)")                           # Jupiter neutral, temporal friend: friend
        self.assertEqual(av["Ketu"], "Khala (mischievous)")                                            # the Sun its great enemy
        self.assertFalse(any("Garvita" in v or "Lajjita" in v for v in av.values()))                  # not among Parashara's nine


if __name__ == "__main__":
    unittest.main()
