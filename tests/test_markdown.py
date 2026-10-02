"""Testes do gerador de Markdown para card de tarefa."""

from __future__ import annotations

from triagem_proposta.engine import triar_proposta
from triagem_proposta.markdown_report import gerar_markdown
from triagem_proposta.models import Motivo, Parecer, ResultadoTriagem


def test_markdown_segue(proposta_segue):
    md = gerar_markdown(triar_proposta(proposta_segue))
    assert "# Triagem da proposta P-001" in md
    assert "**Parecer:** SEGUE" in md
    assert "## Motivos" in md
    assert "## Pendências" in md
    assert "Nenhuma pendência" in md


def test_markdown_recusada_com_conflito(proposta_conflito):
    md = gerar_markdown(triar_proposta(proposta_conflito))
    assert "**Parecer:** RECUSADA" in md
    assert "**R2**" in md
    assert "**R3**" in md
    assert "não há pendências de análise" in md


def test_markdown_revisao_com_checkboxes(proposta_divergencia_area):
    md = gerar_markdown(triar_proposta(proposta_divergencia_area))
    assert "**Parecer:** REVISÃO HUMANA" in md
    assert "- [ ]" in md
    assert "[R5]" in md


def test_markdown_estrutura_minima():
    resultado = ResultadoTriagem(
        proposta_id="X-1",
        parecer=Parecer.REVISAO_HUMANA,
        motivos=(Motivo("R6", Parecer.REVISAO_HUMANA, "Campo obrigatório ausente: id"),),
        pendencias=("[R6] Campo obrigatório ausente: id",),
    )
    md = gerar_markdown(resultado)
    assert md.startswith("# Triagem da proposta X-1\n")
    assert "Campo obrigatório ausente: id" in md
