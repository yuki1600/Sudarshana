"""The lore pop-ups' database (data/lore/): every graha, rashi, bhava and nakshatra complete, what each signifies grouped as jiva
(living) and ajiva (non-living), the BPHS slokas quoted for each, and the routes that serve them."""
import json
import unittest

from fastapi.testclient import TestClient

from server import lore
from server.app import app

client = TestClient(app)
JIVA, AJIVA = ["people", "body", "mind", "creatures"], ["work", "wealth", "property", "things", "places", "pursuits"]


def text_of(v) -> str:
    return json.dumps(v, ensure_ascii=False)


class TestRecords(unittest.TestCase):
    def test_every_record_and_its_groups(self):
        for name, key, count in (("grahas.json", "grahas", 9), ("rashis.json", "rashis", 12), ("bhavas.json", "bhavas", 12)):
            recs = lore._load(name)[key]
            self.assertEqual(len(recs), count, name)
            for r in recs:
                s = r["significations"]
                self.assertEqual((sorted(s["jiva"]), sorted(s["ajiva"])), (sorted(JIVA), sorted(AJIVA)), (name, r.get("id", r.get("n"))))
                self.assertTrue(r["about"] and s["jiva"]["people"] and s["jiva"]["body"], (name, r.get("name")))
        sig = lore._load("nakshatra_significations.json")["nakshatras"]
        self.assertEqual([x["n"] for x in sig], list(range(1, 28)))
        self.assertTrue(all(sorted(x["jiva"]) == sorted(JIVA) and sorted(x["ajiva"]) == sorted(AJIVA) and x["jiva"]["people"] for x in sig))

    def test_facts_name_their_source(self):
        for name, key in (("grahas.json", "grahas"), ("rashis.json", "rashis")):
            for r in lore._load(name)[key]:
                rows = [row for g in r["facts"] for row in g["rows"]]
                self.assertTrue(all(row["k"] and row["v"] and "src" in row for row in rows), r["name"])
                self.assertGreaterEqual(sum(bool(row.get("tile")) for row in rows), 6, r["name"])

    def test_bphs_quotes_in_the_apps_words(self):
        q = lore._load("bphs_quotes.json")
        self.assertEqual(q["grahas"]["Su"][0]["head"], "Description of the Sun")
        self.assertTrue(all(len(q["rashis"][str(n)]) == 1 for n in range(1, 13)))
        self.assertEqual(q["rashis"]["8"][0]["head"], "Scorpio described")        # Libra and Scorpio share 4.15-16½
        self.assertTrue(q["bhavas"]["5"][0]["source"] == "BPHS 11.6" and q["bhavas"]["5"][1]["source"].startswith("BPHS 16."))
        # the translation's Sanskrit names and marks turned into the app's
        for w in ("Sūrya", "Candr", "Mangal", "Śukr", "Śani", "Rāśi", "ᓼ", "grahaas", "Navāńś"):
            self.assertNotIn(w, text_of(q), w)

    def test_combination_tables_complete(self):
        rb, nb = lore._load("rashi_bhava.json")["readings"], lore._load("nakshatra_bhava.json")["readings"]
        self.assertEqual(([r["sign"] for r in rb], [r["n"] for r in nb]), (list(range(1, 13)), list(range(1, 28))))
        for r in rb + nb:
            self.assertEqual(len(r["houses"]), 12)
            self.assertTrue(all(h["jiva"].strip() and h["ajiva"].strip() for h in r["houses"]), r)
        gb, ga = lore._load("graha_bhava.json")["readings"], lore._load("graha_aspects.json")["readings"]
        self.assertEqual((sorted(gb), sorted(ga)), (sorted(lore.GRAHAS), sorted(lore.GRAHAS)))
        self.assertTrue(all(len(gb[g]) == 12 and all(x["text"] for x in gb[g]) for g in gb))
        self.assertTrue(all(len(ga[g]) == 12 and all(ga[g]) for g in ga))
        # each graha in each bhava names its Phaladeepika 8 sloka, but for the Sun in the 1st to 6th, missing from the text consulted
        self.assertEqual([(g, i + 1) for g in gb for i, x in enumerate(gb[g]) if not x["source"]], [("Su", h) for h in range(1, 7)])
        gr, gn = lore._load("graha_rashi.json")["readings"], lore._load("graha_nakshatra.json")["readings"]
        self.assertEqual((sorted(gr), sorted(gn)), (sorted(lore.GRAHAS), sorted(lore.GRAHAS)))
        self.assertTrue(all(len(gr[g]) == 12 and all(x["text"] for x in gr[g]) for g in gr))
        self.assertTrue(all(len(gn[g]) == 27 and all(gn[g]) for g in gn))
        # a graha's deepest exaltation or debilitation named in a nakshatra is the one the nakshatra's own pop-up places there
        for n in range(1, 28):
            marks = {(x["graha"], x["kind"]) for x in lore.nakshatra(n)["dignities"]}
            said = {(g, k) for g in gn for k, w in (("exalted", "deepest exaltation"), ("debilitated", "deepest debilitation")) if w in gn[g][n - 1] and "past its" not in gn[g][n - 1]}
            self.assertEqual(said, marks, n)
        for name in ("rashi_bhava.json", "nakshatra_bhava.json", "graha_bhava.json", "graha_aspects.json", "graha_rashi.json", "graha_nakshatra.json"):
            self.assertFalse(any(w in text_of(lore._load(name)) for w in ("Cosmic Insights", "Arjun Pai")), name)


class TestRoutes(unittest.TestCase):
    def test_graha(self):
        g = client.get("/api/lore/graha/Su").json()
        self.assertEqual((g["name"], g["rules"]), ("Sun", {"signs": [5], "nakshatras": [3, 12, 21]}))
        self.assertEqual(g["relations"]["friends"], ["Mo", "Ma", "Ju"])
        self.assertEqual(g["karaka_of"], {"bphs": [1], "phaladeepika": [1, 9, 10]})
        self.assertEqual([s["id"] for s in g["significations"]], ["jiva", "ajiva"])
        self.assertTrue(g["classics"] and g["classics_all"])
        self.assertEqual(client.get("/api/lore/graha/Ur").status_code, 422)
        # Jupiter is the karaka of four bhavas in BPHS (2, 5, 9, 11); Saturn of the 8th and 12th
        self.assertEqual(client.get("/api/lore/graha/Ju").json()["karaka_of"]["bphs"], [2, 5, 9, 11])
        self.assertEqual(client.get("/api/lore/graha/Sa").json()["karaka_of"]["bphs"], [8, 12])

    def test_rashi(self):
        r = client.get("/api/lore/rashi/2").json()
        self.assertEqual((r["name"], r["lord"]), ("Taurus", "Ve"))
        self.assertEqual([(x["name"], x["padas"]) for x in r["nakshatras"]], [("Krittika", [2, 3, 4]), ("Rohini", [1, 2, 3, 4]), ("Mrigashira", [1, 2])])
        kinds = {(d["graha"], d["kind"]) for d in r["dignities"]}
        self.assertTrue({("Mo", "exalted"), ("Mo", "moolatrikona"), ("Ve", "own"), ("Ra", "exalted"), ("Ke", "debilitated")} <= kinds)
        self.assertEqual(client.get("/api/lore/rashi/13").status_code, 422)
        # every rashi holds nine padas; Libra exalts Saturn at 20° and debilitates the Sun at 10°
        for n in range(1, 13):
            self.assertEqual(sum(len(x["padas"]) for x in client.get(f"/api/lore/rashi/{n}").json()["nakshatras"]), 9)
        libra = {(d["graha"], d["kind"]): d["deg"] for d in client.get("/api/lore/rashi/7").json()["dignities"]}
        self.assertEqual((libra[("Sa", "exalted")], libra[("Su", "debilitated")]), (20, 10))

    def test_bhava(self):
        b = client.get("/api/lore/bhava/5").json()
        self.assertEqual((b["name"], b["kinds"], b["karakas"]["bphs"]), ("Putra", ["Trikona", "Panaphara"], ["Ju"]))
        self.assertEqual([x["house"] for x in b["lords"]["from"]], list(range(1, 13)))
        self.assertEqual([x["lord"] for x in b["lords"]["into"]], list(range(1, 13)))
        self.assertTrue(b["classics"][0]["source"] == "BPHS 11.6" and b["judge"] and b["karaka_slokas"])
        self.assertEqual(client.get("/api/lore/bhava/0").status_code, 422)

    def test_nakshatra_significations(self):
        k = client.get("/api/lore/nakshatra/1").json()
        jiva = {p["id"]: p["items"] for p in k["significations"][0]["parts"]}
        ajiva = {p["id"]: p["items"] for p in k["significations"][1]["parts"]}
        self.assertIn("Physicians", jiva["people"])
        self.assertIn("Male Horse (its yoni)", jiva["creatures"])
        self.assertIn("Knees and the Top Portion of the Feet", jiva["body"])
        self.assertIn("Physicians", ajiva["work"])          # the book's careers, after the classics' work

    def test_no_modern_book_named(self):
        got = [client.get(f"/api/lore/{k}/{n}").json() for k, ns in (("graha", lore.GRAHAS), ("rashi", range(1, 13)), ("bhava", range(1, 13))) for n in ns]
        self.assertFalse(any(w in text_of(got) for w in ("Cosmic Insights", "Arjun Pai")))


class TestBhavaReading(unittest.TestCase):
    """A bhava read for a chart agrees with the screens that show the same facts: the Houses table, KP, the Aspects table and the
    Grahas tab's insights."""
    @classmethod
    def setUpClass(cls):
        from server.tests.test_modes import birth_of
        cls.b = birth_of("Swami Vivekananda")
        cls.read = {(h, ref): client.post("/api/lore/bhava_reading", json={"birth": cls.b, "house": h, "ref": ref}).json() for h in range(1, 13) for ref in (0, 2)}

    def test_cusp_sign_and_nakshatra(self):
        houses = client.post("/api/houses", json={"birth": self.b, "ref": 0}).json()
        kp = {r["label"]: r["lords"] for r in client.post("/api/kp", json={"birth": self.b, "ref": 0}).json()}
        for h in range(1, 13):
            r = self.read[(h, 0)]
            self.assertAlmostEqual(r["cusp"], houses[h - 1]["cusp"] % 360.0, places=6)
            self.assertEqual(r["sign"], int(r["cusp"] // 30) + 1)
            self.assertEqual([r["nakshatra"]["lord"], r["nakshatra"]["sub_lord"]], kp[f"{lore.ORDINAL[h - 1]} bhava"][:2], h)
            self.assertEqual(sum(p["percent"] for p in r["span"]), 100)
            nine = {x for x in houses[h - 1]["occupants"] if x in lore.GRAHAS}
            self.assertEqual({o["graha"] for o in r["occupants"]}, nine, h)

    def test_lord_aspects_and_strength(self):
        ins = {g["name"]: g for g in client.post("/api/graha_insights", json={"birth": self.b, "division": 1}).json()}
        asp = {row["body"][:2]: row["houses"] for row in client.post("/api/aspect_table", json={"birth": self.b, "division": 1, "ref": 0}).json()["rows"]}
        bala = client.post("/api/strengths", json={"birth": self.b}).json()["shadbala"]["bhavas"]
        for h in range(1, 13):
            r = self.read[(h, 0)]
            self.assertEqual(r["lord"]["graha"], lore.SIGN_LORD[r["sign"] - 1])
            self.assertEqual(r["lord"]["bhava"], ins[lore.NAMES[r["lord"]["graha"]]]["bhava"], h)
            self.assertEqual({a["graha"]: a["value"] for a in r["aspects"]}, {g: v[h - 1] for g, v in asp.items() if v[h - 1]}, h)
            self.assertAlmostEqual(r["bala"]["percent"], bala[h - 1]["rupas"] / 7 * 100, places=6)       # Bhava Bala against its 7 rupas
            self.assertTrue(r["checks"] and all(c["source"].startswith("BPHS") or not c["source"] for c in r["checks"]))
            kinds = [p["kind"] for p in r["parts"]]
            self.assertEqual(kinds[:3], ["rashi", "nakshatra", "lord"], h)
            self.assertTrue(all(p["link"]["kind"] in ("rashi", "nakshatra", "graha") for p in r["parts"]))

    def test_from_the_moon(self):
        r = self.read[(1, 2)]
        moon = client.post("/api/graha_insights", json={"birth": self.b, "division": 1}).json()[1]
        self.assertEqual((r["from"], r["bala"]), ("the Moon", None))       # Bhava Bala is the Lagna's bhavas' only
        self.assertEqual(r["sign"], moon["sign_no"] + 1)                    # equal bhavas from the Moon: her own sign holds the 1st cusp
        self.assertNotIn("Mo", [o["graha"] for o in r["occupants"]])       # the reference is not an occupant of its own 1st bhava
        self.assertEqual(client.post("/api/lore/bhava_reading", json={"birth": self.b, "house": 13}).status_code, 422)


if __name__ == "__main__":
    unittest.main()
