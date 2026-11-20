"""Tests for the certificate (no window is opened).  Run:  python -m unittest discover tests"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.certificate import build_html, certificate_info, file_name


def entry(correct, name="Sangay"):
    return {"name": name, "topic": "Networking", "correct": correct, "total": 10,
            "finalScore": 80, "bestStreak": 3, "date": "2026-11-20"}


class CertificateTests(unittest.TestCase):
    def test_pass_gets_achievement(self):
        self.assertEqual(certificate_info(entry(7))["sub"], "OF ACHIEVEMENT")

    def test_not_passed_still_gets_participation_certificate(self):
        self.assertEqual(certificate_info(entry(2))["sub"], "OF PARTICIPATION")

    def test_name_is_escaped_in_html(self):
        page = build_html(entry(7, "<script>x</script>"))
        self.assertNotIn("<script>x", page)
        self.assertIn("&lt;script&gt;", page)

    def test_file_name_is_safe(self):
        self.assertEqual(file_name(entry(7, "Sangay D/Tenzin")), "Certificate_Sangay_D_Tenzin_Networking.html")

    def test_page_is_landscape(self):
        self.assertIn("A4 landscape", build_html(entry(7)))


if __name__ == "__main__":
    unittest.main()
