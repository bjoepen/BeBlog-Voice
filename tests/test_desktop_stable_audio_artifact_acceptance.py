import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BRIDGE = ROOT / "scripts" / "ui-project-bridge.py"


class DesktopStableAudioArtifactAcceptanceTests(unittest.TestCase):
    def test_desktop_render_supplies_stable_artifact_directory(self):
        source = BRIDGE.read_text(encoding="utf-8")
        self.assertIn("artifact_directory=", source)
        self.assertIn("AUDIO_ARTIFACT_DIRECTORY", source)

    def test_stable_artifacts_are_separate_from_runtime_output(self):
        source = BRIDGE.read_text(encoding="utf-8")
        self.assertIn('ROOT / "output"', source)
        self.assertIn('ROOT / ".local" / "audio-artifacts"', source)


if __name__ == "__main__":
    unittest.main()
