# Security Assessment & Route Inventory: Bridge Troll (`c:/workspace/bridge_troll`)

We assessed commit `#40747c6510014958c9519d3708b5dc9325a0cc1c`

---

## 1. Behavior & Business Purpose
* **What does it do? (business purpose)**: Bridge Troll is an event management and workshop coordination application developed for RailsBridge. It manages workshop creation, volunteer and student RSVPs, event check-ins, section/group arrangements, waitlists, attendee surveys, and email broadcasts.
* **Who does it do this for?**: 
  - **Internal**: Event Organizers, Chapter Leaders, Region Leaders, Volunteers, Students, and Site Administrators.
  - **External**: Public workshop participants, Meetup users, and aid/educational workshop partners.
* **What kind of information will it hold?**:
  - **PII**: Full names, emails, dietary restrictions, emergency contact details, locations.
  - **Auth Data**: Devise credentials, encrypted passwords, OAuth tokens (GitHub, Google, Facebook, Twitter, Meetup).
  - **Event Data**: Workshop details, attendee surveys, organizer notes, RSVP statuses, waitlists.
* **What aspects concern clients/staff the most?**:
  - Preventing unauthorized access to attendee contact details and dietary PII.
  - Ensuring workshop organizers cannot perform unauthorized administrative modifications to chapters/regions.
  - Protecting email broadcast systems from unauthorized spam or phishing abuse.

---

## 2. Tech Stack
* **Framework & Language**: Ruby on Rails 8.0.3, Ruby 3.x
* **Datastore**: PostgreSQL (`pg` gem)
* **Authentication**: `Devise` (Database authentication & password resets) + OmniAuth (`github`, `facebook`, `google_oauth2`, `twitter`, `meetup`) + `omniauth-rails_csrf_protection`
* **Authorization**: `Pundit` (Policy-based RBAC/ABAC with `ApplicationPolicy` and `after_action :verify_authorized`)
* **3rd Party Libraries & Middleware**: `Puma`, `Rack::Cors`, `Rack::CanonicalHost`, `Rack::MiniProfiler`, `Sanitize`, `SimpleForm`, `Sprockets`

---

## 3. Brainstorming & Risk Profile
* **Insecure Direct Object Reference (IDOR/BOLA)**: Event controllers fetching RSVPs, check-ins, or surveys by primary key without verifying policy ownership via Pundit scope (`policy_scope`).
* **Mass Assignment Vulnerabilities**: Bypassing permitted parameters during user sign-up or profile update (`devise_parameter_sanitizer.permit(:sign_up)`).
* **Unchecked Privilege Escalation**: Chapter leadership or event organizer roles elevating themselves to global `admin` or `publisher` status.
* **XSS in Event Details**: Unescaped user-supplied HTML in event details or volunteer instructions rendered via ERB templates.

---

## 4. Route Security Inventory

### Summary
- **Total Routes Identified**: 43 Endpoints
- **External Internet-Exposed Routes**: 43
- **Internal Private Routes**: 0 (Monolithic Rails Web Application)
- **Protocols & API Styles**: `HTTPS` (REST / ERB / JSON / RSS / Atom)
- **1st Degree High-Relevance Routes**: 29
- **2nd Degree Connected Routes**: 14
- **Authentication Routes**: 6
- **Debug / Diagnostic Routes**: 3

---

### Route Inventory Table (Sorted by Priority Rank Number)

| Route / Security Attribute | Details / Value |
| :--- | :--- |
| **`#1: POST /chapters/:chapter_id/leaders`** | **Functional Summary**: Appoints a designated user as a Chapter Leader with administrative authority over regional workshops. |
| ├── **Handler** | `chapters/leaders#create` |
| ├── **Type & Exposure** | `ADMINISTRATIVE / EXTERNAL_INTERNET_EXPOSED (HTTPS)` |
| ├── **Authentication** | `AUTHENTICATED (Devise Session)` |
| ├── **Roles Required** | `Chapter Leader, Admin` |
| ├── **Secure Parameters** | `PATH: :chapter_id (HIGH_RISK_CONTROL), BODY: leader[user_id] (HIGH_RISK_CONTROL)` |
| ├── **Privileges Needed** | `SYSTEM_ADMIN` |
| ├── **Known Flaws / Risks** | `Unchecked Privilege Escalation, BOLA` |
| └── **Degree Connection** | `1st Degree (CRITICAL)` |
| **`#2: DELETE /chapters/:chapter_id/leaders/:id`** | **Functional Summary**: Removes a user from chapter leadership, revoking administrative rights over local workshops. |
| ├── **Handler** | `chapters/leaders#destroy` |
| ├── **Type & Exposure** | `ADMINISTRATIVE / EXTERNAL_INTERNET_EXPOSED (HTTPS)` |
| ├── **Authentication** | `AUTHENTICATED (Devise Session)` |
| ├── **Roles Required** | `Chapter Leader, Admin` |
| ├── **Secure Parameters** | `PATH: :chapter_id (HIGH_RISK_CONTROL), PATH: :id (HIGH_RISK_CONTROL)` |
| ├── **Known Flaws / Risks** | `BOLA / Unauthorized Leadership Removal` |
| └── **Degree Connection** | `1st Degree (CRITICAL)` |
| **`#3: POST /events/:event_id/emails`** | **Functional Summary**: Sends mass email announcements and instructions to registered event volunteers or students. |
| ├── **Handler** | `events/emails#create` |
| ├── **Type & Exposure** | `BUSINESS_LOGIC / EXTERNAL_INTERNET_EXPOSED (HTTPS)` |
| ├── **Authentication** | `AUTHENTICATED (Devise Session)` |
| ├── **Roles Required** | `Organizer, Chapter Leader` |
| ├── **Sensitive Data** | `PII (Attendee Emails)` |
| ├── **Secure Parameters** | `PATH: :event_id (HIGH_RISK_CONTROL), BODY: email[subject] (STANDARD_INPUT), email[body] (STANDARD_INPUT)` |
| ├── **Known Flaws / Risks** | `Email Spam Abuse, Phishing / Unchecked Broadcast` |
| └── **Degree Connection** | `1st Degree (CRITICAL)` |
| **`#4: POST /users/auth/:provider`** | **Functional Summary**: Handles third-party OAuth authentication callbacks and logs in or registers users via external providers. |
| ├── **Handler** | `devise_overrides/omniauth_callbacks#passthru` |
| ├── **Type & Exposure** | `AUTHENTICATION / EXTERNAL_INTERNET_EXPOSED (HTTPS)` |
| ├── **Authentication** | `UNAUTHENTICATED / PUBLIC` |
| ├── **Sensitive Data** | `CREDENTIALS, OAuth Tokens` |
| ├── **Secure Parameters** | `QUERY: code (CREDENTIALS_SECRET), state (HIGH_RISK_CONTROL)` |
| ├── **Known Flaws / Risks** | `OAuth CSRF, State Parameter Injection` |
| └── **Degree Connection** | `1st Degree (CRITICAL)` |
| **`#5: POST /users/sign_in`** | **Functional Summary**: Authenticates user email and password credentials, creating an active session cookie upon successful verification. |
| ├── **Handler** | `devise/sessions#create` |
| ├── **Type & Exposure** | `AUTHENTICATION / EXTERNAL_INTERNET_EXPOSED (HTTPS)` |
| ├── **Authentication** | `UNAUTHENTICATED / PUBLIC` |
| ├── **Sensitive Data** | `CREDENTIALS, PII` |
| ├── **Secure Parameters** | `BODY: user[email] (PII), user[password] (CREDENTIALS_SECRET)` |
| ├── **Known Flaws / Risks** | `User Enumeration, Brute Force Authentication` |
| └── **Degree Connection** | `1st Degree (CRITICAL)` |
| **`#6: POST /users`** | **Functional Summary**: Registers a new user account with profile information and location parameters. |
| ├── **Handler** | `devise_overrides/registrations#create` |
| ├── **Type & Exposure** | `AUTHENTICATION / EXTERNAL_INTERNET_EXPOSED (HTTPS)` |
| ├── **Authentication** | `UNAUTHENTICATED / PUBLIC` |
| ├── **Sensitive Data** | `CREDENTIALS, PII` |
| ├── **Secure Parameters** | `BODY: user[email] (PII), user[password] (CREDENTIALS_SECRET), user[region_ids] (HIGH_RISK_CONTROL)` |
| ├── **Known Flaws / Risks** | `Mass Assignment in Devise Parameter Sanitizer` |
| └── **Degree Connection** | `1st Degree (CRITICAL)` |
| **`#7: GET /admin_dashboard`** | **Functional Summary**: Provides central administrative management interface and system operational metrics for global platform admins. |
| ├── **Handler** | `admin_pages#admin_dashboard` |
| ├── **Type & Exposure** | `ADMINISTRATIVE / EXTERNAL_INTERNET_EXPOSED (HTTPS)` |
| ├── **Authentication** | `AUTHENTICATED (Devise Session)` |
| ├── **Roles Required** | `Admin` |
| ├── **Privileges Needed** | `SYSTEM_ADMIN` |
| └── **Degree Connection** | `1st Degree (CRITICAL)` |
| **`#8: GET /admin_dashboard/raise_exception`** | **Functional Summary**: Intentionally triggers a server exception to test error tracking integration and diagnostic handlers. |
| ├── **Handler** | `admin_pages#raise_exception` |
| ├── **Type & Exposure** | `DEBUG_DIAGNOSTIC / EXTERNAL_INTERNET_EXPOSED (HTTPS)` |
| ├── **Authentication** | `AUTHENTICATED (Devise Session)` |
| ├── **Roles Required** | `Admin` |
| ├── **Privileges Needed** | `SYSTEM_ADMIN` |
| ├── **Known Flaws / Risks** | `Intentional Diagnostic Exception Leakage` |
| └── **Degree Connection** | `1st Degree (CRITICAL)` |
| **`#9: GET /admin_dashboard/send_test_email`** | **Functional Summary**: Triggers a diagnostic test email to confirm SMTP/mail delivery pipeline operation. |
| ├── **Handler** | `admin_pages#send_test_email` |
| ├── **Type & Exposure** | `DEBUG_DIAGNOSTIC / EXTERNAL_INTERNET_EXPOSED (HTTPS)` |
| ├── **Authentication** | `AUTHENTICATED (Devise Session)` |
| ├── **Roles Required** | `Admin` |
| ├── **Privileges Needed** | `SYSTEM_ADMIN` |
| └── **Degree Connection** | `1st Degree (CRITICAL)` |
| **`#10: POST /events/organizer_tools/send_announcement_email`** | **Functional Summary**: Dispatches a custom announcement broadcast to all event attendees and organizers. |
| ├── **Handler** | `events/organizer_tools#send_announcement_email` |
| ├── **Type & Exposure** | `BUSINESS_LOGIC / EXTERNAL_INTERNET_EXPOSED (HTTPS)` |
| ├── **Authentication** | `AUTHENTICATED (Devise Session)` |
| ├── **Roles Required** | `Organizer, Chapter Leader` |
| ├── **Sensitive Data** | `PII (Attendee Emails)` |
| ├── **Secure Parameters** | `PATH: :event_id (HIGH_RISK_CONTROL), BODY: subject (STANDARD_INPUT), BODY: body (STANDARD_INPUT)` |
| ├── **Known Flaws / Risks** | `Unrestricted Email Broadcast / Phishing Risk` |
| └── **Degree Connection** | `1st Degree (CRITICAL)` |
| **`#11: POST /events/unpublished_events/:id/publish`** | **Functional Summary**: Approves and publishes a draft workshop event to make it visible on public feeds. |
| ├── **Handler** | `events/unpublished_events#publish` |
| ├── **Type & Exposure** | `BUSINESS_LOGIC / EXTERNAL_INTERNET_EXPOSED (HTTPS)` |
| ├── **Authentication** | `AUTHENTICATED (Devise Session)` |
| ├── **Roles Required** | `Publisher, Admin, Chapter Leader` |
| ├── **Secure Parameters** | `PATH: :id (HIGH_RISK_CONTROL)` |
| ├── **Known Flaws / Risks** | `Unauthorized State Change / Privilege Bypass` |
| └── **Degree Connection** | `1st Degree (HIGH)` |
| **`#12: POST /events/unpublished_events/:id/flag`** | **Functional Summary**: Flags an unpublished event as requiring review or moderation. |
| ├── **Handler** | `events/unpublished_events#flag` |
| ├── **Type & Exposure** | `BUSINESS_LOGIC / EXTERNAL_INTERNET_EXPOSED (HTTPS)` |
| ├── **Authentication** | `AUTHENTICATED (Devise Session)` |
| ├── **Roles Required** | `Publisher, Admin` |
| ├── **Secure Parameters** | `PATH: :id (HIGH_RISK_CONTROL)` |
| └── **Degree Connection** | `1st Degree (HIGH)` |
| **`#13: POST /events/:event_id/rsvps`** | **Functional Summary**: Registers students or volunteers for workshop participation including dietary restrictions and childcare requests. |
| ├── **Handler** | `rsvps#create` |
| ├── **Type & Exposure** | `BUSINESS_LOGIC / EXTERNAL_INTERNET_EXPOSED (HTTPS)` |
| ├── **Authentication** | `AUTHENTICATED (Devise Session)` |
| ├── **Roles Required** | `Student, Volunteer` |
| ├── **Sensitive Data** | `PII (Dietary Needs, Emergency Contact)` |
| ├── **Secure Parameters** | `PATH: :event_id (HIGH_RISK_CONTROL), BODY: rsvp[dietary_restrictions] (SENSITIVE_PII_PHI)` |
| ├── **Known Flaws / Risks** | `Potential BOLA / IDOR on Event ID` |
| └── **Degree Connection** | `1st Degree (HIGH)` |
| **`#14: PATCH/PUT /events/:event_id/rsvps/:id`** | **Functional Summary**: Updates an existing RSVP status, dietary preferences, or waitlist position. |
| ├── **Handler** | `rsvps#update` |
| ├── **Type & Exposure** | `BUSINESS_LOGIC / EXTERNAL_INTERNET_EXPOSED (HTTPS)` |
| ├── **Authentication** | `AUTHENTICATED (Devise Session)` |
| ├── **Roles Required** | `Student, Volunteer, Organizer` |
| ├── **Secure Parameters** | `PATH: :event_id (HIGH_RISK_CONTROL), PATH: :id (HIGH_RISK_CONTROL)` |
| ├── **Known Flaws / Risks** | `IDOR on RSVP ID / Unauthorized Status Change` |
| └── **Degree Connection** | `1st Degree (HIGH)` |
| **`#15: DELETE /events/:event_id/rsvps/:id`** | **Functional Summary**: Cancels an existing workshop RSVP for a student or volunteer. |
| ├── **Handler** | `rsvps#destroy` |
| ├── **Type & Exposure** | `BUSINESS_LOGIC / EXTERNAL_INTERNET_EXPOSED (HTTPS)` |
| ├── **Authentication** | `AUTHENTICATED (Devise Session)` |
| ├── **Roles Required** | `Student, Volunteer, Organizer` |
| ├── **Secure Parameters** | `PATH: :event_id (HIGH_RISK_CONTROL), PATH: :id (HIGH_RISK_CONTROL)` |
| ├── **Known Flaws / Risks** | `IDOR / BOLA Deletion Flaw` |
| └── **Degree Connection** | `1st Degree (HIGH)` |
| **`#16: POST /events`** | **Functional Summary**: Creates a new RailsBridge workshop event with locations, schedules, and custom details. |
| ├── **Handler** | `events#create` |
| ├── **Type & Exposure** | `BUSINESS_LOGIC / EXTERNAL_INTERNET_EXPOSED (HTTPS)` |
| ├── **Authentication** | `AUTHENTICATED (Devise Session)` |
| ├── **Roles Required** | `User, Organizer` |
| ├── **Secure Parameters** | `BODY: event[title] (STANDARD_INPUT), event[details] (STANDARD_INPUT), event[chapter_id] (HIGH_RISK_CONTROL)` |
| ├── **Known Flaws / Risks** | `Stored XSS in Event Details, Unvalidated Chapter Scope` |
| └── **Degree Connection** | `1st Degree (HIGH)` |
| **`#17: PATCH/PUT /events/:id`** | **Functional Summary**: Updates event parameters, schedules, or volunteer instructions. |
| ├── **Handler** | `events#update` |
| ├── **Type & Exposure** | `BUSINESS_LOGIC / EXTERNAL_INTERNET_EXPOSED (HTTPS)` |
| ├── **Authentication** | `AUTHENTICATED (Devise Session)` |
| ├── **Roles Required** | `Organizer, Chapter Leader` |
| ├── **Secure Parameters** | `PATH: :id (HIGH_RISK_CONTROL), BODY: event[...]` |
| ├── **Known Flaws / Risks** | `BOLA / Unauthorized Event Modification` |
| └── **Degree Connection** | `1st Degree (HIGH)` |
| **`#18: DELETE /events/:id`** | **Functional Summary**: Cancels and deletes an entire workshop event from the system. |
| ├── **Handler** | `events#destroy` |
| ├── **Type & Exposure** | `BUSINESS_LOGIC / EXTERNAL_INTERNET_EXPOSED (HTTPS)` |
| ├── **Authentication** | `AUTHENTICATED (Devise Session)` |
| ├── **Roles Required** | `Organizer, Chapter Leader, Admin` |
| ├── **Secure Parameters** | `PATH: :id (HIGH_RISK_CONTROL)` |
| ├── **Known Flaws / Risks** | `Unauthorized Resource Deletion` |
| └── **Degree Connection** | `1st Degree (HIGH)` |
| **`#19: POST /events/:event_id/sections`** | **Functional Summary**: Creates workshop class sections (e.g. beginner, intermediate) for an event. |
| ├── **Handler** | `sections#create` |
| ├── **Type & Exposure** | `BUSINESS_LOGIC / EXTERNAL_INTERNET_EXPOSED (HTTPS)` |
| ├── **Authentication** | `AUTHENTICATED (Devise Session)` |
| ├── **Roles Required** | `Organizer` |
| ├── **Secure Parameters** | `PATH: :event_id (HIGH_RISK_CONTROL)` |
| └── **Degree Connection** | `1st Degree (HIGH)` |
| **`#20: POST /events/:event_id/sections/arrange`** | **Functional Summary**: Automatically or manually arranges students and volunteers into workshop sections. |
| ├── **Handler** | `sections#arrange` |
| ├── **Type & Exposure** | `BUSINESS_LOGIC / EXTERNAL_INTERNET_EXPOSED (HTTPS)` |
| ├── **Authentication** | `AUTHENTICATED (Devise Session)` |
| ├── **Roles Required** | `Organizer` |
| ├── **Secure Parameters** | `PATH: :event_id (HIGH_RISK_CONTROL)` |
| └── **Degree Connection** | `1st Degree (HIGH)` |
| **`#21: POST /events/:event_id/organizers`** | **Functional Summary**: Adds a co-organizer user to a workshop event. |
| ├── **Handler** | `organizers#create` |
| ├── **Type & Exposure** | `BUSINESS_LOGIC / EXTERNAL_INTERNET_EXPOSED (HTTPS)` |
| ├── **Authentication** | `AUTHENTICATED (Devise Session)` |
| ├── **Roles Required** | `Organizer, Chapter Leader` |
| ├── **Secure Parameters** | `PATH: :event_id (HIGH_RISK_CONTROL), BODY: organizer[user_id] (HIGH_RISK_CONTROL)` |
| ├── **Known Flaws / Risks** | `Privilege Grant to Event Scope` |
| └── **Degree Connection** | `1st Degree (HIGH)` |
| **`#22: DELETE /events/:event_id/organizers/:id`** | **Functional Summary**: Removes a co-organizer from an event. |
| ├── **Handler** | `organizers#destroy` |
| ├── **Type & Exposure** | `BUSINESS_LOGIC / EXTERNAL_INTERNET_EXPOSED (HTTPS)` |
| ├── **Authentication** | `AUTHENTICATED (Devise Session)` |
| ├── **Roles Required** | `Organizer, Chapter Leader` |
| ├── **Secure Parameters** | `PATH: :event_id (HIGH_RISK_CONTROL), PATH: :id (HIGH_RISK_CONTROL)` |
| └── **Degree Connection** | `1st Degree (HIGH)` |
| **`#23: POST /chapters`** | **Functional Summary**: Creates a new local chapter organization for hosting events. |
| ├── **Handler** | `chapters#create` |
| ├── **Type & Exposure** | `BUSINESS_LOGIC / EXTERNAL_INTERNET_EXPOSED (HTTPS)` |
| ├── **Authentication** | `AUTHENTICATED (Devise Session)` |
| ├── **Roles Required** | `Admin, Publisher` |
| ├── **Secure Parameters** | `BODY: chapter[name] (STANDARD_INPUT)` |
| └── **Degree Connection** | `1st Degree (HIGH)` |
| **`#24: POST /regions`** | **Functional Summary**: Defines a new geographic region grouping multiple chapters. |
| ├── **Handler** | `regions#create` |
| ├── **Type & Exposure** | `BUSINESS_LOGIC / EXTERNAL_INTERNET_EXPOSED (HTTPS)` |
| ├── **Authentication** | `AUTHENTICATED (Devise Session)` |
| ├── **Roles Required** | `Admin` |
| ├── **Secure Parameters** | `BODY: region[name] (STANDARD_INPUT)` |
| └── **Degree Connection** | `1st Degree (HIGH)` |
| **`#25: POST /organizations`** | **Functional Summary**: Registers a new umbrella organization representing multiple chapters. |
| ├── **Handler** | `organizations#create` |
| ├── **Type & Exposure** | `BUSINESS_LOGIC / EXTERNAL_INTERNET_EXPOSED (HTTPS)` |
| ├── **Authentication** | `AUTHENTICATED (Devise Session)` |
| ├── **Roles Required** | `Admin` |
| └── **Degree Connection** | `1st Degree (HIGH)` |
| **`#26: POST /locations`** | **Functional Summary**: Creates a new physical location venue for hosting events. |
| ├── **Handler** | `locations#create` |
| ├── **Type & Exposure** | `BUSINESS_LOGIC / EXTERNAL_INTERNET_EXPOSED (HTTPS)` |
| ├── **Authentication** | `AUTHENTICATED (Devise Session)` |
| ├── **Roles Required** | `User, Organizer` |
| ├── **Secure Parameters** | `BODY: location[address] (PII), location[name] (STANDARD_INPUT)` |
| └── **Degree Connection** | `1st Degree (HIGH)` |
| **`#27: PATCH /locations/:id/archive`** | **Functional Summary**: Archives a venue location so it cannot be selected for new events. |
| ├── **Handler** | `locations#archive` |
| ├── **Type & Exposure** | `BUSINESS_LOGIC / EXTERNAL_INTERNET_EXPOSED (HTTPS)` |
| ├── **Authentication** | `AUTHENTICATED (Devise Session)` |
| ├── **Roles Required** | `Admin, Chapter Leader` |
| ├── **Secure Parameters** | `PATH: :id (HIGH_RISK_CONTROL)` |
| └── **Degree Connection** | `1st Degree (HIGH)` |
| **`#28: POST /courses`** | **Functional Summary**: Creates a new workshop curriculum course module. |
| ├── **Handler** | `courses#create` |
| ├── **Type & Exposure** | `BUSINESS_LOGIC / EXTERNAL_INTERNET_EXPOSED (HTTPS)` |
| ├── **Authentication** | `AUTHENTICATED (Devise Session)` |
| ├── **Roles Required** | `Admin` |
| └── **Degree Connection** | `1st Degree (HIGH)` |
| **`#29: POST /external_events`** | **Functional Summary**: Adds an external partner event listing to the bridge troll calendar. |
| ├── **Handler** | `external_events#create` |
| ├── **Type & Exposure** | `BUSINESS_LOGIC / EXTERNAL_INTERNET_EXPOSED (HTTPS)` |
| ├── **Authentication** | `AUTHENTICATED (Devise Session)` |
| ├── **Roles Required** | `Admin, Publisher` |
| └── **Degree Connection** | `1st Degree (HIGH)` |
| **`#30: GET /events`** | **Functional Summary**: Lists upcoming published workshop events visible to the current user. |
| ├── **Handler** | `events#index` |
| ├── **Type & Exposure** | `BUSINESS_LOGIC / EXTERNAL_INTERNET_EXPOSED (HTTPS)` |
| ├── **Authentication** | `UNAUTHENTICATED / PUBLIC` |
| └── **Degree Connection** | `2nd Degree (MEDIUM)` |
| **`#31: GET /events/:id`** | **Functional Summary**: Displays details, session schedules, and RSVP attendee lists for a specific event. |
| ├── **Handler** | `events#show` |
| ├── **Type & Exposure** | `BUSINESS_LOGIC / EXTERNAL_INTERNET_EXPOSED (HTTPS)` |
| ├── **Authentication** | `UNAUTHENTICATED / PUBLIC` |
| ├── **Sensitive Data** | `PII (Attendee Names, Public Email)` |
| ├── **Secure Parameters** | `PATH: :id (HIGH_RISK_CONTROL)` |
| └── **Degree Connection** | `2nd Degree (MEDIUM)` |
| **`#32: GET /events/feed`** | **Functional Summary**: Serves RSS and Atom feeds of upcoming public workshop events. |
| ├── **Handler** | `events#feed` |
| ├── **Type & Exposure** | `BUSINESS_LOGIC / EXTERNAL_INTERNET_EXPOSED (HTTPS)` |
| ├── **Authentication** | `UNAUTHENTICATED / PUBLIC` |
| └── **Degree Connection** | `2nd Degree (LOW)` |
| **`#33: GET /events/past_events`** | **Functional Summary**: Displays historical archive of completed workshops. |
| ├── **Handler** | `events#past_events` |
| ├── **Type & Exposure** | `BUSINESS_LOGIC / EXTERNAL_INTERNET_EXPOSED (HTTPS)` |
| ├── **Authentication** | `UNAUTHENTICATED / PUBLIC` |
| └── **Degree Connection** | `2nd Degree (LOW)` |
| **`#34: GET /events/:id/levels`** | **Functional Summary**: Displays student experience level descriptions for an event. |
| ├── **Handler** | `events#levels` |
| ├── **Type & Exposure** | `BUSINESS_LOGIC / EXTERNAL_INTERNET_EXPOSED (HTTPS)` |
| ├── **Authentication** | `UNAUTHENTICATED / PUBLIC` |
| └── **Degree Connection** | `2nd Degree (LOW)` |
| **`#35: GET /users`** | **Functional Summary**: Lists registered users and community members across chapters. |
| ├── **Handler** | `users#index` |
| ├── **Type & Exposure** | `BUSINESS_LOGIC / EXTERNAL_INTERNET_EXPOSED (HTTPS)` |
| ├── **Authentication** | `AUTHENTICATED (Devise Session)` |
| ├── **Sensitive Data** | `PII (User Names, Locations)` |
| └── **Degree Connection** | `2nd Degree (MEDIUM)` |
| **`#36: GET /users/:user_id/profile`** | **Functional Summary**: Displays user public profile, attended workshops, and leadership roles. |
| ├── **Handler** | `profiles#show` |
| ├── **Type & Exposure** | `BUSINESS_LOGIC / EXTERNAL_INTERNET_EXPOSED (HTTPS)` |
| ├── **Authentication** | `AUTHENTICATED (Devise Session)` |
| ├── **Sensitive Data** | `PII (Email, Bio, Location)` |
| ├── **Secure Parameters** | `PATH: :user_id (HIGH_RISK_CONTROL)` |
| └── **Degree Connection** | `2nd Degree (MEDIUM)` |
| **`#37: GET /chapters`** | **Functional Summary**: Lists active chapter groups and regional organization details. |
| ├── **Handler** | `chapters#index` |
| ├── **Type & Exposure** | `BUSINESS_LOGIC / EXTERNAL_INTERNET_EXPOSED (HTTPS)` |
| ├── **Authentication** | `UNAUTHENTICATED / PUBLIC` |
| └── **Degree Connection** | `2nd Degree (LOW)` |
| **`#38: GET /chapters/:id`** | **Functional Summary**: Shows chapter details, local leadership team, and upcoming regional workshops. |
| ├── **Handler** | `chapters#show` |
| ├── **Type & Exposure** | `BUSINESS_LOGIC / EXTERNAL_INTERNET_EXPOSED (HTTPS)` |
| ├── **Authentication** | `UNAUTHENTICATED / PUBLIC` |
| └── **Degree Connection** | `2nd Degree (LOW)` |
| **`#39: GET /regions`** | **Functional Summary**: Lists geographic regions containing local chapters. |
| ├── **Handler** | `regions#index` |
| ├── **Type & Exposure** | `BUSINESS_LOGIC / EXTERNAL_INTERNET_EXPOSED (HTTPS)` |
| ├── **Authentication** | `UNAUTHENTICATED / PUBLIC` |
| └── **Degree Connection** | `2nd Degree (LOW)` |
| **`#40: GET /locations`** | **Functional Summary**: Displays list of available event venue locations. |
| ├── **Handler** | `locations#index` |
| ├── **Type & Exposure** | `BUSINESS_LOGIC / EXTERNAL_INTERNET_EXPOSED (HTTPS)` |
| ├── **Authentication** | `UNAUTHENTICATED / PUBLIC` |
| └── **Degree Connection** | `2nd Degree (LOW)` |
| **`#41: GET /courses`** | **Functional Summary**: Lists available teaching curricula and course materials. |
| ├── **Handler** | `courses#index` |
| ├── **Type & Exposure** | `BUSINESS_LOGIC / EXTERNAL_INTERNET_EXPOSED (HTTPS)` |
| ├── **Authentication** | `UNAUTHENTICATED / PUBLIC` |
| └── **Degree Connection** | `2nd Degree (LOW)` |
| **`#42: GET /about`** | **Functional Summary**: Renders public informational page describing RailsBridge mission and community guidelines. |
| ├── **Handler** | `static_pages#about` |
| ├── **Type & Exposure** | `BUSINESS_LOGIC / EXTERNAL_INTERNET_EXPOSED (HTTPS)` |
| ├── **Authentication** | `UNAUTHENTICATED / PUBLIC` |
| └── **Degree Connection** | `2nd Degree (LOW)` |
| **`#43: GET /style_guide`** | **Functional Summary**: Displays UI style guide and CSS component showcase. |
| ├── **Handler** | `static_pages#style_guide` |
| ├── **Type & Exposure** | `DEBUG_DIAGNOSTIC / EXTERNAL_INTERNET_EXPOSED (HTTPS)` |
| ├── **Authentication** | `UNAUTHENTICATED / PUBLIC` |
| └── **Degree Connection** | `2nd Degree (LOW)` |

---

## 5. Authorization Deep Dive Question

### **Challenge: How are users authorized in `bridge_troll`?**

`bridge_troll` enforces authorization through a **two-layered architecture**:

#### **Layer 1: Central Controller Enforcement (`ApplicationController` + Pundit)**
1. **Pundit Inclusion**: `ApplicationController` includes `Pundit::Authorization`.
2. **Global Verification Callback**: 
   ```ruby
   after_action :verify_authorized, unless: :devise_controller?
   ```
   This ensures that **every action** in every controller inheriting from `ApplicationController` MUST explicitly execute a Pundit authorization check (e.g., `authorize @event`) or explicitly opt out using `skip_authorization`. If a developer forgets to authorize an action, Rails raises a runtime `Pundit::AuthorizationNotPerformedError`.
3. **Rescue Handler**:
   ```ruby
   rescue_from Pundit::NotAuthorizedError, with: :user_not_authorized
   ```
   If a user fails an authorization check, Pundit raises `Pundit::NotAuthorizedError`, which is caught globally to display a flash error (`"You are not authorized to perform this action."`) and redirect the user safely back.

#### **Layer 2: Declarative Policy Classes (`app/policies/*_policy.rb`)**
Each domain model has a corresponding policy class inheriting from `ApplicationPolicy` (e.g., `EventPolicy`, `ChapterPolicy`, `RsvpPolicy`, `UserPolicy`).

1. **Role Identification Methodologies**:
   User roles and permissions are evaluated on the `user` model using boolean flags and association queries:
   - **Global Roles**: `user.admin?`, `user.publisher?`
   - **Scoped Leadership Roles**:
     - `user.chapter_leaderships.present?` / `record.chapter.leader?(user)`
     - `user.organization_leaderships.present?` / `record.organization.leader?(user)`
   - **Event-Specific Roles**: `record.organizer?(user)`, `record.checkiner?(user)`

2. **Policy Methods Example (`EventPolicy`)**:
   ```ruby
   def update?
     return false if record.historical?
     user.admin? || record.organizer?(user) || record.chapter.leader?(user) || record.organization.leader?(user)
   end

   def publish?
     user.publisher? || user.admin? || record.chapter.leader?(user) || record.chapter.organization.leader?(user)
   end
   ```

3. **Attribute-Level Authorization (`permitted_attributes`)**:
   Pundit policies also enforce **Mass Assignment Protection** by dynamically returning allowed strong parameter arrays based on user roles (e.g., `policy(User).permitted_attributes`).

---

## Mapping / Authorization Decorators Checklist

- [x] `include Pundit::Authorization` (`ApplicationController`)
- [x] `after_action :verify_authorized` (`ApplicationController`)
- [x] `authorize @record` (Called inside controller actions)
- [x] `policy_scope(Scope)` (Filters collection querysets based on user permissions)
- [x] `skip_authorization` (Explicitly used for public/unrestricted routes like `EventsController#index`, `#show`, `#past_events`)
- [x] `authenticate_user!` (Devise filter enforcing active authentication session)
- [x] `ApplicationPolicy`, `EventPolicy`, `ChapterPolicy`, `RsvpPolicy`, `UserPolicy`
