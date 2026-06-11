from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)

# --- MASTER PRODUCTION ENGINE DATABASE ---
def init_db():
    conn = sqlite3.connect("village_mainframe_v17.db")
    db = conn.cursor()
    db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY, coins INTEGER, pph INTEGER, level INTEGER, 
            streak_count INTEGER, energy INTEGER, tractor_tier TEXT
        )
    """)
    db.execute("SELECT id FROM users WHERE id = 'Murthy_Grand_Tycoon'")
    if not db.fetchone():
        db.execute("INSERT INTO users VALUES ('Murthy_Grand_Tycoon', 1655165, 900, 3, 1, 500, 'Cyber Tractor')")
    conn.commit()
    conn.close()

init_db()

@app.route("/")
def home():
    conn = sqlite3.connect("village_mainframe_v17.db")
    db = conn.cursor()
    row = db.execute("SELECT coins, pph, level, energy, tractor_tier FROM users WHERE id = 'Murthy_Grand_Tycoon'").fetchone()
    conn.close()
    
    coins, pph, level, energy, tractor_tier = row
    
    # Force Energy Auto-Charge Safeguard Rule
    if energy is None or energy <= 10:
        energy = 500
        conn = sqlite3.connect("village_mainframe_v17.db")
        conn.execute("UPDATE users SET energy = 500 WHERE id = 'Murthy_Grand_Tycoon'")
        conn.commit()
        conn.close()

    # Economy Tiers Logic Grid
    level_targets = [0, 100000, 1000000, 5000000, 20000000, 100000000, 250000000, 500000000, 1000000000, 2500000000, 5000000000]
    if coins < 100000: level = 1
    elif coins < 1000000: level = 2
    elif coins < 5000000: level = 3
    elif coins < 20000000: level = 4          
    elif coins < 100000000: level = 5         
    elif coins < 250000000: level = 6         
    elif coins < 500000000: level = 7         
    elif coins < 1000000000: level = 8        
    elif coins < 2500000000: level = 9        
    else: level = 10                          

    next_target = level_targets[level]
    needed = max(0, next_target - coins)
    prev_target = level_targets[level - 1]
    progress = min(int(((coins - prev_target) / max(1, next_target - prev_target)) * 100), 100)
    
    multiplier = 4 if tractor_tier == "Cyber Tractor" else (2 if tractor_tier == "Iron Tractor" else 1)
    days_left = max(0, (datetime(2026, 11, 10) - datetime.now()).days)

    data = {
        "coins": coins, "pph": pph, "level": level, "energy": energy, 
        "multiplier": multiplier, "needed": needed, "progress": progress, "days_left": days_left
    }
    return render_template("index.html", data=data)

@app.route("/tap", methods=["POST"])
def tap():
    conn = sqlite3.connect("village_mainframe_v17.db")
    db = conn.cursor()
    row = db.execute("SELECT coins, level, energy, tractor_tier FROM users WHERE id = 'Murthy_Grand_Tycoon'").fetchone()
    coins, level, energy, tractor_tier = row
    
    multiplier = 4 if tractor_tier == "Cyber Tractor" else (2 if tractor_tier == "Iron Tractor" else 1)
    
    if energy >= 10:
        energy -= 10
        coins += (40 * level * multiplier)
        db.execute("UPDATE users SET coins = ?, energy = ? WHERE id = 'Murthy_Grand_Tycoon'", (coins, energy))
        conn.commit()
    conn.close()
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)
