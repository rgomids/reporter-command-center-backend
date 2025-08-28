# Deploy na AWS — Daily Reporter Bot

Este guia cobre duas estratégias de deploy: EC2 simples e ECS Fargate (recomendado). Inclui RDS (Postgres), EventBridge (scheduler), S3 (exports), Secrets Manager (segredos), e ALB (tráfego).

## Pré-requisitos
- AWS CLI configurado e credenciais com acesso a: EC2, ECS, ECR, RDS, IAM, S3, CloudWatch, EventBridge, Secrets Manager, VPC/ELB
- Docker e docker-compose
- Repositório com `Dockerfile`

## Variáveis de ambiente principais

```
APP_ENV=prod
PORT=8000
DATABASE_URL=postgresql+psycopg://user:pass@host:5432/dbname
JWT_SECRET=<segredo forte>
JWT_AUDIENCE=daily-reporter
JWT_ISSUER=https://your-issuer
TEAMS_WEBHOOK_SECRET=<assinatura webhooks>
DEFAULT_TIMEZONE=America/Sao_Paulo
OPENAI_API_KEY_REF=secretsmanager://tenant/<tenant_id>/openai
``` 

## Opção 1: EC2 (simples)
1) Criar VPC + subnets públicas (app) e privadas (RDS)
2) Criar Security Groups mínimos (ALB→EC2: 443/80; EC2→RDS: 5432)
3) RDS Postgres (subnets privadas, SG apenas de EC2)
4) EC2 (Amazon Linux 2023):
   - Instalar Docker e docker-compose
   - Provisionar `.env` com segredos (ZIP/SSM Parameter Store)
   - Executar: `docker-compose -f deploy/docker-compose.ec2.yml up -d`
5) ALB + Target Group apontando para EC2:8000 (healthcheck `/healthz`)
6) TLS: ACM + Listener 443 → TG
7) CloudWatch Logs: configurar `awslogs` ou fluentbit

## Opção 2: ECS Fargate (recomendado)
1) ECR: `aws ecr create-repository --repository-name daily-reporter`
2) Build & Push:
   - `docker build -t daily-reporter:latest .`
   - `docker tag daily-reporter:latest <ACCOUNT>.dkr.ecr.<REGION>.amazonaws.com/daily-reporter:latest`
   - `aws ecr get-login-password | docker login --username AWS --password-stdin <ACCOUNT>.dkr.ecr.<REGION>.amazonaws.com`
   - `docker push <ACCOUNT>.dkr.ecr.<REGION>.amazonaws.com/daily-reporter:latest`
3) VPC + Subnets públicas (ALB) e privadas (Fargate, RDS)
4) RDS Postgres (como acima)
5) Criar ECS Cluster (Fargate)
6) Task Definition:
   - Container image: ECR URI
   - CPU/Mem: 0.25 vCPU / 512MB (inicial)
   - Port mapping: 8000
   - Env vars de Secrets Manager (IAM Task Role com permissões para `secretsmanager:GetSecretValue`)
   - Log driver: awslogs
7) Service (Fargate): AutoScaling 1–3 tasks, subnets privadas, SG apenas do ALB
8) ALB + Target Group + Listener 443
9) EventBridge Scheduler: regras cron para invocar endpoint interno (ou SQS) p/ ticks

## Scheduler (EventBridge)
- Crie uma Rule por fuso/tenant (ou agregue e filtre no app) que dispare para API Gateway/ALB → `/internal/scheduler/tick` com header assinatura.
- Alternativamente, use EventBridge → SQS → Consumer no app.

## S3 (Exportação)
- Bucket privado `daily-reporter-exports` com política de retenção.
- O app grava CSV por streaming com chaves `tenant/<id>/exports/<data>.csv`.

## Secrets Manager
- Armazene segredos por tenant: `tenant/<tenant_id>/openai`, `tenant/<tenant_id>/teams`.
- O app resolve URIs `secretsmanager://...` via IAM.

## Observabilidade
- CloudWatch Logs: `daily-reporter/app`
- Datapoints: métricas custom (taxa de resposta, latência de IA, erros de webhook)
- Alarmes: taxa de erro 5xx, latência p95 > X ms, custo IA > cota

## Backup/Restore
- RDS snapshots automáticos
- Exportações S3 versionadas + lifecycle rules
- Playbook de restore: apontar app para réplicas/restore e reprovisionar scheduler

## Zero-downtime deploy
- ECS rolling update com healthchecks
- EC2: `docker-compose pull && docker-compose up -d` com ALB drenando conexões

## Segurança
- TLS obrigatório, SGs mínimos, WAF opcional
- Criptografia em trânsito (TLS) e repouso (RDS, S3)
- Rotação de segredos e chaves (Secrets Manager)

