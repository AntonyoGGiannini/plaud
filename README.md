# Plaud MCP Server

MCP server para acessar gravações, transcrições e resumos do Plaud.ai via Claude.

## Deploy no Railway

### 1. Crie um novo projeto no Railway
- Acesse https://railway.app → New Project → Deploy from GitHub Repo
- Suba estes arquivos num repositório GitHub (ou use Railway CLI)

### 2. Configure a variável de ambiente
No painel do Railway → Variables → adicione:

```
PLAUD_TOKEN=bearer eyJ...seu_token_completo...
```

### 3. Exponha o serviço
- Settings → Networking → Generate Domain
- Anote a URL gerada (ex: `https://plaud-mcp-production.up.railway.app`)

### 4. Conecte ao Claude.ai
- Claude.ai → Settings → Integrations → Add MCP Server
- URL: `https://sua-url.railway.app/sse`

## Ferramentas disponíveis

| Tool | Descrição |
|------|-----------|
| `list_recordings` | Lista suas gravações (limit opcional) |
| `get_transcript` | Transcrição completa por file_id |
| `get_summary` | Resumo de IA por file_id |
| `get_recording_detail` | Metadados completos por file_id |

## Renovar o token
O token dura ~10 meses. Quando expirar:
1. Acesse https://web.plaud.ai
2. DevTools → Application → Local Storage → copie `tokenstr`
3. Atualize a variável `PLAUD_TOKEN` no Railway
