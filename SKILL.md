---
name: triagem-proposta
description: >-
  Triagem determinística de propostas de crédito rural da AgDev. Recebe JSON
  (área degradada, matrícula, CAR, alerta de desmatamento, situações) e devolve
  parecer SEGUE, RECUSADA ou REVISÃO HUMANA com motivos e card Markdown.
  Use when the user asks to triar, analisar, validar ou dar parecer em proposta
  de crédito, pastagem degradada, CAR, SICAR, PRODES ou triagem-proposta.
---

# Skill: triagem-proposta

## Quando usar

Acione esta skill quando o usuário pedir para:

- Triar / analisar / validar uma **proposta de crédito** rural da AgDev
- Emitir **parecer** (SEGUE, RECUSADA, REVISÃO HUMANA)
- Conferir **CAR**, **alerta de desmatamento**, **área degradada** ou **situação cadastral**
- Gerar um **card Markdown** de tarefa a partir do resultado

Não use para política de crédito real fora deste fluxo — as regras são fictícias e vivem em código.

## Como usar

### 1. Preferir a tool MCP (determinística)

Chame a tool `triar_proposta` do servidor MCP `triagem-proposta`.

- **Endpoint em Nuvem (Claude Web / Remote):** `https://mcp-triagem.anotae.app.br/mcp` (transporte Streamable HTTP, sem autenticação para testes).
- **Endpoint Local (stdio):** via CLI ou Claude Desktop local.

JSON de entrada esperado:

```json
{
  "id": "P-001",
  "area_degradada_ha": 850,
  "area_matricula_ha": 1200,
  "area_car_ha": 1190,
  "alerta_desmatamento": null,
  "situacao_car": "Ativo",
  "situacao_cadastral": "Regular"
}
```

`alerta_desmatamento` aceita `null`, `YYYY-MM-DD` ou `DD/MM/YYYY`.

### 2. Sem MCP disponível

Execute no shell do projeto (com o pacote instalado):

```bash
python -m triagem_proposta.cli --json '{"id":"P-001",...}'
```

Ou importe:

```python
from triagem_proposta import triar_proposta
resultado = triar_proposta(proposta_dict)
```

### 3. O que NÃO fazer

- **Não** reimplementar as regras R1–R6 por inferência do modelo
- **Não** alterar o parecer retornado pelo código
- **Não** omitir motivos — sempre apresente a lista completa

## Saída esperada

Apresente ao usuário:

1. O **parecer** final
2. A lista de **motivos** (regra + descrição)
3. O campo **`markdown`** pronto para virar card de tarefa
4. Se houver **pendências**, destaque-as como checklist

## Resolução de conflitos (lembrete)

Se o código retornar motivos de RECUSADA e REVISÃO HUMANA juntos, o parecer final já será **RECUSADA**. Explique isso ao analista sem alterar o resultado.

## Exemplos de gatilho

| Usuário diz | Ação |
|-------------|------|
| "Triar a proposta P-004" | Chamar `triar_proposta` com o JSON |
| "Essa proposta pode seguir?" | Mesmo fluxo; responder com o parecer |
| "Gera o card dessa triagem" | Usar o `markdown` da tool |
