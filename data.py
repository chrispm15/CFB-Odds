import os
import aiohttp
from dotenv import load_dotenv
load_dotenv()

CFB_API_KEY = os.getenv("CFB_API_KEY")
BASE_URL = "https://api.collegefootballdata.com"
HEADERS = {"Authorization": f"Bearer {CFB_API_KEY}"}

async def get_team_games(team):
    url = f"{BASE_URL}/games"
    params = {"year": 2025, "team": team, "seasonType": "regular"}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=HEADERS, params=params) as resp:
            result = await resp.text()
            return await resp.json()

async def get_game_odds(game_id):
    url = f"{BASE_URL}/lines"
    params = {"gameId": game_id}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=HEADERS, params=params) as resp:
            return await resp.json()
