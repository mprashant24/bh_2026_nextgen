---
name: authentication-audit
description: 'Perform an automated, strictly-scoped authentication security audit across codebases. Follows a systematic 3-stage methodology: 1) Comprehensive Authentication Checklist Construction (User ID methods, Auth flows, Session handling), 2) Code Review & Implementation Inspection (Login flow security, Registration & privilege assignment, Session management config), and 3) Vulnerability Documentation with severity ratings. Strictly scoped to authentication and session management flaws only.'
argument-hint: 'Path to target repository or app directory (e.g., ./app, c:/workspace/bhima, or c:/workspace/bridge_troll)'
user-invocable: true
---

# Authentication Security Audit Skill

This skill provides a systematic procedure for auditing codebases specifically for **Authentication (AuthN) and Session Management Vulnerabilities**.

---

## 🛑 STRICT SCOPE CONSTRAINT

> **CRITICAL MANDATE**: This skill is **STRICTLY CONSTRAINED** to authentication mechanisms, credential handling, session management, identity verification, and password/account security flaws.
>
> **DO NOT DRIFT** into auditing other vulnerability categories (e.g., Authorization/Access Control, SQL Injection, XSS, CSRF, Unsanitized Shell Commands, Dependency Scans) unless they directly impact identity verification or session state integrity. Disregard non-authentication findings to keep the report high-precision and laser-focused on Authentication & Session Security.

---

## 1. Audit Workflow Overview

The audit follows a strict 3-stage process:

```
┌──────────────────────────────────────────────────────────┐
│ 1. Construct Authentication Checklist                    │
│    (User ID Methods, Auth Flows, Session Mechanisms)      │
└────────────────────────────┬─────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────┐
│ 2. Execute Code Inspection & Review                      │
│    (Login Security, Registration & Roles, Session Config) │
└────────────────────────────┬─────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────┐
│ 3. Document Findings & Severity Ratings                 │
│    (Code References, Exploit Scenarios, & Remediation)   │
└──────────────────────────────────────────────────────────┘
```

---

## 2. Stage 1: Construct Comprehensive Authentication Checklist

Analyze the application architecture, configuration files, and authentication libraries (e.g., Devise, Passport.js, Spring Security, Django Auth, NextAuth, OAuth SDKs) to build an audit checklist across 3 key pillars:

### A. User Identification Methods & Error Information Disclosure
- [ ] **Identity Token / Credentials**: Verify how users identify themselves (Username, Email, Phone Number, SSN, Employee ID).
- [ ] **User Enumeration**: Inspect login, password reset, and registration endpoints to ensure error messages and response times do not reveal whether an account exists.
- [ ] **Authentication Error Handling & Sensitive Data Disclosure**:
  - Inspect catch blocks, exception handlers, and validation responses across all authentication flows.
  - Ensure failed login/reset responses do NOT leak sensitive details such as:
    - Account existence status (`"User not found"` vs `"Invalid credentials"`).
    - Database error messages, internal SQL/ORM query traces, or stack dumps on failed authentication attempts.
    - Password hashes, password reset tokens, MFA secret seeds, or session keys in JSON error responses/API payloads.
    - Internal server paths, server version headers, or database schema names in unhandled exception responses during auth failures.
- [ ] **Multi-Factor Authentication (MFA/2FA)**: Check if MFA is enforced, how TOTP/SMS/Email tokens are verified, and if MFA bypass vectors exist.

### B. Authentication Flows
- [ ] **Login Flow Security**: Inspect credential verification algorithms, password hashing (Bcrypt, Argon2, PBKDF2 vs weak MD5/SHA1/Plaintext), and rate-limiting/brute-force protection (lockout policies, `express-rate-limit`, Rack::Attack).
- [ ] **Registration & Account Provisioning**: Verify password strength/complexity policies, default role assignment during signup (preventing mass assignment of `role=admin`), and email verification workflows.
- [ ] **Password Reset & Recovery**: Inspect password reset token generation (`crypto.randomBytes`, UUIDv4 vs predictable timestamps/sequential IDs), token expiration TTL, single-use enforcement, and secure token delivery via email/SMS.
- [ ] **OAuth / Social Login / SSO**: Verify state parameter usage (`state` CSRF token validation), redirect URI allowlisting, and secure token/code exchange logic.

### C. Session Handling Mechanisms
- [ ] **Session Token Storage & Generation**: Inspect session ID entropy, token signing secrets (`SESS_SECRET`, `JWT_SECRET`), and secret entropy/hardcoding.
- [ ] **Session Cookie Configuration**: Verify cookie security flags: `HttpOnly` (XSS protection), `Secure` (HTTPS transport enforcement), and `SameSite` (`Lax` or `Strict` for CSRF mitigation).
- [ ] **Session Lifecycle & Invalidation**: Verify session termination on logout (`req.session.destroy()`, JWT blocklisting/revocation), idle session timeout, and session fixation prevention (regenerating session ID upon login).

---

## 3. Stage 2: Code Review & Implementation Inspection

Systematically inspect the controller handlers, middleware configurations, security libraries, and configuration files.

### Targeted Inspection Areas:

#### 1. Framework Configuration & Initializer Files Inspection
Inspect all framework security and authentication configuration files (e.g. `config/initializers/devise.rb`, `config/initializers/session_store.rb`, `config/initializers/cors.rb`, `config/initializers/filter_parameter_logging.rb`, `config/express.js`, `settings.py`, `SecurityConfig.java`). Verify secret key entropy, session timeouts, parameter logging filters, and rate-limiting rules.

#### 2. Custom Application Security Controls & Identity Services
Inspect custom authentication services, helpers, and OAuth attribute generators (e.g. `OmniauthProviders`, `User.from_omniauth`, `PasswordHasher`, `AccountMerger`, `TokenVerifier`). Verify that custom application code does NOT bypass framework security controls, trust unverified third-party claims, or introduce pre-authenticated account linking flaws.

#### 3. Login Flow Security & Error Handling
- Inspect authentication controller actions (e.g. `auth.js`, `sessions_controller.rb`, `AuthController.java`).
- Search for timing attacks, verbose error responses (`"Invalid password"` vs `"Invalid credentials"`), missing rate limiters, and plaintext password logging.
- Audit exception handlers and error response payloads for leakage of database traces, internal stack dumps, user object attributes, or sensitive credentials in error JSON bodies.

#### 4. Registration Process & Privilege Assignment
- Inspect user creation handlers (`registrations_controller.rb`, `users.js:create`, signup endpoints).
- Search for Mass Assignment / Parameter Pollution flaws that accept client-provided `admin`, `is_staff`, or `role` parameters during registration.
- Verify password validation rules (length, complexity, dictionary checks).

#### 5. Session Management Configuration
- Inspect Express session middleware (`express.js`), Rails session config (`session_store.rb`), or JWT configuration (`jwt.js`).
- Verify `cookie.httpOnly`, `cookie.secure`, `cookie.sameSite`, and Redis/file session store options.
- Confirm session ID regeneration on login (`req.session.regenerate()` or framework equivalent).

---

## 4. Stage 3: Vulnerability Documentation & Severity Ratings

Document every identified authentication vulnerability with standardized severity ratings (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`).

### Severity Rating Matrix:
- **CRITICAL**: Hardcoded JWT/Session secrets, plaintext password storage, unauthenticated password reset token prediction, account takeover via OAuth callback flaw, or mass assignment allowing `role=admin` on public registration.
- **HIGH**: Missing rate limiting on login (brute-force/credential stuffing), weak password hashing (MD5/SHA1), missing `HttpOnly`/`Secure` flags on session cookies in production, or improper session invalidation on logout.
- **MEDIUM**: User enumeration via verbose error messages or timing differences, missing password complexity rules, or long-lived password reset tokens without expiration.
- **LOW**: Non-standard session cookie names, minor error message inconsistencies, or missing lockout notification emails.

---

## 5. Output Report Requirements & Persistence

To ensure complete, modular documentation, running this skill **MUST MANDATORILY GENERATE 2 SEPARATE MARKDOWN REPORTS** in the target directory (e.g. `scripts/extras/exercise-14/` or `docs/`):

1. **Authentication Security Review Checklist**: `<app_name>_authentication_checklist.md`
2. **Authentication Security Audit Findings Report**: `<app_name>_authentication_audit.md`

> **Note**: Do NOT combine checklist and findings into a single file. Generate both files below.

---

### Report 1 Template: `<app_name>_authentication_checklist.md`

```markdown
# Application Authentication Security Review Checklist

## Application: `<App Name>`
- **Assessed Commit**: `#<commit_hash>`

---

## 1. User Identification & Credentials Checklist
- [ ] **Primary Identifier**: Confirm user identity token is validated.
- [ ] **User Enumeration**: Inspect login/reset/registration error messages.
- [ ] **Authentication Error Disclosure**: Verify catch blocks do not leak stack traces, SQL errors, or hashes.

## 2. Authentication Flows Review Checklist
- [ ] **Password Hashing**: Verify Bcrypt/Argon2 configuration and stretches/work factor.
- [ ] **Brute-Force & Rate-Limiting**: Confirm login lockout module and rate-limiting middleware.
- [ ] **Mass Assignment**: Inspect user registration for parameter pollution on role attributes.
- [ ] **Password Reset**: Verify token randomness (`Crypto`), TTL expiration, and single-use invalidation.
- [ ] **OAuth / SSO**: Check `state` parameter validation and pre-authenticated account linking guards.

## 3. Session Handling & Cookie Security Checklist
- [ ] **Session Storage**: Verify secret key entropy and environmental loading.
- [ ] **Cookie Security Flags**: Confirm `HttpOnly`, `Secure`, and `SameSite` flags in production.
- [ ] **Session Lifecycle**: Confirm idle timeout and complete server-side session destruction on logout.
```

---

### Report 2 Template: `<app_name>_authentication_audit.md`

```markdown
# Authentication Security Audit Findings Report

## Application: `<App Name>`
- **Assessed Commit**: `#<commit_hash>`

---

## 1. Authentication Architecture Summary

| Security Area | Implementation / Configuration | Audit Result | Status |
| :--- | :--- | :--- | :---: |
| **User Identification** | Primary ID: `Email` / Username | User Enumeration Checked | ⚠️ / ✅ |
| **Password Hashing** | `Bcrypt` / `Argon2` (work factor: 12) | Password Hashing Verified | ✅ |
| **Brute-Force Protection** | Rate Limiting / Lockout Middleware | Rate Limiting Status | ⚠️ / ✅ |
| **Registration & Roles** | Strong Parameters / Schema Validation | Mass Assignment Guarded | ✅ |
| **Password Reset** | Token Generation & Expiration TTL | Reset Flow Verified | ✅ |
| **Session Storage** | `RedisStore` / Encrypted Cookies | Session Secret Entropy | ✅ |
| **Session Cookie Flags** | `HttpOnly`, `Secure`, `SameSite` | Production Cookie Flags | ⚠️ / ✅ |
| **Logout Invalidation** | Server-side Session Destruction | Session Revoked on Logout | ✅ |

---

## 2. Confirmed Authentication Vulnerabilities

### 🔴 Finding 1: `<Vulnerability Title>` (`<CWE ID>`)
* **Vulnerability Type**: Password Reset Flaw / Brute-Force Vulnerability / Session Fixation / Mass Assignment
* **Severity Rating**: `CRITICAL` | `HIGH` | `MEDIUM` | `LOW`
* **File Location**: `<file_path>:<line_numbers>`
* **Vulnerable Code**:
  ```<language>
  // Vulnerable authentication or session code snippet
  ```
* **Flaw Analysis**: Detailed technical breakdown of how the authentication mechanism fails or can be exploited.
* **Exploit Scenario**: Step-by-step attack scenario demonstrating credential compromise or session hijacking.
* **Remediation**:
  1. `<Step 1 code or configuration fix>`
  2. `<Step 2 secure pattern implementation>`

---

## 3. Verified Secure Authentication Controls

* **`<Control Name>`** (`<file_path>:<line_numbers>`): Verified secure implementation of `<auth/session mechanism>`.
```
