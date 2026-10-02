"""Testes do servidor MCP."""

from __future__ import annotations

import json
import pytest

from triagem_proposta.models import Parecer
from triagem_proposta.server import main, mcp, triar_proposta_tool


def test_server_triar_proposta_dict(proposta_segue: dict) -> None:
    res = triar_proposta_tool(proposta_segue)
    assert res["parecer"] == Parecer.SEGUE.value
    assert res["id"] == "P-001"


def test_server_triar_proposta_string_json(proposta_segue: dict) -> None:
    res = triar_proposta_tool(json.dumps(proposta_segue))
    assert res["parecer"] == Parecer.SEGUE.value
    assert res["id"] == "P-001"


def test_server_triar_proposta_tipo_invalido() -> None:
    with pytest.raises(TypeError, match="deve ser um objeto JSON"):
        triar_proposta_tool([1, 2, 3])  # type: ignore[arg-type]


def test_server_main(monkeypatch: pytest.MonkeyPatch) -> None:
    chamado = False

    def mock_run(transport: str = "stdio") -> None:
        nonlocal chamado
        chamado = True
        assert transport == "stdio"

    monkeypatch.setattr(mcp, "run", mock_run)
    main([])
    assert chamado is True


def test_server_main_sse(monkeypatch: pytest.MonkeyPatch) -> None:
    chamado = False

    def mock_run(transport: str = "stdio") -> None:
        nonlocal chamado
        chamado = True
        assert transport == "sse"

    monkeypatch.setattr(mcp, "run", mock_run)
    main(["--transport", "sse", "--host", "0.0.0.0", "--port", "8888"])
    assert chamado is True
    assert mcp.settings.host == "0.0.0.0"
    assert mcp.settings.port == 8888
