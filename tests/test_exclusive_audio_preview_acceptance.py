import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUST = ROOT / "ui" / "src-tauri" / "src" / "lib.rs"


class ExclusiveAudioPreviewAcceptanceTests(unittest.TestCase):
    def test_playback_state_represents_one_global_preview(self):
        source = RUST.read_text(encoding="utf-8")
        self.assertNotIn("HashMap<String, Child>", source)
        self.assertIn("Option<(String, Child)>", source)

    def test_starting_preview_stops_previous_preview(self):
        source = RUST.read_text(encoding="utf-8")
        play = source[source.index("fn play_unit_audio"):source.index("fn stop_unit_audio")]
        self.assertIn("players.take()", play)
        self.assertIn("previous.kill()", play)
        self.assertIn("previous.wait()", play)


if __name__ == "__main__":
    unittest.main()
