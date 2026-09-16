#!/usr/bin/env python3

import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APPLICATION = ROOT / "src" / "application"

FORBIDDEN_IMPORTS = {
    "subprocess",
    "piper",
}

FORBIDDEN_REFERENCES = {
    ".onnx",
    ".wav",
}

REQUIRED_CORE_IMPORT = (
    "src.core.render_units",
    "build_render_units",
)


def imported_names(tree):
    imports = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append((alias.name, None))

        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""

            for alias in node.names:
                imports.append((module, alias.name))

    return imports


def main():
    files = sorted(APPLICATION.glob("*.py"))

    if not files:
        raise SystemExit(
            "FAIL: no application modules found"
        )

    core_import_found = False

    for path in files:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))

        for module, name in imported_names(tree):
            root_module = module.split(".")[0]

            if root_module in FORBIDDEN_IMPORTS:
                raise SystemExit(
                    f"FAIL: forbidden import "
                    f"{module!r} in {path}"
                )

            if (
                module == REQUIRED_CORE_IMPORT[0]
                and name == REQUIRED_CORE_IMPORT[1]
            ):
                core_import_found = True

        for reference in FORBIDDEN_REFERENCES:
            if reference in source:
                raise SystemExit(
                    f"FAIL: forbidden runtime reference "
                    f"{reference!r} in {path}"
                )

    if not core_import_found:
        raise SystemExit(
            "FAIL: application does not use "
            "build_render_units"
        )

    print("004-F APPLICATION INTEGRITY: PASS")
    print(f"Application modules checked: {len(files)}")
    print("PASS: no subprocess dependency")
    print("PASS: no Piper dependency")
    print("PASS: no ONNX references")
    print("PASS: no WAV coupling")
    print("PASS: render units come from product core")


if __name__ == "__main__":
    main()
