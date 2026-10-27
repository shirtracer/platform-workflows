# Releasing

For the platform admin. App teams call the workflow at `@v1` (see [README](README.md)).

## Rules

- Changes reach `main` only by pull request with review and a green `ci` (ruleset on `main`).
- Every release is a tag `v1.x.y` with a GitHub release and notes. Release tags are **never moved
  or deleted** (tag ruleset `release-tags`: only admins create, update or delete `v*`).
- `v1` is the moving major tag: it points at the latest `v1.x.y`.
- Version: patch for fixes, pin updates and docs; minor for new optional inputs or behaviour;
  major (`v2`) for anything an app must change for. Before a `v2`, the platform accepts
  `refs/tags/v2` and `refs/tags/v2.*.*` (its `DEPLOY_API_WORKFLOW_REFS`).

## Steps

1. Merge the pull request into `main`; wait for `ci` on `main`.
2. Tag and push the release, then move `v1`:
   ```
   git switch main && git pull
   git tag -a v1.x.y -m "v1.x.y"
   git push origin v1.x.y
   git tag -f v1 v1.x.y
   git push -f origin v1
   ```
3. GitHub → Releases → Draft a new release → tag `v1.x.y` → notes (what changed, whether apps need
   to do anything) → Publish.
4. Check: an app at `@v1` deploys (its run's "platform" job shows the workflow at the new commit).

## Policy pin

`POLICY_BUNDLE` in `.github/workflows/app.yml` must equal the platform's `policy_bundle`. Change
both together, in the order of the platform's upgrade runbook: platform first, then this pin as a
patch release right after; requests in between are refused with "validated with policy X; the
platform runs Y".

## A bad release

Move `v1` back to the previous release (`git tag -f v1 v1.x.(y-1) && git push -f origin v1`),
then fix forward with the next patch. Never move or delete the bad release's own tag.
