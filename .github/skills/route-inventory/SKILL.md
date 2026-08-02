---
name: route-inventory
description: 'Perform an automated route and API endpoint inventory across codebases. Identifies routing files by technology (Express, Rails, Django, Spring, Flask, Fast API, ASP.NET, Go, Next.js), decorates endpoints with security context (Auth, Roles, Sensitive Data PII/PHI/Financial, Known Vulns, Privileges, Debug/Auth route flags, Secure Parameters), and computes security relevance rankings (First-Degree vs Second-Degree priority).'
argument-hint: 'Path to repository or technology stack (e.g. ./server or Node/Express)'
user-invocable: true
---

# Route & API Inventory Skill

This skill provides a systematic procedure for mapping, decorating, and prioritizing all application routes and API endpoints in a codebase for security code reviews.

---

## 1. Routing Location & Technology Identification (Flexible Guidance)

> **Important**: The file patterns and technology signatures below are **flexible guidance**, not a fixed or rigid scope. Modern codebases frequently use custom directory layouts, hybrid stacks, internal routing abstractions, gateway reverse-proxies, or non-standard framework conventions. Always adapt your search dynamically based on the project's actual architecture and configuration.

### Discovery Principles & Guidance
1. **Explore Beyond Standard Paths**: Check for custom route registration files, microservice entrypoints, serverless function handlers (AWS Lambda, Azure Functions), and API gateway definitions (e.g., GraphQL schemas, gRPC proto files, OpenAPI/Swagger specs).
2. **Inspect Infrastructure-as-Code (IaC) & Network Ingress**: Search Terraform (`*.tf`), Helm charts (`templates/*.yaml`), Kubernetes Ingress/Service manifests (`ingress.yaml`, `service.yaml`), API Gateway configs, and reverse-proxy settings (Nginx, HAProxy, Envoy) to determine whether routes are **INTERNET_EXPOSED** or **INTERNAL_ONLY**.
3. **Trace Application Entrypoints**: Inspect main startup scripts (`app.js`, `main.py`, `Program.cs`, `main.go`, `config/routes.rb`) and follow middleware chains or controller imports to discover non-standard route definitions.
4. **Scan for Generic Route Declarations**: Look for HTTP method registrations (`GET`, `POST`, `PUT`, `DELETE`, `PATCH`), annotation/decorator tags (`@Route`, `@GetMapping`), or file-system route structures across all source folders.

### Infrastructure & Network Exposure Mapping Matrix (IaC Guidance)

| IaC / Config File Type | File / Manifest Patterns | Exposure Inspection Signals | Scope Classification |
| :--- | :--- | :--- | :--- |
| **Kubernetes Ingress / Gateway API** | `ingress.yaml`, `helm/*/templates/ingress.yaml` | `spec.rules[].host`, annotations (`kubernetes.io/ingress.class: nginx`), TLS certs | `EXTERNAL_INTERNET_EXPOSED` |
| **Kubernetes Service** | `service.yaml`, `values.yaml` | `type: LoadBalancer`, `type: NodePort` (External) vs `type: ClusterIP` (Internal) | `EXTERNAL` vs `INTERNAL_PRIVATE` |
| **Terraform (AWS / Azure / GCP)** | `*.tf` (`aws_lb_listener`, `aws_security_group`) | `internal = false`, `cidr_blocks = ["0.0.0.0/0"]`, `aws_api_gateway_rest_api` | `EXTERNAL_INTERNET_EXPOSED` |
| **Reverse Proxy (Nginx / HAProxy / Envoy)** | `nginx.conf`, `haproxy.cfg`, `envoy.yaml` | `server_name example.com;`, `location /api/`, `allow / deny` IP rules | `EXTERNAL` vs `INTERNAL_RESTRICTED` |
| **Service Mesh (Istio / Linkerd / Consul)** | `VirtualService.yaml`, `AuthorizationPolicy` | `gateways: [mesh]` (Internal) vs `gateways: [ingressgateway]` (External) | `SERVICE_MESH_PRIVATE` |

### Technology Reference Reference Matrix (Guidance Only)

| Framework / Technology | Typical File Patterns / Locations | Route Discovery Patterns |
| :--- | :--- | :--- |
| **Node.js / Express** | `routes/*.js`, `controllers/**/*.js`, `app.js`, `server.js` | `app.get()`, `app.post()`, `router.route()`, `express.Router()` |
| **Ruby on Rails** | `config/routes.rb`, `app/controllers/**/*.rb` | `resources :name`, `get '/path'`, `post '/path'`, `namespace :admin` |
| **Python / Django** | `urls.py`, `**/urls.py`, `views.py` | `path('route/', view)`, `re_path()`, `urlpatterns = [...]`, `@api_view()` |
| **Python / FastAPI & Flask** | `main.py`, `app.py`, `views/*.py`, `routers/*.py` | `@app.get()`, `@app.post()`, `@router.get()`, `@app.route()` |
| **Java / Spring Boot** | `src/main/java/**/*Controller.java` | `@RestController`, `@RequestMapping`, `@GetMapping`, `@PostMapping` |
| **C# / ASP.NET Core** | `Controllers/*.cs`, `Program.cs` | `[ApiController]`, `[Route("api/[controller]")]`, `[HttpGet]`, `app.MapGet()` |
| **Go / Gin, Mux & Chi** | `main.go`, `routes/*.go`, `controllers/*.go` | `r.HandleFunc()`, `r.GET()`, `r.POST()`, `r.Group("/api")` |
| **TypeScript / Next.js** | `pages/api/**/*.ts`, `app/api/**/route.ts` | File-system routing (`route.ts`, `GET()`, `POST()`, `DELETE()`) |

---

## 2. Route Security Context Decoration

For every discovered route, analyze the handler function, middleware chain, input schemas, and database queries to extract and assign the following **Security Context Attributes**:

### Context Attributes
1. **Network Exposure & Transport Protocol (IaC & Architecture Derived)**:
   - **Exposure Scope**:
     - `EXTERNAL_INTERNET_EXPOSED`: Route accessible from the public internet via Public Ingress, External Load Balancer (`0.0.0.0/0`), API Gateway, or Public Domain.
     - `INTERNAL_PRIVATE_ONLY`: Route restricted to internal VPC/VNet, Private Subnet, `ClusterIP`, Internal Load Balancer, or IP allowlist.
     - `SERVICE_MESH_PRIVATE`: Intra-cluster service-to-service communication gated by sidecar proxy / mTLS.
   - **Protocol & API Style**:
     - `HTTPS` / `HTTP`: Standard REST / Web API over HTTP (notes whether TLS transport encryption is enforced vs unencrypted HTTP).
     - `WSS` / `WS`: Real-time WebSocket connection (notes whether Secure WSS with TLS is enforced, plus origin check & socket auth).
     - `GRPC`: High-performance binary RPC over HTTP/2 (notes gRPC interceptors, mTLS, and proto definition).
     - `GRAPHQL`: Single-endpoint GraphQL API (notes query depth limits, introspection status, and field-level auth).
     - `SOAP`: XML-based web service (notes XXE protections and WS-Security signatures).
2. **Route Type Category**:
   - `AUTHENTICATION`: Endpoints managing user identity, sessions, credentials, OAuth, or password recovery (`/auth/login`, `/auth/logout`, `/auth/reload`, `/password/reset`).
   - `DEBUG_DIAGNOSTIC`: Endpoints exposing system status, debug logs, health checks, metrics, or internal configs (`/system/information`, `/debug`, `/actuator`, `/metrics`, `/env`).
   - `BUSINESS_LOGIC`: Core domain operations (medical, financial, inventory, user data).
   - `ADMINISTRATIVE`: Privileged management interfaces (`/admin/users`, `/admin/roles`).
2. **Authentication Status**:
   - `UNAUTHENTICATED` / `PUBLIC` (No login required)
   - `AUTHENTICATED` (Requires valid session token / JWT)
3. **Authorization & Role Requirements**:
   - Explicit roles or permissions required (e.g., `Admin`, `Finance_Manager`, `Doctor`, `is_staff`, `user.has_perm()`).
4. **Sensitive Data Classification**:
   - `PII` (Personally Identifiable Information: Names, Emails, Phone Numbers, Addresses)
   - `PHI` (Protected Health Information: Medical histories, Diagnoses, Prescriptions, Lab Results)
   - `FINANCIAL` (Credit Cards, Invoices, Bank Details, Ledgers, Subsidies, Payroll)
   - `CREDENTIALS` / `SECRETS` (Passwords, API Keys, Tokens)
   - `NONE` / `PUBLIC_DATA`
5. **Secure Parameter Types & Locations**:
   - Explicitly identify and list all parameter locations and secure data types passed into the route:
     - **Location / Passing Mechanism**:
       - `QUERY` (URL query parameters, e.g., `?q=`, `?token=`, `?user_id=`)
       - `BODY` (JSON, Form-data, URL-encoded payload, e.g., `password`, `ssn`, `credit_card`)
       - `HEADER` (HTTP headers, e.g., `x-access-token`, `Authorization`, `x-user-role`, `Cookie`)
       - `PATH` (URL path parameters/slugs, e.g., `/users/:id`, `/locations/:uuid`)
     - **Secure Parameter Classification**:
       - `CREDENTIALS_SECRET` (Passwords, Private Keys, JWTs, Auth Tokens)
       - `SENSITIVE_PII_PHI` (SSN, Medical Diagnostics, Personal Contact Info)
       - `FINANCIAL_DATA` (Credit Card numbers, Bank Account numbers, Account Balances)
       - `HIGH_RISK_CONTROL` (Role name, User ID overrides, SQL clauses, File paths)
       - `STANDARD_INPUT` (Search keywords, Pagination offsets, Language codes)
6. **Privileges Needed / State Impact**:
   - `READ_ONLY` (GET / Safe operations)
   - `STATE_CHANGING` (CREATE, UPDATE, DELETE, Password Reset, Role Assignment)
   - `SYSTEM_ADMIN` (Process execution, File uploads, Configuration updates, Backup/Restore)
7. **Known Vulnerability / Code Flaw Present**:
   - Specific security flaws found during review (e.g., `CWE-639 IDOR`, `CWE-89 SQLi`, `CWE-352 CSRF Exempt`, `CWE-79 XSS`, `Unsanitized Shell Command`).

---

## 3. Security Relevance & Ranking Methodology

Assign a **Security Relevance Rating** (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`) to prioritize manual code review based on degree of connection:

### Security Relevance Degrees
* **First-Degree Security Relevance (Direct Target)**:
  - **EXTERNAL Internet-Exposed Routes** handling user input, authentication, or sensitive data.
  - **Authentication Routes** accepting user credentials or issuing tokens.
  - **Debug & Diagnostic Routes** exposing internal infrastructure, memory, or system configs.
  - Endpoints handling **PHI, Financial, or System Admin** operations.
  - Endpoints with **no authentication** (`PUBLIC`) that accept POST/PUT/DELETE input.
  - Endpoints with **Secure Parameters** (e.g., unvalidated Object IDs, raw SQL search inputs).
  - **Review Priority**: **TOP PRIORITY** (Immediate Deep Review)

* **Second-Degree Security Relevance (Connected / Dependency Target)**:
  - **INTERNAL_PRIVATE_ONLY** routes that receive input from or serve external front-facing endpoints.
  - Routes connected to First-Degree endpoints by **calling them** or **being called by them** (e.g., internal helper routes, webhook handlers, logging wrappers, data pipeline callbacks).
  - Routes that pass parameters directly into First-Degree endpoints or consume output from High-Relevance routes.
  - **Review Priority**: **LOWER PRIORITY** (Reviewed after First-Degree routes are verified).

### Ranking Criteria Table

| Relevance Rank | Criteria | Degree | Action Required |
| :--- | :--- | :--- | :--- |
| **CRITICAL** | Public External Auth routes (`/login`, `/reset-password`), External Debug/System info routes, Public POST/PUT/DELETE, Raw SQL execution | 1st Degree | Immediate manual code audit |
| **HIGH** | External Authenticated PHI/PII/Financial endpoints, IDOR risk on Path ID params (`:uuid`), Role update endpoints, File uploads | 1st Degree | High priority review |
| **MEDIUM** | Authenticated read-only external routes, Internal admin endpoints behind VPC, Standard user profile queries | 1st Degree | Standard review |
| **LOW** | Internal ClusterIP utilities, helper routes called by High routes, public static metadata endpoints | 2nd Degree | Secondary review / Verification |

---

## 4. Route Inventory Output Template

Present the completed route inventory as a **Single 2-Column Table** sorted strictly in ascending order of Review Priority Number (`#1`, `#2`, `#3`, ...):

1. **First Column (`Route / Security Attribute`)**:
   - For **Route Header Rows**: Format as `#<PriorityNumber>: <METHOD> <ROUTE_PATH>` (e.g., `#1: POST /chapters/:chapter_id/leaders`).
   - For **Security Decorator Sub-Rows**: Format as `├── Attribute Name` (e.g., `├── Handler`, `├── Authentication`, `├── Known Flaws / Risks`).
2. **Second Column (`Details / Value`)**:
   - For **Route Header Rows**: Contains a concise **Functional Summary** statement (1-2 sentences, max 20-25 words).
   - For **Security Decorator Sub-Rows**: Displays the specific attribute details/value.
3. **Sparse Decorators**: **ONLY include rows for security decorators that are PRESENT**. Do NOT add blank rows or empty cells if a decorator is not present/applicable.

```markdown
# Application Route Security Inventory

## Summary
- **Total Routes Identified**: `<Count>`
- **External Internet-Exposed Routes**: `<Count>`
- **Internal Private Routes**: `<Count>`
- **Protocols & API Styles**: `HTTPS: <Count>`, `WSS: <Count>`, `gRPC: <Count>`, `GraphQL: <Count>`
- **1st Degree High-Relevance Routes**: `<Count>`
- **2nd Degree Connected Routes**: `<Count>`
- **Authentication Routes**: `<Count>`
- **Debug / Diagnostic Routes**: `<Count>`

---

## Route Inventory Table (Sorted by Priority Rank)

| Route / Security Attribute | Details / Value |
| :--- | :--- |
| **`#1: POST /auth/login`** | **Functional Summary**: Authenticates user credentials and issues session JWT tokens for authorized system access. |
| ├── **Handler** | `controllers/auth.js:login` |
| ├── **Type & Exposure** | `AUTHENTICATION / EXTERNAL_INTERNET_EXPOSED (HTTPS)` |
| ├── **Authentication** | `UNAUTHENTICATED / PUBLIC` |
| ├── **Sensitive Data** | `CREDENTIALS, PII` |
| ├── **Secure Parameters** | `BODY: username (PII), password (CREDENTIALS_SECRET), project (HIGH_RISK_CONTROL)` |
| ├── **Known Flaws / Risks** | `User Enumeration, Brute Force Risk` |
| └── **Degree Connection** | `1st Degree (CRITICAL)` |
| **`#2: POST /admin/roles`** | **Functional Summary**: Creates new system security roles and assigns system-wide permission policies. |
| ├── **Handler** | `controllers/admin/roles.js:create` |
| ├── **Type & Exposure** | `ADMINISTRATIVE / EXTERNAL_INTERNET_EXPOSED (HTTPS)` |
| ├── **Authentication** | `AUTHENTICATED (JWT Session)` |
| ├── **Roles Required** | `System Admin` |
| ├── **Secure Parameters** | `HEADER: x-access-token (CREDENTIALS_SECRET), BODY: label (HIGH_RISK_CONTROL)` |
| ├── **Privileges Needed** | `SYSTEM_ADMIN` |
| ├── **Known Flaws / Risks** | `Unchecked Privilege Escalation` |
| └── **Degree Connection** | `1st Degree (CRITICAL)` |
| **`#3: GET /system/information`** | **Functional Summary**: Exposes system operational metrics and environment configuration details for administrative monitoring. |
| ├── **Handler** | `controllers/system.js:info` |
| ├── **Type & Exposure** | `DEBUG_DIAGNOSTIC / EXTERNAL_INTERNET_EXPOSED (HTTPS)` |
| ├── **Authentication** | `UNAUTHENTICATED / PUBLIC` |
| ├── **Known Flaws / Risks** | `Sensitive System Metadata Exposure` |
| └── **Degree Connection** | `1st Degree (CRITICAL)` |
| **`#4: GET /medical/patients/:id`** | **Functional Summary**: Retrieves complete patient clinical medical history, diagnoses, and personal contact details by patient ID. |
| ├── **Handler** | `controllers/medical/patients.js:detail` |
| ├── **Type & Exposure** | `BUSINESS_LOGIC / EXTERNAL_INTERNET_EXPOSED (HTTPS)` |
| ├── **Authentication** | `AUTHENTICATED (JWT Session)` |
| ├── **Roles Required** | `Doctor, Nurse` |
| ├── **Sensitive Data** | `PHI, PII` |
| ├── **Secure Parameters** | `PATH: :id (HIGH_RISK_CONTROL / Primary Key)` |
| ├── **Known Flaws / Risks** | `Potential BOLA / IDOR` |
| └── **Degree Connection** | `1st Degree (HIGH)` |
| **`#5: GET /languages`** | **Functional Summary**: Returns public list of supported application interface languages for localization. |
| ├── **Handler** | `controllers/admin/languages.js:list` |
| ├── **Type & Exposure** | `ADMINISTRATIVE / EXTERNAL_INTERNET_EXPOSED (HTTPS)` |
| ├── **Authentication** | `UNAUTHENTICATED / PUBLIC` |
| └── **Degree Connection** | `2nd Degree (LOW)` |

---

## Security Review Recommendations

### First-Degree High Priority Review Targets
1. `[CRITICAL]` **`<Route>`**: `<Functional Summary & Reason for Critical Rank>`
2. `[HIGH]` **`<Route>`**: `<Functional Summary & Reason for High Rank>`

### Second-Degree Dependency Targets
1. `[LOW]` **`<Route>`**: Connected to `<First-Degree Route>` via `<Calling/Called Relationship>`.
```

---

## 5. Report Generation & Persistence Requirements

1. **Mandatory File Output**:
   - The generated route inventory report **MUST always be saved as a Markdown (`.md`) file** in the workspace.
   - Do NOT rely solely on printing the report to chat output.

2. **Automatic Location Inference**:
   - Infer the destination folder from the user prompt or active workspace context:
     - **Exercise-Specific Tasks**: Save next to the relevant exercise folder (e.g., `scripts/extras/exercise-14/<app_name>_route_inventory.md` or `scripts/exercise-02/<app_name>_route_inventory.md`).
     - **Repository / Root Analysis**: Save in the root or `docs/` folder of the target repository (e.g., `docs/<app_name>_route_inventory.md`).

3. **User Prompting when Location Unclear**:
   - If the target file path cannot be inferred automatically from the context or exercise instructions, the agent **MUST ask the user** for the preferred destination path (using `vscode_askQuestions` or direct prompt) before generating or saving the file.

