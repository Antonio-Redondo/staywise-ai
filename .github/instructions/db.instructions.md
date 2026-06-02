---
applyTo: "src/db/**,drizzle/**,src/clients/db.ts"
---

# Database and ORM patterns

Load this whenever editing schema, migrations, or anything that reads or writes to Postgres outside the LangGraph checkpointer tables.

## ORM and migrations

- Drizzle ORM. Schema files live in `src/db/schema/`.
- One table per file. File name matches the table name in snake_case.
- Generate migrations with `pnpm drizzle-kit generate`. Apply with `pnpm drizzle-kit migrate`.
- Never edit a migration after it has been applied to any environment. Add a new migration instead.
- Migration files live in `drizzle/` at the repo root. Commit them.

## Schema rules

- Every table has `id` (`uuid`, default `gen_random_uuid()`), `created_at` (`timestamptz`, default `now()`), and `updated_at` (`timestamptz`, default `now()`).
- Soft delete with `deleted_at` (nullable `timestamptz`). Never run `DELETE FROM` in application code.
- Foreign keys are explicit and specify `onDelete` behavior.
- Indexes are added with the migration that introduces the column they index.
- Column names are snake_case in SQL, mapped to camelCase in TypeScript via Drizzle's column config.

## Query organization

- Queries live in `src/db/queries/` organized by domain: `listings.ts`, `clicks.ts`, `sessions.ts`.
- Every query function takes a typed `db` instance as its first argument so transactions can be shared.
- No raw SQL in route handlers or LangGraph nodes. Go through a query function.
- Use Drizzle's `.prepare()` for any query called more than once per request.

## Connection

- One connection pool per process, exported as `db` from `src/db/index.ts`.
- The LangGraph checkpointer shares this pool via `PostgresSaver.fromConnString(process.env.DATABASE_URL!)`. Do not open a second pool.
- Connection string is `DATABASE_URL`. Locally points at the Neon dev branch, in prod at Neon main.

## pgvector

- Vector columns use `vector(1024)` for Anthropic-compatible embeddings via Voyage AI, or `vector(1536)` for OpenAI-compatible.
- Add an `hnsw` index on every vector column that gets queried, with cosine distance unless there is a written reason to use L2.
- Embedding generation lives in a dedicated skill at `src/skills/embed.ts`, called from a node or query function, never inline.

## Click tracking

- The `clicks` table stores affiliate click events: `id`, `listing_id`, `source_domain`, `affiliate_url`, `user_session_id` (nullable), `referrer`, `user_agent`, `created_at`.
- The `/api/track-click` route handler inserts one row per click before redirecting.
- Add an index on `(created_at, source_domain)` for the conversion funnel query.

## Testing

- Database tests use a transaction wrapped in Vitest's `beforeEach` (`BEGIN`) and `afterEach` (`ROLLBACK`).
- Never run tests against the production database. The CI database URL points at a separate Neon branch named `ci`.
- For unit tests on skills that touch queries, mock the query function, not the db connection.

## Drizzle config

`drizzle.config.ts` at the repo root reads `DATABASE_URL` from env and outputs to `drizzle/`. Do not check the generated SQL meta files into version control; only the migrations themselves.
