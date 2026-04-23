import os
import json
import httpx
from mcp.server.fastmcp import FastMCP

# --- Config ---
PLAUD_TOKEN = os.environ.get("PLAUD_TOKEN", "")
PLAUD_API = "https://api.plaud.ai"

mcp = FastMCP("plaud", host="0.0.0.0", stateless_http=True)

def headers():
    return {
        "Authorization": PLAUD_TOKEN,
        "Content-Type": "application/json",
    }

# --- Tools ---

@mcp.tool()
def list_recordings(limit: int = 20) -> str:
    """Lista as gravações do Plaud. Retorna id, nome, duração e data de criação."""
    url = f"{PLAUD_API}/file/simple/web"
    params = {"page": 1, "page_size": limit}
    with httpx.Client(timeout=15) as client:
        r = client.get(url, headers=headers(), params=params)
        r.raise_for_status()
        data = r.json()

    files = data.get("data", data) if isinstance(data, dict) else data
    if isinstance(files, dict):
        files = files.get("list", files.get("files", []))

    result = []
    for f in files:
        result.append({
            "id": f.get("id"),
            "name": f.get("filename") or f.get("name") or "sem nome",
            "duration": f.get("duration_display") or f"{round(f.get('duration_ms', 0) / 60000, 1)} min",
            "created_at": f.get("created_at") or f.get("create_time"),
            "has_transcript": bool(f.get("has_transcription") or f.get("trans_result")),
            "has_summary": bool(f.get("has_summary") or f.get("summary")),
        })

    return json.dumps(result, ensure_ascii=False, indent=2)


@mcp.tool()
def get_transcript(file_id: str) -> str:
    """Retorna a transcrição completa de uma gravação pelo seu ID."""
    url = f"{PLAUD_API}/file/detail/{file_id}"
    with httpx.Client(timeout=20) as client:
        r = client.get(url, headers=headers())
        r.raise_for_status()
        data = r.json()

    file_data = data.get("data", data)

    # Try to extract transcript
    trans = file_data.get("trans_result") or {}
    segments = trans.get("segments", [])

    if not segments:
        return "Transcrição não disponível para esta gravação."

    lines = []
    for seg in segments:
        speaker = seg.get("speaker") or seg.get("spk") or "?"
        text = seg.get("text", "").strip()
        start = seg.get("start_time") or seg.get("start") or ""
        if start:
            start_str = f"[{int(float(start))//60:02d}:{int(float(start))%60:02d}] "
        else:
            start_str = ""
        lines.append(f"{start_str}{speaker}: {text}")

    return "\n".join(lines)


@mcp.tool()
def get_summary(file_id: str) -> str:
    """Retorna o resumo de IA gerado pelo Plaud para uma gravação."""
    url = f"{PLAUD_API}/file/detail/{file_id}"
    with httpx.Client(timeout=20) as client:
        r = client.get(url, headers=headers())
        r.raise_for_status()
        data = r.json()

    file_data = data.get("data", data)

    summary = (
        file_data.get("summary")
        or file_data.get("ai_summary")
        or file_data.get("note")
    )

    if not summary:
        return "Resumo não disponível para esta gravação."

    if isinstance(summary, dict):
        return json.dumps(summary, ensure_ascii=False, indent=2)

    return str(summary)


@mcp.tool()
def get_recording_detail(file_id: str) -> str:
    """Retorna todos os metadados de uma gravação (nome, duração, falantes, tags etc)."""
    url = f"{PLAUD_API}/file/detail/{file_id}"
    with httpx.Client(timeout=20) as client:
        r = client.get(url, headers=headers())
        r.raise_for_status()
        data = r.json()

    file_data = data.get("data", data)

    # Return clean metadata without raw transcript blob
    meta = {k: v for k, v in file_data.items() if k not in ("trans_result", "summary", "ai_summary")}
    return json.dumps(meta, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    app = mcp.streamable_http_app()
    uvicorn.run(app, host="0.0.0.0", port=port)
