# Bridge Troll — Injection Security Audit Findings Report

We assessed commit `#40747c6510014958c9519d3708b5dc9325a0cc1c`

This report was generated using the **Injection Security Audit Skill** (`injection-audit`) to document verified input validation controls, SQL injection analysis, XSS defenses, and log injection safeguards in the Bridge Troll application (`c:/workspace/bridge_troll`).

---

## 1. Injection Security Architecture Summary

| Security Area | Implementation / Configuration | Audit Result | Status |
| :--- | :--- | :--- | :---: |
| **SQL Injection (SQLi)** | ActiveRecord ORM Parameter Binding (`?` / Hash) | Bound parameters enforced across queries | ✅ |
| **Raw SQL Fragments** | `UserSearcher` (`user_searcher.rb:14`) & `LeadersController` | SQL subqueries use parameter placeholders (`?`) | ✅ |
| **Stored & Reflected XSS** | ERB Auto-Escaping + Rails HTML Escaper | No raw `html_safe` / `raw()` on user inputs | ✅ |
| **Log Injection (CWE-117)** | ActiveSupport Tagged Logger + Parameter Filter | Passwords/secrets masked from log streams | ✅ |
| **Command Injection** | No system shell calls (`system`, `` ` ``) on user input | Zero shell command execution sinks found | ✅ |

---

## 2. Confirmed Injection Vulnerabilities & Observations

### 🟢 Verified Control 1: Parameterized Raw SQL in User Search (`UserSearcher`)
* **File Location**: `app/services/user_searcher.rb:11-16`
* **Code Reference**:
  ```ruby
  args = 'lower(first_name)', "' '", 'lower(last_name)'
  search_field = Rails.application.using_postgres? ? "CONCAT(#{args * ', '})" : args * ' || '

  @relation
    .select(:id, :first_name, :last_name)
    .where("#{search_field} like ?", "%#{@query.downcase}%")
  ```
* **Analysis**: While `search_field` dynamically constructs SQL string functions (`CONCAT(...)` vs `||`), the values inside `args` are hardcoded field names. The user-supplied `@query` parameter is passed safely via ActiveRecord's bound parameter placeholder (`?`), preventing SQL injection.

---

### 🟢 Verified Control 2: Parameterized Subquery in Chapter Leadership Search
* **File Location**: `app/controllers/chapters/leaders_controller.rb:36-40`
* **Code Reference**:
  ```ruby
  users_not_assigned = User.where(<<-SQL.squish, @chapter.id)
    users.id NOT IN (
      SELECT user_id FROM chapter_leaderships WHERE chapter_id = ?
    )
  SQL
  ```
* **Analysis**: The SQL subquery fragment uses a parameter placeholder `?` bound directly to `@chapter.id`, ensuring `@chapter.id` cannot be manipulated to inject malicious SQL syntax.

---

### 🟢 Verified Control 3: Automatic ERB Output Encoding & Input Validation
* **File Location**: `app/views/` & `app/controllers/application_controller.rb`
* **Analysis**: All ERB templates use standard `<%= ... %>` tags with Rails automatic contextual HTML output encoding. No unescaped `html_safe` or `raw()` calls were found acting on user-supplied parameters. Input parameters are sanitized via Devise strong parameters (`devise_parameter_sanitizer`) and Pundit `permitted_attributes`.

---

## 3. Summary & Recommendations

1. **Maintain Strict ORM Parameterization**: Continue enforcing array/hash bound parameter syntax for all new ActiveRecord queries and raw SQL fragments.
2. **Context-Aware Output Encoding**: Ensure any future rich-text fields or custom view helpers utilize the `Sanitize` gem before rendering HTML.
