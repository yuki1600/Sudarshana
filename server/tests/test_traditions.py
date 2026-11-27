"""The Traditions tab's route (server/traditions.py, native/traditions): each sub tab for the sample charts, with checks
anyone can make by hand. Skipped without the native module (./start.sh builds it)."""
import unittest
from dataclasses import replace

from fastapi.testclient import TestClient

from core_logic import ephemeris as E
from server import settings as S, traditions as TD
from server.app import main
import os

client = TestClient(main.app)
CHART = "Mahatma Gandhi"
SAMPLES = os.path.join(os.path.dirname(__file__), "..", "..", "data", "sample_charts")


def birth(name):
    with open(os.path.join(SAMPLES, name + ".jhd"), encoding="utf-8", errors="replace") as f:
        return client.post("/api/jhd/parse", json={"content": f.read()}).json()["birth"]


def part(name, **extra):
    return client.post("/api/traditions", json={"birth": birth(name), **extra})


@unittest.skipUnless(TD.T is not None, "native/traditions is not built")
class TestTraditions(unittest.TestCase):
    def test_every_part(self):
        for p in TD.PARTS:
            r = part(CHART, part=p, person="Mohandas Karamchand Gandhi")
            self.assertEqual(r.status_code, 200, (p, r.text[:200]))

    def test_western(self):
        w = part(CHART, part="western").json()
        self.assertEqual([b["name"] for b in w["bodies"]][:10], TD.WESTERN)
        self.assertEqual(len(w["houses"]["cusps"]), 12)
        self.assertEqual(len(w["lots"]), 97)
        # XALEN's Placidus against the Swiss Ephemeris' at the same moment (its houses use mean sidereal time: under 0.01 degree)
        b = birth(CHART)
        jd = E.julian_day_ut(b["year"], b["month"], b["day"], b["hour_local"] - b["tz_east_hours"])
        sw = E._require_swe().houses(jd, b["latitude"], b["longitude_east"], b"P")
        self.assertLess(abs((w["houses"]["ascendant"] - sw[1][0] + 180) % 360 - 180), 0.01)
        # the Sun's tropical longitude is the app's own (Swiss Ephemeris, DE442), under the request's settings
        sun = E.planet_positions(jd, replace(S.config(S.SettingsIn()), ayanamsa="TROPICAL"))["Sun"]["lon"]
        self.assertAlmostEqual(w["bodies"][0]["lon"], sun, places=6)
        self.assertEqual(part(CHART, part="western", house_system="nope").status_code, 422)

    def test_chinese(self):
        c = part(CHART, part="chinese").json()
        # Gandhi, 2 October 1869: the year Ji Si (己巳) and the month Gui You (癸酉), as published BaZi give it
        self.assertEqual((c["bazi"]["year"]["stem"], c["bazi"]["year"]["branch"]), ("Ji", "Si"))
        self.assertEqual((c["bazi"]["month"]["stem"], c["bazi"]["month"]["branch"]), ("Gui", "You"))
        self.assertEqual(c["lunar_date"]["month"], 8)
        self.assertEqual(len(c["ziwei"]["chart"]["palaces"]), 12)

    def test_the_rest(self):
        w = part(CHART, part="world").json()
        self.assertIn(w["almuten"], ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"])
        self.assertEqual(sum(p["years"] for p in w["persian"]), 129)
        i = part(CHART, part="iching").json()
        self.assertTrue(1 <= i["primary"]["hexagram"]["number"] <= 64)
        n = part(CHART, part="numerology", person="Mohandas Karamchand Gandhi").json()
        self.assertEqual(n["numbers"][0], {"name": "Life path", "number": 9, "meaning": None, "karmic_debt": False})   # 2+10+1869 -> 2+1+6 -> 9
        lk = part(CHART, part="lalkitab").json()
        self.assertEqual(len(lk["planets"]), 9)
        self.assertEqual(sum(len(h) for h in lk["chart"]["placements"]), 9)


if __name__ == "__main__":
    unittest.main()
