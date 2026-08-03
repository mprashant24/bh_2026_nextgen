---
name: authorization-audit
description: 'Perform an automated, strictly-scoped authorization and access control security audit across codebases. Follows a systematic multi-stage methodology: 1) Authorization Matrix Construction, 2) Route & Controller Authorization Checklist Generation, and 3) Deep Code Inspection & Vulnerability Identification (BOLA/IDOR, Missing Function-Level Access Control, Bypassed Guards, Privilege Escalation). Strictly scoped to authorization and access control flaws only.'
argument-hint: 'Path to target repository or app directory (e.g., ./app or c:/workspace/bridge_troll)'
user-invocable: true
---

# Authorization & Access Control Audit Skill

This skill provides a systematic procedure for auditing codebases specifically for **Authorization (AuthZ) and Access Control Vulnerabilities**.

---

## 🛑 STRICT SCOPE CONSTRAINT

> **CRITICAL MANDATE**: This skill is **STRICTLY CONSTRAINED** to authorization, access control, role/privilege enforcement, and object-level permission flaws. 
>
> **DO NOT DRIFT** into auditing other vulnerability categories (e.g., SQL Injection, XSS, CSRF, Cryptographic Flaws, Insecure Deserialization, Dependency Scans) unless they directly result in an authorization bypass (e.g., role attribute mass assignment). Disregard non-authorization findings to keep the report high-precision and laser-focused on Access Control.

---

## 1. Audit Workflow Overview

The audit follows a strict 3-stage process:

```
┌─────────────────────────────────────────┐
│ 1. Build Authorization Matrix           │
│    (Map Roles, Resources, & Rules)      │
└────────────────────┬────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────┐
│ 2. Generate Audit Checklist             │
│    (Priority-ranked Controller Rules)   │
└────────────────────┬────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────┐
│ 3. Execute Deep Code Inspection         │
│    (Verify AuthZ & Document Flaws)      │
└─────────────────────────────────────────┘
```

---

## 2. Stage 1: Construct Authorization Matrix

Analyze the application's authentication framework (Devise, Passport, Spring Security, Django Auth) and authorization framework (Pundit, CanCanCan, CASL, Django Permissions, Spring `@PreAuthorize`) to build a comprehensive **Role-Based & Attribute-Based Authorization Matrix**.

### Steps:
1. **Identify User Roles & Scopes**:
   - Global Roles (e.g., `Admin`, `Publisher`, `User`, `Guest`).
   - Domain/Resource-Scoped Roles (e.g., `Chapter Leader`, `Org Manager`, `Event Organizer`, `Checkiner`).
   - Resource Ownership (e.g., `Owner` / `Self`).
2. **Map Resources to Actions**:
   - CRUD operations on core business entities (Events, Users, Financial Records, Settings).
3. **Define Permission Rules**:
   - `ALLOW` (✅): Unrestricted permission.
   - `DENY` (❌): Forbidden action.
   - `OWNER` (👤): Permitted only if `user_id == resource.owner_id`.
   - `SCOPED` (🔒): Permitted only within user's assigned scope (Chapter, Org, Group).

---

## 3. Stage 2: Generate Authorization Audit Checklist

Synthesize the Authorization Matrix and Route Inventory to produce a **Targeted Authorization Checklist** for high-risk routes.

### Focus Areas for Checklist Items:
1. **High-Privilege Operations**:
   - Role/leadership assignment, privilege modification, admin dashboards.
2. **State-Changing Operations on Resources**:
   - `CREATE`, `UPDATE`, `DELETE` routes handling user data, status transitions, or broadcasts.
3. **Object-Level Lookups**:
   - Endpoints retrieving resources via URL parameters (`:id`, `:uuid`, `:pk`).
4. **Bypass Signals**:
   - Skipped authorization filters (e.g. `skip_authorization`, `allow_anonymous`, `unprotected_endpoints`).

---

## 4. Stage 3: Deep Code Inspection & Vulnerability Identification

Systematically review the controller handlers, policy classes, and database query wrappers against the checklist.

### Target Vulnerability Patterns to Identify:

#### A. Broken Object Level Authorization (BOLA / IDOR)
- **Pattern**: Controller fetches an object by `params[:id]` or `params[:uuid]` without scoping the query to `current_user` or evaluating policy scope (`policy_scope`).
- **Example**: `Task.find(params[:id])` instead of `current_user.tasks.find(params[:id])`.

#### B. Missing Function Level Access Control (FLAC)
- **Pattern**: Administrative or state-changing actions lacking explicit role/permission checks or decorators.
- **Example**: `POST /admin/roles` accessible to any authenticated user.

#### C. Bypassed / Skipped Authorization Guards
- **Pattern**: Controllers explicitly skipping global authorization callbacks or misconfiguring filter skip lists.
- **Example**: `before_action :skip_authorization` applied globally, or `before_action :authenticate_user!, except: [:destroy]`.

#### D. Privilege Escalation via Mass Assignment
- **Pattern**: User update/registration endpoints accepting raw request body payloads without filtering role/permission fields.
- **Example**: `params.require(:user).permit!` allowing `{ role: "admin" }` injection.

#### E. Token-Based Unauthenticated Access Flaws
- **Pattern**: Actions relying on predictable/guessable tokens or primary keys to allow unauthenticated state changes or deletions.

---

## 5. Output Report Requirements & Persistence

To ensure complete, modular documentation, running this skill **MUST MANDATORILY GENERATE 3 SEPARATE MARKDOWN REPORTS** in the target directory (e.g. `scripts/extras/exercise-14/` or `docs/`):

1. **Authorization Matrix Report**: `<app_name>_authorization_matrix.md`
2. **Authorization Security Checklist**: `<app_name>_authorization_checklist.md`
3. **Authorization Code Review & Findings Report**: `<app_name>_authorization_security_code_review.md`

> **Note**: Do NOT combine all sections into a single file. Generate each of the three files below.

---

### Report 1 Template: `<app_name>_authorization_matrix.md`

```markdown
# Application Authorization Matrix

## Application: `<App Name>`
- **Assessed Commit**: `#<commit_hash>`

---

## 1. Overview & Legend
- `ALLOW` (✅): Permitted action
- `DENY` (❌): Forbidden action
- `OWNER` (👤): Permitted ONLY if user owns the specific resource
- `SCOPED` (🔒): Permitted ONLY within user's assigned scope (Chapter, Org, Group)

---

## 2. Authorization Matrix Table

| Resource / Action | Policy / Controller Method | Public / Guest | Regular User | Scoped Role | Admin |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **`<Resource>`** | | | | | |
| `<Action Name>` | `<handler/policy>` | ❌ | 👤 (OWNER) | 🔒 (SCOPED) | ✅ |

---

## 3. Policy Enforcement Architecture
Explanation of central authorization enforcement mechanisms and policy resolution flows.
```

---

### Report 2 Template: `<app_name>_authorization_checklist.md`

```markdown
# Application Authorization Security Review Checklist

## Application: `<App Name>`
- **Assessed Commit**: `#<commit_hash>`

---

## 1. High-Priority Route Authorization Checklist
- [ ] **`<Route 1>`**: Verify object-level query scoping (`policy_scope`).
- [ ] **`<Route 2>`**: Check role enforcement on state-changing POST/PUT/DELETE.

## 2. Policy Enforcement & Guardrails Checklist
- [ ] **Global Verification**: Confirm `after_action :verify_authorized` or equivalent global callback is active.
- [ ] **Skip Authorization Review**: Audit occurrences of `skip_authorization` or `allow_anonymous`.

## 3. Mass Assignment & Strong Parameters Checklist
- [ ] Confirm role and permission fields are excluded from permitted parameter lists.
```

---

### Report 3 Template: `<app_name>_authorization_security_code_review.md`

```markdown
# Authorization Security Code Review & Findings Report

## Application: `<App Name>`
- **Assessed Commit**: `#<commit_hash>`

---

## 1. Confirmed Authorization Vulnerabilities

### 🔴 Finding 1: `<Vulnerability Title>` (`<CWE ID>`)
* **Vulnerability Type**: BOLA / Missing FLAC / Guard Bypass / Privilege Escalation
* **Severity**: `CRITICAL` | `HIGH` | `MEDIUM`
* **File Location**: `<file_path>:<line_numbers>`
* **Vulnerable Code**:
  ```<language>
  // Vulnerable code snippet
  ```
* **Flaw Analysis**: Detailed explanation of how the authorization check fails or is bypassed.
* **Remediation**:
  1. `<Step 1 to fix code>`
  2. `<Step 2 to fix policy>`

---

## 2. Verified Secure Authorization Controls

* **`<Control Name>`** (`<file_path>:<line_numbers>`): Verified secure implementation of `<policy/check>`.
```
