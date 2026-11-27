"""core_logic.deltat: Swiss Ephemeris 2.02's Delta-T table and its extrapolations."""
import unittest

from core_logic import deltat as D


class TestDeltaT(unittest.TestCase):
    def test_values(self):
        jd_1900 = 2415020.5   # 1900-01-01: table value -2.72 s plus the tidal adjustment
        self.assertAlmostEqual(D.deltat_se202(jd_1900) * 86400, -2.72 - 0.000091 * 0.2 * 55 ** 2, places=2)

    def test_outside_the_table(self):
        jd_1610 = 2309100.5 + 0.5 * 365.2425    # Espenak & Meeus: 120 - 0.9808u - 0.01532u^2 + u^3/7129, tidal
        u = 2000 + (jd_1610 - D.J2000) / 365.2425 - 1600
        em = 120 - 0.9808 * u - 0.01532 * u * u + u ** 3 / 7129 - 0.000091 * 0.2 * (u + 1600 - 1955) ** 2
        self.assertAlmostEqual(D.deltat_se202(jd_1610) * 86400, em, places=6)
        y = 2000 + (2469807.5 - D.J2000) / 365.2425   # 2050: Stephenson 1997 blended from the table's 69.5 s
        st = -20 + 31 * ((y - 1820) / 100) ** 2 + (y - 2119) * (-20 + 31 * 1.99 ** 2 - 69.5) / 100
        self.assertAlmostEqual(D.deltat_se202(2469807.5) * 86400, st, places=6)
        for jd in (2317746.130902778, 2458484.5 + 365.2425):   # continuous at 1633.7 and at the table's end
            self.assertLess(abs(D.deltat_se202(jd - 1e-3) - D.deltat_se202(jd + 1e-3)) * 86400, 2.0)


if __name__ == "__main__":
    unittest.main()
