import subprocess


class PiperProcessError(RuntimeError):
    pass


def run_piper(command: list[str], *, input_text: str) -> None:
    if not isinstance(command, list) or not command:
        raise ValueError("command must be a non-empty list")

    if not all(isinstance(part, str) and part for part in command):
        raise ValueError(
            "command entries must be non-empty strings"
        )

    if not isinstance(input_text, str) or not input_text:
        raise ValueError(
            "input_text must be a non-empty string"
        )

    try:
        subprocess.run(
            command,
            input=input_text,
            text=True,
            check=True,
            capture_output=True,
        )
    except FileNotFoundError as exc:
        raise PiperProcessError(
            f"Piper executable not found: {command[0]}"
        ) from exc
    except subprocess.CalledProcessError as exc:
        stderr = (exc.stderr or "").strip()

        message = (
            f"Piper process failed with exit code "
            f"{exc.returncode}"
        )

        if stderr:
            message += f": {stderr}"

        raise PiperProcessError(message) from exc
