import unittest
from somali_lexicon import detect_somali_terms, vocabulary_prompt, enrich_result


class SomaliLexiconTests(unittest.TestCase):
    def test_prompt_is_somali_lexicon_only(self):
        prompt = vocabulary_prompt()
        self.assertIn("sheeko", prompt)
        self.assertIn("maahmaah", prompt)
        self.assertNotIn("French", prompt)

    def test_detects_somali_terms_case_insensitively(self):
        found = detect_somali_terms("Waxaan maqlay SHEEKO iyo maahmaahyo.")
        self.assertIn("sheeko", found)
        self.assertIn("maahmaah", found)

    def test_enrichment_does_not_rewrite_transcript(self):
        original = "Tani waa sheeko dhaqanka."
        result = {"texte": original, "segments": []}
        enriched = enrich_result(result)
        self.assertEqual(enriched["texte"], original)
        self.assertEqual(enriched["mots_somali"], ["sheeko", "dhaqan"])
        self.assertEqual(enriched["lexique_somali_version"], 1)

    def test_empty_transcript(self):
        self.assertEqual(detect_somali_terms(""), [])


if __name__ == "__main__":
    unittest.main()
