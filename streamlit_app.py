"""ICT Quiz Master - Streamlit version.   Run:  streamlit run streamlit_app.py"""
import pandas as pd
import streamlit as st

import quiz_core as core
from quiz_custom import load_custom_questions, save_custom_questions
from quiz_data import PASS_MARK, ranking

st.set_page_config(page_title="ICT Quiz Master", page_icon="🎓", layout="centered")

# Streamlit re-runs this file after every click, so everything that must be
# remembered lives in st.session_state.
S = st.session_state
S.setdefault("quiz", None)        # the running quiz (None = not started)
S.setdefault("checked", False)    # has the current answer been checked?
S.setdefault("result", None)      # final result record


def start(topic_name, student):
    S.quiz, S.checked, S.result, S.student = core.new_quiz(topic_name), False, None, student


# ───────────────────────── Quiz page ─────────────────────────
def quiz_page():
    st.title("🎓 ICT Quiz Master")
    if S.quiz is None:
        st.write("Pick a topic and answer 10 questions. Streaks give bonus points!")
        name = st.text_input("Your name", max_chars=20)
        topic = st.selectbox("Topic", list(core.TOPIC_BY_NAME),
                             format_func=lambda n: f"{core.TOPIC_BY_NAME[n]['icon']} {n} "
                                                   f"({core.TOPIC_BY_NAME[n]['level']})")
        st.caption(core.TOPIC_BY_NAME[topic]["desc"])
        if st.button("Start quiz", type="primary"):
            if len(name.strip()) < 2:
                st.warning("Please enter a name with at least 2 characters.")
            else:
                start(topic, name.strip())
                st.rerun()
        return

    quiz = S.quiz
    if core.is_finished(quiz):
        if S.result is None:
            S.result = core.finish_quiz(quiz, S.student)
        r = S.result
        st.success(f"Well done, {r['name']}!  Final score: **{r['finalScore']}**")
        c1, c2, c3 = st.columns(3)
        c1.metric("Correct", f"{r['correct']}/{r['total']}")
        c2.metric("Streak bonus", f"+{r['streakBonus']}")
        c3.metric("Penalty", f"-{r['penalty']}")
        st.write("✅ Passed" if r["correct"] >= PASS_MARK else f"❌ Pass mark is {PASS_MARK}. Try again!")
        with st.expander("Review your answers"):
            for i, a in enumerate(quiz["answers"], 1):
                st.write(f"{'✅' if a['ok'] else '❌'} **Q{i}.** {a['q']}")
        if st.button("Try another quiz"):
            S.quiz = None
            st.rerun()
        return

    i, q = quiz["index"], quiz["questions"][quiz["index"]]
    st.progress(i / len(quiz["questions"]), text=f"Question {i + 1} of {len(quiz['questions'])}")
    c1, c2, c3 = st.columns(3)
    c1.metric("Score", quiz["points"] + quiz["bonus"])
    c2.metric("Streak 🔥", quiz["streak"])
    c3.metric("Topic", quiz["topic"])
    st.subheader(q["text"])
    choice = st.radio("Choose one answer", core.option_text(q), index=None,
                      key=f"q{i}", disabled=S.checked)
    if not S.checked:
        if st.button("Check answer", disabled=choice is None):
            ok, msg = core.check_answer(quiz, core.letter_of(choice))
            S.checked, S.last_ok, S.last_msg = True, ok, msg
            st.rerun()
    else:
        (st.success if S.last_ok else st.error)(
            "Correct! 🎉" if S.last_ok else f"Not quite. Correct answer: {core.correct_text(q)}")
        if S.last_msg:
            st.balloons()
            st.info(S.last_msg)
        st.caption(f"💡 {q['why']}")
        if st.button("Next ➜" if i + 1 < len(quiz["questions"]) else "Finish quiz"):
            quiz["index"] += 1
            S.checked = False
            st.rerun()


# ───────────────────────── Leaderboard page ─────────────────────────
def leaderboard_page():
    st.title("🏆 Leaderboard")
    topic = st.selectbox("Topic", ["All topics"] + list(core.TOPIC_BY_NAME))
    sort = st.radio("Sort by", ["score", "streak", "speed"], horizontal=True)
    rows = ranking(None if topic == "All topics" else topic, sort)
    if not rows:
        st.info("No results yet. Finish a quiz first!")
        return
    df = pd.DataFrame([{"Rank": n, "Name": e["name"], "Topic": e["topic"], "Score": e["finalScore"],
                        "Correct": f"{e['correct']}/{e['total']}", "Best streak": e["bestStreak"],
                        "Time (s)": e["timeSecs"]} for n, e in enumerate(rows, 1)])
    st.dataframe(df, hide_index=True, use_container_width=True)
    st.bar_chart(df.set_index("Name")["Score"])


# ───────────────────────── Teacher page ─────────────────────────
def teacher_page():
    st.title("👩‍🏫 Teacher mode")
    questions = load_custom_questions()
    with st.form("add_q", clear_on_submit=True):
        q = st.text_input("Question")
        a = st.text_input("Model answer")
        level = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"])
        if st.form_submit_button("Add question"):
            if q.strip() and a.strip():
                questions.append({"q": q.strip(), "a": a.strip(), "level": level})
                save_custom_questions(questions)
                st.success(f"Question added ({len(questions)} total).")
            else:
                st.error("Please type both a question and a model answer.")
    st.subheader(f"Saved questions ({len(questions)})")
    for n, item in enumerate(questions):
        col1, col2 = st.columns([6, 1])
        col1.write(f"**[{item['level']}]** {item['q']}  \n_Answer: {item['a']}_")
        if col2.button("🗑️", key=f"del{n}"):
            questions.pop(n)
            save_custom_questions(questions)
            st.rerun()


page = st.sidebar.radio("Go to", ["Take a quiz", "Leaderboard", "Teacher mode"])
{"Take a quiz": quiz_page, "Leaderboard": leaderboard_page, "Teacher mode": teacher_page}[page]()
