package domain

import "time"

type Role string

const (
    RoleAdmin Role = "admin"
    RoleUser  Role = "user"
)

type Claims struct {
    TenantID string `json:"tenant_id"`
    UserID   string `json:"user_id"`
    Email    string `json:"email"`
    Role     Role   `json:"role"`
    Iat      int64  `json:"iat"`
    Exp      int64  `json:"exp"`
}

type OrgConfig struct {
    TenantID       string    `json:"tenant_id"`
    Nome           string    `json:"nome"`
    Fuso           string    `json:"fuso"`
    JanelaInicio   string    `json:"janela_inicio"`
    JanelaFim      string    `json:"janela_fim"`
    FrequenciaHoras int      `json:"frequencia_horas"`
    FlagsIA        map[string]any `json:"flags_ia"`
    PrePrompt      string    `json:"pre_prompt"`
    UpdatedAt      time.Time `json:"updated_at"`
}

type TeamsIntegration struct {
    TenantID      string `json:"tenant_id"`
    AppID         string `json:"app_id"`
    AppSecret     string `json:"app_secret"`
    WebhookSecret string `json:"webhook_secret"`
    Status        string `json:"status"`
}

type TeamsMessage struct {
    ChannelID string `json:"channel_id"`
    UserID    string `json:"user_id"`
    Text      string `json:"text"`
}

type AIConfig struct {
    TenantID string `json:"tenant_id"`
    Provider string `json:"provider"`
    ApiKey   string `json:"api_key"`
}
