# Registration

Apps aren't registered one by one. The platform admin registers **owners**: the organization
`shirtracer` is registered, and a personal account is registered once on request. Any repository
of a registered owner can deploy a new app; its first successful check **binds** the app name to
that repository, so no other repository can take the name or the app's data afterwards.

## In the organization `shirtracer`

Nothing to ask. Create the repository, pick a free app name and push
([Getting started](getting-started.md)). The organization can hold up to 50 apps.

## In your own account

Ask the platform admin once to register your account (your GitHub login), then do the
[steps in your account](repositories.md#your-own-account-the-extra-steps). A personal account can
hold up to 10 apps; ask if you need more. Until the registration, a push is refused with
"owner … is not registered".

Managers of your groups aren't part of any registration: set them yourself in `platform.yaml` →
`access.managers`; they must be existing platform usernames.

## App names

The first push that passes all checks claims the name for that repository. Afterwards:

| Refusal | Meaning |
|---------|---------|
| `app <name> belongs to <owner>/<repository>` | another repository has the name: pick another name, or ask the admin if your team replaced that repository |
| `owner <login> has reached its limit of N apps` | the owner's apps (offboarded ones count until purged) fill its limit: retire an app or ask the admin |
| `app <name> has no binding: ask the admin` | an app from before owner registration that hasn't been bound yet: ask the admin |

A deleted and recreated repository with the same name is a different repository and can't deploy
the old app. A **renamed** repository keeps its apps, and so does one **transferred** to another
registered owner (within that owner's limit).

## Changes later

| You want | Ask the admin to |
|----------|------------------|
| deploy an app from a new repository (keeping its data) | move the app name to the new repository first |
| keep a name for a repository before its first push | bind the name to it |
| a custom domain instead of `<name>.apps.platform.shirtracer.gmbh` | allowlist the domain (and point its DNS record at the platform) |
| a Postgres extension that isn't on the list | check whether the platform's image ships it |
| Grafana access for your team (logs, metrics) | add your platform users to `grafana-viewers` |
| start and restart your app yourself | add your platform users to `arcane-operators` |

## Retiring an app

Offboard it yourself ([Operations](operations.md#offboarding)). The name stays bound to your
repository until the admin purges the kept data; ask for the purge once you're sure, and the name
is free again.
