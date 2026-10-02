# Imagem base oficial Python (compatível com x86_64 e ARM64 / Oracle Ampere A1)
FROM python:3.12-slim

# Variáveis de ambiente
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    MCP_TRANSPORT=streamable-http \
    MCP_HOST=0.0.0.0 \
    MCP_PORT=8000

WORKDIR /app

# Cria usuário não-root para segurança
RUN groupadd -r appuser && useradd -r -g appuser -u 1000 appuser

# Copia os arquivos do projeto
COPY pyproject.toml README.md DESIGN.md SKILL.md ./
COPY src/ ./src/

# Instala o pacote (sem dependências de dev)
RUN pip install --no-cache-dir .

# Garante permissões adequadas
RUN chown -R appuser:appuser /app
USER appuser

# Porta padrão de escuta para transporte SSE/HTTP
EXPOSE 8000

# Executa o servidor MCP (utiliza variáveis de ambiente MCP_TRANSPORT, MCP_HOST, MCP_PORT)
CMD ["python", "-m", "triagem_proposta.server"]
