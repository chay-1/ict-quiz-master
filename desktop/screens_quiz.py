import random
import tkinter as tk

from desktop.quiz_art import PIC_H, PIC_W, draw_picture
from core.quiz_data import (
    PASS_MARK, POINTS_PER_CORRECT, STREAK_BONUS, STREAK_LABEL,
    beep, final_score, fmt_time, penalty_for, ranking, save_result,
)
from core.quiz_questions import prepare
from core.quiz_theme import (
    AMBER, BG, BLUE, DARKRED, FONT, GREEN, GREY, LIGHT, MUTED, NAVY,
    ORANGE, RED, TIME_LIMIT, WHITE,
)
from desktop.widgets import FlatButton, bind_all, card, label, top_bar


OPT_STYLE = {"default": (WHITE, GREY), "selected": (LIGHT, BLUE),
             "correct": ("#ecfdf5", GREEN), "incorrect": ("#fef2f2", RED)}


class QuizScreen(tk.Frame):
    """We run the quiz and manage answers, the timer, and scoring."""

    def __init__(self, app, topic):
        super().__init__(app, bg=BG)
        self.app, self.topic = app, topic
        self.cur, self.selected, self.checked, self.review = 0, None, False, False
        self.records = {}          # index -> {selected, correct, attempts, locked}
        self.secs = 0
        self.streak = self.best = self.points = self.bonus = 0
        self.milestone, self.earned = None, 0
        self.qs = prepare(topic["id"])
        self.hidden, self.lifeline_used = {}, False     # 50/50 lifeline
        self.qleft, self.left = TIME_LIMIT, {}          # countdown per question
        app.bind("<Key>", self.on_key)                  # keyboard shortcuts
        self._build()
        self.render()
        self._tick_id = self.after(1000, self._tick)

    # ----- layout -----
    def _build(self):
        bar = top_bar(self)
        self.timer_lbl = label(bar, "00:00", 12, True, BLUE, LIGHT, padx=12, pady=4)
        self.timer_lbl.pack(side="right", padx=(8, 24))
        self.qtimer_lbl = label(bar, "", 12, True, GREEN, WHITE, padx=10, pady=4)
        self.qtimer_lbl.pack(side="right", padx=4)
        self.qnum_lbl = label(bar, "", 11, True)
        self.qnum_lbl.pack(side="right", padx=8)
        self.streak_lbl = label(bar, "", 11, True, padx=10, pady=4)
        self.streak_lbl.pack(side="right", padx=8)
        self.pts_lbl = label(bar, "", 11, True, BLUE, LIGHT, padx=10, pady=4)
        self.pts_lbl.pack(side="right", padx=8)

        trough = tk.Frame(self, bg=GREY, height=8)
        trough.pack(fill="x")
        self.fill = tk.Frame(trough, bg=BLUE)
        self.fill.place(relx=0, rely=0, relheight=1, relwidth=0)

        nav = tk.Frame(self, bg=WHITE)
        nav.pack(fill="x")
        label(nav, "Questions:", 9, fg=MUTED, bg=WHITE).pack(side="left", padx=(24, 6), pady=8)
        self.nav_btns = []
        for i in range(len(self.qs)):
            b = tk.Label(nav, text=str(i + 1), width=3, font=(FONT, 10, "bold"), cursor="hand2")
            b.pack(side="left", padx=2)
            b.bind("<Button-1>", lambda e, i=i: self.goto(i))
            self.nav_btns.append(b)
        self.answered_lbl = label(nav, "", 9, fg=MUTED, bg=WHITE)
        self.answered_lbl.pack(side="right", padx=24)
        self.best_lbl = label(nav, "", 9, True, ORANGE, WHITE)
        self.best_lbl.pack(side="right", padx=8)

        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True)
        body.grid_rowconfigure(0, weight=1)
        body.grid_columnconfigure(0, weight=1)
        inner = tk.Frame(body, bg=BG, width=760)
        inner.grid(row=0, column=0)

        self.banner_slot = tk.Frame(inner, bg=BG)
        self.banner_slot.pack(fill="x")
        qcard = card(inner, padx=20, pady=9)
        qcard.pack(fill="x", pady=(4, 6))
        self.pic = tk.Canvas(qcard, width=PIC_W, height=PIC_H, bg=WHITE, highlightthickness=0)
        self.q_lbl = label(qcard, "", 15, True, wraplength=470, justify="left")
        self.q_lbl.pack(side="left", anchor="w")

        self.opt_rows = {}
        for lab in "ABCD":
            row = tk.Frame(inner, bg=WHITE, highlightthickness=2, highlightbackground=GREY,
                           padx=14, pady=7, cursor="hand2")
            row.pack(fill="x", pady=4)
            tk.Label(row, text=lab, width=3, bg=BLUE, fg=WHITE, font=(FONT, 11, "bold")).pack(side="left")
            txt = tk.Label(row, text="", bg=WHITE, fg=NAVY, font=(FONT, 12), anchor="w")
            txt.pack(side="left", padx=12, fill="x", expand=True)
            bind_all(row, "<Button-1>", lambda e, l=lab: self.choose(l))
            self.opt_rows[lab] = (row, txt)

        self.action_slot = tk.Frame(inner, bg=BG)
        self.action_slot.pack(fill="x", pady=5)
        self.check_btn = FlatButton(self.action_slot, "CHECK ANSWER", self.check)
        self.check_btn.pack(side="left", fill="x", expand=True)
        self.fifty_btn = FlatButton(self.action_slot, "🎯 50/50", self.fifty, "blue")
        self.fifty_btn.pack(side="left", padx=(8, 0))
        self.fb_slot = tk.Frame(inner, bg=BG)
        self.fb_slot.pack(fill="x")

    # ----- helpers -----
    def locked(self, i):
        return self.records.get(i, {}).get("locked", False)

    def next_index(self):
        for i in range(len(self.qs)):
            if i != self.cur and not self.locked(i):
                return i
        return None

    def _paint_qtimer(self):
        if self.checked or self.review:
            self.qtimer_lbl.config(text="", bg=WHITE)
            return
        low = self.qleft <= 5
        self.qtimer_lbl.config(text=f"⏳ {max(self.qleft, 0)}s", fg=RED if low else GREEN,
                               bg="#fef2f2" if low else "#ecfdf5")

    def _tick(self):
        # We update the total time and question countdown every second.
        self.secs += 1
        self.timer_lbl.config(text=fmt_time(self.secs))
        if not self.checked and not self.review:
            self.qleft -= 1
            self._paint_qtimer()
            if self.qleft <= 0:
                self.timeout()
        self._tick_id = self.after(1000, self._tick)

    def destroy(self):
        try:
            self.app.unbind("<Key>")
            self.after_cancel(self._tick_id)
        except Exception:
            pass
        super().destroy()

    # ----- actions -----
    def on_key(self, e):
        # We let the student use A-D to answer, Enter to continue, and F for 50/50.
        k = e.keysym.lower()
        if k in ("a", "b", "c", "d"):
            self.choose(k.upper())
        elif k in ("return", "kp_enter"):
            if self.review:
                return
            self.cont() if self.checked else self.check()
        elif k == "f":
            self.fifty()

    def fifty(self):
        # We hide two wrong choices. The student can use this lifeline once per quiz.
        if self.lifeline_used or self.checked or self.review:
            return
        q = self.qs[self.cur]
        wrong = [l for l, _ in q["options"] if l != q["answer"]]
        self.hidden[self.cur] = set(random.sample(wrong, 2))
        if self.selected in self.hidden[self.cur]:
            self.selected = None
        self.lifeline_used = True
        self.render()

    def timeout(self):
        if self.checked or self.review:
            return
        self.apply_answer(None)

    def choose(self, lab):
        if lab in self.hidden.get(self.cur, ()):
            return
        if not self.checked and not self.review:
            self.selected = lab
            self.render()

    def check(self):
        if not self.selected or self.checked or self.review:
            return
        self.apply_answer(self.selected)

    def apply_answer(self, choice):
        # We check the answer, update the score and streak, and show feedback.
        q = self.qs[self.cur]
        done = self.records.get(self.cur)
        if done and done["correct"]:          # already scored: show the feedback again, do not count it twice
            self.selected, self.checked = done["selected"], True
            self.render()
            return
        ok = choice == q["answer"]
        prev = self.records.get(self.cur, {}).get("attempts", 0)
        self.selected = choice
        self.records[self.cur] = {"selected": choice, "correct": ok,
                                  "attempts": prev + 1, "locked": False}
        self.milestone, self.earned = None, 0
        if ok:
            self.streak += 1
            self.best = max(self.best, self.streak)
            self.points += POINTS_PER_CORRECT
            self.earned = POINTS_PER_CORRECT
            bonus = STREAK_BONUS.get(self.streak, 0)
            self.bonus += bonus
            if self.streak in STREAK_LABEL:
                self.milestone = (self.streak, STREAK_LABEL[self.streak], bonus)
        else:
            self.streak = 0
        beep("streak" if self.milestone and self.milestone[2] else "ok" if ok else "bad", self.app)
        self.checked = True
        self.render()

    def retry(self):
        self.checked, self.selected = False, None
        self.qleft = TIME_LIMIT
        self.render()

    def cont(self):
        # We save this answer and go to the next question or finish the quiz.
        self.records[self.cur]["locked"] = True
        nxt = self.next_index()
        if nxt is None:
            correct = sum(1 for r in self.records.values() if r["correct"])
            review = [{"text": q["text"], "ok": self.records[i]["correct"], "why": q["why"], "pic": q.get("pic"),
                       "right": dict(q["options"])[q["answer"]],
                       "yours": dict(q["options"]).get(self.records[i]["selected"], "No answer (time ran out)")}
                      for i, q in enumerate(self.qs)]
            self.app.finish_quiz(self.topic, {"review": review,
                "correct": correct, "points": self.points, "bonus": self.bonus,
                "best": self.best, "secs": self.secs, "endStreak": self.streak})
        else:
            self.goto(nxt)

    def goto(self, i):
        if i == self.cur and not self.review:
            return
        self.left[self.cur] = self.qleft
        self.cur = i
        self.qleft = self.left.get(i, TIME_LIMIT)
        rec = self.records.get(i)
        if rec:
            self.selected, self.review, self.checked = rec["selected"], rec["locked"], rec["locked"]
        else:
            self.selected, self.review, self.checked = None, False, False
        self.render()

    # ----- drawing -----
    def render(self):
        # We update the question, choices, progress, and feedback on screen.
        q = self.qs[self.cur]
        locked_n = sum(1 for r in self.records.values() if r["locked"])
        self.pts_lbl.config(text=f"⭐ {self.points + self.bonus} pts")
        self.streak_lbl.config(text=f"🔥 {self.streak}",
                               fg=ORANGE if self.streak else MUTED,
                               bg="#fff7ed" if self.streak else "#f1f5f9")
        self.qnum_lbl.config(text=f"Q{self.cur + 1}/{len(self.qs)}")
        self.fill.place_configure(relwidth=locked_n / len(self.qs))
        self.answered_lbl.config(text=f"{locked_n}/{len(self.qs)} answered")
        self.best_lbl.config(text=f"🏆 Best streak: {self.best}" if self.best else "")

        for i, b in enumerate(self.nav_btns):
            rec = self.records.get(i)
            if rec and rec["locked"]:
                bg, fg = (GREEN, WHITE) if rec["correct"] else (RED, WHITE)
            elif rec:
                bg, fg = AMBER, WHITE
            else:
                bg, fg = GREY, NAVY
            b.config(bg=bg, fg=fg, highlightthickness=2 if i == self.cur else 0, highlightbackground=NAVY)

        for w in self.banner_slot.winfo_children():
            w.destroy()
        if self.review:
            ban = tk.Frame(self.banner_slot, bg="#fffbeb", highlightthickness=1,
                           highlightbackground="#fde68a", padx=14, pady=8)
            ban.pack(fill="x", pady=(0, 6))
            label(ban, f"👁 Reviewing Question {self.cur + 1} (already answered)", 10, True, "#92400e").pack(side="left")
            nxt = self.next_index()
            if nxt is not None:
                lb = label(ban, "Back to Quiz →", 10, True, "#92400e", "#fef3c7", padx=8, pady=3, cursor="hand2")
                lb.pack(side="right")
                lb.bind("<Button-1>", lambda e: self.goto(nxt))

        self.q_lbl.config(text=f"Q{self.cur + 1}.  {q['text']}")
        if q.get("pic"):
            self.pic.pack(side="right", padx=(12, 0))
            draw_picture(self.pic, q["pic"])
            self.q_lbl.config(wraplength=470)
        else:
            self.pic.pack_forget()
            self.q_lbl.config(wraplength=640)
        for lab, text in q["options"]:
            row, txt = self.opt_rows[lab]
            if lab in self.hidden.get(self.cur, ()):
                row.config(bg=GREY, highlightbackground=GREY)
                txt.config(text="—  removed by 50/50", bg=GREY, fg=MUTED)
                continue
            if self.checked and lab == q["answer"]:
                state = "correct"
            elif self.checked and lab == self.selected:
                state = "incorrect"
            elif lab == self.selected:
                state = "selected"
            else:
                state = "default"
            bg, border = OPT_STYLE[state]
            row.config(bg=bg, highlightbackground=border)
            txt.config(text=text, bg=bg, fg=NAVY)

        if self.review:
            self.action_slot.pack_forget()
        else:
            self.action_slot.pack(fill="x", pady=5, before=self.fb_slot)
            is_last_q = self.cur == len(self.qs) - 1
            self.check_btn.config(text="FINISH QUIZ" if is_last_q else "CHECK ANSWER")
            self.check_btn.set_enabled(bool(self.selected) and not self.checked)
            self.fifty_btn.config(text="🎯 USED" if self.lifeline_used else "🎯 50/50")
            self.fifty_btn.set_enabled(not self.lifeline_used and not self.checked)
        self._paint_qtimer()
        self._feedback(q)

    def _feedback(self, q):
        for w in self.fb_slot.winfo_children():
            w.destroy()
        if not self.checked or self.review:
            return
        ok = self.selected == q["answer"]
        bg, edge = ("#ecfdf5", GREEN) if ok else ("#fef2f2", RED)
        box = tk.Frame(self.fb_slot, bg=bg, highlightthickness=2, highlightbackground=edge, padx=18, pady=9)
        box.pack(fill="x")
        if ok:
            label(box, "✓  Correct!   +10 points", 14, True, "#047857").pack(anchor="w")
            if self.milestone:
                n, text, bonus = self.milestone
                msg = f"🔥 {n} ANSWERS IN A ROW — {text}"
                if bonus:
                    msg += f"   +{bonus} STREAK BONUS"
                label(box, msg, 11, True, ORANGE).pack(anchor="w", pady=2)
        else:
            label(box, "⏰  Time's up!   0 points" if self.selected is None else "✕  Not Quite   0 points",
                  14, True, "#b91c1c").pack(anchor="w")
            label(box, f"💔 STREAK BROKEN — current streak: 0 · best streak: {self.best}",
                  11, True, ORANGE).pack(anchor="w", pady=2)
            label(box, f"The correct answer is {q['answer']}.", 11, True, "#b91c1c").pack(anchor="w")
        label(box, q["why"], 10, fg=MUTED, wraplength=660, justify="left").pack(anchor="w", pady=4)
        row = tk.Frame(box, bg=bg)
        row.pack(anchor="w", pady=(4, 0))
        finishing = self.next_index() is None
        if not ok:
            FlatButton(row, "TRY AGAIN", self.retry, "secondary").pack(side="left", padx=(0, 8))
        if ok:
            text = "FINISH QUIZ" if finishing else "CONTINUE →"
        else:
            text = "SKIP & FINISH" if finishing else "SKIP & CONTINUE"
        FlatButton(row, text, self.cont, "success" if ok else "primary").pack(side="left")


# ───────────────────────── Screen 9: Result ─────────────────────────
class ResultScreen(tk.Frame):
    """We show the final score, pass status, and next steps."""
    def __init__(self, app, topic, r, entry):
        super().__init__(app, bg=BG)
        self.app = app
        pass_ = r["correct"] >= PASS_MARK
        pct = r["correct"] * 10
        if pass_:
            Confetti(self)
            beep("streak", app)
        wrap = tk.Frame(self, bg=BG)
        wrap.place(relx=0.5, rely=0.5, anchor="center")

        ban = tk.Frame(wrap, bg=NAVY if pass_ else DARKRED, padx=60, pady=16)
        ban.pack(fill="x")
        label(ban, "QUIZ COMPLETE!", 11, True, "#93c5fd").pack()
        label(ban, f"🏆 {entry['finalScore']}", 40, True, WHITE).pack()
        label(ban, "PASSED ✓" if pass_ else "TRY AGAIN ✗", 13, True, "#bfdbfe").pack()

        label(wrap, f"{topic['icon']} {topic['name']}  ·  {app.student}  ·  {pct}%", 12, True).pack(pady=8)

        grid = tk.Frame(wrap, bg=BG)
        grid.pack()
        items = [("✓ CORRECT", f"{r['correct']}/10", GREEN),
                 ("✗ INCORRECT", str(10 - r["correct"]), RED),
                 ("🎯 PASS MARK", f"{PASS_MARK}/10", BLUE),
                 ("🔥 BEST STREAK", str(r["best"]), ORANGE),
                 ("⚡ STREAK BONUS", f"+{r['bonus']}", BLUE),
                 ("📉 PENALTY", f"−{entry['penalty']}" if entry["penalty"] else "0", RED if entry["penalty"] else MUTED),
                 ("⏱ TIME TAKEN", fmt_time(r["secs"]), NAVY),
                 ("🏆 FINAL SCORE", str(entry["finalScore"]), NAVY)]
        for i, (t, v, col) in enumerate(items):
            c = card(grid, padx=18, pady=10, width=170)
            c.grid(row=i // 4, column=i % 4, padx=5, pady=5)
            label(c, v, 18, True, col).pack()
            label(c, t, 8, True, MUTED).pack()

        label(wrap, f"{r['points']} points + {r['bonus']} streak bonus − {entry['penalty']} penalty "
                    f"= {entry['finalScore']}", 10, fg=MUTED).pack(pady=4)
        label(wrap, self._motivation(r, entry), 11, True, ORANGE).pack(pady=2)

        row = tk.Frame(wrap, bg=BG)
        row.pack(pady=10)
        FlatButton(row, "VIEW PERFORMANCE", lambda: app.show_performance(topic, r, entry)).pack(side="left", padx=5)
        FlatButton(row, "REVIEW ANSWERS", lambda: app.show_review(topic, r, entry), "secondary").pack(side="left", padx=5)
        FlatButton(row, "🏆 LEADERBOARD", app.show_leaderboard, "secondary").pack(side="left", padx=5)
        FlatButton(row, "TRY AGAIN", app.show_topics, "secondary").pack(side="left", padx=5)
        FlatButton(row, "HOME", app.show_welcome, "secondary").pack(side="left", padx=5)

    @staticmethod
    def _motivation(r, entry):
        if r["correct"] == PASS_MARK - 1:
            return "One more correct answer would have secured a PASS!"
        if r["correct"] < PASS_MARK:
            return "Review the questions and try again. You can beat this score!"
        higher = [e["finalScore"] for e in ranking() if e["finalScore"] > entry["finalScore"]]
        if higher:
            return f"You're only {min(higher) - entry['finalScore']} points away from the next rank!"
        return "You're at the top of the leaderboard. Can you beat your best streak?"


class Confetti(tk.Canvas):
    """Falling confetti drawn behind the result card when the student passes."""
    COLORS = [BLUE, GREEN, AMBER, RED, "#a855f7", "#06b6d4"]

    def __init__(self, parent):
        super().__init__(parent, bg=BG, highlightthickness=0)
        self.place(x=0, y=0, relwidth=1, relheight=1)
        self.items, self.frame = [], 0
        for _ in range(80):
            size = random.randint(6, 11)
            item = self.create_rectangle(0, 0, size, size, fill=random.choice(self.COLORS), outline="")
            self.items.append([item, random.random(), random.random() * -1, size, random.uniform(0.006, 0.016)])
        self.after(50, self.step)

    def step(self):
        # We move the confetti down the screen to create an animation.
        try:
            w, h = self.winfo_width(), self.winfo_height()
            self.frame += 1
            for it in self.items:
                it[2] += it[4]
                if it[2] > 1.05 and self.frame < 150:
                    it[2] = -0.05
                x, y = it[1] * w, it[2] * h
                self.coords(it[0], x, y, x + it[3], y + it[3])
            if self.frame < 220:
                self.after(40, self.step)
        except tk.TclError:      # screen was closed
            pass


# ───────────────────────── Review answers ─────────────────────────
class ReviewScreen(tk.Frame):
    """We show the student's answer, correct answer, and explanation."""
    def __init__(self, app, topic, r, entry):
        super().__init__(app, bg=BG)
        self.app, self.topic, self.r, self.entry, self.i = app, topic, r, entry, 0
        top_bar(self, "ICT Quiz Master · Review Answers")
        self.wrap = tk.Frame(self, bg=BG)
        self.wrap.place(relx=0.5, rely=0.5, anchor="center")
        self.show()

    def show(self):
        for w in self.wrap.winfo_children():
            w.destroy()
        d, total = self.r["review"][self.i], len(self.r["review"])
        label(self.wrap, f"Question {self.i + 1} of {total}", 11, True, MUTED).pack()
        box = card(self.wrap, padx=24, pady=18)
        box.pack(pady=10)
        if d.get("pic"):
            pc = tk.Canvas(box, width=PIC_W, height=PIC_H, bg=WHITE, highlightthickness=0)
            pc.pack(anchor="w", pady=(0, 8))
            draw_picture(pc, d["pic"])
        label(box, d["text"], 15, True, wraplength=640, justify="left").pack(anchor="w")
        label(box, ("✓  Your answer: " if d["ok"] else "✕  Your answer: ") + d["yours"], 12, True,
              GREEN if d["ok"] else RED, wraplength=640, justify="left").pack(anchor="w", pady=(12, 2))
        if not d["ok"]:
            label(box, "✓  Correct answer: " + d["right"], 12, True, GREEN,
                  wraplength=640, justify="left").pack(anchor="w")
        label(box, d["why"], 10, fg=MUTED, wraplength=640, justify="left").pack(anchor="w", pady=(10, 0))
        row = tk.Frame(self.wrap, bg=BG)
        row.pack(pady=8)
        prev = FlatButton(row, "← PREVIOUS", lambda: self.move(-1), "secondary")
        prev.pack(side="left", padx=5)
        prev.set_enabled(self.i > 0)
        nxt = FlatButton(row, "NEXT →", lambda: self.move(1))
        nxt.pack(side="left", padx=5)
        nxt.set_enabled(self.i < total - 1)
        FlatButton(row, "BACK TO RESULT", lambda: self.app.swap(ResultScreen, self.topic, self.r, self.entry),
                   "secondary").pack(side="left", padx=5)

    def move(self, step):
        self.i += step
        self.show()


# ───────────────────────── Screen 10: Performance ─────────────────────────
class PerformanceScreen(tk.Frame):
    """We show the student's score as a chart and statistics."""
    def __init__(self, app, topic, r, entry):
        super().__init__(app, bg=BG)
        pct = r["correct"] * 10
        wrap = tk.Frame(self, bg=BG)
        wrap.place(relx=0.5, rely=0.5, anchor="center")
        label(wrap, "Your Performance", 24, True).pack()
        label(wrap, f"{topic['icon']} {topic['name']}", 13, True, BLUE).pack(pady=4)

        cv = tk.Canvas(wrap, width=170, height=170, bg=BG, highlightthickness=0)
        cv.pack(pady=6)
        cv.create_oval(15, 15, 155, 155, outline=GREY, width=14)
        if pct:
            cv.create_arc(15, 15, 155, 155, start=90, extent=-3.6 * pct, style="arc",
                          outline=GREEN if pct >= 60 else RED, width=14)
        cv.create_text(85, 85, text=f"{pct}%", font=(FONT, 26, "bold"), fill=NAVY)
        label(wrap, "Good Job!" if pct >= 60 else "Keep Practising", 14, True).pack()

        box = card(wrap, padx=30, pady=12)
        box.pack(pady=10, fill="x")
        rows = [("Correct Answers", r["correct"]), ("Incorrect Answers", 10 - r["correct"]),
                ("Total Questions", 10), ("Score", f"{r['correct']}/10"),
                ("Final Points", entry["finalScore"]), ("Time Taken", fmt_time(r["secs"])),
                ("Status", "PASS" if r["correct"] >= PASS_MARK else "TRY AGAIN")]
        for k, v in rows:
            line = tk.Frame(box, bg=WHITE)
            line.pack(fill="x", pady=2)
            label(line, k, 11, fg=MUTED).pack(side="left")
            label(line, str(v), 11, True).pack(side="right")

        row = tk.Frame(wrap, bg=BG)
        row.pack(pady=6)
        FlatButton(row, "TRY ANOTHER QUIZ", self.master.show_topics).pack(side="left", padx=6)
        FlatButton(row, "EXIT", self.master.show_welcome, "secondary").pack(side="left", padx=6)


# ───────────────────────── Leaderboard (interactive) ─────────────────────────
# We make button groups for choosing leaderboard filters.
