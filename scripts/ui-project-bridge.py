#!/usr/bin/env python3
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.application.desktop_runtime_config import load_desktop_runtime_config
from src.application.project import create_project, sync_project
from src.application.project_file import load_project_file, save_project_file
from src.application.render_binding import render_project_unit
from src.application.ui_state import build_ui_state, set_unit_voice
from src.runtime.piper import PiperRuntime
from src.runtime.process import run_piper

DEFAULT_MANUSCRIPT = "Die Linearführung wird vor der Montage geprüft.\n\nDes werd schon widder!"
AUDIO_ARTIFACT_DIRECTORY = ROOT / ".local" / "audio-artifacts"


def load_voices() -> dict:
    return json.loads((ROOT / "resources" / "voices.json").read_text(encoding="utf-8"))


def load_pronunciation() -> dict:
    return json.loads((ROOT / "resources" / "pronunciation.json").read_text(encoding="utf-8"))


def build_runtime(voices: dict) -> PiperRuntime:
    config = load_desktop_runtime_config()
    piper_command = config["piperCommand"]

    def configured_runner(command: list[str], *, input_text: str) -> None:
        run_piper([*piper_command, *command[1:]], input_text=input_text)

    return PiperRuntime(voices=voices, model_directory=Path(config["modelDirectory"]), output_directory=ROOT / "output", runner=configured_runner)


def audio_from_request(request: dict) -> dict:
    audio = request.get("audioByUnit")
    if audio is None:
        return {}
    if not isinstance(audio, dict):
        raise ValueError("audioByUnit must be a dictionary")
    return audio


def respond(project: dict, voices: dict, *, audio_by_unit: dict | None = None) -> dict:
    return {
        "project": project,
        "view": build_ui_state(
            project,
            voices,
            pronunciation=load_pronunciation(),
            audio_by_unit=audio_by_unit,
        ),
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
        return respond(project, voices, audio_by_unit=audio_from_request(request))

    if action == "sync":
        manuscript = request.get("manuscript")
        if not isinstance(manuscript, str):
            raise ValueError("sync requires manuscript")
        return respond(sync_project(project, manuscript), voices, audio_by_unit=audio_from_request(request))

    if action == "voice":
        changed = set_unit_voice(project, unit_id=request.get("unitId"), voice_id=request.get("voiceId"), voices=voices)
        return respond(changed, voices, audio_by_unit=audio_from_request(request))

    if action == "render":
        unit_id = request.get("unitId")
        if not isinstance(unit_id, str) or not unit_id:
            raise ValueError("render requires unitId")
        previous_audio = request.get("previousAudio")
        if previous_audio is not None and not isinstance(previous_audio, dict):
            raise ValueError("previousAudio must be a dictionary")
        return render_project_unit(
            project=project,
            unit_id=unit_id,
            pronunciation=load_pronunciation(),
            voices=voices,
            runtime=build_runtime(voices),
            previous_audio=previous_audio,
            artifact_directory=AUDIO_ARTIFACT_DIRECTORY,
        )

    raise ValueError(f"unknown bridge action: {action!r}")


def main() -> int:
    try:
        request = json.load(sys.stdin)
        json.dump(handle(request), sys.stdout, ensure_ascii=False, default=str)
        sys.stdout.write("\n")
        return 0
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
