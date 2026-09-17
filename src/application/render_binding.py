from pathlib import Path
import os
import shutil
import tempfile

from src.application.audio_state import complete_render, fail_render
from src.core.render_units import build_render_units


def _voice_plan(project: dict) -> dict:
    units = project.get("units")
    if not isinstance(units, list):
        raise ValueError("project requires units")

    plan = {}
    for index, unit in enumerate(units, start=1):
        if not isinstance(unit, dict):
            raise ValueError("project unit must be a dictionary")

        voice_id = unit.get("voiceId")
        if not isinstance(voice_id, str) or not voice_id:
            raise ValueError("project unit requires voiceId")

        plan[f"{index:03d}"] = voice_id

    return plan


def _promote_audio_artifact(*, source, artifact_directory, unit_id: str):
    source_path = Path(source)
    if not source_path.is_file():
        raise RuntimeError(f"runtime audio artifact does not exist: {source_path}")

    artifact_directory = Path(artifact_directory)
    artifact_directory.mkdir(parents=True, exist_ok=True)
    target = artifact_directory / f"{unit_id}{source_path.suffix}"

    fd, temporary_name = tempfile.mkstemp(
        prefix=f".{unit_id}.", suffix=".artifact.tmp", dir=artifact_directory
    )
    os.close(fd)
    temporary = Path(temporary_name)
    try:
        shutil.copyfile(source_path, temporary)
        with temporary.open("rb") as handle:
            os.fsync(handle.fileno())
        os.replace(temporary, target)
    finally:
        if temporary.exists():
            temporary.unlink()

    return target


def render_project_unit(
    *,
    project: dict,
    unit_id: str,
    pronunciation: dict,
    voices: dict,
    runtime,
    previous_audio: dict | None = None,
    artifact_directory=None,
) -> dict:
    if not isinstance(project, dict):
        raise TypeError("project must be a dictionary")

    manuscript = project.get("manuscript")
    project_units = project.get("units")

    if not isinstance(manuscript, str):
        raise ValueError("project requires manuscript")

    if not isinstance(project_units, list):
        raise ValueError("project requires units")

    selected_index = None
    for index, project_unit in enumerate(project_units):
        if not isinstance(project_unit, dict):
            raise ValueError("project unit must be a dictionary")
        if project_unit.get("id") == unit_id:
            selected_index = index
            break

    if selected_index is None:
        raise ValueError(f"unknown project unit ID: {unit_id!r}")

    render_units = build_render_units(
        manuscript=manuscript,
        pronunciation=pronunciation,
        voices=voices,
        voice_plan=_voice_plan(project),
    )

    if len(render_units) != len(project_units):
        raise ValueError("project units do not match manuscript")

    render_unit = render_units[selected_index]
    previous_audio = previous_audio or {}
    previous_fingerprint = previous_audio.get("renderedFingerprint")
    previous_path = previous_audio.get("audioPath")

    try:
        runtime_path = runtime.render(render_unit)
        audio_path = (
            _promote_audio_artifact(
                source=runtime_path,
                artifact_directory=artifact_directory,
                unit_id=unit_id,
            )
            if artifact_directory is not None
            else runtime_path
        )
    except Exception as error:
        failed = fail_render(
            rendered_fingerprint=previous_fingerprint,
            error=str(error),
        )
        return {
            "unitId": unit_id,
            "audioState": failed["status"],
            "renderedFingerprint": failed["renderedFingerprint"],
            "audioPath": previous_path,
            "error": failed["error"],
        }

    completed = complete_render(
        render_text=render_unit["renderText"],
        voice_id=render_unit["voiceId"],
    )

    return {
        "unitId": unit_id,
        "audioState": completed["status"],
        "renderedFingerprint": completed["renderedFingerprint"],
        "audioPath": audio_path,
    }
