import tempfile
import unittest
from pathlib import Path

from src.runtime.piper import (
    PiperRuntime,
    RuntimeConfigurationError,
)


VOICES = {
    "thorsten-high": {
        "name": "Thorsten High",
        "role": "default",
        "modelRef": "de_DE-thorsten-high",
    },
    "thorsten-hessisch": {
        "name": "Thorsten Hessisch",
        "role": "special",
        "modelRef":
            "Thorsten-Voice_Hessisch_Piper_high-Oct2023",
    },
}


class PiperRuntimeAcceptanceTest(unittest.TestCase):

    def test_resolves_voice_to_model(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            high = root / "de_DE-thorsten-high.onnx"
            high.touch()

            runtime = PiperRuntime(
                voices=VOICES,
                model_directory=root,
            )

            self.assertEqual(
                runtime.resolve_model("thorsten-high"),
                high,
            )

    def test_resolves_hessisch_independently(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            hessisch = (
                root
                / "Thorsten-Voice_Hessisch_Piper_high-Oct2023.onnx"
            )
            hessisch.touch()

            runtime = PiperRuntime(
                voices=VOICES,
                model_directory=root,
            )

            self.assertEqual(
                runtime.resolve_model("thorsten-hessisch"),
                hessisch,
            )

    def test_missing_model_fails_explicitly(self):
        with tempfile.TemporaryDirectory() as tmp:
            runtime = PiperRuntime(
                voices=VOICES,
                model_directory=Path(tmp),
            )

            with self.assertRaises(RuntimeConfigurationError):
                runtime.resolve_model("thorsten-high")

    def test_unknown_voice_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            runtime = PiperRuntime(
                voices=VOICES,
                model_directory=Path(tmp),
            )

            with self.assertRaises(ValueError):
                runtime.resolve_model("karlsson")

    def test_output_path_is_derived_from_unit_id(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "output"

            runtime = PiperRuntime(
                voices=VOICES,
                model_directory=Path(tmp),
                output_directory=output,
            )

            self.assertEqual(
                runtime.output_path("003"),
                output / "003.wav",
            )


    def test_render_unit_invokes_runner(self):
        calls = []

        def fake_runner(command, *, input_text):
            calls.append((command, input_text))

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            model = root / "de_DE-thorsten-high.onnx"
            model.touch()

            output = root / "output"

            runtime = PiperRuntime(
                voices=VOICES,
                model_directory=root,
                output_directory=output,
                runner=fake_runner,
            )

            unit = {
                "id": "001",
                "originalText": "Die Montage beginnt.",
                "renderText": "Die [[ mɔnˈtaːʒə ]] beginnt.",
                "voiceId": "thorsten-high",
            }

            result = runtime.render(unit)

            self.assertEqual(result, output / "001.wav")
            self.assertEqual(len(calls), 1)

            command, input_text = calls[0]

            self.assertEqual(
                command,
                [
                    "piper",
                    "--model",
                    str(model),
                    "--output_file",
                    str(output / "001.wav"),
                ],
            )

            self.assertEqual(
                input_text,
                "Die [[ mɔnˈtaːʒə ]] beginnt.",
            )

    def test_render_uses_selected_voice(self):
        calls = []

        def fake_runner(command, *, input_text):
            calls.append((command, input_text))

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            model = (
                root
                / "Thorsten-Voice_Hessisch_Piper_high-Oct2023.onnx"
            )
            model.touch()

            runtime = PiperRuntime(
                voices=VOICES,
                model_directory=root,
                runner=fake_runner,
            )

            unit = {
                "id": "003",
                "originalText": "Des werd schon widder!",
                "renderText": "Des werd schon widder!",
                "voiceId": "thorsten-hessisch",
            }

            runtime.render(unit)

            command, input_text = calls[0]

            self.assertIn(str(model), command)
            self.assertEqual(
                input_text,
                "Des werd schon widder!",
            )


if __name__ == "__main__":
    unittest.main()
