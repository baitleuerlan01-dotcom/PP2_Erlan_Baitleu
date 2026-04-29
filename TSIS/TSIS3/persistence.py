import json
import os

def load_settings():
    if not os.path.exists("settings.json"):
        return {"sound": True, "color": [0,255,0], "difficulty": 1}
    with open("settings.json", "r") as f:
        return json.load(f)

def save_settings(settings):
    with open("settings.json", "w") as f:
        json.dump(settings, f, indent=4)

def load_scores():
    if not os.path.exists("leaderboard.json"):
        return []
    with open("leaderboard.json", "r") as f:
        return json.load(f)

def save_score(name, score, distance):
    data = load_scores()
    data.append({"name": name, "score": score, "distance": distance})
    data = sorted(data, key=lambda x: x["score"], reverse=True)[:10]
    with open("leaderboard.json", "w") as f:
        json.dump(data, f, indent=4)