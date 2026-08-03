---
name: injection-audit
description: 'Perform an automated, strictly-scoped injection security audit across codebases. Follows a systematic 3-stage methodology: 1) Technology-Tailored Injection Checklist Construction (SQL Injection, Cross-Site Scripting XSS, Log Injection, Command Injection, Input Validation & Output Encoding controls), 2) Code Review & Implementation Inspection (ORM raw queries, unsafe template rendering, unescaped log inputs, command execution), and 3) Vulnerability Documentation with severity ratings and remediations. Strictly scoped to injection vulnerabilities only.'
argument-hint: 'Path to target repository or app directory (e.g., ./app, c:/workspace/bridge_troll, or c:/workspace/bhima)'
user-invocable: true
---

# Injection Security Audit Skill

This skill provides a systematic procedure for auditing codebases specifically for **Injection Vulnerabilities (SQLi, XSS, Log Injection, Command Injection)** and assessing input validation and output encoding controls.

---

## 🛑 STRICT SCOPE CONSTRAINT

> **CRITICAL MANDATE**: This skill is **STRICTLY CONSTRAINED** to injection vulnerabilities (SQL Injection, Reflected/Stored/DOM XSS, Log Injection / CRLF, Command Injection) and their associated defenses (Input Validation routines, Output Encoding, Parameterized ORM queries).
>
> **DO NOT DRIFT** into auditing other vulnerability categories (e.g., Authorization/Access Control, Authentication Bypass, Broken Cryptography, CSRF, Dependency CVEs) unless they directly facilitate an injection flaw. Disregard non-injection findings to keep the report high-precision and laser-focused on Injection Security.

---

## 1. Audit Workflow Overview

The audit follows a strict 3-stage process:

```
┌──────────────────────────────────────────────────────────┐
│ 1. Construct Injection Security Checklist                │
│    (SQLi, Stored/Reflected XSS, Log Injection, Input/Output)│
└────────────────────────────┬─────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────┐
│ 2. Execute Code Inspection & Review                      │
│    (ORM Raw Queries, ERB/HTML Unescaped Output, Logging)  │
└────────────────────────────┬─────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────┐
│ 3. Generate 2 Mandatory Markdown Audit Reports           │
│    (Injection Checklist & Injection Audit Findings Report)│
└──────────────────────────────────────────────────────────┘
```

---

## 2. Stage 1: Construct Comprehensive Injection Checklist

Analyze the application technology stack (e.g., Rails / ActiveRecord / ERB, Node / Express / Sequelize / Pug, Python / Django / ORM) to build a technology-tailored checklist across 4 key pillars:

### A. SQL Injection (SQLi)
- [ ] **ORM Parameterization**: Verify ORM query calls use parameter binding (`where("title = ?", input)`, `where(title: input)`).
- [ ] **Raw SQL Execution / Fragment Concatenation**: Inspect raw query fragments (`.where("... #{params[:input]} ...")`, `.pluck("...")`, `.order("...")`, `.group("...")`, `.select("...")`, `execute("...")`, `find_by_sql("...")`).
- [ ] **Dynamic Table / Column Identifiers**: Inspect endpoints accepting user input to specify database table names or column order (`order(params[:sort_by])`).

### B. Cross-Site Scripting (XSS)
- [ ] **Unescaped View Output (Stored & Reflected XSS)**: Inspect view templates (ERB `<%== %>`, `<%= raw(...) %>`, `html_safe`, Pug `!=`, Angular `[innerHTML]`, React `dangerouslySetInnerHTML`).
- [ ] **HTML Sanitization Libraries**: Inspect usage of HTML sanitizers (`Sanitize` gem, `DOMPurify`, `sanitize-html`). Verify allowlist configurations (permitted tags, attributes, and protocols like `javascript:` links).
- [ ] **Client-Side / DOM XSS**: Inspect frontend scripts for unsafe sinks (`document.write`, `element.innerHTML`, `eval()`, `location.href = javascript:...`).

### C. Log Injection (CRLF Log Pollution - CWE-117)
- [ ] **Log Input Sanitization**: Inspect `logger.info`, `logger.warn`, and custom logging invocations for user-supplied string interpolation (`params[:q]`, `request.remote_ip`, user-agent headers).
- [ ] **CRLF Injection Protection**: Verify newlines (`\r\n`) in logged parameters are stripped or encoded before writing to log streams to prevent log forging or header splitting.

### D. Input Validation & Output Encoding Defenses
- [ ] **Server-Side Type Casting & Schema Validation**: Confirm input parameters are validated and cast to strict types (Integer, Enum, Date, UUID) on the server before processing.
- [ ] **Context-Aware Output Encoding**: Verify output is encoded appropriately for its destination context (HTML body, HTML attribute, JavaScript context, URL parameter).

---

## 3. Stage 2: Code Review & Implementation Inspection

Systematically inspect the codebase for vulnerable patterns and controls.

### Targeted Inspection Areas:

#### 1. Database Queries & ORM Usage
- Search for string interpolation/concatenation in ORM method arguments (`.where`, `.order`, `.pluck`, `.select`, `.group`, `.joins`, `.from`, `.execute`, `.find_by_sql`).

#### 2. View Templates & Output Rendering
- Search for raw or unescaped HTML helper methods (`raw()`, `html_safe`, `sanitize()`, `| safe`, `!=`) across all view templates and email templates.

#### 3. Loggers & System Commands
- Search for logger calls accepting unescaped user parameters.
- Search for system command execution (`system()`, `` `cmd` ``, `exec()`, `Open3`, `popen()`, `subprocess`).

---

## 4. Stage 3: Output Report Requirements & Persistence

To ensure complete, modular documentation, running this skill **MUST MANDATORILY GENERATE 2 SEPARATE MARKDOWN REPORTS** in the target directory (e.g., `scripts/extras/exercise-19/` or `docs/`):

1. **Injection Security Review Checklist**: `<app_name>_injection_checklist.md`
2. **Injection Security Audit Findings Report**: `<app_name>_injection_audit.md`

> **Note**: Do NOT combine checklist and findings into a single file. Generate both files below.

---

### Report 1 Template: `<app_name>_injection_checklist.md`

```markdown
# Application Injection Security Review Checklist

## Application: `<App Name>`
- **Assessed Commit**: `#<commit_hash>`
- **Technology Stack**: `<e.g. Ruby on Rails 8 / PostgreSQL / ERB>`

---

## 1. SQL Injection Checklist
- [ ] **ORM Parameter Binding**: Confirm all `.where()`, `.find_by()` calls use array/hash bindings.
- [ ] **Raw SQL Fragments**: Audit `.where("... #{var} ...")`, `.order()`, `.pluck()`, `.select()`.
- [ ] **Dynamic Query Sorting**: Verify user-supplied sort columns are validated against an allowlist.

## 2. Cross-Site Scripting (XSS) Checklist
- [ ] **Unescaped View Output**: Audit view templates for `raw()`, `html_safe`, `<%== %>`.
- [ ] **Sanitization Allow lists**: Inspect HTML sanitizer configurations for permit tags/protocols.
- [ ] **User-Generated Content**: Confirm review, feedback, or title fields encode output contextually.

## 3. Log Injection Checklist
- [ ] **Log Stream Sanitization**: Confirm user inputs in `logger` calls strip CRLF (`\r\n`) characters.
- [ ] **Logging Parameter Filters**: Verify sensitive keys are masked from log outputs.

## 4. Input Validation & Command Injection Checklist
- [ ] **Server-Side Validation**: Confirm type casting (Integer, Enum, Date) is enforced on server parameters.
- [ ] **Command Execution**: Audit for OS shell invocation methods (`system`, `` ` ``, `exec`).
```

---

### Report 2 Template: `<app_name>_injection_audit.md`

```markdown
# Injection Security Audit Findings Report

## Application: `<App Name>`
- **Assessed Commit**: `#<commit_hash>`

---

## 1. Injection Security Architecture Summary

| Security Area | Implementation / Configuration | Audit Result | Status |
| :--- | :--- | :--- | :---: |
| **SQL Injection (SQLi)** | ORM Parameterization & Raw Fragments | Query Binding Inspected | ⚠️ / ✅ |
| **Stored XSS** | HTML Sanitization & ERB Escaping | Template Tags Inspected | ⚠️ / ✅ |
| **Reflected XSS** | Contextual Output Encoding | Request Echoing Inspected | ✅ |
| **Log Injection (CWE-117)** | Logger Input Sanitization | CRLF Injections Inspected | ⚠️ / ✅ |
| **Command Injection** | Shell Command Invocation | Command Exec Calls Inspected | ✅ |

---

## 2. Confirmed Injection Vulnerabilities

### 🔴 Finding 1: `<Vulnerability Title>` (`<CWE ID>`)
* **Vulnerability Type**: SQL Injection / Stored XSS / Log Injection / Command Injection
* **Severity Rating**: `CRITICAL` | `HIGH` | `MEDIUM` | `LOW`
* **File Location**: `<file_path>:<line_numbers>`
* **Vulnerable Code**:
  ```<language>
  // Vulnerable code snippet
  ```
* **Flaw Analysis**: Technical breakdown of how user input reaches the vulnerable sink without sanitization.
* **Exploit Scenario**: Step-by-step attack scenario demonstrating injection execution.
* **Remediation**:
  1. `<Step 1 code fix / parameterized query>`
  2. `<Step 2 output encoding / sanitization>`

---

## 3. Verified Secure Injection Controls

* **`<Control Name>`** (`<file_path>:<line_numbers>`): Verified secure implementation of `<parameterized query / sanitizer>`.
```
