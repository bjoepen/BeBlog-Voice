import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class DesktopAudioPlaybackAcceptanceTests(unittest.TestCase):
    def read(self, relative_path: str) -> str:
        return (ROOT / relative_path).read_text(encoding="utf-8")

    def test_frontend_bridge_exposes_audio_playback_commands(self):
        source = self.read("ui/src/lib/projectBridge.js")
        self.assertIn('invoke("play_unit_audio"', source)
        self.assertIn('invoke("stop_unit_audio"', source)
        self.assertIn("unitId", source)

    def test_tauri_owns_system_playback_without_domain_logic(self):
        source = self.read("ui/src-tauri/src/lib.rs")
        self.assertIn("fn play_unit_audio", source)
        self.assertIn("fn stop_unit_audio", source)
        self.assertIn("play_unit_audio,", source)
        self.assertIn("stop_unit_audio,", source)
        self.assertNotIn("render_fingerprint", source)
        self.assertNotIn("apply_pronunciation", source)
        self.assertNotIn(".onnx", source)

    def test_svelte_only_offers_playback_for_ready_audio(self):
        source = self.read("ui/src/App.svelte")
        self.assertIn("Anhören", source)
        self.assertIn("Stop", source)
        self.assertIn("projectBridge.playUnitAudio", source)
        self.assertIn("projectBridge.stopUnitAudio", source)
        self.assertIn('unit.audioState === "ready"', source)
        self.assertNotIn("renderText", source)
        self.assertNotIn("sha256", source)
        self.assertNotIn(".onnx", source)
        self.assertNotIn("/Volumes/", source)

    def test_project_model_contains_no_playback_state(self):
        source = self.read("src/application/project.py")
        self.assertNotIn("isPlaying", source)
        self.assertNotIn("playbackState", source)


if __name__ == "__main__":
    unittest.main()
