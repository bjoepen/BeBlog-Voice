import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class PlaybackCompletionAcceptanceTests(unittest.TestCase):
    def read(self, relative_path: str) -> str:
        return (ROOT / relative_path).read_text(encoding="utf-8")

    def test_tauri_exposes_playback_state_query(self):
        source = self.read("ui/src-tauri/src/lib.rs")
        self.assertIn("fn is_unit_audio_playing", source)
        self.assertIn("is_unit_audio_playing,", source)
        self.assertIn("try_wait()", source)

    def test_frontend_bridge_exposes_playback_state_query(self):
        source = self.read("ui/src/lib/projectBridge.js")
        self.assertIn('invoke("is_unit_audio_playing"', source)
        self.assertIn("isUnitAudioPlaying", source)

    def test_svelte_reconciles_natural_playback_completion(self):
        source = self.read("ui/src/App.svelte")
        self.assertIn("projectBridge.isUnitAudioPlaying", source)
        self.assertIn("playingUnitId = null", source)
        self.assertIn("setTimeout", source)
        self.assertNotIn("audio.duration", source)
        self.assertNotIn("wavDuration", source)


if __name__ == "__main__":
    unittest.main()
