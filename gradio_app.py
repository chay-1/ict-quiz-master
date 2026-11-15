"""ICT Quiz Master — Gradio web application.
Run: python gradio_app.py
"""
import base64
import json

import pandas as pd
import gradio as gr

from core import quiz_core as core
from core.quiz_custom import load_custom_questions, save_custom_questions
from core.quiz_data import PASS_MARK, ranking, fmt_time
from web.web_game_assets import question_visual, certificate_file, SOUND_DIR

TOPIC_NAMES = list(core.TOPIC_BY_NAME)


# ── Sound effects ────────────────────────────────────────────────────────────
# The sounds are loaded ONCE in the browser and played with JavaScript after each
# click, with no audio player on the page. (Putting an <audio> tag into an HTML box worked only for question 1,
# because Gradio does not redraw a box when its content stays the same.)
def _load_sound_files():
    uris = {}
    for kind in ("correct", "wrong", "celebration"):
        for ext, mime in ((".mp3", "audio/mpeg"), (".wav", "audio/wav")):
            path = SOUND_DIR / f"{kind}{ext}"
            if path.is_file() and path.stat().st_size:
                uris[kind] = f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode("ascii")
                break
    return uris


LOAD_SOUNDS_JS = """() => {
  const files = %s;
  // Web Audio plays the sound without any audio player, so the browser shows no
  // play/pause music icon.
  const AudioCtx = window.AudioContext || window.webkitAudioContext;
  const ctx = new AudioCtx();
  window.quizBuffers = {};
  const toBuffer = (uri) => {
    const text = atob(uri.split(',')[1]);
    const bytes = new Uint8Array(text.length);
    for (let i = 0; i < text.length; i++) { bytes[i] = text.charCodeAt(i); }
    return bytes.buffer;
  };
  for (const name in files) {
    ctx.decodeAudioData(toBuffer(files[name]))
      .then((buffer) => { window.quizBuffers[name] = buffer; })
      .catch(() => {});
  }
  const unlock = () => { if (ctx.state === 'suspended') { ctx.resume(); } };
  document.addEventListener('pointerdown', unlock);
  document.addEventListener('keydown', unlock);
  window.playQuizSound = (name) => {
    const buffer = window.quizBuffers[name];
    if (!buffer) { return; }
    unlock();
    const source = ctx.createBufferSource();
    source.buffer = buffer;
    source.connect(ctx.destination);
    source.start(0);
  };
}""" % json.dumps(_load_sound_files())

# the feedback text contains a tick for a correct answer and a cross for a wrong one
ANSWER_SOUND_JS = """(feedbackText, soundOn) => {
  if (soundOn && feedbackText) {
    window.playQuizSound(feedbackText.includes('\u2705') ? 'correct' : 'wrong');
  }
}"""

# the result summary stays empty until the last question has been finished
FINISH_SOUND_JS = """(summaryText, soundOn) => {
  if (soundOn && summaryText && summaryText.trim()) { window.playQuizSound('celebration'); }
}"""


def _timer_text(state):
    if not state:
        return "⏱️ **Time:** 00:00"
    import time
    elapsed = int(state.get("elapsed_final", time.time() - state["started"]))
    return f"⏱️ **Time:** {elapsed // 60:02d}:{elapsed % 60:02d}"


def start_quiz(name, topic, sound_on):
    if not name or len(name.strip()) < 2:
        raise gr.Error("Please enter your name (at least 2 characters).")
    state = core.new_quiz(topic)
    state["student"] = name.strip()
    state["sound_on"] = bool(sound_on)
    q = state["questions"][0]
    topic_info = core.TOPIC_BY_NAME[topic]
    return (
        state, gr.update(visible=False), gr.update(visible=True), gr.update(visible=False),
        _timer_text(state), "Question 1 of 10", "0", "0", "0",
        f"### {topic_info['icon']} Topic: **{topic}**",
        question_visual(q.get("pic")), q["text"], gr.update(choices=core.option_text(q), value=None),
        "", gr.update(visible=True), gr.update(visible=False), None
    )


def check_answer(state, choice):
    if not state:
        raise gr.Error("Start a quiz first.")
    if not choice:
        raise gr.Error("Choose an answer first.")
    q = state["questions"][state["index"]]
    ok, msg = core.check_answer(state, core.letter_of(choice))
    if ok:
        feedback = "### ✅ Correct! Great job! **+10 points**"
        if msg:
            feedback += f"\n\n🔥 {msg}"
    else:
        feedback = f"### ❌ Not quite. Correct answer: **{core.correct_text(q)}**"
    return (
        state, feedback,
        gr.update(visible=False), gr.update(visible=True),
        state["points"] + state["bonus"], state["streak"], state["best"]
    )


def next_question(state):
    if not state:
        raise gr.Error("No active quiz.")
    state["index"] += 1
    if core.is_finished(state):
        result = core.finish_quiz(state, state["student"])
        state["elapsed_final"] = result["timeSecs"]
        pdf_path = certificate_file(result)
        passed = result["correct"] >= PASS_MARK
        headline = "🏆 **Passed!**" if passed else "🎉 **Quiz completed!**"
        summary = (
            f"## {headline}\n\n"
            f"Well done, **{result['name']}**!\n\n"
            f"- **Topic:** {result['topic']}\n"
            f"- **Correct answers:** {result['correct']}/{result['total']}\n"
            f"- **Final score:** {result['finalScore']}\n"
            f"- **Streak bonus:** +{result['streakBonus']}\n"
            f"- **Best streak:** {result['bestStreak']}\n"
            f"- **Time taken:** {fmt_time(result['timeSecs'])}\n\n"
            + (f"Pass mark: {PASS_MARK}/10." if passed else
               f"You completed all questions. The pass mark is {PASS_MARK}/10; your completion certificate is still available.")
        )
        review = "\n\n".join(
            f"{'✅' if a['ok'] else '❌'} **Q{i}.** {a['q']}  \nYour answer: {a['chosen']} · Correct answer: {a['right']}"
            for i, a in enumerate(state["answers"], 1)
        )
        return (
            state, gr.update(visible=False), gr.update(visible=True), summary, review,
            pdf_path, _timer_text(state),
            "Quiz completed", result["finalScore"], result["endStreak"],
            result["bestStreak"], "", "", "",
            gr.update(choices=[], value=None), "",
            gr.update(visible=False), gr.update(visible=False)
        )

    i = state["index"]
    q = state["questions"][i]
    return (
        state, gr.update(visible=True), gr.update(visible=False), "", "",
        None, _timer_text(state),
        f"Question {i + 1} of {len(state['questions'])}",
        state["points"] + state["bonus"], state["streak"], state["best"],
        f"### {core.TOPIC_BY_NAME[state['topic']]['icon']} Topic: **{state['topic']}**",
        question_visual(q.get("pic")), q["text"],
        gr.update(choices=core.option_text(q), value=None),
        "", gr.update(visible=True), gr.update(visible=False)
    )


def timer_tick(state):
    return _timer_text(state)


def restart_quiz():
    return (
        None, gr.update(visible=True), gr.update(visible=False), gr.update(visible=False),
        "⏱️ **Time:** 00:00", "", "", "", "", "", "", None
    )


def load_leaderboard(topic, sort_by):
    rows = ranking(None if topic == "All topics" else topic, sort_by)
    data = [[i, e["name"], e["topic"], e["finalScore"], f"{e['correct']}/{e['total']}",
             e["bestStreak"], fmt_time(e.get("timeSecs", 0))]
            for i, e in enumerate(rows, 1)]
    return pd.DataFrame(data, columns=["Rank", "Name", "Topic", "Score", "Correct", "Best streak", "Time"])


def add_teacher_question(question, answer, level):
    questions = load_custom_questions()
    if not question.strip() or not answer.strip():
        raise gr.Error("Enter both a question and a model answer.")
    questions.append({"q": question.strip(), "a": answer.strip(), "level": level})
    if not save_custom_questions(questions):
        raise gr.Error("Could not save teacher_questions.json.")
    return "", "", questions, f"Added successfully. {len(questions)} question(s) saved."


def delete_teacher_questions(index):
    questions = load_custom_questions()
    if not questions:
        return questions, "There are no saved questions."
    try:
        remove_at = int(index) - 1
        removed = questions.pop(remove_at)
    except (ValueError, IndexError):
        raise gr.Error("Enter a valid question number to delete.")
    save_custom_questions(questions)
    return questions, f"Deleted: {removed['q']}"


QUIZ_CSS = r"""
/* Balanced quiz layout: keep the illustration supportive, not dominant. */
.gradio-container { max-width: 1180px !important; margin: 0 auto !important; }
.quiz-visual { width: min(100%, 390px) !important; max-width: 390px !important; aspect-ratio: 16 / 9 !important;
  height: auto !important; margin: 0 auto 4px !important; overflow: hidden !important; }
.quiz-visual svg { width: 100% !important; height: 100% !important; display: block !important; }
.picture-box { padding: 0 !important; min-height: 0 !important; border: 0 !important; background: transparent !important; }
.question-text { margin-top: 0 !important; margin-bottom: 4px !important; }
.question-text h1, .question-text h2, .question-text h3, .question-text p {
  font-size: clamp(24px, 2.2vw, 31px) !important; line-height: 1.35 !important;
  font-weight: 750 !important; color: #172554 !important; margin: 0 !important; }
.answer-options label, .answer-options span, .answer-options p {
  font-size: 19px !important; line-height: 1.55 !important; }
/* Answer options: the same 2 x 2 grid and the same box size for every question.
   Gradio puts the class on the <fieldset> itself, so both selectors are listed. */
.answer-options > div:has(> label),
.answer-options fieldset > div:has(> label) {
  display: grid !important; grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
  grid-auto-rows: 1fr !important; gap: 12px !important; width: 100% !important;
}
.answer-options label {
  display: flex !important; align-items: center !important; justify-content: flex-start !important;
  text-align: left !important; gap: 12px !important; width: 100% !important; min-width: 0 !important;
  min-height: 64px !important; margin: 0 !important; padding: 12px 18px !important; box-sizing: border-box !important;
}
.answer-options label span, .answer-options label p { text-align: left !important; margin: 0 !important; }
.timer-top { font-size: 20px !important; font-weight: 750 !important; color: #172554 !important;
  background: #eff6ff !important; border: 1px solid #bfdbfe !important;
  border-radius: 12px !important; padding: 10px 16px !important; width: fit-content !important; }
@media (max-width: 700px) {
  .quiz-visual { max-width: 100% !important; }
  .question-text h1, .question-text h2, .question-text h3, .question-text p { font-size: 23px !important; }
  .answer-options label, .answer-options span, .answer-options p { font-size: 17px !important; }
  .answer-options > div:has(> label), .answer-options fieldset > div:has(> label) { grid-template-columns: 1fr !important; }
}
"""

with gr.Blocks(title="ICT Quiz Master", css=QUIZ_CSS) as demo:
    gr.Markdown("# 🎓 ICT Quiz Master\nLearn ICT through an interactive quiz game.")
    demo.load(None, inputs=None, outputs=None, js=LOAD_SOUNDS_JS)
    with gr.Tabs():
        with gr.Tab("🎮 Take a quiz"):
            quiz_state = gr.State(None)
            timer = gr.Timer(value=1, active=True)
            with gr.Column(visible=True) as setup_group:
                student_name = gr.Textbox(label="Your name", placeholder="Enter your name", max_lines=1)
                topic_choice = gr.Dropdown(
                    choices=TOPIC_NAMES, value=TOPIC_NAMES[0],
                    label="Choose your ICT topic", interactive=True
                )
                sound_toggle = gr.Checkbox(value=True, label="🔊 Sound effects")
                start_button = gr.Button("🚀 Start quiz", variant="primary")
            with gr.Column(visible=False) as game_group:
                timer_label = gr.Markdown("⏱️ **Time:** 00:00", elem_classes=["timer-top"])
                progress_label = gr.Markdown()
                with gr.Row():
                    score_label = gr.Number(value=0, label="⭐ Score", interactive=False)
                    streak_label = gr.Number(value=0, label="🔥 Current streak", interactive=False)
                    best_label = gr.Number(value=0, label="🏆 Best streak", interactive=False)
                topic_label = gr.Markdown()
                picture = gr.HTML(elem_classes=["picture-box"])
                question_label = gr.Markdown(elem_classes=["question-text"])
                answer_choice = gr.Radio(choices=[], label="Choose one answer", elem_classes=["answer-options"])
                with gr.Row():
                    check_button = gr.Button("Check answer ✓", variant="primary", visible=True)
                    next_button = gr.Button("Next question ➜", variant="primary", visible=False)
                feedback = gr.Markdown()
            with gr.Column(visible=False) as result_group:
                result_summary = gr.Markdown()
                review_output = gr.Markdown()
                certificate_output = gr.File(label="🎓 Download your PDF certificate")
                restart_button = gr.Button("🔄 Try another quiz", variant="primary")
            timer.tick(timer_tick, inputs=quiz_state, outputs=timer_label)

            start_button.click(
                start_quiz,
                inputs=[student_name, topic_choice, sound_toggle],
                outputs=[quiz_state, setup_group, game_group, result_group, timer_label,
                         progress_label, score_label, streak_label, best_label, topic_label,
                         picture, question_label, answer_choice, feedback, check_button,
                         next_button, certificate_output]
            )
            check_button.click(
                check_answer,
                inputs=[quiz_state, answer_choice],
                outputs=[quiz_state, feedback, check_button, next_button,
                         score_label, streak_label, best_label]
            ).success(None, inputs=[feedback, sound_toggle], outputs=None, js=ANSWER_SOUND_JS)
            next_button.click(
                next_question,
                inputs=quiz_state,
                outputs=[quiz_state, game_group, result_group, result_summary, review_output,
                         certificate_output, timer_label, progress_label,
                         score_label, streak_label, best_label, topic_label, picture,
                         question_label, answer_choice, feedback, check_button, next_button]
            ).success(None, inputs=[result_summary, sound_toggle], outputs=None, js=FINISH_SOUND_JS)
            restart_button.click(
                restart_quiz,
                outputs=[quiz_state, setup_group, game_group, result_group, timer_label,
                         progress_label, score_label, streak_label, best_label, topic_label,
                         picture, question_label]
            )

        with gr.Tab("🏆 Leaderboard"):
            leaderboard_topic = gr.Dropdown(
                choices=["All topics"] + TOPIC_NAMES, value="All topics", label="Topic"
            )
            leaderboard_sort = gr.Dropdown(
                choices=["score", "streak", "speed"], value="score", label="Sort by"
            )
            leaderboard_button = gr.Button("Refresh leaderboard")
            leaderboard_table = gr.Dataframe(
                headers=["Rank", "Name", "Topic", "Score", "Correct", "Best streak", "Time"],
                interactive=False
            )
            leaderboard_button.click(load_leaderboard, [leaderboard_topic, leaderboard_sort], leaderboard_table)
            leaderboard_topic.change(load_leaderboard, [leaderboard_topic, leaderboard_sort], leaderboard_table)
            leaderboard_sort.change(load_leaderboard, [leaderboard_topic, leaderboard_sort], leaderboard_table)

        with gr.Tab("👩‍🏫 Teacher mode"):
            teacher_question = gr.Textbox(label="Question")
            teacher_answer = gr.Textbox(label="Model answer")
            teacher_level = gr.Dropdown(["Easy", "Medium", "Hard"], value="Easy", label="Difficulty")
            add_button = gr.Button("Add question", variant="primary")
            teacher_status = gr.Markdown()
            teacher_list = gr.JSON(value=load_custom_questions(), label="Saved custom questions")
            delete_number = gr.Number(label="Question number to delete", precision=0)
            delete_button = gr.Button("Delete question", variant="stop")
            add_button.click(
                add_teacher_question,
                [teacher_question, teacher_answer, teacher_level],
                [teacher_question, teacher_answer, teacher_list, teacher_status]
            )
            delete_button.click(
                delete_teacher_questions,
                [delete_number],
                [teacher_list, teacher_status]
            )

if __name__ == "__main__":
    demo.launch()