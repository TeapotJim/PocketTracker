
import csv
import json
from datetime import datetime, timedelta
import pandas as pd

def load_logs(filepath):
    with open(filepath, newline='') as csvfile:
        return list(csv.DictReader(csvfile))

def calculate_snapshot(logs):
    df = pd.DataFrame(logs)
    df["date"] = pd.to_datetime(df["date"])
    df["wins"] = df["wins"].astype(int)
    df["losses"] = df["losses"].astype(int)
    df["points"] = df["points"].astype(int)

    today = datetime.now().date()
    yesterday = today - timedelta(days=1)

    # Daily aggregates
    df_yesterday = df[df["date"].dt.date == yesterday]
    wins_y = df_yesterday["wins"].sum()
    losses_y = df_yesterday["losses"].sum()
    points_y = df_yesterday["points"].sum()
    games_y = wins_y + losses_y
    win_rate_y = (wins_y / games_y * 100) if games_y > 0 else 0
    ppg_y = (points_y / games_y) if games_y > 0 else 0

    # Season totals
    total_wins = df["wins"].sum()
    total_losses = df["losses"].sum()
    total_points = df["points"].sum()
    total_games = total_wins + total_losses
    season_win_rate = (total_wins / total_games * 100) if total_games > 0 else 0
    season_avg_ppg = (total_points / total_games) if total_games > 0 else 0

    # 7-day ranges
    df_sorted = df.sort_values("date")
    df_last14 = df_sorted[df_sorted["date"] >= pd.to_datetime(today - timedelta(days=14))]
    df_7 = df_last14[df_last14["date"] >= pd.to_datetime(today - timedelta(days=7))]
    df_prev7 = df_last14[df_last14["date"] < pd.to_datetime(today - timedelta(days=7))]

    wins_7 = df_7["wins"].sum()
    losses_7 = df_7["losses"].sum()
    points_7 = df_7["points"].sum()
    days_played_7 = 7
    avg_games_per_day_7 = (wins_7 + losses_7) / days_played_7
    win_rate_7 = (wins_7 / (wins_7 + losses_7) * 100) if (wins_7 + losses_7) > 0 else 0

    wins_prev = df_prev7["wins"].sum()
    losses_prev = df_prev7["losses"].sum()
    avg_games_per_day_prev = (wins_prev + losses_prev) / 7 if not df_prev7.empty else 0

    return {
        "yesterday": {
            "points": points_y,
            "win_percent": round(win_rate_y, 1),
            "ppg": round(ppg_y, 2),
            "trend_points": "up" if ppg_y > season_avg_ppg else "down",
            "trend_winrate": "up" if win_rate_y > season_win_rate else "down"
        },
        "7_day": {
            "avg_games": round(avg_games_per_day_7, 2),
            "avg_win_percent": round(win_rate_7, 1),
            "trend_games": "up" if avg_games_per_day_7 > avg_games_per_day_prev else "down",
            "trend_winrate": "up" if win_rate_7 > season_win_rate else "down"
        },
        "overall_avg_games": round(avg_games_per_day_prev, 2),
        "overall_avg_win_percent": round(season_win_rate, 1),
        "season_avg_ppg": round(season_avg_ppg, 2)
    }

logs = load_logs("data/daily_log.csv")
snapshot = calculate_snapshot(logs)

with open("data/trend_snapshot.json", "w") as f:
    json.dump(snapshot, f, indent=2)
