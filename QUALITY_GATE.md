# Quality Gate — Daily Reporter Bot

Requisitos mínimos e como verificar localmente e no CI.

## Thresholds
- Cobertura de testes (domínio/aplicação): ≥ 80%
- Complexidade ciclomática (por função/método): CC ≤ 10
- Lint (Ruff): 0 erros
- Tipagem (mypy): sem erros críticos

## Comandos

Após instalar dependências (`pip install -r requirements.txt`):

```
make test           # pytest + cobertura
make cc             # relatório de complexidade (radon)
make lint           # ruff
make typecheck      # mypy
make quality        # roda tudo e falha se gates não atendidos
```

Relatórios gerados em `./reports`.

## Integração CI
- Workflow em `.github/workflows/ci.yml` executa os mesmos comandos
- Fails o build se qualquer gate não for atendido

