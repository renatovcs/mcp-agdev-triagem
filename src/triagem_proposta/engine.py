"""Engine de triagem: orquestra regras e resolve conflitos de parecer."""

from __future__ import annotations

from typing import Any, Mapping

from triagem_proposta.markdown_report import gerar_markdown
from triagem_proposta.models import Motivo, Parecer, ResultadoTriagem
from triagem_proposta.rules import (
    aplicar_r1,
    aplicar_r2,
    aplicar_r3,
    aplicar_r4,
    aplicar_r5,
    aplicar_r6,
    campos_ausentes,
    construir_proposta,
)


def resolver_parecer(motivos: list[Motivo]) -> Parecer:
    """Resolve o parecer final.

    Prioridade: RECUSADA > REVISÃO HUMANA > SEGUE.
    Se RECUSADA e REVISÃO HUMANA coexistirem, prevalece RECUSADA.
    """
    if not motivos:
        return Parecer.SEGUE

    pareceres = {m.parecer for m in motivos}
    if Parecer.RECUSADA in pareceres:
        return Parecer.RECUSADA
    if Parecer.REVISAO_HUMANA in pareceres:
        return Parecer.REVISAO_HUMANA
    return Parecer.SEGUE


def _pendencias_de(motivos: list[Motivo]) -> tuple[str, ...]:
    """Extrai pendências acionáveis a partir dos motivos de revisão."""
    return tuple(
        f"[{m.regra}] {m.descricao}"
        for m in motivos
        if m.parecer is Parecer.REVISAO_HUMANA
    )


def _ok(ausentes: set[str], *campos: str) -> bool:
    return all(campo not in ausentes for campo in campos)


def triar_proposta(dados: Mapping[str, Any]) -> ResultadoTriagem:
    """Aplica R1–R6 acumulando todos os motivos e resolve o parecer final.

    Continua o processamento mesmo após encontrar RECUSADA ou REVISÃO HUMANA.
    Regras com dependência ausente são puladas (R6 já identifica o campo).
    """
    motivos: list[Motivo] = []
    ausentes_lista = campos_ausentes(dados)
    ausentes = set(ausentes_lista)

    motivos.extend(aplicar_r6(dados))

    # Defaults só para montar o objeto; regras dependentes de campo ausente não rodam.
    try:
        proposta = construir_proposta(
            {
                "id": dados.get("id") or "DESCONHECIDO",
                "area_degradada_ha": dados.get("area_degradada_ha", 0),
                "area_matricula_ha": dados.get("area_matricula_ha", 0),
                "area_car_ha": dados.get("area_car_ha", 0),
                "alerta_desmatamento": (
                    dados["alerta_desmatamento"] if "alerta_desmatamento" in dados else None
                ),
                "situacao_car": dados.get("situacao_car") or "Ativo",
                "situacao_cadastral": dados.get("situacao_cadastral") or "Regular",
            }
        )
    except (TypeError, ValueError):
        proposta = None

    if proposta is not None:
        if _ok(ausentes, "area_degradada_ha"):
            motivos.extend(aplicar_r1(proposta))
        if "alerta_desmatamento" not in ausentes:
            motivos.extend(aplicar_r2(proposta))
        if _ok(ausentes, "situacao_car"):
            motivos.extend(aplicar_r3(proposta))
        if _ok(ausentes, "situacao_cadastral"):
            motivos.extend(aplicar_r4(proposta))
        if _ok(ausentes, "area_matricula_ha", "area_car_ha"):
            motivos.extend(aplicar_r5(proposta))

    proposta_id = str(dados.get("id") or "DESCONHECIDO").strip() or "DESCONHECIDO"
    return ResultadoTriagem(
        proposta_id=proposta_id,
        parecer=resolver_parecer(motivos),
        motivos=tuple(motivos),
        pendencias=_pendencias_de(motivos),
        campos_ausentes=tuple(ausentes_lista),
    )


def triar_e_formatar(dados: Mapping[str, Any]) -> dict[str, Any]:
    """Triagem + payload estruturado com resumo Markdown (para MCP/API)."""
    resultado = triar_proposta(dados)
    return {
        "id": resultado.proposta_id,
        "parecer": resultado.parecer.value,
        "motivos": [
            {
                "regra": m.regra,
                "parecer": m.parecer.value,
                "descricao": m.descricao,
            }
            for m in resultado.motivos
        ],
        "pendencias": list(resultado.pendencias),
        "campos_ausentes": list(resultado.campos_ausentes),
        "markdown": gerar_markdown(resultado),
    }
