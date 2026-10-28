# Bringing an existing repository

You don't need a new repository: an existing one deploys once it has the platform's files and
the app fits the contract. Allow an hour or more, depending on how far the app is from the
contract; the policy names every violation and its fix, so pushing and working through the list
is fine. A coding assistant can do most of it: [Prompts for an AI assistant](ai-prompts.md#an-existing-repository).

## 1. Add the platform's files

Copy these from [shirtracer/platform-app-template](https://github.com/shirtracer/platform-app-template),
at the same paths:

| File | What to do |
|------|------------|
| `platform.yaml` | set the app name, `auth`, `access`, `services`, `secrets` ([The contract](contract.md#platformyaml)) |
| `deploy/compose.yaml` | your stack, rewritten to the rules (step 2); start from the template's or from your own compose file |
| `.github/workflows/deploy.yml` | the caller at `@v1`; keep the `secrets:` lines as they are |
| `.platform/platform.schema.json` | the schema for your editor; don't edit |

`template-ci.yml` and the template's `README.md` aren't needed. An existing workflow that
deploys elsewhere should go, or at least not run on the default branch.

## 2. Fit the app to the contract

### The image

The workflow builds **one** image of your own from `Dockerfile` in the repository root and fills
it in as `${APP_IMAGE}`. A different file or folder: pass the inputs `dockerfile:` and
`context:` in `deploy.yml` (`with:`). Other services use public images with a fixed version
or digest, never `latest` ([APP-C-IMAGE](contract.md#images-and-resources)). The services that
use your image may run different commands (`command:`).

### State and credentials

- **No volumes or bind mounts** ([APP-C-VOLUME](contract.md#host-access)): data goes into
  Postgres or Silo ([Shared services](services.md)), temporary files into `tmpfs`. Redis is a
  cache. Existing data is moved in by the app itself or by a one-off import; the platform
  doesn't migrate data.
- **Credentials are files** under `/run/secrets/<NAME>`, never environment variables
  ([APP-C-ENV-SECRET](contract.md#secrets)). An app that reads `DATABASE_URL` from the
  environment needs a small change, e.g. reading the file at startup:

  ```python
  DATABASE_URL = open("/run/secrets/DATABASE_URL").read()
  ```

  Fixed settings (hosts, ports, bucket names) stay environment variables
  ([Shared services](services.md#connection-settings)).

### Common rewrites in `deploy/compose.yaml`

| You have | The platform wants | Rule |
|----------|--------------------|------|
| `ports: ["8080:8080"]` | `expose` and the Traefik labels of the template (rule ``Host(`${APP_HOST}`)``) | [APP-C-PORTS](contract.md#host-access), [APP-C-PROXY](contract.md#networks-and-names) |
| `build: .` | `image: ${APP_IMAGE}` | [APP-C-BUILD](contract.md#structure) |
| `env_file`, `extends`, `include` | everything in `deploy/compose.yaml`; secrets as files | [APP-C-INCLUDE](contract.md#structure) |
| `volumes:` | Postgres, Silo or `tmpfs` | [APP-C-VOLUME](contract.md#host-access) |
| `container_name`, any service name | services named `<name>` or `<name>-<suffix>` | [APP-C-SVCNAME](contract.md#networks-and-names) |
| a database or Redis container of your own | `services.postgres` / `services.redis` in `platform.yaml` (your own would need a volume) | [APP-C-VOLUME](contract.md#host-access) |
| no limits | `deploy.resources.limits.cpus` and `.memory` on every service | [APP-C-LIMITS](contract.md#images-and-resources) |
| no health check | a `healthcheck` on every routed service | [APP-C-HEALTH](contract.md#images-and-resources) |
| `restart: on-failure` | `unless-stopped` | [APP-C-RESTART](contract.md#host-access) |
| your own networks | `proxy`, `storage`, `apps`, `default` | [APP-C-NET](contract.md#networks-and-names) |

### Login

With `auth: forward` the platform login runs before your app and passes `X-authentik-*`
headers. An app with its own login uses `oidc` (with the platform's OIDC client) or `none`.

## 3. The default branch

The platform deploys from the repository's **default branch**, whatever it's called (it reads
it from GitHub on every deploy). If yours isn't `main` (e.g. `master`):

- in `.github/workflows/deploy.yml`, change `push: branches: [main]` to your branch;
- the `production` Environment's deployment branch is your branch
  ([Secrets](secrets.md)).

Renaming the default branch later works the same way: change both places, then push to the new
default branch.

## 4. Secrets, registration, push

As for a new app: secrets in the `production` Environment
([Getting started](getting-started.md#4-add-your-secrets)); in a personal account its
registration and the [extra steps](repositories.md#your-own-account-the-extra-steps)
([Registration](registration.md)); then push to the default branch.

The policy runs in the workflow on pull requests too, without deploying: a pull request with
the new files is a safe place to work through the violations before the first push to the
default branch.
