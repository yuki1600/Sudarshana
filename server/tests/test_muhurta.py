"""Muhurta tab: the day's panchang and daily muhurtas, and the lunar calendar."""
import unittest

from fastapi.testclient import TestClient

from core_logic import ephemeris as E
from server import calendars as CAL, muhurta as MU
from server.app import app

client = TestClient(app)
DELHI = {"year": 2026, "month": 11, "day": 5, "hour_local": 12.0, "tz_east_hours": 5.5, "longitude_east": 77.209,
         "latitude": 28.6139, "altitude_m": 0, "gregorian": True, "place": "Delhi"}


def day(**kw):
    r = client.post("/api/muhurta/day", json={"birth": {**DELHI, **kw.pop("birth", {})}, **kw})
    assert r.status_code == 200, r.text
    return r.json()


class MuhurtaDay(unittest.TestCase):
    def test_delhi_5_nov_2026(self):
        d = day()
        # Drikpanchang, New Delhi: Abhijit 11:43-12:26, Rahu Kalam 13:27-14:49 (its sunrise is the upper limb, ours the default definition)
        abhijit = next(a for a in d["auspicious"] if a["name"] == "Abhijit Muhurta")
        self.assertEqual(abhijit["start"][11:16], "11:42")
        rahu = next(a for a in d["avoid"] if a["name"] == "Rahu Kalam")
        self.assertTrue("13:20" <= rahu["start"][11:16] <= "13:30", rahu)
        self.assertEqual(d["tithi"][0]["name"], "Krishna Ekadashi")
        self.assertEqual(d["month"]["amanta"], "Ashwina")
        self.assertEqual(d["month"]["purnimanta"], "Kartika")
        self.assertEqual(d["month"]["vikram"], 2083)

    def test_amanta_names_the_krishna_half_by_the_old_month(self):
        self.assertEqual(day(lunar="amanta")["month"]["name"], "Ashwina")
        self.assertEqual(day(lunar="purnimanta")["month"]["name"], "Kartika")

    def test_the_day_is_covered_without_gaps(self):
        d = day()
        for key in ("tithi", "nakshatra", "yoga", "karana", "moon_sign"):
            rows = d[key]
            self.assertEqual(rows[0]["start"][:10], d["date"], key)
            self.assertIsNone(rows[-1]["end"], key)
            for a, b in zip(rows, rows[1:]):
                self.assertEqual(a["end"], b["start"], key)
        for slots in (d["choghadiya"]["day"], d["choghadiya"]["night"], d["hora"], d["gowri"], d["lagna"]):
            for a, b in zip(slots, slots[1:]):
                self.assertEqual(a["end"], b["start"])
        self.assertEqual(len(d["choghadiya"]["day"]), 8)
        self.assertEqual(len(d["hora"]), 24)

    def test_wednesday_has_no_abhijit(self):
        d = day(birth={"day": 4})                 # Wednesday
        self.assertEqual(d["weekday"], "Wednesday")
        self.assertFalse(any(a["name"] == "Abhijit Muhurta" for a in d["auspicious"]))


class Eras(unittest.TestCase):
    def test_years(self):
        self.assertEqual(CAL.eras(2026, 11, 6), {"vikram": 2083, "shaka": 1948, "gujarati": 2082})   # Ashwina
        self.assertEqual(CAL.eras(2026, 12, 8)["gujarati"], 2083)                                       # after Kartika Shukla 1
        self.assertEqual(CAL.eras(2027, 1, 9)["vikram"], 2083)                                          # Pausha in January
        self.assertEqual(CAL.eras(2026, 3, 11)["vikram"], 2082)                                         # Phalguna, before Chaitra
        self.assertEqual(CAL.eras(2026, 4, 0)["vikram"], 2083)

    def test_adhika_month(self):
        # Adhika Jyeshtha 2026 ran from 17 May to 15 June (Delhi, Amanta)
        cfg = E.EphemerisConfig()
        jd = E.julian_day_ut(2026, 6, 1, 1.0, True)
        m = CAL.lunar_month(jd, 4, cfg, 2026, 6)
        self.assertTrue(m["adhika"], m)
        self.assertEqual(m["amanta"], "Jyeshtha")

    def test_kshaya_month(self):
        # the Amanta month from the new moon of 14 January 1983 holds both the Makara and Kumbha Sankrantis (Lahiri):
        # it is Pausha, Magha is lost, and its dark half is Purnimanta Phalguna, the next month's name
        cfg = E.EphemerisConfig()
        jd = E.julian_day_ut(1983, 2, 5, 1.0, True)
        m = CAL.lunar_month(jd, 20, cfg, 1983, 2)
        self.assertEqual((m["amanta"], m["kshaya"], m["purnimanta"], m["adhika"]), ("Pausha", "Magha", "Phalguna", False), m)
        self.assertEqual(CAL.lunar_month(E.julian_day_ut(2026, 1, 25, 1.0, True), 6, cfg, 2026, 1)["kshaya"], "")


def find(event, natal=None, **birth):
    body = {"birth": {**DELHI, "day": 1, **birth}, "event": event}
    if natal:
        body["natal"] = natal
    r = client.post("/api/muhurta/find", json=body)
    assert r.status_code == 200, r.text
    return r.json()


class FindMuhurta(unittest.TestCase):
    def test_events_listed(self):
        ids = {e["id"] for e in client.get("/api/muhurta/events").json()}
        self.assertTrue({"vivah", "griha_pravesh", "vehicle", "property", "namakarana"} <= ids)

    def test_unknown_event(self):
        r = client.post("/api/muhurta/find", json={"birth": DELHI, "event": "nope"})
        self.assertEqual(r.status_code, 422)

    def test_griha_pravesh_november_2026(self):
        r = find("griha_pravesh")
        self.assertEqual(len(r["days"]), 30)
        for d in r["days"]:
            if d["weekday"] in ("Sunday", "Tuesday"):
                self.assertEqual(d["short"], "Weekday", d)
        # Ashwina (Amanta) is closed to Griha Pravesh; it ends on 9 November 2026
        self.assertEqual(r["days"][4]["short"], "Month closed")
        self.assertGreater(r["good_days"], 0)

    def test_windows_avoid_rahu_and_stay_in_day(self):
        r = find("griha_pravesh")
        for d in r["days"]:
            if not d["windows"]:
                continue
            day_ = client.post("/api/muhurta/day", json={"birth": {**DELHI, "day": int(d["date"][8:])}}).json()
            hard = [a for a in day_["avoid"] if a["name"] in MU.HARD_AVOID]
            for w in d["windows"]:
                self.assertLessEqual(day_["sunrise"], w["start"])
                self.assertLess(w["start"], w["end"])
                for a in hard:
                    self.assertFalse(a["start"] < w["end"] and w["start"] < a["end"], (w, a))
            self.assertEqual(d["best"], max(w["score"] for w in d["windows"]))

    def test_personal_adds_tara_and_chandra(self):
        natal = {**DELHI, "year": 1990, "month": 6, "day": 15, "hour_local": 9.0}
        r = find("vehicle", natal=natal)
        self.assertTrue(r["personal"])
        labels = [x["label"] for d in r["days"] for w in d["windows"] for x in w["reasons"]]
        self.assertTrue(any(x.startswith("Tarabala") for x in labels))
        self.assertTrue(any(x.startswith("Chandrabala") for x in labels))


class Bala(unittest.TestCase):
    def test_tara_and_chandra(self):
        self.assertEqual(MU.tara(0, 0), 0)            # Janma
        self.assertEqual(MU.tara(0, 2), 2)            # Vipat
        self.assertEqual(MU.tara(26, 0), 1)           # Ashwini is Sampat from Revati
        self.assertEqual(MU.chandra_house(0, 7), 8)   # Chandrashtama
        self.assertEqual(MU.chandra_house(11, 0), 2)

    def test_tithis(self):
        rule = {"tithis": [2, 3], "purnima": True}
        self.assertTrue(MU.tithi_allowed(rule, 1))    # Shukla Dvitiya
        self.assertTrue(MU.tithi_allowed(rule, 16))   # Krishna Dvitiya
        self.assertTrue(MU.tithi_allowed(rule, 14))   # Purnima
        self.assertFalse(MU.tithi_allowed(rule, 29))  # Amavasya
        self.assertFalse(MU.tithi_allowed({"tithis": [2], "purnima": False}, 14))

    def test_subtract(self):
        self.assertEqual(MU.subtract([(0, 10)], [(2, 3), (5, 12)]), [(0, 2), (3, 5)])


if __name__ == "__main__":
    unittest.main()
