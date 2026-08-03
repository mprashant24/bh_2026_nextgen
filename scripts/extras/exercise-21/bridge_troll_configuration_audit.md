# Bridge Troll — Configuration Security Audit Findings Report

We assessed commit `#40747c6510014958c9519d3708b5dc9325a0cc1c`

This report was generated using the **Configuration Security Audit Skill** (`configuration-audit`) to document verified framework security settings, HTTP header policies, and dependency management controls in the Bridge Troll application (`c:/workspace/bridge_troll`).

---

## 1. Configuration Architecture Summary

| Security Area | Implementation / Configuration | Audit Result | Status |
| :--- | :--- | :--- | :---: |
| **CSRF Protection** | `protect_from_forgery` (ApplicationController) | Global Verification Active | ✅ |
| **CORS Policy** | `config/initializers/cors.rb` | No Permissive Wildcards (`*`) | ✅ |
| **Content Security Policy** | `content_security_policy.rb` | **CSP is Completely Disabled** | ⚠️ **HIGH** |
| **Transport Headers** | `config.force_ssl = true` | HSTS Preload Enabled (1 year) | ✅ |
| **Diagnostic Modes** | `consider_all_requests_local = false` | Stack Traces Suppressed in Prod | ✅ |

---

## 2. Confirmed Configuration Vulnerabilities

### 🔴 Finding 1: Missing Content Security Policy (CSP) Frame and Script Protections
* **Vulnerability Type**: Missing Security Header / Disabled CSP (CWE-693 / CWE-1021)
* **Severity Rating**: **HIGH**
* **File Location**: `config/initializers/content_security_policy.rb:9-25`
* **Vulnerable Code**:
  ```ruby
  # Rails.application.configure do
  #   config.content_security_policy do |policy|
  #     policy.default_src :self, :https
  # ...
  #     policy.script_src  :self, :https
  #   end
  # end
  ```
* **Flaw Analysis**: The entire `content_security_policy` configuration block is commented out. Without a strict CSP, the application relies solely on Rails ERB auto-escaping to prevent Cross-Site Scripting (XSS). If a single unescaped output vulnerability exists, an attacker can load arbitrary malicious JavaScript (`script-src`) or frame the site (`object-src` / `frame-ancestors`) to execute Clickjacking attacks.
* **Remediation**:
  1. Uncomment and enforce a strict CSP in `config/initializers/content_security_policy.rb`:
     ```ruby
     Rails.application.configure do
       config.content_security_policy do |policy|
         policy.default_src :self, :https
         policy.font_src    :self, :https, :data
         policy.img_src     :self, :https, :data
         policy.object_src  :none
         policy.script_src  :self, :https
         policy.style_src   :self, :https, :unsafe_inline
         policy.frame_ancestors :none
       end
     end
     ```

---

## 3. Verified Secure Configuration Controls

* **Global CSRF Protection & Origin Check** (`app/controllers/application_controller.rb:4`): Verified that `protect_from_forgery` is globally enabled across all state-changing endpoints, bolstered by `forgery_protection_origin_check = true` in the initializers to block cross-origin requests masking as same-origin.
* **Strict Transport Security (HSTS)** (`config/environments/production.rb:48-49`): Verified that `config.force_ssl = true` enforces encrypted TLS transport with `hsts: { preload: true, subdomains: true, expires: 1.year }`.
* **Production Error Handling** (`config/environments/production.rb:18`): Verified `config.consider_all_requests_local = false` is enforced, ensuring database traces and exceptions are not leaked to external clients.
