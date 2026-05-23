import unittest
import json
from src.app import chart
from src.jyotisha.pipeline.chart import compute_chart


class TestRefactoredChart(unittest.TestCase):
    def test_compute_chart_success(self):
        # Compute chart for Chennai birth details
        res = compute_chart(
            y=1990, m=1, d=1, hh=10, mm=0, ss=0,
            lat=13.0827, lon=80.2707,
            ephe_path="ephe", use_moseph=False, ayanamsa="Lahiri"
        )
        
        # Verify essential chart properties
        self.assertIn("points", res)
        self.assertIn("shadbala", res)
        self.assertIn("aspect_grid", res)
        self.assertIn("bhava_bala", res)
        self.assertIn("avastha", res)

        # Check Shadbala DataFrame structure and values
        sb_df = res["shadbala"]
        self.assertEqual(len(sb_df), 7)
        self.assertIn("Planet", sb_df.columns)
        self.assertIn("Total (Rupa)", sb_df.columns)

        # Check Avastha DataFrame structure and values
        av_df = res["avastha"]
        self.assertEqual(len(av_df), 9)  # 7 planets + Rahu & Ketu
        self.assertIn("Planet", av_df.columns)
        self.assertIn("Baladi", av_df.columns)
        self.assertIn("Jagratadi", av_df.columns)
        self.assertIn("Deeptaadi", av_df.columns)
        self.assertIn("Lajjitadi", av_df.columns)
        self.assertIn("Shayanadi", av_df.columns)

        # Verify specific Baladi values for Sun (ex: 1990-01-01 Sun is in Sagittarius 16 deg, Sagittarius is odd, 16 deg -> Yuva)
        sun_row = av_df[av_df["Planet"] == "Sun"].iloc[0]
        self.assertEqual(sun_row["Baladi"], "Yuva")

    def test_chart_api_endpoint(self):
        # Directly call FastAPI endpoint function passing default arguments explicitly
        response = chart(
            date="1990-01-01",
            time="10:00",
            lat=13.0827,
            lon=80.2707,
            tz="Asia/Kolkata",
            house_sys="O",
            moseph=False,
            ayanamsa="Lahiri",
            name=None
        )
        # Parse JSON response payload
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.body.decode())
        self.assertIn("avastha", data)
        self.assertGreater(len(data["avastha"]), 0)
        
        # Check first avastha item
        av0 = data["avastha"][0]
        self.assertIn("Planet", av0)
        self.assertIn("Baladi", av0)
        self.assertIn("Jagratadi", av0)
        self.assertIn("Deeptaadi", av0)
        self.assertIn("Lajjitadi", av0)
        self.assertIn("Shayanadi", av0)
        print("FastAPI /chart avastha payload:", av0)


if __name__ == "__main__":
    unittest.main()
