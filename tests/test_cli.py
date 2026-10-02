"""Testes da interface de linha de comando (CLI)."""

from __future__ import annotations

import json
from pathlib import Path
import pytest

from triagem_proposta.cli import main


def test_cli_json_inline(capsys: pytest.CaptureFixture, proposta_segue: dict) -> None:
    codigo = main(["--json", json.dumps(proposta_segue)])
    assert codigo == 0
    saida = capsys.readouterr().out
    assert "P-001" in saida
    assert "SEGUE" in saida


def test_cli_somente_parecer(capsys: pytest.CaptureFixture, proposta_segue: dict) -> None:
    codigo = main(["--json", json.dumps(proposta_segue), "--somente-parecer"])
    assert codigo == 0
    saida = capsys.readouterr().out.strip()
    assert saida == "P-001\tSEGUE"


def test_cli_arquivo_multiplas_propostas(
    tmp_path: Path, capsys: pytest.CaptureFixture, proposta_segue: dict, proposta_area_baixa: dict
) -> None:
    arquivo = tmp_path / "propostas.json"
    arquivo.write_text(json.dumps([proposta_segue, proposta_area_baixa]), encoding="utf-8")

    codigo = main([str(arquivo), "--somente-parecer"])
    assert codigo == 0
    saida = capsys.readouterr().out
    assert "P-001\tSEGUE" in saida
    assert "P-002\tRECUSADA" in saida


def test_cli_arquivo_com_relatorio_completo(
    tmp_path: Path, capsys: pytest.CaptureFixture, proposta_segue: dict, proposta_area_baixa: dict
) -> None:
    arquivo = tmp_path / "propostas.json"
    arquivo.write_text(json.dumps([proposta_segue, proposta_area_baixa]), encoding="utf-8")

    codigo = main([str(arquivo)])
    assert codigo == 0
    saida = capsys.readouterr().out
    assert "---" in saida
    assert "P-001" in saida
    assert "P-002" in saida


def test_cli_stdin(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture, proposta_segue: dict) -> None:
    import io

    monkeypatch.setattr("sys.stdin", io.StringIO(json.dumps(proposta_segue)))
    codigo = main(["-"])
    assert codigo == 0
    saida = capsys.readouterr().out
    assert "P-001" in saida


def test_cli_sem_argumentos_dispara_erro(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("sys.stdin.isatty", lambda: True)
    with pytest.raises(SystemExit):
        main([])
