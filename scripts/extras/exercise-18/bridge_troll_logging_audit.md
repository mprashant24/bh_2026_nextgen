# Bridge Troll — Logging & Security Audit Findings Report

We assessed commit `#40747c6510014958c9519d3708b5dc9325a0cc1c`

This report was generated using the **Logging & Auditing Security Skill** (`logging-auditing-audit`) to document verified logging configurations, audit trail deficiencies, and sensitive data risks in the Bridge Troll application (`c:/workspace/bridge_troll`).

---

## 1. Logging Architecture Summary

| Security Area | Implementation / Configuration | Audit Result | Status |
| :--- | :--- | :--- | :---: |
| **Logging Library** | `ActiveSupport::TaggedLogging` + Ruby `Logger` | Standard Rails Tagged Logger initialized | ✅ |
| **Log Level** | `config.log_level = :debug` in `production.rb:58` | Verbose `:debug` level enabled in production | ⚠️ **HIGH** |
| **Parameter Filtering** | `filter_parameter_logging.rb` (%i[passw email secret token]) | ActiveSupport parameter masking active | ✅ |
| **Sensitive Data Leakage** | Controllers inspected (`app/controllers/**/*.rb`) | No explicit `Rails.logger` dumps of passwords/PII found | ✅ |
| **Authentication Audit Trail** | Devise Auth Controllers (`sessions`, `omniauth_callbacks`) | **No structured audit logging for failed logins/reset events** | ⚠️ **HIGH** |
| **Administrative Audit Trail** | `Chapters::LeadersController`, `Events::EmailsController` | **No audit logging for leader appointments or email broadcasts** | ⚠️ **MEDIUM** |
| **Log Storage & Rotation** | STDOUT Logger (`Logger.new($stdout)`) | Dependent on host environment (Docker/Heroku) | ✅ |

---

## 2. Confirmed Logging & Auditing Vulnerabilities

### 🔴 Finding 1: Verbose `:debug` Log Level Enabled in Production Environment
* **Vulnerability Type**: Excessive Information Disclosure in Logs (CWE-532)
* **Severity Rating**: **HIGH**
* **File Location**: `config/environments/production.rb:58`
* **Vulnerable Configuration**:
  ```ruby
  # config/environments/production.rb
  # Use the lowest log level to ensure availability of diagnostic information
  # when problems arise.
  config.log_level = :debug
  ```
* **Flaw Analysis**: In Rails, setting `config.log_level = :debug` in `production.rb` causes the application to record detailed internal application state, SQL query parameters, session tokens, and request processing traces to production log files. If log files or log aggregation tools (Splunk, Datadog) are accessed or compromised, sensitive query parameters and internal database schemas are exposed.
* **Exploit Scenario**:
  1. An attacker gains read access to server log files or log management dashboards.
  2. Because `:debug` logging is enabled, raw database queries and internal application variable states are recorded verbatim in log lines.
  3. The attacker extracts sensitive parameters and internal system architecture details from the log stream.
* **Remediation**:
  1. Change the production log level to `:info` or `:warn` in `config/environments/production.rb`:
     ```ruby
     config.log_level = ENV.fetch('RAILS_LOG_LEVEL', 'info').to_sym
     ```

---

### 🔴 Finding 2: Missing Security Audit Trail for Authentication & Failed Login Events
* **Vulnerability Type**: Insufficient Security Audit Logging (CWE-778)
* **Severity Rating**: **HIGH**
* **File Location**: `app/controllers/devise_overrides/omniauth_callbacks_controller.rb` & Devise Session Routes
* **Vulnerable Code**:
  ```ruby
  # app/controllers/devise_overrides/omniauth_callbacks_controller.rb
  def all
    ...
    if user.persisted?
      flash[:notice] = "#{provider_name} login successful."
      sign_in_and_redirect user
    else
      session['devise.omniauth'] = omniauth.except('extra')
      redirect_to new_user_registration_path
    end
  end
  ```
* **Flaw Analysis**: Neither Devise login attempts nor OmniAuth authentication callbacks produce structured security audit logs when authentication fails or succeeds. There are no log entries recording client IP addresses, target user IDs, timestamps, or failure reasons.
* **Exploit Scenario**:
  1. A malicious actor executes a credential-stuffing or brute-force campaign against Bridge Troll accounts.
  2. Because failed login attempts leave no structured security audit records, security operations teams (SOC) have no visibility into the ongoing attack and cannot identify compromised accounts post-incident.
* **Remediation**:
  1. Instrument Warden/Devise authentication callbacks in `config/initializers/devise.rb` to generate structured audit logs for login events:
     ```ruby
     Warden::Manager.after_authentication do |user, auth, opts|
       Rails.logger.info("[AUDIT_AUTH_SUCCESS] user_id=#{user.id} ip=#{auth.request.remote_ip}")
     end

     Warden::Manager.before_failure do |env, opts|
       request = Rack::Request.new(env)
       Rails.logger.warn("[AUDIT_AUTH_FAILURE] ip=#{request.remote_ip} path=#{request.path}")
     end
     ```

---

### 🟡 Finding 3: Missing Audit Logs for Privileged Administrative & Leadership Actions
* **Vulnerability Type**: Insufficient Auditing of Administrative Actions (CWE-778)
* **Severity Rating**: **MEDIUM**
* **File Location**: `app/controllers/chapters/leaders_controller.rb:12-23` & `app/controllers/events/emails_controller.rb:17-30`
* **Vulnerable Code**:
  ```ruby
  # app/controllers/chapters/leaders_controller.rb
  def create
    authorize @chapter, :modify_leadership?
    leader = ChapterLeadership.new(chapter: @chapter, user_id: leader_id_param)
    if leader.save
      redirect_to chapter_leaders_path(@chapter), notice: 'Booyah!'
  ```
* **Flaw Analysis**: Granting chapter leadership (`Chapters::LeadersController#create`), deleting leadership roles (`#destroy`), and sending mass email broadcasts (`Events::EmailsController#create`) perform significant state changes but do not write security audit events.
* **Remediation**:
  1. Add explicit audit logging for administrative role changes:
     ```ruby
     Rails.logger.info("[AUDIT_ADMIN_ACTION] action=add_chapter_leader admin_id=#{current_user.id} target_user_id=#{leader_id_param} chapter_id=#{@chapter.id}")
     ```

---

## 3. Verified Secure Logging & Auditing Controls

* **Parameter Filtering Configuration** (`config/initializers/filter_parameter_logging.rb:7-9`): Verified that ActiveSupport parameter filtering masks sensitive keys (`passw`, `email`, `secret`, `token`, `crypt`, `salt`, `otp`, `ssn`) from Rails log outputs.
* **HTTPS SSL Transport Enforcement** (`config/environments/production.rb:48`): Verified `config.force_ssl = true` ensures HTTP headers and cookies are transmitted over encrypted TLS connections.
