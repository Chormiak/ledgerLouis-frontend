import json
from pathlib import Path

import pytest

FAKE = str(Path(__file__).parent.parent / "fixtures" / "fake_claude.py")
J = {"content_type": "application/json"}


def events(response) -> list[dict]:
    body = b"".join(response.streaming_content).decode()
    return [json.loads(chunk.removeprefix("data: ")) for chunk in body.strip().split("\n\n")]


@pytest.fixture
def fake(settings, tmp_path, monkeypatch):
    settings.CLAUDE_BIN = FAKE
    args = tmp_path / "args.json"
    monkeypatch.setenv("FAKE_CLAUDE_ARGS", str(args))
    return args


def test_chat_streams_text_tools_and_locks_down_claude(client, fake):
    r = client.post("/api/chat", {"message": "como está minha carteira?"}, **J)
    assert r["Content-Type"] == "text/event-stream"
    evs = events(r)
    assert evs[0]["type"] == "session"
    assert {"type": "tool", "name": "get_portfolio"} in evs
    assert "".join(e["text"] for e in evs if e["type"] == "text") == "Sua carteira está concentrada."
    assert evs[-1] == {"type": "done", "is_error": False, "error": None}

    argv = json.loads(fake.read_text())
    assert argv[argv.index("--tools") + 1] == ""  # sem Bash, Edit, Read...
    assert argv[argv.index("--permission-mode") + 1] == "dontAsk"
    assert argv[argv.index("--allowedTools") + 1] == "mcp__ledgerlouis"
    assert "--strict-mcp-config" in argv and "--session-id" in argv


def test_followup_resumes_same_session(client, fake):
    sid = events(client.post("/api/chat", {"message": "oi"}, **J))[0]["session_id"]
    events(client.post("/api/chat", {"message": "e agora?", "session_id": sid}, **J))
    argv = json.loads(fake.read_text())
    assert argv[argv.index("--resume") + 1] == sid


def test_missing_claude_is_a_clear_error(client, settings):
    settings.CLAUDE_BIN = "/nao/existe/claude"
    evs = events(client.post("/api/chat", {"message": "oi"}, **J))
    assert evs[-1]["is_error"] and "Claude Code não encontrado" in evs[-1]["error"]


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
