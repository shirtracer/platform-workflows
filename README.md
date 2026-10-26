# platform-workflows

The reusable workflow apps on the shirtracer platform call to deploy. It validates the app's
`platform.yaml` and `deploy/compose.yaml` against the platform's policy bundle, builds and pushes
the image to GHCR (`ghcr.io/<owner>/<repo>:sha-<commit>`), and sends the deploy or offboard
request to the platform with the job's short-lived GitHub identity token. No credential for the
platform is stored anywhere.

## Calling it

From the app template's `.github/workflows/deploy.yml`:

```yaml
jobs:
  platform:
    uses: shirtracer/platform-workflows/.github/workflows/app.yml@main
    with:
      action: ${{ inputs.action || 'deploy' }}
      confirm: ${{ inputs.confirm || '' }}
    secrets: inherit
```

The caller needs `permissions: contents: read, packages: write, id-token: write`. Pushes to the
default branch deploy; pull requests and other branches only validate and build.

**Repositories outside the `shirtracer` organization** (personal accounts): `secrets: inherit`
passes nothing to a workflow of another owner, so the caller passes its repository secrets as
one value instead:

```yaml
    secrets:
      PLATFORM_SECRETS: ${{ toJSON(secrets) }}
```

The workflow takes from it only the names listed in `platform.yaml` and masks them in the log.

| Input | Default | Meaning |
|-------|---------|---------|
| `action` | `deploy` | `deploy`, or `offboard` (only by hand, with `confirm`) |
| `confirm` | | offboard only: the app name |
| `environment` | `production` | GitHub Environment the request jobs run in |
| `controller-url` | `https://deploy.platform.shirtracer.gmbh` | the platform's deploy API |
| `dockerfile`, `context` | `Dockerfile`, `.` | the image build |

App secrets: the names listed in `platform.yaml` → `secrets`. Organization repositories: from
the `production` Environment (recommended, restricted to `main`) or from repository secrets.
Personal-account repositories: from repository secrets only (GitHub hands Environment secrets to
a workflow of another owner only for names it declares in advance).

## Who can deploy

Anyone can call this workflow; only repositories registered on the platform deploy. The platform
checks the token's repository and owner against its registry, the default branch, and that the
request came from this workflow at an accepted ref. Apps in personal accounts install the
platform's GitHub App on the repository and grant the platform read access to their image
package once; the first deploy says what is missing.

## Refs

`main` is the version apps use until the first release; releases get semver tags and a moving
`v1`. Changes go through pull requests with review and passing `ci`.
