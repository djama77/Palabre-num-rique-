import io
import unittest
from unittest.mock import Mock, patch
from local_narration import narration_get

class NarrationTests(unittest.TestCase):
    def handler(self, record):
        h=Mock()
        h.path="/api/local/ecouter/r1"
        h.client_address=("127.0.0.1",1234)
        h.server.server_port=8765
        h.headers={"Host":"127.0.0.1:8765"}
        h.store.get_public.return_value=record
        h.wfile=io.BytesIO()
        return h

    def test_private_record_never_sent(self):
        h=self.handler(None)
        with patch("local_narration.synthesize_validated_text") as speak:
            self.assertTrue(narration_get(h))
            h.send_error.assert_called_with(404,"Traduction publique introuvable")
            speak.assert_not_called()

    def test_published_translation_narrated(self):
        h=self.handler({"translation_fr":"Un récit autorisé"})
        with patch.dict("os.environ",{"ELEVENLABS_VOICE_ID":"voice123"}):
            with patch("local_narration.synthesize_validated_text",return_value=b"mp3") as speak:
                self.assertTrue(narration_get(h))
                speak.assert_called_once_with("Un récit autorisé",voice_id="voice123",approved=True)
                h.send_response.assert_called_with(200)
                self.assertEqual(h.wfile.getvalue(),b"mp3")

    def test_no_voice_configured(self):
        h=self.handler({"translation_fr":"Texte"})
        with patch.dict("os.environ",{},clear=True):
            self.assertTrue(narration_get(h))
            h.send_error.assert_called_with(503,"Voix non configurée")

if __name__=="__main__":
    unittest.main()
