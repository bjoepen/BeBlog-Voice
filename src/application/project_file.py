import json
import os
from pathlib import Path
import tempfile

from src.application.project import deserialize_project, serialize_project


def save_project_file(path, project: dict) -> None:
    target = Path(path)
    data = serialize_project(project)
    payload = json.dumps(
        data,
        ensure_ascii=False,
        indent=2,
    ) + "\n"

    target.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=target.parent,
            prefix=f".{target.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            temporary_path = Path(handle.name)
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())

        os.replace(temporary_path, target)
        temporary_path = None
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


def load_project_file(path) -> dict:
    source = Path(path)

    try:
        data = json.loads(source.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ValueError("invalid project file") from error

    return deserialize_project(data)
