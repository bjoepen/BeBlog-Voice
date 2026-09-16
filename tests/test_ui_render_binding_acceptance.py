import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class DesktopRenderBindingAcceptanceTests(unittest.TestCase):
    def read(self, relative_path: str) -> str:
        return (ROOT / relative_path).read_text(encoding="utf-8")

    def test_frontend_bridge_exposes_stable_unit_render_command(self):
        source = self.read("ui/src/lib/projectBridge.js")
        self.assertIn('invoke("render_project_unit"', source)
        self.assertIn("unitId", source)

    def test_tauri_transport_exposes_render_command_without_tts_domain_logic(self):
        source = self.read("ui/src-tauri/src/lib.rs")
        self.assertIn("fn render_project_unit", source)
        self.assertIn("render_project_unit,", source)
        self.assertIn('"action": "render"', source)
        self.assertNotIn("render_fingerprint", source)
        self.assertNotIn("apply_pronunciation", source)
        self.assertNotIn(".onnx", source)

    def test_python_bridge_delegates_render_to_application_binding(self):
        source = self.read("scripts/ui-project-bridge.py")
        self.assertIn(
            "from src.application.render_binding import render_project_unit",
            source,
        )
        self.assertIn('if action == "render":', source)
        self.assertIn("render_project_unit(", source)
        self.assertIn("resources", source)
        self.assertIn("pronunciation.json", source)
        self.assertNotIn("render_fingerprint(", source)
        self.assertNotIn("apply_pronunciation(", source)

    def test_svelte_has_per_unit_render_action_and_no_domain_details(self):
        source = self.read("ui/src/App.svelte")
        self.assertIn("Rendern", source)
        self.assertIn("projectBridge.renderProjectUnit", source)
        self.assertIn("unit.id", source)
        self.assertNotIn("renderText", source)
        self.assertNotIn("sha256", source)
        self.assertNotIn(".onnx", source)
        self.assertNotIn("/Volumes/", source)


if __name__ == "__main__":
    unittest.main()
