"""core_logic/chinese_calendar.py against published Chinese lunar dates: new years, leap months (1990's fifth, 2020's
fourth, 2023's second) and a year's last day (Hong Kong Observatory's Gregorian-lunar tables)."""
import unittest

from core_logic import ephemeris as E
from core_logic.chinese_calendar import lunar_date

try:
    import swisseph  # noqa: F401
    HAVE_SWE = True
except ImportError:  # pragma: no cover
    HAVE_SWE = False

KNOWN = [((2024, 2, 10), (2024, 1, 0, 1)), ((2023, 3, 22), (2023, 2, 1, 1)), ((2025, 1, 28), (2024, 12, 0, 29)), ((1990, 6, 15), (1990, 5, 0, 23)),
         ((1990, 7, 1), (1990, 5, 1, 9)), ((2020, 5, 23), (2020, 4, 1, 1)), ((1984, 2, 2), (1984, 1, 0, 1))]


@unittest.skipUnless(HAVE_SWE, "pyswisseph not installed")
class TestChineseCalendar(unittest.TestCase):
    def test_known_dates(self):
        cfg = E.EphemerisConfig()
        for (y, m, d), want in KNOWN:
            r = lunar_date(int(E.julian_day_ut(y, m, d, 12.0) + 0.5), cfg)
            self.assertEqual((r["year"], r["month"], r["leap"], r["day"]), want, (y, m, d))


if __name__ == "__main__":
    unittest.main()
