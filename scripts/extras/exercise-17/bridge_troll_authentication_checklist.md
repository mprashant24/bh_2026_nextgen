# Bridge Troll — Authentication & Session Security Checklist

We assessed commit `#40747c6510014958c9519d3708b5dc9325a0cc1c`

This checklist synthesizes the **Authentication Audit Skill** (`authentication-audit`) and deep inspection of `config/initializers/devise.rb` to guide manual security code review for the Bridge Troll application (`c:/workspace/bridge_troll`).

---

## 1. User Identification & Credentials Checklist

- [x] **Primary Identifier**: Confirm user identity token is `email` validated via Devise `:validatable` (`app/models/user.rb`).
- [ ] **User Enumeration in Error Messages**:
  - [ ] Audit login failure responses (`devise/sessions#create`) to ensure generic `"Invalid Email or password"` errors are returned.
  - [ ] Audit password reset requests (`devise/passwords#create`) to verify response messages do not reveal whether an email exists.
  - [x] **[FAIL]** Audit OAuth provider linking (`devise_overrides/omniauth_callbacks_controller.rb:16`): Verify error alert does NOT disclose victim email address (`"already in use by #{existing_auth.user.email}"`).
- [ ] **Multi-Factor Authentication (MFA/2FA)**:
  - [ ] Check if MFA is available or enforced for administrative accounts (`admin`, `publisher`).
  - [ ] Verify backup recovery codes and TOTP seed generation security if MFA is enabled.

---

## 2. Authentication Flows & Devise Configuration Checklist (`config/initializers/devise.rb`)

### A. Secret Keys & Token Security
- [x] **[FAIL] Weak Fallback Devise Secret Key**: Inspect `config.secret_key` in `config/initializers/devise.rb`:
  - **Check**: Verify if `config.secret_key` falls back to a predictable default string when `ENV['DEVISE_SECRET_KEY']` is missing:
    ```ruby
    config.secret_key = ENV['DEVISE_SECRET_KEY'] || ('x' * 30)
    ```
  - **Risk**: Hardcoded fallback secret allows attackers to forge confirmation, password reset, and session tokens offline if the environment variable is omitted in deployment.

### B. Login Flow, Rate-Limiting & Bcrypt Stretches
- [x] **Bcrypt Stretches / Work Factor**: Verify `config.stretches = 10` in non-test environments.
- [ ] **Plaintext Credential Logging**: Check Rails logging configuration (`config/environments/production.rb`) to verify `config.filter_parameters += [:password, :password_confirmation, :current_password]` filters sensitive credentials from log files.
- [x] **[FAIL] Brute-Force & Lockout Policy Disabled**:
  - **Check**: Inspect `:lockable` configuration in `devise.rb` and `app/models/user.rb`.
  - **Risk**: `:lockable` is not included in `User` model, and `config.lock_strategy` is commented out. No rate-limiting middleware (`rack-attack`) guards `POST /users/sign_in`.

### C. Registration & Account Provisioning
- [ ] **Strong Parameter Mass Assignment**: Inspect `configure_permitted_parameters` in `ApplicationController` and `DeviseOverrides::RegistrationsController` to ensure client parameters cannot override boolean role flags (`admin`, `publisher`).
- [x] **[WARN] Account Reconfirmation Disabled**: Inspect `config.reconfirmable = false` in `devise.rb`:
  - **Risk**: When a user changes their email address, the change takes effect immediately without requiring confirmation on the new email address, allowing account takeover if an email is mistyped or hijacked.
- [x] **[WARN] Unlimited Confirmation Token Expiration**: Inspect `config.confirm_within = nil`:
  - **Risk**: Account confirmation tokens never expire, leaving long-lived confirmation links in email logs indefinitely.

### D. Password Reset & Recovery Flow
- [x] **Password Reset Token TTL**: Confirm `config.reset_password_within = 2.hours`.
- [ ] **Reset Token Randomness & Single-Use**: Confirm Devise `:recoverable` module uses cryptographically secure random token generation (`Devise.friendly_token`) and invalidates tokens upon use.

### E. OAuth / Social Login / SSO
- [ ] **OAuth CSRF State Parameter**: Confirm `omniauth-rails_csrf_protection` middleware is active for all OAuth providers (GitHub, Google, Facebook, Twitter, Meetup).
- [ ] **Redirect URI Allowlisting**: Confirm OAuth callbacks explicitly match strict registered redirect URIs.
- [x] **[FAIL] Pre-Authenticated Account Linking**: Inspect `User.from_omniauth` (`app/models/user.rb:28`): Confirm existing accounts require password re-authentication or verified email checks before linking new third-party OAuth UIDs.

---

## 3. Session Handling & Cookie Security Checklist

- [x] **[FAIL] Excessive Session Timeout TTL**: Inspect `config.timeout_in` in `config/initializers/devise.rb`:
  - **Check**: Verify session timeout length:
    ```ruby
    config.timeout_in = 2.weeks # Lillie wanted 'forever' but we compromised at '2 weeks'
    ```
  - **Risk**: Excessive 2-week idle session timeout leaves unattended workstations and hijacked session cookies active for 14 days without requiring re-authentication.
- [ ] **Cookie Security Flags**:
  - [ ] **HttpOnly**: Confirm `HttpOnly` flag is set to `true` to block JavaScript access to session cookies.
  - [ ] **Secure**: Confirm `Secure` flag is enforced in production (`config.force_ssl = true`).
  - [ ] **SameSite**: Confirm `SameSite=Lax` or `SameSite=Strict` is set to mitigate Cross-Site Request Forgery.
- [ ] **Session Lifecycle & Invalidation**:
  - [ ] **Logout Invalidation**: Confirm `DELETE /users/sign_out` (`config.sign_out_via = :delete`) destroys the server-side session and clears client cookies.
  - [ ] **Session Fixation Prevention**: Confirm Devise regenerates the session ID upon user login (`bypass_sign_in`).

---

## 4. Error Handling & Information Disclosure Checklist

- [ ] **Stack Trace & Environment Dumps**: Inspect production error handlers to ensure failed authentication attempts do not render unhandled exception traces or database connection string details.
- [ ] **Database Exception Interception**: Confirm raw database driver exceptions (e.g. `PG::UniqueViolation`, `PG::ConnectionBad`) are caught before reaching API/JSON responses.
- [ ] **Sensitive Attribute Filtering**: Verify user profile API endpoints and error payloads do not serialize `encrypted_password`, `reset_password_token`, or `confirmation_token`.
