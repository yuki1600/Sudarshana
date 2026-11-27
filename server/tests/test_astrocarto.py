"""The map's bhava bands against /api/houses for the relocated chart."""
import unittest

from fastapi.testclient import TestClient

from server.app import app

client = TestClient(app)
BIRTH = {"year": 1990, "month": 6, "day": 15, "hour_local": 10.5, "tz_east_hours": 5.5, "longitude_east": 77.2, "latitude": 28.6}
ORDINAL = lambda h: {1: "1st", 2: "2nd", 3: "3rd"}.get(h, "%dth" % h)


def post(url, birth=BIRTH, **body):
    r = client.post(url, json={"birth": birth, **body})
    assert r.status_code == 200, r.text
    return r.json()


def house_with(rows, label):
    return next(r["house"] for r in rows if label in r["occupants"])


def wrap(lon):
    return (lon + 180.0) % 360.0 - 180.0


def lon_at(curve, lat):
    (x0, y0), (x1, y1) = next(pair for pair in zip(curve, curve[1:]) if pair[1][1] >= lat)
    return x0 + (x1 - x0) * (lat - y0) / (y1 - y0)


class TestAstrocartography(unittest.TestCase):
    def test_shape(self):
        m = post("/api/astrocartography")
        self.assertEqual(len(m["signs"]), 13)
        self.assertEqual(len(m["lines"]), 36)
        self.assertIsNone(m["bhavas"])
        self.assertEqual(len(m["poles"]), 2)
        self.assertEqual([b["area"] is None for b in m["signs"]], [False] * 12 + [True])

    def test_birth_place_lies_in_the_band_of_its_lagna_sign(self):
        m = post("/api/astrocartography")
        sign = post("/api/chart")["lagna_sign"]
        for shift in (-360, 0, 360):
            for a, b in zip(m["signs"], m["signs"][1:]):
                if lon_at(a["curve"], 28.6) + shift <= 77.2 < lon_at(b["curve"], 28.6) + shift:
                    self.assertEqual(a["sign"], sign)
                    return
        self.fail("no band holds the birth place")

    def test_graha_zones_are_its_equal_houses(self):
        for middle in (True, False):
            settings = {"house_type": 1, "house_cusp_in_middle": middle}
            m = post("/api/astrocartography", settings=settings, bhava_of="Jupiter")
            self.assertEqual([b["house"] for b in m["bhavas"]], [*range(12, 0, -1), 12])
            for band, border in zip(m["bhavas"], m["bhavas"][1:]):
                for row in (20, 45, 65):    # 50 S to 40 N; right by the ecliptic poles half a degree crosses several bands
                    lon, lat = border["curve"][row]
                    for east, h in ((-0.5, band["house"]), (0.5, border["house"])):
                        rows = post("/api/houses", {**BIRTH, "longitude_east": wrap(lon + east), "latitude": lat}, settings=settings)
                        self.assertEqual(house_with(rows, "Ju"), ORDINAL(h), (middle, band["house"], lat))

    def test_graha_zones_in_a_chosen_system_are_its_houses_there(self):
        for t, rows in ((0, (20, 45, 65)), (2, (20, 45, 65)), (4, (22, 37, 52)), (6, (22, 37, 52))):    # a quadrant system's rows run 64 S to 64 N
            settings = {"house_type": t, "house_cusp_in_middle": True}
            m = post("/api/astrocartography", settings={"house_cusp_in_middle": True}, bhava_of="Saturn", bhava_system=t)
            self.assertEqual([b["house"] for b in m["bhavas"]], [*range(12, 0, -1), 12])
            for band, border in zip(m["bhavas"], m["bhavas"][1:]):
                for row in rows:
                    lon, lat = border["curve"][row]
                    for east, h in ((-0.5, band["house"]), (0.5, border["house"])):
                        rel = post("/api/houses", {**BIRTH, "longitude_east": wrap(lon + east), "latitude": lat}, settings=settings)
                        self.assertEqual(house_with(rel, "Sa"), ORDINAL(h), (t, band["house"], lat))

    def test_lagna_zones_in_a_chosen_system_are_the_natal_bhavas(self):
        settings = {"house_type": 4, "house_cusp_in_middle": False}
        m = post("/api/astrocartography", settings={"house_cusp_in_middle": False}, bhava_of="Lagna", bhava_system=4)
        natal = post("/api/houses", settings=settings)
        for band, border in zip(m["bhavas"], m["bhavas"][1:]):
            lon, lat = border["curve"][45]
            lagna = post("/api/chart", {**BIRTH, "longitude_east": wrap(lon + 0.5), "latitude": lat})["lagna_lon"]
            s = natal[border["house"] - 1]
            self.assertLessEqual((lagna - s["start"]) % 360.0, (s["end"] - s["start"]) % 360.0, border["house"])

    def test_lagna_zones_are_the_natal_sripati_bhavas(self):
        for middle in (True, False):
            settings = {"house_type": 3, "house_cusp_in_middle": middle}
            m = post("/api/astrocartography", settings=settings, bhava_of="Lagna")
            natal = post("/api/houses", settings=settings)
            self.assertEqual([b["house"] for b in m["bhavas"]], [*range(1, 13), 1])
            for band, border in zip(m["bhavas"], m["bhavas"][1:]):
                for row in (20, 45, 65):    # 50 S to 40 N; right by the ecliptic poles half a degree crosses several bands
                    lon, lat = border["curve"][row]
                    for east, h in ((-0.5, band["house"]), (0.5, border["house"])):
                        lagna = post("/api/chart", {**BIRTH, "longitude_east": wrap(lon + east), "latitude": lat})["lagna_lon"]
                        s = natal[h - 1]
                        self.assertLessEqual((lagna - s["start"]) % 360.0, (s["end"] - s["start"]) % 360.0, (middle, h, lat))

    def test_lagna_cusps_are_the_natal_cusps(self):
        settings = {"house_type": 3, "house_cusp_in_middle": True}
        m = post("/api/astrocartography", settings=settings, bhava_of="Lagna")
        natal = post("/api/houses", settings=settings)
        for band in m["bhavas"][:12]:
            for row in (20, 45, 65, 80):
                lon, lat = band["cusp"][row]
                lagna = post("/api/chart", {**BIRTH, "longitude_east": wrap(lon), "latitude": lat})["lagna_lon"]
                self.assertLess(abs(wrap(lagna - natal[band["house"] - 1]["cusp"])), 1e-3, (band["house"], lat))

    def test_graha_cusps_put_it_on_the_cusp_of_that_house(self):
        settings = {"house_type": 1, "house_cusp_in_middle": True}
        m = post("/api/astrocartography", settings=settings, bhava_of="Jupiter")
        for band in m["bhavas"][:12]:
            lon, lat = band["cusp"][45]
            rows = post("/api/houses", {**BIRTH, "longitude_east": wrap(lon), "latitude": lat}, settings=settings)
            row = rows[band["house"] - 1]
            self.assertEqual(row["house"], ORDINAL(band["house"]))
            self.assertIn("Ju", row["occupants"])
            jupiter = post("/api/chart")["planet_longitudes"]["Jupiter"]
            self.assertLess(abs(wrap(jupiter - row["cusp"])), 1e-3, band["house"])

    def test_with_the_cusp_at_the_start_the_border_is_the_cusp(self):
        for of in ("Lagna", "Moon"):
            m = post("/api/astrocartography", settings={"house_cusp_in_middle": False}, bhava_of=of)
            self.assertFalse(any("cusp" in band for band in m["bhavas"]), of)

    def test_bhavas_ignore_the_house_system_option(self):
        for of in ("Lagna", "Moon"):
            a = post("/api/astrocartography", bhava_of=of)["bhavas"]
            b = post("/api/astrocartography", settings={"house_type": 4}, bhava_of=of)["bhavas"]
            self.assertEqual(a, b)

    def test_tropical_and_ayanamsa_move_the_sign_borders(self):
        a = post("/api/astrocartography")["signs"][0]["curve"][33][0]
        b = post("/api/astrocartography", settings={"ayanamsa": "TROPICAL"})["signs"][0]["curve"][33][0]
        self.assertGreater(abs(wrap(a - b)), 1.0)

    def test_charts_without_a_map_say_so(self):
        for body in ({"settings": {"siddhanta": 1}}, {"settings": {"topocentric": True}}, {"settings": {"apparent_refraction": True}}):
            self.assertEqual(client.post("/api/astrocartography", json={"birth": BIRTH, **body}).status_code, 422, body)
        r = client.post("/api/astrocartography", json={"birth": {**BIRTH, "adjust": {"arc": 1.0}}})
        self.assertEqual(r.status_code, 422)
        self.assertIn("natal chart", r.json()["detail"])

    def test_bad_reference_is_refused(self):
        self.assertEqual(client.post("/api/astrocartography", json={"birth": BIRTH, "bhava_of": "Pluto"}).status_code, 422)


if __name__ == "__main__":
    unittest.main()
