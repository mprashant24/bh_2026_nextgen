# Bridge Troll — Configuration & Headers Security Checklist

We assessed commit `#40747c6510014958c9519d3708b5dc9325a0cc1c`

This checklist synthesizes the **Configuration Audit Skill** (`configuration-audit`) to guide manual security code review for the Bridge Troll application (`c:/workspace/bridge_troll`).

---

## 1. Framework Settings & CSRF Checklist
- [x] **CSRF Protection**: Confirm global CSRF token verification is enforced.
  - [x] Result: `protect_from_forgery` is enabled globally in `app/controllers/application_controller.rb:4`.
  - [x] Result: Origin checking (`config.action_controller.forgery_protection_origin_check = true`) is enabled in `request_forgery_protection.rb`.
- [x] **Production Error Handling**: Verify diagnostic/debug modes are disabled.
  - [x] Result: `config.consider_all_requests_local = false` is correctly set in `production.rb:18`, preventing stack trace leakage on 500 errors.

## 2. Security Headers & CORS Checklist
- [x] **[FAIL] Content Security Policy (CSP)**: Verify CSP restricts `script-src` and disables `unsafe-inline` where possible.
  - [x] Result: The CSP block in `config/initializers/content_security_policy.rb` is entirely commented out. No CSP is enforced.
- [x] **HSTS & Secure Transport**: Confirm `Strict-Transport-Security` is active.
  - [x] Result: `config.force_ssl = true` is enabled in `production.rb:48` with `hsts: { preload: true, subdomains: true, expires: 1.year }`.
- [x] **CORS Origins**: Verify CORS rules restrict origins to specific trusted domains.
  - [x] Result: `rack-cors` configuration in `config/initializers/cors.rb` is commented out. No permissive CORS wildcard (`*`) flaws exist.

## 3. Dependency Management Checklist
- [x] **Audit Integration**: Verify dependency scanning tools are used.
  - [x] Result: `brakeman` (Rails SAST scanner) is included in the `:test, :development` groups in `Gemfile`.
