# Triagem de Propostas — AgDev
# Skill Claude + servidor MCP Python para triagem determinística de crédito rural.

## Pré-requisitos

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

## Servidor MCP (Claude Desktop e Claude Code)

O servidor expõe a ferramenta determinística `triar_proposta`. A integração funciona no **Claude Desktop** e no **Claude Code (CLI)**.

> **Nota sobre o Claude Web (claude.ai no navegador):** O Claude Web não tem acesso direto a processos locais via `stdio`. Para usá-lo na nuvem, utilize a CLI local para gerar o parecer ou envie a proposta em texto.

---

### Opção 1: Configuração no Claude Desktop (Passo a Passo)

#### 1. Abra o arquivo de configuração
- **Pelo próprio aplicativo:** Abra o Claude Desktop, clique no menu superior esquerdo (ou ícone de engrenagem) ➔ **Settings** ➔ **Developer** ➔ clique no botão **Edit Config**.
- **Ou pelo Explorador de Arquivos:**
  - **Windows:** Pressione `Win + R`, digite `%APPDATA%\Claude` e abra o arquivo `claude_desktop_config.json` com o Bloco de Notas ou VS Code.
  - **macOS:** Abra `~/Library/Application Support/Claude/claude_desktop_config.json`.

#### 2. Cole a configuração
Adicione o servidor dentro da chave `"mcpServers"`. 

> ⚠️ **Atenção no Windows (Barras no caminho):** No formato JSON, barras invertidas (`\`) causam erro de sintaxe. Use barras normais (`/`) ou barras duplas (`\\`).

Exemplo pronto (ajuste para o seu caminho onde o projeto está salvo, ex: `D:/agdev`):

```json
{
  "mcpServers": {
    "triagem-proposta": {
      "command": "D:/agdev/.venv/Scripts/python.exe",
      "args": ["-m", "triagem_proposta.server"]
    }
  }
}
```

*(No macOS/Linux, substitua o comando por `/caminho/para/agdev/.venv/bin/python`).*

#### 3. Reinicie o Claude Desktop
Feche completamente o aplicativo e abra-o novamente.

#### 4. Como conferir se deu certo (Validação Visual)
1. No canto inferior direito da caixa de mensagem de um novo chat, procure pelo ícone de **ferramentas/martelo** (🔨).
2. Clique nele e verifique se a ferramenta `triar_proposta` está listada e habilitada.
3. Teste enviando uma mensagem simples:
   > *"Por favor, trie a proposta P-001 usando a ferramenta triar_proposta: `{"id": "P-001", "area_degradada_ha": 850, "area_matricula_ha": 1200, "area_car_ha": 1190, "alerta_desmatamento": null, "situacao_car": "Ativo", "situacao_cadastral": "Regular"}`"*

---

### Opção 2: Configuração no Claude Code (CLI)

Se você utiliza o **Claude Code** no terminal, não precisa editar arquivos JSON manualmente. Basta rodar o comando:

```bash
# No diretório do projeto:
claude mcp add triagem-proposta -- .venv/Scripts/python.exe -m triagem_proposta.server
```

Para verificar se foi reconhecido:
```bash
claude mcp list
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

Para rodar o servidor MCP encapsulado em contêiner com suporte a rede (transporte SSE na porta 8000):

```bash
docker compose up -d --build
```

O endpoint SSE fica disponível em `http://localhost:8000/sse` (ou no IP público da sua VPS / Cloud).

## Documentação

- [SKILL.md](SKILL.md) — quando usar a skill
- [DESIGN.md](DESIGN.md) — revisão humana, dados reais, versionamento e adoção
- [DEPLOY_ORACLE_CLOUD.md](doc/DEPLOY_ORACLE_CLOUD.md) — guia completo de deploy em contêiner na Oracle Cloud (OCI)
