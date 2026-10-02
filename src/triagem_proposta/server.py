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


# Rota informativa na raiz para checagem rápida no navegador
from starlette.responses import JSONResponse
from starlette.routing import Route

mcp._custom_starlette_routes.append(
    Route(
        "/",
        lambda req: JSONResponse({
            "status": "online",
            "server": "triagem-proposta-mcp",
            "endpoint": "/mcp",
            "protocol": "streamable-http",
        }),
        methods=["GET"],
    )
)


def main(argv: list[str] | None = None) -> None:
    """Entrypoint do servidor MCP (suporta stdio, sse e streamable-http)."""
    import argparse
    import os

    parser = argparse.ArgumentParser(description="Servidor MCP triagem-proposta")
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse", "streamable-http"],
        default=os.getenv("MCP_TRANSPORT", "stdio"),
        help="Transporte MCP (stdio para local, sse para contêiner/remoto)",
    )
    parser.add_argument(
        "--host",
        default=os.getenv("MCP_HOST", "0.0.0.0"),
        help="Host/IP de escuta para SSE/HTTP (padrão: 0.0.0.0)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.getenv("MCP_PORT", "8000")),
        help="Porta de escuta para SSE/HTTP (padrão: 8000)",
    )

    args = parser.parse_args(argv)

    if args.transport in {"sse", "streamable-http"}:
        from mcp.server.transport_security import TransportSecuritySettings

        mcp.settings.host = args.host
        mcp.settings.port = args.port
        # Permite tráfego vindo de domínios externos e proxies reversos (Cloudflare, Nginx, etc.)
        mcp.settings.transport_security = TransportSecuritySettings(
            enable_dns_rebinding_protection=False
        )

    mcp.run(transport=args.transport)


if __name__ == "__main__":
    main()
