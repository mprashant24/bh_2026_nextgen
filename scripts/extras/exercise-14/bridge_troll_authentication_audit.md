# Bridge Troll — Authentication & Session Security Audit Report

We assessed commit `#40747c6510014958c9519d3708b5dc9325a0cc1c`

This audit was performed strictly using the **Authentication Audit Skill** (`authentication-audit`). All findings and checklist evaluations are strictly scoped to **Authentication Flows, User Identification, Credential Verification, Error Handling, and Session Management Security**.

---

## 1. Authentication Architecture & Checklist Summary

| Security Area | Implementation / Configuration | Audit Result | Status |
| :--- | :--- | :--- | :---: |
| **User Identification** | Primary ID: `Email` + OAuth UIDs | Email required with `:confirmable` and Devise `:validatable` | ✅ |
| **Devise Secret Key** | `config.secret_key = ENV['DEVISE_SECRET_KEY'] \|\| ('x' * 30)` | **Hardcoded Fallback Secret Key** | ⚠️ **CRITICAL** |
| **Session Idle Timeout** | `config.timeout_in = 2.weeks` | **Excessive 2-Week Session Idle Timeout** | ⚠️ **HIGH** |
| **Password Hashing** | `Bcrypt` via Devise (`cost: 10` in prod, `1` in test) | Secure Adaptive Hashing Enforced | ✅ |
| **Brute-Force Protection** | Unrestricted POST `/users/sign_in` | **NO Rate Limiting or Lockout Middleware** | ⚠️ **HIGH** |
| **User Enumeration in Error Responses** | Devise Auth Failure + Account Existing Alerts | **Verbose Account Email Exposure in OAuth Error Alert** | ⚠️ **HIGH** |
| **Account Reconfirmation** | `config.reconfirmable = false` | **Email Changes Do Not Require Confirmation** | ⚠️ **MEDIUM** |
| **Confirmation Link Expiry** | `config.confirm_within = nil` | **Account Confirmation Tokens Never Expire** | ⚠️ **LOW** |
| **Registration & Roles** | `DeviseOverrides::RegistrationsController` | Strong parameters restricted; Password bypass checked | ✅ |
| **OAuth / SSO Integration** | Devise OmniAuth (`github`, `google_oauth2`, `facebook`, `twitter`, `meetup`) | Provider linking without re-authentication verification | ⚠️ **MEDIUM** |
| **Session Cookie Security** | Rails Cookie Session Store (`_bridge_troll_session`) | `HttpOnly` enabled; `Secure` flag depends on SSL config | ✅ |
| **Session Invalidation** | Devise Session Destruction (`delete /users/sign_out`) | Session token destroyed on logout | ✅ |

---

## 2. Confirmed Authentication Vulnerabilities

### 🔴 Finding 1: Hardcoded Fallback Devise Secret Key Allows Token Forgery
* **Vulnerability Type**: Hardcoded Cryptographic Secret Key / Token Forgery (CWE-321 / CWE-798)
* **Severity Rating**: **CRITICAL**
* **File Location**: `config/initializers/devise.rb:8`
* **Vulnerable Code**:
  ```ruby
  Devise.setup do |config|
    config.secret_key = ENV['DEVISE_SECRET_KEY'] || ('x' * 30)
  ```
* **Flaw Analysis**: If `ENV['DEVISE_SECRET_KEY']` is not explicitly set in a deployment environment, Devise falls back to a static string of 30 `'x'` characters (`"xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"`). Because Devise uses `secret_key` to sign and verify confirmation tokens, password reset tokens, and unlock tokens, an attacker knowing the fallback secret can construct and sign arbitrary password reset tokens offline to compromise any user account on the system.
* **Exploit Scenario**:
  1. An environment is deployed without setting `ENV['DEVISE_SECRET_KEY']`.
  2. An attacker knows the open-source code fallback (`"x" * 30`).
  3. The attacker generates a signed password reset payload targeting an admin user's ID/email and submits it to `/users/password`.
  4. The server validates the token using the hardcoded key and resets the admin password.
* **Remediation**:
  1. Require `ENV.fetch('DEVISE_SECRET_KEY')` without fallback in production, or raise an exception on boot if the environment variable is absent:
     ```ruby
     config.secret_key = ENV['DEVISE_SECRET_KEY'] || (Rails.env.production? ? raise("Missing DEVISE_SECRET_KEY") : ('x' * 30))
     ```

---

### 🔴 Finding 2: Excessive 2-Week Session Idle Timeout
* **Vulnerability Type**: Insufficient Session Expiration / Long Idle Timeout (CWE-613)
* **Severity Rating**: **HIGH**
* **File Location**: `config/initializers/devise.rb:147`
* **Vulnerable Code**:
  ```ruby
  # config/initializers/devise.rb
  config.timeout_in = 2.weeks # Lillie wanted 'forever' but we compromised at '2 weeks'
  ```
* **Flaw Analysis**: Standard security practices recommend an idle session timeout between 15 and 30 minutes for web applications handling PII/PHI. Setting `timeout_in = 2.weeks` keeps user sessions active for 14 full days without requiring activity or re-authentication.
* **Exploit Scenario**:
  1. A user logs into Bridge Troll on a shared or public computer (e.g. at a workshop venue) and closes the browser tab without logging out.
  2. Another user accesses the same workstation days later, reopens the site, and remains fully authenticated as the previous user.
* **Remediation**:
  1. Reduce the session idle timeout to 30 minutes to 1 hour:
     ```ruby
     config.timeout_in = 30.minutes
     ```

---

### 🔴 Finding 3: Unrestricted Credential Stuffing & Brute-Force Vulnerability on Login
* **Vulnerability Type**: Missing Rate-Limiting / Brute-Force Lockout (CWE-307)
* **Severity Rating**: **HIGH**
* **File Location**: `config/initializers/devise.rb` & `config/routes.rb`
* **Vulnerable Configuration**:
  ```ruby
  # config/initializers/devise.rb
  # Devise :lockable module is NOT included in User model
  class User < ApplicationRecord
    devise :database_authenticatable, :registerable, :omniauthable,
           :recoverable, :rememberable, :trackable, :validatable,
           :confirmable, :timeoutable
  ```
* **Flaw Analysis**: The `User` model omits Devise's `:lockable` module, and no web application firewall or Rack rate-limiting middleware (such as `rack-attack`) is configured on `POST /users/sign_in`.
* **Exploit Scenario**:
  1. An attacker executes an automated dictionary or credential-stuffing attack against `POST /users/sign_in`.
  2. Because there are no rate limits or account lockouts, the attacker can submit millions of password attempts without triggering an IP ban or account lockout.
* **Remediation**:
  1. Add `:lockable` to the Devise module list in `app/models/user.rb` and configure `config.maximum_attempts = 5` and `config.unlock_strategy = :time` in `config/initializers/devise.rb`.
  2. Install and configure `rack-attack` gem to rate-limit `POST /users/sign_in` by IP address.

---

### 🔴 Finding 4: User Account Enumeration via OAuth Error Messages
* **Vulnerability Type**: Information Disclosure / User Enumeration via Error Messages (CWE-209 / CWE-204)
* **Severity Rating**: **HIGH**
* **File Location**: `app/controllers/devise_overrides/omniauth_callbacks_controller.rb:13-17`
* **Vulnerable Code**:
  ```ruby
  module DeviseOverrides
    class OmniauthCallbacksController < Devise::OmniauthCallbacksController
      def all
        omniauth = request.env['omniauth.auth']
        provider_name = OmniauthProviders.provider_data_for(omniauth['provider'])[:name]
        if current_user
          auth_args = { provider: omniauth['provider'], uid: omniauth['uid'].to_s }
          auth = current_user.authentications.create(auth_args)

          return (
            if auth.persisted?
              redirect_to edit_user_registration_path, notice: "#{provider_name} authentication added."
            else
              existing_auth = Authentication.find_by(auth_args)
              redirect_to edit_user_registration_path,
                          alert: "That #{provider_name} authentication is already in use by #{existing_auth.user.email}!."
            end
          )
  ```
* **Flaw Analysis**: When an authenticated user attempts to link an OAuth provider account (e.g. GitHub or Google) that is already linked to another user, the error alert explicitly discloses the victim user's email address: `"That #{provider_name} authentication is already in use by #{existing_auth.user.email}!"`.
* **Remediation**:
  1. Remove `existing_auth.user.email` from the error message. Use a generic alert: `"That #{provider_name} account is already linked to another Bridge Troll profile."`

---

### 🟡 Finding 5: Email Changes Take Effect Immediately Without Re-Confirmation
* **Vulnerability Type**: Missing Email Re-Confirmation Guard (CWE-287)
* **Severity Rating**: **MEDIUM**
* **File Location**: `config/initializers/devise.rb:122`
* **Vulnerable Code**:
  ```ruby
  # config/initializers/devise.rb
  config.reconfirmable = false
  ```
* **Flaw Analysis**: Setting `config.reconfirmable = false` means that when a user updates their email address in their profile, the new email takes effect immediately without sending a verification link to the new address. If an attacker gains temporary session access or XSS execution, they can instantly change the account email to an attacker-controlled address and execute a password reset.
* **Remediation**:
  1. Set `config.reconfirmable = true` in `config/initializers/devise.rb` to require confirming email updates.

---

## 3. Verified Secure Authentication Controls

* **Bcrypt Password Hashing** (`app/models/user.rb:5`): Verified that Devise uses `database_authenticatable` with Bcrypt hashing and salt, ensuring passwords are never stored in plaintext.
* **Mass Assignment Protection during Registration** (`app/controllers/devise_overrides/registrations_controller.rb:39-41`): Verified that registration uses `permitted_attributes(User)` via Pundit, preventing attackers from injecting administrative role attributes during signup.
* **Session Destruction on Logout** (`config/routes.rb:5-8`): Verified that logging out via Devise destroys the server-side session cookie and revokes authentication.
