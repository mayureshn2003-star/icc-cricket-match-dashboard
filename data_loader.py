import requests
import pandas as pd

# Free Cricket API (e.g., CricAPI or RapidAPI Cricket endpoints)
API_KEY = "YOUR_API_KEY"  # Replace with your API key if using a live service

def fetch_live_matches():
    """
    Fetch live match list or mock live data.
    """
    url = f"https://api.cricapi.com/v1/currentMatches?apikey={API_KEY}&offset=0"
    try:
        response = requests.get(url)
        data = response.json()
        return data.get("data", [])
    except Exception as e:
        print("API Error:", e)
        return []

# Example mock match data for initial dashboard setup
def load_mock_match_data():
    over_data = pd.DataFrame({
        "Over": list(range(1, 21)),
        "India_Runs": [8, 15, 23, 31, 42, 50, 58, 65, 74, 85, 96, 108, 120, 135, 150, 162, 178, 190, 205, 218],
        "England_Runs": [6, 12, 18, 25, 38, 45, 52, 60, 71, 80, 89, 98, 110, 122, 138, 149, 160, 175, 188, 211],
        "India_Wickets": [0, 0, 1, 1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 4, 5, 5, 6, 7, 7],
        "England_Wickets": [1, 1, 2, 2, 2, 3, 3, 4, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8, 9, 10]
    })
    return over_data