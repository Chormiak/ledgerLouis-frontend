"""Chat do dashboard: conversa com o Gemini (API do Google) e repassa a resposta em streaming (SSE).
O Gemini só enxerga as ferramentas do servidor MCP do LedgerLouis (chamadas aqui dentro, sem subprocesso):
sem terminal, sem arquivos.
"""

import asyncio
import json
import uuid
from collections.abc import Iterator

from django.conf import settings
from django.http import HttpResponse, JsonResponse, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from google import genai
from google.genai import types

MAX_MESSAGE = 4000
MAX_ROUNDS = 8  # idas e voltas modelo <-> ferramentas por mensagem

CHAT_RULES = """Você está no painel de chat do LedgerLouis, ao lado do dashboard do Erick. Responda em português,
de forma curta e direta, em texto simples (sem tabelas). Siga as instruções do servidor MCP do LedgerLouis.
Quando falar de uma ação, grupo, proposta ou da carteira, use show_on_screen para abri-la no dashboard.
Para mudar carteira ou perfil, use propose_holding_change / propose_profile_change e diga que a sugestão
aparece como cartão para ele aplicar ou recusar: você nunca altera nada sozinho."""

# shortcut: histórico só em memória (some ao reiniciar o backend); guardar no banco se isso incomodar.
_histories: dict[str, list[types.Content]] = {}


def _mcp():
    from ledgerlouis.interfaces.mcp_server import mcp  # importa tarde: o módulo chama django.setup()

    return mcp


async def _list_tools() -> list[types.Tool]:
    from fastmcp import Client

    async with Client(_mcp()) as c:
        decls = [
            types.FunctionDeclaration(name=t.name, description=t.description, parameters_json_schema=t.input_schema)
            for t in await c.list_tools()
        ]
    return [types.Tool(function_declarations=decls)]


async def _call_tool(name: str, args: dict) -> dict:
    from fastmcp import Client

    async with Client(_mcp()) as c:
        r = await c.call_tool(name, args, raise_on_error=False)
    if r.is_error:
        return {"error": " ".join(getattr(b, "text", "") for b in r.content)}
    return {"result": r.structured_content if r.structured_content is not None else r.data}


def sse(event: dict) -> str:
    return f"data: {json.dumps(event, ensure_ascii=False)}\n\n"


def run_chat(message: str, session_id: str) -> Iterator[str]:
    yield sse({"type": "session", "session_id": session_id})
    if not settings.GEMINI_API_KEY:
        yield sse({"type": "done", "is_error": True, "error": "Defina GEMINI_API_KEY no .env do backend."})
        return
    history = _histories.setdefault(session_id, [])
    sent = len(history)
    history.append(types.Content(role="user", parts=[types.Part(text=message)]))
    try:
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        config = types.GenerateContentConfig(
            system_instruction=f"{_mcp().instructions}\n\n{CHAT_RULES}",
            tools=asyncio.run(_list_tools()),
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
        )
        for _ in range(MAX_ROUNDS):
            parts: list[types.Part] = []
            for chunk in client.models.generate_content_stream(model=settings.GEMINI_CHAT_MODEL, contents=history, config=config):
                for part in (chunk.candidates[0].content.parts or []) if chunk.candidates and chunk.candidates[0].content else []:
                    parts.append(part)
                    if part.text and not part.thought:
                        yield sse({"type": "text", "text": part.text})
            if not parts:
                break
            history.append(types.Content(role="model", parts=parts))
            calls = [p.function_call for p in parts if p.function_call]
            if not calls:
                break
            answers = []
            for fc in calls:
                yield sse({"type": "tool", "name": fc.name})
                answers.append(types.Part.from_function_response(name=fc.name, response=asyncio.run(_call_tool(fc.name, dict(fc.args or {})))))
            history.append(types.Content(role="user", parts=answers))
        else:
            yield sse({"type": "warning", "text": "Parei depois de muitas chamadas de ferramenta; peça de novo se faltou algo."})
    except Exception as e:  # erro de rede, chave, cota...: o chat mostra em vez de quebrar o stream
        del history[sent:]  # volta ao estado anterior para a próxima mensagem não herdar uma volta quebrada
        yield sse({"type": "done", "is_error": True, "error": f"Gemini: {str(e)[:300]}"})
        return
    yield sse({"type": "done", "is_error": False, "error": None})


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
    try:
        session_id = str(uuid.UUID(str(body.get("session_id"))))
    except ValueError:
        session_id = str(uuid.uuid4())
    response = StreamingHttpResponse(run_chat(message.strip(), session_id), content_type="text/event-stream")
    response["Cache-Control"] = "no-cache"
    response["X-Accel-Buffering"] = "no"
    return response
