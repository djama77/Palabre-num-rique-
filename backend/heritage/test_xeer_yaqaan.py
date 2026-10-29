import tempfile
import unittest
from pathlib import Path

from xeer_yaqaan import load_passages, search_evidence


class XeerYaqaanTests(unittest.TestCase):
    def test_retrieves_page_and_text(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / "ocr.txt"
            source.write_text(
                "[[PAGE 7]]\nXeer-Ciise iyo nabad waa muhiim.\n\n"
                "[[PAGE 8]]\nMag waxaa lagu xalliyaa arrimo gaar ah.\n",
                encoding="utf-8",
            )
            result = search_evidence("xeer nabad", source)
            self.assertTrue(result["found"])
            self.assertEqual(result["sources"][0]["page"], 7)
            self.assertIn("nabad", result["sources"][0]["text"])

    def test_missing_page_markers_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / "ocr.txt"
            source.write_text("Plain text without page markers", encoding="utf-8")
            with self.assertRaises(ValueError):
                load_passages(source)

    def test_no_match_does_not_invent_answer(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / "ocr.txt"
            source.write_text("[[PAGE 1]]\nQoraal kale oo tijaabo ah.\n", encoding="utf-8")
            result = search_evidence("nebula spaceship", source)
            self.assertFalse(result["found"])
            self.assertEqual(result["sources"], [])


if __name__ == "__main__":
    unittest.main()
