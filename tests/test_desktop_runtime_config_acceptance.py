import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.application.desktop_runtime_config import load_desktop_runtime_config


class DesktopRuntimeConfigAcceptanceTests(unittest.TestCase):
    def test_loads_machine_local_runtime_configuration(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "runtime.json"
            path.write_text(
                json.dumps(
                    {
                        "piperCommand": ["/local/piper-python", "-m", "piper"],
                        "modelDirectory": "/local/piper-models",
                    }
                ),
                encoding="utf-8",
            )

            config = load_desktop_runtime_config(path=path)

        self.assertEqual(
            config["piperCommand"],
            ["/local/piper-python", "-m", "piper"],
        )
        self.assertEqual(config["modelDirectory"], "/local/piper-models")

    def test_environment_selects_config_file_without_embedding_machine_path(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "runtime.json"
            path.write_text(
                json.dumps(
                    {
                        "piperCommand": ["python3", "-m", "piper"],
                        "modelDirectory": "/models",
                    }
                ),
                encoding="utf-8",
            )

            with patch.dict(
                os.environ,
                {"BEBLOG_VOICE_RUNTIME_CONFIG": str(path)},
                clear=False,
            ):
                config = load_desktop_runtime_config()

        self.assertEqual(config["modelDirectory"], "/models")

    def test_invalid_configuration_is_rejected(self):
        invalid_configs = [
            {},
            {"piperCommand": [], "modelDirectory": "/models"},
            {"piperCommand": ["python3"], "modelDirectory": ""},
            {"piperCommand": "python3 -m piper", "modelDirectory": "/models"},
        ]

        for data in invalid_configs:
            with self.subTest(data=data), tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "runtime.json"
                path.write_text(json.dumps(data), encoding="utf-8")
                with self.assertRaises(ValueError):
                    load_desktop_runtime_config(path=path)

    def test_configuration_is_not_project_content(self):
        source = Path("src/application/project.py").read_text(encoding="utf-8")
        self.assertNotIn("piperCommand", source)
        self.assertNotIn("modelDirectory", source)
        self.assertNotIn("BEBLOG_VOICE_RUNTIME_CONFIG", source)


if __name__ == "__main__":
    unittest.main()
