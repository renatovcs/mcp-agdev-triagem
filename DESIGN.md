# DESIGN.md — triagem-proposta

*Máximo ~1 página. Regras e dados do teste são fictícios.*

## 1. Pontos de revisão humana

A revisão humana entra onde o código **não deve decidir sozinho**:

| Gatilho | Por quê humano |
|---------|----------------|
| CAR **Pendente** (R3) | Pode regularizar; não é recusa automática |
| Situação cadastral ≠ Regular (R4) | Exige checagem na Receita / documentos |
| Divergência área matrícula×CAR > 5% (R5) | Pode ser retificação, georreferenciamento ou erro de digitação |
| Campo obrigatório ausente (R6) | Falta dado — analista completa ou devolve ao proponente |
| CAR com status desconhecido | Fora do vocabulário esperado → escalar |

**RECUSADA** (área < 100 ha, desmatamento pós-2020, CAR cancelado/suspenso) é automática: o comitê não gasta tempo. Em conflito RECUSADA + REVISÃO, prevalece **RECUSADA**, mas **todos** os motivos ficam auditáveis no card.

## 2. Dados reais (SICAR, PRODES) e mitigação de erros

| Fonte | Uso | O que pode dar errado | Mitigação |
|-------|-----|----------------------|-----------|
| **SICAR** | `situacao_car`, `area_car_ha` | Lag de API, CAR sob judice, geometrias desatualizadas | Cache com TTL + timestamp no parecer; retry; se status incerto → REVISÃO |
| **PRODES / alertas** | `alerta_desmatamento` | Falso positivo, recorte municipal ≠ imóvel, fuso/datas | Cruzar com bounding box do CAR; guardar evidência (URL/ID do alerta); corte de data versionado |
| **Receita Federal** | `situacao_cadastral` | Homônimos, CNPJ matriz×filial | Validar documento + razão social; timeout → REVISÃO, nunca SEGUE por omissão |
| **Cartório / matrícula** | `area_matricula_ha` | OCR, unidade (m²×ha) | Validação de unidade na ingestão; R5 como rede de segurança |

O núcleo permanece **determinístico**: integrações alimentam o JSON; a skill não “interpreta” política.

## 3. Atualização e versionamento de regras

1. Constantes e funções em `rules.py` (ex.: limite 100 ha, data-corte 2020-01-01, 5%).
2. Mudança do comitê → PR com testes de borda atualizados + bump semântico (`1.1.0` se regra muda comportamento).
3. Tag Git + changelog; MCP/skill publicam a mesma versão.
4. Pareceres antigos guardam `regra` + texto — replay histórico possível.
5. Feature flag só se coexistirem duas políticas; default = uma versão ativa por ambiente.

## 4. Adoção por analistas não técnicos e Deploy em Nuvem

- **Acesso direto no Claude Web / Desktop:** O servidor MCP está implantado na Oracle Cloud em contêiner Docker, atrás do proxy Cloudflare com SSL: `https://mcp-triagem.anotae.app.br/mcp`.
- **Protocolo Moderno:** Utiliza **Streamable HTTP** (novo padrão oficial da especificação MCP), eliminando as limitações e a deprecação do SSE.
- **Autenticação (Teste vs Produção):** Para a avaliação deste teste prático, o servidor opera **sem autenticação (None)**, permitindo que os avaliadores conectem e testem de imediato no Claude sem necessidade de credenciais. Em produção real na AgDev, o endpoint é protegido via **OAuth 2.0** (integrado ao Cloudflare Zero Trust / IdP corporativo) ou token Bearer.
- **Operação pelo Analista:** No Claude, o analista cola a proposta em JSON ➔ a skill aciona a tool determinística ➔ saída em card Markdown padronizado com parecer, motivos e pendências.
- **Confiança:** As regras rodam **em código Python testado**, eliminando alucinações do modelo de linguagem.

## Uso de IA neste entregável

Claude/Cursor auxiliou no scaffold MCP, redação da documentação e geração da suíte de testes. A lógica R1–R6, a resolução de conflitos e os resultados esperados dos exemplos foram definidos e revisados por mim (engenheiro), com `pytest` como fonte de verdade.
