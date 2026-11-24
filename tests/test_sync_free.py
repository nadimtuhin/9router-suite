import io
import json
import sqlite3
import subprocess
import urllib.error

import pytest


class _Resp(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()


def _http_error(code):
    return urllib.error.HTTPError("http://x/v1/models", code, "err", {}, None)


@pytest.fixture
def no_sleep(sync_free, monkeypatch):
    monkeypatch.setattr(sync_free.time, "sleep", lambda s: None)


@pytest.mark.parametrize("code", [429, 503])
def test_catalog_fetch_retries_transient_http_errors(sync_free, monkeypatch, no_sleep, code):
    calls = []
    body = json.dumps({"data": [{"id": "cl/z-ai/glm-5.2:free"}]}).encode()

    def fake_urlopen(req, timeout=None):
        calls.append(req)
        if len(calls) == 1:
            raise _http_error(code)
        return _Resp(body)

    captured = {}
    monkeypatch.setattr(sync_free.urllib.request, "urlopen", fake_urlopen)
    monkeypatch.setattr(sync_free, "update_combo_in_db", lambda db, name, m: captured.setdefault(name, m))

    assert sync_free.sync_cline_free("db", "http://x") == ["cl/z-ai/glm-5.2:free"]
    assert len(calls) == 2


def test_catalog_fetch_does_not_retry_client_errors(sync_free, monkeypatch, no_sleep):
    calls = []

    def fake_urlopen(req, timeout=None):
        calls.append(req)
        raise _http_error(404)

    monkeypatch.setattr(sync_free.urllib.request, "urlopen", fake_urlopen)
    assert sync_free.sync_cline_free("db", "http://x") == []
    assert len(calls) == 1


def test_opencode_models_call_has_timeout(sync_free, tmp_path, monkeypatch):
    binary = tmp_path / "opencode"
    binary.write_text("#!/bin/sh\n")
    binary.chmod(0o755)
    seen = {}

    def fake_check_output(cmd, **kwargs):
        seen.update(kwargs)
        raise subprocess.TimeoutExpired(cmd, kwargs.get("timeout"))

    monkeypatch.setattr(sync_free.subprocess, "check_output", fake_check_output)
    assert sync_free.sync_opencode_free(str(tmp_path / "db"), str(binary)) == []
    assert seen.get("timeout"), "opencode models must be called with a timeout"


def test_db_connection_closed_on_error(sync_free, tmp_path, monkeypatch):
    db_path = tmp_path / "data.sqlite"
    db_path.write_bytes(b"")  # exists, but has no 'combos' table -> execute fails
    opened = []
    real_connect = sqlite3.connect

    class Tracking:
        def __init__(self, path):
            self.conn = real_connect(path)
            self.closed = False
            opened.append(self)

        def __getattr__(self, name):
            return getattr(self.conn, name)

        def close(self):
            self.closed = True
            self.conn.close()

    monkeypatch.setattr(sync_free.sqlite3, "connect", Tracking)
    assert sync_free.update_combo_in_db(str(db_path), "cline-free", ["a"]) is False
    assert opened and opened[0].closed
