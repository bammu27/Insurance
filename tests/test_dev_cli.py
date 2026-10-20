"""Tests for scripts/dev_cli.py.

Validates that CLI:
- Returns full JSON envelope on valid inputs.
- Fails when actor_role is supplied in payload.
- Fails when empty text is passed.
"""

import json
import subprocess
import sys


def run_cli(*args):
    cmd = [sys.executable, "scripts/dev_cli.py", *args]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    return proc.returncode, proc.stdout, proc.stderr


def test_cli_chat_success():
    code, stdout, stderr = run_cli("chat", "--user", "cust_a", "--json", '{"text":"hello"}')
    assert code == 0
    data = json.loads(stdout)
    assert data["status"] == "ok"
    assert "request_id" in data
    assert "latency_ms" in data
    assert len(data["citations"]) > 0


def test_cli_rejects_actor_role():
    code, stdout, stderr = run_cli("chat", "--user", "cust_a", "--json", '{"text":"hello","actor_role":"admin"}')
    assert code == 1
    data = json.loads(stdout)
    assert data["status"] == "error"
    assert "Validation failed" in data["message"]
    assert "Extra inputs are not permitted" in str(data["warnings"])


def test_cli_rejects_empty_text():
    code, stdout, stderr = run_cli("chat", "--user", "cust_a", "--json", '{"text":""}')
    assert code == 1
    data = json.loads(stdout)
    assert data["status"] == "error"
    assert "at least 1 character" in data["message"]


def test_cli_policies():
    code, stdout, stderr = run_cli("policies", "--user", "cust_a")
    assert code == 0
    data = json.loads(stdout)
    assert data["status"] == "ok"
    assert len(data["policies"]) == 2
