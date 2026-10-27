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
| CPU and memory per service | 2 CPUs, 2 GiB |
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
