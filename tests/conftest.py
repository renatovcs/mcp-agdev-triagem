"""Fixtures compartilhadas dos testes."""

from __future__ import annotations

import pytest


@pytest.fixture
def proposta_segue() -> dict:
    """P-001: proposta limpa que deve seguir."""
    return {
        "id": "P-001",
        "area_degradada_ha": 850,
        "area_matricula_ha": 1200,
        "area_car_ha": 1190,
        "alerta_desmatamento": None,
        "situacao_car": "Ativo",
        "situacao_cadastral": "Regular",
    }


@pytest.fixture
def proposta_area_baixa() -> dict:
    """P-002: área degradada abaixo do mínimo."""
    return {
        "id": "P-002",
        "area_degradada_ha": 60,
        "area_matricula_ha": 300,
        "area_car_ha": 298,
        "alerta_desmatamento": None,
        "situacao_car": "Ativo",
        "situacao_cadastral": "Regular",
    }


@pytest.fixture
def proposta_divergencia_area() -> dict:
    """P-003: divergência matrícula/CAR > 5%."""
    return {
        "id": "P-003",
        "area_degradada_ha": 400,
        "area_matricula_ha": 900,
        "area_car_ha": 1000,
        "alerta_desmatamento": None,
        "situacao_car": "Ativo",
        "situacao_cadastral": "Regular",
    }


@pytest.fixture
def proposta_conflito() -> dict:
    """P-004: RECUSADA (alerta) + REVISÃO (CAR Pendente) → final RECUSADA."""
    return {
        "id": "P-004",
        "area_degradada_ha": 1500,
        "area_matricula_ha": 2000,
        "area_car_ha": 2010,
        "alerta_desmatamento": "2023-03-15",
        "situacao_car": "Pendente",
        "situacao_cadastral": "Regular",
    }


@pytest.fixture
def proposta_campos_ausentes() -> dict:
    """P-005: matrícula ausente + situação cadastral irregular."""
    return {
        "id": "P-005",
        "area_degradada_ha": 300,
        "area_car_ha": 700,
        "alerta_desmatamento": None,
        "situacao_car": "Ativo",
        "situacao_cadastral": "Pendente de regularização",
    }
