"""The Longevity tab over the API on every sample chart. The rules are checked in core_logic/tests/test_ayurdaya.py; here, that each chart reaches them and that the
view agrees with the Key Info list."""
import unittest

from fastapi.testclient import TestClient

from server.app import app
from server.tests.test_modes import birth_of

client = TestClient(app)
SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
IDS = ["summary", "pairs", "marakas", "rudra", "spans", "eighth", "ashtakavarga", "yogas"]


def sections(birth, settings=None):
    r = client.post("/api/longevity", json={"birth": birth, "settings": settings})
    r.raise_for_status()
    return {s["id"]: s for s in r.json()}


def table(section, title):
    return next(t for t in section["tables"] if t["title"].startswith(title))


class TestLongevity(unittest.TestCase):
    def test_every_sample_chart(self):
        names = client.get("/api/samples").json()
        self.assertGreaterEqual(len(names), 18)
        for name in names:
            with self.subTest(name):
                birth = birth_of(name)
                got = sections(birth)
                self.assertEqual(list(got), IDS)
                for s in got.values():
                    self.assertTrue(s["verdict"])
                    for t in s["tables"]:
                        for row in t["rows"]:
                            self.assertEqual(len(row), len(t["columns"]), t["title"])
                # Rudra as the Key Info view has it, and the Trishoola rasis its trines
                key = client.post("/api/table", json={"birth": birth, "view": "brahma"}).json()
                who = table(got["rudra"], "Rudra and")["rows"]
                self.assertEqual(who[0][1], next(r[1] for r in key["rows"] if r[0] == "Rudra"))
                sign = SIGNS.index(who[0][2])
                self.assertEqual([r[0] for r in table(got["rudra"], "Trishoola")["rows"]], [SIGNS[(sign + k) % 12] for k in (0, 4, 8)])
                self.assertEqual(len(table(got["rudra"], "Niryana Shoola dasa")["rows"]), 12)
                self.assertEqual(len(table(got["rudra"], "Shoola dasa")["rows"]), 12)
                self.assertIn("headline", got["summary"])
                self.assertEqual(got["summary"]["headline"]["class"], dict(table(got["pairs"], "The result")["rows"])["Final class"])
                # the summary's primary row matches the pairs class
                self.assertEqual(table(got["summary"], "Primary")["rows"][0][2], got["summary"]["headline"]["class"])
                self.assertTrue(got["marakas"]["tables"])
                self.assertTrue(any(t["title"].startswith("Manner") for t in got["marakas"]["tables"]))
                # the Starlight view's values: every section has them, and Varnada's limit is one period at most
                self.assertTrue(all(s["data"] for k, s in got.items() if k != "summary"))
                varnada = next(d for d in got["rudra"]["data"]["dasas"] if d["id"] == "varnada")
                self.assertLessEqual(sum(p["candidate"] for p in varnada["periods"]), 1)
                self.assertEqual(got["summary"]["headline"]["methods"][0]["class"], got["summary"]["headline"]["class"])

    def test_vivekananda_by_hand(self):
        """Worked from BPHS 43.33-47: the lords movable + dual = short, Saturn + Moon both dual and Lagna + Hora Lagna both dual = medium.
        Saturn decides only from his Saturn-Moon seat, not as the lagna or 8th lord: by default (he causes no yoga) medium stays; with the wider reading it falls."""
        got = sections(birth_of("Swami Vivekananda"))
        self.assertEqual([r[3] for r in table(got["pairs"], "The three pairs")["rows"]], ["Short (Alpayu)", "Medium (Madhyayu)", "Medium (Madhyayu)"])
        result = dict(table(got["pairs"], "The result")["rows"])
        self.assertEqual(result["Final class"], "Medium (Madhyayu)")
        self.assertEqual(result["Span by class and agreement (43.41-44)"], "72")
        wide = dict(table(sections(birth_of("Swami Vivekananda"), {"longevity_saturn": 1})["pairs"], "The result")["rows"])
        self.assertEqual(wide["Final class"], "Short (Alpayu)")
        self.assertEqual(wide["Span by class and agreement (43.41-44)"], "36")
        self.assertEqual(result["Contributors"], "Saturn, Moon, Lagna, Hora Lagna")
        # the Sun in the lagna, a malefic there; Saturn and the Moon together in the 10th: only Saturn, the stronger, loses
        pinda = {r[0]: r for r in table(got["spans"], "Pindayu")["rows"]}
        self.assertNotEqual(pinda["Sun"][7], "-")
        self.assertEqual(pinda["Moon"][4], "-")
        self.assertEqual(pinda["Saturn"][4], "0.333")
        self.assertEqual(table(got["rudra"], "Rudra and")["rows"][0][1:3], ["Moon", "Virgo"])

    def test_gandhi_has_a_short_list_of_marakas(self):
        """44.6-7 read functionally: Libra lagna, the Sun rules only the 11th and Jupiter the 3rd and 6th; 2nd and 7th lord Mars and the malefics on them are prime."""
        got = sections(birth_of("Mahatma Gandhi"))["marakas"]["data"]["grahas"]
        self.assertEqual([g["graha"] for g in got if g["prime"]], ["Ma", "Me", "Sa", "Ra"])
        self.assertLess(len(got), 9)

    def test_settings_reach_it(self):
        birth = birth_of("Mahatma Gandhi")
        plain = table(sections(birth)["pairs"], "The three pairs")
        tropical = table(sections(birth, {"ayanamsa": "TROPICAL"})["pairs"], "The three pairs")
        self.assertNotEqual(plain["rows"], tropical["rows"])

    def test_bad_birth_is_422(self):
        self.assertEqual(client.post("/api/longevity", json={"birth": {"year": 2000}}).status_code, 422)


if __name__ == "__main__":
    unittest.main()
