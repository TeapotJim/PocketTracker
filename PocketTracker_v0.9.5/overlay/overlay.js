
async function fetchStats() {
  try {
    const res = await fetch("../data/stats.json");
    const stats = await res.json();

    document.getElementById("current-rank").textContent = stats.current_rank;
    document.getElementById("rank-streak").textContent = `${stats.streak_type.charAt(0).toUpperCase() + stats.streak_type.slice(1)} Streak: ${stats.current_streak}`;

    document.getElementById("points").textContent = stats.current_points;
    document.getElementById("next-rank").textContent = `Next Rank: ${stats.next_rank}`;
    document.getElementById("points-to-next").textContent = `Points to Next: ${stats.points_to_next}`;
    document.getElementById("est-games-next").textContent = `Est. Games Needed: ${stats.est_games_next}`;

    document.getElementById("wins").textContent = `Wins Today: ${stats.wins_today}`;
    document.getElementById("losses").textContent = `Losses Today: ${stats.losses_today}`;
    document.getElementById("win-percent").textContent = `Win % Today: ${stats.win_percent_today.toFixed(1)}%`;
    document.getElementById("streak").textContent = `${stats.streak_type.charAt(0).toUpperCase() + stats.streak_type.slice(1)} Streak: ${stats.current_streak}`;

    document.getElementById("top-player").textContent = `Top Score: ${stats.top_score}`;
    document.getElementById("points-behind").textContent = `Points Behind: ${stats.points_behind}`;
    document.getElementById("est-games-to-top").textContent = `Est. Games to #1: ${stats.est_games_to_top}`;
  } catch (err) {
    console.error("Failed to fetch stats:", err);
  }
}

// Auto-refresh every 3 seconds
setInterval(fetchStats, 3000);
fetchStats();
