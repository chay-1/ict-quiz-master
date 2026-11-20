"""Main window: creates the Tkinter window and moves between screens."""
import time
import tkinter as tk
from datetime import date

from core.quiz_data import final_score, penalty_for, save_result
from core.quiz_theme import BG
from desktop.screens_certificate import CertificateScreen
from desktop.screens_home import SetupScreen, TopicScreen, WelcomeScreen
from desktop.screens_leaderboard import LeaderboardScreen
from desktop.screens_quiz import PerformanceScreen, QuizScreen, ResultScreen, ReviewScreen
from desktop.screens_teacher import LiveQuizScreen, LiveResultScreen, TeacherSetupScreen


class App(tk.Tk):
    """We use this class to create the window and move between screens."""

    def __init__(self):
        super().__init__()
        self.title("ICT Quiz Master")
        w = min(1100, self.winfo_screenwidth() - 40)          # fit small laptop screens
        h = min(780, self.winfo_screenheight() - 90)          # leave room for the taskbar
        self.geometry(f"{w}x{h}+{max(0, (self.winfo_screenwidth() - w) // 2)}+10")
        self.minsize(900, 580)
        self.configure(bg=BG)
        self.student = "Student"        # name typed on the setup screen
        self.sound_enabled = True       # changed by the sound button
        self.current = None             # the screen that is showing now
        self.show_welcome()

    def swap(self, cls, *args):
        # We close the current screen and show the next screen.
        if self.current is not None:
            self.current.destroy()
        self.current = cls(self, *args)
        self.current.pack(fill="both", expand=True)

    def show_welcome(self): self.swap(WelcomeScreen)
    def show_topics(self): self.swap(TopicScreen)
    def show_setup(self, topic): self.swap(SetupScreen, topic)
    def show_quiz(self, topic): self.swap(QuizScreen, topic)
    def show_leaderboard(self): self.swap(LeaderboardScreen)
    def show_teacher_setup(self): self.swap(TeacherSetupScreen)
    def show_live_quiz(self, qs, name): self.swap(LiveQuizScreen, qs, name)
    def show_live_result(self, qs, ans, name, secs): self.swap(LiveResultScreen, qs, ans, name, secs)

    def show_review(self, topic, r, entry):
        self.swap(ReviewScreen, topic, r, entry)

    def show_certificate(self, topic, r, entry):
        self.swap(CertificateScreen, topic, r, entry)

    def show_performance(self, topic, r, entry):
        self.swap(PerformanceScreen, topic, r, entry)

    def finish_quiz(self, topic, r):
        # We calculate the final score, save the result, and show it on screen.
        penalty = penalty_for(r["correct"])
        entry = {
            "id": str(time.time()), "name": self.student, "topic": topic["name"],
            "correct": r["correct"], "total": 10, "points": r["points"],
            "streakBonus": r["bonus"], "penalty": penalty,
            "finalScore": final_score(r["points"], r["bonus"], r["correct"]),
            "bestStreak": r["best"], "endStreak": r["endStreak"],
            "timeSecs": r["secs"], "date": date.today().isoformat(),
        }
        save_result(entry)
        self.swap(ResultScreen, topic, r, entry)


if __name__ == "__main__":
    App().mainloop()
