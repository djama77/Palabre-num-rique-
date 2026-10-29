import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from evaluate_somali_asr import normalize, edit_distance, error_rate


class EvaluateSomaliASRTests(unittest.TestCase):
    def test_normalize_ignores_case_and_punctuation(self):
        self.assertEqual(normalize("SHEEKO, dhaqanka!"), ["sheeko", "dhaqanka"])

    def test_edit_distance(self):
        self.assertEqual(edit_distance(["a", "b", "c"], ["a", "c"]), 1)

    def test_wer_identical(self):
        self.assertEqual(error_rate("Tani waa sheeko.", "tani waa sheeko"), 0.0)

    def test_cer(self):
        self.assertGreater(error_rate("sheeko", "sheekooyin", characters=True), 0.0)

    def test_empty_reference_rejected(self):
        with self.assertRaises(ValueError):
            error_rate("", "wax")


if __name__ == "__main__":
    unittest.main()
