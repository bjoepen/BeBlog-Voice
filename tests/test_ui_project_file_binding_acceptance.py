from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class UIProjectFileBindingAcceptanceTest(unittest.TestCase):
    def test_frontend_bridge_exposes_open_and_save_commands(self):
        source = (ROOT / "ui" / "src" / "lib" / "projectBridge.js").read_text(encoding="utf-8")

        self.assertIn('invoke("open_project_file"', source)
        self.assertIn('invoke("save_project_file"', source)

    def test_tauri_declares_open_and_save_commands(self):
        source = (ROOT / "ui" / "src-tauri" / "src" / "lib.rs").read_text(encoding="utf-8")

        self.assertIn("fn open_project_file", source)
        self.assertIn("fn save_project_file", source)
        self.assertIn("open_project_file,", source)
        self.assertIn("save_project_file,", source)

    def test_python_bridge_uses_application_project_file_boundary(self):
        source = (ROOT / "scripts" / "ui-project-bridge.py").read_text(encoding="utf-8")

        self.assertIn("from src.application.project_file import", source)
        self.assertIn("load_project_file", source)
        self.assertIn("save_project_file", source)
        self.assertIn('action == "open-file"', source)
        self.assertIn('action == "save-file"', source)

    def test_app_exposes_open_and_save_without_domain_logic(self):
        source = (ROOT / "ui" / "src" / "App.svelte").read_text(encoding="utf-8")

        self.assertIn("Projekt öffnen", source)
        self.assertIn("Projekt speichern", source)
        self.assertNotIn("renderText", source)
        self.assertNotIn("sha256", source.lower())
        self.assertNotIn(".onnx", source.lower())


if __name__ == "__main__":
    unittest.main()
