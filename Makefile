
SHELL := /bin/bash
.DEFAULT_GOAL := help

APP_NAME := reporter-command-center-backend
BIN_DIR := bin
BIN := $(BIN_DIR)/server
GOLANGCI_LINT_VERSION ?= v1.59.1
COVERAGE_FILE := coverage.out
COVERAGE_THRESHOLD ?= 0

.PHONY: help build run tidy test test-coverage fmt fmt-check vet lint quality qa docker-build docker-run compose-up compose-down compose-logs clean

help: ## Mostrar ajuda com alvos disponíveis
	@grep -E '^[a-zA-Z_-]+:.*?##' $(MAKEFILE_LIST) | sed -e 's/:.*##/\t- /' -e 's/^[^ ]* //'

build: ## Compilar o binário em $(BIN)
	@mkdir -p $(BIN_DIR)
	go build -o $(BIN) ./cmd/server

run: ## Executar o servidor localmente (PORT=8000 padrão)
	PORT=$${PORT:-8000} go run ./cmd/server

tidy: ## Organizar dependências
	go mod tidy

fmt: ## Formatador (gofmt -s -w)
	gofmt -s -w .

fmt-check: ## Verificar formatação (falha se arquivos não formatados)
	@diff=$$(gofmt -s -l .); \
	if [[ -n "$$diff" ]]; then \
	  echo "Arquivos não formatados:"; echo "$$diff"; \
	  exit 1; \
	fi

vet: ## Análises estáticas do Go (go vet)
	go vet ./...

lint: ## Lint com golangci-lint (usa binário local ou container)
	@if command -v golangci-lint >/dev/null 2>&1; then \
	  golangci-lint run ./...; \
	else \
	  docker run --rm -v $$PWD:/app -w /app golangci/golangci-lint:$(GOLANGCI_LINT_VERSION) golangci-lint run ./...; \
	fi

test: ## Executar testes
	go test ./...

test-coverage: ## Testes com cobertura + verificação de threshold
	go test -coverprofile=$(COVERAGE_FILE) ./...
	@total=$$(go tool cover -func=$(COVERAGE_FILE) | tail -n1 | awk '{print $$3}' | sed 's/%//'); \
	echo "Cobertura total: $$total% (threshold: $(COVERAGE_THRESHOLD)%)"; \
	awk 'BEGIN { exit !('"$$total"' + 0 >= '"$(COVERAGE_THRESHOLD)"' + 0) }' /dev/null || \
	 (echo "Falha: cobertura abaixo do limite" && exit 1)

quality: fmt-check vet lint test-coverage ## Quality gate (formatação, vet, lint, cobertura)
qa: quality ## Alias para quality

docker-build: ## Build da imagem do backend
	docker build -t $(APP_NAME):latest .

docker-run: ## Executa imagem local do backend (porta 8000)
	docker run --rm -e PORT=8000 -e JWT_SECRET=dev -e CORS_ALLOWED_ORIGINS=http://localhost:8080 -p 8000:8000 $(APP_NAME):latest

compose-up: ## Sobe stack completa (db, backend, frontend)
	docker compose up -d --build

compose-down: ## Derruba stack completa
	docker compose down -v

compose-logs: ## Logs agrupados dos serviços
	docker compose logs -f

clean: ## Limpar artefatos
	rm -rf $(BIN_DIR) $(COVERAGE_FILE)
