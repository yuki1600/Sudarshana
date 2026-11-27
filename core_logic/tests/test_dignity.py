"""BPHS's dignities by degree: a moolatrikona sign is moolatrikona, exalted or own by the degree, never two at once."""
import unittest

from core_logic.natal_chart import get_graha_dignity as dignity


class TestDignity(unittest.TestCase):
    def test_moolatrikona_signs_split_by_degree(self):
        cases = {("Venus", 187): "Moolatrikona", ("Venus", 200): "Own Sign",          # Libra 0-15 / 15-30
                 ("Mercury", 160): "Exalted", ("Mercury", 167): "Moolatrikona", ("Mercury", 175): "Own Sign",   # Virgo 0-15 / 15-20 / 20-30
                 ("Moon", 32): "Exalted", ("Moon", 40): "Moolatrikona",               # Taurus 0-3 / 3-30
                 ("Sun", 125): "Moolatrikona", ("Sun", 145): "Own Sign",              # Leo 0-20 / 20-30
                 ("Mars", 5): "Moolatrikona", ("Mars", 20): "Own Sign", ("Mars", 215): "Own Sign",
                 ("Jupiter", 245): "Moolatrikona", ("Jupiter", 260): "Own Sign", ("Saturn", 305): "Moolatrikona", ("Saturn", 325): "Own Sign",
                 ("Jupiter", 100): "Exalted", ("Saturn", 6 * 30 + 1): "Exalted", ("Venus", 10 * 30): "General Sign"}
        for (p, lon), want in cases.items():
            self.assertEqual(dignity(p, lon), want, (p, lon))


if __name__ == "__main__":
    unittest.main()
