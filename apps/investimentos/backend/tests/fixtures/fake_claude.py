#!/usr/bin/env python3
"""Claude Code falso para testes: grava os argumentos e imprime um stream-json típico."""
import json
import os
import sys

with open(os.environ["FAKE_CLAUDE_ARGS"], "w") as f:
    json.dump(sys.argv[1:], f)
events = [
    {"type": "system", "subtype": "init", "session_id": "x", "mcp_servers": [{"name": "ledgerlouis", "status": "connected"}]},
    {"type": "assistant", "message": {"content": [{"type": "tool_use", "name": "mcp__ledgerlouis__get_portfolio", "input": {}}]}},
    {"type": "stream_event", "event": {"type": "content_block_delta", "delta": {"type": "text_delta", "text": "Sua carteira "}}},
    {"type": "stream_event", "event": {"type": "content_block_delta", "delta": {"type": "text_delta", "text": "está concentrada."}}},
    {"type": "assistant", "message": {"content": [{"type": "text", "text": "Sua carteira está concentrada."}]}},
    {"type": "result", "subtype": "success", "is_error": False, "result": "Sua carteira está concentrada.", "session_id": "x"},
]
for e in events:
    print(json.dumps(e), flush=True)
