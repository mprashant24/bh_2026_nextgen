We assessed commit `#c1a8ae34712cdd6529c59af9e79c5e6a8900ade5`

# Notes for you/your team

## Behavior

* **What does it do? (business purpose)**
  BHIMA (Basic Hospital Information Management Application) is an open-source Hospital Information Management System (HIMS) and accounting software. It manages hospital operations including patient registration, medical records, financial accounting (income/expenses, budgeting, debtor billing, subsidies), inventory/pharmacy stock control, purchasing, asset management, and payroll, conforming to western/central African OHADA accounting standards.

* **Who does it do this for? (internal / external customer base)**
  - **Internal**: Hospital administrators, doctors, nurses, pharmacists, cashiers/accountants, stock managers, and data entry clerks.
  - **External**: Aid organizations, donor agencies (e.g. FCDO, IMA World Health), governmental/non-governmental health agencies, and Western/Central African health regulators.

* **What kind of information will it hold?**
  - **Patient PII & Medical Records**: Names, medical histories, clinical diagnoses, prescriptions, lab results, triage data.
  - **Financial Data**: Patient invoices, organizational billing, income/expense ledgers, budgets, debtor subsidies, payroll, taxes (IPR tax).
  - **Inventory & Pharmacy**: Drug stock levels, medical supplies, pricing structures, asset registers, supplier details.
  - **System Credentials**: User accounts, hashed passwords, roles, permission assignments, session tokens (JWT / Redis).

* **What are the different types of roles?**
  - **System / Enterprise Administrator**: System configuration, enterprise management, user/role administration.
  - **Finance Manager / Accountant**: Financial ledgers, debtor group invoicing, budgets, OHADA reporting, payroll.
  - **Doctor / Physician**: Clinical consultations, medical records, prescriptions, ordering lab tests.
  - **Nurse / Triage Staff**: Patient intake, vital signs, ward management.
  - **Pharmacist / Stock Manager**: Pharmacy inventory, stock movements, dispensing, purchasing.
  - **Data Collector / Clerk**: Patient registration, basic data entry, survey form management.

* **What aspects concern your client/customer/staff the most?**
  - **Patient Confidentiality & Data Privacy**: Preventing unauthorized exposure or leakage of sensitive medical records and PII.
  - **Financial Integrity & Fraud Prevention**: Preventing cash skimming, improper discount grants, unauthorized billing modifications, or stock tampering.
  - **Availability & Resilience**: Ensuring high system uptime and reliable operation in remote/low-resource clinic environments with intermittent power/network connectivity.
  - **Role Segregation & Access Control**: Enforcing strict permission checks to prevent unauthorized privilege escalation or data tampering across departments.

## Tech Stack

* **Framework & Language** - Client: AngularJS (JavaScript) | Server: Node.js (Express.js)
* **3rd party components**:
  * Node modules (npm packages): `express`, `jsonwebtoken`, `redis`, `mysql2`, `pdfmake`, `bcryptjs`, `mocha`, `karma`, `playwright`
  * Client libraries: AngularJS 1.x, Bootstrap, UI-Router, FontAwesome
  * Dependent services: External SMTP servers (email reports), cron job runners
* **Datastore** - MySQL (Primary Relational Database), Redis (Session Store & Token Management)


## Brainstorming / Risks

* **SQL Injection via String Formatting**: While `mysql.format()` and parameterized placeholders (`?`) are standard, developers might construct queries via raw string concatenation or template literals before passing to `db.exec()`, especially in complex filtering routes (e.g. `groups.js` queries or reporting endpoints).
* **Cross-Site Scripting (XSS) in Client Rendering**: Unsafe use of AngularJS `$sce.trustAsHtml()` or `ng-bind-html` when rendering user-submitted medical notes, survey form metadata, or custom report templates.
* **Insecure Direct Object References (IDOR/BOLA)**: Endpoints fetching or modifying resources by primary key or UUID (e.g., `/medical/patients/:id`, `/finance/vouchers/:id`, `/locations/detail/:uuid`) without enforcing server-side ownership or project authorization.
* **Privilege Escalation via Role/Group Management**: Routes like `/admin/roles`, `/admin/users/assignRolesToUser`, or `/groups/:key/:id` accepting raw role or group update payloads without validating if the current user possesses administrative permissions.
* **Session & Authentication Token Hijacking**: Misconfigured `SESS_SECRET` in `.env`, lack of HTTPS/Secure cookie flags in non-production environments, or improper JWT token revocation on `/auth/logout`.
* **Public Information Exposure**: Unauthenticated access to public routes listed in `access.js` (`/languages`, `/projects`, `/units`, `/currencies`, `/helpdesk_info`) leaking enterprise metadata or sensitive internal settings.

## Checklist of things to review

### Risks
- [ ] Audit client templates for `ng-bind-html` and `$sce.trustAsHtml` usage with unescaped user input (XSS risk).
- [ ] Check `server/lib/db/index.js` `db.exec()` calls across all controllers for string concatenation or template literal query formatting.
- [ ] Review file upload handling in `server/lib/uploader.js` for path traversal, unrestricted file extensions, or shell upload vulnerabilities.
- [ ] Inspect session store setup in `server/config/express.js` (`SESS_SECRET`, `RedisStore`, cookie flags `httpOnly`, `secure`, `sameSite`).

### Authentication
- [ ] Inspect `/auth/login` in `server/controllers/auth.js` to ensure login error messages do not allow user enumeration.
- [ ] Verify password verification and hashing in `server/lib/password.js` (`bcryptjs`) to ensure plain-text passwords are never logged or stored.
- [ ] Check JWT token creation & verification in `server/config/jwt.js` and confirm token invalidation upon `/auth/logout`.

### Authorization
- [ ] Inspect `server/config/access.js` middleware to ensure all non-public API routes enforce valid JWT tokens and active user sessions.
- [ ] Check role-assignment controllers (`/admin/roles.js`, `/admin/users/`) to ensure users cannot elevate their own privileges.
- [ ] Verify IDOR protections on patient records (`/medical/patients`), financial vouchers (`/finance/vouchers`), and invoices (`/finance/patientInvoice`).

### Auditing/Logging
- [ ] Inspect `morgan` and `debug` logging configurations in `server/app.js` & `server/config/express.js` to prevent sensitive credentials or JWT tokens from leaking in log files.
- [ ] Verify audit log tracking for administrative actions (user creation, role modifications, financial ledger edits).

### Injection
- [ ] Search for raw SQL string formatting or concatenated parameters across `server/controllers/` (e.g. `DELETE FROM ${key} WHERE ${subscription.entity} = ?` in `groups.js`).
- [ ] Review raw MySQL query handlers for array or object parameter manipulation flaws.

### Cryptography
- [ ] Verify `SESS_SECRET` and `JWT_SECRET` in `server/config/jwt.js` and `server/config/express.js` enforce high entropy and environment variable loading.
- [ ] Confirm all sensitive communications (patient medical records, financial data, auth tokens) require HTTPS in production.

### Configuration
- [ ] Run static analysis security tools (`npm audit`, `eslint-plugin-security`) across server and client codebases.
- [ ] Verify production environment settings (`NODE_ENV=production`, `trust proxy=true`, `cookie.secure=true`) in `server/config/express.js`.

## Mapping / Routes

- [x] `POST /auth/login` -> `server/controllers/auth.js` (`loginRoute`)
- [x] `GET /auth/logout` -> `server/controllers/auth.js` (`logout`)
- [x] `GET /languages` -> `server/controllers/admin/languages.js` (`list`) [Public]
- [x] `GET /projects` -> `server/controllers/admin/projects.js` (`list`) [Public]
- [x] `POST /admin/roles` -> `server/controllers/admin/roles.js` (`create`)
- [x] `POST /admin/roles/assignTouser` -> `server/controllers/admin/roles.js` (`assignRolesToUser`)
- [x] `POST /groups/:key/:id` -> `server/controllers/groups.js` (`updateSubscriptions`)
- [x] `GET /medical/patients` -> `server/controllers/medical/patients.js` (`list`)
- [x] `POST /finance/vouchers` -> `server/controllers/finance/vouchers.js` (`create`)
- [x] `GET /locations/detail/:uuid` -> `server/controllers/admin/locations.js` (`detail`)

## Mapping / Authorization Decorators

- [x] `access.js` (Express global auth middleware: validates `x-access-token` JWT header & active `req.session.user`)
- [x] `publicRoutes` array in `server/config/access.js` (Explicit list of unauthenticated public API routes)
- [x] `JWTConfig.verify(token)` in `server/config/jwt.js` (JWT signature validation)
- [x] Role/action checking queries in `server/controllers/admin/roles.js` (`hasAction`, `listForUser`)

## Mapping / Files

- [x] `server/app.js` (Central HTTP server & Express application initialization)
- [x] `server/config/express.js` (Middleware stack, Helmet HTTP headers, Redis session store)
- [x] `server/config/routes.js` (Master API route definitions)
- [x] `server/config/access.js` (JWT authentication & public route access control middleware)
- [x] `server/config/jwt.js` (JWT configuration, token signing & verification)
- [x] `server/lib/db/index.js` (Database connector & MySQL query execution wrapper)
- [x] `server/controllers/auth.js` (User authentication, password verification, session loading)
- [x] `server/controllers/admin/roles.js` (Role & permission management controller)
- [x] `client/app/app.js` (AngularJS client application root module)
