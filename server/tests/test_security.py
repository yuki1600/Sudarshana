"""The site-wide guards (server/app/main.py): known hosts only, a cap on request bodies, the security headers, no API docs."""
import unittest

from fastapi.testclient import TestClient

from server.app import app, main


def client(base="http://127.0.0.1:8000"):
    return TestClient(app, base_url=base)


class TestSecurity(unittest.TestCase):
    def test_headers(self):
        r = client().get("/api/sky")
        self.assertEqual(r.status_code, 200)
        self.assertIn("frame-ancestors 'none'", r.headers["content-security-policy"])
        self.assertEqual((r.headers["x-content-type-options"], r.headers["x-frame-options"]), ("nosniff", "DENY"))
        self.assertNotIn("strict-transport-security", r.headers)   # plain http: HSTS would mean nothing
        self.assertIn("max-age", client("https://abc.trycloudflare.com").get("/api/sky").headers["strict-transport-security"])
        self.assertIn("content-security-policy", client().get("/api/samples").headers)   # on refusals and errors too

    def test_unknown_host_refused(self):
        self.assertEqual(client("http://evil.example").get("/api/sky").status_code, 400)   # DNS rebinding
        self.assertEqual(client("http://trycloudflare.com.evil.example").get("/").status_code, 400)
        self.assertEqual(client("https://abc.trycloudflare.com").get("/api/sky").status_code, 200)
        self.assertEqual(client("http://localhost:5173").get("/api/sky").status_code, 200)   # npm run dev's proxy
        self.assertEqual(client("http://10.0.0.7:8000").get("/healthz").json(), {"ok": True})   # a load balancer's probe
        self.assertFalse(main.host_ok("trycloudflare.com"))   # "*.x" is x's subdomains, not x

    def test_body_cap(self):
        self.assertEqual(client().post("/api/ini/parse", json={"content": ""}).status_code, 200)
        self.assertEqual(client().post("/api/ini/parse", json={"content": "x" * main.MAX_BODY}).status_code, 413)
        chunked = (b"x" * 2 ** 16 for _ in range(main.MAX_BODY // 2 ** 16 + 1))   # no Content-Length to go by
        r = client().post("/api/ini/parse", content=chunked, headers={"Content-Type": "application/json"})
        self.assertEqual(r.status_code, 413)

    def test_no_api_docs(self):
        for p in ("/docs", "/redoc", "/openapi.json"):
            self.assertEqual(client().get(p).status_code, 404, p)


if __name__ == "__main__":
    unittest.main()
