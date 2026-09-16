import json
import os
from pathlib import Path


RUNTIME_CONFIG_ENV = "BEBLOG_VOICE_RUNTIME_CONFIG"


def _validate_config(data: dict) -> dict:
    if not isinstance(data, dict):
        raise ValueError("desktop runtime configuration must be a dictionary")

    piper_command = data.get("piperCommand")
    model_directory = data.get("modelDirectory")

    if (
        not isinstance(piper_command, list)
        or not piper_command
        or any(not isinstance(part, str) or not part for part in piper_command)
    ):
        raise ValueError("piperCommand must be a non-empty list of strings")

    if not isinstance(model_directory, str) or not model_directory:
        raise ValueError("modelDirectory must be a non-empty string")

    return {
        "piperCommand": list(piper_command),
        "modelDirectory": model_directory,
    }


def load_desktop_runtime_config(*, path=None) -> dict:
    if path is None:
        configured_path = os.environ.get(RUNTIME_CONFIG_ENV)
        if not configured_path:
            raise ValueError(
                f"desktop runtime configuration requires {RUNTIME_CONFIG_ENV}"
            )
        path = configured_path

    source = Path(path)
    try:
        data = json.loads(source.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ValueError("invalid desktop runtime configuration") from error

    return _validate_config(data)
