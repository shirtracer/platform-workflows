"""The app-team documentation: every rule of the pinned policy bundle is documented and nothing
else, links resolve, nothing points into the private admin repository, nothing looks like a
credential. The rule test reads the pulled bundle from POLICY_BUNDLE_DIR (set by CI)."""

import os
import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
PAGES = sorted([REPO / "README.md", REPO / "RELEASING.md", *(REPO / "docs").glob("*.md")])
LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
CREDENTIAL = re.compile(
    r"-----BEGIN [A-Z ]*PRIVATE KEY-----|\b(ghp|ghs|gho|ghu|github_pat)_[A-Za-z0-9_]{20,}|AGE-SECRET-KEY-1"
    r"|\b[A-Za-z0-9+/]{48,}={0,2}\b|\b[0-9a-f]{48,}\b")
# Example hashes and digests are allowed where the line says so.
CREDENTIAL_OK = re.compile(r"sha256:[0-9a-f]{64}|sha256sum|shasum|example", re.IGNORECASE)


def anchors(path):
    """GitHub's heading anchors of a page."""
    found = set()
    for line in path.read_text().splitlines():
        if line.startswith("#"):
            title = line.lstrip("#").strip().lower()
            found.add(re.sub(r"[^\w\- ]", "", title).replace(" ", "-"))
    return found


def test_rule_ids_match_the_bundle():
    bundle = os.environ.get("POLICY_BUNDLE_DIR")
    if not bundle:
        if os.environ.get("GITHUB_ACTIONS"):
            pytest.fail("POLICY_BUNDLE_DIR not set")
        pytest.skip("POLICY_BUNDLE_DIR not set (pull the pinned bundle to run this)")
    rego = [p for p in Path(bundle).rglob("*.rego") if not p.name.endswith("_test.rego")]
    assert rego, "no Rego files under %s" % bundle
    in_bundle = {m for p in rego for m in re.findall(r'"(APP-[A-Z0-9-]+)"', p.read_text())}
    documented = set(re.findall(r"^\| (APP-[A-Z0-9-]+) \|", (REPO / "docs/contract.md").read_text(),
                                re.MULTILINE))
    assert in_bundle - documented == set(), "rules missing in docs/contract.md"
    assert documented - in_bundle == set(), "rules in docs/contract.md the bundle doesn't have"


@pytest.mark.parametrize("path", PAGES, ids=lambda p: p.relative_to(REPO).as_posix())
def test_links(path):
    broken = []
    for target in LINK.findall(path.read_text()):
        if "svenm3/shirtracer-ai-admin" in target:
            broken.append(target + " (private admin repository)")
        if re.match(r"[a-z]+:", target):
            continue
        file, _, anchor = target.partition("#")
        dest = (path.parent / file).resolve() if file else path
        if not dest.exists():
            broken.append(target)
        elif anchor and dest.suffix == ".md" and anchor not in anchors(dest):
            broken.append(target + " (no such heading)")
    assert not broken, broken


@pytest.mark.parametrize("path", PAGES, ids=lambda p: p.relative_to(REPO).as_posix())
def test_no_credentials(path):
    hits = [n for n, line in enumerate(path.read_text().splitlines(), 1)
            if CREDENTIAL.search(line) and not CREDENTIAL_OK.search(line)]
    assert not hits, "credential-shaped strings on lines %s" % hits
