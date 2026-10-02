# Guia de Implantação do Servidor MCP na Oracle Cloud (OCI)

Este guia documenta o deploy em produção do servidor MCP `triagem-proposta` em contêiner Docker na **Oracle Cloud Infrastructure (OCI)** com proxy reverso e SSL via **Cloudflare**.

---

## 1. Topologia da Arquitetura

```
[Cliente: Claude Web / Desktop] 
         │
         ▼ (HTTPS / SSL)
[Cloudflare Proxy] (mcp-triagem.anotae.app.br)
         │ (Redirecionamento para porta 8001)
         ▼
[Oracle Cloud VM (Ubuntu aarch64 / ARM Ampere)]
         │
         ▼ (Porta 8001 -> 8000)
[Docker Container: triagem-mcp-server]
   └─ FastMCP Python (Streamable HTTP /mcp)
```

- **URL de Produção:** `https://mcp-triagem.anotae.app.br/mcp`
- **Healthcheck:** `https://mcp-triagem.anotae.app.br/`
- **Protocolo:** **Streamable HTTP** (novo padrão oficial da Anthropic)
- **Autenticação:** **None** (aberto para validação e testes práticos)

---

## 2. Pré-requisitos na Instância Oracle Cloud

- Instância Compute ativa (Ubuntu ou Oracle Linux, x86_64 ou ARM Ampere A1).
- **Docker** e **Docker Compose** instalados.

```bash
# Instalação rápida do Docker se necessário
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
newgrp docker
```

---

## 3. Subir o Contêiner com Docker Compose

No terminal da máquina:

```bash
# 1. Clone o repositório
git clone https://github.com/renatovcs/mcp-agdev-triagem.git
cd mcp-agdev-triagem

# 2. Suba o contêiner em segundo plano
docker compose up -d --build
```

O `docker-compose.yml` mapeia a porta externa `8001` para a porta interna `8000` do contêiner e inicializa o transporte `streamable-http`.

Verifique os logs:
```bash
docker logs -f triagem-mcp-server
```

---

## 4. Liberação de Portas e Firewall (Passo Crítico)

Para permitir que a Cloudflare se conecte à porta 8001:

### A) Firewall do Sistema Operacional (Ubuntu)
```bash
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 8001 -j ACCEPT
sudo netfilter-persistent save 2>/dev/null || true
```

### B) Console Web da Oracle Cloud (VCN Ingress Rules)
1. **Networking** ➔ **Virtual Cloud Networks (VCN)** ➔ clique na sua VCN.
2. Acesse **Security Lists** ➔ **Default Security List for...**.
3. Adicione uma **Ingress Rule**:
   - **Source CIDR:** `0.0.0.0/0`
   - **IP Protocol:** `TCP`
   - **Destination Port Range:** `8001`

---

## 5. Como Conectar no Claude

### A) Claude Web (claude.ai)
1. Acesse **Customize** ➔ **Connectors** ➔ **Add custom connector**.
2. Preencha a URL: `https://mcp-triagem.anotae.app.br/mcp`.
3. Selecione:
   - **Transport:** `Streamable HTTP`
   - **Authentication:** `None`

### B) Claude Desktop
Em `claude_desktop_config.json`:
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

### C) Claude Code (CLI)
```bash
claude mcp add triagem-proposta -- npx -y mcp-remote https://mcp-triagem.anotae.app.br/mcp
```
