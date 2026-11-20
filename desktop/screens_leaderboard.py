import tkinter as tk

from core.quiz_data import fmt_time, load_results, ranking
from core.quiz_questions import TOPICS
from core.quiz_theme import BG, GREY, INK, MUTED, ORANGE, ORANGE_LIGHT, PINK, WHITE
from core.quiz_theme import (BORDER, SURFACE, SURFACE_2, INK_ON_LIME, LIME, LIME_DARK, TEAL,
                             TEAL_SOFT, TEAL_EDGE, RED_SOFT, RED_EDGE, PURPLE, PURPLE_SOFT)
from desktop.widgets import FlatButton, bind_all, card, chip_group, label, top_bar


class LeaderboardScreen(tk.Frame):
    """1st place at the top, 2nd below it, 3rd below that, and so on.
    Interactive: filter by topic, change the ranking (score / streak / speed),
    click any student to open their details, show top 10 or everyone."""
    PODIUM = {1: ("🥇", "#3a3210", "#eab308"),      # medal, background, border/bar colour
              2: ("🥈", "#262a35", "#94a3b8"),
              3: ("🥉", "#33200f", "#ea580c")}

    def __init__(self, app):
        super().__init__(app, bg=BG)
        self.app, self._jobs, self._shine_job, self.show_all = app, [], None, False
        self.topic_var, self.sort_var = tk.StringVar(value="all"), tk.StringVar(value="score")
        top_bar(self)
        label(self, "🏆 ICT QUIZ LEADERBOARD", 22, True).pack(pady=(14, 0))
        label(self, "Click a student to see their details. Can you reach the top?",
              10, fg=MUTED).pack(pady=(2, 6))

        row = tk.Frame(self, bg=BG)
        row.pack()
        label(row, "Topic:", 10, True, MUTED).pack(side="left", padx=(0, 4))
        chip_group(row, [("all", "All")] + [(t["name"], t["name"]) for t in TOPICS], self.topic_var, 9, self.refresh)
        row2 = tk.Frame(self, bg=BG)
        row2.pack(pady=(4, 0))
        label(row2, "Rank by:", 10, True, MUTED).pack(side="left", padx=(0, 4))
        chip_group(row2, [("score", "⭐ Score"), ("streak", "🔥 Best streak"), ("speed", "⚡ Correct & fastest")],
                   self.sort_var, 9, self.refresh)

        self.tip = label(self, "", 11, True, ORANGE)
        self.tip.pack(pady=(6, 0))

        nav = tk.Frame(self, bg=BG)                       # packed first so it is never pushed off-screen
        nav.pack(side="bottom", pady=8)
        FlatButton(nav, "← BACK TO HOME", app.show_welcome, "secondary", 11).pack(side="left", padx=6)
        self.more_btn = FlatButton(nav, "SHOW ALL", self.toggle_all, "secondary", 11)
        self.more_btn.pack(side="left", padx=6)

        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True, pady=(6, 0))
        board_area = tk.Frame(body, bg=BG, width=810)
        board_area.pack(anchor="center", fill="y", expand=True)
        board_area.pack_propagate(False)
        self.canvas = tk.Canvas(board_area, bg=BG, highlightthickness=0)
        bar = tk.Scrollbar(board_area, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=bar.set)
        bar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.inner = tk.Frame(self.canvas, bg=BG)
        self.win = self.canvas.create_window((0, 0), window=self.inner, anchor="n")
        self.inner.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", self._resize)
        self.bind_all("<MouseWheel>", lambda e: self.canvas.yview_scroll(-1 if e.delta > 0 else 1, "units"))
        self.refresh()

    def _resize(self, e):
        width = max(1, min(e.width - 30, 780))
        self.canvas.itemconfig(self.win, width=width)
        self.canvas.coords(self.win, e.width / 2, 0)

    def _later(self, ms, fn, *args):
        self._jobs.append(self.after(ms, lambda: fn(*args)))

    def _cancel_jobs(self):
        for j in self._jobs + [self._shine_job]:
            if j:
                try:
                    self.after_cancel(j)
                except Exception:
                    pass
        self._jobs, self._shine_job = [], None

    def toggle_all(self):
        self.show_all = not self.show_all
        self.refresh()

    # ----- build the list -----
    def refresh(self):
        self._cancel_jobs()
        for w in self.inner.winfo_children():
            w.destroy()
        topic = None if self.topic_var.get() == "all" else self.topic_var.get()
        sort = self.sort_var.get()
        board = ranking(topic, sort)
        shown = board if self.show_all else board[:10]
        self.more_btn.config(text="SHOW TOP 10" if self.show_all else f"SHOW ALL ({len(board)})")
        self.more_btn.set_enabled(len(board) > 10)
        self._paint_tip(board, topic, sort)
        self.canvas.yview_moveto(0)

        if not shown:
            box = card(self.inner, padx=20, pady=24)
            box.pack(fill="x", pady=20, padx=6)
            label(box, "No results yet. Complete a quiz to appear here!", 12, fg=MUTED).pack()
            return
        top = max(self._metric(e, sort)[0] for e in shown) or 1
        for i, e in enumerate(shown, 1):               # rows appear one after another, 1st place first
            self._later(120 * (i - 1), self._add_row, i, e, sort, top)

    def _paint_tip(self, board, topic, sort):
        results = load_results()
        if not results:
            self.tip.config(text="")
            return
        me = results[-1]["name"].strip().lower()
        names = [e["name"].strip().lower() for e in board]
        if me not in names:
            self.tip.config(text=f"{results[-1]['name']}, you have no result in this topic yet.")
        elif names.index(me) == 0:
            self.tip.config(text=f"👑 {results[-1]['name']}, you are in 1st place!")
        else:
            k = names.index(me)
            gap = self._metric(board[k - 1], sort)[0] - self._metric(board[k], sort)[0]
            unit = {"score": "points", "streak": "streak", "speed": "correct answer(s)"}[sort]
            self.tip.config(text=f"{results[-1]['name']}, you are #{k + 1}. Only {gap} {unit} to reach #{k}!"
                            if gap > 0 else f"{results[-1]['name']}, you are #{k + 1}. Beat the time to climb!")

    @staticmethod
    def _metric(e, sort):
        """(number used for ranking & the bar, function that writes it as text)"""
        if sort == "streak":
            return e["bestStreak"], lambda v: f"🔥 {v}"
        if sort == "speed":
            return e.get("correct", 0), lambda v: f"✓ {v}/10   ⏱ {fmt_time(e.get('timeSecs', 0))}"
        return e["finalScore"], lambda v: f"⭐ {v}"

    def _add_row(self, i, e, sort, top):
        medal, bg, edge = self.PODIUM.get(i, ("", SURFACE, BORDER))
        first, podium = i == 1, i <= 3
        mine = bool(load_results()) and e["name"].strip().lower() == load_results()[-1]["name"].strip().lower()
        row = tk.Frame(self.inner, bg=bg, highlightthickness=3 if podium else 2, highlightbackground=edge,
                       cursor="hand2", padx=18, pady=14 if first else 9)
        row.pack(fill="x", pady=4, padx=6)
        head = tk.Frame(row, bg=bg)
        head.pack(fill="x")
        label(head, medal or f"#{i}", 26 if first else 18 if podium else 13, True, INK, bg, width=4).pack(side="left")
        label(head, e["name"], 18 if first else 14 if podium else 12, True, INK, bg).pack(side="left", padx=6)
        if mine:
            label(head, " YOU ", 9, True, WHITE, PINK).pack(side="left", padx=6)
        value, fmt = self._metric(e, sort)
        main = label(head, fmt(0), 20 if first else 14 if podium else 12, True, INK, bg)
        main.pack(side="right")
        side = f"🔥 {e['bestStreak']}" if sort == "score" else f"⭐ {e['finalScore']}"
        label(head, side, 11, True, ORANGE, bg).pack(side="right", padx=16)

        trough = tk.Frame(row, bg=GREY, height=6)
        trough.pack(fill="x", pady=(8, 0))
        fill = tk.Frame(trough, bg=edge if podium else PINK)
        fill.place(relx=0, rely=0, relheight=1, relwidth=0)

        detail = tk.Frame(row, bg=bg)
        info = (f"{e['topic']}   ·   ✓ {e.get('correct', '?')}/{e.get('total', 10)} correct   ·   "
                f"⚡ +{e.get('streakBonus', 0)} bonus   ·   📉 −{e.get('penalty', 0)}   ·   "
                f"⏱ {fmt_time(e.get('timeSecs', 0))}   ·   📅 {e.get('date', '')}")
        label(detail, info, 10, fg=INK if podium else MUTED,
              bg=bg, wraplength=700, justify="left").pack(anchor="w")

        def toggle(_e=None):
            if detail.winfo_ismapped():
                detail.pack_forget()
            else:
                detail.pack(fill="x", pady=(8, 0))
        bind_all(row, "<Button-1>", toggle)

        self._count(main, fill, value, fmt, value / top)
        if first:
            self._shine(row)

    def _count(self, lbl, bar, value, fmt, frac, step=0, steps=18):
        """Numbers count up and the bar grows (a short animation)."""
        try:
            lbl.config(text=fmt(round(value * step / steps)))
            bar.place_configure(relwidth=frac * step / steps)
            if step < steps:
                self._later(28, self._count, lbl, bar, value, fmt, frac, step + 1, steps)
        except tk.TclError:
            pass

    def _shine(self, row, on=True):
        """The 1st-place card glows."""
        try:
            row.config(highlightbackground="#facc15" if on else "#ca8a04")
            self._shine_job = self.after(550, lambda: self._shine(row, not on))
        except tk.TclError:
            pass

    def destroy(self):
        self._cancel_jobs()
        try:
            self.unbind_all("<MouseWheel>")
        except Exception:
            pass
        super().destroy()

