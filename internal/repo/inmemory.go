package repo

import (
    "sync"
    "time"

    "reporter-command-center-backend/internal/domain"
)

type InMemory struct {
    mu sync.RWMutex

    orgs          map[string]domain.OrgConfig              // by tenant
    teamsIntegr   map[string]domain.TeamsIntegration       // by tenant
    aiConfig      map[string]domain.AIConfig               // by tenant
    webhookSeen   map[string]time.Time                     // event id -> seen at
    responses     map[string][]domain.TeamsMessage         // tenant -> msgs
}

func NewInMemory() *InMemory {
    return &InMemory{
        orgs:        make(map[string]domain.OrgConfig),
        teamsIntegr: make(map[string]domain.TeamsIntegration),
        aiConfig:    make(map[string]domain.AIConfig),
        webhookSeen: make(map[string]time.Time),
        responses:   make(map[string][]domain.TeamsMessage),
    }
}

// Org config
func (m *InMemory) GetOrg(tid string) (domain.OrgConfig, bool) {
    m.mu.RLock(); defer m.mu.RUnlock()
    v, ok := m.orgs[tid]
    return v, ok
}
func (m *InMemory) SaveOrg(cfg domain.OrgConfig) {
    m.mu.Lock(); defer m.mu.Unlock()
    cfg.UpdatedAt = time.Now()
    m.orgs[cfg.TenantID] = cfg
}

// Teams integration
func (m *InMemory) GetTeams(tid string) (domain.TeamsIntegration, bool) {
    m.mu.RLock(); defer m.mu.RUnlock()
    v, ok := m.teamsIntegr[tid]
    return v, ok
}
func (m *InMemory) SaveTeams(t domain.TeamsIntegration) {
    m.mu.Lock(); defer m.mu.Unlock()
    m.teamsIntegr[t.TenantID] = t
}

// AI config
func (m *InMemory) SaveAI(c domain.AIConfig) {
    m.mu.Lock(); defer m.mu.Unlock()
    m.aiConfig[c.TenantID] = c
}
func (m *InMemory) GetAI(tid string) (domain.AIConfig, bool) {
    m.mu.RLock(); defer m.mu.RUnlock()
    v, ok := m.aiConfig[tid]
    return v, ok
}

// Webhook dedup
func (m *InMemory) SeenEvent(eid string) bool {
    m.mu.RLock(); defer m.mu.RUnlock()
    _, ok := m.webhookSeen[eid]
    return ok
}
func (m *InMemory) MarkEvent(eid string) {
    m.mu.Lock(); defer m.mu.Unlock()
    m.webhookSeen[eid] = time.Now()
}

// Responses
func (m *InMemory) AddResponse(tid string, msg domain.TeamsMessage) {
    m.mu.Lock(); defer m.mu.Unlock()
    m.responses[tid] = append(m.responses[tid], msg)
}
func (m *InMemory) ListResponses(tid string) []domain.TeamsMessage {
    m.mu.RLock(); defer m.mu.RUnlock()
    return append([]domain.TeamsMessage(nil), m.responses[tid]...)
}
