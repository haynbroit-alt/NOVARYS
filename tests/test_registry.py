from __future__ import annotations

import json
from pathlib import Path

import pytest

from novarys_omega import registry


def filled(path: Path, count: int = 3) -> list[dict[str, object]]:
    return [registry.append(path, {"claim": f"c{i}", "status": "PROUVE"}) for i in range(count)]


def rewrite(path: Path, records: list[dict[str, object]]) -> None:
    path.write_text("".join(registry.canonical(r) + "\n" for r in records), encoding="utf-8")


def test_append_chains_each_record_to_the_previous_one(tmp_path: Path) -> None:
    path = tmp_path / "registre" / "preuves.jsonl"
    first, second, third = filled(path)
    assert (first["seq"], first["prev"]) == (1, "")
    assert second["prev"] == first["hash"] and third["prev"] == second["hash"]
    assert registry.read(path) == [first, second, third]
    assert registry.chain_errors(registry.read(path)) == []


def test_any_rewrite_of_the_past_is_detected(tmp_path: Path) -> None:
    path = tmp_path / "preuves.jsonl"
    records = filled(path)

    rewrite(path, [{**records[0], "status": "ECHEC"}, *records[1:]])  # contenu modifié
    assert "contenu modifié" in registry.chain_errors(registry.read(path))[0]

    forged = {**records[0], "status": "ECHEC"}
    forged["hash"] = registry.seal(forged)  # modifié ET rescellé : c'est le chaînage qui le trahit
    rewrite(path, [forged, *records[1:]])
    assert any("chaînage rompu" in error for error in registry.chain_errors(registry.read(path)))

    rewrite(path, [records[0], records[2]])  # un échec retiré du milieu
    assert registry.chain_errors(registry.read(path))

    rewrite(path, [records[1], records[0], records[2]])  # permutation
    assert registry.chain_errors(registry.read(path))


def test_append_refuses_to_continue_a_corrupted_registry(tmp_path: Path) -> None:
    path = tmp_path / "preuves.jsonl"
    records = filled(path)
    rewrite(path, [{**records[0], "status": "ECHEC"}, *records[1:]])
    with pytest.raises(ValueError, match="registre corrompu"):
        registry.append(path, {"claim": "c9"})
    assert len(registry.read(path)) == 3


def test_floats_and_invalid_lines_are_refused(tmp_path: Path) -> None:
    path = tmp_path / "preuves.jsonl"
    with pytest.raises(TypeError, match="virgule"):
        registry.append(path, {"runs": [{"duration_ms": 1.5}]})
    assert registry.read(path) == []
    path.write_text("pas du json\n", encoding="utf-8")
    with pytest.raises(ValueError, match="ligne 1"):
        registry.read(path)


def test_extends_means_same_past_and_nothing_removed(tmp_path: Path) -> None:
    path = tmp_path / "preuves.jsonl"
    records = filled(path)
    assert (
        registry.extends([], records) and registry.extends(records[:2], records) and registry.extends(records, records)
    )
    assert not registry.extends(records, records[:2])  # tronqué
    altered = json.loads(json.dumps(records))
    altered[0]["status"] = "ECHEC"
    assert not registry.extends(records[:2], altered)  # passé réécrit


def test_unusual_characters_and_a_missing_final_newline_do_not_break_the_file(tmp_path: Path) -> None:
    path = tmp_path / "preuves.jsonl"
    registry.append(path, {"output": "ligne\u2028suite\u2029fin\x85"})  # séparateurs que splitlines() couperait
    path.write_text(path.read_text(encoding="utf-8").rstrip("\n"), encoding="utf-8")  # un éditeur a ôté le dernier
    registry.append(path, {"output": "seconde"})
    records = registry.read(path)
    assert [r["seq"] for r in records] == [1, 2] and registry.chain_errors(records) == []
    assert records[0]["output"] == "ligne\u2028suite\u2029fin\x85"
