"""Testes unitários das regras individuais (R1–R6) e bordas."""

from __future__ import annotations

from datetime import date

import pytest

from triagem_proposta.models import Parecer, Proposta
from triagem_proposta.rules import (
    aplicar_r1,
    aplicar_r2,
    aplicar_r3,
    aplicar_r4,
    aplicar_r5,
    aplicar_r6,
    campos_ausentes,
)


def _base(**overrides) -> Proposta:
    dados = {
        "id": "T-000",
        "area_degradada_ha": 200.0,
        "area_matricula_ha": 1000.0,
        "area_car_ha": 1000.0,
        "alerta_desmatamento": None,
        "situacao_car": "Ativo",
        "situacao_cadastral": "Regular",
    }
    dados.update(overrides)
    return Proposta(**dados)


# --- R1 ---


def test_r1_abaixo_do_minimo_recusa():
    motivos = aplicar_r1(_base(area_degradada_ha=99.9))
    assert len(motivos) == 1
    assert motivos[0].regra == "R1"
    assert motivos[0].parecer is Parecer.RECUSADA


def test_r1_exatamente_100_ha_segue():
    assert aplicar_r1(_base(area_degradada_ha=100.0)) == []


def test_r1_acima_do_minimo_segue():
    assert aplicar_r1(_base(area_degradada_ha=850.0)) == []


# --- R2 ---


def test_r2_alerta_apos_corte_recusa():
    motivos = aplicar_r2(_base(alerta_desmatamento=date(2023, 3, 15)))
    assert motivos[0].parecer is Parecer.RECUSADA
    assert motivos[0].regra == "R2"


def test_r2_alerta_no_dia_do_corte_nao_recusa():
    """'Após 01/01/2020' é exclusivo — o próprio dia-corte não dispara."""
    assert aplicar_r2(_base(alerta_desmatamento=date(2020, 1, 1))) == []


def test_r2_alerta_antes_do_corte_segue():
    assert aplicar_r2(_base(alerta_desmatamento=date(2019, 12, 31))) == []


def test_r2_sem_alerta_segue():
    assert aplicar_r2(_base(alerta_desmatamento=None)) == []


# --- R3 ---


@pytest.mark.parametrize(
    "situacao,parecer_esperado",
    [
        ("Pendente", Parecer.REVISAO_HUMANA),
        ("pendente", Parecer.REVISAO_HUMANA),
        ("Cancelado", Parecer.RECUSADA),
        ("Suspenso", Parecer.RECUSADA),
        ("Ativo", None),
        ("ativo", None),
    ],
)
def test_r3_situacoes_car(situacao, parecer_esperado):
    motivos = aplicar_r3(_base(situacao_car=situacao))
    if parecer_esperado is None:
        assert motivos == []
    else:
        assert motivos[0].parecer is parecer_esperado
        assert motivos[0].regra == "R3"


def test_r3_situacao_desconhecida_revisao():
    motivos = aplicar_r3(_base(situacao_car="Em análise"))
    assert motivos[0].parecer is Parecer.REVISAO_HUMANA


# --- R4 ---


def test_r4_regular_segue():
    assert aplicar_r4(_base(situacao_cadastral="Regular")) == []


def test_r4_outra_situacao_revisao():
    motivos = aplicar_r4(_base(situacao_cadastral="Pendente de regularização"))
    assert motivos[0].parecer is Parecer.REVISAO_HUMANA
    assert motivos[0].regra == "R4"


# --- R5 (bordas críticas) ---


def test_r5_divergencia_maior_que_5_porcento():
    # |900 - 1000| / 900 = 11.11% > 5%
    motivos = aplicar_r5(_base(area_matricula_ha=900, area_car_ha=1000))
    assert motivos[0].parecer is Parecer.REVISAO_HUMANA
    assert motivos[0].regra == "R5"


def test_r5_divergencia_exatamente_5_porcento_nao_dispara():
    """Borda obrigatória: diferença == 5% NÃO dispara R5."""
    # 5% de 1000 = 50 → CAR = 950 ou 1050
    assert aplicar_r5(_base(area_matricula_ha=1000, area_car_ha=950)) == []
    assert aplicar_r5(_base(area_matricula_ha=1000, area_car_ha=1050)) == []


def test_r5_divergencia_logo_acima_de_5_porcento():
    # 50.01 / 1000 = 5.001% > 5%
    motivos = aplicar_r5(_base(area_matricula_ha=1000, area_car_ha=949.99))
    assert len(motivos) == 1
    assert motivos[0].regra == "R5"


def test_r5_areas_iguais_segue():
    assert aplicar_r5(_base(area_matricula_ha=1200, area_car_ha=1200)) == []


def test_r5_matricula_zero_revisao():
    motivos = aplicar_r5(_base(area_matricula_ha=0, area_car_ha=100))
    assert motivos[0].parecer is Parecer.REVISAO_HUMANA


# --- R6 ---


def test_r6_campo_ausente():
    dados = {
        "id": "P-005",
        "area_degradada_ha": 300,
        "area_car_ha": 700,
        "alerta_desmatamento": None,
        "situacao_car": "Ativo",
        "situacao_cadastral": "Regular",
    }
    motivos = aplicar_r6(dados)
    assert len(motivos) == 1
    assert motivos[0].regra == "R6"
    assert "area_matricula_ha" in motivos[0].descricao
    assert "area_matricula_ha" in campos_ausentes(dados)


def test_r6_alerta_null_nao_e_ausencia():
    dados = {
        "id": "P-001",
        "area_degradada_ha": 850,
        "area_matricula_ha": 1200,
        "area_car_ha": 1190,
        "alerta_desmatamento": None,
        "situacao_car": "Ativo",
        "situacao_cadastral": "Regular",
    }
    assert aplicar_r6(dados) == []
    assert campos_ausentes(dados) == []


def test_r6_multiplos_campos_ausentes():
    dados = {"id": "X"}
    faltantes = campos_ausentes(dados)
    assert "area_degradada_ha" in faltantes
    assert "situacao_car" in faltantes
    assert len(aplicar_r6(dados)) == len(faltantes)
