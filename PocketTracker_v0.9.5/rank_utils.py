import json
import os
import math

# Use a path relative to this file so the module works regardless of the
# current working directory.
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

def load_config():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def get_rank_info(points):
    """Return the rank configuration for the provided point total."""
    config = load_config()
    # Flatten and sort all ranks by their minimum point thresholds so the logic
    # works regardless of how ranks are grouped in the config file.
    ranks = []
    for group in config["ranks"].values():
        ranks.extend(group)
    ranks.sort(key=lambda r: r["min_points"])

    # Initialise with the lowest rank so we have a sensible default.
    previous_rank = ranks[0]
    for rank in ranks:
        if points < rank["min_points"]:
            return previous_rank
        previous_rank = rank

    # If points exceed the highest threshold, return the last rank.
    return ranks[-1]

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
