from pathlib import Path

from src.core.voices import require_voice, validate_voices


class RuntimeConfigurationError(RuntimeError):
    pass


class PiperRuntime:
    def __init__(
        self,
        voices: dict,
        model_directory: Path,
        output_directory: Path | None = None,
        runner=None,
    ):
        validate_voices(voices)

        self.voices = voices
        self.model_directory = Path(model_directory)
        self.output_directory = (
            Path(output_directory)
            if output_directory is not None
            else Path("output")
        )
        self.runner = runner

    def resolve_model(self, voice_id: str) -> Path:
        voice = require_voice(self.voices, voice_id)

        model_ref = voice["modelRef"]
        model_path = self.model_directory / f"{model_ref}.onnx"

        if not model_path.is_file():
            raise RuntimeConfigurationError(
                f"Piper model not found for voice "
                f"{voice_id!r}: {model_path}"
            )

        return model_path

    def output_path(self, unit_id: str) -> Path:
        if not isinstance(unit_id, str) or not unit_id:
            raise ValueError(
                "unit_id must be a non-empty string"
            )

        return self.output_directory / f"{unit_id}.wav"

    def render(self, unit: dict) -> Path:
        if self.runner is None:
            raise RuntimeConfigurationError(
                "Piper runner is not configured"
            )

        if not isinstance(unit, dict):
            raise TypeError("unit must be a dictionary")

        unit_id = unit.get("id")
        render_text = unit.get("renderText")
        voice_id = unit.get("voiceId")

        if not isinstance(render_text, str) or not render_text:
            raise ValueError(
                "render unit requires non-empty renderText"
            )

        if not isinstance(voice_id, str) or not voice_id:
            raise ValueError(
                "render unit requires non-empty voiceId"
            )

        model_path = self.resolve_model(voice_id)
        output_path = self.output_path(unit_id)

        self.output_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        command = [
            "piper",
            "--model",
            str(model_path),
            "--output_file",
            str(output_path),
        ]

        self.runner(
            command,
            input_text=render_text,
        )

        return output_path
