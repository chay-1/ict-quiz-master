import tkinter as tk
from tkinter import messagebox

from core.quiz_data import PASS_MARK, load_results, ranking
from core.quiz_questions import TOPICS
from core.quiz_theme import AMBER, BG, BLUE, FONT, GREEN, GREY, LIGHT, MUTED, NAVY, ORANGE, RED, TIME_LIMIT, WHITE
from desktop.widgets import FlatButton, bind_all, card, label, top_bar


class WelcomeScreen(tk.Frame):
    """We show the home screen and the student's saved progress."""
    def __init__(self, app):
        super().__init__(app, bg=BG)
        results = load_results()
        self.app, self.topic_cards = app, {}
        self.selected_topic = None

        wrap = tk.Frame(self, bg=BG, padx=42, pady=28)
        wrap.pack(fill="both", expand=True)
        wrap.grid_columnconfigure(0, weight=1, uniform="home")
        wrap.grid_columnconfigure(1, weight=1, uniform="home")
        wrap.grid_rowconfigure(0, weight=1)

        left = tk.Frame(wrap, bg=BG)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 30))
        brand = tk.Frame(left, bg=BG)
        brand.pack(anchor="w", pady=(0, 34))
        logo = tk.Canvas(brand, width=66, height=58, bg=BLUE, highlightthickness=0)
        logo.pack(side="left")
        logo.create_rectangle(9, 6, 49, 34, fill=NAVY, outline=WHITE, width=3)
        logo.create_rectangle(14, 11, 44, 29, fill="#bfdbfe", outline=WHITE, width=2)
        logo.create_rectangle(26, 34, 32, 42, fill=WHITE, outline=WHITE)
        logo.create_rectangle(18, 43, 40, 47, fill=WHITE, outline=WHITE)
        logo.create_rectangle(51, 14, 61, 47, fill=NAVY, outline=WHITE, width=2)
        logo.create_line(54, 20, 58, 20, fill="#bfdbfe", width=2)
        logo.create_line(54, 25, 58, 25, fill="#bfdbfe", width=2)
        brand_copy = tk.Frame(brand, bg=BG)
        brand_copy.pack(side="left", padx=12)
        label(brand_copy, "ICT Quiz Master", 17, True).pack(anchor="w")
        label(brand_copy, "Offline Learning Platform", 10, fg="#60a5fa").pack(anchor="w")

        label(left, "Test Your ICT\nKnowledge", 34, True, wraplength=440, justify="left").pack(anchor="w")
        label(left, "Practice ICT topics, receive instant feedback, and\ntrack your performance — all offline.",
              12, fg=MUTED, justify="left").pack(anchor="w", pady=(12, 18))

        feats = tk.Frame(left, bg=BG)
        feats.pack(anchor="w", pady=(0, 18))
        for icon, txt in [("✦", "Multiple Choice"), ("⚡", "Instant Feedback"),
                          ("📊", "Track Performance")]:
            f = tk.Frame(feats, bg=WHITE, padx=10, pady=7,
                         highlightthickness=1, highlightbackground=GREY)
            f.pack(anchor="w", pady=3)
            label(f, f"{icon}  {txt}", 10, True, NAVY, WHITE).pack()

        FlatButton(left, "START QUIZ   →", app.show_topics, "blue", 15).pack(fill="x", pady=(8, 8))
        actions = tk.Frame(left, bg=BG)
        actions.pack(fill="x")
        FlatButton(actions, "👩‍🏫 Teacher Mode", app.show_teacher_setup,
                   "secondary", 10).pack(side="left", fill="x", expand=True, padx=(0, 4))
        FlatButton(actions, "🏆 Leaderboard", app.show_leaderboard,
                   "secondary", 10).pack(side="left", fill="x", expand=True, padx=(4, 0))
        label(left, "No account required · Works fully offline", 9, fg=MUTED).pack(anchor="w", pady=(10, 0))

        panel = card(wrap, padx=18, pady=16)
        panel.grid(row=0, column=1, sticky="nsew")
        panel.grid_columnconfigure(0, weight=1)
        label(panel, "Choose a topic", 17, True, NAVY, WHITE).pack(anchor="w")
        label(panel, "Pick a subject and jump straight in.", 10, fg=MUTED, bg=WHITE).pack(
            anchor="w", pady=(2, 12))
        for topic in TOPICS:
            self._topic_card(panel, topic)
        self.continue_btn = FlatButton(panel, "CONTINUE   →", self.continue_topic, "blue", 12)
        self.continue_btn.pack(fill="x", pady=(12, 0))
        if results:
            self._dashboard(left, results)

        # The prototype highlights Networking by default; every topic remains selectable.
        self.pick_topic(next((topic for topic in TOPICS if topic["id"] == "networking"), TOPICS[0]))

    def _topic_card(self, parent, topic):
        row = tk.Frame(parent, bg=WHITE, highlightthickness=1, highlightbackground=GREY,
                       padx=10, pady=7, cursor="hand2", height=68)
        row.pack(fill="x", pady=4)
        row.pack_propagate(False)
        icon = tk.Label(row, text=topic["icon"], bg=LIGHT, fg=NAVY, font=(FONT, 16), width=3)
        icon.pack(side="left", padx=(0, 10))
        copy = tk.Frame(row, bg=WHITE)
        copy.pack(side="left", fill="both", expand=True)
        label(copy, topic["name"], 11, True, NAVY, WHITE).pack(anchor="w")
        label(copy, topic["desc"], 9, fg=MUTED, bg=WHITE, wraplength=290,
              justify="left").pack(anchor="w")
        level_color = {"Easy": GREEN, "Medium": AMBER, "Hard": RED}[topic["level"]]
        label(row, topic["level"], 9, True, level_color, WHITE).pack(side="right", padx=(4, 0))
        bind_all(row, "<Button-1>", lambda event, selected=topic: self.pick_topic(selected))
        row.bind("<Enter>", lambda event, selected=topic: self._hover_topic(selected, True))
        row.bind("<Leave>", lambda event, selected=topic: self._hover_topic(selected, False))
        self.topic_cards[topic["id"]] = row

    def _paint_topic(self, topic, selected=False, hover=False):
        row = self.topic_cards[topic["id"]]
        color = LIGHT if selected or hover else WHITE
        border = BLUE if selected else "#55708f" if hover else GREY
        row.config(bg=color, highlightbackground=border, highlightthickness=2 if selected else 1)
        for child in row.winfo_children():
            child.config(bg=color)
            for nested in child.winfo_children():
                nested.config(bg=color)

    def _hover_topic(self, topic, hovering):
        if self.selected_topic != topic:
            self._paint_topic(topic, hover=hovering)

    def pick_topic(self, topic):
        if self.selected_topic:
            self._paint_topic(self.selected_topic)
        self.selected_topic = topic
        self._paint_topic(topic, selected=True)

    def continue_topic(self):
        if self.selected_topic:
            self.app.show_setup(self.selected_topic)

    def _dashboard(self, parent, results):
        last = results[-1]
        board = ranking()
        names = [e["name"].strip().lower() for e in board]
        rank = names.index(last["name"].strip().lower()) + 1
        mine = [e for e in results if e["name"].strip().lower() == last["name"].strip().lower()]
        box = card(parent, padx=20, pady=12)
        box.pack(fill="x", pady=6)
        label(box, f"YOUR QUIZ PROGRESS · {last['name']}", 10, True, MUTED).pack(anchor="w")
        row = tk.Frame(box, bg=WHITE)
        row.pack(pady=6)
        stats = [("🔥 Last Streak", last.get("endStreak", 0)),
                 ("🏆 Best Streak", max(e["bestStreak"] for e in mine)),
                 ("⭐ Best Score", max(e["finalScore"] for e in mine)),
                 ("🥇 Class Rank", f"#{rank}")]
        for t, v in stats:
            cell = tk.Frame(row, bg=WHITE, padx=14)
            cell.pack(side="left")
            label(cell, str(v), 20, True).pack()
            label(cell, t, 9, fg=MUTED).pack()
        label(box, "Can you beat your best streak?", 10, True, ORANGE).pack()


# ───────────────────────── Screen 2: Topic selection ─────────────────────────
class TopicScreen(tk.Frame):
    """We let the student choose a quiz topic."""
    def __init__(self, app):
        super().__init__(app, bg=BG)
        self.app, self.selected, self.cards = app, None, {}
        top_bar(self)
        label(self, "Choose Your Topic", 24, True).pack(pady=(24, 0))
        label(self, "Select an ICT topic to begin.", 12, fg=MUTED).pack(pady=(0, 14))

        grid = tk.Frame(self, bg=BG)
        grid.pack()
        lvl_col = {"Easy": GREEN, "Medium": AMBER, "Hard": RED}
        for i, t in enumerate(TOPICS):
            c = tk.Frame(grid, bg=WHITE, highlightthickness=2, highlightbackground=GREY,
                         padx=20, pady=16, cursor="hand2", width=380, height=170)
            c.grid(row=i // 2, column=i % 2, padx=10, pady=10)
            c.pack_propagate(False)
            label(c, t["icon"], 28).pack(anchor="w")
            label(c, t["name"], 15, True).pack(anchor="w")
            label(c, t["desc"], 10, fg=MUTED, wraplength=330, justify="left").pack(anchor="w")
            meta = tk.Frame(c, bg=WHITE)
            meta.pack(anchor="w", pady=(8, 0))
            label(meta, "10 Questions", 10, True, NAVY).pack(side="left")
            label(meta, f"  ●  {t['level']}", 10, True, lvl_col[t["level"]]).pack(side="left")
            bind_all(c, "<Button-1>", lambda e, t=t: self.pick(t))
            c.bind("<Enter>", lambda e, t=t: self.hover(t, True))
            c.bind("<Leave>", lambda e, t=t: self.hover(t, False))
            self.cards[t["id"]] = c

        nav = tk.Frame(self, bg=BG)
        nav.pack(pady=10)
        FlatButton(nav, "← BACK", app.show_welcome, "secondary").pack(side="left", padx=6)
        self.cont = FlatButton(nav, "CONTINUE →", self.go)
        self.cont.pack(side="left", padx=6)
        self.cont.set_enabled(False)

    def _paint(self, tid, bg, border):
        c = self.cards[tid]
        c.config(bg=bg, highlightbackground=border)
        for w in c.winfo_children():
            w.config(bg=bg)
            for x in w.winfo_children():
                x.config(bg=bg)

    def hover(self, t, on):
        if self.selected and self.selected["id"] == t["id"]:
            return
        self._paint(t["id"], LIGHT if on else WHITE, "#93c5fd" if on else GREY)

    def pick(self, t):
        if self.selected:
            self._paint(self.selected["id"], WHITE, GREY)
        self.selected = t
        self._paint(t["id"], LIGHT, BLUE)
        self.cont.set_enabled(True)

    def go(self):
        if self.selected:
            self.app.show_setup(self.selected)


# ───────────────────────── Screen 3: Quiz setup ─────────────────────────
class SetupScreen(tk.Frame):
    """We show the rules and check the student's name before starting."""
    def __init__(self, app, topic):
        super().__init__(app, bg=BG)
        self.app, self.topic = app, topic
        top_bar(self)
        wrap = tk.Frame(self, bg=BG)
        wrap.place(relx=0.5, rely=0.55, anchor="center")
        label(wrap, "Quiz Setup", 24, True).pack()
        label(wrap, f"{topic['icon']}  {topic['name']}", 16, True, BLUE).pack(pady=6)

        info = card(wrap, padx=24, pady=12)
        info.pack(fill="x", pady=6)
        for k, v in [("Difficulty", topic["level"]), ("Questions", "10"), ("Estimated Time", "5–10 minutes")]:
            r = tk.Frame(info, bg=WHITE)
            r.pack(fill="x", pady=2)
            label(r, k, 11, fg=MUTED).pack(side="left")
            label(r, v, 11, True).pack(side="right")
        label(wrap, "Answer each question carefully. You will receive feedback after every answer.",
              10, fg=MUTED).pack(pady=4)

        rules = tk.Frame(wrap, bg="#fffbeb", highlightthickness=1, highlightbackground="#fde68a", padx=20, pady=10)
        rules.pack(fill="x", pady=6)
        label(rules, f"SCORING RULES · PASS MARK: {PASS_MARK}/10", 10, True, "#92400e").pack(anchor="w")
        for line in ["🔥 Correct answers build your streak.",
                     "⭐ Streaks can earn bonus points (3, 5, 7 and 10 in a row).",
                     "📉 Below 6 correct answers results in a score penalty.",
                     "🏆 Higher scores move you up the leaderboard.",
                     f"⏳ You have {TIME_LIMIT} seconds per question.  🎯 One 50/50 lifeline per quiz.",
                     "⌨ Keys: A–D choose · Enter check / continue · F use 50/50"]:
            label(rules, line, 10, fg="#78350f").pack(anchor="w")

        row = tk.Frame(wrap, bg=BG)
        row.pack(pady=6)
        label(row, "Your name:", 11, True).pack(side="left", padx=(0, 8))
        self.name = tk.Entry(row, font=(FONT, 12), width=22, relief="solid", bd=1)
        self.name.pack(side="left")
        self.name.focus_set()

        nav = tk.Frame(wrap, bg=BG)
        nav.pack(pady=10)
        FlatButton(nav, "← BACK", app.show_topics, "secondary").pack(side="left", padx=6)
        FlatButton(nav, "START QUIZ", self.start).pack(side="left", padx=6)
        self.name.bind("<Return>", lambda e: self.start())

    def start(self):
        student_name = self.name.get().strip()
        if not student_name:
            messagebox.showwarning(
                "Name required",
                "Please enter your name before starting the quiz.",
                parent=self
            )
            self.name.focus_set()
            return
        if len(student_name) < 2:
            messagebox.showwarning(
                "Name too short",
                "Please enter a name with at least 2 characters.",
                parent=self
            )
            self.name.focus_set()
            return
        self.app.student = student_name
        self.app.show_quiz(self.topic)


# ───────────────────────── Screens 4-8: Quiz ─────────────────────────
