package config

import (
    "os"
)

type Config struct {
    Port       string
    JWTSecret  string
    CORSAllowedOrigins string
}

func FromEnv() Config {
    return Config{
        Port:               getenv("PORT", "8000"),
        JWTSecret:          getenv("JWT_SECRET", "dev-secret-change-me"),
        CORSAllowedOrigins: getenv("CORS_ALLOWED_ORIGINS", "*"),
    }
}

func getenv(key, def string) string {
    if v := os.Getenv(key); v != "" {
        return v
    }
    return def
}
