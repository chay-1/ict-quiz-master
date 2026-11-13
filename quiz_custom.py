import json
import os


QUESTIONS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "teacher_questions.json")


def load_custom_questions():
    try:
        with open(QUESTIONS_FILE, "r", encoding="utf-8") as f:
            questions = json.load(f)
    except (OSError, ValueError):
        return []
    if not isinstance(questions, list):
        return []
    # keep only complete questions so a damaged file cannot crash Teacher Mode
    return [q for q in questions
            if isinstance(q, dict) and q.get("q") and q.get("a") and q.get("level") in ("Easy", "Medium", "Hard")]


def save_custom_questions(questions):
    try:
        with open(QUESTIONS_FILE, "w", encoding="utf-8") as f:
            json.dump(questions, f, ensure_ascii=False, indent=2)
    except OSError:
        return False
    return True
