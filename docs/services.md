# Shared services

The platform runs one Postgres, one Redis and one S3 store (Silo) for all apps. Declare what
your app uses in `platform.yaml` → `services`, put the services that use them on the `storage`
network, and read the credentials from files ([Secrets](secrets.md)). Removing a service from
`platform.yaml` revokes access and keeps the data.

## Connection settings

Fixed values, fine as environment variables:

| Service | Settings | Credential files |
|---------|----------|------------------|
| Postgres | host `storage-postgres`, port `5432`, database and user = app name | `POSTGRES_PASSWORD`, `DATABASE_URL` |
| Redis | host `storage-redis`, port `6379`, user = app name | `REDIS_PASSWORD`, `REDIS_URL` |
| Silo (S3) | endpoint `http://storage-silo:9000`, region `us-east-1`, path-style addressing, bucket = app name | `S3_ACCESS_KEY`, `S3_SECRET_KEY` |

## Postgres

```yaml
services:
  postgres:
    extensions: [pg_trgm, citext]
```

| Your app can | Your app cannot |
|--------------|-----------------|
| own its database `<name>`: create, alter and drop tables, schemas, indexes, views; run migrations | touch other databases; act as superuser; create databases or roles |
| use the extensions it lists | install extensions not on the list |

Allowed extensions: `btree_gin`, `btree_gist`, `citext`, `cube`, `earthdistance`,
`fuzzystrmatch`, `hstore`, `intarray`, `isn`, `lo`, `ltree`, `pg_trgm`, `pgcrypto`, `seg`,
`tablefunc`, `unaccent`, `uuid-ossp`. The platform creates them in your database at the deploy;
removing one from `platform.yaml` never drops it. Need another one? Ask the admin
([Registration](registration.md)).

At most **50 connections** per app; size your connection pools across all replicas below that.
Your database is backed up by the platform (daily, with point-in-time recovery); a restore is
done by the admin on request.

### Looking into your database (pgAdmin)

Your team can open your app's database in the browser at
[pgadmin.platform.shirtracer.gmbh](https://pgadmin.platform.shirtracer.gmbh), with your normal
platform login (Authentik, with its second factor). Nobody gets a database password, and your
app's credentials are never shown there.

- **Who**: the app's managers (`access.managers` in `platform.yaml`) and the members of the
  Authentik group `<name>-db`. The platform creates that group for every app with Postgres; your
  managers add and remove people in it themselves (Authentik → Directory → Groups → `<name>-db`),
  like your app's other groups. Being in your app's access groups alone does not give database
  access. An app with `auth: none` has no managers on the platform: ask the platform admin to add
  or remove people in `<name>-db`.
- **What you see**: after login, the group `<name>` with one entry `<name>`; connect without a
  password. You see no other app's database and can't connect to one, even with a server you add
  yourself.
- **What you can do**: everything your app can, on your app's database only: read and change
  data, create and alter tables, run SQL. **This is production data**: there is no undo apart
  from a restore by the admin. Tables you create belong to your app, so your app can use them.
- **Limits**: at most 5 connections for your whole team, a statement is cancelled after 5
  minutes, and a transaction left open is ended after 10 minutes (so a forgotten pgAdmin tab
  never blocks your app for long). These limits count separately from your app's 50 connections.
- **Logging out and leaving**: sessions end after 8 hours. Someone removed from `<name>-db` can't
  open a new connection from then on; the admin can also switch your team's database access off
  and on again at once.
- **From abroad**: like everything on the platform, pgAdmin answers only in Germany
  ([Operations](operations.md)).

pgAdmin keeps no data of its own besides your preferences; downloads and uploads in its file
manager are gone after a restart.

## Redis

```yaml
services:
  redis: true
```

| Your app can | Your app cannot |
|--------------|-----------------|
| any keys and pub/sub channels under `<name>:` | other prefixes |
| normal data commands | admin and dangerous commands (`KEYS`, `FLUSHALL`, `FLUSHDB`, `CONFIG`, …); use `SCAN` instead of `KEYS` |

Redis is a **cache**: it survives restarts but isn't backed up. Keep anything you can't
rebuild in Postgres or Silo.

## Silo

```yaml
services:
  s3: true
```

| Your app can | Your app cannot |
|--------------|-----------------|
| read and write objects in the bucket `<name>` | other apps' buckets |
| create and delete buckets `<name>-*` (e.g. `shop-uploads`) | buckets without its prefix; users and policies |

Keep to at most **20 buckets** `<name>-*`: Silo can't enforce a count, so the platform reports
more and the admin follows up. Buckets are copied offsite with the platform's backups.

## Limits

| Limit | Value |
|-------|-------|
| CPU and memory per service | 4 CPUs, 8 GiB (policy 2.2.0; 2 CPUs, 2 GiB before) |
| CPU and memory per app (limits × replicas) | 4 CPUs, 8 GiB |
| Postgres connections per app | 50 |
| Buckets per app | 20 |

The first two are checked before the deploy ([APP-C-QUOTA-SVC, APP-C-QUOTA-APP](contract.md#images-and-resources)).

## Stateless apps

Containers have no volumes and are replaced at every deploy. State lives in Postgres or Silo;
temporary files go into a `tmpfs` mount:

```yaml
    tmpfs:
      - /tmp
```
