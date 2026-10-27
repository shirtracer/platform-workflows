# Registration

Only registered repositories deploy; registering is the one step the platform admin does per
app.

## Ask for it

Send the platform admin:

- the **app name** (rules: [Getting started](getting-started.md#2-choose-the-app-name));
- the **repository** (`owner/name`) and that its default branch is `main`.

The admin checks the name, registers the repository with its owner and confirms. Managers of your
groups aren't part of the registration: set them yourself in `platform.yaml` →
`access.managers`; they must be existing platform usernames. In your own
account, do the [two one-time steps](repositories.md#your-own-account-the-two-one-time-steps)
then. Organization repositories need nothing more. A push before the registration is refused
with "app … is not registered"; push again afterwards.

## Changes later

| You want | Ask the admin to |
|----------|------------------|
| move the repository (owner or name) | update the registration first |
| a custom domain instead of `<name>.apps.platform.shirtracer.gmbh` | allowlist the domain (and point its DNS record at the platform) |
| a Postgres extension that isn't on the list | check whether the platform's image ships it |
| Grafana access for your team (logs, metrics) | add your platform users to `grafana-viewers` |
| start and restart your app yourself | add your platform users to `arcane-operators` |

## Retiring an app

Offboard it yourself ([Operations](operations.md#offboarding)), then ask the admin to remove the
registration and, once you're sure, to purge the kept data.
