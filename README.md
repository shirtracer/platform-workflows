# platform-workflows

The reusable workflow apps on the shirtracer platform call to deploy, and the documentation for
app teams: **[docs/](docs/README.md)**. It validates the app's
`platform.yaml` and `deploy/compose.yaml` against the platform's policy bundle, builds and pushes
the image to GHCR (`ghcr.io/<owner>/<repo>:sha-<commit>`), and sends the deploy or offboard
request to the platform with the job's short-lived GitHub identity token. No credential for the
platform is stored anywhere.

## Calling it

From the app template's `.github/workflows/deploy.yml`:

```yaml
jobs:
  platform:
    uses: shirtracer/platform-workflows/.github/workflows/app.yml@v1
    with:
      action: ${{ inputs.action || 'deploy' }}
      confirm: ${{ inputs.confirm || '' }}
    secrets:
      PLATFORM_SECRETS: ${{ toJSON(secrets) }}
```

The caller needs `permissions: contents: read, packages: write, id-token: write`. Pushes to the
default branch deploy; pull requests and other branches only validate and build.

Secrets are passed explicitly, not with `secrets: inherit`: inheriting passes nothing to a
workflow of another owner (personal-account repositories), and app secret names differ per app.
The workflow takes from `PLATFORM_SECRETS` only the names listed in `platform.yaml` and masks
them in the log.

| Input | Default | Meaning |
|-------|---------|---------|
| `action` | `deploy` | `deploy`, or `offboard` (only by hand, with `confirm`) |
| `confirm` | | offboard only: the app name |
| `environment` | `production` | GitHub Environment the request jobs run in |
| `controller-url` | `https://deploy.platform.shirtracer.gmbh` | the platform's deploy API |
| `dockerfile`, `context` | `Dockerfile`, `.` | the image build |

App secrets: the names listed in `platform.yaml` → `secrets`, from the `production` Environment
(recommended, restricted to `main`; they reach the request jobs directly and take precedence) or
from repository secrets (through `PLATFORM_SECRETS`). Both work for organization and
personal-account repositories.

## Who can deploy

Anyone can call this workflow; only repositories of owners registered on the platform deploy. The
platform checks the token's owner against its registry, binds each app name to the repository
that first deployed it, checks the default branch, and that the request came from this workflow
at an accepted ref. Personal accounts install the platform's GitHub App once and grant the
platform read access to each image package; the first deploy says what is missing.

## Versions

| Ref | Meaning |
|-----|---------|
| `@v1` | the latest `v1.x.y`; fixes and compatible changes reach your app without a change in your repository (recommended) |
| `@v1.x.y` | one exact release; you move it yourself |
| `@main` or any branch | refused by the platform |

Releases follow semantic versioning: patch for fixes and pin updates, minor for new optional
behaviour, a new major (`v2`) for anything an app has to change for. Release tags never change;
only `v1` moves. How releases are made: [RELEASING.md](RELEASING.md).
