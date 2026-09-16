from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "ui" / "src" / "App.svelte"
BRIDGE = ROOT / "ui" / "src" / "lib" / "projectBridge.js"
RUST = ROOT / "ui" / "src-tauri" / "src" / "lib.rs"


class UiLiveBindingAcceptanceTests(unittest.TestCase):
    def test_svelte_uses_project_bridge_instead_of_hardcoded_units(self):
        source = APP.read_text(encoding="utf-8")

        self.assertIn("projectBridge", source)
        self.assertNotIn("let units = [", source)
        self.assertNotIn('number: "001"', source)

    def test_bridge_exposes_project_sync_and_stable_voice_change(self):
        source = BRIDGE.read_text(encoding="utf-8")

        self.assertIn("loadProjectState", source)
        self.assertIn("syncManuscript", source)
        self.assertIn("setUnitVoice", source)
        self.assertIn("unitId", source)

    def test_frontend_calls_tauri_commands_but_contains_no_domain_logic(self):
        source = BRIDGE.read_text(encoding="utf-8").lower()

        self.assertIn("@tauri-apps/api/core", source)
        self.assertIn("invoke", source)
        self.assertNotIn("sha256", source)
        self.assertNotIn("render_fingerprint", source)
        self.assertNotIn("onnx", source)
        self.assertNotIn("wiktionary", source)

    def test_tauri_boundary_declares_project_state_commands(self):
        source = RUST.read_text(encoding="utf-8")

        self.assertIn("load_project_state", source)
        self.assertIn("sync_manuscript", source)
        self.assertIn("set_unit_voice", source)
        self.assertIn("invoke_handler", source)

    def test_svelte_addresses_voice_change_by_stable_id(self):
        source = APP.read_text(encoding="utf-8")

        self.assertIn("unit.id", source)
        self.assertIn("setUnitVoice", source)
        self.assertNotIn("renderText", source)


if __name__ == "__main__":
    unittest.main()
