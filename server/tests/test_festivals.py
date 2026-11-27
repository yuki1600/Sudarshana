"""Festivals by regional calendar: dates for New Delhi in 2025, as Drikpanchang lists them."""
import unittest

from fastapi.testclient import TestClient

from server.app import app

client = TestClient(app)
DELHI = {"year": 2025, "month": 6, "day": 1, "hour_local": 12.0, "tz_east_hours": 5.5, "longitude_east": 77.209,
         "latitude": 28.6139, "altitude_m": 0, "gregorian": True, "place": "Delhi"}
_cache: dict = {}


def items(calendar: str) -> dict:
    if calendar not in _cache:
        r = client.post("/api/festivals", json={"birth": DELHI, "calendar": calendar})
        assert r.status_code == 200, r.text
        _cache[calendar] = {x["id"]: x for x in r.json()["items"]}
    return _cache[calendar]


def dates(calendar: str, fid: str) -> list:
    return [d["date"] for d in items(calendar)[fid]["dates"]]


class Festivals(unittest.TestCase):
    def test_north_by_the_kala_each_needs(self):
        for fid, day in [("maha-shivaratri", "2025-02-26"), ("holika-dahan", "2025-03-13"), ("rama-navami", "2025-04-06"),
                         ("narasimha-jayanti", "2025-05-11"), ("vat-savitri", "2025-05-26"), ("raksha-bandhan", "2025-08-09"),
                         ("ganesh-chaturthi", "2025-08-27"), ("vijaya-dashami", "2025-10-02"),
                         ("karva-chauth", "2025-10-10"), ("diwali", "2025-10-20"), ("bhai-dooj", "2025-10-23"), ("lohri", "2025-01-13")]:
            self.assertEqual(dates("north", fid), [day], fid)

    def test_diwali_differs_by_calendar(self):
        tamil = items("tamil")["deepavali"]
        self.assertEqual(dates("tamil", "deepavali"), ["2025-10-20"])
        self.assertEqual(dates("bengali", "kali-puja"), ["2025-10-20"])
        self.assertIn("Diwali (Lakshmi Puja)", [e["name"] for e in tamil["elsewhere"]])

    def test_solar_calendars_begin_their_months_by_their_own_rule(self):
        # Mesha Sankranti 14 Apr 2025, 03:30 IST: Tamil and Kerala that day (before sunrise), Bengal two days on (past midnight)
        self.assertEqual(dates("tamil", "puthandu"), ["2025-04-14"])
        self.assertEqual(dates("kerala", "vishu"), ["2025-04-14"])
        self.assertEqual(dates("bengali", "poila-baishakh"), ["2025-04-15"])
        self.assertEqual(dates("kerala", "onam"), ["2025-09-05"])
        self.assertEqual(dates("tamil", "thai-pusam"), ["2025-02-11"])

    def test_ekadasis_smarta_and_vaishnava(self):
        self.assertEqual(dates("north", "ekadasi-devshayani"), ["2025-07-06"])
        self.assertEqual(dates("tamil", "vaikunta-ekadasi"), ["2025-01-10", "2025-12-30"])
        # Vaishnava: Dashami at Arunodaya on 30 Dec moves the fast to the 31st
        self.assertEqual(dates("srivaishnava", "vaikunta-ekadasi"), ["2025-01-10", "2025-12-31"])
        self.assertIn("parana", items("srivaishnava")["vaikunta-ekadasi"]["dates"][1])
        d = items("north")["ekadasi-devshayani"]["dates"][0]
        self.assertTrue(d["parana"]["from"].startswith("2025-07-07"), d)
        self.assertLessEqual(d["parana"]["hari_vasara_end"], d["parana"]["from"])
        self.assertIn("kshaya", items("north")["ekadasi-devshayani"]["note"])

    def test_every_day_has_its_sunrise_tithi_and_month(self):
        days = client.post("/api/festivals", json={"birth": DELHI, "calendar": "north"}).json()["days"]
        self.assertEqual(len(days), 365)
        self.assertEqual(days["2025-07-06"], {"tithi": "Shukla Ekadashi", "masa": "Ashadha"})
        self.assertEqual(days["2025-10-20"]["tithi"], "Krishna Chaturdashi")

    def test_pitru_paksha_and_sri_vaishnava_thirunakshatrams(self):
        self.assertEqual(dates("north", "pitru-0"), ["2025-09-07"])
        self.assertEqual(items("north")["pitru-15"]["name"], "Sarva Pitru Amavasya")
        self.assertEqual(dates("srivaishnava", "pitru-15"), ["2025-09-21"])
        self.assertEqual(dates("srivaishnava", "ramanuja"), ["2025-05-02"])
        self.assertEqual(dates("srivaishnava", "sri-jayanti"), ["2025-09-14"])

    def test_unknown_calendar_is_refused(self):
        self.assertEqual(client.post("/api/festivals", json={"birth": DELHI, "calendar": "martian"}).status_code, 422)
        self.assertEqual(len(client.get("/api/festivals/calendars").json()), 9)

    def test_polar_night_and_midnight_sun(self):
        # at 78 N the Moon goes days without rising: a festival kept at moonrise falls back to its tithi's day, no crash
        for month, hour in ((12, 12.0), (6, 0.5)):
            polar = {"year": 2020, "month": month, "day": 21, "hour_local": hour, "tz_east_hours": 1.0, "longitude_east": 15.65, "latitude": 78.22}
            r = client.post("/api/festivals", json={"birth": polar, "calendar": "north"})
            self.assertEqual(r.status_code, 200, month)
            self.assertTrue(r.json()["items"], month)


if __name__ == "__main__":
    unittest.main()
