## Build stage
FROM golang:1.22-alpine AS builder
WORKDIR /app

# Enable static build for minimal runtime image
ENV CGO_ENABLED=0 GOOS=linux GOARCH=amd64

COPY go.mod ./
RUN go mod download || true

COPY . .
RUN go build -o /out/server ./cmd/server

## Runtime stage
FROM alpine:3.20
WORKDIR /app

ENV PORT=8000
COPY --from=builder /out/server /usr/local/bin/server

EXPOSE 8000
CMD ["/usr/local/bin/server"]

