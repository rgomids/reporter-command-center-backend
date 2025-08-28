package main

import (
    "context"
    "fmt"
    "log"
    "net/http"
    "os"
    "os/signal"
    "syscall"
    "time"

    "github.com/go-chi/chi/v5"
    "github.com/go-chi/chi/v5/middleware"

    "reporter-command-center-backend/internal/config"
    httpx "reporter-command-center-backend/internal/http"
    "reporter-command-center-backend/internal/repo"
)

func main() {
    cfg := config.FromEnv()
    store := repo.NewInMemory()
    srv := httpx.NewServer(cfg, store)

    r := chi.NewRouter()
    r.Use(middleware.RealIP)
    r.Use(middleware.RequestID)
    r.Use(middleware.Logger)
    r.Use(middleware.Recoverer)
    r.Use(httpx.WithAuth(cfg))

    r.Get("/", func(w http.ResponseWriter, r *http.Request) {
        w.Header().Set("Content-Type", "application/json")
        _, _ = w.Write([]byte(`{"service":"reporter-command-center-backend","status":"ok"}`))
    })
    r.Get("/healthz", func(w http.ResponseWriter, r *http.Request) {
        w.WriteHeader(http.StatusOK)
        _, _ = w.Write([]byte("ok"))
    })

    // Auth
    r.Post("/auth/login", srv.Login)
    r.Get("/auth/session", srv.Session)

    // Org config
    r.Get("/org/config", srv.GetOrgConfig)
    r.Put("/org/config", srv.PutOrgConfig)

    // Integrations - Teams
    r.Post("/integrations/teams/validate", srv.TeamsValidate)
    r.Post("/integrations/teams/save", srv.TeamsSave)
    r.Post("/integrations/teams/send", srv.TeamsSend)

    // Integrations - AI
    r.Post("/integrations/ai/save", srv.AISave)
    r.Post("/ai/summarize", srv.AISummarize)

    // Webhooks (no auth)
    r.Post("/webhooks/teams", srv.TeamsWebhook)

    // Debug: list collected responses per tenant
    r.Get("/collections/responses", srv.ListResponses)

    addr := fmt.Sprintf(":%s", cfg.Port)
    srvHTTP := &http.Server{Addr: addr, Handler: r}

    // start server
    go func() {
        log.Printf("Go server listening on %s", addr)
        if err := srvHTTP.ListenAndServe(); err != nil && err != http.ErrServerClosed {
            log.Fatalf("server error: %v", err)
        }
    }()

    // graceful shutdown on SIGINT/SIGTERM
    stop := make(chan os.Signal, 1)
    signal.Notify(stop, syscall.SIGINT, syscall.SIGTERM)
    <-stop
    log.Printf("Shutting down...")
    ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
    defer cancel()
    if err := srvHTTP.Shutdown(ctx); err != nil {
        log.Printf("graceful shutdown failed: %v", err)
    }
    log.Printf("Server stopped")
}
