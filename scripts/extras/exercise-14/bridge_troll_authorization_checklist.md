# Bridge Troll — Authorization Security Code Review Checklist

We assessed commit `#40747c6510014958c9519d3708b5dc9325a0cc1c`

This checklist synthesizes the **Route Security Inventory** (`bridge_troll_route_inventory.md`) and **Authorization Matrix** (`bridge_troll_authorization_matrix.md`) to guide manual security code review for the Bridge Troll application.

---

## 1. High-Priority Route Authorization Review Checklist

### 🔴 Priority #1: Chapter Leadership Appointment
* **Route**: `POST /chapters/:chapter_id/leaders` (`chapters/leaders#create`)
* **Risk**: Unchecked Privilege Escalation / BOLA
* **Checklist Items**:
  - [ ] Verify `ChapterPolicy#modify_leadership?` or `update?` is invoked via `authorize @chapter` before creating leader record.
  - [ ] Confirm a Chapter Leader for Chapter A cannot appoint leaders in Chapter B by manipulating `:chapter_id` in the URL path.
  - [ ] Ensure non-leader authenticated users receive `401 Unauthorized` / `403 Forbidden` when attempting POST requests.

### 🔴 Priority #2: Mass Email Broadcast System
* **Route**: `POST /events/:event_id/emails` (`events/emails#create`)
* **Risk**: Email Spam Abuse / Unauthenticated Phishing Broadcast / BOLA
* **Checklist Items**:
  - [ ] Inspect `Events::EmailsController` to confirm `authorize @event` is executed before enqueuing mailer jobs.
  - [ ] Verify that only assigned event organizers, chapter leaders, or admins can send broadcast emails.
  - [ ] Check if email `subject` and `body` parameters are sanitized to prevent mailer header injection or HTML phishing.

### 🔴 Priority #3: OAuth Provider Authentication Callback
* **Route**: `POST/GET /users/auth/:provider` (`devise_overrides/omniauth_callbacks#passthru`)
* **Risk**: OAuth CSRF / State Parameter Injection / Account Takeover
* **Checklist Items**:
  - [ ] Confirm `omniauth-rails_csrf_protection` middleware is active for all OAuth providers.
  - [ ] Verify that the `state` parameter is validated server-side during the callback.
  - [ ] Inspect user lookup logic to ensure unverified OAuth email claims cannot hijack existing passwords or admin accounts.

### 🔴 Priority #4: Admin Diagnostic Exception Handler
* **Route**: `GET /admin_dashboard/raise_exception` (`admin_pages#raise_exception`)
* **Risk**: Intentional Stack Trace / Diagnostic Data Exposure
* **Checklist Items**:
  - [ ] Confirm `authorize :admin_page` or `current_user.admin?` check is enforced prior to triggering exceptions.
  - [ ] Ensure verbose stack traces and environment variable dumps are disabled in production error handlers.

### 🟠 Priority #5: Event Publishing & State Changes
* **Route**: `POST /events/unpublished_events/:id/publish` (`events/unpublished_events#publish`)
* **Risk**: Unauthorized Event Publishing / Workflow Bypass
* **Checklist Items**:
  - [ ] Inspect `EventPolicy#publish?` to confirm regular organizers cannot self-publish events without `publisher`, `admin`, or `chapter_leader` permissions.
  - [ ] Verify `policy_scope(Event)` is applied when querying unpublished events to prevent unauthorized draft enumeration.

### 🟠 Priority #6: Attendee RSVP & Sensitive PII Submissions
* **Route**: `POST /events/:event_id/rsvps` (`rsvps#create`)
* **Risk**: BOLA / IDOR / Sensitive PII Exposure (Dietary & Childcare Needs)
* **Checklist Items**:
  - [ ] Confirm `RsvpPolicy` prevents users from creating or modifying RSVPs on behalf of other user IDs.
  - [ ] Verify `permitted_attributes` strictly limits assignable fields, preventing students from self-promoting to organizer or checked-in status.

---

## 2. Pundit Authorization Policy Enforcement Checklist

### Global Controller Guardrails
- [ ] **Verify Authorized Callback**: Confirm `after_action :verify_authorized` remains enabled in `ApplicationController`.
- [ ] **Policy Scoping**: Confirm all index/list routes (`EventsController#index`, `OrganizationsController#index`) use `policy_scope()` to prevent data leaks.
- [ ] **Skip Authorization Review**: Audit every occurrence of `skip_authorization` (e.g. `events#index`, `events#past_events`, `static_pages#about`) to ensure no privileged actions bypass checks.
- [ ] **Rescue Handlers**: Confirm `rescue_from Pundit::NotAuthorizedError` safely redirects users without leaking sensitive internal state or stack traces.

### Model Policy Specific Checks
- [ ] **`EventPolicy`**:
  - [ ] Verify `update?` blocks modifications to historical events (`record.historical?`).
  - [ ] Verify `checkin?` restricts check-in access strictly to assigned event checkiners, chapter leaders, and admins.
- [ ] **`ChapterPolicy`**:
  - [ ] Verify `destroy?` is restricted exclusively to `user.admin?`.
- [ ] **`LocationPolicy`**:
  - [ ] Verify `archive?` prevents archiving locations with active upcoming events.
  - [ ] Verify `edit_additional_details?` restricts contact info/notes edits to Region Leaders or Admins.
- [ ] **`UserPolicy` & `ProfilePolicy`**:
  - [ ] Verify users can only edit their own profile attributes unless operating as `admin`.

---

## 3. Mass Assignment & Strong Parameters Checklist

- [ ] **Devise Parameter Sanitizer**: Inspect `configure_permitted_parameters` in `ApplicationController` to ensure `region_ids` and custom parameters cannot be manipulated for privilege escalation.
- [ ] **Pundit `permitted_attributes`**: Confirm controllers use `permit(policy(record).permitted_attributes)` rather than hardcoded parameter lists.
- [ ] **Role Flag Protection**: Verify boolean role flags (`admin`, `publisher`) are excluded from general user update forms and permitted parameter lists.

---

## 4. Session & CSRF Security Checklist

- [ ] **OmniAuth CSRF**: Confirm `omniauth-rails_csrf_protection` gem is present and active across all OAuth authentication paths.
- [ ] **Forgery Protection**: Verify `protect_from_forgery with: :exception` is enabled in `ApplicationController`.
- [ ] **Session Invalidation**: Confirm logging out via `devise/sessions#destroy` completely destroys the server-side session and clears authentication cookies.
