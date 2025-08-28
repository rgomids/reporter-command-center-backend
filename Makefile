.PHONY: build run tidy test

build:
	go build -o bin/server ./cmd/server

run:
	PORT=$${PORT:-8000} go run ./cmd/server

tidy:
	go mod tidy

test:
	go test ./...

