# Prompts for an AI assistant

Two prompts to give a coding assistant (Claude Code, Copilot, Cursor and the like), opened in
your repository. Replace the parts in `<angle brackets>` first. The assistant reads these pages
from the links in the prompt; one without web access needs them pasted in.

The assistant prepares the files. The steps outside the repository stay yours: the `production`
Environment and its secrets ([Secrets](secrets.md)), and in your own account its registration
([Registration](registration.md)) and the
[extra steps](repositories.md#your-own-account-the-extra-steps). Never paste secret
values into the chat; the files only name them.

## A new app from the template

Create the repository from the template first ([Getting started](getting-started.md#1-create-your-repository)),
clone it and open the assistant in it.

```text
This repository was created from the shirtracer platform's app template. Turn it into my app.

App name: <name>  (lower-case letters and digits, starting with a letter, no "-")
What the app does: <one or two sentences, or "keep the example app for now">
Language/framework: <e.g. Python/FastAPI, Node/Express>
Login: <forward | oidc | none>
Who may use it: <platform groups, e.g. name-users>; managers: <platform usernames>
Shared services: <any of postgres, redis, s3, or none>
My own secrets (names only): <e.g. STRIPE_API_KEY, or none>

Read these first and follow them exactly:
- https://raw.githubusercontent.com/shirtracer/platform-workflows/v1/docs/getting-started.md
- https://raw.githubusercontent.com/shirtracer/platform-workflows/v1/docs/contract.md
- https://raw.githubusercontent.com/shirtracer/platform-workflows/v1/docs/services.md
- https://raw.githubusercontent.com/shirtracer/platform-workflows/v1/docs/secrets.md

Rules:
- Replace "myapp" on every line marked "change:" in platform.yaml and deploy/compose.yaml.
  Keep the lines marked "keep:" as they are.
- Each of my secret names appears in three places with the same spelling: platform.yaml
  "secrets", the service's "secrets:" list and the top-level "secrets:" of
  deploy/compose.yaml. Replace or remove EXAMPLE_API_KEY in all three. Remove DATABASE_URL,
  REDIS_URL or S3_* where I don't use that service.
- The app reads credentials from the files /run/secrets/<NAME>, never from environment
  variables. No volumes; data goes to Postgres or the S3 bucket.
- Don't change .github/workflows/deploy.yml or .platform/platform.schema.json.
- Never write secret values into any file.
- Replace the example app in app/ and the Dockerfile with mine. Keep a health endpoint
  (the example's is /healthz) and make the compose healthcheck work in my image (the
  template's calls python).

When done, list what you changed, and the secret names I must add to the GitHub
Environment "production".
```

## An existing repository

Open the assistant in your repository, on a new branch.

```text
Convert this repository so it deploys on the shirtracer platform. Don't deploy anything.

App name: <name>  (lower-case letters and digits, starting with a letter, no "-")
Default branch: <main | master | ...>
Login: <forward | oidc | none>
Who may use it: <platform groups>; managers: <platform usernames>

Read these first and follow them exactly:
- https://raw.githubusercontent.com/shirtracer/platform-workflows/v1/docs/existing-repository.md
- https://raw.githubusercontent.com/shirtracer/platform-workflows/v1/docs/contract.md
- https://raw.githubusercontent.com/shirtracer/platform-workflows/v1/docs/services.md
- https://raw.githubusercontent.com/shirtracer/platform-workflows/v1/docs/secrets.md
Take the platform's files from https://github.com/shirtracer/platform-app-template
(platform.yaml, deploy/compose.yaml, .github/workflows/deploy.yml,
.platform/platform.schema.json) at the same paths.

Steps:
1. Look at the app first: its Dockerfile(s), compose files, the services it runs, where it
   keeps data, how it reads configuration and credentials. Tell me what doesn't fit the
   contract and what you plan to change, before you change it.
2. Write platform.yaml and deploy/compose.yaml by the rules, using the "Common rewrites"
   table. One image of our own (inputs dockerfile:/context: in deploy.yml if not ./Dockerfile);
   other services as public images with a fixed version; no volumes; databases and Redis
   from "services" in platform.yaml instead of our own containers.
3. Change the code so credentials are read from /run/secrets/<NAME> files instead of
   environment variables. Fixed settings (hosts, ports, bucket names) stay environment
   variables.
4. Each secret name appears in three places with the same spelling (platform.yaml
   "secrets", the service's "secrets:" list, the top-level "secrets:" of the compose file).
5. If the default branch isn't main, change "push: branches" in deploy.yml.
6. Remove or disable workflows that deploy elsewhere from the default branch.
- Never write secret values into any file; list the names instead.
- Don't edit .platform/platform.schema.json or the "secrets:" lines in deploy.yml.

When done, list the changes, anything that needs a decision from me (e.g. data to move
into Postgres or S3), and the secret names for the GitHub Environment "production".
```

Push the branch and open a pull request: the workflow checks the files without deploying, and a
refusal names the rule ([The contract](contract.md)). Give the failed run's output back to the
assistant until the check passes, then merge.
