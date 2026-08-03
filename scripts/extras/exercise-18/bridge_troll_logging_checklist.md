# Bridge Troll — Logging & Security Auditing Checklist

We assessed commit `#40747c6510014958c9519d3708b5dc9325a0cc1c`

This checklist synthesizes the **Logging & Auditing Security Skill** (`logging-auditing-audit`) to guide manual security code review for the Bridge Troll application (`c:/workspace/bridge_troll`).

---

## 1. Logging Framework & Configuration Checklist

- [x] **Logging Library Identification**: Confirm Rails standard logger (`ActiveSupport::TaggedLogging` wrapping Ruby `Logger`) is initialized in `config/environments/production.rb`.
- [x] **[FAIL] Verbose Production Log Level**: Inspect `config.log_level` in `config/environments/production.rb:58`:
  - **Check**: Verify if `config.log_level = :debug` is explicitly set in production.
  - **Risk**: Verbose `:debug` level logs SQL query strings, database parameter bindings, internal session payloads, and HTTP request attributes to production log streams.
- [ ] **Log Storage & Rotation**: Inspect STDOUT / file logger configuration (`config.logger = ActiveSupport::TaggedLogging.new(Logger.new($stdout))`):
  - **Check**: Confirm log rotation / stdout buffer limits are enforced by host environment (Heroku / Docker) to prevent memory or disk exhaustion.

---

## 2. Sensitive Data Leakage & Parameter Filtering Checklist

- [x] **Parameter Log Filter Configuration**: Inspect `config/initializers/filter_parameter_logging.rb`:
  - **Check**: Confirm ActiveSupport parameter filter list filters sensitive keys:
    ```ruby
    Rails.application.config.filter_parameters += %i[
      passw email secret token _key crypt salt certificate otp ssn cvv cvc
    ]
    ```
- [x] **HTTP Headers & Session Data**: Confirm authorization tokens in HTTP request headers (`x-access-token`, `Authorization: Bearer`) or cookies are filtered or excluded from public loggers.
- [x] **Explicit Controller Logging Audit**:
  - [x] Audit controllers (`app/controllers/**/*.rb`) for explicit `logger.info` or `Rails.logger.debug` invocations containing raw user objects, PII, or credentials.
  - [x] Result: No explicit `Rails.logger` calls dumping raw user models or passwords were found in controller handlers.

---

## 3. Security Audit Trail Completeness Checklist

- [x] **[FAIL] Missing Authentication Audit Logging**:
  - [x] Inspect Devise authentication controller overrides (`DeviseOverrides::SessionsController` / `DeviseOverrides::RegistrationsController` / `OmniauthCallbacksController`).
  - [x] **Check**: Verify whether failed login attempts, password resets, or OAuth logins create structured audit log entries (recording timestamp, target email/user ID, client IP address, and success/failure status).
  - [x] **Risk**: Absence of login failure audit logging prevents security teams from detecting active credential stuffing, password guessing attacks, or brute-force campaigns.
- [x] **[FAIL] Missing Administrative Action Audit Logging**:
  - [x] Inspect administrative controllers (`AdminPagesController`, `Chapters::LeadersController`).
  - [x] **Check**: Verify whether appointing chapter leaders (`POST /chapters/:chapter_id/leaders`), publishing events (`events/unpublished_events#publish`), or mass email broadcasts (`events/emails#create`) generate audit records.
  - [x] **Risk**: Lack of audit trails for administrative role assignments or broadcast emails hinders incident investigation and insider threat tracking.

---

## 4. Log Injection & Error Handling Checklist

- [ ] **Log Injection / CRLF Sanitization (CWE-117)**: Inspect logged parameters to ensure user-supplied input (e.g. search queries or request IDs) containing newlines (`\r\n`) cannot inject forged log lines.
- [ ] **Exception Stack Trace Disclosure**: Confirm production error handlers (`config.consider_all_requests_local = false`) suppress raw stack traces and database credentials from client HTTP responses.
