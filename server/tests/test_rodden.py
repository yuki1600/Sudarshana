"""databases/build_rodden_db.py: a Rodden text file read into a chart and its Predictions facts."""
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "databases"))
import build_rodden_db as R  # noqa: E402

FILE = """START MAIN BIRTH DATA
name: Doe, Jane
gender: F
born_on: 1 August 1527 Jul.Cal. (11 Aug 1527 greg.) at 23:16  (= 11:16 PM )
place: Paris, France, 48n52,  2e20
timezone: PMT m2e2015 (is standard time)
datasource: Quoted BC/BR
rodden_rating: AA
collector: Test
END MAIN BIRTH DATA

START BIOGRAPHY
French writer.
Link to Wikipedia biography
END BIOGRAPHY

START EVENTS
Relationship : Marriage  12 July 1550   (First)     chart Placidus Equal_H.
Death of Father  1560
Relationship : Divorce dates  May 1562
END EVENTS

START SOURCE NOTES
A book.
END SOURCE NOTES

START CATEGORY KEYWORDS
Kids more than 3 (Six)
1527 birthsBirthday
END CATEGORY KEYWORDS
"""


class Rodden(unittest.TestCase):
    def test_api_lists_the_library(self):
        from fastapi.testclient import TestClient
        from server.app import app
        r = TestClient(app).get("/api/rodden")   # made on first asking and kept gzipped
        self.assertEqual((r.status_code, r.headers.get("content-encoding")), (200, "gzip"))
        rows = r.json()
        self.assertIsInstance(rows, list)   # empty until databases/build_rodden_db.py has run
        self.assertTrue(all(len(x) == 8 for x in rows[:100]))

    def test_zones_and_coordinates(self):
        self.assertEqual(R.zone("IST h5e30 (is standard time)"), (5.5, False))
        self.assertEqual(R.zone("EWT h4w (is war time)"), (-4.0, True))
        self.assertAlmostEqual(R.zone("PMT m2e2015 (is standard time)")[0], (2 + 20 / 60 + 15 / 3600) / 15)
        self.assertAlmostEqual(R.coord("13s3956"), -(13 + 39 / 60 + 56 / 3600))
        self.assertEqual(R.coord("1e0"), 1.0)
        self.assertEqual(R.born("13 January 1099 BC (-1098) Jul.Cal. at 06:50  (= 06:50 AM )"), (-1098, 1, 13, 6 + 50 / 60, False))

    def test_chart_and_facts(self):
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as f:
            f.write(FILE)
        try:
            c = R.chart(f.name)
        finally:
            os.unlink(f.name)
        b = c["birth"]
        self.assertEqual((b["year"], b["month"], b["day"], b["gregorian"]), (1527, 8, 1, False))
        self.assertEqual(c["s"]["meta"]["gender"], 2)
        a = c["facts"]["answers"]
        self.assertEqual(a, {"gender": "Female", "father": "Passed", "father.year": 1560, "marriage": "Divorced", "marriage.year": 1550})
        self.assertEqual([(e["year"], e["kind"], e["note"]) for e in c["facts"]["events"]],
                         [(1550, "Relationship: Marriage", "12 July 1550 · First"), (1560, "Death of Father", ""), (1562, "Relationship: Divorce dates", "May 1562")])
        notes = c["facts"]["notes"]
        self.assertIn("French writer.", notes)
        self.assertIn("Kids more than 3 (Six)", notes)
        self.assertNotIn("Wikipedia", notes)
        self.assertNotIn("births", notes)

    def test_alive_or_dead_from_the_death_event(self):
        from server import rodden
        died = lambda kind, note: rodden.with_death({"answers": {}, "events": [{"kind": kind, "note": note}]})["answers"]  # noqa: E731
        self.assertEqual(died("Death by Disease", "3 June 1990 at 14:05 · in hospital"), {"status": "Dead", "death.date": "1990-06-03", "death.time": "14:05"})
        self.assertEqual(died("Death, Cause unspecified", "5 August 1962"), {"status": "Dead", "death.date": "1962-08-05"})
        self.assertEqual(died("Death, Cause unspecified", "1990"), {"status": "Dead"})      # the year only: no date to give
        for other in ("Death of Mother", "Death: Suicide Attempt", "Death and Came back"):
            self.assertEqual(died(other, "1 May 1990"), {})

    def test_event_kinds(self):
        from tools.mundane_rodden import kind_of
        self.assertEqual([kind_of(n, []) for n in ("Nature:Earthquake Mexico 1986", "Accident: Plane Crash 14268", "Nature:Eruption:Mayon 1993",
                                                   "First performance:Die Entführung aus dem Serail", "Historic: Bosnian War:Ceasefire",
                                                   "Mortality: Assassination of John F. Kennedy", "Accident: Moorgate Train Crash", "Nation: Kenya")],
                         ["earthquake", "air crash", "volcano", None, None, None, "rail accident", "nation"])
        from tools.mundane_rodden import event_type
        self.assertEqual([event_type(n, c) for n, c in (("UFO Sighting 12707", []), ("Entertainment: Will and Grace", ["Release dates (TV series)"]),
                                                        ("Terrorist: Bali Explosion", []), ("Space: Apollo 12 (Launch)", []), ("Oracle, Shares", []))],
                         ["UFO sighting", "TV show", "terror attack", "space flight", "business"])


if __name__ == "__main__":
    unittest.main()
