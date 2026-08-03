---
name: logging-auditing-audit
description: 'Perform an automated, strictly-scoped logging and auditing security review across codebases. Follows a systematic multi-stage methodology: 1) Construction of Logging & Auditing Checklist (logging libraries, log configuration, log levels, output destinations), 2) Deep Code & Configuration Inspection (sensitive data leakage in logs, unhandled exception logging, missing audit trails for privileged actions), and 3) Generation of 2 Markdown Reports (Checklist & Findings Audit Report). Strictly scoped to logging, auditing, and sensitive data leakage in logs only.'
argument-hint: 'Path to target repository or app directory (e.g., ./app, c:/workspace/bhima, or c:/workspace/bridge_troll)'
user-invocable: true
---

# Logging & Auditing Security Review Skill

This skill provides a systematic procedure for auditing codebases specifically for **Logging, Security Auditing, and Sensitive Data Exposure in Logs**.

---

## 🛑 STRICT SCOPE CONSTRAINT

> **CRITICAL MANDATE**: This skill is **STRICTLY CONSTRAINED** to logging mechanisms, audit trail completeness, log configuration, sensitive data leakage in logs, log injection, and log storage/transport security.
>
> **DO NOT DRIFT** into auditing other vulnerability categories (e.g., Authorization/Access Control, Authentication Bypass, SQL Injection, XSS, CSRF, Dependency Vulnerabilities) unless they directly result in log tampering, log injection, or sensitive data leakage in log files. Disregard non-logging findings to keep the report high-precision and laser-focused on Logging & Security Auditing.

---

## 1. Audit Workflow Overview

The audit follows a strict 3-stage process:

```
┌──────────────────────────────────────────────────────────┐
│ 1. Construct Logging & Auditing Checklist                │
│    (Logging Libraries, Config, Parameter Filters)        │
└────────────────────────────┬─────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────┐
│ 2. Execute Deep Code & Configuration Inspection          │
│    (Sensitive Data Leakage, Audit Trails, Exceptions)    │
└────────────────────────────┬─────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────┐
│ 3. Generate 2 Mandatory Markdown Audit Reports           │
│    (Logging Checklist & Logging Audit Findings Report)   │
└──────────────────────────────────────────────────────────┘
```

---

## 2. Stage 1: Construct Logging & Auditing Checklist

Analyze the application architecture, logger initializers, framework configurations, and logging libraries (e.g., `Winston`, `Bunyan`, `Morgan`, `Log4j`, `SLF4J`, `Loguru`, `ActiveSupport::Logger`, Rails `filter_parameter_logging.rb`, Django `LOGGING`) across 4 key pillars:

### A. Logging Framework & Configuration
- [ ] **Logging Library Used**: Identify the logging framework (e.g., Winston, Morgan, Log4j, Rails logger, Python `logging`).
- [ ] **Log Level Configuration**: Inspect environment settings (`LOG_LEVEL=debug` in production exposes internal application state vs `info`/`warn`).
- [ ] **Log Destinations & Transport Security**: Verify where logs are written (STDOUT, local file system, Syslog, SIEM like Datadog/Splunk/ELK) and ensure transport encryption (TLS) is used for remote log streaming.
- [ ] **Log Retention & Rotation**: Verify log rotation policies (`logrotate`, `FileStream` limits) to prevent disk space exhaustion (DoS).

### B. Sensitive Data Leakage in Logs (PII / PHI / Credentials)
- [ ] **Parameter Filtering / Masking**: Inspect framework parameter log filters (e.g., `filter_parameter_logging.rb`, Winston formatters, Log4j rewrite policies). Verify passwords, tokens, credit card numbers, SSNs, and API keys are masked.
- [ ] **HTTP Request & Body Logging**: Inspect HTTP request loggers (e.g., `morgan('dev')`, Express body loggers). Ensure raw authorization headers (`Authorization: Bearer <token>`), cookie headers, or POST body payloads containing credentials/PII are not logged.
- [ ] **Explicit Logger Calls**: Search for `logger.info`, `console.log`, `logger.debug`, `System.out.println` calls passing sensitive objects (e.g., `logger.info("User details: " + user)`).

### C. Security Audit Trail Completeness
- [ ] **Authentication & Access Events**: Verify successful and failed login attempts, password resets, logout events, and MFA challenges produce structured audit log entries (timestamp, user ID, IP address, event status).
- [ ] **Privileged Administrative Actions**: Verify role changes, user creation/deletion, permission grants, and security configuration changes generate immutable audit log records.
- [ ] **Sensitive Data Access / Export**: Verify bulk data downloads, patient medical record views, or financial ledger exports create audit trail entries.

### D. Log Injection & Exception Handling
- [ ] **Log Injection (CWE-117)**: Inspect log statements accepting unsanitized user input (e.g., untrusted usernames or URL params containing `\n` or `\r`) that could allow attackers to forge fake log entries or pollute log files.
- [ ] **Unhandled Exception Logging**: Inspect catch/rescue blocks to ensure uncaught exceptions do not dump raw SQL queries, database credentials, or system environment variables into public log files or web responses.

---

## 3. Stage 2: Deep Code & Configuration Inspection

Systematically inspect the framework loggers, middleware configurations, error handlers, and business logic controllers.

### Targeted Inspection Areas:

#### 1. Logger Initializer & Configuration Files
Inspect logging configuration files (e.g., `config/initializers/filter_parameter_logging.rb`, `config/initializers/sentry.rb`, `server/config/express.js` with Morgan/Winston, `settings.py` `LOGGING` dict, `logback.xml`). Verify parameter filter lists and production log levels.

#### 2. Authentication & Financial Controllers
Search for `logger.info`, `logger.debug`, or `console.log` invocations inside login, signup, password reset, payment, patient, or administrative controllers. Verify that user passwords, JWT tokens, credit cards, or medical records are not printed to logs.

#### 3. Catch Blocks & Exception Handlers
Inspect `rescue_from` (Rails), `app.use((err, req, res, next))` (Express), or `@ExceptionHandler` (Spring) blocks to ensure stack dumps or raw SQL query strings are redacted before logging.

---

## 4. Stage 3: Output Report Requirements & Persistence

To ensure complete, modular documentation, running this skill **MUST MANDATORILY GENERATE 2 SEPARATE MARKDOWN REPORTS** in the target directory (e.g. `scripts/extras/exercise-18/` or `docs/`):

1. **Logging Security Review Checklist**: `<app_name>_logging_checklist.md`
2. **Logging Security Audit Findings Report**: `<app_name>_logging_audit.md`

> **Note**: Do NOT combine checklist and findings into a single file. Generate both files below.

---

### Report 1 Template: `<app_name>_logging_checklist.md`

```markdown
# Application Logging & Auditing Security Review Checklist

## Application: `<App Name>`
- **Assessed Commit**: `#<commit_hash>`

---

## 1. Logging Framework & Configuration Checklist
- [ ] **Logging Library**: Identify logging framework and confirm production log level (`info` / `warn`).
- [ ] **Parameter Filtering**: Verify parameter log filter lists for passwords, secrets, and PII.
- [ ] **Log Rotation & Storage**: Confirm log rotation limits to prevent disk exhaustion.

## 2. Sensitive Data Leakage Checklist
- [ ] **Credential Logging**: Audit authentication controllers to confirm passwords/tokens are not logged.
- [ ] **PII/PHI Logging**: Audit patient, user, and financial controllers for unmasked PII/PHI in log statements.
- [ ] **HTTP Request Headers**: Verify `Authorization` headers and session cookies are excluded from HTTP loggers.

## 3. Security Audit Trail Checklist
- [ ] **Authentication Events**: Confirm success/failure login events log timestamp, User ID, and IP address.
- [ ] **Administrative Actions**: Confirm role modifications, user creations, and privilege grants are logged.
- [ ] **Data Export Events**: Confirm bulk data or report downloads trigger audit records.

## 4. Log Injection & Error Handling Checklist
- [ ] **Log Injection (CWE-117)**: Verify user inputs logged are sanitized against CRLF (`\r\n`) injection.
- [ ] **Exception Stack Dumps**: Confirm uncaught exceptions do not dump raw SQL or env secrets to log streams.
```

---

### Report 2 Template: `<app_name>_logging_audit.md`

```markdown
# Logging & Auditing Security Audit Findings Report

## Application: `<App Name>`
- **Assessed Commit**: `#<commit_hash>`

---

## 1. Logging Architecture Summary

| Security Area | Implementation / Configuration | Audit Result | Status |
| :--- | :--- | :--- | :---: |
| **Logging Library** | e.g., `Winston` / `ActiveSupport::Logger` | Framework Identified | ✅ |
| **Log Level** | Configured Production Log Level | Log Level Verified | ✅ / ⚠️ |
| **Parameter Filtering** | `filter_parameters` / Custom Formatter | Password / Secret Filtering | ✅ / ⚠️ |
| **Sensitive Data in Logs** | Code Search for Unmasked PII / Tokens | Data Leakage Inspected | ⚠️ / ✅ |
| **Audit Trail Completeness** | Auth & Admin Action Logging | Audit Trail Status | ⚠️ / ✅ |
| **Log Injection (CWE-117)** | CRLF Sanitization in Log Streams | Log Injection Inspected | ✅ / ⚠️ |

---

## 2. Confirmed Logging & Auditing Vulnerabilities

### 🔴 Finding 1: `<Vulnerability Title>` (`<CWE ID>`)
* **Vulnerability Type**: Sensitive Data Leakage in Logs / Log Injection / Missing Audit Trail
* **Severity Rating**: `CRITICAL` | `HIGH` | `MEDIUM` | `LOW`
* **File Location**: `<file_path>:<line_numbers>`
* **Vulnerable Code**:
  ```<language>
  // Vulnerable logging or configuration code snippet
  ```
* **Flaw Analysis**: Detailed technical breakdown of how sensitive data is leaked or how logging fails.
* **Exploit Scenario**: Attack scenario showing how logged credentials or unformatted log streams can be exploited.
* **Remediation**:
  1. `<Step 1 code or configuration fix>`
  2. `<Step 2 secure logging implementation>`

---

## 3. Verified Secure Logging & Auditing Controls

* **`<Control Name>`** (`<file_path>:<line_numbers>`): Verified secure implementation of `<logging/filtering mechanism>`.
```
