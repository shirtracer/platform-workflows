"""The request step of .github/workflows/app.yml: the Python code is taken from the workflow
itself and run against a local token endpoint and deploy API."""

import json
import os
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[1]
SECRET = "app-secret-value-55aa"
TOKEN = "identity-token-value-77bb"


def request_code():
    workflow = yaml.safe_load((REPO / ".github/workflows/app.yml").read_text())
    run = workflow["jobs"]["deploy"]["steps"][0]["run"]
    assert workflow["jobs"]["offboard"]["steps"][1]["run"] == run  # one script for both
    return run.split("<<'PY'\n", 1)[1].rsplit("\nPY", 1)[0]


class Fake(BaseHTTPRequestHandler):
    answer = (200, [{"event": "progress", "message": "request verified"},
                    {"event": "result", "outcome": "accepted", "reason": "stub"}])
    received = []

    def do_GET(self):  # token endpoint
        assert self.headers["Authorization"] == "Bearer request-token"
        Fake.audience = self.path.split("audience=", 1)[1]
        self._send(200, json.dumps({"value": TOKEN}))

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        Fake.received.append((self.path, self.headers["Authorization"], body))
        status, payload = Fake.answer
        text = "".join(json.dumps(e) + "\n" for e in payload) if status == 200 else json.dumps(payload)
        self._send(status, text)

    def _send(self, status, text):
        data = text.encode()
        self.send_response(status)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *args):
        pass


@pytest.fixture
def fake():
    Fake.received = []
    server = ThreadingHTTPServer(("127.0.0.1", 0), Fake)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    yield "http://127.0.0.1:%d" % server.server_address[1]
    server.shutdown()


def run(fake, tmp_path, **env):
    base = {
        "PATH": os.environ["PATH"], "CONTROLLER_URL": fake, "APP": "apptest", "GITHUB_SHA": "a" * 40,
        "ACTIONS_ID_TOKEN_REQUEST_URL": fake + "/token?api-version=2.0", "ACTIONS_ID_TOKEN_REQUEST_TOKEN": "request-token",
        "GITHUB_STEP_SUMMARY": str(tmp_path / "summary.md"),
    }
    base.update(env)
    return subprocess.run([sys.executable, "-c", request_code()], env=base, capture_output=True, text=True, timeout=30)


def deploy_env(**extra):
    env = {"ACTION": "deploy", "IMAGE": "ghcr.io/svenm3/platform-apptest:sha-x@sha256:y", "POLICY_VERSION": "1.0.0-rc.1",
           "SECRET_NAMES": json.dumps(["EXAMPLE_API_KEY"]),
           "SECRETS_JSON": json.dumps({"EXAMPLE_API_KEY": SECRET, "OTHER": "not-sent", "github_token": "gh"})}
    env.update(extra)
    return env


def test_deploy_sends_only_named_secrets(fake, tmp_path):
    proc = run(fake, tmp_path, **deploy_env())
    assert proc.returncode == 0, proc.stdout + proc.stderr
    path, auth, body = Fake.received[0]
    assert path == "/v1/deploy" and auth == "Bearer " + TOKEN and Fake.audience == fake
    assert body["secrets"] == {"EXAMPLE_API_KEY": SECRET} and body["commit"] == "a" * 40
    assert "deploy apptest: accepted" in proc.stdout
    assert SECRET not in proc.stdout + proc.stderr
    assert all(line.startswith("::add-mask::") for line in proc.stdout.splitlines() if TOKEN in line)
    assert "accepted" in (tmp_path / "summary.md").read_text()


def test_bundled_secrets_of_personal_repositories(fake, tmp_path):
    bundle = json.dumps({"EXAMPLE_API_KEY": SECRET, "OTHER": "not-sent", "github_token": "gh"})
    proc = run(fake, tmp_path, **deploy_env(SECRETS_JSON=json.dumps({"PLATFORM_SECRETS": bundle, "github_token": "gh"})))
    assert proc.returncode == 0, proc.stdout + proc.stderr
    _, _, body = Fake.received[0]
    assert body["secrets"] == {"EXAMPLE_API_KEY": SECRET}
    # The value appears only in its mask command, which the runner hides.
    assert [line for line in proc.stdout.splitlines() if SECRET in line] == ["::add-mask::" + SECRET]


def test_direct_secrets_win_over_the_bundle(fake, tmp_path):
    bundle = json.dumps({"EXAMPLE_API_KEY": "from-the-bundle"})
    proc = run(fake, tmp_path, **deploy_env(SECRETS_JSON=json.dumps({"PLATFORM_SECRETS": bundle,
                                                                       "EXAMPLE_API_KEY": SECRET})))
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert Fake.received[0][2]["secrets"] == {"EXAMPLE_API_KEY": SECRET}


def test_broken_bundle_is_refused_without_printing_it(fake, tmp_path):
    proc = run(fake, tmp_path, **deploy_env(SECRETS_JSON=json.dumps({"PLATFORM_SECRETS": "not json " + SECRET})))
    assert proc.returncode == 1 and Fake.received == []
    assert SECRET not in proc.stdout + proc.stderr


def test_missing_secret_is_named_and_nothing_sent(fake, tmp_path):
    proc = run(fake, tmp_path, **deploy_env(SECRETS_JSON=json.dumps({})))
    assert proc.returncode == 1
    assert "EXAMPLE_API_KEY" in proc.stdout and Fake.received == []


def test_refusal_fails_the_job(fake, tmp_path):
    Fake.answer = (403, {"outcome": "refused", "reason": "only the default branch main may deploy"})
    try:
        proc = run(fake, tmp_path, **deploy_env())
    finally:
        Fake.answer = (200, [{"event": "result", "outcome": "accepted", "reason": "stub"}])
    assert proc.returncode == 1 and "refused — only the default branch" in proc.stdout


def test_offboard_sends_no_secrets(fake, tmp_path):
    proc = run(fake, tmp_path, ACTION="offboard", CONFIRM="apptest", SECRETS_JSON=json.dumps({"X": "y"}))
    assert proc.returncode == 0, proc.stdout + proc.stderr
    path, _, body = Fake.received[0]
    assert path == "/v1/offboard" and body == {"app": "apptest", "commit": "a" * 40, "confirm": "apptest"}


def test_unreachable_api_fails(tmp_path):
    proc = run("http://127.0.0.1:9", tmp_path, **deploy_env(ACTIONS_ID_TOKEN_REQUEST_URL="http://127.0.0.1:9/t?x=1"))
    assert proc.returncode != 0
