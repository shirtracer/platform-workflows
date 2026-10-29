# Where your repository lives

| | Organization `shirtracer` | Your own GitHub account |
|---|---|---|
| Who owns the code | the organization | you |
| Registration | none (the organization is registered) | your account, once ([Registration](registration.md)) |
| Extra steps | none | the GitHub App once, package access per repository (below) |
| Image | `ghcr.io/shirtracer/<repository>` | `ghcr.io/<you>/<repository>` |
| Who can be given access | organization members | collaborators you invite (they always get write access) |

Both deploy the same way. The platform accepts owners by their numeric account ID and binds each
app name to its repository's numeric ID, so neither a renamed or re-registered account nor a
recreated repository can take over an app.

## Your own account: the extra steps

After the admin has registered your account:

1. **Install the platform's GitHub App, once**:
   <https://github.com/apps/platform-controller/installations/new> → your account → **All
   repositories** → Install. The platform reads each repository's `platform.yaml`,
   `deploy/compose.yaml` and default branch through it (read-only). With "Only select
   repositories" instead, add every new app repository to the installation.
   Without it a deploy is refused with
   `repository … is not readable by the platform's GitHub App: install it (…)`.
2. **Grant the platform read access to each new image**, after the repository's first push has
   published it: your profile → **Packages** → the package named like the repository →
   **Package settings → Manage access → Invite teams or people** → `svenm3`, role **Read**.
   GitHub has no account-wide setting for this, so it is once per repository.
   Without it a deploy is refused with
   `image not pullable: grant the GitHub user svenm3 read access to the package …`.

Each refusal names the missing step; after fixing it, start a new run (Actions → deploy → Run
workflow) or push again.

## Pushing from your machine

GitHub accepts only tokens for `git` over HTTPS: create a classic token with the scopes `repo` and
`workflow` (the latter for changes under `.github/workflows/`) and enter it at the password prompt.

## Moving a repository

A **rename** needs nothing: the app follows the repository. A **transfer** between your account
and the organization (or another registered account) also needs nothing, as long as the new owner
is registered and below its limit; in your own account, repeat the extra steps for it. A **new**
repository for an existing app: ask the admin to move the app name to it first. Data,
credentials and the app's address stay in every case.
