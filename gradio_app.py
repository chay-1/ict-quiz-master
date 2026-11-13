"""ICT Quiz Master - Gradio version.   Run:  python gradio_app.py"""
import gradio as gr
import pandas as pd

import quiz_core as core
from quiz_custom import load_custom_questions, save_custom_questions
from quiz_data import PASS_MARK, ranking

TOPIC_NAMES = list(core.TOPIC_BY_NAME)


# ───────────────────────── Quiz tab ─────────────────────────
# Gradio keeps the running quiz in a gr.State object (one copy per browser tab).
# Each function returns a dictionary {component: new_value}, so we only name
# the parts of the page that change.
def status_line(s):
    return (f"Question {s['index'] + 1} of {len(s['questions'])}   |   "
            f"Score: {s['points'] + s['bonus']}   |   Streak: {s['streak']} 🔥")


def show_question(s):
    q = s["questions"][s["index"]]
    return {question: f"### {q['text']}",
            choices: gr.update(choices=core.option_text(q), value=None, interactive=True),
            status: status_line(s), feedback: "",
            check_btn: gr.update(visible=True), next_btn: gr.update(visible=False)}


def start_quiz(name, topic_name):
    if len((name or "").strip()) < 2:
        gr.Warning("Please enter a name with at least 2 characters.")
        return {summary: ""}
    s = core.new_quiz(topic_name)
    s["student"] = name.strip()
    return {state: s, setup: gr.update(visible=False), quiz_box: gr.update(visible=True),
            summary: "", again_btn: gr.update(visible=False), **show_question(s)}


def check(s, choice):
    if not choice:
        gr.Warning("Choose an answer first.")
        return {status: status_line(s)}
    q = s["questions"][s["index"]]
    ok, msg = core.check_answer(s, core.letter_of(choice))
    text = ("✅ **Correct!**  " if ok else f"❌ **Not quite.** Correct answer: {core.correct_text(q)}.  ") \
        + (f"\n\n🔥 {msg}" if msg else "") + f"\n\n💡 {q['why']}"
    last = s["index"] + 1 >= len(s["questions"])
    return {state: s, feedback: text, status: status_line(s),
            choices: gr.update(interactive=False), check_btn: gr.update(visible=False),
            next_btn: gr.update(visible=True, value="Finish quiz" if last else "Next ➜")}


def next_question(s):
    s["index"] += 1
    if not core.is_finished(s):
        return {state: s, **show_question(s)}
    r = core.finish_quiz(s, s["student"])
    verdict = "✅ Passed" if r["correct"] >= PASS_MARK else f"❌ Pass mark is {PASS_MARK}. Try again!"
    return {state: s, quiz_box: gr.update(visible=False), again_btn: gr.update(visible=True),
            summary: (f"## Well done, {r['name']}!\n**Final score: {r['finalScore']}**  \n"
                      f"Correct: {r['correct']}/{r['total']}  |  Streak bonus: +{r['streakBonus']}  |  "
                      f"Penalty: -{r['penalty']}  \nBest streak: {r['bestStreak']}  |  {verdict}")}


def try_again():
    return {setup: gr.update(visible=True), summary: "", again_btn: gr.update(visible=False)}


# ───────────────────────── Leaderboard tab ─────────────────────────
def show_board(topic, sort):
    rows = ranking(None if topic == "All topics" else topic, sort)
    return pd.DataFrame([{"Rank": n, "Name": e["name"], "Topic": e["topic"], "Score": e["finalScore"],
                          "Correct": f"{e['correct']}/{e['total']}", "Best streak": e["bestStreak"],
                          "Time (s)": e["timeSecs"]} for n, e in enumerate(rows, 1)],
                        columns=["Rank", "Name", "Topic", "Score", "Correct", "Best streak", "Time (s)"])


# ───────────────────────── Teacher tab ─────────────────────────
def question_table():
    return pd.DataFrame([{"No.": n, "Level": x["level"], "Question": x["q"], "Model answer": x["a"]}
                         for n, x in enumerate(load_custom_questions(), 1)],
                        columns=["No.", "Level", "Question", "Model answer"])


def add_question(q, a, level):
    if not (q or "").strip() or not (a or "").strip():
        return "⚠️ Please type both a question and a model answer.", question_table(), q, a
    items = load_custom_questions()
    items.append({"q": q.strip(), "a": a.strip(), "level": level})
    save_custom_questions(items)
    return f"✅ Question added ({len(items)} total).", question_table(), "", ""


def delete_question(number):
    items = load_custom_questions()
    n = int(number or 0)
    if not 1 <= n <= len(items):
        return "⚠️ Type a valid question number from the table.", question_table()
    removed = items.pop(n - 1)
    save_custom_questions(items)
    return f"🗑️ Deleted: {removed['q'][:40]}", question_table()


# ───────────────────────── Page layout ─────────────────────────
with gr.Blocks(title="ICT Quiz Master", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🎓 ICT Quiz Master")
    with gr.Tab("Take a quiz"):
        state = gr.State()
        with gr.Group(visible=True) as setup:
            name = gr.Textbox(label="Your name", max_length=20)
            topic = gr.Dropdown(TOPIC_NAMES, value=TOPIC_NAMES[0], label="Topic")
            start_btn = gr.Button("Start quiz", variant="primary")
        with gr.Group(visible=False) as quiz_box:
            status = gr.Markdown()
            question = gr.Markdown()
            choices = gr.Radio([], label="Choose one answer")
            feedback = gr.Markdown()
            check_btn = gr.Button("Check answer", variant="primary")
            next_btn = gr.Button("Next ➜", visible=False)
        summary = gr.Markdown()
        again_btn = gr.Button("Try another quiz", visible=False)

        start_btn.click(start_quiz, [name, topic],
                        {state, setup, quiz_box, summary, again_btn, question, choices,
                         status, feedback, check_btn, next_btn})
        check_btn.click(check, [state, choices],
                        {state, feedback, status, choices, check_btn, next_btn})
        next_btn.click(next_question, state,
                       {state, quiz_box, again_btn, summary, question, choices,
                        status, feedback, check_btn, next_btn})
        again_btn.click(try_again, None, {setup, summary, again_btn})
    with gr.Tab("Leaderboard"):
        lb_topic = gr.Dropdown(["All topics"] + TOPIC_NAMES, value="All topics", label="Topic")
        lb_sort = gr.Radio(["score", "streak", "speed"], value="score", label="Sort by")
        board = gr.Dataframe(value=show_board("All topics", "score"), interactive=False)
        gr.Button("Refresh").click(show_board, [lb_topic, lb_sort], board)
    with gr.Tab("Teacher mode"):
        t_q, t_a = gr.Textbox(label="Question"), gr.Textbox(label="Model answer")
        t_level = gr.Dropdown(["Easy", "Medium", "Hard"], value="Easy", label="Difficulty")
        t_msg = gr.Markdown()
        table = gr.Dataframe(value=question_table(), interactive=False)
        gr.Button("Add question", variant="primary").click(add_question, [t_q, t_a, t_level],
                                                           [t_msg, table, t_q, t_a])
        number = gr.Number(label="Question number to delete", precision=0)
        gr.Button("Delete question").click(delete_question, number, [t_msg, table])

if __name__ == "__main__":
    demo.launch()
