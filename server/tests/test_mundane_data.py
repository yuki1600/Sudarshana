"""Mundane tab databases: every record is castable, and the pattern factors are right for a known chart."""
import unittest

from fastapi.testclient import TestClient

from server import mundane_data as MD
from server.app import app

client = TestClient(app)


class Records(unittest.TestCase):
    def test_every_record_is_castable(self):
        seen = set()
        for name in MD.SETS:
            recs = MD.dataset(name)["records"]
            self.assertTrue(recs, name)
            for r in recs:
                self.assertEqual(MD.sanity(name, r), [], (name, r.get("id")))
                self.assertNotIn(r["id"], seen, "duplicate id")
                seen.add(r["id"])
                if r.get("date"):   # only a company may have none (a startup whose founding day is unknown)
                    MD.birth_of(r).jd_ut   # casts without error

    def test_only_accurate_records_are_kept(self):
        for name in MD.SETS:
            d, raw = MD.dataset(name), MD.raw_dataset(name)
            moments = MD.quake_moments(raw)
            self.assertEqual([r["id"] for r in d["records"] if MD.dropped(r, moments)], [], name)
            self.assertEqual(len(d["records"]) + sum(d["removed"].values()), len(raw), name)
        self.assertEqual(MD.dropped({"id": "ts1", "date": "2004-12-26", "time": "00:58:53", "time_confidence": "exact", "place": "Sumatra"},
                                    frozenset({("2004-12-26", "00:58")})), "same as an earthquake")
        oath = {"id": "el-us-2025-01-20-president", "date": "2025-01-20", "time": "12:00", "time_confidence": "reported", "place": "Capitol", "oath_known": True}
        self.assertIsNone(MD.dropped(oath))
        self.assertEqual(MD.dropped({**oath, "id": "ea1"}), "time not exact")
        winners = {(r["iso2"], r["winner"]) for r in MD.dataset("elections")["records"]}
        self.assertTrue({("US", "Donald Trump"), ("IN", "Narendra Modi"), ("IN", "Manmohan Singh")} <= winners)

    def test_nations_have_one_primary_each(self):
        nations = MD.dataset("nations")["records"]
        by = {}
        for r in nations:
            by.setdefault(r["iso2"], []).append(r["primary"])
        self.assertEqual({k: v.count(True) for k, v in by.items() if v.count(True) != 1}, {})

    def test_elections_and_sports_link_up(self):
        nations = {r["iso2"] for r in MD.raw_dataset("nations")}   # the Philippines' founding chart is untimed, so only the raw file has it
        elections = MD.dataset("elections")["records"]
        self.assertFalse({r["iso2"] for r in elections} - nations, "an election country without a founding chart")
        for r in MD.dataset("sports")["records"]:
            self.assertIn(r["winner"], (r["team_a"], r["team_b"], None), r["id"])

    def test_named_disasters_label_their_ncei_record_once(self):
        recs = MD.dataset("disasters")["records"]
        self.assertFalse([r for r in recs if r.get("same_as")], "a linked curated record is listed twice")
        sumatra = next(r for r in recs if r["id"] == "ea5823")   # NCEI's 2004-12-26 Mw 9.1
        self.assertIn("Indian Ocean", sumatra.get("name", ""))
        self.assertEqual(sumatra["time"], "00:58:53")

    def test_rodden_charts_time_and_join_the_sets(self):
        # tools/mundane_rodden.py: NCEI has Etna's 1979 eruption untimed, the Rodden library has it to the minute; Katrina only Rodden has
        recs = {r["id"]: r for r in MD.dataset("disasters")["records"]}
        self.assertEqual((recs["vo30"]["time"], recs["vo30"]["tz_east"], recs["vo30"]["time_confidence"]), ("15:47:00", 0, "exact"))
        self.assertIn("Rodden", recs["vo30"]["time_source"])
        self.assertEqual(recs["ro-nature-hurricane-katrina"]["type"], "cyclone")
        self.assertNotIn("time", next(r for r in MD.raw_dataset("disasters", rodden=False) if r["id"] == "vo30"))
        old = next(r for r in MD.raw_dataset("disasters") if r["id"].startswith("ro-") and r.get("type") == "earthquake" and MD._year(r) < 1900 and r.get("gregorian", True))
        self.assertEqual(MD.dropped(old), "before 1900")   # pre-instrumental, whoever timed it
        kinds = {r["type"] for r in MD.dataset("events")["records"]}   # what no other set has a kind for
        self.assertTrue({"UFO sighting", "TV show", "terror attack", "space flight"} <= kinds, kinds)

    def test_finance_lists_companies_at_their_first_trade(self):
        recs = {r["id"]: r for r in MD.dataset("finance")["records"]}
        apple = recs["fi-q312"]   # Nasdaq opened at 10:00 until 30 Sep 1985; the Rodden library's AA chart of the first trade agrees
        self.assertEqual((apple["date"], apple["time"], apple["tz_east"], apple["mic"]), ("1980-12-12", "10:00", -5.0, "XNAS"))
        self.assertEqual((apple["status"], apple["founded"], apple["time_confidence"]), ("listed", "1976-04-01", "reported"))
        self.assertTrue({"S&P 500", "Nasdaq-100", "Dow Jones"} <= set(apple["indices"]))
        tsmc = next(r for r in recs.values() if r.get("symbol") == "TSM")   # its New York ADR came later: the first listing is Taipei's
        self.assertEqual((tsmc["listed"], tsmc["mic"], tsmc["time"], tsmc["tz_east"]), ("1994-09-05", "XTAI", "09:00", 8.0))
        self.assertEqual(recs["fi-q333718"]["listed"], "1944-09-25")   # J&J, looked up by hand (a Monday: its own "24th" was a Sunday)
        startups = [r for r in recs.values() if r["status"] == "startup"]
        self.assertTrue(startups and any(not r.get("founded") and not r.get("date") for r in startups))   # kept without a date
        self.assertTrue(all(r["chart"] == "founding" and len(r["date"]) == 10 for r in startups if r.get("date")))

    def test_finance_builder_helpers(self):
        from tools.mundane_finance import calibrate, norm_ticker, open_time, sector_of
        self.assertEqual([norm_ticker(t) for t in ("NYSE: BRK.B", "BRK-B", "7203.T", "0700", "005930")], ["BRKB", "BRKB", "7203", "700", "5930"])
        self.assertEqual((open_time("XNYS", "1985-09-27"), open_time("XNYS", "1985-09-30"), open_time("XHKG", "2004-06-16")), ("10:00", "09:30", "10:00"))
        # Yahoo's days are trusted from the first that agrees and after which 90% agree: not before, where a data start disagrees
        pairs = [("1999-01-04", "1980-05-01")] + [(f"2001-02-{d:02d}", f"2001-02-{d:02d}") for d in range(1, 10)]
        self.assertEqual(calibrate({"X": pairs}), {"X": "2001-02-01"})
        self.assertEqual(calibrate({"X": pairs[:5]}), {})   # too few to say
        self.assertEqual((sector_of("Electric utility"), sector_of("Oil and gas"), sector_of("Retail")), ("Utilities", "Energy", "Consumer Cyclical"))

    def test_api_serves_sets_and_refuses_others(self):
        r = client.get("/api/mundane/data/nations")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.headers.get("content-encoding"), "gzip")   # kept compressed, sent as it is
        self.assertIn("about", r.json())
        plain = client.get("/api/mundane/data/nations", headers={"Accept-Encoding": "identity"})
        self.assertIsNone(plain.headers.get("content-encoding"))
        self.assertEqual(plain.json()["records"], r.json()["records"])
        self.assertEqual(client.get("/api/mundane/data/secrets").status_code, 404)

    def test_overview_summary_matches_the_sets(self):
        s = client.get("/api/mundane/summary").json()
        self.assertEqual(set(s), set(MD.SETS))
        for name, card in s.items():
            recs = MD.dataset(name)["records"]
            self.assertEqual(card["count"], len(recs), name)
            self.assertEqual(card["countries"], len({r["country"] for r in recs if r.get("country")}), name)
            self.assertTrue(0 < len(card["notable"]) <= 5 and len(card["kinds"]) <= 5, name)
        deaths = [r["deaths"] for r in s["disasters"]["notable"]]
        self.assertEqual(deaths, sorted(deaths, reverse=True))   # the deadliest
        fin = s["finance"]
        self.assertEqual(sum(fin["status"].values()), fin["count"])
        self.assertEqual(fin["notable"][0]["rank"], 1)   # the most valuable company first
        self.assertEqual(s["nations"]["last"], max(r["date"] for r in MD.dataset("nations")["records"]))


class Patterns(unittest.TestCase):
    def test_india_1947(self):
        # the India sample chart: Lagna Taurus, Sun and Moon in Cancer, Moon in Pushya
        r = client.post("/api/mundane/patterns", json={"ids": ["na-in-independence"]})
        self.assertEqual(r.status_code, 200, r.text)
        e = r.json()["events"][0]
        self.assertTrue(e["timed"])
        self.assertEqual(e["lagna"], 1)
        self.assertEqual(e["p"]["Sun"][0], 3)
        self.assertEqual(e["p"]["Moon"][:2], [3, 7])
        self.assertEqual(e["p"]["Sun"][3], 3)   # Cancer is the 3rd from a Taurus Lagna
        self.assertEqual(e["weekday"], 5)        # a Friday
        self.assertEqual(len(r.json()["control"]), MD.CONTROL)

    def test_control_is_deterministic_and_unknown_ids_are_counted(self):
        a = client.post("/api/mundane/patterns", json={"ids": ["na-in-independence", "nope"]}).json()
        b = client.post("/api/mundane/patterns", json={"ids": ["na-in-independence"]}).json()
        self.assertEqual(a["unknown"], 1)
        self.assertEqual(a["control"][:5], b["control"][:5])

    def test_untimed_events_have_no_lagna(self):
        untimed = next(r for r in MD.raw_dataset("nations") if r["time_confidence"] == "date")
        e = MD._factors(MD.birth_of(untimed).jd_ut, MD.birth_of(untimed), MD.SET.config(MD.SET.SettingsIn()), False, True, False)
        self.assertIsNone(e["lagna"])
        self.assertTrue(all(v[3] is None for v in e["p"].values()))


if __name__ == "__main__":
    unittest.main()
