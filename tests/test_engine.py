"""Testes da engine: acumulação de motivos e resolução de conflitos."""

from __future__ import annotations

from triagem_proposta.engine import resolver_parecer, triar_e_formatar, triar_proposta
from triagem_proposta.models import Motivo, Parecer


def test_p001_segue(proposta_segue):
    resultado = triar_proposta(proposta_segue)
    assert resultado.parecer is Parecer.SEGUE
    assert resultado.motivos == ()
    assert resultado.pendencias == ()


def test_p002_recusada_por_area(proposta_area_baixa):
    resultado = triar_proposta(proposta_area_baixa)
    assert resultado.parecer is Parecer.RECUSADA
    assert any(m.regra == "R1" for m in resultado.motivos)


def test_p003_revisao_por_divergencia(proposta_divergencia_area):
    resultado = triar_proposta(proposta_divergencia_area)
    assert resultado.parecer is Parecer.REVISAO_HUMANA
    assert any(m.regra == "R5" for m in resultado.motivos)
    assert len(resultado.pendencias) >= 1


def test_p004_conflito_prevalece_recusada(proposta_conflito):
    """RECUSADA (R2) + REVISÃO (R3) → parecer final RECUSADA, ambos listados."""
    resultado = triar_proposta(proposta_conflito)
    assert resultado.parecer is Parecer.RECUSADA
    regras = {m.regra for m in resultado.motivos}
    assert "R2" in regras
    assert "R3" in regras
    assert any(m.parecer is Parecer.RECUSADA for m in resultado.motivos)
    assert any(m.parecer is Parecer.REVISAO_HUMANA for m in resultado.motivos)


def test_p005_revisao_campo_ausente_e_cadastral(proposta_campos_ausentes):
    resultado = triar_proposta(proposta_campos_ausentes)
    assert resultado.parecer is Parecer.REVISAO_HUMANA
    assert "area_matricula_ha" in resultado.campos_ausentes
    regras = {m.regra for m in resultado.motivos}
    assert "R6" in regras
    assert "R4" in regras  # situação cadastral presente e irregular


def test_p005_com_matricula_tambem_dispara_r4():
    """Quando todos os campos existem, R4 também dispara."""
    dados = {
        "id": "P-005b",
        "area_degradada_ha": 300,
        "area_matricula_ha": 700,
        "area_car_ha": 700,
        "alerta_desmatamento": None,
        "situacao_car": "Ativo",
        "situacao_cadastral": "Pendente de regularização",
    }
    resultado = triar_proposta(dados)
    assert resultado.parecer is Parecer.REVISAO_HUMANA
    assert any(m.regra == "R4" for m in resultado.motivos)


def test_acumula_multiplas_recusas():
    dados = {
        "id": "P-MULTI",
        "area_degradada_ha": 50,
        "area_matricula_ha": 1000,
        "area_car_ha": 1000,
        "alerta_desmatamento": "2021-06-01",
        "situacao_car": "Cancelado",
        "situacao_cadastral": "Regular",
    }
    resultado = triar_proposta(dados)
    assert resultado.parecer is Parecer.RECUSADA
    regras = {m.regra for m in resultado.motivos}
    assert regras >= {"R1", "R2", "R3"}


def test_resolver_parecer_prioridades():
    assert resolver_parecer([]) is Parecer.SEGUE
    assert (
        resolver_parecer(
            [Motivo("R3", Parecer.REVISAO_HUMANA, "x")]
        )
        is Parecer.REVISAO_HUMANA
    )
    assert (
        resolver_parecer(
            [
                Motivo("R1", Parecer.RECUSADA, "a"),
                Motivo("R3", Parecer.REVISAO_HUMANA, "b"),
            ]
        )
        is Parecer.RECUSADA
    )


def test_triar_e_formatar_payload(proposta_segue):
    payload = triar_e_formatar(proposta_segue)
    assert payload["parecer"] == "SEGUE"
    assert payload["id"] == "P-001"
    assert "markdown" in payload
    assert "# Triagem da proposta P-001" in payload["markdown"]


def test_alerta_em_formato_brasileiro():
    dados = {
        "id": "P-BR",
        "area_degradada_ha": 200,
        "area_matricula_ha": 1000,
        "area_car_ha": 1000,
        "alerta_desmatamento": "15/03/2023",
        "situacao_car": "Ativo",
        "situacao_cadastral": "Regular",
    }
    resultado = triar_proposta(dados)
    assert resultado.parecer is Parecer.RECUSADA
    assert any(m.regra == "R2" for m in resultado.motivos)
