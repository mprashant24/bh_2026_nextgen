We assessed commit `#6f6486e3a0df149690487316e20ca3d1e45f5cc7`

# Notes for you/your team

## Behavior

* **What does it do? (business purpose)**
  VTM (Vulnerable Task Manager) is an intentionally insecure web application used for training and education. It manages projects, tasks, notes, user profiles, and file uploads/downloads, allowing users to collaborate on task assignments and track project completion.

* **Who does it do this for? (internal / external customer base)**
  - **Internal**: Project Managers, Team Members, Developers, and System Administrators.
  - **External**: Students, application security researchers, and trainees performing security testing.

* **What kind of information will it hold?**
  - **Patient / User PII**: Usernames, email addresses, names, biography descriptions, profile pictures.
  - **Credential / Secret Data**: Hashed passwords, password reset tokens, API session tokens (DRF Token Authentication).
  - **Project & Task Data**: Project names, task titles, descriptive task text, associated file attachments, and private project notes.

* **What are the different types of roles?**
  - **Administrator / Staff**: Full database control, django admin panel access, system-wide configurations, group/permissions management.
  - **Project Manager**: Create projects, assign tasks, edit project parameters, and moderate members.
  - **Team Member**: Create and modify assigned tasks, complete tasks, read assigned project scopes, and write notes.

* **What aspects concern your client/customer/staff the most?**
  - **Confidentiality of Projects & Notes**: Protecting private project tasks and notes from unauthorized external exposure or BOLA/IDOR access by other teams.
  - **Integrity of Task Assignments**: Preventing team members from modifying or deleting tasks belonging to projects they are not assigned to.
  - **System Access Integrity**: Enforcing strong authorization controls to prevent unauthenticated users from accessing project dashboards, downloading internal files, or escalating privileges to administrators.

We assessed commit `#6f6486e3a0df149690487316e20ca3d1e45f5cc7`

# Notes for you/your team

## Behavior

* **What does it do? (business purpose)**
  VTM (Vulnerable Task Manager) is an intentionally insecure web application used for training and education. It manages projects, tasks, notes, user profiles, and file uploads/downloads, allowing users to collaborate on task assignments and track project completion.
  
  Additionally, the application features an integrated **AI Chatbot** component (`chatbot/`) which acts as an intelligent assistant (VTAM Assistant). The chatbot uses a ReAct loop to query database records, search files, and help users create, update, or manage tasks dynamically.

* **Who does it do this for? (internal / external customer base)**
  - **Internal**: Project Managers, Team Members, Developers, and System Administrators.
  - **External**: Students, application security researchers, and trainees performing security testing.

* **What kind of information will it hold?**
  - **Patient / User PII**: Usernames, email addresses, names, biography descriptions, profile pictures.
  - **Credential / Secret Data**: Hashed passwords, password reset tokens, API session tokens (DRF Token Authentication).
  - **Project & Task Data**: Project names, task titles, descriptive task text, associated file attachments, and private project notes.
  - **AI / Chat Session Data**: User prompts, chat message logs, conversation histories, and agent tool execution contexts.

* **What are the different types of roles?**
  - **Administrator / Staff**: Full database control, django admin panel access, system-wide configurations, group/permissions management.
  - **Project Manager**: Create projects, assign tasks, edit project parameters, and moderate members.
  - **Team Member**: Create and modify assigned tasks, complete tasks, read assigned project scopes, and write notes.

* **What aspects concern your client/customer/staff the most?**
  - **Confidentiality of Projects & Notes**: Protecting private project tasks and notes from unauthorized external exposure or BOLA/IDOR access by other teams.
  - **Integrity of Task Assignments**: Preventing team members from modifying or deleting tasks belonging to projects they are not assigned to.
  - **System Access Integrity**: Enforcing strong authorization controls to prevent unauthenticated users from accessing project dashboards, downloading internal files, or escalating privileges to administrators.
  - **AI Prompt Injection & Data Leakage**: Preventing attackers from tricking the AI Chatbot into bypassing database security restrictions or exposing other users' private task data.

## Tech Stack

* **Framework & Language** - Backend: Django (Python) | API: Django REST Framework (DRF)
* **3rd party components**:
  * Python packages: `django`, `djangorestframework`, `drf-spectacular`, `django-health-check`, `openai` (AI Chatbot Client integration)
  * Client styling: Bootstrap, standard CSS/JS files
* **Datastore** - SQLite / MySQL (Database configuration for storing users, projects, tasks, notes, and files - SQLite is the active default)


## Brainstorming / Risks

* **BOLA/IDOR (Broken Object Level Authorization)**: Controllers fetching projects or tasks using primary keys directly from user-supplied parameters (`project_id`, `task_id`) without validating whether the requesting user belongs to the assigned project.
* **SQL Injection**: Using string formatting or raw SQL concatenation within Custom SQL queries or ORM extra clauses (e.g. login, forgot password, or search functions).
* **Stored and Reflected XSS**: Unescaped user-supplied inputs (like task names, descriptions, or project details) rendered in Django templates using the `|safe` filter or inside API response fields.
* **Privilege Escalation**: Modifying role/group attributes in the user profile updates or user registration parameters, allowing standard users to elevate themselves to administrative status.
* **AI Prompt Injection & Insecure Tool Execution**: Exploit loops inside `chatbot/views.py` and `chatbot/tools.py` where a malicious user prompt overrides system constraints or causes tools to perform unauthorized actions (e.g., viewing unassigned project details).

## Checklist of things to review

### Risks
- [ ] Look for instances of `|safe` in the templates (`taskManager/templates/**/*.html`).
- [ ] Look for OS commands or raw subprocess execution (e.g. `subprocess`, `os.system` in `views.py`).
- [ ] Inspect raw database query execution methods (`connection.cursor()`, `.raw()`, `.extra()`) for parameter interpolation flaws.
- [ ] Inspect AI system prompts and tool execution methods in `chatbot/views.py` and `chatbot/tools.py` for input handling flaws.

### Authentication
- [ ] Login endpoint (`/taskManager/login/`): Check for user enumeration or lack of brute-force protection/lockouts.
- [ ] Password Reset (`/taskManager/forgot_password/`): Check if token generation uses secure PRNG (`SecureRandom` / `secrets`) and validates expiration.

### Authorization
- [ ] Uses `@login_required` decorator: Verify all view functions in `views.py` require authenticated sessions.
- [ ] Object-level checks: Verify queryset lookups on Projects, Tasks, and Notes check user assignment (BOLA/IDOR).
- [ ] Chatbot Tool Access Controls: Ensure chatbot tool actions (`chatbot/tools.py`) perform strict user permission validation before returning data.

### Auditing/Logging
- [ ] Logging configuration in `settings.py`: Verify failed logins and sensitive administrative edits write security audit logs.

### Injection
- [ ] SQL Injection: Search for raw query formatting using `%` or f-strings in database execution sinks.

### Cryptography
- [ ] Verify security of session cookies (`SESSION_COOKIE_SECURE = True`) and secure storage of JWT/API tokens.

### Configuration
- [ ] Django settings: Check `DEBUG = False` and `ALLOWED_HOSTS` configurations in production settings.
- [ ] AI Integration: Check API keys and base url configurations for OpenAI SDK in `settings.py`.

## Mapping / Routes

- [x] `GET/POST /taskManager/login/` -> `taskManager.views.login` (Authentication)
- [x] `POST /taskManager/forgot_password/` -> `taskManager.views.forgot_password` (Credentials Reset)
- [x] `GET /taskManager/view_all_users/` -> `taskManager.views.view_all_users` (PII Listing)
- [x] `GET /taskManager/download/(?P<file_id>\d+)/` -> `taskManager.views.download` (File Download / IDOR Risk)
- [x] `POST /taskManager/(?P<project_id>\d+)/upload/` -> `taskManager.views.upload` (File Upload / Path Traversal)
- [x] `GET /taskManager/downloadprofilepic/(?P<user_id>\d+)/` -> `taskManager.views.download_profile_pic` (PII / IDOR)
- [x] `POST /taskManager/project_create/` -> `taskManager.views.project_create` (State Change)
- [x] `GET /taskManager/(?P<project_id>.+)/project_details/` -> `taskManager.views.project_details` (BOLA/IDOR Target)
- [x] `POST /taskManager/(?P<project_id>\d+)/task_create/` -> `taskManager.views.task_create` (State Change)
- [x] `GET /taskManager/(?P<project_id>\d+)/(?P<task_id>\d+)/` -> `taskManager.views.task_details` (BOLA/IDOR Target)
- [x] `POST /taskManager/(?P<project_id>\d+)/task_edit/(?P<task_id>\d+)` -> `taskManager.views.task_edit` (State Change)
- [x] `POST /taskManager/(?P<project_id>\d+)/task_delete/(?P<task_id>\d+)` -> `taskManager.views.task_delete` (State Change)
- [x] `GET /taskManager/settings/` -> `taskManager.views.tm_settings` (DEBUG Endpoint)
- [x] `GET /taskManager/ping/` -> `taskManager.views.ping` (DEBUG Endpoint)
- [x] `GET/POST /chat/` -> `chatbot.views` (Integrated AI Assistant Chat Interface)

## Mapping / Authorization Decorators

- [x] `@login_required` (Django standard authentication decorator applied to views)
- [x] `is_authenticated` (Django session verification check inside views)
- [x] `permission_classes = [IsAuthenticated]` (DRF API token verification)
- [x] `_project_accessible`, `_task_accessible`, `_note_accessible` (Custom authorization checks in `chatbot/tools.py`)

## Mapping / Files

- [x] `taskManager/wsgi.py` (WSGI app entry point)
- [x] `taskManager/settings.py` (Central application configuration)
- [x] `taskManager/urls.py` (Master routing patterns)
- [x] `taskManager/taskManager_urls.py` (taskManager app namespaces routes)
- [x] `taskManager/views.py` (Controller actions and business logic handlers)
- [x] `taskManager/models.py` (ActiveRecord ORM DB schemas)
- [x] `taskManager/middleware.py` (Custom security & request/session processing middleware)
- [x] `chatbot/views.py` (Chat interface controllers & ReAct loops)
- [x] `chatbot/tools.py` (AI Assistant database query tools & permissions)
