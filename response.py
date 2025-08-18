from data import get_team_games, get_game_odds
from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta
load_dotenv()

prefProvider = "ESPN Bet"

async def build_odds_response(raw_input: str):
    """
    Behaviors:
      - "!odds TeamA, TeamB" => specific matchup odds (unchanged)
      - "!odds Team"         => next upcoming game only
      - "!odds Team *"       => every game with odds (previous single-team behavior)
    Output formatting matches the existing bot exactly.
    """
    raw = (raw_input or "").strip()


    def _parse_dt(iso_str):
        """Parse startDate ISO strings; treat naive as UTC."""
        if not iso_str:
            return None
        try:
            iso_norm = iso_str.replace("Z", "+00:00")
            dt = datetime.fromisoformat(iso_norm)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except Exception:
            return None

    def _favorites_from_lines(lines):
        """Return list like ['home','away',...] from moneylines; used to detect conflict."""
        favs = []
        for ln in lines:
            home_ml = ln.get("homeMoneyline")
            away_ml = ln.get("awayMoneyline")
            if home_ml is not None and away_ml is not None:
                favs.append("home" if home_ml < away_ml else "away")
        return favs

    def _select_line(lines):
        """Pick preferred line by provider, else the first."""
        if not lines:
            return None
        for ln in lines:
            if ln.get("provider") == prefProvider:
                return ln
        return lines[0]

    # ---------- Specific game: "Team A, Team B" ----------
    if "," in raw:
        try:
            team1, team2 = [t.strip().title() for t in raw.split(",", 1)]
            games = await get_team_games(team1)
            game = next((g for g in games if g.get("homeTeam") == team2 or g.get("awayTeam") == team2), None)
            if not game:
                return f"❌ Couldn't find a 2025 game between {team1} and {team2}."

            odds_data = await get_game_odds(game["id"])
            if not odds_data:
                return f"✅ Found game: {game['awayTeam']} @ {game['homeTeam']} — {game['startDate'][:10]}, but no odds posted yet."

            lines_list = odds_data[0]["lines"] if odds_data and "lines" in odds_data[0] else []
            if not lines_list:
                return f"✅ Found game: {game['awayTeam']} @ {game['homeTeam']}, but no valid lines yet."

            favorites = _favorites_from_lines(lines_list)
            conflict_warning = "⚠️ Books disagree on favorite\n" if len(set(favorites)) > 1 else None

            selected_line = _select_line(lines_list)
            provider = selected_line.get("provider", "Unknown")

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
            msg += f"Book: {provider}\n"
            if conflict_warning:
                msg += f"{conflict_warning}"
            msg += "\n"
            if spread is not None:
                if spread_team:
                    msg += f"Spread: {spread_team:} {spread:+}\n"
                else:
                    # Use moneyline to identify favorite, fallback to spread sign
                    if home_ml is not None and away_ml is not None:
                        favorite = home if home_ml < away_ml else away
                    else:
                        favorite = home if spread < 0 else away
                    msg += f"Spread: {favorite:} {-abs(spread):+.1f}\n"
            if home_ml is not None and away_ml is not None:
                msg += f"ML: {home:} {home_ml:+} | {away:} {away_ml:+}\n"
            if over_under is not None:
                msg += f"O/U: {over_under}"
            msg += "\n```"
            return msg
        except Exception:
            return "Usage limits hit, try again later."

    # ---------- Single team: upcoming or all ----------
    try:
        wants_all = raw.endswith("*")
        team = raw.rstrip("*").strip().title()

        games = await get_team_games(team)
        if not games:
            return f"❌ No games found for {team}."

        if not wants_all:
            # Upcoming only
            now = datetime.now(timezone.utc) - timedelta(hours=24)
            future_games = [g for g in games if _parse_dt(g.get("startDate")) and _parse_dt(g.get("startDate")) >= now]
            game = min(future_games, key=lambda g: _parse_dt(g.get("startDate"))) if future_games else None
            if not game:
                return f"✅ No upcoming game for {team}."

            odds_data = await get_game_odds(game["id"])
            if not odds_data:
                return f"✅ Found upcoming game: {game['awayTeam']} @ {game['homeTeam']} — {game['startDate'][:10]}, but no odds posted yet."

            lines_list = odds_data[0]["lines"] if odds_data and "lines" in odds_data[0] else []
            if not lines_list:
                return f"✅ Found upcoming game: {game['awayTeam']} @ {game['homeTeam']}, but no valid lines yet."

            favorites = _favorites_from_lines(lines_list)
            conflict_warning = "⚠️ Books disagree on favorite\n" if len(set(favorites)) > 1 else None

            selected_line = _select_line(lines_list)
            provider = selected_line.get("provider", "Unknown")

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
            msg += f"Book: {provider}\n"
            if conflict_warning:
                msg += f"{conflict_warning}"
            msg += "\n"
            if spread is not None:
                if spread_team:
                    msg += f"Spread: {spread_team:} {spread:+}\n"
                else:
                    if home_ml is not None and away_ml is not None:
                        favorite = home if home_ml < away_ml else away
                    else:
                        favorite = home if spread < 0 else away
                    msg += f"Spread: {favorite:} {-abs(spread):+.1f}\n"
            if home_ml is not None and away_ml is not None:
                msg += f"ML: {home:} {home_ml:+} | {away:} {away_ml:+}\n"
            if over_under is not None:
                msg += f"O/U: {over_under}"
            msg += "\n```"
            return msg

        # '*' suffix => every game (previous behavior)
        header = f"2025 Odds for {team}"
        lines = [header]

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

            favorites = _favorites_from_lines(lines_list)
            conflict_warning = "  ⚠️ Books disagree on favorite" if len(set(favorites)) > 1 else None

            selected_line = _select_line(lines_list)
            provider = selected_line.get("provider", "Unknown")
            spread = selected_line.get("spread")
            spread_team = selected_line.get("spreadTeam")
            over_under = selected_line.get("overUnder")
            home_ml = selected_line.get("homeMoneyline")
            away_ml = selected_line.get("awayMoneyline")

            matchup = f"• {away} @ {home} — {date}"
            details = []
            details.append(f"Book: {provider}")
            if conflict_warning:
                details.append(conflict_warning)
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

        return "```\n" + "\n\n".join(lines) + "\n```"

    except Exception:
        return "Usage limits hit, try again later."
