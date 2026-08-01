# Security & Architecture Knowledge Base: Bridge Troll (Ruby on Rails)

High-density reference context optimized for low token burn during LLM analysis and RAG retrieval.

---

## 1. Stack & Dependencies
- **Framework**: Ruby on Rails 8.0, Ruby 3.x
- **Database**: PostgreSQL (`pg` gem), ActiveRecord ORM
- **Authentication**: `Devise`, OmniAuth (`github`, `facebook`, `google_oauth2`, `twitter`, `meetup`), `omniauth-rails_csrf_protection`
- **Authorization**: `Pundit` (Policy-based RBAC/ABAC)
- **Sanitization & Security**: `sanitize` gem, `rack-cors`, `rack-canonical-host`
- **Frontend/Views**: ERB templates, Bootstrap, jQuery, Handlebars, SimpleForm

---

## 2. Core Domain & Functionality
- **Events**: Workshop creation, sections, attendees, check-ins, RSVPs, surveys, email broadcasts.
- **Users & Roles**: Admins, Chapter Leaders, Region Leaders, Event Organizers, Volunteers, Students.
- **Structure**: Chapters, Regions, Locations, Organizations.

---

## 3. Threat Model & Trust Boundaries
- **Assets**: User PII, OAuth tokens, RSVP records, Chapter/Region admin privileges, Broadcast email engine.
- **Trust Boundaries**:
  1. Unauthenticated Client <-> Rails Controllers (`CSRF` & `Session Cookie`)
  2. Controller <-> Pundit Authorization Layer
  3. Rails App <-> PostgreSQL Database
  4. App <-> External OAuth Providers (GitHub, Google, Facebook, Twitter, Meetup)
- **Threat Actors**: External anonymous users, Regular registered users (horizontal IDOR), Organizers/Leaders (vertical escalation).

---

## 4. Rails Vulnerability Vectors & OWASP Mapping
- **A01: Broken Access Control**: Missing `authorize @resource` in Pundit policies; BOLA/IDOR in RSVP/Event params; Mass Assignment parameter leaks (`Strong Parameters`).
- **A02: Cryptographic Failures**: Insecure OAuth callback token storage; hardcoded secrets in `credentials.yml` or `.env`.
- **A03: Injection**:
  - **XSS**: Unsafe use of `raw`, `html_safe`, or misconfigured `sanitize()` in event descriptions or email views.
  - **SQLi**: String interpolation in `ActiveRecord` query fragments (`where("title LIKE '%#{params[:q]}%'")`).
- **A05: Security Misconfiguration**: Unrestricted CORS (`rack-cors`); exposed dev endpoints (`better_errors`, `binding_of_caller`).
- **A07: Identification & Auth**: OAuth CSRF flaws (missing/unvalidated state parameters); session fixation.
- **A08: Data Integrity**: Unsafe YAML/Marshal deserialization (`YAML.load` vs `YAML.safe_load`).

---

## 5. Key Security Controls
1. **Access Control**: Strict `Pundit` policies with `after_action :verify_authorized` and `after_action :verify_policy_scoped`.
2. **Parameters**: Mandatory `Strong Parameters` (`params.require().permit()`).
3. **XSS Defense**: Built-in ERB HTML escaping; explicit strict `sanitize` allowlists.
4. **CSRF**: `protect_from_forgery with: :exception` and `omniauth-rails_csrf_protection`.
5. **Static Analysis**: Automated `brakeman` & `rubocop-performance` scans.
