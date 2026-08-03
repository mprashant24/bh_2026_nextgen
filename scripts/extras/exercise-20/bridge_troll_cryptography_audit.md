# Bridge Troll — Cryptographic Security Audit Findings Report

We assessed commit `#40747c6510014958c9519d3708b5dc9325a0cc1c`

This report was generated using the **Cryptographic Security Audit Skill** (`cryptography-audit`) to document verified cryptographic algorithms, key management vulnerabilities, and transport security controls in the Bridge Troll application (`c:/workspace/bridge_troll`).

---

## 1. Cryptographic Architecture Summary

| Security Area | Implementation / Configuration | Audit Result | Status |
| :--- | :--- | :--- | :---: |
| **Password Hashing** | `Bcrypt` (stretches: 10) | Standard Devise Hashing | ✅ |
| **Secret Key Entropy** | `ENV['DEVISE_SECRET_KEY']` with fallback | **Hardcoded Fallback Secret Key** | ⚠️ **CRITICAL** |
| **PRNG Entropy** | `SecureRandom` (Standard Ruby/Rails) | Cryptographic PRNG Verified | ✅ |
| **Transport Encryption** | `config.force_ssl = true` / HSTS | TLS Enforcement Active | ✅ |

---

## 2. Confirmed Cryptographic Vulnerabilities

### 🔴 Finding 1: Hardcoded Fallback Devise Secret Key Allows Token Forgery
* **Vulnerability Type**: Hardcoded Cryptographic Secret Key / Token Forgery (CWE-321 / CWE-798)
* **Severity Rating**: **CRITICAL**
* **File Location**: `config/initializers/devise.rb:8`
* **Vulnerable Code**:
  ```ruby
  Devise.setup do |config|
    config.secret_key = ENV['DEVISE_SECRET_KEY'] || ('x' * 30)
  ```
* **Flaw Analysis**: If `ENV['DEVISE_SECRET_KEY']` is omitted in a deployment environment, Devise falls back to a static string of 30 `'x'` characters (`"xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"`). Devise uses this secret to sign and verify confirmation tokens, password reset tokens, and session cookies. An attacker knowing this open-source fallback can construct and sign arbitrary tokens offline to compromise any user account or session on the system.
* **Exploit Scenario**:
  1. An environment is deployed without setting `ENV['DEVISE_SECRET_KEY']`.
  2. An attacker generates a signed password reset token targeting an admin user's email using the known key `"xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"`.
  3. The attacker submits the forged token to the reset password endpoint.
  4. The server validates the signature using the hardcoded fallback and resets the admin password.
* **Remediation**:
  1. Require `ENV.fetch('DEVISE_SECRET_KEY')` without fallback in production:
     ```ruby
     config.secret_key = ENV.fetch('DEVISE_SECRET_KEY')
     ```

---

## 3. Verified Secure Cryptographic Controls

* **Transport Layer Security (TLS)** (`config/environments/production.rb:48`): Verified that `config.force_ssl = true` is enabled, enforcing HSTS and secure cookie flags for all production traffic.
* **Bcrypt Password Hashing** (`app/models/user.rb:5`): Verified that user credentials use `database_authenticatable` with salted Bcrypt hashing.
* **Secure Random Token Generation** (Standard Devise): Verified that password reset and confirmation tokens rely on cryptographically secure random number generators provided by Ruby's `SecureRandom` module.
