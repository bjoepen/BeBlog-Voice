import subprocess
import unittest
from unittest.mock import patch

from src.runtime.process import (
    PiperProcessError,
    run_piper,
)


class PiperProcessTest(unittest.TestCase):

    @patch("src.runtime.process.subprocess.run")
    def test_invokes_subprocess(self, mocked_run):
        run_piper(
            [
                "piper",
                "--model",
                "/models/thorsten.onnx",
                "--output_file",
                "/output/001.wav",
            ],
            input_text="Hallo Thorsten.",
        )

        mocked_run.assert_called_once_with(
            [
                "piper",
                "--model",
                "/models/thorsten.onnx",
                "--output_file",
                "/output/001.wav",
            ],
            input="Hallo Thorsten.",
            text=True,
            check=True,
            capture_output=True,
        )

    @patch(
        "src.runtime.process.subprocess.run",
        side_effect=FileNotFoundError,
    )
    def test_missing_executable_is_explicit(self, _mocked_run):
        with self.assertRaisesRegex(
            PiperProcessError,
            "Piper executable not found",
        ):
            run_piper(
                ["piper"],
                input_text="Test.",
            )

    @patch("src.runtime.process.subprocess.run")
    def test_failed_process_is_explicit(self, mocked_run):
        mocked_run.side_effect = subprocess.CalledProcessError(
            returncode=1,
            cmd=["piper"],
            stderr="synthetic failure",
        )

        with self.assertRaisesRegex(
            PiperProcessError,
            "synthetic failure",
        ):
            run_piper(
                ["piper"],
                input_text="Test.",
            )

    def test_rejects_empty_text(self):
        with self.assertRaises(ValueError):
            run_piper(
                ["piper"],
                input_text="",
            )


if __name__ == "__main__":
    unittest.main()
