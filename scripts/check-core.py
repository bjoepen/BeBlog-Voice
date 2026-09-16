#!/usr/bin/env python3

import ast
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "src/core"
VOICES = ROOT / "resources/voices.json"

FORBIDDEN_IMPORTS = {
    "subprocess",
    "piper",
}

FORBIDDEN_SUFFIXES = {
    ".onnx",
    ".wav",
}


def check_python_file(path: Path) -> None:
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(path))

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".")[0]

                if root in FORBIDDEN_IMPORTS:
                    raise RuntimeError(
                        f"{path}: forbidden import {alias.name!r}"
                    )

        elif isinstance(node, ast.ImportFrom):
            if node.module:
                root = node.module.split(".")[0]

                if root in FORBIDDEN_IMPORTS:
                    raise RuntimeError(
                        f"{path}: forbidden import {node.module!r}"
                    )

    for suffix in FORBIDDEN_SUFFIXES:
        if suffix in source:
            raise RuntimeError(
                f"{path}: runtime artifact reference {suffix!r}"
            )


def main():
    files = sorted(CORE.glob("*.py"))

    if not files:
        raise RuntimeError("No product core files found.")

    for path in files:
        check_python_file(path)

    voices = json.loads(
        VOICES.read_text(encoding="utf-8")
    )

    defaults = [
        voice_id
        for voice_id, voice in voices.items()
        if voice.get("role") == "default"
    ]

    if defaults != ["thorsten-high"]:
        raise RuntimeError(
            f"Unexpected default voices: {defaults}"
        )

    for voice_id, voice in voices.items():
        if "model" in voice:
            raise RuntimeError(
                f"{voice_id}: physical model path found"
            )

        if not voice.get("modelRef"):
            raise RuntimeError(
                f"{voice_id}: modelRef missing"
            )

    print("004-D CORE INTEGRITY: PASS")
    print(f"Core modules checked: {len(files)}")
    print("PASS: no subprocess dependency")
    print("PASS: no Piper dependency")
    print("PASS: no ONNX references")
    print("PASS: no WAV/runtime coupling")
    print("PASS: Voice Registry uses modelRef")
    print("PASS: thorsten-high is sole default")


if __name__ == "__main__":
    main()
