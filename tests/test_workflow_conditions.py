"""Job conditions of .github/workflows/app.yml: offboarding only by hand with confirmation,
deploys only from the default branch, registry credentials only on the push path, identity
tokens only in the request jobs."""

from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
WORKFLOW = yaml.safe_load((REPO / ".github/workflows/app.yml").read_text())
JOBS = WORKFLOW["jobs"]


def _if(job):
    return " ".join(str(JOBS[job].get("if", "")).split())


def test_build_and_deploy_never_run_for_offboard():
    assert _if("build") == "inputs.action == 'deploy'"
    assert "inputs.action == 'deploy'" in _if("deploy")


def test_deploy_only_from_the_default_branch_on_push_or_dispatch():
    cond = _if("deploy")
    assert "needs.validate.outputs.deploy_branch == 'true'" in cond
    assert "(github.event_name == 'push' || github.event_name == 'workflow_dispatch')" in cond
    assert "pull_request" not in cond


def test_offboard_only_by_hand_from_the_default_branch_with_confirmation():
    cond = _if("offboard")
    assert "inputs.action == 'offboard'" in cond
    assert "github.event_name == 'workflow_dispatch'" in cond and "push" not in cond
    assert "needs.validate.outputs.deploy_branch == 'true'" in cond
    steps = JOBS["offboard"]["steps"]
    assert steps[0]["name"] == "Confirmation" and '"$CONFIRM" != "$APP"' in steps[0]["run"]
    assert steps[1]["env"]["ACTION"] == "offboard" and "SECRETS_JSON" not in steps[1]["env"]


def test_registry_login_only_on_the_push_path():
    push = " ".join(JOBS["build"]["env"]["PUSH"].split())
    assert "needs.validate.outputs.deploy_branch == 'true'" in push
    assert "(github.event_name == 'push' || github.event_name == 'workflow_dispatch')" in push
    logins = [s for s in JOBS["build"]["steps"] if "docker/login-action" in str(s.get("uses", ""))]
    assert logins and all(s.get("if") == "env.PUSH == 'true'" for s in logins)


def test_permissions_per_job():
    assert WORKFLOW["permissions"] == {}
    # The policy bundle is public: validate needs no packages.
    assert JOBS["validate"]["permissions"] == {"contents": "read"}
    assert not [s for s in JOBS["validate"]["steps"] if "docker/login-action" in str(s.get("uses", ""))]
    assert JOBS["build"]["permissions"] == {"contents": "read", "packages": "write"}
    for job in ("deploy", "offboard"):
        assert JOBS[job]["permissions"] == {"contents": "read", "id-token": "write"}
        assert JOBS[job]["environment"] == "${{ inputs.environment }}"


def test_secrets_only_in_the_deploy_request():
    for name, job in JOBS.items():
        text = yaml.safe_dump(job)
        if name == "deploy":
            assert "toJSON(secrets)" in text
        else:
            assert "toJSON(secrets)" not in text, name


def test_third_party_actions_are_pinned_by_commit():
    for job in JOBS.values():
        for step in job.get("steps", []):
            uses = step.get("uses")
            if uses:
                ref = uses.split("@", 1)[1]
                assert len(ref) == 40 and all(c in "0123456789abcdef" for c in ref), uses
