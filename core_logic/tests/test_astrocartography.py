"""The map's curves against the engine: a relocated chart must have the angle the curve says it has."""
import math
import unittest

from core_logic import astrocartography as A, ephemeris as E

MOMENTS = [(1990, 6, 15, 10.5, 5.5, 77.2, 28.6), (1869, 10, 2, 7.75, 4.8, 69.6, 21.6), (2024, 1, 1, 0.0, -5.0, -74.0, 40.7)]


def off(a, b):
    return abs((a - b + 180.0) % 360.0 - 180.0)


def lon_at(curve, lat):
    (x0, y0), (x1, y1) = next(pair for pair in zip(curve, curve[1:]) if pair[1][1] >= lat)
    return x0 + (x1 - x0) * (lat - y0) / (y1 - y0)


def inside(polygon, lon, lat):
    crossings = 0
    for (x0, y0), (x1, y1) in zip(polygon, polygon[1:] + polygon[:1]):
        if (y0 > lat) != (y1 > lat) and lon < x0 + (lat - y0) / (y1 - y0) * (x1 - x0):
            crossings += 1
    return crossings % 2 == 1


class TestAstrocartography(unittest.TestCase):
    def setUp(self):
        self.moments = [E.BirthData(*m).jd_ut for m in MOMENTS]

    def test_sign_curves_have_that_lagna(self):
        for jd in self.moments:
            f = A.frame(jd)
            for i, curve in enumerate(A.bands([30.0 * i for i in range(12)], f)):
                for lon, lat in curve[1:-1]:    # at the very ends rising meets setting, so the Lagna may be either point
                    self.assertLess(off(E.house_cusps(jd, lat, lon, "RASI")["ascendant"], 30.0 * i), 1e-3, (i, lat))

    def test_graha_lines_have_that_graha_on_the_angle(self):
        for jd in self.moments:
            f = A.frame(jd)
            for p in E.planet_positions(jd).values():
                x = p["lon"]
                for lon, lat in A.lagna_curve(x, f)[1:-1]:
                    self.assertLess(off(E.house_cusps(jd, lat, lon, "RASI")["ascendant"], x), 1e-3)
                for lon, lat in A.lagna_curve(x + 180.0, f)[1:-1]:
                    self.assertLess(off(E.house_cusps(jd, lat, lon, "RASI")["ascendant"] + 180.0, x), 1e-3)
                for lat in (-80, -30, 0, 45, 80):
                    self.assertLess(off(E.house_cusps(jd, lat, A.meridian_lon(x, f), "RASI")["mc"], x), 1e-3)
                    self.assertLess(off(E.house_cusps(jd, lat, A.meridian_lon(x + 180.0, f), "RASI")["mc"] + 180.0, x), 1e-3)

    def test_rising_and_setting_join_at_the_ends_of_the_curve(self):
        f = A.frame(self.moments[0])
        for x in (0.0, 47.0, 200.0):
            rising, setting = A.lagna_curve(x, f), A.lagna_curve(x + 180.0, f)
            for end in (0, -1):
                self.assertAlmostEqual(off(rising[end][0], setting[end][0]), 0.0)
                self.assertAlmostEqual(rising[end][1], setting[end][1])

    def test_bands_never_cross_below_the_polar_circles_and_close_the_circle(self):
        for jd in self.moments:
            curves = A.bands([30.0 * i for i in range(12)], A.frame(jd))
            for lat in range(-66, 67, 6):
                lons = [lon_at(c, lat) for c in curves]
                self.assertTrue(all(a < b for a, b in zip(lons, lons[1:])), lat)
                self.assertAlmostEqual(lons[12], lons[0] + 360.0)

    def test_every_place_lies_in_the_band_of_its_lagna(self):
        for jd in self.moments:
            f = A.frame(jd)
            lons = [30.0 * i for i in range(12)]
            areas = A.band_areas(lons, f, A.bands(lons, f))
            for lat in (-88, -80, -72, -66, -40, 0, 30, 66, 72, 80, 88):
                for lon in range(-180, 180, 20):
                    asc = E.house_cusps(jd, lat, lon, "RASI")["ascendant"]
                    if min(asc % 30.0, 30.0 - asc % 30.0) < 1.0:
                        continue
                    held = [i for i, a in enumerate(areas) for k in range(-3, 4) if inside(a, lon + 360.0 * k, lat)]
                    self.assertEqual(held, [int(asc // 30.0)], (lat, lon))

    def test_every_lagna_circle_passes_through_the_ecliptic_poles(self):
        f = A.frame(self.moments[0])
        for pole_lon, pole_lat in A.ecliptic_poles(f):
            self.assertAlmostEqual(abs(pole_lat), 90.0 - f.obliquity)
            for x in range(0, 180, 30):
                circle = [*A.lagna_curve(x, f, 1), *A.lagna_curve(x + 180.0, f, 1)]
                self.assertLess(min(off(lon, pole_lon) * math.cos(math.radians(lat)) + abs(lat - pole_lat) for lon, lat in circle), 2.0, x)



if __name__ == "__main__":
    unittest.main()
