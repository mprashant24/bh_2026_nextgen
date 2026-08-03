# Bridge Troll — Cryptographic Security Review Checklist

We assessed commit `#40747c6510014958c9519d3708b5dc9325a0cc1c`

This checklist synthesizes the **Cryptographic Security Audit Skill** (`cryptography-audit`) to guide manual security code review for the Bridge Troll application (`c:/workspace/bridge_troll`).

---

## 1. Cryptographic Algorithms & Ciphers Checklist
- [x] **Password Hashing**: Confirm Bcrypt/Argon2 is used with proper work factor; verify MD5/SHA1 is avoided.
  - [x] Result: Verified Devise uses `database_authenticatable` (Bcrypt) in `User` model.
- [x] **Encryption Ciphers**: Verify AES-256-GCM or equivalent modern ciphers; confirm RC4/DES/ECB are disabled.
  - [x] Result: No custom symmetric encryption sinks found in `app/`.

## 2. Secrets & Key Management Checklist
- [x] **[FAIL] Environment Secret Loading**: Confirm `SECRET_KEY_BASE` and `DEVISE_SECRET_KEY` load from `ENV` without hardcoded fallbacks.
  - [x] Check: `config/initializers/devise.rb:8`
  - [x] Finding: `config.secret_key = ENV['DEVISE_SECRET_KEY'] || ('x' * 30)` allows for a hardcoded 30-character fallback.
- [x] **Cryptographic PRNG**: Confirm tokens use `SecureRandom` or `crypto.randomBytes`.
  - [x] Result: Standard Devise modules use `SecureRandom` for tokens.

## 3. Transport & Storage Encryption Checklist
- [x] **TLS Enforcement**: Confirm `config.force_ssl = true` and HSTS headers in production.
  - [x] Check: `config/environments/production.rb:48`
  - [x] Result: `config.force_ssl = true` is enabled with HSTS configured for 1 year.
- [x] **Cookie Security**: Verify `Secure` and `HttpOnly` flags on session cookies.
  - [x] Result: `force_ssl` automatically sets the `Secure` flag on cookies. `HttpOnly` is default in Rails.
