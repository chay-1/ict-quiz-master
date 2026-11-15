"""ICT Quiz Master — enhanced Streamlit game.
Run: streamlit run streamlit_app.py
"""
from pathlib import Path
import time
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from core import quiz_core as core
from core.quiz_custom import load_custom_questions, save_custom_questions
from core.quiz_data import PASS_MARK, ranking
from web.web_game_assets import VISUAL_HEIGHT, question_visual, sound_html, certificate_pdf

st.set_page_config(page_title="ICT Quiz Master", page_icon="🎓", layout="wide")

st.markdown("""
<style>
div.block-container, [data-testid="stMainBlockContainer"] {max-width: 1250px; padding-top: 4rem; padding-bottom: 1rem;}
.game-title {font-size:2.25rem;font-weight:800;color:#172554;letter-spacing:-1px;}
.game-sub {color:#64748b;margin-top:-12px;margin-bottom:22px;}
.mini-title {font-size:1.35rem;font-weight:800;color:#172554;letter-spacing:-.5px;line-height:1.15;}
.mini-title small {display:block;font-size:.8rem;font-weight:600;color:#64748b;letter-spacing:0;}
div[data-testid="stMetric"] {background:#f8fafc;padding:12px 16px;border-radius:14px;border:1px solid #e2e8f0;}
/* one row of equal-height chips: timer, score, streak, best streak */
.timer-chip, .stat-chip {display:flex;align-items:center;justify-content:space-between;gap:10px;height:52px;
  box-sizing:border-box;border-radius:14px;padding:0 12px;margin:0;font-weight:700;white-space:nowrap;}
.timer-chip {background:#fff7ed;border:1px solid #fed7aa;color:#9a3412;justify-content:flex-start;}
.timer-chip .watch {font-size:1.2rem;line-height:1;}
.timer-chip .lbl {font-size:.82rem;font-weight:600;}
.timer-chip .time {font-size:1.3rem;font-variant-numeric:tabular-nums;letter-spacing:.04em;}
.stat-chip {background:#f8fafc;border:1px solid #e2e8f0;color:#172554;}
.stat-chip .lbl {font-size:.82rem;font-weight:600;color:#475569;}
.stat-chip .val {font-size:1.35rem;}
div.stButton > button[kind="primary"] {border-radius:12px;font-weight:700;min-height:2.8rem;}
.topic-pill {background:#eaf2ff;color:#174ea6;padding:8px 16px;border-radius:12px;font-size:1rem;margin-bottom:8px;}
.q-text {font-size:1.55rem;font-weight:750;line-height:1.3;color:#172554;margin:0 0 10px;}
/* answer options: every option is a box of the same size with the same gap */
div[role="radiogroup"] {gap:8px !important;}
div[role="radiogroup"] label, [data-testid="stRadio"] label[data-baseweb="radio"] {
  width:100% !important;box-sizing:border-box !important;min-height:50px !important;padding:8px 14px !important;
  margin:0 !important;border:1px solid #cbd5e1 !important;border-radius:12px !important;background:#fff !important;
  align-items:center !important;}
div[role="radiogroup"] label p {font-size:1.1rem !important;}
/* the hidden sound player must not take any space on the page */
div:has(> iframe[height="1"]), [data-testid="stElementContainer"]:has(iframe[height="1"]) {
  position:absolute !important;width:1px !important;height:1px !important;opacity:0 !important;
  overflow:hidden !important;pointer-events:none !important;}
div[data-testid="stProgress"] {margin-bottom:-6px;}
</style>
""", unsafe_allow_html=True)

S = st.session_state
for key, value in {
    "quiz": None, "checked": False, "result": None,
    "pending_sound": None, "sound_enabled": True, "student": ""
}.items():
    if key not in S:
        S[key] = value


@st.fragment(run_every="1s")
def live_timer(started_at):
    """Refresh only the timer once per second while a quiz is active."""
    elapsed = max(0, int(time.time() - started_at))
    minutes, seconds = divmod(elapsed, 60)
    st.markdown(
        f'<div class="timer-chip"><span class="watch">⏱️</span>'
        f'<span class="lbl">Time</span><span class="time">{minutes:02d}:{seconds:02d}</span></div>',
        unsafe_allow_html=True
    )


def play_pending_sound():
    sound = S.pending_sound
    if sound:
        S.pending_sound = None
        if S.sound_enabled:
            components.html(sound_html(sound), height=1, scrolling=False)


def start(topic_name, student):
    S.quiz = core.new_quiz(topic_name)
    S.checked = False
    S.result = None
    S.student = student
    S.pending_sound = None
    S.last_ok = False
    S.last_msg = ""


def stat_chip(label, value):
    return f'<div class="stat-chip"><span class="lbl">{label}</span><span class="val">{value}</span></div>'


def quiz_page():
    if S.quiz is None:
        _, middle, _ = st.columns([1, 2, 1])
        with middle:
            st.markdown('<div class="game-title">🎓 ICT Quiz Master</div>', unsafe_allow_html=True)
            st.markdown('<div class="game-sub">Learn ICT concepts through a fun interactive challenge.</div>', unsafe_allow_html=True)
            st.markdown("### Ready to play?")
            st.write("Choose a topic, enter your name and answer 10 questions to earn points and streak rewards.")
            with st.container(border=True):
                name = st.text_input("Your name", max_chars=30, key="student_name")
                topic = st.selectbox(
                    "Choose your ICT topic", list(core.TOPIC_BY_NAME),
                    format_func=lambda n: f"{core.TOPIC_BY_NAME[n]['icon']}  {n}  ·  {core.TOPIC_BY_NAME[n]['level']}"
                )
                st.caption(core.TOPIC_BY_NAME[topic]["desc"])
                S.sound_enabled = st.toggle("🔊 Sound effects", value=S.sound_enabled)
                if st.button("🚀 Start quiz", type="primary", use_container_width=True):
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
            S.pending_sound = "celebration"
        play_pending_sound()
        st.markdown('<div class="game-title">🎓 ICT Quiz Master</div>', unsafe_allow_html=True)
        r = S.result
        passed = r["correct"] >= PASS_MARK
        st.balloons()
        st.success(f"Quiz completed! Well done, {r['name']}!")
        st.markdown(f"## {'🏆 Passed!' if passed else '🎉 Completion certificate available!'}")
        st.caption(f"Topic: {r['topic']}")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Correct", f"{r['correct']}/{r['total']}")
        c2.metric("Final score", r["finalScore"])
        c3.metric("Streak bonus", f"+{r['streakBonus']}")
        c4.metric("Best streak", r["bestStreak"])
        if not passed:
            st.info(f"The pass mark is {PASS_MARK}/10. You still completed the quiz and can download your certificate.")
        with st.expander("📖 Review your answers", expanded=False):
            for n, answer in enumerate(quiz["answers"], 1):
                mark = "✅" if answer["ok"] else "❌"
                st.write(f"{mark} **Q{n}.** {answer['q']}")
        pdf = certificate_pdf(r)
        safe_name = "".join(ch for ch in r["name"] if ch.isalnum() or ch in "-_") or "student"
        st.download_button(
            "🎓 Download your PDF certificate",
            data=pdf,
            file_name=f"ICT_Quiz_Certificate_{safe_name}.pdf",
            mime="application/pdf",
            type="primary",
            use_container_width=True
        )
        if st.button("🔄 Try another quiz", use_container_width=True):
            S.quiz = None
            S.checked = False
            S.result = None
            S.pending_sound = None
            st.rerun()
        return

    i = quiz["index"]
    total = len(quiz["questions"])
    q = quiz["questions"][i]
    topic_info = core.TOPIC_BY_NAME[quiz["topic"]]

    # Row 1: title, timer and scores, all in one compact line at the top
    c_title, c_time, c_score, c_streak, c_best = st.columns([2.2, 1.35, 1.1, 1.2, 1.1], gap="small")
    c_title.markdown('<div class="mini-title">🎓 ICT Quiz Master<small>Learn ICT through a quiz game</small></div>',
                     unsafe_allow_html=True)
    with c_time:
        live_timer(quiz["started"])
    c_score.markdown(stat_chip("⭐ Score", quiz["points"] + quiz["bonus"]), unsafe_allow_html=True)
    c_streak.markdown(stat_chip("🔥 Streak", quiz["streak"]), unsafe_allow_html=True)
    c_best.markdown(stat_chip("🏆 Best", quiz["best"]), unsafe_allow_html=True)
    st.progress((i + 1) / total, text=f"Question {i + 1} of {total}")

    # Row 2: picture and feedback on the left, question and options on the right
    left, right = st.columns([1, 1.45], gap="large")
    with left:
        st.markdown(f'<div class="topic-pill">{topic_info["icon"]} <b>{quiz["topic"]}</b></div>', unsafe_allow_html=True)
        components.html(
            "<style>body{margin:0;overflow:hidden}</style>" + question_visual(q.get("pic")),
            height=VISUAL_HEIGHT, scrolling=False)
        if S.checked:
            if S.last_ok:
                st.success("✨ Correct! Great job! +10 points")
            else:
                st.error(f"Not quite. The correct answer is **{core.correct_text(q)}**.")
            if S.last_msg:
                st.info(f"🔥 {S.last_msg}")
            st.caption(f"💡 Learn: {q['why']}")
            play_pending_sound()
    with right:
        st.markdown(f'<div class="q-text">{q["text"]}</div>', unsafe_allow_html=True)
        choice = st.radio(
            "Choose one answer", core.option_text(q), index=None,
            key=f"answer_{id(quiz)}_{i}", disabled=S.checked, label_visibility="collapsed"
        )
        if not S.checked:
            if st.button("Check answer ✓", disabled=choice is None, type="primary", use_container_width=True):
                ok, msg = core.check_answer(quiz, core.letter_of(choice))
                S.checked, S.last_ok, S.last_msg = True, ok, msg
                S.pending_sound = "correct" if ok else "wrong"
                st.rerun()
        else:
            if st.button("Next question ➜" if i + 1 < total else "🏁 Finish quiz", type="primary", use_container_width=True):
                quiz["index"] += 1
                S.checked = False
                st.rerun()


def leaderboard_page():
    st.title("🏆 Leaderboard")
    topic = st.selectbox("Topic", ["All topics"] + list(core.TOPIC_BY_NAME))
    sort = st.radio("Sort by", ["score", "streak", "speed"], horizontal=True)
    rows = ranking(None if topic == "All topics" else topic, sort)
    if not rows:
        st.info("No results yet. Finish a quiz first!")
        return
    df = pd.DataFrame([{
        "Rank": n, "Name": e["name"], "Topic": e["topic"],
        "Score": e["finalScore"], "Correct": f"{e['correct']}/{e['total']}",
        "Best streak": e["bestStreak"], "Time (s)": e["timeSecs"]
    } for n, e in enumerate(rows, 1)])
    st.dataframe(df, hide_index=True, use_container_width=True)
    st.bar_chart(df.set_index("Name")["Score"])


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


page = st.sidebar.radio("Navigate", ["Take a quiz", "Leaderboard", "Teacher mode"])
{"Take a quiz": quiz_page, "Leaderboard": leaderboard_page, "Teacher mode": teacher_page}[page]()