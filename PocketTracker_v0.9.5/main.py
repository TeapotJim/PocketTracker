# Line 1
from rank_utils import points_to_next_rank, estimate_wins_to_top  # We no longer use estimate_wins_needed here
# Line 2
import tkinter as tk
# Line 3
from tkinter import messagebox
# Line 4
import json
# Line 5
import os
# Line 6
import math
# Line 7
from datetime import datetime

# --- Define base directory so relative paths work correctly ---
# Line 10
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Line 11
STATS_FILE = os.path.join(BASE_DIR, "data", "stats.json")
# Line 12
SNAPSHOT_FILE = os.path.join(BASE_DIR, "data", "trend_snapshot.json")
# Line 13
DAILY_LOG_FILE = os.path.join(BASE_DIR, "data", "daily_log.csv")

# --- Updated load_stats() to ensure new keys exist ---
# Line 16
def load_stats():
    with open(STATS_FILE, "r") as f:
        stats = json.load(f)
    # If new keys are missing, recalc stats and save them
    if "est_games_next" not in stats or "est_games_to_top" not in stats:
        recalc_stats(stats)
        save_stats(stats)
    return stats

# Line 24
def load_snapshot():
    with open(SNAPSHOT_FILE, "r") as f:
        return json.load(f)

# Line 28
def save_stats(data):
    with open(STATS_FILE, "w") as f:
        json.dump(data, f, indent=4)

# --- Main Calculation Function ---
def recalc_stats(stats):
    # Calculate today's win percentage
    games = stats["wins_today"] + stats["losses_today"]
    stats["win_percent_today"] = (stats["wins_today"] / games) * 100 if games > 0 else 0.0

    # Calculate season win percentage (used for estimation, though we'll use today's rate here)
    total_season = stats["season_wins"] + stats["season_losses"]
    stats["win_percent_season"] = (stats["season_wins"] / total_season * 100) if total_season > 0 else 0.0

    # Determine current streak information
    if stats["wins_today"] > 0 and stats["losses_today"] == 0:
        stats["streak_type"] = "win"
        stats["current_streak"] = stats["wins_today"]
    elif stats["losses_today"] > 0 and stats["wins_today"] == 0:
        stats["streak_type"] = "loss"
        stats["current_streak"] = stats["losses_today"]
    else:
        stats["streak_type"] = "win" if stats["wins_today"] >= stats["losses_today"] else "loss"
        stats["current_streak"] = abs(stats["wins_today"] - stats["losses_today"])
    
    # Recalculate Points to Next dynamically using the helper function
    stats["points_to_next"] = points_to_next_rank(stats["current_points"])

    # --- New: Estimate Games Needed for Next Rank ---
    # Determine loss value based on the current rank.
    current_rank = stats["current_rank"]
    if "Ultra Ball" in current_rank:
        loss_value = 7
    elif "Great Ball" in current_rank or "Poke Ball" in current_rank:
        loss_value = 5
    elif "Master Ball" in current_rank:
        loss_value = 10
    else:
        loss_value = 0

    # Today's win rate as a fraction
    p = stats["win_percent_today"] / 100.0
    # Effective points per game: wins give +10; losses subtract loss_value.
    effective_points = (p * 10) + ((1 - p) * (-loss_value))
    if effective_points <= 0:
        stats["est_games_next"] = "N/A"
    else:
        stats["est_games_next"] = math.ceil(stats["points_to_next"] / effective_points)

    # --- New: Estimate Games Needed to Reach Top Score ---
    if "top_score" in stats:
        stats["points_behind"] = stats["top_score"] - stats["current_points"] if stats["current_points"] < stats["top_score"] else 0
        if effective_points <= 0:
            stats["est_games_to_top"] = "N/A"
        else:
            stats["est_games_to_top"] = math.ceil(stats["points_behind"] / effective_points)
    else:
        stats["points_behind"] = "N/A"
        stats["est_games_to_top"] = "N/A"

# --- Function to Update the UI ---
def update_ui():
    stats = load_stats()
    snapshot = load_snapshot()

    lbl_points.config(text=f"Points: {stats['current_points']}")
    lbl_rank.config(text=f"Rank: {stats['current_rank']}")
    lbl_next.config(text=f"Next: {stats['next_rank']} ({stats['points_to_next']} pts, ~{stats['est_games_next']} games)")
    
    lbl_wins.config(text=f"Wins Today: {stats['wins_today']}")
    lbl_losses.config(text=f"Losses Today: {stats['losses_today']}")
    lbl_win_percent.config(text=f"Win % Today: {stats['win_percent_today']:.1f}%")
    lbl_streak.config(text=f"Win Streak: {stats['current_streak']}")

    # Snapshot Summary
    y = snapshot["yesterday"]
    s = snapshot["7_day"]
    summary = (
        f"Yesterday: {y['ppg']} pts/game | {y['win_percent']}% WR\n"
        f"7-Day Avg: {s['avg_games']} games/day | {s['avg_win_percent']}% WR"
    )
    lbl_snapshot.config(text=summary)

# --- Button Action Functions ---
def add_win():
    stats = load_stats()
    stats["current_points"] += 10
    stats["wins_today"] += 1
    stats["season_wins"] += 1
    recalc_stats(stats)
    save_stats(stats)
    update_ui()

def add_loss():
    stats = load_stats()
    stats["current_points"] -= 7
    stats["losses_today"] += 1
    stats["season_losses"] += 1
    recalc_stats(stats)
    save_stats(stats)
    update_ui()

def reset_day():
    stats = load_stats()
    stats["wins_today"] = 0
    stats["losses_today"] = 0
    recalc_stats(stats)
    save_stats(stats)
    update_ui()

def log_session():
    os.system("python update_snapshot.py")

def open_dashboard():
    os.system("start http://localhost:8080/overlay/dashboard.html")

# --- New: Top Score Override Section ---
def submit_top_score_override():
    try:
        new_top_score = int(top_score_entry.get())
    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter a valid number for World #1 Pts.")
        return
    stats = load_stats()
    stats["top_score"] = new_top_score  # Update only the top score
    recalc_stats(stats)
    save_stats(stats)
    update_ui()
    messagebox.showinfo("World #1 Pts Updated", "World #1 Point Total has been updated.")

# --- Manual Overrides Section (for current points and season record) ---
def submit_manual_override():
    try:
        new_points = int(override_points_entry.get())
        new_season_wins = int(override_season_wins_entry.get())
        new_season_losses = int(override_season_losses_entry.get())
    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter valid numbers for current points and season record.")
        return

    stats = load_stats()
    stats["current_points"] = new_points
    stats["season_wins"] = new_season_wins
    stats["season_losses"] = new_season_losses
    recalc_stats(stats)
    save_stats(stats)
    update_ui()
    messagebox.showinfo("Overrides Updated", "Manual overrides have been applied.")

# --- Offline Session Logging Section ---
def submit_offline_session():
    try:
        offline_points = int(offline_points_entry.get())
        offline_season_wins = int(offline_wins_entry.get())
        offline_season_losses = int(offline_losses_entry.get())
    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter valid numbers for all offline session fields.")
        return

    stats = load_stats()
    delta_points = offline_points - stats["current_points"]
    delta_wins = offline_season_wins - stats["season_wins"]
    delta_losses = offline_season_losses - stats["season_losses"]

    stats["current_points"] = offline_points
    stats["season_wins"] = offline_season_wins
    stats["season_losses"] = offline_season_losses
    recalc_stats(stats)
    save_stats(stats)
    update_ui()

    total = stats["season_wins"] + stats["season_losses"]
    new_season_win_percent = (stats["season_wins"] / total * 100) if total > 0 else 0

    current_date = datetime.now().strftime("%Y-%m-%d")
    log_line = f"{current_date},{delta_wins},{delta_losses},{delta_points},{stats['season_wins']},{new_season_win_percent}\n"
    try:
        with open(DAILY_LOG_FILE, "a") as f:
            f.write(log_line)
    except Exception as e:
        messagebox.showerror("Log Error", f"Failed to write to daily log: {e}")
        return

    messagebox.showinfo("Offline Session Logged", "Offline session data has been logged successfully.")
    offline_points_entry.delete(0, tk.END)
    offline_wins_entry.delete(0, tk.END)
    offline_losses_entry.delete(0, tk.END)

# --- Tkinter UI Setup ---
root = tk.Tk()
root.title("Pocket Tracker Control Panel")

# Existing Control Buttons
btn_win = tk.Button(root, text="+ Win", command=add_win)
btn_loss = tk.Button(root, text="- Loss", command=add_loss)
btn_reset = tk.Button(root, text="Reset Day", command=reset_day)
btn_log = tk.Button(root, text="Log Session", command=log_session)
btn_dash = tk.Button(root, text="Open Dashboard", command=open_dashboard)

btn_win.pack()
btn_loss.pack()
btn_reset.pack()
btn_log.pack()
btn_dash.pack()

lbl_points = tk.Label(root, text="Points:")
lbl_points.pack()

lbl_rank = tk.Label(root, text="Rank:")
lbl_rank.pack()

lbl_next = tk.Label(root, text="Next:")
lbl_next.pack()

lbl_wins = tk.Label(root, text="Wins Today:")
lbl_wins.pack()

lbl_losses = tk.Label(root, text="Losses Today:")
lbl_losses.pack()

lbl_win_percent = tk.Label(root, text="Win % Today:")
lbl_win_percent.pack()

lbl_streak = tk.Label(root, text="Win Streak:")
lbl_streak.pack()

lbl_snapshot = tk.Label(root, text="Snapshot Summary", justify="left", fg="blue")
lbl_snapshot.pack(pady=10)

# --- New: World #1 Point Total Section ---
world_frame = tk.LabelFrame(root, text="World #1 Point Total", padx=10, pady=10)
world_frame.pack(padx=10, pady=10, fill="x")

tk.Label(world_frame, text="Set World #1 Pts:").grid(row=0, column=0, sticky="e")
top_score_entry = tk.Entry(world_frame)
top_score_entry.grid(row=0, column=1)
btn_top_score = tk.Button(world_frame, text="Update World #1 Pts", command=submit_top_score_override)
btn_top_score.grid(row=1, column=0, columnspan=2, pady=5)

# --- Manual Overrides Section for Current Record ---
manual_frame = tk.LabelFrame(root, text="Manual Overrides", padx=10, pady=10)
manual_frame.pack(padx=10, pady=10, fill="x")

tk.Label(manual_frame, text="Override Current Points:").grid(row=0, column=0, sticky="e")
override_points_entry = tk.Entry(manual_frame)
override_points_entry.grid(row=0, column=1)

tk.Label(manual_frame, text="Override Season Wins:").grid(row=1, column=0, sticky="e")
override_season_wins_entry = tk.Entry(manual_frame)
override_season_wins_entry.grid(row=1, column=1)

tk.Label(manual_frame, text="Override Season Losses:").grid(row=2, column=0, sticky="e")
override_season_losses_entry = tk.Entry(manual_frame)
override_season_losses_entry.grid(row=2, column=1)

btn_override = tk.Button(manual_frame, text="Submit Overrides", command=submit_manual_override)
btn_override.grid(row=3, column=0, columnspan=2, pady=5)

# --- Offline Session Logging Section UI ---
offline_frame = tk.LabelFrame(root, text="Offline Session Logging", padx=10, pady=10)
offline_frame.pack(padx=10, pady=10, fill="x")

tk.Label(offline_frame, text="Offline Current Points:").grid(row=0, column=0, sticky="e")
offline_points_entry = tk.Entry(offline_frame)
offline_points_entry.grid(row=0, column=1)

tk.Label(offline_frame, text="Offline Season Wins:").grid(row=1, column=0, sticky="e")
offline_wins_entry = tk.Entry(offline_frame)
offline_wins_entry.grid(row=1, column=1)

tk.Label(offline_frame, text="Offline Season Losses:").grid(row=2, column=0, sticky="e")
offline_losses_entry = tk.Entry(offline_frame)
offline_losses_entry.grid(row=2, column=1)

btn_offline = tk.Button(offline_frame, text="Log Offline Session", command=submit_offline_session)
btn_offline.grid(row=3, column=0, columnspan=2, pady=5)

update_ui()
root.mainloop()
