"""Simple automatic tests for the shared quiz logic.   Run:  python -m unittest discover tests"""
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import quiz_core as core, quiz_data
from web.web_game_assets import certificate_pdf


def play(topic, correct_answers):
    """Play a whole quiz, answering the first `correct_answers` questions correctly."""
    state = core.new_quiz(topic)
    while not core.is_finished(state):
        q = state["questions"][state["index"]]
        right = state["index"] < correct_answers
        choice = q["answer"] if right else next(l for l, _ in q["options"] if l != q["answer"])
        core.check_answer(state, choice)
        state["index"] += 1
    return state


class QuizTests(unittest.TestCase):
    def setUp(self):
        # save results in a temporary file so the real data folder is not touched
        self.folder = tempfile.TemporaryDirectory()
        quiz_data.DATA_DIR = self.folder.name
        quiz_data.DATA_FILE = os.path.join(self.folder.name, "quiz_results.json")

    def tearDown(self):
        self.folder.cleanup()

    def test_each_topic_has_ten_questions(self):
        for name in core.TOPIC_BY_NAME:
            self.assertEqual(len(core.new_quiz(name)["questions"]), 10)

    def test_perfect_score(self):
        result = core.finish_quiz(play("Networking", 10), "Test")
        self.assertEqual(result["correct"], 10)
        self.assertEqual(result["finalScore"], 155)      # 100 points + 55 streak bonus

    def test_all_wrong_score_is_zero(self):
        result = core.finish_quiz(play("Database", 0), "Test")
        self.assertEqual(result["finalScore"], 0)         # score never goes below zero

    def test_result_is_saved_and_ranked(self):
        core.finish_quiz(play("Networking", 10), "Ann")
        core.finish_quiz(play("Networking", 7), "Ben")
        self.assertEqual([e["name"] for e in quiz_data.ranking()][0], "Ann")

    def test_certificate_is_a_pdf(self):
        result = core.finish_quiz(play("Cybersecurity", 8), "Karma Dema")
        self.assertTrue(certificate_pdf(result).startswith(b"%PDF"))


if __name__ == "__main__":
    unittest.main()
