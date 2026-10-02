# Triagem de Propostas — AgDev
Skill Claude + servidor MCP Python para triagem determinística de crédito rural.

> 🌐 **Servidor MCP Online (Pronto para Uso em Teste):**  
> Um servidor MCP já está implantado e disponível na nuvem para avaliação imediata:  
> - **Endpoint:** `https://mcp-triagem.anotae.app.br/mcp`  
> - **Transporte:** **Streamable HTTP** (padrão recomendado pela Anthropic)  
> - **Autenticação:** **Sem autenticação (None)** *(aberto temporariamente para facilitar a avaliação deste teste prático)*  
> - **Healthcheck no navegador:** [https://mcp-triagem.anotae.app.br/](https://mcp-triagem.anotae.app.br/)

---

## Como Conectar no Claude Web (claude.ai)

A melhor prática para agentes no Claude Web é combinar uma **Skill (Instrução/Guardrail)** com um **Conector (MCP Tool)**:
- **O Conector (MCP Tool):** Executa o código Python determinístico na nuvem.
- **A Skill (Instrução):** Atua como governança, garantindo que o Claude **nunca alucine** regras de negócio e acione obrigatoriamente a ferramenta `triar_proposta`.

### Passo 1: Cadastrar o Conector MCP
1. Acesse [claude.ai](https://claude.ai) ➔ menu lateral **Customize** ➔ aba **Connectors**.
2. Clique no botão **`+ Add ▾`** ➔ **Add custom connector**.
3. Preencha:
   - **Name:** `triagem-proposta` (ou `triagem-agdev`)
   - **URL:** `https://mcp-triagem.anotae.app.br/mcp`
4. Ao avançar (ou em *Continue anyway*):
   - **Transport:** `Streamable HTTP`
   - **Authentication:** `None` (sem autenticação para testes)
5. Salve o conector.

### Passo 2: Cadastrar a Skill de Orquestração
1. Na mesma tela de **Customize**, clique na aba **Skills** ➔ botão **`+ Add ▾`** ➔ **Add skill**.
2. Preencha o nome: `triagem-proposta`.
3. No conteúdo da instrução da Skill (`SKILL.md`), cole a diretriz:
   ```text
   Você atua na triagem de propostas da AgDev. Quando o usuário fornecer dados de uma proposta (em JSON ou texto), acione obrigatoriamente a ferramenta triar_proposta. Não avalie as regras de negócio por conta própria. Aguarde o retorno da ferramenta e apresente ao usuário exatamente o resumo em Markdown gerado por ela, contendo título, parecer, motivos e pendências.
   ```
4. Salve e deixe a Skill ativada.

### Passo 3: Utilização pelo Analista
Abra um novo chat (`+ New`) e envie a proposta (em JSON ou texto livre):
> *"Trie a proposta P-001: `{"id": "P-001", "area_degradada_ha": 850, "area_matricula_ha": 1200, "area_car_ha": 1190, "alerta_desmatamento": null, "situacao_car": "Ativo", "situacao_cadastral": "Regular"}`"*

O Claude ativará a Skill, acionará a ferramenta remota e entregará o card Markdown com parecer determinístico.

---

## Pré-requisitos (Execução Local)

- Python 3.11+
- (opcional) [uv](https://github.com/astral-sh/uv) — acelera a instalação

## Instalação e execução (< 5 minutos)

```bash
# 1. Clone e entre no repositório
cd agdev

# 2. Crie o ambiente e instale (com extras de teste)
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS/Linux
# source .venv/bin/activate

pip install -e ".[dev]"

# 3. Rode os testes
pytest -q

# 4. Triagem rápida via CLI (exemplos do enunciado)
python -m triagem_proposta.cli examples/propostas.json --somente-parecer
```

Saída esperada:

```
P-001	SEGUE
P-002	RECUSADA
P-003	REVISÃO HUMANA
P-004	RECUSADA
P-005	REVISÃO HUMANA
```

### Uma proposta isolada

```bash
python -m triagem_proposta.cli --json "{\"id\":\"P-001\",\"area_degradada_ha\":850,\"area_matricula_ha\":1200,\"area_car_ha\":1190,\"alerta_desmatamento\":null,\"situacao_car\":\"Ativo\",\"situacao_cadastral\":\"Regular\"}"
```

---

## Configuração no Claude Desktop

### 1. Abra o arquivo de configuração
- **Pelo próprio aplicativo:** Abra o Claude Desktop, clique no menu superior esquerdo (ou ícone de engrenagem) ➔ **Settings** ➔ **Developer** ➔ clique no botão **Edit Config**.
- **Ou pelo Explorador de Arquivos:**
  - **Windows:** Pressione `Win + R`, digite `%APPDATA%\Claude` e abra o arquivo `claude_desktop_config.json` com o Bloco de Notas ou VS Code.
  - **macOS:** Abra `~/Library/Application Support/Claude/claude_desktop_config.json`.

### 2. Cole a configuração

**A) Conectando ao Servidor Online na Nuvem (Recomendado):**
```json
{
  "mcpServers": {
    "triagem-proposta": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-remote",
        "https://mcp-triagem.anotae.app.br/mcp"
      ]
    }
  }
}
```

**B) Ou rodando o Python Local:**
> ⚠️ **Atenção no Windows (Barras no caminho):** No formato JSON, use barras normais (`/`) ou barras duplas (`\\`).
```json
{
  "mcpServers": {
    "triagem-proposta-local": {
      "command": "D:/agdev/.venv/Scripts/python.exe",
      "args": ["-m", "triagem_proposta.server"]
    }
  }
}
```
*(No macOS/Linux, substitua o comando por `/caminho/para/agdev/.venv/bin/python`).*

### 3. Reinicie o Claude Desktop
Feche completamente o aplicativo e abra-o novamente.

### 4. Validação Visual
No canto inferior direito da caixa de mensagem de um novo chat, verifique o ícone de **ferramentas/martelo** (🔨) com a tool `triar_proposta`.

---

## Configuração no Claude Code (CLI)

No terminal:

```bash
# Conectando ao servidor em nuvem:
claude mcp add triagem-proposta -- npx -y mcp-remote https://mcp-triagem.anotae.app.br/mcp

# Ou conectando localmente:
claude mcp add triagem-proposta-local -- .venv/Scripts/python.exe -m triagem_proposta.server
```

---

## Estrutura

```
src/triagem_proposta/
  models.py           # Parecer, Proposta, Motivo
  rules.py            # R1–R6 isoladas (sem I/O)
  engine.py           # Orquestração + resolução de conflitos
  markdown_report.py  # Card Markdown
  server.py           # Servidor MCP (FastMCP / stdio)
  cli.py              # CLI local
tests/                # Casos negativos e de borda
examples/             # JSON do enunciado
```

## Regras (resumo)

| Regra | Critério | Parecer |
|-------|----------|---------|
| R1 | Área degradada < 100 ha | RECUSADA |
| R2 | Alerta de desmatamento após 01/01/2020 | RECUSADA |
| R3 | CAR Pendente / Cancelado / Suspenso | REVISÃO / RECUSADA |
| R4 | Situação cadastral ≠ Regular | REVISÃO HUMANA |
| R5 | \|matrícula − CAR\| > 5% da matrícula | REVISÃO HUMANA |
| R6 | Campo obrigatório ausente | REVISÃO HUMANA |

Conflito: **RECUSADA prevalece sobre REVISÃO HUMANA**; todos os motivos são listados.

## Execução via Docker (Contêiner)

Para rodar o servidor MCP encapsulado em contêiner com suporte a rede (**Streamable HTTP** na porta 8001/8000):

```bash
docker compose up -d --build
```

O endpoint MCP fica disponível em `http://localhost:8001/mcp` (e em produção via Cloudflare em `https://mcp-triagem.anotae.app.br/mcp`).  
Um endpoint informativo de healthcheck responde em `http://localhost:8001/`.

## Documentação

- [SKILL.md](SKILL.md) — quando usar a skill
- [DESIGN.md](DESIGN.md) — revisão humana, dados reais, versionamento e adoção
- [DEPLOY_ORACLE_CLOUD.md](doc/DEPLOY_ORACLE_CLOUD.md) — guia completo de deploy em contêiner na Oracle Cloud (OCI)
