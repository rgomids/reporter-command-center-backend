package httpx

import (
    "context"
    "net/http"
    "strings"

    "reporter-command-center-backend/internal/auth"
    "reporter-command-center-backend/internal/config"
    "reporter-command-center-backend/internal/domain"
)

type ctxKey string

const ClaimsKey ctxKey = "claims"

func WithAuth(cfg config.Config) func(http.Handler) http.Handler {
    return func(next http.Handler) http.Handler {
        return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
            // allow unauthenticated for health, root, login and webhooks
            if r.URL.Path == "/" || r.URL.Path == "/healthz" || r.URL.Path == "/auth/login" || strings.HasPrefix(r.URL.Path, "/webhooks/") {
                next.ServeHTTP(w, r)
                return
            }
            authz := r.Header.Get("Authorization")
            if authz == "" || !strings.HasPrefix(authz, "Bearer ") {
                http.Error(w, "missing bearer token", http.StatusUnauthorized)
                return
            }
            token := strings.TrimPrefix(authz, "Bearer ")
            claims, err := auth.Verify(token, cfg.JWTSecret)
            if err != nil {
                http.Error(w, "invalid token", http.StatusUnauthorized)
                return
            }
            ctx := context.WithValue(r.Context(), ClaimsKey, claims)
            next.ServeHTTP(w, r.WithContext(ctx))
        })
    }
}

func GetClaims(r *http.Request) (domain.Claims, bool) {
    v := r.Context().Value(ClaimsKey)
    if v == nil {
        return domain.Claims{}, false
    }
    c, ok := v.(domain.Claims)
    return c, ok
}

// WithCORS adds permissive CORS headers and handles preflight.
// Allowed origins can be configured via cfg.CORSAllowedOrigins (comma-separated) or "*".
func WithCORS(cfg config.Config) func(http.Handler) http.Handler {
    allowed := strings.Split(cfg.CORSAllowedOrigins, ",")
    for i := range allowed {
        allowed[i] = strings.TrimSpace(allowed[i])
    }
    return func(next http.Handler) http.Handler {
        return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
            origin := r.Header.Get("Origin")
            allowOrigin := ""
            if cfg.CORSAllowedOrigins == "*" {
                allowOrigin = "*"
            } else {
                for _, o := range allowed {
                    if o == origin {
                        allowOrigin = origin
                        break
                    }
                }
            }
            if allowOrigin != "" {
                w.Header().Set("Access-Control-Allow-Origin", allowOrigin)
                w.Header().Set("Vary", "Origin")
            }
            w.Header().Set("Access-Control-Allow-Credentials", "true")
            w.Header().Set("Access-Control-Allow-Headers", "Authorization, Content-Type, X-Requested-With")
            w.Header().Set("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")

            if r.Method == http.MethodOptions {
                w.WriteHeader(http.StatusNoContent)
                return
            }
            next.ServeHTTP(w, r)
        })
    }
}
