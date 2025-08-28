package httpx

import (
    "crypto/hmac"
    "crypto/sha256"
    "encoding/hex"
    "encoding/json"
    "io"
    "log"
    "net/http"
    "strings"
    "time"

    "reporter-command-center-backend/internal/auth"
    "reporter-command-center-backend/internal/config"
    "reporter-command-center-backend/internal/domain"
    "reporter-command-center-backend/internal/repo"
)

type Server struct {
    Cfg  config.Config
    Repo *repo.InMemory
}

func NewServer(cfg config.Config, r *repo.InMemory) *Server {
    return &Server{Cfg: cfg, Repo: r}
}

func writeJSON(w http.ResponseWriter, status int, v any) {
    w.Header().Set("Content-Type", "application/json")
    w.WriteHeader(status)
    _ = json.NewEncoder(w).Encode(v)
}

// Auth
type loginReq struct {
    TenantID string      `json:"tenant_id"`
    UserID   string      `json:"user_id"`
    Email    string      `json:"email"`
    Password string      `json:"password"`
    Role     domain.Role `json:"role"`
}

func (s *Server) Login(w http.ResponseWriter, r *http.Request) {
    var req loginReq
    if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
        http.Error(w, "bad request", http.StatusBadRequest)
        return
    }
    if req.TenantID == "" || req.UserID == "" || req.Email == "" {
        http.Error(w, "missing fields", http.StatusBadRequest)
        return
    }
    if req.Password == "" { // demo auth
        http.Error(w, "invalid credentials", http.StatusUnauthorized)
        return
    }
    if req.Role == "" {
        req.Role = domain.RoleAdmin
    }
    token, _ := auth.Sign(domain.Claims{
        TenantID: req.TenantID,
        UserID:   req.UserID,
        Email:    req.Email,
        Role:     req.Role,
    }, s.Cfg.JWTSecret, 24*time.Hour)
    writeJSON(w, http.StatusOK, map[string]string{"access_token": token})
}

func (s *Server) Session(w http.ResponseWriter, r *http.Request) {
    claims, ok := GetClaims(r)
    if !ok {
        http.Error(w, "no session", http.StatusUnauthorized)
        return
    }
    writeJSON(w, http.StatusOK, claims)
}

// Org config
func (s *Server) GetOrgConfig(w http.ResponseWriter, r *http.Request) {
    claims, _ := GetClaims(r)
    if cfg, ok := s.Repo.GetOrg(claims.TenantID); ok {
        writeJSON(w, http.StatusOK, cfg)
        return
    }
    writeJSON(w, http.StatusOK, domain.OrgConfig{TenantID: claims.TenantID})
}

func (s *Server) PutOrgConfig(w http.ResponseWriter, r *http.Request) {
    claims, _ := GetClaims(r)
    var body domain.OrgConfig
    if err := json.NewDecoder(r.Body).Decode(&body); err != nil {
        http.Error(w, "bad request", http.StatusBadRequest)
        return
    }
    body.TenantID = claims.TenantID
    s.Repo.SaveOrg(body)
    writeJSON(w, http.StatusOK, body)
}

// Teams integration validate/save/send
type teamsCreds struct {
    AppID         string `json:"app_id"`
    AppSecret     string `json:"app_secret"`
    WebhookSecret string `json:"webhook_secret"`
}

func (s *Server) TeamsValidate(w http.ResponseWriter, r *http.Request) {
    var req teamsCreds
    if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
        http.Error(w, "bad request", http.StatusBadRequest)
        return
    }
    valid := req.AppID != "" && req.AppSecret != "" && req.WebhookSecret != ""
    writeJSON(w, http.StatusOK, map[string]any{"valid": valid})
}

func (s *Server) TeamsSave(w http.ResponseWriter, r *http.Request) {
    claims, _ := GetClaims(r)
    var req teamsCreds
    if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
        http.Error(w, "bad request", http.StatusBadRequest)
        return
    }
    s.Repo.SaveTeams(domain.TeamsIntegration{
        TenantID:      claims.TenantID,
        AppID:         req.AppID,
        AppSecret:     req.AppSecret,
        WebhookSecret: req.WebhookSecret,
        Status:        "configured",
    })
    writeJSON(w, http.StatusOK, map[string]string{"status": "saved"})
}

type sendReq struct {
    ChannelID string `json:"channel_id"`
    Text      string `json:"text"`
}

func (s *Server) TeamsSend(w http.ResponseWriter, r *http.Request) {
    claims, _ := GetClaims(r)
    var req sendReq
    if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
        http.Error(w, "bad request", http.StatusBadRequest)
        return
    }
    // Simulate send by logging
    log.Printf("[TeamsSend] tenant=%s channel=%s text=%q", claims.TenantID, req.ChannelID, req.Text)
    writeJSON(w, http.StatusOK, map[string]string{"status": "sent"})
}

// Webhook (Teams) with HMAC signature and dedup
func (s *Server) TeamsWebhook(w http.ResponseWriter, r *http.Request) {
    // event id and signature headers
    eventID := r.Header.Get("X-Event-ID")
    sig := r.Header.Get("X-Signature")
    tenant := r.URL.Query().Get("tenant")
    if tenant == "" {
        http.Error(w, "missing tenant", http.StatusBadRequest)
        return
    }
    cfg, ok := s.Repo.GetTeams(tenant)
    if !ok {
        http.Error(w, "integration not configured", http.StatusNotFound)
        return
    }
    // read raw body
    raw, _ := io.ReadAll(r.Body)
    // verify signature: hex( HMAC-SHA256(body, webhook_secret) )
    mac := hmac.New(sha256.New, []byte(cfg.WebhookSecret))
    mac.Write(raw)
    expected := hex.EncodeToString(mac.Sum(nil))
    if !hmac.Equal([]byte(strings.ToLower(expected)), []byte(strings.ToLower(sig))) {
        http.Error(w, "invalid signature", http.StatusUnauthorized)
        return
    }
    if eventID != "" && s.Repo.SeenEvent(eventID) {
        writeJSON(w, http.StatusOK, map[string]string{"status": "duplicate"})
        return
    }
    if eventID != "" {
        s.Repo.MarkEvent(eventID)
    }
    // parse payload
    var msg domain.TeamsMessage
    if err := json.Unmarshal(raw, &msg); err != nil {
        http.Error(w, "bad payload", http.StatusBadRequest)
        return
    }
    s.Repo.AddResponse(tenant, msg)
    writeJSON(w, http.StatusOK, map[string]string{"status": "received"})
}

func (s *Server) ListResponses(w http.ResponseWriter, r *http.Request) {
    claims, _ := GetClaims(r)
    msgs := s.Repo.ListResponses(claims.TenantID)
    writeJSON(w, http.StatusOK, msgs)
}

// AI integration save config and summarize (stub)
type aiSaveReq struct {
    Provider string `json:"provider"`
    ApiKey   string `json:"api_key"`
}

func (s *Server) AISave(w http.ResponseWriter, r *http.Request) {
    claims, _ := GetClaims(r)
    var req aiSaveReq
    if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
        http.Error(w, "bad request", http.StatusBadRequest)
        return
    }
    s.Repo.SaveAI(domain.AIConfig{TenantID: claims.TenantID, Provider: req.Provider, ApiKey: req.ApiKey})
    writeJSON(w, http.StatusOK, map[string]string{"status": "saved"})
}

type aiSummarizeReq struct {
    Text string `json:"text"`
}
type aiSummarizeResp struct {
    Summary string `json:"summary"`
}

func naiveSummary(s string) string {
    s = strings.TrimSpace(s)
    if len(s) <= 240 {
        return s
    }
    return s[:240] + "..."
}

func (s *Server) AISummarize(w http.ResponseWriter, r *http.Request) {
    claims, _ := GetClaims(r)
    if _, ok := s.Repo.GetAI(claims.TenantID); !ok {
        http.Error(w, "ai not configured", http.StatusBadRequest)
        return
    }
    var req aiSummarizeReq
    if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
        http.Error(w, "bad request", http.StatusBadRequest)
        return
    }
    writeJSON(w, http.StatusOK, aiSummarizeResp{Summary: naiveSummary(req.Text)})
}
