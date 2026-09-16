#!/usr/bin/env python3

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.application.render import render_manuscript
from src.runtime.piper import PiperRuntime
from src.runtime.process import run_piper


PIPER_ROOT = Path("/Volumes/Kioxia/Tools/piper")
PIPER_PYTHON = PIPER_ROOT / ".venv/bin/python"

VOICES_PATH = ROOT / "resources" / "voices.json"
PRONUNCIATION_PATH = ROOT / "resources" / "pronunciation.json"

OUTPUT = ROOT / "output" / "acceptance-004f"


MANUSCRIPT = """Die Linearführung wird vor der Montage geprüft.

Des werd schon widder!"""


VOICE_PLAN = {
    "002": "thorsten-hessisch",
}


def real_runner(command: list[str], *, input_text: str) -> None:
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
        VOICES_PATH.read_text(encoding="utf-8")
    )

    pronunciation = json.loads(
        PRONUNCIATION_PATH.read_text(encoding="utf-8")
    )

    OUTPUT.mkdir(parents=True, exist_ok=True)

    runtime = PiperRuntime(
        voices=voices,
        model_directory=PIPER_ROOT,
        output_directory=OUTPUT,
        runner=real_runner,
    )

    original_manuscript = MANUSCRIPT

    results = render_manuscript(
        manuscript=MANUSCRIPT,
        pronunciation=pronunciation,
        voices=voices,
        runtime=runtime,
        voice_plan=VOICE_PLAN,
    )

    if MANUSCRIPT != original_manuscript:
        raise RuntimeError(
            "Manuscript was mutated"
        )

    if [result["unitId"] for result in results] != [
        "001",
        "002",
    ]:
        raise RuntimeError(
            f"Unexpected render units: {results}"
        )

    for result in results:
        assert_wav(result["audioPath"])

    print("=== 004-F END-TO-END ACCEPTANCE ===")
    print()
    print("PASS: normales Manuskript angenommen")
    print("PASS: zwei Render Units erzeugt")
    print("PASS: Originalmanuskript unverändert")
    print("PASS: Application Service -> Runtime")
    print("PASS: reale Piper-Ausgabe erzeugt")
    print()

    for result in results:
        path = result["audioPath"]
        print(
            f"PASS: {result['unitId']} -> "
            f"{path.stat().st_size} bytes"
        )

    print()
    print("Hörprüfung:")
    print(f"  {results[0]['audioPath']}")
    print(f"  {results[1]['audioPath']}")
    print()
    print(
        "004-F4 – Automatic End-to-End "
        "Acceptance: PASS"
    )


if __name__ == "__main__":
    main()
