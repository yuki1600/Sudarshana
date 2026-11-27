"""Finance tab: Yahoo/CCXT OHLC routing and astrology event overlays."""
import unittest
from datetime import datetime, timezone

from fastapi.testclient import TestClient

from server.app import app

client = TestClient(app)
BIRTH = {
    "year": 1863, "month": 1, "day": 12, "hour_local": 6.0, "tz_east_hours": 5.5,
    "longitude_east": 80.27, "latitude": 13.08, "altitude_m": 0, "gregorian": True, "place": "Chennai",
}


def post(url, birth=BIRTH, **body):
    r = client.post(url, json={"birth": birth, **body})
    assert r.status_code == 200, r.text
    return r.json()


class FinanceApi(unittest.TestCase):
    def test_ohlc_rejects_empty(self):
        self.assertEqual(client.post("/api/finance/ohlc", json={"symbol": ""}).status_code, 422)

    def test_ohlc_yahoo_aapl(self):
        r = client.post("/api/finance/ohlc", json={"symbol": "AAPL", "range": "1mo", "interval": "1d"})
        self.assertEqual(r.status_code, 200, r.text)
        body = r.json()
        self.assertEqual(body["source"], "yahoo")
        self.assertGreaterEqual(len(body["bars"]), 5)
        self.assertIn("c", body["bars"][0])
        self.assertIn("t", body["bars"][0])

    def test_ohlc_ccxt_pair(self):
        r = client.post("/api/finance/ohlc", json={"symbol": "BTC/USDT", "range": "1mo", "interval": "1d"})
        self.assertEqual(r.status_code, 200, r.text)
        body = r.json()
        self.assertEqual(body["source"], "ccxt")
        self.assertGreaterEqual(len(body["bars"]), 5)

    def test_events_ingress(self):
        end = datetime(2000, 3, 1, tzinfo=timezone.utc)
        start = datetime(2000, 1, 1, tzinfo=timezone.utc)
        rows = post("/api/finance/events",
                    start_ms=int(start.timestamp() * 1000),
                    end_ms=int(end.timestamp() * 1000),
                    kinds=["ingress", "eclipse"])
        self.assertTrue(any(e["kind"] == "ingress" for e in rows), rows[:3])
        self.assertTrue(all("t" in e and "label" in e for e in rows))


if __name__ == "__main__":
    unittest.main()
