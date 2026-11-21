from __future__ import annotations

import subprocess
from collections.abc import Callable
from pathlib import Path

import pytest

from novarys_omega.model import Charter, load_charter

ASSET = """
[[asset]]
name = "demo"
title = "Démonstration"
observed = "2026-11-21"
location = "nulle part"
access = "lecture"
state = "fictif"
demonstrated = "rien"
dependencies = "aucune"
costs = "0 €"
reuse = "INCONNU"
proofs = "aucune"
blockers = "aucun"
next_action = "aucune"
"""


def git(path: Path, *args: str) -> str:
    done = subprocess.run(
        ["git", "-C", str(path), "-c", "user.name=test", "-c", "user.email=test@invalid", *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return done.stdout.strip()


@pytest.fixture
def root(tmp_path: Path) -> Path:
    """Un dépôt NOVARYS minimal : Git initialisé, registre d'actifs présent, référentiel à écrire."""

    path = tmp_path / "novarys"
    (path / "registre").mkdir(parents=True)
    (path / "registre" / "actifs.toml").write_text(ASSET, encoding="utf-8")
    git(tmp_path, "init", "-q", str(path))
    return path


@pytest.fixture
def charter(root: Path) -> Callable[[str], Charter]:
    def write(text: str) -> Charter:
        target = root / "registre" / "capacites.toml"
        target.write_text(text, encoding="utf-8")
        return load_charter(target)

    return write
