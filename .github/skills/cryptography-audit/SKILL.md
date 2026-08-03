---
name: cryptography-audit
description: 'Perform an automated, strictly-scoped cryptographic security audit across codebases. Follows a systematic 3-stage methodology: 1) Construction of Cryptographic Security Checklist (algorithms, key management, secrets management, and data storage/transport encryption), 2) Deep Code & Configuration Inspection (weak ciphers like MD5/SHA1, hardcoded secrets, weak random number generators, insecure password hashing, session secret entropy), and 3) Generation of 2 Markdown Reports (Checklist & Findings Audit Report). Strictly scoped to cryptographic controls only.'
argument-hint: 'Path to target repository or app directory (e.g., ./app, c:/workspace/bridge_troll, or c:/workspace/bhima)'
user-invocable: true
---

# Cryptographic Security Audit Skill

This skill provides a systematic procedure for auditing codebases specifically for **Cryptographic Controls, Key Management, Password Hashing, and Storage/Transport Encryption**.

---

## 🛑 STRICT SCOPE CONSTRAINT

> **CRITICAL MANDATE**: This skill is **STRICTLY CONSTRAINED** to cryptographic algorithms, cipher suite strength, key management, secrets handling, password hashing functions, random number generation entropy, and storage/transport encryption.
>
> **DO NOT DRIFT** into auditing other vulnerability categories (e.g., Authorization/Access Control, SQL Injection, XSS, CSRF, Unsanitized Shell Commands, Dependency CVEs) unless they directly result from cryptographic key or token compromise. Disregard non-cryptographic findings to keep the report high-precision and laser-focused on Cryptographic Security.

---

## 1. Audit Workflow Overview

The audit follows a strict 3-stage process:

```
┌──────────────────────────────────────────────────────────┐
│ 1. Construct Cryptographic Security Checklist             │
│    (Algorithms, Key Management, Password Hashing, Storage)│
└────────────────────────────┬─────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────┐
│ 2. Execute Code & Configuration Inspection               │
│    (Secret Keys, Random Generators, Hashing, Transport)  │
└────────────────────────────┬─────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────┐
│ 3. Generate 2 Mandatory Markdown Audit Reports           │
│    (Crypto Checklist & Crypto Audit Findings Report)     │
└──────────────────────────────────────────────────────────┘
```

---

## 2. Stage 1: Construct Comprehensive Cryptographic Checklist

Analyze the application architecture, initializers, configuration files, and cryptographic libraries (e.g., `Bcrypt`, `Argon2`, `OpenSSL`, `crypto`, `Devise.secret_key`, `SECRET_KEY_BASE`) to build an audit checklist across 4 key pillars:

### A. Cryptographic Algorithms & Ciphers
- [ ] **Password Hashing Algorithms**: Verify password hashing uses adaptive, salted algorithms (`Bcrypt`, `Argon2id`, `scrypt`, `PBKDF2`) with adequate work factors (e.g., Bcrypt cost ≥ 10/12). Confirm obsolete algorithms (`MD5`, `SHA1`, unsalted `SHA256`) are NOT used for credentials.
- [ ] **Symmetric & Asymmetric Encryption Ciphers**: Verify symmetric encryption uses modern ciphers (`AES-256-GCM`, `ChaCha20-Poly1305`) and asymmetric ciphers use adequate key lengths (`RSA ≥ 2048-bit`, `ECDSA P-256/Ed25519`). Confirm outdated stream/block ciphers (`RC4`, `DES`, `3DES`, `Blowfish`, `ECB mode`) are disabled.
- [ ] **Cryptographic Hash Functions for Tokens**: Confirm token generation and checksum verification use secure hash functions (`SHA256`, `SHA512`, `BLAKE2`) rather than collision-prone `MD5` or `SHA1`.

### B. Secrets & Key Management
- [ ] **Hardcoded Secrets & Fallback Keys**: Inspect configuration initializers (`secret_key`, `SECRET_KEY_BASE`, `JWT_SECRET`, `SESS_SECRET`) to ensure secret keys are loaded exclusively from environment variables (`ENV['SECRET_KEY']`) and do NOT fall back to hardcoded strings or predictable defaults.
- [ ] **Cryptographic Randomness (CWE-330)**: Verify random tokens (session IDs, password reset tokens, OAuth state tokens) are generated using cryptographically secure pseudorandom number generators (`SecureRandom`, `crypto.randomBytes`, `java.security.SecureRandom`) rather than non-cryptographic PRNGs (`rand()`, `Math.random()`).
- [ ] **Secret Storage & Rotation**: Verify private keys, API secrets, and encryption keys are stored securely outside source control and support rotation workflows.

### C. Storage & Transport Encryption
- [ ] **Transport Layer Security (TLS / SSL)**: Verify `config.force_ssl = true` is enforced in production. Confirm HSTS (`Strict-Transport-Security`) headers and secure cookies are configured.
- [ ] **Database & File Storage Encryption**: Verify sensitive PII/PHI or financial data stored at rest uses column-level or storage-level encryption.

---

## 3. Stage 2: Code Review & Implementation Inspection

Systematically inspect the codebase for cryptographic controls.

### Targeted Inspection Areas:

#### 1. Configuration Initializers & Environment Setup
- Inspect Rails initializers (`config/initializers/devise.rb`, `config/initializers/session_store.rb`, `config/initializers/secret_token.rb`, `config/environments/production.rb`), Express setup (`config/express.js`, `jwt.js`), or Django `settings.py`.
- Search for fallback secret keys, low Bcrypt stretch iterations, and HTTP/SSL configurations.

#### 2. Password & Token Generation Services
- Inspect user authentication models (`app/models/user.rb`), password reset services, and OAuth helpers.
- Search for custom hashing logic, `Digest::MD5`, `Digest::SHA1`, or non-cryptographic `rand()` usages.

---

## 4. Stage 3: Output Report Requirements & Persistence

To ensure complete, modular documentation, running this skill **MUST MANDATORILY GENERATE 2 SEPARATE MARKDOWN REPORTS** in the target directory (e.g. `scripts/extras/exercise-20/` or `docs/`):

1. **Cryptographic Security Review Checklist**: `<app_name>_cryptography_checklist.md`
2. **Cryptographic Security Audit Findings Report**: `<app_name>_cryptography_audit.md`

> **Note**: Do NOT combine checklist and findings into a single file. Generate both files below.

---

### Report 1 Template: `<app_name>_cryptography_checklist.md`

```markdown
# Application Cryptographic Security Review Checklist

## Application: `<App Name>`
- **Assessed Commit**: `#<commit_hash>`

---

## 1. Cryptographic Algorithms & Ciphers Checklist
- [ ] **Password Hashing**: Confirm Bcrypt/Argon2 is used with proper work factor; verify MD5/SHA1 is avoided.
- [ ] **Encryption Ciphers**: Verify AES-256-GCM or equivalent modern ciphers; confirm RC4/DES/ECB are disabled.

## 2. Secrets & Key Management Checklist
- [ ] **Environment Secret Loading**: Confirm `SECRET_KEY_BASE` and `DEVISE_SECRET_KEY` load from `ENV` without hardcoded fallbacks.
- [ ] **Cryptographic PRNG**: Confirm tokens use `SecureRandom` or `crypto.randomBytes`.

## 3. Transport & Storage Encryption Checklist
- [ ] **TLS Enforcement**: Confirm `config.force_ssl = true` and HSTS headers in production.
- [ ] **Cookie Security**: Verify `Secure` and `HttpOnly` flags on session cookies.
```

---

### Report 2 Template: `<app_name>_cryptography_audit.md`

```markdown
# Cryptographic Security Audit Findings Report

## Application: `<App Name>`
- **Assessed Commit**: `#<commit_hash>`

---

## 1. Cryptographic Architecture Summary

| Security Area | Implementation / Configuration | Audit Result | Status |
| :--- | :--- | :--- | :---: |
| **Password Hashing** | `Bcrypt` (stretches: 10/12) | Adaptive Hashing Verified | ✅ |
| **Secret Key Entropy** | `ENV['SECRET_KEY']` loading | Secret Key Audit | ⚠️ / ✅ |
| **PRNG Entropy** | `SecureRandom` / `crypto.randomBytes` | Cryptographic PRNG Verified | ✅ |
| **Transport Encryption** | `config.force_ssl = true` / HSTS | TLS Enforcement | ⚠️ / ✅ |

---

## 2. Confirmed Cryptographic Vulnerabilities

### 🔴 Finding 1: `<Vulnerability Title>` (`<CWE ID>`)
* **Vulnerability Type**: Hardcoded Secret Key / Weak Hashing Algorithm / Non-Cryptographic PRNG
* **Severity Rating**: `CRITICAL` | `HIGH` | `MEDIUM` | `LOW`
* **File Location**: `<file_path>:<line_numbers>`
* **Vulnerable Code**:
  ```<language>
  // Vulnerable cryptographic code or configuration
  ```
* **Flaw Analysis**: Technical breakdown of why the cryptographic mechanism or secret key is insecure.
* **Remediation**:
  1. `<Step 1 code or configuration fix>`
  2. `<Step 2 secure pattern implementation>`

---

## 3. Verified Secure Cryptographic Controls

* **`<Control Name>`** (`<file_path>:<line_numbers>`): Verified secure implementation of `<crypto mechanism>`.
```
