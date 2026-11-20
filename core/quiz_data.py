import json
import os
import threading

try:
    import winsound
except ImportError:
    winsound = None

from core.quiz_theme import SOUNDS


_SOUND_FILES = {}      # kind -> path of the WAV file (made once, then reused)


def _make_wav(kind):
    """Build a small WAV file for one sound: sine tones with a soft start and end (no clicks)."""
    import math
    import struct
    import tempfile
    import wave
    rate, volume = 22050, 0.45
    frames = bytearray()
    for freq, ms in SOUNDS[kind]:
        n = int(rate * ms / 1000)
        fade = max(1, int(rate * 0.006))
        for i in range(n):
            env = min(1.0, i / fade, (n - i) / fade)
            frames += struct.pack("<h", int(32767 * volume * env * math.sin(2 * math.pi * freq * i / rate)))
    path = os.path.join(tempfile.gettempdir(), f"ict_quiz_{kind}.wav")
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(bytes(frames))
    return path


def _play_feedback_sound(kind):
    """Old method (system speaker). We only use it if the WAV method fails."""
    try:
        for freq, ms in SOUNDS[kind]:
            winsound.Beep(freq, ms)
    except (RuntimeError, OSError):
        winsound.MessageBeep(winsound.MB_OK if kind != "bad" else winsound.MB_ICONEXCLAMATION)


# On Windows we play a WAV file with the sound card (SND_ASYNC = it plays in the background,
# so the quiz never freezes and two sounds never fight each other). If that fails, we use Beep.
# On other systems we use Tk's own bell.
def beep(kind, root=None):
    if kind not in SOUNDS:
        raise ValueError(f"Unknown sound effect: {kind}")
    if root is not None and not getattr(root, "sound_enabled", True):
        return
    if winsound:
        try:
            if kind not in _SOUND_FILES:
                _SOUND_FILES[kind] = _make_wav(kind)
            winsound.PlaySound(_SOUND_FILES[kind], winsound.SND_FILENAME | winsound.SND_ASYNC)
            return
        except Exception:
            threading.Thread(target=_play_feedback_sound, args=(kind,), daemon=True).start()
    elif root is not None and kind not in ("click", "tick"):
        try:
            root.bell()
        except Exception:
            pass


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
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # the ICT_Quiz_Master folder
DATA_DIR = os.path.join(ROOT, "data")                                 # saved results live here
DATA_FILE = os.path.join(DATA_DIR, "quiz_results.json")


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
        os.makedirs(DATA_DIR, exist_ok=True)
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
