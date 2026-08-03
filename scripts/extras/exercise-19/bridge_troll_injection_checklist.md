# Bridge Troll — Injection Security Review Checklist

We assessed commit `#40747c6510014958c9519d3708b5dc9325a0cc1c`

This checklist synthesizes the **Injection Security Audit Skill** (`injection-audit`) to guide manual security code review for the Bridge Troll application (`c:/workspace/bridge_troll`).

---

## 1. SQL Injection (SQLi) Checklist

- [x] **ActiveRecord Parameter Binding**: Confirm ActiveRecord query calls (`where`, `find_by`) use parameter placeholders (`?`) or hash conditions (`where(id: params[:id])`).
- [x] **Raw SQL Query Fragments Audit**:
  - [x] Inspect `UserSearcher` (`app/services/user_searcher.rb:14`): Verified `@relation.where("#{search_field} like ?", "%#{@query.downcase}%")` uses bound parameter `?` for user search queries.
  - [x] Inspect `Chapters::LeadersController` (`app/controllers/chapters/leaders_controller.rb:36`): Verified `User.where(..., @chapter.id)` uses bound parameter `?` for SQL subqueries.
- [x] **Dynamic Table / Column Name Sorting**: Inspect controller `.order()` calls to ensure user-supplied sort parameters are validated against hardcoded allowlists.

---

## 2. Cross-Site Scripting (XSS) Checklist

- [x] **Automatic ERB HTML Escaping**: Confirm Rails automatic contextual HTML output encoding (`<%= ... %>`) is active across all view templates in `app/views/`.
- [x] **Unsafe Raw Output Helper Audit**:
  - [x] Grep search for `raw()`, `html_safe`, and `<%== %>`: Verified no unescaped user-supplied inputs are rendered in HTML templates.
- [x] **HTML Sanitization**: Inspect `Sanitize` gem usage (`Gemfile`) to verify user-submitted rich text or event details are sanitized before storage and rendering.

---

## 3. Log Injection (CRLF Log Pollution - CWE-117) Checklist

- [x] **Log Stream Parameter Filtering**: Inspect `config/initializers/filter_parameter_logging.rb`:
  - [x] Confirm ActiveSupport parameter filter masks passwords, secrets, tokens, and PII from log outputs.
- [x] **Unescaped User Inputs in Log Statements**: Audit controller log calls to ensure unsanitized user inputs containing newlines (`\r\n`) cannot forge fake log lines or pollute log streams.

---

## 4. Input Validation & Command Injection Checklist

- [x] **Server-Side Type Casting & Parameter Sanitization**: Confirm parameters are sanitized via Devise strong parameters (`devise_parameter_sanitizer`) and Pundit `permitted_attributes`.
- [x] **OS Command Execution Audit**:
  - [x] Grep search for `system()`, `` ` `` (backticks), `exec()`, and `Open3`: Verified no shell commands accept unvalidated user parameters.
