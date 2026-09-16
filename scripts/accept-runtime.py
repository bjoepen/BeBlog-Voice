#!/usr/bin/env python3

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.runtime.piper import PiperRuntime
from src.runtime.process import run_piper


PIPER_ROOT = Path("/Volumes/Kioxia/Tools/piper")
PIPER_PYTHON = PIPER_ROOT / ".venv/bin/python"

VOICES = ROOT / "resources/voices.json"
OUTPUT = ROOT / "output" / "acceptance-004e"


def real_runner(command: list[str], *, input_text: str) -> None:
    # The runtime contract intentionally uses "piper" as its
    # logical executable. This acceptance test binds that logical
    # command to the proven local Piper virtual environment.
    if command[0] != "piper":
        raise RuntimeError(
            f"Unexpected runtime executable: {command[0]}"
        )

    real_command = [
        str(PIPER_PYTHON),
        "-m",
        "piper",
        *command[1:],
    ]

    run_piper(
        real_command,
        input_text=input_text,
    )


def assert_wav(path: Path) -> None:
    if not path.is_file():
        raise RuntimeError(
            f"WAV was not created: {path}"
        )

    if path.stat().st_size == 0:
        raise RuntimeError(
            f"WAV is empty: {path}"
        )


def main() -> None:
    if not PIPER_PYTHON.is_file():
        raise RuntimeError(
            f"Piper Python not found: {PIPER_PYTHON}"
        )

    voices = json.loads(
        VOICES.read_text(encoding="utf-8")
    )

    OUTPUT.mkdir(parents=True, exist_ok=True)

    runtime = PiperRuntime(
        voices=voices,
        model_directory=PIPER_ROOT,
        output_directory=OUTPUT,
        runner=real_runner,
    )

    high = {
        "id": "001",
        "originalText":
            "Jetzt prüfen wir die lineare Führung.",
        "renderText":
            "Jetzt prüfen wir die lineare Führung.",
        "voiceId": "thorsten-high",
    }

    hessisch = {
        "id": "002",
        "originalText":
            "Des werd schon widder!",
        "renderText":
            "Des werd schon widder!",
        "voiceId": "thorsten-hessisch",
    }

    high_wav = runtime.render(high)
    hessisch_wav = runtime.render(hessisch)

    assert_wav(high_wav)
    assert_wav(hessisch_wav)

    print("=== 004-E REAL-WORLD ACCEPTANCE ===")
    print(
        f"PASS: Thorsten High -> "
        f"{high_wav.stat().st_size} bytes"
    )
    print(
        f"PASS: Thorsten Hessisch -> "
        f"{hessisch_wav.stat().st_size} bytes"
    )
    print("PASS: beide WAV-Dateien nicht leer")
    print("PASS: Voice-Auswahl erreicht reales Piper")
    print()
    print("Hörprüfung:")
    print(f"  {high_wav}")
    print(f"  {hessisch_wav}")
    print()
    print("004-E5 – Automatic Real-World Acceptance: PASS")


if __name__ == "__main__":
    main()
