# Daily Reporter Bot — Backend

Arquitetura hexagonal (Domínio, Aplicação, Adapters, Infra) com FastAPI e SQLAlchemy. Implementa autenticação JWT multi-tenant, RBAC mínimo, integrações (Teams/IA via ports), scheduler local, coleta e respostas, sumarização diária, relatórios e exportação CSV, auditoria, e qualidade com testes, cobertura e complexidade ciclomática.

Links úteis:
- ROADMAP: `ROADMAP.md`
- Deploy AWS: `DEPLOY_AWS.md`
- Quality gate: `QUALITY_GATE.md`

## Requisitos
- Python 3.11+
- pip

## Instalação
```
cp .env.example .env
pip install -r requirements.txt
```

## Execução (dev)
```
make dev
# API: http://localhost:8000
# OpenAPI: http://localhost:8000/docs
```

## Testes e qualidade
```
make test      # cobertura
make cc        # complexidade ciclomática
make lint      # ruff
make typecheck # mypy
make quality   # tudo acima
```

## Endpoints principais
- Auth: POST `/auth/login`, GET `/auth/session`
- Org Config: GET/PUT `/org/config`
- Integrations: Teams (validate/save/sync), AI (save)
- Directory: CRUD Teams (`/teams`), CRUD Users (`/users`), Import (`/users/import`)
- Collection: GET `/collections/ticks`, POST `/webhooks/teams`
- Reporting: GET `/reports/aggregate`, GET `/reports/export`
- Admin/Audit: GET `/admin/audit`
