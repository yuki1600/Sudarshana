"""data/point_names.csv: the names of the 102 points, in Sanskrit and English, long and short."""
import csv
import os
import unittest

CSV = os.path.join(os.path.dirname(__file__), "..", "..", "data", "point_names.csv")


class TestPointNames(unittest.TestCase):
    def test_tables(self):
        with open(CSV, encoding="utf-8", newline="") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), 102)
        self.assertEqual(len(rows[0]), 6)
        self.assertEqual([rows[i]["sanskrit"] for i in (0, 1, 13, 31)], ["Lagna", "Surya", "Bhava Lagna", "Maandi"])
        self.assertEqual([rows[i]["english"] for i in (0, 1, 2)], ["Asc", "Sun", "Moon"])
        self.assertEqual(rows[14]["english_2"], "HL ")  # the trailing space is the column's padding
        self.assertEqual(rows[101]["sanskrit"], "Sani's Aq Arudha")
        self.assertTrue(all(r[c] for r in rows for c in r))


if __name__ == "__main__":
    unittest.main()
