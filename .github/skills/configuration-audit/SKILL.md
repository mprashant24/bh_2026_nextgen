---
name: configuration-audit
description: 'Perform an automated, strictly-scoped configuration security audit across codebases. Follows a systematic 3-stage methodology: 1) Construction of Configuration Security Checklist (framework settings, HTTP security headers, CORS, CSRF, dependency management), 2) Deep Code & Configuration Inspection (CSP, HSTS, secure defaults, outdated/vulnerable dependencies), and 3) Generation of 2 Markdown Reports (Checklist & Findings Audit Report). Strictly scoped to configuration, headers, and dependency management only.'
argument-hint: 'Path to target repository or app directory (e.g., ./app, c:/workspace/bridge_troll, or c:/workspace/bhima)'
user-invocable: true
---

# Configuration & Security Headers Audit Skill

This skill provides a systematic procedure for auditing codebases specifically for **Framework Security Configurations, HTTP Security Headers, CORS, CSRF, and Dependency Management**.

---

## 🛑 STRICT SCOPE CONSTRAINT

> **CRITICAL MANDATE**: This skill is **STRICTLY CONSTRAINED** to web framework security defaults, HTTP headers (CSP, HSTS, X-Frame-Options), Cross-Origin Resource Sharing (CORS), CSRF mitigations, and dependency management (manifest files).
>
> **DO NOT DRIFT** into auditing other vulnerability categories (e.g., Authorization/Access Control, Authentication, SQL Injection, XSS, Cryptography) unless they are direct results of a missing security header (e.g., XSS exacerbated by missing CSP) or a misconfigured framework setting.

---

## ⚡ API RATE LIMITING & PACING CONSTRAINT

> **TOKEN BUDGET RULE**: The model operates under a strict limit of **2,000,000 tokens per minute (TPM)**.
> - Space out file reads and tool invocations into measured batches rather than issuing massive, rapid sequential file requests.
> - Avoid reading entire repository directories at once; inspect target configuration files (e.g., `application.rb`, `production.rb`, `cors.rb`, `package.json`, `Gemfile`) using targeted line ranges or specific paths.

---

## 1. Audit Workflow Overview

The audit follows a strict 3-stage process:

```
┌──────────────────────────────────────────────────────────┐
│ 1. Construct Configuration Security Checklist            │
│    (Framework Defaults, Headers, Dependencies, CORS)      │
└────────────────────────────┬─────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────┐
│ 2. Execute Code & Configuration Inspection               │
│    (CSP, HSTS, CSRF Middleware, Dependency Manifests)     │
└────────────────────────────┬─────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────┐
│ 3. Generate 2 Mandatory Markdown Audit Reports           │
│    (Config Checklist & Configuration Findings Report)     │
└──────────────────────────────────────────────────────────┘
```

---

## 2. Stage 1: Construct Comprehensive Configuration Checklist

Analyze the application architecture and configuration initializers to build an audit checklist across 3 key pillars:

### A. Framework Security Settings & CSRF
- [ ] **CSRF Protection**: Verify Cross-Site Request Forgery protections are enabled globally (`protect_from_forgery` in Rails, `csurf` in Express, `CsrfViewMiddleware` in Django).
- [ ] **Debug & Error Modes**: Confirm debug mode and verbose stack traces are disabled in production (`config.consider_all_requests_local = false`, `DEBUG = False`).
- [ ] **Secure Defaults**: Verify modern framework security defaults are applied (e.g., Rails `load_defaults`, Origin Checks).

### B. HTTP Security Headers & CORS
- [ ] **Content Security Policy (CSP)**: Inspect CSP configuration to ensure it restricts `script-src` and `object-src` to trusted domains, mitigating XSS impact.
- [ ] **Strict-Transport-Security (HSTS)**: Verify HSTS is enforced to guarantee encrypted transport.
- [ ] **X-Frame-Options & Clickjacking**: Ensure `X-Frame-Options` is set to `DENY` or `SAMEORIGIN`.
- [ ] **CORS Configuration**: Inspect CORS initializers (`cors.rb`, Express `cors()`) to ensure the `Access-Control-Allow-Origin` header does not allow wildcard `*` with credentials or overly broad domain regexes.

### C. Dependency Management
- [ ] **Dependency Manifests**: Inspect `Gemfile`, `package.json`, `requirements.txt`, or `pom.xml` for known outdated or deprecated libraries.
- [ ] **Vulnerability Auditing Setup**: Check for the presence of automated dependency scanning tools (`bundler-audit`, `npm audit`, `Dependabot`, `Snyk`, `OWASP Dependency-Check`).

---

## 3. Stage 2: Code Review & Implementation Inspection

Systematically inspect framework configuration files.

### Targeted Inspection Areas:
1. **Initializers & Environment Configs**: Inspect `config/environments/production.rb`, `config/initializers/cors.rb`, `config/initializers/content_security_policy.rb`, `config/application.rb`, or equivalent settings files.
2. **Global Controllers/Middleware**: Check `ApplicationController` or main server entrypoints for CSRF and header definitions.
3. **Manifest Files**: Skim the `Gemfile` or `package.json` for major versions of critical security libraries.

---

## 4. Stage 3: Output Report Requirements & Persistence

To ensure complete, modular documentation, running this skill **MUST MANDATORILY GENERATE 2 SEPARATE MARKDOWN REPORTS** in the target directory (e.g. `scripts/extras/exercise-21/` or `docs/`):

1. **Configuration Security Review Checklist**: `<app_name>_configuration_checklist.md`
2. **Configuration Security Audit Findings Report**: `<app_name>_configuration_audit.md`

> **Note**: Do NOT combine checklist and findings into a single file. Generate both files.

---

### Report 1 Template: `<app_name>_configuration_checklist.md`

```markdown
# Application Configuration & Headers Security Checklist

## Application: `<App Name>`
- **Assessed Commit**: `#<commit_hash>`

---

## 1. Framework Settings & CSRF Checklist
- [ ] **CSRF Protection**: Confirm global CSRF token verification is enforced.
- [ ] **Production Error Handling**: Verify diagnostic/debug modes are disabled.

## 2. Security Headers & CORS Checklist
- [ ] **Content Security Policy (CSP)**: Verify CSP restricts `script-src` and disables `unsafe-inline` where possible.
- [ ] **HSTS & Secure Transport**: Confirm `Strict-Transport-Security` is active.
- [ ] **CORS Origins**: Verify CORS rules restrict origins to specific trusted domains.

## 3. Dependency Management Checklist
- [ ] **Manifest Review**: Review dependencies for outdated major versions.
- [ ] **Audit Integration**: Verify dependency scanning tools are used.
```

---

### Report 2 Template: `<app_name>_configuration_audit.md`

```markdown
# Configuration Security Audit Findings Report

## Application: `<App Name>`
- **Assessed Commit**: `#<commit_hash>`

---

## 1. Configuration Architecture Summary

| Security Area | Implementation / Configuration | Audit Result | Status |
| :--- | :--- | :--- | :---: |
| **CSRF Protection** | Global framework CSRF config | Verified | ✅ / ⚠️ |
| **CORS Policy** | CORS Middleware Config | Verified | ✅ / ⚠️ |
| **Content Security Policy** | CSP Initializer | Verified | ⚠️ / ✅ |
| **Transport Headers** | HSTS / X-Frame-Options | Verified | ✅ / ⚠️ |

---

## 2. Confirmed Configuration Vulnerabilities

### 🔴 Finding 1: `<Vulnerability Title>` (`<CWE ID>`)
* **Vulnerability Type**: Missing Security Header / Permissive CORS / Debug Mode Enabled
* **Severity Rating**: `CRITICAL` | `HIGH` | `MEDIUM` | `LOW`
* **File Location**: `<file_path>:<line_numbers>`
* **Vulnerable Code**:
  ```<language>
  // Vulnerable configuration
  ```
* **Flaw Analysis**: Technical breakdown of the misconfiguration risk.
* **Remediation**:
  1. `<Step 1 code or configuration fix>`

---

## 3. Verified Secure Configuration Controls

* **`<Control Name>`** (`<file_path>:<line_numbers>`): Verified secure implementation of `<configuration mechanism>`.
```
