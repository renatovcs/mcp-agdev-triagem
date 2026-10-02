# Guia de Implantação do Servidor MCP na Oracle Cloud (OCI)

Este guia orienta o deploy do servidor MCP `triagem-proposta` em um contêiner Docker na sua instância de computação da **Oracle Cloud Infrastructure (OCI)**.

---

## 1. Pré-requisitos na sua Instância Oracle Cloud

- Instância Compute ativa (Ubuntu ou Oracle Linux, x86_64 ou ARM Ampere A1).
- **Docker** e **Docker Compose** instalados na máquina.

Se ainda não tiver o Docker instalado na instância:
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
newgrp docker
```

---

## 2. Clonar o Repositório e Subir o Contêiner

Acesse sua instância via SSH e execute:

```bash
# 1. Clone o seu repositório publicado
git clone <URL_DO_SEU_REPOSITORIO_GITHUB>
cd mcp-agdev-triagem  # ou o nome da sua pasta clonada

# 2. Suba o contêiner em segundo plano
docker compose up -d --build
```

Verifique se o contêiner está rodando:
```bash
docker ps
# Deve exibir o contêiner "triagem-mcp-server" com status UP na porta 0.0.0.0:8000->8000/tcp
```

Para ver os logs em tempo real:
```bash
docker logs -f triagem-mcp-server
```

---

## 3. Liberação de Portas na Oracle Cloud (Passo Importante ⚠️)

A Oracle Cloud possui **duas barreiras de segurança** para liberar portas externas. É necessário liberar em ambas:

### Camada A: Painel Web da Oracle Cloud (VCN Security List)

1. No console da OCI, acesse o menu de navegação ➔ **Networking** ➔ **Virtual Cloud Networks (VCN)**.
2. Clique na VCN da sua instância ➔ clique em **Security Lists** no menu lateral.
3. Clique em **Default Security List for...** ➔ botão **Add Ingress Rules**.
4. Preencha com os seguintes dados:
   - **Source CIDR:** `0.0.0.0/0` (ou o seu IP de internet para restringir o acesso)
   - **IP Protocol:** `TCP`
   - **Destination Port Range:** `8000`
   - **Description:** `MCP Server SSE (Triagem AgDev)`
5. Clique em **Add Ingress Rules**.

### Camada B: Firewall do Sistema Operacional da Instância (Linux)

No terminal SSH da sua máquina Oracle Cloud:

- **Se a instância for Oracle Linux:**
  ```bash
  sudo firewall-cmd --permanent --add-port=8000/tcp
  sudo firewall-cmd --reload
  ```

- **Se a instância for Ubuntu:**
  ```bash
  sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 8000 -j ACCEPT
  sudo netfilter-persistent save 2>/dev/null || true
  # Se usar UFW:
  sudo ufw allow 8000/tcp
  ```

---

## 4. Testar a Conexão Remota

No terminal da sua máquina local (ou via navegador), faça um teste rápido:

```bash
curl http://<IP_PUBLICO_ORACLE_CLOUD>:8000/sse
```
*Se a conexão abrir e aguardar eventos, o servidor está respondendo perfeitamente via Server-Sent Events (SSE)!*

---

## 5. Como conectar o Claude ao Servidor Remoto

### No Claude Desktop local

Como o Claude Desktop local espera comandos stdio, a forma recomendada e oficial pela Anthropic para conectar a um servidor SSE remoto é usando o wrapper `mcp-remote`:

No arquivo de configuração (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "triagem-proposta-oracle": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-remote",
        "http://<IP_PUBLICO_ORACLE_CLOUD>:8000/sse"
      ]
    }
  }
}
```

### No Claude Code (CLI)

```bash
claude mcp add triagem-proposta-oracle -- npx -y mcp-remote http://<IP_PUBLICO_ORACLE_CLOUD>:8000/sse
```

### Em outros clientes MCP (Cursor, OpenWebUI, LibreChat, etc.)
Configure o servidor MCP remoto diretamente fornecendo:
- **Type / Transport:** `SSE`
- **URL:** `http://<IP_PUBLICO_ORACLE_CLOUD>:8000/sse`
