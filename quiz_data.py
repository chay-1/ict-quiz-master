import json
import os
import threading

try:
    import winsound
except ImportError:
    winsound = None

from quiz_theme import SOUNDS


def _play_feedback_sound(kind, root):
    if winsound:
        try:
            for freq, ms in SOUNDS[kind]:
                winsound.Beep(freq, ms)
            return
        except (RuntimeError, OSError):
            winsound.MessageBeep(winsound.MB_OK if kind != "bad" else winsound.MB_ICONEXCLAMATION)
            return
    if root is not None:
        root.bell()


# Play tones off the Tk event loop so feedback never pauses quiz controls.
def beep(kind, root=None):
    if kind not in SOUNDS:
        raise ValueError(f"Unknown sound effect: {kind}")
    if root is not None and not getattr(root, "sound_enabled", True):
        return
    threading.Thread(target=_play_feedback_sound, args=(kind, root), daemon=True).start()

# ───────────────────────── Scoring rules ─────────────────────────
# We set the points, pass mark, streak bonuses, and score penalty here.
POINTS_PER_CORRECT = 10
PASS_MARK = 6
STREAK_BONUS = {3: 5, 5: 10, 7: 15, 10: 25}
STREAK_LABEL = {2: "Nice Start!", 3: "You're on Fire!", 5: "Hot Streak!",
                7: "Unstoppable!", 10: "ICT Master!"}


# We give a penalty when the student gets fewer than six answers correct.
def penalty_for(correct):
    return 0 if correct >= PASS_MARK else (PASS_MARK - correct) * 10


# We calculate the final score and make sure it cannot go below zero.
def final_score(points, bonus, correct):
    return max(0, points + bonus - penalty_for(correct))


# We show the time in minutes and seconds.
def fmt_time(secs):
    return f"{secs // 60:02d}:{secs % 60:02d}"

# ───────────────────────── Local storage (JSON) ─────────────────────────
# We save results beside this program so we can use the quiz offline.
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "quiz_results.json")


# We load saved results. If there are none yet, we start with an empty list.
def load_results():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return []


# We add the new result and save all results in a JSON file.
def save_result(entry):
    data = load_results()
    data.append(entry)
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except OSError:
        return False      # the quiz still shows the result even if the file cannot be saved
    return True


SORTS = {"score": lambda e: (e["finalScore"], e["bestStreak"]),
         "streak": lambda e: (e["bestStreak"], e["finalScore"]),
         "speed": lambda e: (e.get("correct", 0), -e.get("timeSecs", 9999))}


# We make the leaderboard using each student's best result.
def ranking(topic=None, sort="score"):
    """Best attempt per student (optionally for one topic), best first."""
    key, best = SORTS[sort], {}
    for e in load_results():
        if topic and e["topic"] != topic:
            continue
        k = e["name"].strip().lower()
        if k not in best or key(e) > key(best[k]):
            best[k] = e
    return sorted(best.values(), key=key, reverse=True)
