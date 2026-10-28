# Getting started

From nothing to your app at `https://<name>.apps.platform.shirtracer.gmbh` in about 30 minutes of
your own work, plus the admin's registration.

## 1. Create your repository

Open [shirtracer/platform-app-template](https://github.com/shirtracer/platform-app-template) →
**Use this template** → **Create a new repository**:

- **Owner**: `shirtracer` (if you're a member) or your own account. The difference is explained
  in [Where your repository lives](repositories.md); the organization needs no extra steps.
- **Visibility**: private is fine.
- Default branch `main` (as in the template).

## 2. Choose the app name

Lower-case letters and digits, starting with a letter, at most 31 characters, no `-`
(e.g. `shop`). It becomes the hostname, the database, the Redis user, the bucket and the prefix of
every service and alias. Some names are reserved for the platform (e.g. `admin`, `app`, `grafana`);
the policy tells you if yours is one ([APP-M-RESERVED](contract.md#manifest-rules)).

Replace `myapp` on every line marked `# change:` in `platform.yaml` and `deploy/compose.yaml`.

## 3. Pick login, services and secrets

In `platform.yaml` (all fields: [The contract](contract.md#platformyaml)):

- `auth`: `forward` (the platform login runs before every request, default), `oidc` (your app
  logs users in with the platform's OIDC client) or `none` (public, or your own login).
- `access.groups`: who may use the app, e.g. `[shop-users]`; `access.managers`: platform
  usernames that manage the members of your own groups.
- `services`: `postgres`, `redis`, `s3`; remove what you don't need
  ([Shared services](services.md)).
- `secrets`: names of your own secrets (API keys and the like). Each name appears in three
  places, all with the same spelling: `platform.yaml` → `secrets`, the service's `secrets:` list
  in `deploy/compose.yaml`, and an entry `<NAME>: {file: ${APP_SECRETS}/<NAME>}` in its top-level
  `secrets:`. Replace `EXAMPLE_API_KEY` in all three (or remove it everywhere); a name left in
  only one place fails the check ([APP-C-SECRET-NAME](contract.md#secrets)). Your app reads
  `/run/secrets/<NAME>`.
- The same holds for the platform's credentials: remove `DATABASE_URL`, `REDIS_URL` or `S3_*`
  from `deploy/compose.yaml` when you drop the service.

## 4. Add your secrets

Repository → **Settings → Environments → New environment** `production` → **Deployment branches
and tags**: "Selected branches and tags", add `main`. Add one secret per name in `platform.yaml` →
`secrets`. Repository secrets work too; [Secrets](secrets.md) explains the difference.

## 5. Get the repository registered

Ask the platform admin ([Registration](registration.md)) with the app name and the repository.
Until then a push is refused with "app … is not registered". In your own account, also do the two
one-time steps in [Where your repository lives](repositories.md).

## 6. Push to `main`

The **deploy** workflow validates `platform.yaml` and `deploy/compose.yaml` against the platform's
rules, builds the image `ghcr.io/<owner>/<repository>:sha-<commit>`, pushes it and asks the
platform to deploy. The run's summary ends with:

```
deploy shop: succeeded — shop healthy at https://shop.apps.platform.shirtracer.gmbh
```

Pull requests and other branches only validate and build. A refusal names its reason and, for a
rule, its ID: look it up in [The contract](contract.md).

## Next

- Replace the example app in `app/` and `Dockerfile` with yours; keep the lines marked `keep:`.
- [Operations](operations.md): logs, metrics, rollback, calling other apps.
- An existing repository instead of the template: [Bringing an existing repository](existing-repository.md).
- Working with a coding assistant: [Prompts for an AI assistant](ai-prompts.md).
