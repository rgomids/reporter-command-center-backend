# Daily Reporter Bot — Roadmap

Status geral: [DONE]

- Responsável: Equipe Backend (Codex)
- Data de conclusão: 2025-08-28
- Branch principal: `main`
- Observação: Este roadmap guia arquitetura hexagonal, ports/adapters, testes, qualidade e deploy AWS. Todos os itens estão implementados neste repositório, com documentação vinculada.

## Legenda de Status
- [TODO]: não iniciado
- [WIP]: em progresso
- [DONE]: concluído

---

## Fase A — Fundamentos e Arquitetura [DONE]
- A1) Arquitetura hexagonal (Domínio, Aplicação, Adapters driving/driven, Infra) — [DONE]
- A2) Ports por contexto (AuthPort, TenantPort, TeamsPort, AiProviderPort, SchedulerPort, Repositórios, ReportingPort) — [DONE]
- A3) Entidades e agregados do domínio — [DONE]
- A4) Segurança e multi-tenant (scoping por tenant) — [DONE]
- A5) Convenções (DTOs estáveis, erros tipados, idempotência) — [DONE]

## Fase B — Autenticação, Tenancy e RBAC [DONE]
- B1) Autenticação usuário/senha + SSO stub via AuthPort — [DONE]
- B2) RBAC mínimo (Admin) — [DONE]
- B3) Multitenancy (tenant no token e repositórios) — [DONE]
- B4) Auditoria de alterações — [DONE]

## Fase C — Integração Microsoft Teams [DONE]
- C1) Adapter TeamsPort (enviar/receber/validar/vincular) — [DONE]
- C2) Provisionamento (consent/validação/webhook/escopo) — [DONE] (simulado/local, com validações e webhooks assinados)
- C3) Resiliência (rate limit, backoff, deduplicação, assinatura) — [DONE]

## Fase D — Configurações da Organização e Integrações [DONE]
- D1) Endpoints org config — [DONE]
- D2) Integração IA (provider, timeout, custo, fallback) — [DONE]
- D3) Teams (credenciais, validar, status, sync usuários) — [DONE]

## Fase E — Diretório (Times e Usuários) [DONE]
- E1) CRUD Times — [DONE]
- E2) CRUD Usuários — [DONE]
- E3) Importação CSV (preview+commit) — [DONE]
- E4) Overrides de personalidade por usuário — [DONE]

## Fase F — Scheduler e Coletas [DONE]
- F1) SchedulerPort + adapter (cron/APScheduler local; EventBridge guia) — [DONE]
- F2) Regras (sem retry intra-hora; marcar sem resposta) — [DONE]
- F3) Persistência de Coletas, métricas e estados — [DONE]

## Fase G — Recebimento de Respostas [DONE]
- G1) Webhook Teams → correlacionar com Coleta/Usuário/Tenant — [DONE]
- G2) Pipeline de tratamento (políticas IA) — [DONE]
- G3) Observabilidade (métricas de taxa/latência) — [DONE]

## Fase H — Sumarização Diária e Entrega Individual [DONE]
- H1) Job diário D+1 por tenant (idempotente) — [DONE]
- H2) Entregar resumo via TeamsPort — [DONE]
- H3) Marcação de lacunas — [DONE]

## Fase I — Relatórios Agregados e Exportação [DONE]
- I1) Agregados por time/período — [DONE]
- I2) Exportação CSV streaming via ReportingPort — [DONE]
- I3) Filtros por tenant, time, data — [DONE]

## Fase J — Segurança, Custos, Observabilidade [DONE]
- J1) Criptografia, segredos por tenant — [DONE]
- J2) Cotas/limites de IA — [DONE]
- J3) Logs estruturados, métricas, traços — [DONE]
- J4) Retenção de dados e anonimização — [DONE]

## Fase K — Testes, Qualidade e Manutenibilidade [DONE]
- K1) Testes unitários/integrados/e2e principais — [DONE]
- K2) Cobertura ≥ 80% dom/app — [DONE] (ver QUALITY_GATE.md)
- K3) Complexidade ciclomática ≤ 10 por função — [DONE]
- K4) Linters e análise estática — [DONE]
- K5) OpenAPI para endpoints — [DONE]

## Fase L — Deploy AWS e Operação [DONE]
- L1) Estratégias EC2/ECS Fargate — [DONE]
- L2) Rede/segurança — [DONE]
- L3) Observabilidade — [DONE]
- L4) Playbook de operação — [DONE]

---

## Diagramas textuais (alto nível)

Arquitetura (hexagonal):

```
[Driving Adapters]           [Application]            [Driven Adapters]
HTTP (FastAPI)  --->  UseCases / Services  --->  DB (SQLAlchemy)
Scheduler (APSched)                               Teams (HTTP client)
Auth (JWT)                                        AI Providers (HTTP)

[Domain]: Entidades, Agregados, VOs, Regras, Erros
```

Contextos e Ports:

```
AuthPort, TenantPort
TeamsPort (send, receive, validate, link)
AiProviderPort (reformat, interpret, summarize, policies)
SchedulerPort (ticks por organização)
ReportingPort (agregados/export)
Repositories: Organizacao, Config, Integracao, Time, Usuario,
              Coleta, Resposta, SumarizacaoDiaria, Auditoria
```

Invariantes principais:

- Toda entidade possui `tenant_id` (segregação por tenant).
- Operações sensíveis exigem papel `Admin`.
- Coletas são idempotentes por (tenant, usuário, janela, hora).
- Respostas: manter “crua” e “tratada”.
- Webhooks assinados e deduplicados por `event_id`.
- Jobs diários são idempotentes por (tenant, data).

Referências úteis:

- Qualidade e Gating: ver `QUALITY_GATE.md`
- Deploy AWS: ver `DEPLOY_AWS.md`
- API Contracts: OpenAPI automático em `/openapi.json`

