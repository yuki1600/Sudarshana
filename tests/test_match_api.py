
import urllib.request
import urllib.parse
import json
import sys

BASE_URL = "http://localhost:8000"

def test_match_endpoint():
    print("Testing /match endpoint...")
    
    # Boy: 1990-01-01 10:00 Chennai
    # Girl: 1992-05-15 14:30 Bangalore
    params = {
        "b_date": "1990-01-01",
        "b_time": "10:00",
        "b_lat": 13.0827,
        "b_lon": 80.2707,
        "b_tz": "Asia/Kolkata",
        "g_date": "1992-05-15",
        "g_time": "14:30",
        "g_lat": 12.9716,
        "g_lon": 77.5946,
        "g_tz": "Asia/Kolkata",
        "ayanamsa": "Lahiri"
    }
    
    query_string = urllib.parse.urlencode(params)
    url = f"{BASE_URL}/match?{query_string}"
    
    try:
        with urllib.request.urlopen(url) as response:
            status = response.getcode()
            print(f"Status Code: {status}")
            
            data = json.loads(response.read().decode())
            print("Response JSON:")
            print(json.dumps(data, indent=2))
            
            # Simple assertions
            assert "total_score" in data
            assert "kutas" in data
            assert data["boy_nak"] is not None
            assert data["girl_nak"] is not None
            print("SUCCESS: /match endpoint working and returning valid data.")
            
    except urllib.error.HTTPError as e:
        print(f"FAILED: Endpoint returned {e.code}")
        print(e.read().decode())
    except Exception as e:
        print(f"ERROR: Could not connect to server or parse response. {e}")
        # Helpful hint if server is possibly down
        print("Hint: Ensure the server (app.py) is running on localhost:8000")

if __name__ == "__main__":
    test_match_endpoint()
