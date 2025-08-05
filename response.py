from data import get_team_games, get_game_odds
from dotenv import load_dotenv
load_dotenv()

prefProvider = "ESPN Bet"
async def build_odds_response(raw_input):
    if ',' in raw_input:
        try:
            team1, team2 = [t.strip().title() for t in raw_input.split(',', 1)]

            games = await get_team_games(team1)
            game = next((g for g in games if g["homeTeam"] == team2 or g["awayTeam"] == team2), None)

            if not game:
                return f"❌ Couldn't find a 2025 game between {team1} and {team2}."

            odds_data = await get_game_odds(game["id"])

            if not odds_data:
                return f"✅ Found game: {game['awayTeam']} @ {game['homeTeam']} — {game['startDate'][:10]}, but no odds posted yet."

            lines_list = odds_data[0]["lines"] if odds_data and "lines" in odds_data[0] else []
            if not lines_list:
                return f"✅ Found game: {game['awayTeam']} @ {game['homeTeam']}, but no valid lines yet."

            # Grab preferred line
            selected_line = next((l for l in lines_list if l.get("provider") == prefProvider), lines_list[0])
            provider = selected_line["provider"] if "provider" in selected_line else "Unknown"

            # Now extract the rest
            spread = selected_line.get("spread")
            spread_team = selected_line.get("spreadTeam")
            over_under = selected_line.get("overUnder")
            home_ml = selected_line.get("homeMoneyline")
            away_ml = selected_line.get("awayMoneyline")

            date = game.get("startDate", "")[:10]
            home = game.get("homeTeam")
            away = game.get("awayTeam")

            msg = f"```"
            msg += f"{away} @ {home} - {date}\n"
            msg += f"Source: {provider}\n"
            msg += "\n"
            if spread is not None:
                if spread_team:
                    msg += f"Spread: {spread_team:} {spread:+}\n"
                else:
                    # Use moneyline to identify favorite
                    if home_ml is not None and away_ml is not None:
                        if home_ml < away_ml:
                            favorite = home
                        else:
                            favorite = away
                    else:
                        favorite = home if spread < 0 else away  # fallback

                    # Force display as "Favorite -abs(spread)"
                    msg += f"Spread: {favorite:} {-abs(spread):+.1f}\n"
            if home_ml is not None and away_ml is not None:
                msg += f"ML: {home:} {home_ml:+} | {away:} {away_ml:+}\n"
            if over_under is not None:
                msg += f"O/U: {over_under}"

            msg += "\n```"
            return msg
        except:
            msg = "Usage limits hit, try again later."
            return msg
    else:
        # Handle team-only: show all games with odds
        team = raw_input.strip().title()
        games = await get_team_games(team)

        if not games:
            return f"❌ No games found for {team}."

        header = f"2025 Odds for {team}"
        lines = [header]

        try:
            for game in games:

                game_id = game.get("id")
                date = game.get("startDate", "")[:10]
                home = game.get("homeTeam", "Unknown")
                away = game.get("awayTeam", "Unknown")

                odds_data = await get_game_odds(game_id)
                if not odds_data:
                    continue

                lines_list = odds_data[0]["lines"] if odds_data and "lines" in odds_data[0] else []
                if not lines_list:
                    continue

                selected_line = next((l for l in lines_list if l.get("provider") == prefProvider), lines_list[0])

                provider = selected_line.get("provider", "Unknown")
                spread = selected_line.get("spread")
                spread_team = selected_line.get("spreadTeam")
                over_under = selected_line.get("overUnder")
                home_ml = selected_line.get("homeMoneyline")
                away_ml = selected_line.get("awayMoneyline")

                matchup = f"• {away} @ {home} — {date}"
                details = []
                details.append(f"Book: {provider}")
                if spread is not None:
                    if spread_team:
                        details.append(f"  Spread: {spread_team} {spread:+}")
                    else:
                        if home_ml is not None and away_ml is not None:
                            favorite = home if home_ml < away_ml else away
                        else:
                            favorite = home if spread < 0 else away

                        details.append(f"  Spread: {favorite} {-abs(spread):+.1f}")

                if home_ml is not None and away_ml is not None:
                    details.append(f"  ML: {home} {home_ml:+} | {away} {away_ml:+}")
                if over_under is not None:
                    details.append(f"  O/U: {over_under}")

                lines.append(f"{matchup}\n  " + "\n".join(details))
        except:
            msg = "Usage limits hit, try again later."
            return msg

        return "```\n" + "\n\n".join(lines) + "\n```"


