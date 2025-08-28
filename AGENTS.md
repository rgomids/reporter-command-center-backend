# Repository Guidelines

## Project Structure & Modules
- `cmd/server/`: Entry point (`main.go`).
- `internal/`: App packages (HTTP handlers, middleware, auth, config, domain, repo).
- `deploy/`: Deployment assets (e.g., `docker-compose` for EC2).
- Root: `Makefile`, `Dockerfile`, `go.mod`, `.env.example`. Legacy Python lives in `legacy/` (kept for reference).

## Build, Test, and Development
- `make run`: Start the API locally on `PORT` (default `8000`).
- `make build`: Compile binary to `bin/server`.
- `make test`: Run Go tests across all packages.
- `make tidy`: Sync module deps (`go mod tidy`).
- Docker: `docker build -t reporter-backend . && docker run -p 8000:8000 reporter-backend`.

## Coding Style & Naming
- Language: Go 1.22+. Use `gofmt` defaults (tabs, standard import grouping).
- Package layout: keep domain types in `internal/domain`, HTTP in `internal/http`, state in `internal/repo`.
- Files: snake_case for filenames; `_test.go` for tests.
- Prefer small, cohesive packages; no cyclic deps. Public identifiers only when used across packages.

## Testing Guidelines
- Framework: standard `testing` package.
- Naming: test files end with `_test.go`; functions `TestXxx(t *testing.T)`.
- Run: `make test` or `go test ./... -race -cover`.
- Coverage: aim ≥80% on core packages (`internal/http`, `internal/repo`, `internal/auth`). Add table‑driven tests for handlers and repo logic.

## Commit & Pull Requests
- Commits: follow Conventional Commits. Examples:
  - `feat(go): add Teams webhook HMAC validation`
  - `fix(http): handle empty tenant id`
- PRs must include:
  - Purpose and linked issue(s).
  - How to validate locally (commands, sample curl).
  - Any config/env changes (`.env`, variables).
  - Screenshots or logs when relevant (e.g., request/response snippets).

## Security & Configuration
- Env vars: `PORT`, `JWT_SECRET`, `CORS_ALLOWED_ORIGINS` (see `.env.example`). Never commit real secrets.
- Webhooks: Teams endpoint uses HMAC SHA‑256 of raw body; document shared secret per tenant.
- Auth: JWT (HS256) via `Authorization: Bearer <token>`; public routes: `/`, `/healthz`, `/auth/login`, `/webhooks/*`.

## Architecture Overview
- HTTP router: chi middleware stack + CORS + auth.
- Storage: in‑memory repo for org config, integrations, webhook dedup, and collected messages.
- Future work: swap `internal/repo` for persistent storage; expand tests and CI for Go.

