"""Shared quiz logic used by BOTH the Streamlit app and the Gradio app.

This file has no user-interface code. Keeping the rules here means the two web
apps always score a quiz in exactly the same way (and the same way as the
Tkinter version, because we re-use quiz_data.py and quiz_questions.py).
"""
import time
from datetime import date

from quiz_data import (POINTS_PER_CORRECT, STREAK_BONUS, STREAK_LABEL,
                       final_score, penalty_for, save_result)
from quiz_questions import TOPICS, prepare

TOPIC_BY_NAME = {t["name"]: t for t in TOPICS}
QUESTIONS_PER_QUIZ = 10


def new_quiz(topic_name):
    """Start a fresh quiz: shuffled questions plus all counters set to zero."""
    topic = TOPIC_BY_NAME[topic_name]
    return {"topic": topic["name"], "questions": prepare(topic["id"]), "index": 0,
            "points": 0, "bonus": 0, "streak": 0, "best": 0, "correct": 0,
            "started": time.time(), "answers": []}


def check_answer(state, choice_letter):
    """Mark one answer. Returns (is_correct, message) and updates the state."""
    q = state["questions"][state["index"]]
    ok = choice_letter == q["answer"]
    message = ""
    if ok:
        state["streak"] += 1
        state["best"] = max(state["best"], state["streak"])
        state["points"] += POINTS_PER_CORRECT
        state["correct"] += 1
        extra = STREAK_BONUS.get(state["streak"], 0)
        state["bonus"] += extra
        if state["streak"] in STREAK_LABEL:
            message = f"{STREAK_LABEL[state['streak']]}" + (f" +{extra} streak bonus" if extra else "")
    else:
        state["streak"] = 0
    state["answers"].append({"q": q["text"], "chosen": choice_letter,
                             "right": q["answer"], "ok": ok})
    return ok, message


def is_finished(state):
    return state["index"] >= len(state["questions"])


def finish_quiz(state, student):
    """Build the result record, save it to quiz_results.json and return it."""
    correct = state["correct"]
    entry = {
        "id": str(time.time()), "name": student.strip() or "Student",
        "topic": state["topic"], "correct": correct, "total": len(state["questions"]),
        "points": state["points"], "streakBonus": state["bonus"],
        "penalty": penalty_for(correct),
        "finalScore": final_score(state["points"], state["bonus"], correct),
        "bestStreak": state["best"], "endStreak": state["streak"],
        "timeSecs": int(time.time() - state["started"]), "date": date.today().isoformat(),
    }
    save_result(entry)
    return entry


def option_text(q):
    """The four answer choices as 'A. text' strings for radio buttons."""
    return [f"{letter}. {text}" for letter, text in q["options"]]


def letter_of(option):
    return option.split(".", 1)[0].strip()


def correct_text(q):
    return f"{q['answer']}. {dict(q['options'])[q['answer']]}"
