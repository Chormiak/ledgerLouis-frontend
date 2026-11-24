"""Chat do dashboard: roda o Claude Code (`claude -p`) no PC do Erick, pela assinatura dele, e repassa a resposta
em streaming (SSE). O Claude deste chat só tem as ferramentas MCP do LedgerLouis: sem terminal, sem arquivos.
"""

import json
import subprocess
import sys
import threading
import uuid
from collections.abc import Iterator
from pathlib import Path

from django.conf import settings
from django.http import HttpResponse, JsonResponse, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt

BACKEND_DIR = Path(__file__).resolve().parents[2]
TIMEOUT_S = 300
MAX_MESSAGE = 4000
TOOL_PREFIX = "mcp__ledgerlouis__"

CHAT_RULES = """Você está no painel de chat do LedgerLouis, ao lado do dashboard do Erick. Responda em português,
de forma curta e direta, em texto simples (sem tabelas). Siga as instruções do servidor MCP do LedgerLouis.
Quando falar de uma ação, grupo, proposta ou da carteira, use show_on_screen para abri-la no dashboard.
Para mudar carteira ou perfil, use propose_holding_change / propose_profile_change e diga que a sugestão
aparece como cartão para ele aplicar ou recusar: você nunca altera nada sozinho."""


def mcp_config() -> str:
    server = {
        "command": sys.executable,
        "args": ["-m", "ledgerlouis.interfaces.mcp_server"],
        "env": {"PYTHONPATH": str(BACKEND_DIR)},
    }
    return json.dumps({"mcpServers": {"ledgerlouis": server}})


def build_command(message: str, session_id: str, resume: bool) -> list[str]:
    cmd = [
        settings.CLAUDE_BIN, "-p", message,
        "--output-format", "stream-json", "--verbose", "--include-partial-messages",
        "--tools", "",  # nenhuma ferramenta interna (Bash, Edit, Read...): só o LedgerLouis
        "--strict-mcp-config", "--mcp-config", mcp_config(),
        "--allowedTools", "mcp__ledgerlouis",
        "--permission-mode", "dontAsk",  # o que não estiver liberado acima é negado, sem perguntar
        "--append-system-prompt", CHAT_RULES,
        "--resume" if resume else "--session-id", session_id,
    ]
    if settings.CLAUDE_CHAT_MODEL:
        cmd += ["--model", settings.CLAUDE_CHAT_MODEL]
    return cmd


def parse_line(line: str) -> list[dict]:
    """Uma linha do stream-json -> eventos simples para o frontend."""
    try:
        ev = json.loads(line)
    except json.JSONDecodeError:
        return []
    kind = ev.get("type")
    if kind == "stream_event":
        delta = ev.get("event", {}).get("delta", {})
        return [{"type": "text", "text": delta["text"]}] if delta.get("type") == "text_delta" else []
    if kind == "assistant":  # o texto já veio pelos deltas; daqui só as chamadas de ferramenta
        return [
            {"type": "tool", "name": b.get("name", "").removeprefix(TOOL_PREFIX)}
            for b in ev.get("message", {}).get("content", [])
            if b.get("type") == "tool_use"
        ]
    if kind == "system" and ev.get("subtype") == "init":
        servers = {s.get("name"): s.get("status") for s in ev.get("mcp_servers", [])}
        if servers.get("ledgerlouis") not in ("connected", "pending"):
            return [{"type": "warning", "text": "As ferramentas do LedgerLouis não conectaram; o Claude responde sem os seus dados."}]
        return []
    if kind == "result":
        return [{"type": "done", "is_error": bool(ev.get("is_error")), "error": ev.get("result") if ev.get("is_error") else None}]
    return []


def sse(event: dict) -> str:
    return f"data: {json.dumps(event, ensure_ascii=False)}\n\n"


def run_chat(message: str, session_id: str, resume: bool) -> Iterator[str]:
    yield sse({"type": "session", "session_id": session_id})
    try:
        proc = subprocess.Popen(
            build_command(message, session_id, resume),
            cwd=BACKEND_DIR, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, bufsize=1,
        )
    except FileNotFoundError:
        yield sse({"type": "done", "is_error": True, "error": "Claude Code não encontrado. Instale e faça login com `claude` no terminal."})
        return
    watchdog = threading.Timer(TIMEOUT_S, proc.kill)
    watchdog.start()
    finished = False
    try:
        for line in proc.stdout:
            for ev in parse_line(line):
                finished |= ev["type"] == "done"
                yield sse(ev)
        proc.wait()
        if not finished:
            err = (proc.stderr.read() or "").strip()[-500:] or f"o Claude Code saiu com código {proc.returncode}"
            yield sse({"type": "done", "is_error": True, "error": err})
    finally:
        watchdog.cancel()
        if proc.poll() is None:  # o navegador fechou a conexão no meio: não deixar o processo órfão
            proc.kill()


@csrf_exempt  # sem cookie de sessão; a proteção é o JSON obrigatório + a checagem de origem abaixo
def chat(request):
    if request.method != "POST":
        return HttpResponse(status=405)
    origin = request.headers.get("Origin")
    if origin and origin not in settings.CORS_ALLOWED_ORIGINS:
        return JsonResponse({"error": "origem não permitida"}, status=403)
    if request.content_type != "application/json":
        return JsonResponse({"error": "envie JSON"}, status=415)
    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "JSON inválido"}, status=400)
    message = body.get("message") if isinstance(body, dict) else None
    if not isinstance(message, str) or not message.strip() or len(message) > MAX_MESSAGE:
        return JsonResponse({"error": f"mensagem vazia ou com mais de {MAX_MESSAGE} caracteres"}, status=400)
    session_id, resume = body.get("session_id"), True
    try:
        session_id = str(uuid.UUID(str(session_id)))
    except ValueError:
        session_id, resume = str(uuid.uuid4()), False
    response = StreamingHttpResponse(run_chat(message.strip(), session_id, resume), content_type="text/event-stream")
    response["Cache-Control"] = "no-cache"
    response["X-Accel-Buffering"] = "no"
    return response
