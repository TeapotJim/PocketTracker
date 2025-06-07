import json
import os
import math

CONFIG_FILE = os.path.join("config.json")

def load_config():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def get_rank_info(points):
    config = load_config()
    for group in config["ranks"].values():
        for rank in group:
            if points < rank["min_points"]:
                return previous_rank
            previous_rank = rank
    return previous_rank

def calculate_points(stats, is_win):
    current = get_rank_info(stats["current_points"])
    points = stats["current_points"]
    streak = stats["current_streak"]

    if is_win:
        base = current["win"]
        bonus = current["streak_bonus"].get(str(streak), current["streak_bonus"].get("5", 0))
        return base + bonus
    else:
        return current["loss"]

def estimate_wins_needed(stats, target_points):
    # This function is no longer used for game estimation.
    if stats["win_percent_season"] == 0:
        return None
    avg_points_per_win = 10 * stats["win_percent_season"]
    points_needed = target_points - stats["current_points"]
    return math.ceil(points_needed / avg_points_per_win) if points_needed > 0 else 0

def estimate_wins_to_top(stats):
    return estimate_wins_needed(stats, stats["top_score"])

def points_to_next_rank(current_points):
    config = load_config()
    ranks = []
    for group in config["ranks"].values():
        ranks.extend(group)
    ranks.sort(key=lambda r: r["min_points"])
    for rank in ranks:
        if current_points < rank["min_points"]:
            return rank["min_points"] - current_points
    return 0
