from __future__ import annotations

from pathlib import Path
import os
import secrets
import subprocess
import typer

from sda.auth import verify_pass, EnvFileNames

# Variables / Constants for usage
app = typer.Typer(add_completion=False, no_args_is_help=True)


def _write_env(path: Path, lines: list[str]) -> None:
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

def _ensure_dirs(data_dir: str, cache_dir: str) -> None:
    Path(data_dir).mkdir(parents=True, exist_ok=True)
    Path(cache_dir).mkdir(parents=True, exist_ok=True)


