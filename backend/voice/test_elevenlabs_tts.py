import os
import unittest
from unittest.mock import patch
from elevenlabs_tts import synthesize_validated_text, VoiceConfigurationError

class VoiceTests(unittest.TestCase):
    def test_reject_unvalidated(self):
        with self.assertRaises(PermissionError):
            synthesize_validated_text("Bonjour", voice_id="demo", approved=False)
    def test_reject_empty(self):
        with self.assertRaises(ValueError):
            synthesize_validated_text("", voice_id="demo", approved=True)
    def test_reject_long_text(self):
        with self.assertRaises(ValueError):
            synthesize_validated_text("a"*1201, voice_id="demo", approved=True)
    def test_missing_key(self):
        with patch.dict(os.environ, {"ELEVENLABS_API_KEY": ""}):
            with self.assertRaises(VoiceConfigurationError):
                synthesize_validated_text("Bonjour", voice_id="demo", approved=True)

if __name__ == "__main__":
    unittest.main()
