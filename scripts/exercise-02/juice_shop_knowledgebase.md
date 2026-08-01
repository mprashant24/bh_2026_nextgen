# Security & Architecture Knowledge Base: Node.js / Express & OWASP Juice Shop

This knowledge base provides reference architecture, dependency patterns, threat modeling concepts, trust boundaries, and security controls specifically designed for analyzing Node.js/Express backends, Angular frontends, and the OWASP Juice Shop application.

---

## 1. Application Architecture & Dependency Analysis

### Key Package Manifest Files
- **Node.js Dependencies**: Defined in `package.json`, locked in `package-lock.json` or `yarn.lock`.
- **Frontend Dependencies**: Angular dependencies located in `package.json` under `dependencies` and `devDependencies`.

### Security-Relevant Node.js & Express Libraries

#### Input Validation & Sanitization
- **Joi / Zod / Validator / Express-Validator**: Schema-based and middleware validation for request body, query, and params.
- **Sanitize-HTML / DOMPurify**: Contextual HTML sanitization to prevent Stored & Reflected XSS.

#### Authentication & Session Management
- **jsonwebtoken (JWT)**: Stateless token authentication. Requires strong secrets (HS256/RS256) and explicit algorithm verification.
- **passport.js / express-jwt**: Middleware for authentication strategies (Local, OAuth2, JWT).
- **express-session / cookie-session / cookie-parser**: State-based sessions. Must configure `httpOnly`, `secure`, and `sameSite` flags.

#### Authorization & Access Control
- **casbin / accesscontrol**: Role-Based Access Control (RBAC) and Attribute-Based Access Control (ABAC).

#### HTTP Security Headers & Traffic Control
- **helmet**: Sets security headers (CSP, X-Content-Type-Options, X-Frame-Options, HSTS).
- **cors**: Controls Cross-Origin Resource Sharing. Must avoid wildcard origins (`*`) with credentials.
- **express-rate-limit / rate-limiter-flexible**: Prevents brute-force, credential stuffing, and DoS attacks.
- **hpp**: Protects against HTTP Parameter Pollution.

#### Cryptography & Hashing
- **bcrypt / argon2 / scrypt**: Password hashing functions with salt and work factors.
- **crypto**: Built-in Node.js module for AES encryption, HMAC, and random token generation (`crypto.randomBytes`).

#### Logging & Auditing
- **winston / bunyan / morgan**: Structured logging utilities. Ensure sensitive data (passwords, tokens, PII) is redacted.

### Frontend Technologies (Angular)
- **Angular 14+ / Angular Material**: Component-based framework with built-in Contextual Output Encoding for XSS defense.
- **Dangerous Angular APIs**: `bypassSecurityTrustHtml`, `bypassSecurityTrustScript`, `bypassSecurityTrustResourceUrl`, `ElementRef.nativeElement`, and `eval()` bypass default Angular XSS sanitization and introduce DOM XSS vectors.

### Database ORMs & Data Access
- **Sequelize / Knex / TypeORM / Prisma**: ORM/Query builders for SQLite, PostgreSQL, MySQL. Raw queries (`sequelize.query()`) with concatenated strings introduce SQL Injection.
- **Mongoose**: ODM for MongoDB. Unsanitized query objects introduce NoSQL Injection (`$gt`, `$ne`).

### Template Engines & Rendering
- **Pug (formerly Jade) / EJS / Handlebars / Mustache / Nunjucks**: Server-side template rendering. Unescaped template variables (`!=` in Pug, `<%-` in EJS) lead to Server-Side Template Injection (SSTI) or XSS.

---

## 2. Threat Modeling Framework for OWASP Juice Shop

### Assets & Sensitive Data
1. **User Data**: Passwords (hashes), email addresses, security questions/answers, payment details, shipping addresses.
2. **System Assets**: Admin credentials, JWT secret keys, API endpoints, SQLite/PostgreSQL database files, server file system (`/ftp`, uploads).
3. **Business Logic**: Order checkout processing, coupon/discount code validation, review submission, challenge instructor state.

### Trust Boundaries
1. **Internet <-> Frontend Client**: Untrusted browser environment interacting with Angular web app.
2. **Frontend Client <-> Express API Server**: API requests across network boundary (`/api`, `/rest`, `/ftp`, `/socket.io`).
3. **Express App <-> SQLite Database**: Data persistence layer boundary.
4. **Express App <-> File System**: Internal file storage for product images, user uploads, logs, and FTP documents.
5. **Express App <-> External Services**: Payment gateways, OAuth providers, or third-party integrations.

### Primary Threat Actors
- **Anonymous External Attackers**: Attempting unauthenticated access, API scraping, brute-force, SQLi, and path traversal.
- **Authenticated Regular Users**: Attempting Privilege Escalation (vertical), IDOR/BOLA (horizontal), and stored XSS against other users/admins.
- **Malicious Insiders / Compromised Admin Accounts**: Attempting full system compromise or data exfiltration.

---

## 3. Vulnerability Patterns & OWASP Top 10 Mapping

### A01:2021 – Broken Access Control
- **Insecure Direct Object References (IDOR/BOLA)**: Manipulating `BasketId`, `UserId`, or `OrderId` in API paths (`/rest/basket/:id`).
- **Privilege Escalation**: Overwriting user roles during registration or profile updates via Mass Assignment (`{ role: "admin" }`).
- **Missing Function Level Access Control**: Admin-only routes (`/rest/admin/change-password`) accessible without admin token validation.
- **Directory Traversal / Path Traversal**: Fetching arbitrary server files via unsanitized file path parameters in download/FTP endpoints (`/ftp/legal.md%00.pdf`).

### A02:2021 – Cryptographic Failures
- **Weak Password Hashing**: Using MD5 or simple SHA1 instead of bcrypt/argon2 for password/security answer storage.
- **Hardcoded JWT Secrets**: Using predictable or default secrets (`jwtSecret: "super-secret-key"`).
- **Sensitive Data Exposure**: Returning hashed security answers or authorization tokens in user profile API responses.

### A03:2021 – Injection
- **SQL Injection (SQLi)**: Unsanitized input concatenated into Sequelize raw queries or SQLite queries (e.g., login form `' OR 1=1--`).
- **Cross-Site Scripting (XSS)**:
  - **Stored XSS**: User reviews, feedback, or profile usernames rendering unsanitized HTML in admin panels or product pages.
  - **DOM XSS**: Misuse of `bypassSecurityTrustHtml()` or `eval()` in Angular client components.
- **Server-Side Template Injection (SSTI)**: Dynamic Pug/EJS template evaluation with user input.

### A04:2021 – Insecure Design & Business Logic Flaws
- **Security Question Bypass**: Predictable security questions enabling account takeover without password.
- **Basket/Checkout Manipulations**: Negative product quantities, duplicate coupon code usage, or client-side price tampering.

### A05:2021 – Security Misconfiguration
- **Exposed Admin Endpoints & Internal Docs**: Publicly accessible debug routes or Swagger UI.
- **Verbose Error Messages**: Uncaught exceptions returning full stack traces and database queries to the client.

### A07:2021 – Identification and Authentication Failures
- **Brute-Force Vulnerability**: Absence of rate limiting on `/rest/user/login`.
- **Weak Password Policies**: No length or complexity requirements enforced during user registration.

---

## 4. Security Control Recommendations

1. **Robust Access Control**: Implement centralized authorization middleware verifying `req.user.id` against resource ownership on all REST/GraphQL endpoints.
2. **Parameterized Database Queries**: Use ORM abstraction methods (`Model.findOne()`) exclusively; never concatenate user input into SQL query strings.
3. **Context-Aware Output Encoding & Sanitization**: Utilize `DOMPurify` on the frontend and `sanitize-html` on the backend for all user-generated content before storage and rendering.
4. **Strong Authentication & Secrets Management**: Use `argon2` or `bcrypt` with salt, store JWT secrets in environment variables (`process.env.JWT_SECRET`), and enforce multi-factor authentication (MFA).
5. **Rate Limiting & Threat Mitigation**: Apply `express-rate-limit` to login, password reset, and registration endpoints.
6. **Security Headers**: Enable `helmet` with a strict Content Security Policy (CSP), disable `X-Powered-By`, and enforce HSTS.
7. **Strict File Handling**: Validate file extensions against allowlists, sanitize file paths using `path.basename()`, and prevent directory traversal.



