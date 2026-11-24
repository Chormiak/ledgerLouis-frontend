import json
from types import SimpleNamespace

import pytest
from google.genai import types

from ledgerlouis.interfaces import chat as chat_mod

J = {"content_type": "application/json"}


def events(response) -> list[dict]:
    body = b"".join(response.streaming_content).decode()
    return [json.loads(chunk.removeprefix("data: ")) for chunk in body.strip().split("\n\n")]


def chunk(*parts):
    return SimpleNamespace(candidates=[SimpleNamespace(content=SimpleNamespace(parts=list(parts)))])


class FakeGemini:
    """Gemini falso: 1ª volta pede get_portfolio; 2ª responde em texto."""

    def __init__(self, **_):
        self.calls = []
        self.models = self

    def generate_content_stream(self, model, contents, config):
        self.calls.append(len(contents))
        if not any(p.function_response for c in contents for p in c.parts):
            yield chunk(types.Part(function_call=types.FunctionCall(name="get_portfolio", args={})))
        else:
            yield chunk(types.Part(text="Sua carteira "))
            yield chunk(types.Part(text="está concentrada."))


@pytest.fixture
def fake(settings, monkeypatch):
    settings.GEMINI_API_KEY = "k"
    called = []

    async def call_tool(name, args):
        called.append(name)
        return {"result": {"total": 0}}

    async def list_tools():
        return []

    monkeypatch.setattr(chat_mod.genai, "Client", FakeGemini)
    monkeypatch.setattr(chat_mod, "_call_tool", call_tool)
    monkeypatch.setattr(chat_mod, "_list_tools", list_tools)
    chat_mod._histories.clear()
    return called


def test_chat_streams_text_and_runs_tools(client, fake):
    r = client.post("/api/chat", {"message": "como está minha carteira?"}, **J)
    assert r["Content-Type"] == "text/event-stream"
    evs = events(r)
    assert evs[0]["type"] == "session"
    assert {"type": "tool", "name": "get_portfolio"} in evs
    assert fake == ["get_portfolio"]
    assert "".join(e["text"] for e in evs if e["type"] == "text") == "Sua carteira está concentrada."
    assert evs[-1] == {"type": "done", "is_error": False, "error": None}


def test_followup_keeps_history(client, fake):
    sid = events(client.post("/api/chat", {"message": "oi"}, **J))[0]["session_id"]
    events(client.post("/api/chat", {"message": "e agora?", "session_id": sid}, **J))
    assert len(chat_mod._histories[sid]) == 6  # 1ª volta: pergunta, ferramenta, resposta, texto; 2ª: pergunta, texto


def test_missing_key_is_a_clear_error(client, settings):
    settings.GEMINI_API_KEY = ""
    evs = events(client.post("/api/chat", {"message": "oi"}, **J))
    assert evs[-1]["is_error"] and "GEMINI_API_KEY" in evs[-1]["error"]


@pytest.mark.parametrize(
    "kwargs, status",
    [
        ({"data": {"message": "oi"}}, 415),  # formulário de outro site
        ({"data": {"message": ""}, **J}, 400),
        ({"data": {"message": "x" * 5000}, **J}, 400),
        ({"data": {"message": "oi"}, "HTTP_ORIGIN": "https://evil.example", **J}, 403),
    ],
)
def test_rejects_bad_requests(client, fake, kwargs, status):
    data = kwargs.pop("data")
    assert client.post("/api/chat", data, **kwargs).status_code == status
