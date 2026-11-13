import time
import tkinter as tk

from quiz_custom import load_custom_questions, save_custom_questions
from quiz_data import fmt_time
from quiz_theme import BG, FONT, GREEN, LEVEL_COLOR, MUTED, NAVY, ORANGE, RED, WHITE
from widgets import FlatButton, card, chip_group, label, top_bar


class TeacherSetupScreen(tk.Frame):
    """FR1 Add questions · FR4 Delete questions · FR6 Assign a difficulty to each question."""

    def __init__(self, app):
        super().__init__(app, bg=BG)
        self.app, self.questions = app, load_custom_questions()
        self.level_var = tk.StringVar(value="Easy")
        top_bar(self, "ICT Quiz Master · Teacher Mode")
        wrap = tk.Frame(self, bg=BG)
        wrap.pack(pady=16)
        label(wrap, "Create Open-Ended Questions", 20, True).pack()

        r = tk.Frame(wrap, bg=BG)
        r.pack(pady=6)
        label(r, "Student name:", 11, True).pack(side="left", padx=6)
        self.name = tk.Entry(r, font=(FONT, 12), width=24, relief="solid", bd=1)
        self.name.pack(side="left")

        for text, attr in [("Question", "q"), ("Model answer", "a")]:
            label(wrap, text, 11, True).pack(anchor="w", pady=(8, 0))
            e = tk.Entry(wrap, font=(FONT, 12), width=70, relief="solid", bd=1)
            e.pack()
            setattr(self, attr, e)

        # difficulty chosen for each question
        lv = tk.Frame(wrap, bg=BG)
        lv.pack(pady=(8, 0))
        label(lv, "Difficulty:", 11, True).pack(side="left", padx=(0, 6))
        chip_group(lv, [("Easy", "Easy"), ("Medium", "Medium"), ("Hard", "Hard")], self.level_var, 10)

        FlatButton(wrap, "+ ADD QUESTION", self.add, "blue", 11).pack(pady=8)
        self.msg = label(wrap, "", 10, True, MUTED)
        self.msg.pack()

        self.listbox = tk.Listbox(wrap, width=80, height=8, font=(FONT, 11),
                                  selectmode="single", exportselection=False)
        self.listbox.pack()
        self.listbox.bind("<Delete>", lambda e: self.delete())

        row = tk.Frame(wrap, bg=BG)
        row.pack(pady=10)
        FlatButton(row, "← BACK", app.show_welcome, "secondary").pack(side="left", padx=6)
        FlatButton(row, "🗑 DELETE SELECTED", self.delete, "danger").pack(side="left", padx=6)
        FlatButton(row, "START STUDENT QUIZ", self.start).pack(side="left", padx=6)

    def refresh(self):
        self.listbox.delete(0, "end")
        for n, item in enumerate(self.questions, 1):
            self.listbox.insert("end", f"{n}. [{item['level']}] {item['q']}")

    def add(self):
        # We check the question and answer, then add them with the chosen difficulty.
        q, a = self.q.get().strip(), self.a.get().strip()
        if not (q and a):
            self.msg.config(text="Please type both a question and a model answer.", fg=RED)
            return
        self.questions.append({"q": q, "a": a, "level": self.level_var.get()})
        saved = save_custom_questions(self.questions)
        self.refresh()
        self.q.delete(0, "end")
        self.a.delete(0, "end")
        if saved:
            self.msg.config(text=f"Question added ({len(self.questions)} total).", fg=GREEN)
        else:
            self.msg.config(text="Question added, but it could not be saved to the file.", fg=RED)

    def delete(self):
        # We remove the selected question from the current list.
        sel = self.listbox.curselection()
        if not sel:
            self.msg.config(text="Click a question in the list first, then press Delete.", fg=RED)
            return
        removed = self.questions.pop(sel[0])
        saved = save_custom_questions(self.questions)
        self.refresh()
        if saved:
            self.msg.config(text=f"Deleted: {removed['q'][:40]}", fg=ORANGE)
        else:
            self.msg.config(text="Deleted, but the change could not be saved to the file.", fg=RED)

    def start(self):
        if not self.questions:
            self.msg.config(text="Add at least one question first.", fg=RED)
            return
        self.app.show_live_quiz(self.questions, self.name.get().strip() or "Student")

class LiveQuizScreen(tk.Frame):
    """We show teacher-created questions and collect written answers."""
    def __init__(self, app, questions, student):
        super().__init__(app, bg=BG)
        self.app, self.questions, self.student = app, questions, student
        self.answers, self.i, self.t0 = [], 0, time.time()
        top_bar(self, f"ICT Quiz Master · {student}")
        wrap = tk.Frame(self, bg=BG)
        wrap.place(relx=0.5, rely=0.5, anchor="center")
        self.head = label(wrap, "", 11, True, MUTED)
        self.head.pack()
        self.qlbl = label(wrap, "", 16, True, wraplength=640, justify="left")
        self.qlbl.pack(pady=10)
        self.box = tk.Text(wrap, width=70, height=7, font=(FONT, 12), relief="solid", bd=1)
        self.box.pack()
        self.btn = FlatButton(wrap, "NEXT →", self.next)
        self.btn.pack(pady=12)
        self.show()

    def show(self):
        item = self.questions[self.i]
        self.head.config(
            text=f"Question {self.i + 1} of {len(self.questions)}   ·   "
                 f"{self.i} answered   ·   Difficulty: {item['level']}",
            fg=LEVEL_COLOR[item["level"]])
        self.qlbl.config(text=item["q"])
        self.box.delete("1.0", "end")
        self.btn.config(text="SUBMIT" if self.i == len(self.questions) - 1 else "NEXT →")

    def next(self):
        # We save this answer and show the next question or the grading screen.
        self.answers.append(self.box.get("1.0", "end").strip())
        self.i += 1
        if self.i >= len(self.questions):
            secs = int(time.time() - self.t0)
            self.app.show_live_result(self.questions, self.answers, self.student, secs)
        else:
            self.show()


class LiveResultScreen(tk.Frame):
    """Teacher grades each answer manually."""

    def __init__(self, app, questions, answers, student, secs):
        super().__init__(app, bg=BG)
        self.questions, self.marks = questions, [None] * len(questions)
        top_bar(self, f"Manual Grading · {student}")
        wrap = tk.Frame(self, bg=BG)
        wrap.pack(pady=12)
        self.score_lbl = label(wrap, "", 16, True)
        self.score_lbl.pack()
        label(wrap, f"Time taken: {fmt_time(secs)}", 10, fg=MUTED).pack()
        self.btns = []
        for i, q in enumerate(questions):
            c = card(wrap, padx=16, pady=8)
            c.pack(fill="x", pady=4)
            label(c, f"Q{i + 1}. [{q['level']}] {q['q']}", 11, True, wraplength=620, justify="left").pack(anchor="w")
            label(c, f"Student: {answers[i] or '(no answer)'}", 10, wraplength=620, justify="left").pack(anchor="w")
            label(c, f"Model answer: {q['a']}", 10, fg="#047857", wraplength=620, justify="left").pack(anchor="w")
            r = tk.Frame(c, bg=WHITE)
            r.pack(anchor="w", pady=4)
            yes = FlatButton(r, "✓ Correct", lambda i=i: self.mark(i, True), "secondary", 10)
            no = FlatButton(r, "✗ Incorrect", lambda i=i: self.mark(i, False), "secondary", 10)
            yes.pack(side="left", padx=4)
            no.pack(side="left", padx=4)
            self.btns.append((yes, no))
        FlatButton(wrap, "HOME", app.show_welcome).pack(pady=8)
        self.update_score()

    def mark(self, i, value):
        # We save the teacher's mark and update the score.
        self.marks[i] = value
        yes, no = self.btns[i]
        yes.config(bg=GREEN if value else WHITE, fg=WHITE if value else NAVY)
        no.config(bg=RED if not value else WHITE, fg=WHITE if not value else NAVY)
        self.update_score()

    def update_score(self):
        # We count graded answers and how many are correct.
        graded = [m for m in self.marks if m is not None]
        good = sum(1 for m in graded if m)
        self.score_lbl.config(text=f"Score: {good}/{len(self.questions)}   ({len(graded)} graded)")