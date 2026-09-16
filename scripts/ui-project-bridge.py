#!/usr/bin/env python3
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.application.project import create_project, sync_project
from src.application.project_file import load_project_file, save_project_file
from src.application.ui_state import build_ui_state, set_unit_voice


DEFAULT_MANUSCRIPT = (
    "Die Linearführung wird vor der Montage geprüft.\n\n"
    "Des werd schon widder!"
)


def load_voices() -> dict:
    return json.loads((ROOT / "resources" / "voices.json").read_text(encoding="utf-8"))


def respond(project: dict, voices: dict) -> dict:
    return {
        "project": project,
        "view": build_ui_state(project, voices),
    }


def handle(request: dict) -> dict:
    voices = load_voices()
    action = request.get("action")

    if action == "load":
        return respond(create_project(DEFAULT_MANUSCRIPT), voices)

    if action == "open-file":
        path = request.get("path")
        if not isinstance(path, str) or not path:
            raise ValueError("open-file requires path")
        return respond(load_project_file(path), voices)

    project = request.get("project")
    if not isinstance(project, dict):
        raise ValueError("bridge request requires project")

    if action == "save-file":
        path = request.get("path")
        if not isinstance(path, str) or not path:
            raise ValueError("save-file requires path")
        save_project_file(path, project)
        return respond(project, voices)

    if action == "sync":
        manuscript = request.get("manuscript")
        if not isinstance(manuscript, str):
            raise ValueError("sync requires manuscript")
        return respond(sync_project(project, manuscript), voices)

    if action == "voice":
        unit_id = request.get("unitId")
        voice_id = request.get("voiceId")
        changed = set_unit_voice(
            project,
            unit_id=unit_id,
            voice_id=voice_id,
            voices=voices,
        )
        return respond(changed, voices)

    raise ValueError(f"unknown bridge action: {action!r}")


def main() -> int:
    try:
        request = json.load(sys.stdin)
        json.dump(handle(request), sys.stdout, ensure_ascii=False)
        sys.stdout.write("\n")
        return 0
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
