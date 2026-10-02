"""CLI local para triar propostas sem subir o MCP (útil em smoke tests)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from triagem_proposta.engine import triar_e_formatar


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Triagem determinística de propostas de crédito (AgDev)."
    )
    parser.add_argument(
        "entrada",
        nargs="?",
        help="Caminho de um JSON (objeto ou lista) ou '-' para stdin",
    )
    parser.add_argument(
        "--json",
        dest="json_inline",
        help="JSON inline da proposta",
    )
    parser.add_argument(
        "--somente-parecer",
        action="store_true",
        help="Imprime apenas id e parecer",
    )
    args = parser.parse_args(argv)

    if args.json_inline:
        bruto = args.json_inline
    elif args.entrada == "-" or (args.entrada is None and not sys.stdin.isatty()):
        bruto = sys.stdin.read()
    elif args.entrada:
        bruto = Path(args.entrada).read_text(encoding="utf-8")
    else:
        parser.error("Informe um arquivo JSON, --json '{...}' ou pipe via stdin")

    dados = json.loads(bruto)
    itens = dados if isinstance(dados, list) else [dados]

    saidas = [triar_e_formatar(item) for item in itens]

    if args.somente_parecer:
        for s in saidas:
            print(f"{s['id']}\t{s['parecer']}")
        return 0

    if len(saidas) == 1:
        print(saidas[0]["markdown"])
        print("---")
        print(json.dumps(saidas[0], ensure_ascii=False, indent=2))
    else:
        for s in saidas:
            print(s["markdown"])
            print("---")
        print(json.dumps(saidas, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
