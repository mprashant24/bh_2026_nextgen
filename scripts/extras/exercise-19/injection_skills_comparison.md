# Injection Skills Comparison Summary

This report provides a comparative summary between the pre-existing **Injection Review Skill** (`injection-review/SKILL.md`) and the newly generated **Injection Audit Skill** (`injection-audit/SKILL.md`). 

---

## 1. Overview & Purpose

| Feature | `injection-review` (Pre-existing) | `injection-audit` (Newly Generated) |
| :--- | :--- | :--- |
| **Primary Goal** | Trace untrusted data sources to dangerous sinks across multiple injection types. | Automate a 3-stage audit covering SQLi, XSS, Log Injection, Command Injection, and generate Markdown reports. |
| **Execution Mode** | Can be run standalone or invoked as a sub-routine by the `secure-code-review` orchestrator. | Runs standalone as a rigid 3-stage process. |
| **Output Destination**| Writes findings to `REVIEW-NOTES.md` (Findings In Progress section). | Generates 2 new dedicated files: `<app>_injection_checklist.md` and `<app>_injection_audit.md`. |
| **False Positive Mitigation** | Uses external calibration files (`references/sqli-examples.md`). | Uses strict scope constraints and code inspection heuristics directly in the prompt. |

---

## 2. Methodology & Workflow

### `injection-review` Methodology (Data-Flow Tracking)
Follows a **Taint Tracking & Data Flow** approach:
1. Establish Scope (Framework identification, locating entry points).
2. Build "Sources" (HTTP params, env vars) and "Sinks" (DB queries, OS calls, template rendering).
3. Run Search Heuristics (Grep commands like `grep -rEn '\.raw\(' .`).
4. Trace each Source to Sink (Confirm path is reachable and unsanitized).
5. Check ORM Misuse and Template Auto-escaping.
6. Evaluate Mitigating Controls (WAFs, middleware) before recording a finding.

### `injection-audit` Methodology (Checklist & Inspection)
Follows a **Checklist & Configuration Review** approach:
1. Construct Comprehensive Injection Checklist (Tailored to specific framework e.g. Rails/Django).
2. Code Review & Implementation Inspection (Search for string concatenation in ORMs, raw HTML outputs, unescaped loggers).
3. Vulnerability Documentation with severity ratings.

---

## 3. Vulnerability Scope

| Vulnerability Type | Covered in `injection-review` | Covered in `injection-audit` |
| :--- | :---: | :---: |
| **SQL Injection (SQLi)** | ✅ | ✅ |
| **Cross-Site Scripting (XSS)** | ✅ | ✅ |
| **Command Injection / OS Calls** | ✅ | ✅ |
| **Log Injection (CRLF)** | ❌ (Mentioned as Sink, but not dedicated) | ✅ (Dedicated Section) |
| **Server-Side Request Forgery (SSRF)**| ✅ | ❌ |
| **NoSQL Injection / LDAP / XXE** | ✅ | ❌ |
| **Template Injection (SSTI)** | ✅ | ❌ (Implicitly covered under XSS) |
| **Open Redirects** | ✅ | ❌ |

---

## 4. Strengths & Weaknesses

### Pre-existing `injection-review`
- **Strengths**: 
  - Highly robust **Source-to-Sink tracing** methodology, which is the industry standard for manual code review.
  - Integrates smoothly into a larger orchestrator pipeline (`secure-code-review`).
  - Broadest coverage of injection types (SSRF, XXE, NoSQLi).
  - Actively accounts for mitigating controls (WAFs, Auth gates) before flagging.
- **Weaknesses**: 
  - Relies on external reference files (`checklist.md`, `sqli-examples.md`) which must be present.
  - Output format is appended to a general `REVIEW-NOTES.md` file rather than generating a standalone, polished report.

### Newly Generated `injection-audit`
- **Strengths**: 
  - Fully self-contained in a single `SKILL.md` file.
  - Produces highly structured, standalone Markdown deliverables (Checklist + Findings Report).
  - Explicitly covers **Log Injection (CWE-117)**, which is often overlooked.
  - Includes explicit severity rating mechanisms.
- **Weaknesses**: 
  - Does not explicitly map "Sources" to "Sinks" (relies more on pattern matching / grep).
  - Narrower vulnerability scope (misses SSRF, XXE, Open Redirects).

---

## 5. Conclusion

- Use **`injection-review`** when performing a comprehensive, deep-dive **Secure Code Review** where tracking data flow from external input down to the database/OS layer is critical, and when operating as part of a larger multi-stage agent orchestrator.
- Use **`injection-audit`** when a fast, highly structured **Compliance & Checklist Assessment** is needed, specifically to generate polished, standalone Markdown reports for SQLi, XSS, and Log Injection.
