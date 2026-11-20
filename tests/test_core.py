"""Simple automatic tests for the quiz rules (no window is opened).

Run:  python -m unittest discover tests
"""
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import quiz_custom, quiz_data
from core.quiz_data import (
    PASS_MARK, STREAK_BONUS, final_score, fmt_time, penalty_for, ranking, save_result,
)
from core.quiz_questions import TOPICS, prepare


def result(name, topic, final, best=3, correct=8, secs=60):
    """A small result record like the one the quiz saves after question 10."""
    return {"name": name, "topic": topic, "finalScore": final, "bestStreak": best,
            "correct": correct, "total": 10, "timeSecs": secs}


class QuestionTests(unittest.TestCase):
    def test_four_topics_with_ten_questions_each(self):
        self.assertEqual(len(TOPICS), 4)
        for topic in TOPICS:
            self.assertEqual(len(prepare(topic["id"])), 10)

    def test_every_question_has_four_options_and_a_valid_answer(self):
        for topic in TOPICS:
            for q in prepare(topic["id"]):
                letters = [letter for letter, _ in q["options"]]
                self.assertEqual(letters, ["A", "B", "C", "D"])
                self.assertIn(q["answer"], letters)
                self.assertTrue(q["why"])


    def test_shuffling_keeps_the_correct_answer(self):
        # the right answer text must stay the same after the options are shuffled
        from core.quiz_questions import BANK
        for topic in TOPICS:
            original = {q["text"]: dict(q["options"])[q["answer"]] for q in BANK[topic["id"]]}
            for q in prepare(topic["id"]):
                self.assertEqual(dict(q["options"])[q["answer"]], original[q["text"]])


class ScoringTests(unittest.TestCase):
    def test_streak_bonus_values(self):
        self.assertEqual(STREAK_BONUS, {3: 5, 5: 10, 7: 15, 10: 25})

    def test_no_penalty_at_or_above_pass_mark(self):
        self.assertEqual(PASS_MARK, 6)
        self.assertEqual(penalty_for(6), 0)
        self.assertEqual(penalty_for(10), 0)

    def test_penalty_below_pass_mark(self):
        self.assertEqual(penalty_for(5), 10)
        self.assertEqual(penalty_for(2), 40)

    def test_perfect_score(self):
        # 10 correct = 100 points; streak bonuses 5 + 10 + 15 + 25 = 55
        self.assertEqual(final_score(100, 55, 10), 155)

    def test_score_never_below_zero(self):
        self.assertEqual(final_score(0, 0, 0), 0)

    def test_time_format(self):
        self.assertEqual(fmt_time(65), "01:05")


class ResultsTests(unittest.TestCase):
    def setUp(self):
        # save results in a temporary file so the real data folder is not touched
        self.folder = tempfile.TemporaryDirectory()
        quiz_data.DATA_DIR = self.folder.name
        quiz_data.DATA_FILE = os.path.join(self.folder.name, "quiz_results.json")

    def tearDown(self):
        self.folder.cleanup()

    def test_missing_file_gives_empty_list(self):
        self.assertEqual(quiz_data.load_results(), [])

    def test_leaderboard_is_sorted_by_score(self):
        save_result(result("Ben", "Networking", 80))
        save_result(result("Ann", "Networking", 155))
        self.assertEqual([e["name"] for e in ranking()], ["Ann", "Ben"])

    def test_leaderboard_keeps_best_attempt_per_student(self):
        save_result(result("Ann", "Networking", 50))
        save_result(result("ann", "Networking", 120))
        board = ranking()
        self.assertEqual(len(board), 1)
        self.assertEqual(board[0]["finalScore"], 120)

    def test_leaderboard_can_filter_by_topic(self):
        save_result(result("Ann", "Networking", 100))
        save_result(result("Ben", "Database", 90))
        self.assertEqual([e["name"] for e in ranking("Database")], ["Ben"])


class TeacherQuestionTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        quiz_custom.DATA_DIR = self.folder.name
        quiz_custom.QUESTIONS_FILE = os.path.join(self.folder.name, "teacher_questions.json")

    def tearDown(self):
        self.folder.cleanup()

    def test_missing_file_gives_empty_list(self):
        self.assertEqual(quiz_custom.load_custom_questions(), [])

    def test_save_and_load_questions(self):
        questions = [{"q": "What is a CPU?", "a": "The brain of the computer", "level": "Easy"}]
        self.assertTrue(quiz_custom.save_custom_questions(questions))
        self.assertEqual(quiz_custom.load_custom_questions(), questions)

    def test_incomplete_questions_are_ignored(self):
        quiz_custom.save_custom_questions([{"q": "Only a question"},
                                           {"q": "Good", "a": "Yes", "level": "Hard"},
                                           {"q": "Bad level", "a": "x", "level": "Impossible"}])
        self.assertEqual(len(quiz_custom.load_custom_questions()), 1)


if __name__ == "__main__":
    unittest.main()
