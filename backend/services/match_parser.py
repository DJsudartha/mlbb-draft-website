def extract_list(prefix: str, count: int, source: dict) -> list[str]:
    values = []
    for i in range(1, count + 1):
        value = source.get(f"{prefix}{i}")
        if value:
            values.append(value)
    return values

def parse_and_normalize_matches(data: dict) -> list[dict]:
    games = []
    matches = data.get("result", [])
    for match in matches:
        for game in match.get("match2games", []):
            extradata = game.get("extradata", {})

            team1_side = extradata.get("team1side")
            team2_side = extradata.get("team2side")
            game_winner = game.get("winner")

            team1_picks = extract_list("team1champion", 5, extradata)
            team2_picks = extract_list("team2champion", 5, extradata)
            team1_bans = extract_list("team1ban", 5, extradata)
            team2_bans = extract_list("team2ban", 5, extradata)

            if len(team1_picks) != 5 or len(team2_picks) != 5:
                continue

            if team1_side == "blue":
                blue_team_heroes = team1_picks
                red_team_heroes = team2_picks
                blue_team_bans = team1_bans
                red_team_bans = team2_bans
                winner = "blue" if game_winner == "1" else "red"
            elif team1_side == "red":
                blue_team_heroes = team2_picks
                red_team_heroes = team1_picks
                blue_team_bans = team2_bans
                red_team_bans = team1_bans
                winner = "red" if game_winner == "1" else "blue"
            else:
                continue
            
            
            normalized_game = {
                "tournament": match.get("tournament"),
                "pagename": match.get("pagename"),
                "date": game.get("date") or match.get("date"),
                "patch": game.get("patch") or match.get("patch"),
                "blue_team_name": match.get("match2opponents", [{}, {}])[0].get("name"),
                "red_team_name": match.get("match2opponents", [{}, {}])[1].get("name"),
                "blue_team": blue_team_heroes,
                "red_team": red_team_heroes,
                "blue_bans": blue_team_bans,
                "red_bans": red_team_bans,
                "winner": winner,
            }
            games.append(normalized_game)

    return games