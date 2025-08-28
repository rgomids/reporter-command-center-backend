# Daily Reporter Bot — Backend

Este repositório está sendo refatorado para Go. A implementação original em Python foi movida para `legacy/` e permanece disponível para referência e eventual manutenção.

Links úteis:
- ROADMAP: `ROADMAP.md`
- Deploy AWS: `DEPLOY_AWS.md`
- Quality gate: `QUALITY_GATE.md`

## Estrutura
- Código Go atual: `cmd/server`, `Dockerfile`, `Makefile`, `go.mod`
- Implementação Python legada: `legacy/`

## Go — Requisitos
- Go 1.22+

## Go — Execução (dev)
```
cp .env.example .env  # opcional
make run              # PORT=8000 por padrão
# http://localhost:8000           -> {"service":"reporter-command-center-backend","status":"ok"}
# http://localhost:8000/healthz   -> ok
```

## Go — Build e Testes
```
make build   # gera binário em bin/server
make test    # testes Go (quando adicionados)
```

## Docker & Compose
```
# Backend image
make docker-build
make docker-run    # expõe 8000

# Stack completa (db + backend + frontend)
make compose-up
make compose-logs
make compose-down
```

## Qualidade de Código
```
make fmt          # formata com gofmt -s
make fmt-check    # verifica formatação
make vet          # análises estáticas padrão
make lint         # golangci-lint (usa binário local ou container)
make test-coverage COVERAGE_THRESHOLD=80  # gera cobertura e aplica limite
make quality      # fmt-check + vet + lint + test-coverage
```
Configurações adicionais do linter em `.golangci.yml`. O limite de cobertura padrão é 0% (para não bloquear enquanto os testes são escritos); ajuste via `COVERAGE_THRESHOLD=80` em CI.

## Endpoints (Go)
- Auth: POST `/auth/login`, GET `/auth/session`
- Org Config: GET `/org/config`, PUT `/org/config`
- Integrations (Teams):
  - POST `/integrations/teams/validate`
  - POST `/integrations/teams/save`
  - POST `/integrations/teams/send`
  - POST `/webhooks/teams` (sem Auth; assinatura HMAC)
- Integrations (AI):
  - POST `/integrations/ai/save`
  - POST `/ai/summarize`
- Coletas: GET `/collections/responses`

### Fluxo rápido (curl)
1) Login e token
```
curl -s localhost:8000/auth/login -X POST -H 'Content-Type: application/json' \
  -d '{"tenant_id":"t1","user_id":"u1","email":"u1@example.com","password":"x","role":"admin"}' | jq -r .access_token
```
2) Salvar integração Teams (use seu segredo)
```
TOKEN=...    # do passo anterior
SECRET=super-secret
curl -s localhost:8000/integrations/teams/save -X POST -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  -d '{"app_id":"app","app_secret":"sec","webhook_secret":"'"$SECRET"'"}'
```
3) Enviar um webhook assinado
```
BODY='{"channel_id":"ch1","user_id":"u1","text":"Olá do Teams!"}'
SIG=$(printf "%s" "$BODY" | openssl dgst -sha256 -hmac "$SECRET" -binary | xxd -p -c 256)
curl -s localhost:8000/webhooks/teams?tenant=t1 -X POST \
  -H "X-Event-ID: ev-123" -H "X-Signature: $SIG" -H 'Content-Type: application/json' \
  -d "$BODY"
```
4) Ver respostas coletadas
```
curl -s localhost:8000/collections/responses -H "Authorization: Bearer $TOKEN"
```
5) Configurar e usar IA (stub)
```
curl -s localhost:8000/integrations/ai/save -X POST -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  -d '{"provider":"stub","api_key":"none"}'
curl -s localhost:8000/ai/summarize -X POST -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  -d '{"text":"Resumo de exemplo muito longo..."}'
```

## Python (legado)
A versão anterior (FastAPI, SQLAlchemy, etc.) está em `legacy/`. Consulte o `legacy/Makefile` e `legacy/Dockerfile` para executar/testar a versão Python.
