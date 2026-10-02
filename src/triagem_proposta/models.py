"""Modelos de domínio da triagem de propostas."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import Any


class Parecer(str, Enum):
    """Pareceres válidos da triagem."""

    SEGUE = "SEGUE"
    RECUSADA = "RECUSADA"
    REVISAO_HUMANA = "REVISÃO HUMANA"


# Campos obrigatórios. `alerta_desmatamento` pode ser null (sem alerta),
# mas a chave precisa existir no JSON de entrada.
CAMPOS_OBRIGATORIOS: tuple[str, ...] = (
    "id",
    "area_degradada_ha",
    "area_matricula_ha",
    "area_car_ha",
    "alerta_desmatamento",
    "situacao_car",
    "situacao_cadastral",
)

DATA_CORTE_DESMATAMENTO = date(2020, 1, 1)
LIMITE_AREA_DEGRADADA_HA = 100.0
LIMITE_DIVERGENCIA_AREA = 0.05  # 5% da área da matrícula


@dataclass(frozen=True, slots=True)
class Motivo:
    """Motivo identificado por uma regra."""

    regra: str
    parecer: Parecer
    descricao: str


@dataclass(frozen=True, slots=True)
class Proposta:
    """Proposta de crédito normalizada para avaliação."""

    id: str
    area_degradada_ha: float
    area_matricula_ha: float
    area_car_ha: float
    alerta_desmatamento: date | None
    situacao_car: str
    situacao_cadastral: str


@dataclass(frozen=True, slots=True)
class ResultadoTriagem:
    """Resultado completo da triagem."""

    proposta_id: str
    parecer: Parecer
    motivos: tuple[Motivo, ...] = field(default_factory=tuple)
    pendencias: tuple[str, ...] = field(default_factory=tuple)
    campos_ausentes: tuple[str, ...] = field(default_factory=tuple)

    @property
    def aprovada(self) -> bool:
        return self.parecer is Parecer.SEGUE


def parse_alerta_desmatamento(valor: Any) -> date | None:
    """Converte alerta de desmatamento (str ISO / date / None) em date | None."""
    if valor is None:
        return None
    if isinstance(valor, date):
        return valor
    if isinstance(valor, str):
        texto = valor.strip()
        if not texto or texto.lower() in {"nenhum", "null", "none", "n/a"}:
            return None
        # Aceita YYYY-MM-DD e DD/MM/YYYY
        if "/" in texto:
            dia, mes, ano = texto.split("/")
            return date(int(ano), int(mes), int(dia))
        return date.fromisoformat(texto)
    raise TypeError(f"Tipo inválido para alerta_desmatamento: {type(valor)!r}")
