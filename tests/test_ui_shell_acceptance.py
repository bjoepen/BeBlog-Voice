from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]


class UIShellAcceptanceTest(unittest.TestCase):

    def test_frontend_declares_svelte_vite_and_tauri(self):
        package_path = ROOT / "ui" / "package.json"
        self.assertTrue(package_path.is_file())

        package = json.loads(package_path.read_text(encoding="utf-8"))
        dependencies = {
            **package.get("dependencies", {}),
            **package.get("devDependencies", {}),
        }

        self.assertIn("svelte", dependencies)
        self.assertIn("vite", dependencies)
        self.assertIn("@tauri-apps/api", dependencies)

    def test_tauri_v2_shell_exists(self):
        cargo_path = ROOT / "ui" / "src-tauri" / "Cargo.toml"
        config_path = ROOT / "ui" / "src-tauri" / "tauri.conf.json"

        self.assertTrue(cargo_path.is_file())
        self.assertTrue(config_path.is_file())

        cargo = cargo_path.read_text(encoding="utf-8")
        self.assertIn('tauri = { version = "2"', cargo)

    def test_shell_contains_manuscript_editor_and_render_units(self):
        app_path = ROOT / "ui" / "src" / "App.svelte"
        self.assertTrue(app_path.is_file())

        app = app_path.read_text(encoding="utf-8")
        self.assertIn("MANUSKRIPT", app)
        self.assertIn("RENDER UNITS", app)
        self.assertIn("textarea", app)

    def test_shell_exposes_explicit_voice_choices_without_fixture_text(self):
        app_path = ROOT / "ui" / "src" / "App.svelte"
        app = app_path.read_text(encoding="utf-8")

        self.assertIn("thorsten-high", app)
        self.assertIn("thorsten-hessisch", app)
        self.assertIn("Thorsten High", app)
        self.assertIn("Thorsten Hessisch", app)
        self.assertNotIn("Des werd schon widder!", app)

    def test_ui_does_not_contain_tts_or_pronunciation_implementation(self):
        source_dir = ROOT / "ui" / "src"
        self.assertTrue(source_dir.is_dir())

        source = "\n".join(
            path.read_text(encoding="utf-8")
            for path in source_dir.rglob("*")
            if path.is_file()
        )

        forbidden = (
            "subprocess",
            ".onnx",
            "wiktionary",
            "sha256",
            "render_fingerprint",
        )
        for token in forbidden:
            self.assertNotIn(token, source.lower())


if __name__ == "__main__":
    unittest.main()
