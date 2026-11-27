"""Timeline tab: a calendar year of the sky."""
import unittest

from fastapi.testclient import TestClient

from core_logic import ephemeris as E
from server import timeline as TL
from server.app import app

client = TestClient(app)
BIRTH = {"year": 2026, "month": 1, "day": 1, "hour_local": 12.0, "tz_east_hours": 5.5,
         "longitude_east": 76.64, "latitude": 12.3, "altitude_m": 0, "gregorian": True, "place": "Mysuru"}


class Timeline(unittest.TestCase):
    def test_samvatsara_names_north_indian_years(self):
        # the year running at Mesha Sankranti names Vikram Samvat 2080..2083
        for y, name in ((2023, "Nala"), (2024, "Pingala"), (2025, "Kaala-yukta"), (2026, "Siddarthi")):
            j = E.julian_day_ut(y, 4, 15, 0.0)
            self.assertEqual(TL.samvatsaras(j, j + 1, 5.5)[0]["name"], name)

    def test_gandanta_zones(self):
        self.assertTrue(TL.in_gandanta(358.0) and TL.in_gandanta(2.0) and TL.in_gandanta(118.0) and TL.in_gandanta(242.0))
        self.assertFalse(TL.in_gandanta(5.0) or TL.in_gandanta(115.0) or TL.in_gandanta(200.0))

    def test_year_2026(self):
        r = client.post("/api/timeline", json={"birth": BIRTH, "year": 2026})
        self.assertEqual(r.status_code, 200, r.text)
        d = r.json()
        self.assertEqual([e["kind"] for e in d["eclipses"]], ["solar", "lunar", "solar", "lunar"])
        self.assertTrue(any(c["bodies"] == ["Saturn", "Neptune"] for c in d["conjunctions"]))
        self.assertTrue(all("Moon" not in c["bodies"] for c in d["conjunctions"]))
        self.assertEqual(len(d["retrograde"]["Mercury"]), 3)
        self.assertEqual((d["eclipses"][2]["type"], d["eclipses"][2]["sign"]), ("total", "Cancer"))     # 12 Aug 2026
        # combustion by the app's fixed-orb rule (6°): Mercury four times, Venus only inside its retrogression
        self.assertEqual(len(d["combustion"]["Mercury"]), 4)
        (v,), (r,) = d["combustion"]["Venus"], d["retrograde"]["Venus"]
        self.assertTrue(r["from"] <= v["from"] and v["to"] <= r["to"])


if __name__ == "__main__":
    unittest.main()
