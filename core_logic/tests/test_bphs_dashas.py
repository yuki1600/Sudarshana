import unittest
from datetime import datetime

from core_logic.dashas import chara_sign_years, compute_chara_dasa


class TestBphsDashas(unittest.TestCase):
    SIGNS = {"Sun": 4, "Moon": 1, "Mars": 9, "Mercury": 5, "Jupiter": 3, "Venus": 11, "Saturn": 6}

    def test_chara_refactor_is_behaviour_preserving(self):
        tl = compute_chara_dasa(0, self.SIGNS, datetime(2000, 1, 1))
        self.assertEqual([p["duration_years"] for p in tl], [chara_sign_years(p["sign_index"], self.SIGNS) for p in tl])
        self.assertEqual(len(tl), 12)


if __name__ == "__main__":
    unittest.main()
