# The contract

Your repository holds two files the platform checks on every run, in CI and again on the server:
`platform.yaml` (what the platform provides) and `deploy/compose.yaml` (your stack). A violation
names its rule, file and field, e.g.

```
[APP-C-PRIV] deploy/compose.yaml: services.shop-web.privileged: not allowed
```

Find the rule ID below. Your editor can check `platform.yaml` while you type: the first line
`# yaml-language-server: $schema=./.platform/platform.schema.json` points at the schema.

## platform.yaml

| Field | Meaning |
|-------|---------|
| `name` (required) | app name: `^[a-z][a-z0-9]{0,30}$`, no `-`; not reserved |
| `domain` | defaults to the app name (`<name>.apps.platform.shirtracer.gmbh`); anything else must be allowlisted by the admin |
| `auth` | `forward` (default), `oidc` or `none` |
| `access.groups` | required with `forward`/`oidc`, at most 20: `<name>-<suffix>` groups are created for your app; other names must be existing platform groups |
| `access.managers` | platform usernames (at most 20) who manage the members of your own groups; needs at least one own group |
| `auth_callbacks` | `oidc` only, at most 10: extra redirect paths on your own host besides `/oauth2/callback` |
| `services.postgres.extensions` | the database `<name>`; extensions from the allowlist ([Shared services](services.md#postgres)) |
| `services.redis` | `true`: a Redis user for keys and channels under `<name>:` |
| `services.s3` | `true`: the bucket `<name>`; your app may create and delete buckets `<name>-*` |
| `secrets` | names (`^[A-Z][A-Z0-9_]*$`, at most 50) of your own secrets ([Secrets](secrets.md)) |
| `deploy.rollback` | `false` keeps a failing version running for debugging (default `true`) |

Removing a service revokes access and keeps the data.

## Compose file in short

- Services are named `<name>` or `<name>-<suffix>`; the app's image is `${APP_IMAGE}` (this
  commit's build), the route's host is `${APP_HOST}`, credential files come from `${APP_SECRETS}`.
  No other `${…}` variables.
- Networks: `proxy` (the route), `storage` (shared services), `apps` (other apps reach the
  aliases you list there), `default` (private to your app).
- Every service has CPU and memory limits; routed services have a health check.
- No volumes, ports, privileges, host access or Docker socket; state lives in Postgres or Silo.

## Manifest rules

| Rule | Means | Fix |
|------|-------|-----|
| APP-INPUT | `platform.yaml` or `deploy/compose.yaml` is missing, not a mapping, or has more than one YAML document | one document per file; keep both files at these paths |
| APP-M-SCHEMA | the manifest doesn't match the schema (unknown field, wrong type, bad name or secret name, too many entries) | compare with the table above; the message names the field |
| APP-M-RESERVED | the app name is reserved for the platform | choose another name |
| APP-M-DOMAIN | `domain` is neither the app name nor allowlisted for this app | remove `domain`, or ask the admin to allowlist it |
| APP-M-EXT | an extension is not on the allowlist | use one from [the list](services.md#postgres) or ask the admin |
| APP-M-SECRET-CLASH | one of your secret names equals a platform credential (e.g. `DATABASE_URL`) | rename your secret |
| APP-M-ACCESS | `forward`/`oidc` without `access.groups`, `none` with `access`, or managers without an own group | add groups; remove `access` with `auth: none`; add a `<name>-…` group for managers |
| APP-M-CALLBACK | `auth_callbacks` without `auth: oidc`, or a path containing `..` | use `auth: oidc`, or plain paths like `/auth/callback` |

## Compose rules

### Structure

| Rule | Means | Fix |
|------|-------|-----|
| APP-C-KEY | a key the platform doesn't allow (top level, service or nested) | remove it; the message names the key |
| APP-C-NAME | top-level `name` differs from the app name | set `name: <name>` or remove it |
| APP-C-INTERP | a `${…}` other than `${APP_IMAGE}` (image), `${APP_HOST}` (router rule), `${APP_SECRETS}` (secret files); `$$` escapes are fine | write the value directly; in commands escape `$` as `$$` |
| APP-C-INCLUDE | `include`, `extends` or `env_file` | put everything into `deploy/compose.yaml` |
| APP-C-BUILD | `build` | the workflow builds `Dockerfile`; use `image: ${APP_IMAGE}` |

### Host access

| Rule | Means | Fix |
|------|-------|-----|
| APP-C-PRIV | `privileged` | remove it |
| APP-C-CAPS | `cap_add` (`cap_drop` is fine) | remove it |
| APP-C-DEVICES | `devices`, `device_cgroup_rules` or `gpus` | remove them |
| APP-C-SECOPT | `security_opt` or `sysctls` | remove them |
| APP-C-NS | `network_mode`, `pid`, `ipc`, `uts`, `userns_mode`, `cgroup`, `cgroup_parent` or `runtime` | remove them |
| APP-C-PORTS | `ports` | use `expose`; the route goes through the platform's proxy |
| APP-C-VOLUME | volumes or bind mounts of any kind (`tmpfs` is fine) | state into Postgres or Silo; temporary files into `tmpfs` |
| APP-C-LOGGING | `logging` | remove it; the platform collects stdout and stderr |
| APP-C-RESTART | `restart` other than `unless-stopped` or `always` | use `unless-stopped` |

### Images and resources

| Rule | Means | Fix |
|------|-------|-----|
| APP-C-IMAGE | no `image`, or a moving tag like `latest` | `${APP_IMAGE}`, or `<image>:<version>` / `<image>@sha256:<digest>` |
| APP-C-LIMITS | a service without `deploy.resources.limits.cpus` and `.memory` | add both |
| APP-C-QUOTA-SVC | a service above 2 CPUs or 2 GiB | lower the limits |
| APP-C-QUOTA-APP | the app above 4 CPUs or 8 GiB in total (limits × replicas) | lower limits or replicas |
| APP-C-HEALTH | a routed service without a working `healthcheck` | add a `healthcheck.test` (not `NONE`, not disabled) |

### Networks and names

| Rule | Means | Fix |
|------|-------|-----|
| APP-C-NET | a network other than `proxy`, `storage`, `apps` (each `external: true`, no `name`) and `default` (no settings) | use these four |
| APP-C-SVCNAME | a service not named `<name>` or `<name>-<suffix>`, or `container_name`, `hostname`, `domainname` | rename the service; remove those keys |
| APP-C-ALIAS | an alias not on `apps`, not `<name>-<suffix>`, or fixed addresses and links | aliases only on `apps`, named `<name>-…` |
| APP-C-STORAGE | a service on `storage` without any service in `platform.yaml` | declare the service you use, or leave `storage` |
| APP-C-PROXY | a service on `proxy` without `traefik.enable: "true"` and a router, or a router without `proxy` | both together, or neither |
| APP-C-METRICS | `platform.metrics.port` not a port, `platform.metrics.path` not `/…` or without a port, or the service not on `apps` | port 1–65535, path starting with `/`, service on `apps` |

### Routes

| Rule | Means | Fix |
|------|-------|-----|
| APP-C-LABEL | a Traefik label the platform doesn't allow, or a reserved label (`com.docker.`, `com.getarcaneapp.`, `platform.` except the metrics opt-in) | keep to the template's labels |
| APP-C-ROUTE-NAME | a router, route service or middleware not named `<name>` or `<name>-<suffix>` | rename it |
| APP-C-HOST | a rule with something other than ``Host(`${APP_HOST}`)`` | use exactly ``Host(`${APP_HOST}`)`` |
| APP-C-ENTRY | `entrypoints` not `websecure`, or `tls.certresolver` not `le` | use `websecure` and `le` |
| APP-C-MIDDLEWARE | a middleware that is neither yours (`<name>…@docker`, allowed types) nor the platform login | use your own middlewares of the allowed types or `authentik@file` |
| APP-C-AUTH | `auth: forward` but a router without `authentik@file`, or `oidc`/`none` with it | add or remove `authentik@file` per router |
| APP-C-DOCKERNET | `traefik.docker.network` other than `proxy` | set it to `proxy` |

Allowed middleware types: `headers`, `redirectregex`, `redirectscheme`, `stripprefix`,
`stripprefixregex`, `addprefix`, `replacepath`, `replacepathregex`, `compress`, `ratelimit`,
`buffering`.

### Secrets

| Rule | Means | Fix |
|------|-------|-----|
| APP-C-SECRET-SRC | a top-level secret not exactly `file: ${APP_SECRETS}/<NAME>` | use that form |
| APP-C-SECRET-NAME | a secret that is neither a platform credential of a declared service nor in `platform.yaml` → `secrets` | declare the service or the secret |
| APP-C-SECRET-USE | a service refers to an undeclared secret, or overrides `uid`, `gid`, `mode` or a target path | refer to top-level secrets only, short form or `source` (+ plain `target`) |
| APP-C-ENV-SECRET | an `environment` variable named like a credential or one of your secrets | read the file `/run/secrets/<NAME>` instead |
