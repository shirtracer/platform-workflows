# Operations

## Deploys

A push to the default branch (`main` in the template) deploys; pull requests and other
branches only validate and build. The workflow
validates the contract, builds and pushes `ghcr.io/<owner>/<repo>:sha-<commit>` and sends the
deploy request; its summary shows the result and, on a refusal, why.

- **A short gap:** a deploy replaces your containers. Expect a few seconds without an answer:
  the route returns 404 until the new container's first health check passes. An app that starts
  fast keeps the gap short.
- **Waiting for health:** the platform waits up to 5 minutes for every routed service to become
  healthy.
- **Same commit again:** changes nothing. After changing a secret, push a new commit
  ([Secrets](secrets.md#changing-a-secret)).

## Rollback

If the routed services don't become healthy, the platform puts the last healthy version back and
reports `failed` with the reason. Storage changes of the failed version stay (they only add
access). The first deploy has nothing to roll back to.

To keep a failing version running for debugging instead:

```yaml
deploy:
  rollback: false
```

To go back to an older version on purpose, revert the commit on `main` and push.

## Logs

Everything your services write to stdout and stderr is collected. Grafana
(`https://grafana.platform.shirtracer.gmbh`, platform login) → Explore → Loki:

```
{stack="<name>"}
{stack="<name>", service="<name>-web"} |= "error"
```

Grafana access needs membership in `grafana-viewers` ([Registration](registration.md)). App
teams never get access to the server.

## Metrics

Container metrics (CPU, memory, restarts) are collected for every app. For your own metrics,
label the service and keep it on the `apps` network:

```yaml
    labels:
      platform.metrics.port: "8000"
      platform.metrics.path: /metrics   # only if not /metrics
    networks: [proxy, apps]
```

The platform scrapes it every 30 s in Prometheus format; the series appear in Grafana with the
labels `stack` (your app), `service` and `container`.

## Calls between apps

Apps reach each other over the `apps` network by aliases, never by container names:

```yaml
services:
  shop-api:
    networks:
      apps:
        aliases: [shop-api]
```

Another app calls `http://shop-api:<port>/…`. Aliases are named `<name>-<suffix>`
([APP-C-ALIAS](contract.md#networks-and-names)).

**Calls over `apps` don't pass the platform login.** A request arriving over `apps` carries
whatever `X-authentik-*` headers the calling app put there, so never treat them as proof of a
user on a service other apps can reach. If such a service must know who calls it, authenticate
the caller yourself, e.g. a shared token stored as a secret in both apps:

```python
token = open("/run/secrets/SHOP_API_TOKEN").read()
if not hmac.compare_digest(request.headers.get("Authorization", ""), f"Bearer {token}"):
    abort(401)
```

## Starting and restarting

Trusted members of your team can get the Arcane Operator role (see status, start and restart
your app) through the `arcane-operators` group; ask the admin ([Registration](registration.md)).

## Template updates

Your repository is a copy of the template; it isn't updated by itself. When the template
changes (the workflow's release notes say so), compare and take over what applies:

- `.platform/platform.schema.json`: replace it with the template's copy (never edit it).
- `.github/workflows/deploy.yml`: keep `@v1`; take over changed inputs or permissions.
- `deploy/compose.yaml`, `Dockerfile`: only if you want the example's changes.

Patch and minor releases of the workflow reach you through `@v1` without any change. Pin
`@v1.x.y` only if you need an exact version, and move it yourself.

## Offboarding

Removing the app is never triggered by a push. In GitHub: **Actions → deploy → Run workflow**,
action `offboard`, and type the app name as confirmation. The platform then keeps a final
database backup, keeps the buckets until the offsite copy has them, and removes the app, its
route, credentials and access to the shared services. The name stays bound to your repository
until the admin purges the kept data ([Registration](registration.md#retiring-an-app)).
