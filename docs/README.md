# Apps on the shirtracer platform

Everything an app team needs to run an app on the platform. You never get access to the server;
your repository and this documentation are all you work with.

| Page | What it covers |
|------|----------------|
| [Getting started](getting-started.md) | from the template to your app at `https://<name>.apps.platform.shirtracer.gmbh` |
| [Bringing an existing repository](existing-repository.md) | the platform's files, the common rewrites, another default branch |
| [Where your repository lives](repositories.md) | the `shirtracer` organization or your own account (two one-time steps) |
| [Registration](registration.md) | getting a repository registered, moving or retiring an app, whom to ask |
| [The contract](contract.md) | every `platform.yaml` field and every rule your compose file must follow, with fixes |
| [Shared services](services.md) | Postgres, Redis and Silo: what your app can do, limits, extensions |
| [Secrets](secrets.md) | your own secrets, the platform's credential files, rotation |
| [Operations](operations.md) | deploys, rollback, logs, metrics, calls between apps, offboarding, template updates |

The template: [shirtracer/platform-app-template](https://github.com/shirtracer/platform-app-template).
The workflow your app calls: [`.github/workflows/app.yml`](../.github/workflows/app.yml), at `@v1`.

These pages are released with the workflow: what you read on `main` describes the latest `v1`.
