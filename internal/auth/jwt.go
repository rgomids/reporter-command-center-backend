package auth

import (
    "crypto/hmac"
    "crypto/sha256"
    "encoding/base64"
    "encoding/json"
    "errors"
    "strings"
    "time"

    "reporter-command-center-backend/internal/domain"
)

func encodeSegment(data []byte) string {
    return strings.TrimRight(base64.URLEncoding.EncodeToString(data), "=")
}

func decodeSegment(seg string) ([]byte, error) {
    // pad base64
    if m := len(seg) % 4; m != 0 {
        seg += strings.Repeat("=", 4-m)
    }
    return base64.URLEncoding.DecodeString(seg)
}

func Sign(claims domain.Claims, secret string, ttl time.Duration) (string, error) {
    now := time.Now().Unix()
    claims.Iat = now
    claims.Exp = time.Now().Add(ttl).Unix()

    header := map[string]string{"alg": "HS256", "typ": "JWT"}
    hb, _ := json.Marshal(header)
    cb, _ := json.Marshal(claims)
    h := encodeSegment(hb)
    c := encodeSegment(cb)
    signingInput := h + "." + c
    mac := hmac.New(sha256.New, []byte(secret))
    mac.Write([]byte(signingInput))
    sig := encodeSegment(mac.Sum(nil))
    return signingInput + "." + sig, nil
}

func Verify(token, secret string) (domain.Claims, error) {
    var empty domain.Claims
    parts := strings.Split(token, ".")
    if len(parts) != 3 {
        return empty, errors.New("invalid token")
    }
    mac := hmac.New(sha256.New, []byte(secret))
    mac.Write([]byte(parts[0] + "." + parts[1]))
    expected := encodeSegment(mac.Sum(nil))
    if !hmac.Equal([]byte(expected), []byte(parts[2])) {
        return empty, errors.New("invalid signature")
    }
    payload, err := decodeSegment(parts[1])
    if err != nil {
        return empty, err
    }
    var c domain.Claims
    if err := json.Unmarshal(payload, &c); err != nil {
        return empty, err
    }
    if time.Now().Unix() > c.Exp {
        return empty, errors.New("token expired")
    }
    return c, nil
}

