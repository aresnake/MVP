from __future__ import annotations

import json
import os
import socket
import subprocess
import time

import httpx
import pytest


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture()
def http_server():
    port = _free_port()
    env = os.environ.copy()
    env["MVP_TRANSPORT"] = "http"
    env["MVP_HTTP_PORT"] = str(port)
    proc = subprocess.Popen(
        ["python", "-m", "mvp.server"],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    base_url = f"http://127.0.0.1:{port}"

    # wait for server up
    client = httpx.Client(base_url=base_url, timeout=5)
    for _ in range(30):
        try:
            resp = client.get("/health")
            if resp.status_code == 200:
                break
        except Exception:
            time.sleep(0.2)
    else:
        proc.terminate()
        proc.wait(timeout=5)
        raise RuntimeError("Server did not start")

    yield base_url
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait(timeout=5)


def test_http_transport_smoke(http_server):
    base = http_server
    client = httpx.Client(base_url=base, timeout=5)

    health = client.get("/health").json()
    assert health["ok"] is True
    assert health["result"]["name"] == "mvp"

    catalog = client.get("/tools").json()
    assert catalog["ok"] is True
    assert any(t["name"] == "system.tools_catalog" for t in catalog["result"]["tools"])

    denied = client.post("/call", json={"name": "runtime.probe", "params": {}}).json()
    assert denied["ok"] is False
    assert denied["error"]["code"] == "contract_required"

    create = client.post(
        "/contract/create",
        json={
            "host_profile": "codex_stdio",
            "runtime_profile": "none",
            "capabilities": ["DATA_ONLY"],
            "tool_allowlist": ["runtime.probe", "system.tools_catalog"],
        },
    ).json()
    assert create["ok"] is True

    after = client.post("/call", json={"name": "system.tools_catalog", "params": {}}).json()
    assert after["ok"] is True
