"""Accounts: sign up, sign in, sign out, and the gate on /api/*."""
import base64
import hashlib
import os
import tempfile
import unittest
import urllib.parse

from fastapi.testclient import TestClient

from server import auth
from server.app import app


class TestAuth(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.db, auth.DB = auth.DB, os.path.join(self.dir.name, "accounts.db")
        auth.REQUIRED = True
        auth._fails.clear()
        self.owner, auth.OWNER = auth.OWNER, None   # no admin account made in these test databases unless a test sets one
        self.samples, auth.SAMPLES = auth.SAMPLES, self.dir.name   # new accounts start empty unless a test gives them the samples
        self.c = TestClient(app)

    def tearDown(self):
        auth.DB, auth.REQUIRED, auth.OWNER, auth.SAMPLES = self.db, False, self.owner, self.samples
        self.dir.cleanup()

    def signup(self, email="a@example.com", password="lotus-feet"):
        return self.c.post("/api/auth/signup", json={"name": "Asha", "email": email, "password": password, "terms": auth.TERMS_VERSION})

    def me(self):
        return {k: v for k, v in self.c.get("/api/auth/me").json().items() if k in ("name", "email", "home")}

    def test_signup_me_logout(self):
        self.assertEqual(self.signup().status_code, 200)
        self.assertEqual(self.c.get("/api/auth/me").json(), {"name": "Asha", "email": "a@example.com", "username": "Asha", "home": None,
                                                             "hasPassword": True, "termsAccepted": True, "admin": False,
                                                             "avatar": None, "themes": []})
        self.c.post("/api/auth/logout")
        self.assertIsNone(self.c.get("/api/auth/me").json())

    def test_duplicate_email_any_case(self):
        self.signup()
        self.assertEqual(self.signup("A@Example.com").status_code, 409)

    def test_bad_input(self):
        self.assertEqual(self.signup("not-an-email").status_code, 422)
        self.assertEqual(self.signup(password="short").status_code, 422)

    def test_login(self):
        self.signup()
        self.c.cookies.clear()
        self.assertEqual(self.c.post("/api/auth/login", json={"email": "a@example.com", "password": "wrong-one"}).status_code, 401)
        self.assertEqual(self.c.post("/api/auth/login", json={"email": "nobody@example.com", "password": "lotus-feet"}).status_code, 401)
        self.assertEqual(self.c.post("/api/auth/login", json={"email": "a@example.com", "password": "lotus-feet"}).status_code, 200)

    def test_username_defaults_to_first_name(self):
        def up(name, email):
            self.c.cookies.clear()
            return self.c.post("/api/auth/signup", json={"name": name, "email": email, "password": "lotus-feet", "terms": auth.TERMS_VERSION}).json()["username"]
        self.assertEqual(up("Priya Rao", "p1@example.com"), "Priya")
        self.assertEqual(up("priya K", "p2@example.com"), "priya2")   # usernames ignore case, so the next free one
        self.assertEqual(up("O'Neil", "o@example.com"), "ONeil")
        self.assertEqual(up("प्रिया", "p3@example.com"), "")             # nothing usable: no username
        self.c.cookies.clear()
        self.assertEqual(self.c.post("/api/auth/login", json={"email": "Priya", "password": "lotus-feet"}).status_code, 200)

    def test_owner_account(self):
        import hashlib
        auth.OWNER = {"username": "Boss", "name": "Boss", "email_sha256": hashlib.sha256(b"boss@example.com").hexdigest(),
                      "password_hash": auth.hash_password("owner-pass")}
        self.assertEqual(self.c.post("/api/auth/login", json={"email": "Boss", "password": "owner-pass"}).status_code, 200)
        self.c.cookies.clear()
        r = self.c.post("/api/auth/login", json={"email": "Boss@Example.com", "password": "owner-pass"})
        self.assertEqual((r.status_code, r.json()["email"]), (200, "Boss@Example.com"))   # the fresh server learns the email
        self.assertIs(r.json()["admin"], True)   # the owner alone may pick the Windows layout and the Praajna colours
        self.assertIs(self.c.get("/api/auth/me").json()["admin"], True)
        self.c.cookies.clear()
        self.assertEqual(self.c.post("/api/auth/login", json={"email": "boss@example.com", "password": "wrong-pass"}).status_code, 401)
        with auth._db() as c:
            self.assertEqual(c.execute("SELECT count(*) FROM users WHERE admin = 1").fetchone()[0], 1)

    def test_owner_login_only_on_this_machine(self):
        path, auth.OWNER_LOGIN = auth.OWNER_LOGIN, os.path.join(self.dir.name, "owner-login.json")
        try:
            with open(auth.OWNER_LOGIN, "w") as f:
                f.write('{"email": "boss@example.com", "password": "owner-pass"}')
            local = TestClient(app, base_url="http://127.0.0.1:8000")
            self.assertEqual(local.get("/api/auth/owner-login").json(), {"email": "boss@example.com", "password": "owner-pass"})
            self.assertIsNone(local.get("/api/auth/owner-login", headers={"CF-Connecting-IP": "203.0.113.9"}).json())   # the tunnel
            self.assertIsNone(TestClient(app, base_url="https://abc.trycloudflare.com").get("/api/auth/owner-login").json())
        finally:
            auth.OWNER_LOGIN = path

    def test_username(self):
        self.assertEqual(self.c.post("/api/auth/signup", json={"name": "Yuki", "email": "y@example.com", "password": "lotus-feet", "username": "Yuki", "terms": auth.TERMS_VERSION}).status_code, 200)
        self.c.cookies.clear()
        for who in ("yuki", "Y@Example.com"):   # either one, any case
            self.assertEqual(self.c.post("/api/auth/login", json={"email": who, "password": "lotus-feet"}).status_code, 200)
        taken = self.c.post("/api/auth/signup", json={"name": "Y2", "email": "y2@example.com", "password": "lotus-feet", "username": "YUKI", "terms": auth.TERMS_VERSION})
        self.assertEqual((taken.status_code, taken.json()["detail"]), (409, "That username is taken."))
        self.assertEqual(self.c.post("/api/auth/signup", json={"name": "Y3", "email": "y3@example.com", "password": "lotus-feet", "username": "a@b", "terms": auth.TERMS_VERSION}).status_code, 422)
        self.assertEqual(self.signup("y4@example.com").status_code, 200)   # no username: still fine, and NULLs don't collide
        self.assertEqual(self.signup("y5@example.com").status_code, 200)

    def test_old_db_gains_username(self):
        import sqlite3
        c = sqlite3.connect(auth.DB)
        c.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, email TEXT NOT NULL UNIQUE COLLATE NOCASE, name TEXT NOT NULL, password_hash TEXT, created INTEGER NOT NULL)")
        c.execute("INSERT INTO users (email, name, password_hash, created) VALUES ('o@example.com', 'Old', ?, 0)", (auth.hash_password("lotus-feet"),))
        c.commit(); c.close()
        self.assertEqual(self.c.post("/api/auth/login", json={"email": "o@example.com", "password": "lotus-feet"}).status_code, 200)

    def test_gate(self):
        sky = self.c.get("/api/sky")   # public: the sign-in page draws it
        self.assertEqual(sky.status_code, 200)
        self.assertEqual(len(sky.json()), 9)
        self.assertEqual(self.c.get("/api/samples").status_code, 401)
        self.signup()
        self.assertEqual(self.c.get("/api/samples").status_code, 200)

    def test_home_is_per_account(self):
        home = {"lat": 13.08, "lon": 80.27, "tz": 5.5, "alt": 6.0, "meta": {"city": "Chennai"}}
        self.assertEqual(self.c.put("/api/auth/home", json={"home": home}).status_code, 401)   # signed out
        self.signup()
        self.assertEqual(self.c.put("/api/auth/home", json={"home": home}).status_code, 200)
        self.assertEqual(self.c.put("/api/auth/home", json={"home": {**home, "lat": 91}}).status_code, 422)
        self.c.post("/api/auth/logout")
        self.assertEqual(self.c.post("/api/auth/login", json={"email": "a@example.com", "password": "lotus-feet"}).json()["home"], home)
        self.signup("b@example.com")   # another account starts with none
        self.assertIsNone(self.c.get("/api/auth/me").json()["home"])
        self.c.put("/api/auth/home", json={"home": None})
        self.assertIsNone(self.c.get("/api/auth/me").json()["home"])

    def test_avatar_and_themes(self):
        self.assertEqual(self.c.put("/api/auth/themes", json={"themes": []}).status_code, 401)   # signed out
        self.signup()
        pic = "data:image/png;base64,iVBORw0KGgo="
        self.assertEqual(self.c.put("/api/auth/avatar", json={"avatar": pic}).json()["avatar"], pic)
        self.assertEqual(self.c.put("/api/auth/avatar", json={"avatar": "javascript:alert(1)"}).status_code, 422)
        theme = {"name": "Mine", "settings": {"ayanamsa": "LAHIRI"}, "chartStyle": "north", "display": {"layout": "starlight"}}
        self.assertEqual(self.c.put("/api/auth/themes", json={"themes": [theme]}).json()["themes"], [theme])
        self.assertEqual(self.c.get("/api/auth/me").json()["themes"], [theme])
        self.assertEqual(self.c.put("/api/auth/themes", json={"themes": [{**theme, "name": ""}]}).status_code, 422)
        self.assertIsNone(self.c.put("/api/auth/avatar", json={"avatar": None}).json()["avatar"])

    def test_facts_are_per_account(self):
        key, data = "Asha|1990-03-12", {"answers": {"gender": "female", "father": "passed", "father.year": 2011}, "events": []}
        self.assertEqual(self.c.put("/api/auth/facts", json={"key": key, "data": data}).status_code, 401)   # signed out
        self.signup()
        self.assertIsNone(self.c.get("/api/auth/facts", params={"key": key}).json()["data"])
        self.assertEqual(self.c.put("/api/auth/facts", json={"key": key, "data": data}).status_code, 200)
        self.assertEqual(self.c.get("/api/auth/facts", params={"key": key}).json()["data"], data)
        self.c.put("/api/auth/facts", json={"key": key, "data": {"answers": {}, "events": []}})   # overwrites
        self.assertEqual(self.c.get("/api/auth/facts", params={"key": key}).json()["data"]["answers"], {})
        self.assertEqual(self.c.put("/api/auth/facts", json={"key": key, "data": {"x": "y" * 70000}}).status_code, 422)
        self.assertEqual(self.c.put("/api/auth/facts", json={"key": "", "data": data}).status_code, 422)
        self.signup("b@example.com")   # another account sees none of it
        self.assertIsNone(self.c.get("/api/auth/facts", params={"key": key}).json()["data"])

    def test_cloud_charts_are_per_account(self):
        self.assertEqual(self.c.get("/api/auth/charts").status_code, 401)   # signed out
        self.signup()
        self.assertEqual(self.c.get("/api/auth/charts").json(), [])
        self.assertEqual(self.c.put("/api/auth/chart", json={"name": "Asha", "content": "{}"}).status_code, 200)
        self.c.put("/api/auth/chart", json={"name": "Asha", "content": "{\"x\": 1}"})   # same name overwrites
        self.assertEqual([r["name"] for r in self.c.get("/api/auth/charts").json()], ["Asha"])
        self.assertEqual(self.c.get("/api/auth/chart", params={"name": "Asha"}).json()["content"], "{\"x\": 1}")
        self.assertEqual(self.c.put("/api/auth/chart", json={"name": "", "content": "{}"}).status_code, 422)
        self.signup("b@example.com")   # another account sees none of it
        self.assertEqual(self.c.get("/api/auth/charts").json(), [])
        self.assertEqual(self.c.get("/api/auth/chart", params={"name": "Asha"}).status_code, 404)
        self.c.post("/api/auth/login", json={"email": "a@example.com", "password": "lotus-feet"})
        s_file = '{"name": "Asha", "birth": {"year": 1990, "month": 3, "day": 12, "hour_local": 6.5}, "meta": {"city": "Pune"}, "notes": ""}'
        self.c.put("/api/auth/chart", json={"name": "Asha", "content": s_file})
        self.c.put("/api/auth/chart", json={"name": "Other", "content": "{}"})
        listed = {r["name"]: r for r in self.c.get("/api/auth/charts").json()}
        self.assertEqual((listed["Asha"]["year"], listed["Asha"]["place"]), (1990, "Pune"))
        self.assertEqual((listed["Asha"]["city"], listed["Asha"]["noteText"], listed["Asha"]["gender"]), ("Pune", "", 0))   # what the app compares
        self.assertNotIn("year", listed["Other"])   # unreadable: listed, without details
        self.assertEqual(self.c.post("/api/auth/chart/rename", json={"old": "Asha", "new": "Other"}).status_code, 409)   # taken
        self.assertEqual(self.c.post("/api/auth/chart/rename", json={"old": "Asha", "new": "Asha D"}).status_code, 200)
        self.assertIn('"Asha D"', self.c.get("/api/auth/chart", params={"name": "Asha D"}).json()["content"])
        self.c.delete("/api/auth/chart", params={"name": "Other"})
        self.c.delete("/api/auth/chart", params={"name": "Asha D"})
        self.assertEqual(self.c.get("/api/auth/charts").json(), [])

    def test_new_account_starts_with_the_sample_charts(self):
        auth.SAMPLES = self.samples
        self.signup()
        self.c.put("/api/auth/chart", json={"name": "Asha", "content": "{}"})
        mine = self.c.get("/api/auth/charts").json()
        self.assertEqual(len(mine), 19)
        samples = {r["name"]: r for r in mine if r.get("category") == "Sample charts"}
        self.assertEqual(len(samples), 18)
        self.assertIn("PVR Narasimha Rao", samples)               # the file "Author of this software"
        self.assertEqual(samples["Swami Vivekananda"]["year"], 1863)
        self.signup("b@example.com")                              # another account: the samples, nothing of the first one's
        theirs = [r["name"] for r in self.c.get("/api/auth/charts").json()]
        self.assertEqual(sorted(theirs), sorted(samples))
        self.c.delete("/api/auth/chart", params={"name": "India"})   # its own: deleting one leaves the first account's
        self.c.post("/api/auth/login", json={"email": "a@example.com", "password": "lotus-feet"})
        self.assertIn("India", [r["name"] for r in self.c.get("/api/auth/charts").json()])

    def test_browser_state_is_kept_per_account(self):
        self.assertIsNone(self.c.get("/api/auth/state").json())   # signed out: null, not a 401
        self.assertEqual(self.c.put("/api/auth/state", json={"changes": {"theme": "dark"}}).status_code, 401)
        self.signup()
        me = self.c.get("/api/auth/state").json()
        self.assertEqual(me["data"], {})
        self.c.put("/api/auth/state", json={"changes": {"theme": "dark", "chart.v2": "{}"}})
        self.c.put("/api/auth/state", json={"changes": {"theme": "light", "chart.v2": None}})   # overwrite, remove
        self.assertEqual(self.c.get("/api/auth/state").json()["data"], {"theme": "light"})
        self.assertEqual(self.c.put("/api/auth/state", json={"changes": {"": "x"}}).status_code, 422)
        too_big = {f"k{i}": "x" * 2 ** 20 for i in range(1)}
        old, auth.KEPT_MOST = auth.KEPT_MOST, 2 ** 20
        try:   # over the limit: refused, and nothing of it kept
            self.assertEqual(self.c.put("/api/auth/state", json={"changes": too_big}).status_code, 422)
        finally:
            auth.KEPT_MOST = old
        self.assertEqual(self.c.get("/api/auth/state").json()["data"], {"theme": "light"})
        self.signup("b@example.com")   # another account sees none of it, under another user
        other = self.c.get("/api/auth/state").json()
        self.assertEqual(other["data"], {})
        self.assertNotEqual(other["user"], me["user"])
        # a tab still showing the first account's page, now with this one's cookie: refused, nothing of it kept here
        self.assertEqual(self.c.put("/api/auth/state", json={"changes": {"recent": "[]"}, "user": me["user"]}).status_code, 409)
        self.assertEqual(self.c.put("/api/auth/state", json={"changes": {"theme": "dark"}, "user": other["user"]}).status_code, 200)
        self.assertEqual(self.c.get("/api/auth/state").json()["data"], {"theme": "dark"})

    def test_a_chart_keeps_its_category_when_saved_again(self):
        self.signup()
        s_file = '{"name": "India", "birth": {"year": 1947, "month": 8, "day": 15, "hour_local": 0.0}, "meta": {"city": "Delhi"}, "notes": ""%s}'
        self.c.put("/api/auth/chart", json={"name": "India", "content": s_file % ', "category": "Sample charts"'})
        self.assertEqual(self.c.get("/api/auth/charts").json()[0]["category"], "Sample charts")
        self.c.put("/api/auth/chart", json={"name": "India", "content": s_file % ""})   # the app's .vs carries none
        self.assertEqual(self.c.get("/api/auth/charts").json()[0]["category"], "Sample charts")
        self.c.put("/api/auth/chart", json={"name": "India", "content": s_file % ', "category": ""'})   # cleared on purpose
        self.assertEqual(self.c.get("/api/auth/charts").json()[0]["category"], "")

    def test_share_chart(self):
        def account(email, username):
            self.c.post("/api/auth/signup", json={"name": username.title(), "email": email, "password": "lotus-feet", "terms": auth.TERMS_VERSION, "username": username})
        account("b@example.com", "bina")
        account("a@example.com", "asha")
        self.c.put("/api/auth/chart", json={"name": "Ravi", "content": '{"birth": {"year": 1990, "month": 3, "day": 12}, "meta": {}}'})
        self.assertEqual([u["username"] for u in self.c.get("/api/auth/users", params={"q": "bi"}).json()], ["bina"])
        self.assertEqual(self.c.get("/api/auth/users", params={"q": "as"}).json(), [])     # not yourself
        self.assertEqual(self.c.get("/api/auth/users", params={"q": "%"}).json(), [])      # wildcards are literal
        self.assertEqual(self.c.post("/api/auth/chart/share", json={"name": "Ravi", "to": "nobody"}).status_code, 404)
        self.assertEqual(self.c.post("/api/auth/chart/share", json={"name": "Nope", "to": "bina"}).status_code, 404)
        self.assertEqual(self.c.post("/api/auth/chart/share", json={"name": "Ravi", "to": "asha"}).status_code, 400)
        self.assertEqual(self.c.post("/api/auth/chart/share", json={"name": "Ravi", "to": "@Bina"}).json()["to"], "bina")
        self.c.post("/api/auth/chart/share", json={"name": "Ravi", "to": "bina"})   # again: replaces, not a second copy
        self.assertEqual(self.c.get("/api/auth/shared").json(), [])                 # the sender's own list is empty
        self.c.post("/api/auth/login", json={"email": "b@example.com", "password": "lotus-feet"})
        [got] = self.c.get("/api/auth/shared").json()
        self.assertEqual((got["name"], got["from"], got["year"]), ("Ravi", "asha", 1990))
        self.assertIn("1990", self.c.get(f"/api/auth/shared/{got['id']}").json()["content"])
        self.c.delete(f"/api/auth/shared/{got['id']}")
        self.assertEqual(self.c.get("/api/auth/shared").json(), [])

    def test_terms_required(self):
        body = {"name": "Asha", "email": "t@example.com", "password": "lotus-feet"}
        self.assertEqual(self.c.post("/api/auth/signup", json=body).status_code, 422)
        self.assertEqual(self.c.post("/api/auth/signup", json={**body, "terms": 1}).status_code, 409)   # an older text
        self.assertEqual(self.c.post("/api/auth/signup", json={**body, "terms": auth.TERMS_VERSION}).status_code, 200)

    def test_too_many_wrong_passwords(self):
        self.signup()
        self.c.cookies.clear()
        for _ in range(auth.TRIES):
            self.assertEqual(self.c.post("/api/auth/login", json={"email": "a@example.com", "password": "wrong-one"}).status_code, 401)
        self.assertEqual(self.c.post("/api/auth/login", json={"email": "a@example.com", "password": "lotus-feet"}).status_code, 429)

    def test_change_name_and_username(self):
        self.signup()
        r = self.c.put("/api/auth/account", json={"name": " Asha D ", "username": "asha"})
        self.assertEqual((r.status_code, r.json()["name"], r.json()["username"]), (200, "Asha D", "asha"))
        self.assertEqual(self.c.put("/api/auth/account", json={"name": "", "username": ""}).status_code, 422)
        self.c.cookies.clear()
        self.signup("b@example.com")
        self.assertEqual(self.c.put("/api/auth/account", json={"name": "B", "username": "ASHA"}).status_code, 409)

    def test_change_password_signs_out_other_devices(self):
        self.signup()
        other = TestClient(app)
        other.post("/api/auth/login", json={"email": "a@example.com", "password": "lotus-feet"})
        self.assertEqual(self.c.put("/api/auth/password", json={"current": "wrong-one", "new": "new-lotus"}).status_code, 401)
        self.assertEqual(self.c.put("/api/auth/password", json={"current": "lotus-feet", "new": "short"}).status_code, 422)
        self.assertEqual(self.c.put("/api/auth/password", json={"current": "lotus-feet", "new": "new-lotus"}).status_code, 200)
        self.assertIsNotNone(self.c.get("/api/auth/me").json())   # this device stays in
        self.assertIsNone(other.get("/api/auth/me").json())
        self.assertEqual(other.post("/api/auth/login", json={"email": "a@example.com", "password": "new-lotus"}).status_code, 200)

    def test_logout_all_and_delete(self):
        self.signup()
        self.c.put("/api/auth/chart", json={"name": "Asha", "content": "{}"})
        other = TestClient(app)
        other.post("/api/auth/login", json={"email": "a@example.com", "password": "lotus-feet"})
        self.c.post("/api/auth/logout-all")
        self.assertIsNone(other.get("/api/auth/me").json())
        self.c.post("/api/auth/login", json={"email": "a@example.com", "password": "lotus-feet"})
        self.assertEqual(self.c.request("DELETE", "/api/auth/account", json={"password": "wrong-one"}).status_code, 401)
        self.assertEqual(self.c.request("DELETE", "/api/auth/account", json={"password": "lotus-feet"}).status_code, 200)
        self.assertEqual(self.c.post("/api/auth/login", json={"email": "a@example.com", "password": "lotus-feet"}).status_code, 401)
        self.assertEqual(self.signup().status_code, 200)   # the email is free again, with nothing left behind
        self.assertEqual(self.c.get("/api/auth/charts").json(), [])

    def test_owner_reset(self):
        self.signup()
        self.assertTrue(auth.reset_password("A@example.com", "fresh-lotus"))
        self.assertIsNone(self.c.get("/api/auth/me").json())   # signed out everywhere
        self.assertEqual(self.c.post("/api/auth/login", json={"email": "a@example.com", "password": "fresh-lotus"}).status_code, 200)
        self.assertFalse(auth.reset_password("nobody@example.com", "fresh-lotus"))

    def test_password_not_stored_plain(self):
        h = auth.hash_password("lotus-feet")
        self.assertNotIn("lotus-feet", h)
        self.assertTrue(auth.check_password("lotus-feet", h))
        self.assertFalse(auth.check_password("lotus-fee", h))
        self.assertFalse(auth.check_password("x", None))

    def test_older_hash_redone_at_sign_in(self):
        self.signup()
        p, auth.P = auth.P, 1   # the cost before OWASP's minimum
        try:
            old = auth.hash_password("lotus-feet")
        finally:
            auth.P = p
        with auth._db() as c:
            c.execute("UPDATE users SET password_hash = ?", (old,))
        self.c.cookies.clear()
        self.assertEqual(self.c.post("/api/auth/login", json={"email": "a@example.com", "password": "lotus-feet"}).status_code, 200)
        with auth._db() as c:
            self.assertTrue(c.execute("SELECT password_hash FROM users").fetchone()[0].startswith(f"scrypt${auth.N}${auth.R}${auth.P}$"))

    def test_sessions_kept_as_digests(self):
        self.signup()
        token = self.c.cookies["sid"]
        with auth._db() as c:
            [stored] = [r[0] for r in c.execute("SELECT token FROM sessions")]
        self.assertEqual(stored, hashlib.sha256(token.encode()).hexdigest())
        stolen = TestClient(app)
        stolen.cookies.set("sid", stored)   # a copy of the database signs no one in
        self.assertIsNone(stolen.get("/api/auth/me").json())

    def test_older_sessions_still_sign_in(self):
        self.signup()
        token = self.c.cookies["sid"]
        with auth._db() as c:   # as a server before digests kept it: the token itself
            c.execute("UPDATE sessions SET token = ?", (token,))
            c.execute("PRAGMA user_version = 0")
        self.assertEqual(self.me()["email"], "a@example.com")
        with auth._db() as c:
            self.assertEqual(c.execute("SELECT token FROM sessions").fetchone()[0], hashlib.sha256(token.encode()).hexdigest())

    def test_too_many_signups_from_one_address(self):
        for i in range(auth.SIGNUPS):
            self.assertEqual(self.signup(f"s{i}@example.com").status_code, 200)
        self.assertEqual(self.signup("one-more@example.com").status_code, 429)

    def test_room_per_account(self):
        self.c.post("/api/auth/signup", json={"name": "Bina", "email": "b@example.com", "password": "lotus-feet", "terms": auth.TERMS_VERSION, "username": "bina"})
        self.signup()
        most, auth.MOST = auth.MOST, 2
        try:
            for n in ("A", "B"):
                self.assertEqual(self.c.put("/api/auth/chart", json={"name": n, "content": "{}"}).status_code, 200)
            self.assertEqual(self.c.put("/api/auth/chart", json={"name": "C", "content": "{}"}).status_code, 422)
            self.assertEqual(self.c.put("/api/auth/chart", json={"name": "B", "content": "{\"x\": 1}"}).status_code, 200)   # overwriting is fine
            auth.MOST = 0   # nothing new fits anywhere: each table's check runs its query
            self.assertEqual(self.c.put("/api/auth/facts", json={"key": "k", "data": {}}).status_code, 422)
            self.assertEqual(self.c.post("/api/auth/chart/share", json={"name": "A", "to": "bina"}).status_code, 422)
        finally:
            auth.MOST = most


class TestOAuth(unittest.TestCase):
    """Sign in with a provider, with the provider's side faked (auth._fetch) and its app switched on in the environment."""
    signup = TestAuth.signup   # borrowed, not inherited, so TestAuth's tests don't run twice
    me = TestAuth.me

    def setUp(self):
        TestAuth.setUp(self)
        self.env = dict(os.environ)
        os.environ.update(OAUTH_GOOGLE_ID="id", OAUTH_GOOGLE_SECRET="secret")
        self.real_fetch, self.info = auth._fetch, {"email": "g@example.com", "email_verified": True, "name": "Gita"}
        auth._fetch = lambda url, data=None, token=None: {"access_token": "t"} if data else self.info

    def tearDown(self):
        auth._fetch = self.real_fetch
        os.environ.clear(); os.environ.update(self.env)
        TestAuth.tearDown(self)

    def start(self, back="?verses"):
        r = self.c.get("/api/auth/oauth/google", params={"back": back}, follow_redirects=False)
        self.assertEqual(r.status_code, 303)
        return r, dict(p.split("=", 1) for p in r.headers["location"].split("?", 1)[1].split("&"))["state"]

    def test_new_account_starts_with_the_sample_charts(self):
        auth.SAMPLES = self.samples
        _, state = self.start()
        self.c.get("/api/auth/oauth/google/callback", params={"code": "c", "state": state})
        self.assertEqual({r.get("category") for r in self.c.get("/api/auth/charts").json()}, {"Sample charts"})
        self.assertEqual(len(self.c.get("/api/auth/charts").json()), 18)

    def test_round_trip_makes_then_reuses_account(self):
        _, state = self.start()
        r = self.c.get("/api/auth/oauth/google/callback", params={"code": "c", "state": state}, follow_redirects=False)
        self.assertEqual(r.headers["location"], "/?verses")
        self.assertEqual(self.me(), {"name": "Gita", "email": "g@example.com", "home": None})
        self.assertEqual(self.c.get("/api/samples").status_code, 200)   # no Terms gate after a social sign-in
        # someone signs up with p@example.com and a password, never proving the address is theirs (account pre-hijacking)
        squatter = TestClient(app)
        squatter.post("/api/auth/signup", json={"name": "Asha", "email": "p@example.com", "password": "lotus-feet", "terms": auth.TERMS_VERSION})
        self.c.cookies.clear()
        self.info = {"email": "P@example.com", "email_verified": True, "name": "Other"}
        _, state = self.start()
        self.c.get("/api/auth/oauth/google/callback", params={"code": "c", "state": state})
        self.assertEqual(self.me(), {"name": "Asha", "email": "p@example.com", "home": None})   # the account is joined by its email
        self.assertFalse(self.c.get("/api/auth/me").json()["hasPassword"])                      # without the password set at sign-up
        self.assertIsNone(squatter.get("/api/auth/me").json())                                  # and whoever set it is signed out
        self.assertEqual(squatter.post("/api/auth/login", json={"email": "p@example.com", "password": "lotus-feet"}).status_code, 401)

    def test_verified_account_keeps_its_password(self):
        _, state = self.start()
        self.c.get("/api/auth/oauth/google/callback", params={"code": "c", "state": state})   # made through Google
        self.assertEqual(self.c.put("/api/auth/password", json={"current": "", "new": "set-later"}).status_code, 200)
        self.c.cookies.clear()
        _, state = self.start()
        self.c.get("/api/auth/oauth/google/callback", params={"code": "c", "state": state})
        self.c.cookies.clear()
        self.assertEqual(self.c.post("/api/auth/login", json={"email": "g@example.com", "password": "set-later"}).status_code, 200)

    def test_pkce(self):
        sent = {}

        def fetch(url, data=None, token=None):
            sent.update(data or {})
            return {"access_token": "t"} if data else self.info
        auth._fetch = fetch
        r, state = self.start()
        q = urllib.parse.parse_qs(urllib.parse.urlsplit(r.headers["location"]).query)
        self.c.get("/api/auth/oauth/google/callback", params={"code": "c", "state": state})
        challenge = base64.urlsafe_b64encode(hashlib.sha256(sent["code_verifier"].encode()).digest()).rstrip(b"=").decode()
        self.assertEqual((q["code_challenge"], q["code_challenge_method"]), ([challenge], ["S256"]))
        self.assertEqual(self.me()["email"], "g@example.com")

    def test_state_must_match(self):
        self.start()
        r = self.c.get("/api/auth/oauth/google/callback", params={"code": "c", "state": "forged"}, follow_redirects=False)
        self.assertIn("auth_error", r.headers["location"])
        self.assertIsNone(self.c.get("/api/auth/me").json())

    def test_unverified_email_refused(self):
        self.info = {"email": "g@example.com", "email_verified": False}
        _, state = self.start()
        r = self.c.get("/api/auth/oauth/google/callback", params={"code": "c", "state": state}, follow_redirects=False)
        self.assertIn("no+verified+email", r.headers["location"])
        self.assertIsNone(self.c.get("/api/auth/me").json())

    def test_microsoft_takes_its_email(self):   # Microsoft's userinfo has no email_verified: personal accounts' emails are
        os.environ.update(OAUTH_MICROSOFT_ID="id", OAUTH_MICROSOFT_SECRET="secret")
        self.info = {"email": "m@outlook.com", "name": "Mira"}
        r = self.c.get("/api/auth/oauth/microsoft", follow_redirects=False)
        self.assertIn("login.microsoftonline.com/consumers/", r.headers["location"])
        state = dict(p.split("=", 1) for p in r.headers["location"].split("?", 1)[1].split("&"))["state"]
        self.c.get("/api/auth/oauth/microsoft/callback", params={"code": "c", "state": state})
        self.assertEqual(self.me(), {"name": "Mira", "email": "m@outlook.com", "home": None})

    def test_unconfigured_and_offsite_back(self):
        r = self.c.get("/api/auth/oauth/microsoft", params={"back": "//evil.example"}, follow_redirects=False)
        self.assertTrue(r.headers["location"].startswith("/?auth_error="))   # back dropped: never leaves this site
        self.assertEqual(self.c.get("/api/auth/oauth/myspace", follow_redirects=False).status_code, 404)


if __name__ == "__main__":
    unittest.main()
