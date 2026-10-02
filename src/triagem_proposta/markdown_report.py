"""Geração de resumo Markdown pronto para card de tarefa."""

from __future__ import annotations

from triagem_proposta.models import Parecer, ResultadoTriagem


def gerar_markdown(resultado: ResultadoTriagem) -> str:
    """Monta o card Markdown: título, parecer, motivos e pendências."""
    titulo = f"Triagem da proposta {resultado.proposta_id}"
    linhas = [
        f"# {titulo}",
        "",
        f"**Parecer:** {resultado.parecer.value}",
        "",
        "## Motivos",
    ]

    if resultado.motivos:
        for motivo in resultado.motivos:
            linhas.append(
                f"- **{motivo.regra}** ({motivo.parecer.value}): {motivo.descricao}"
            )
    else:
        linhas.append("- Nenhum motivo de restrição. Proposta apta a seguir.")

    linhas.extend(["", "## Pendências"])

    if resultado.parecer is Parecer.SEGUE:
        linhas.append("- Nenhuma pendência.")
    elif resultado.parecer is Parecer.RECUSADA:
        linhas.append("- Proposta recusada — não há pendências de análise.")
        if resultado.pendencias:
            linhas.append("- Motivos de revisão também identificados (não prevalecem):")
            for pendencia in resultado.pendencias:
                linhas.append(f"  - {pendencia}")
    else:
        if resultado.pendencias:
            for pendencia in resultado.pendencias:
                linhas.append(f"- [ ] {pendencia}")
        else:
            linhas.append("- [ ] Revisar proposta manualmente.")

    linhas.append("")
    return "\n".join(linhas)
