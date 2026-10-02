"""Regras de negócio determinísticas da triagem (R1–R6).

Cada regra retorna zero ou mais Motivo. A engine acumula todos os motivos
antes de resolver o parecer final — não há short-circuit.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any

from triagem_proposta.models import (
    CAMPOS_OBRIGATORIOS,
    DATA_CORTE_DESMATAMENTO,
    LIMITE_AREA_DEGRADADA_HA,
    LIMITE_DIVERGENCIA_AREA,
    Motivo,
    Parecer,
    Proposta,
    parse_alerta_desmatamento,
)

RegraFn = Callable[[Proposta], list[Motivo]]


def campos_ausentes(dados: Mapping[str, Any]) -> list[str]:
    """Retorna campos obrigatórios ausentes ou com valor vazio (exceto alerta)."""
    ausentes: list[str] = []
    for campo in CAMPOS_OBRIGATORIOS:
        if campo not in dados:
            ausentes.append(campo)
            continue
        valor = dados[campo]
        if campo == "alerta_desmatamento":
            # null é válido (sem alerta); ausência da chave já foi tratada
            continue
        if valor is None or (isinstance(valor, str) and not valor.strip()):
            ausentes.append(campo)
    return ausentes


def aplicar_r6(dados: Mapping[str, Any]) -> list[Motivo]:
    """R6: campo obrigatório ausente → REVISÃO HUMANA."""
    faltantes = campos_ausentes(dados)
    return [
        Motivo(
            regra="R6",
            parecer=Parecer.REVISAO_HUMANA,
            descricao=f"Campo obrigatório ausente: {campo}",
        )
        for campo in faltantes
    ]


def aplicar_r1(proposta: Proposta) -> list[Motivo]:
    """R1: área degradada < 100 ha → RECUSADA."""
    if proposta.area_degradada_ha < LIMITE_AREA_DEGRADADA_HA:
        return [
            Motivo(
                regra="R1",
                parecer=Parecer.RECUSADA,
                descricao=(
                    f"Área degradada ({proposta.area_degradada_ha:g} ha) "
                    f"abaixo do mínimo de {LIMITE_AREA_DEGRADADA_HA:g} ha"
                ),
            )
        ]
    return []


def aplicar_r2(proposta: Proposta) -> list[Motivo]:
    """R2: alerta de desmatamento após 01/01/2020 → RECUSADA."""
    alerta = proposta.alerta_desmatamento
    if alerta is not None and alerta > DATA_CORTE_DESMATAMENTO:
        return [
            Motivo(
                regra="R2",
                parecer=Parecer.RECUSADA,
                descricao=(
                    f"Alerta de desmatamento em {alerta.isoformat()} "
                    f"(após {DATA_CORTE_DESMATAMENTO.isoformat()})"
                ),
            )
        ]
    return []


def aplicar_r3(proposta: Proposta) -> list[Motivo]:
    """R3: CAR Pendente → REVISÃO; Cancelado/Suspenso → RECUSADA; Ativo → ok."""
    situacao = proposta.situacao_car.strip()
    situacao_norm = situacao.casefold()

    if situacao_norm == "pendente":
        return [
            Motivo(
                regra="R3",
                parecer=Parecer.REVISAO_HUMANA,
                descricao=f'Situação do CAR "{situacao}" requer revisão humana',
            )
        ]
    if situacao_norm in {"cancelado", "suspenso"}:
        return [
            Motivo(
                regra="R3",
                parecer=Parecer.RECUSADA,
                descricao=f'Situação do CAR "{situacao}" impede a continuidade',
            )
        ]
    if situacao_norm != "ativo":
        return [
            Motivo(
                regra="R3",
                parecer=Parecer.REVISAO_HUMANA,
                descricao=(
                    f'Situação do CAR "{situacao}" não reconhecida '
                    '(esperado: Ativo, Pendente, Cancelado ou Suspenso)'
                ),
            )
        ]
    return []


def aplicar_r4(proposta: Proposta) -> list[Motivo]:
    """R4: situação cadastral diferente de Regular → REVISÃO HUMANA."""
    situacao = proposta.situacao_cadastral.strip()
    if situacao.casefold() != "regular":
        return [
            Motivo(
                regra="R4",
                parecer=Parecer.REVISAO_HUMANA,
                descricao=(
                    f'Situação cadastral "{situacao}" diferente de "Regular"'
                ),
            )
        ]
    return []


def aplicar_r5(proposta: Proposta) -> list[Motivo]:
    """R5: |matrícula − CAR| > 5% da matrícula → REVISÃO HUMANA.

    Diferença de exatamente 5% NÃO dispara a regra (somente maior que).
    """
    if proposta.area_matricula_ha <= 0:
        return [
            Motivo(
                regra="R5",
                parecer=Parecer.REVISAO_HUMANA,
                descricao=(
                    f"Área da matrícula inválida ({proposta.area_matricula_ha:g} ha); "
                    "impossível calcular divergência com o CAR"
                ),
            )
        ]

    diferenca = abs(proposta.area_matricula_ha - proposta.area_car_ha)
    limite = proposta.area_matricula_ha * LIMITE_DIVERGENCIA_AREA
    percentual = (diferenca / proposta.area_matricula_ha) * 100

    if diferenca > limite:
        return [
            Motivo(
                regra="R5",
                parecer=Parecer.REVISAO_HUMANA,
                descricao=(
                    f"Divergência entre matrícula ({proposta.area_matricula_ha:g} ha) "
                    f"e CAR ({proposta.area_car_ha:g} ha) de {percentual:.2f}% "
                    f"(limite: {LIMITE_DIVERGENCIA_AREA * 100:.0f}%)"
                ),
            )
        ]
    return []


REGRAS_PROPOSTA: tuple[RegraFn, ...] = (
    aplicar_r1,
    aplicar_r2,
    aplicar_r3,
    aplicar_r4,
    aplicar_r5,
)


def construir_proposta(dados: Mapping[str, Any]) -> Proposta:
    """Monta Proposta a partir de um mapping já validado quanto a campos."""
    return Proposta(
        id=str(dados["id"]).strip(),
        area_degradada_ha=float(dados["area_degradada_ha"]),
        area_matricula_ha=float(dados["area_matricula_ha"]),
        area_car_ha=float(dados["area_car_ha"]),
        alerta_desmatamento=parse_alerta_desmatamento(dados["alerta_desmatamento"]),
        situacao_car=str(dados["situacao_car"]).strip(),
        situacao_cadastral=str(dados["situacao_cadastral"]).strip(),
    )
