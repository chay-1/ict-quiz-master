import time
from datetime import date

import tkinter as tk

from quiz_data import final_score, penalty_for, save_result
from screens_home import SetupScreen, TopicScreen, WelcomeScreen
from screens_leaderboard import LeaderboardScreen
from screens_quiz import PerformanceScreen, QuizScreen, ResultScreen, ReviewScreen
from screens_teacher import LiveQuizScreen, LiveResultScreen, TeacherSetupScreen
from quiz_theme import BG


class App(tk.Tk):
    """We use this class to create the window and move between screens."""

    def __init__(self):
        super().__init__()
        self.title("ICT Quiz Master")
        self.geometry("1100x780")
        self.minsize(960, 700)
        self.configure(bg=BG)
        self.student = "Student"
        self.sound_enabled = True
        self.current = None
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
