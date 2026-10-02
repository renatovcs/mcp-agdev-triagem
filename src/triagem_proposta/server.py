"""Servidor MCP leve que expõe a triagem de propostas como tool."""

from __future__ import annotations

import json
from typing import Any

from mcp.server.fastmcp import FastMCP

from triagem_proposta.engine import triar_e_formatar

mcp = FastMCP(
    name="triagem-proposta",
    instructions=(
        "Triagem determinística de propostas de crédito rural da AgDev. "
        "Use a tool triar_proposta com o JSON da proposta. "
        "As regras de negócio são aplicadas em código, não por inferência do modelo."
    ),
)


@mcp.tool(
    name="triar_proposta",
    description=(
        "Aplica as regras R1–R6 de forma determinística sobre uma proposta de crédito "
        "e retorna parecer (SEGUE | RECUSADA | REVISÃO HUMANA), motivos e resumo Markdown."
    ),
)
def triar_proposta_tool(proposta: dict[str, Any] | str) -> dict[str, Any]:
    """Recebe JSON (objeto ou string) e devolve o resultado da triagem.

    Campos esperados: id, area_degradada_ha, area_matricula_ha, area_car_ha,
    alerta_desmatamento, situacao_car, situacao_cadastral.
    """
    if isinstance(proposta, str):
        dados = json.loads(proposta)
    else:
        dados = proposta
    if not isinstance(dados, dict):
        raise TypeError("proposta deve ser um objeto JSON (dict)")
    return triar_e_formatar(dados)


def main() -> None:
    """Entrypoint do servidor MCP via stdio (Claude Desktop / Claude Code)."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
