# Where your repository lives

| | Organization `shirtracer` | Your own GitHub account |
|---|---|---|
| Who owns the code | the organization | you |
| Extra steps before the first deploy | none | two, once per app (below) |
| Image | `ghcr.io/shirtracer/<repository>` | `ghcr.io/<you>/<repository>` |
| Who can be given access | organization members | collaborators you invite (they always get write access) |

Both deploy the same way; the platform binds each app to its repository **and** the owner's
account ID, so a renamed or re-registered account can't take over an app.

## Your own account: the two one-time steps

After the admin has registered the repository:

1. **Install the platform's GitHub App** on the repository:
   <https://github.com/apps/platform-controller/installations/new> → your account → "Only select
   repositories" → this repository → Install. The platform reads `platform.yaml` and
   `deploy/compose.yaml` through it (read-only, this repository only).
   Without it a deploy is refused with
   `repository … is not readable by the platform's GitHub App: install it (…)`.
2. **Grant the platform read access to your image**, after the first push has published it: your
   profile → **Packages** → the package named like the repository → **Package settings → Manage
   access → Invite teams or people** → `svenm3`, role **Read**.
   Without it a deploy is refused with
   `image not pullable: grant the GitHub user svenm3 read access to the package …`.

Each refusal names the missing step; after fixing it, start a new run (Actions → deploy → Run
workflow) or push again.

## Pushing from your machine

GitHub accepts only tokens for `git` over HTTPS: create a classic token with the scopes `repo` and
`workflow` (the latter for changes under `.github/workflows/`) and enter it at the password prompt.

## Moving a repository

Between your account and the organization, or to a new name: ask the admin to update the
registration (repository and owner) first. Until then deploys from the new location are refused.
Data, credentials and the app's address stay.
