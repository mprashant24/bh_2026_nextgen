# Security Assessment & Route Inventory: VTM (`c:/workspace/vtm`)

We assessed commit `#6f6486e3a0df149690487316e20ca3d1e45f5cc7`

---

## 1. Behavior & Business Purpose
* **What does it do? (business purpose)**: VTM (Vulnerable Task Manager) is an intentionally insecure task and project management web application designed for developer and security training. It supports creating projects, managing task lists, posting project notes, uploading/downloading related attachments, and user registration.
  - **AI Integration**: Additionally, VTM includes an integrated **AI Chatbot** (`chatbot/`) which acts as an intelligent assistant (VTAM Assistant), using a ReAct loop to query databases, search files, and help users manage tasks dynamically.
* **Who does it do this for?**:
  - **Internal**: Project Managers, Team Members, Developers, and System Administrators.
  - **External**: Students, security trainees, and application security researchers.
* **What kind of information will it hold?**:
  - **PII**: Usernames, email addresses, biography descriptions, and profile pictures.
  - **Auth Data**: Hashed user passwords, password reset tokens, and API authentication tokens.
  - **Project & Task Data**: Project names, task descriptions, private project notes, and uploaded files.
  - **AI Conversation Logs**: User chat logs, AI agent tool execution contexts, and chat history.
* **What aspects concern clients/staff the most?**:
  - Protecting private projects, tasks, and notes from unauthorized external exposure or BOLA/IDOR access by unassigned users.
  - Preventing attackers from using SQL Injection or XSS vulnerabilities to compromise the server or take over admin sessions.
  - Preventing prompt injection attacks against the AI Chatbot to bypass data boundaries.

---

## 2. Tech Stack
* **Framework & Language**: Django 4.x / Python 3.12, Django REST Framework (DRF)
* **Datastore**: SQLite (Primary active default backend) / MySQL (commented out setup option)
* **Authentication**: Django Session Authentication (Web UI) + DRF Token / JWT Authentication (APIs)
* **Authorization**: Django Groups (`admin_g`, `project_managers`, `team_member`) and view-level permissions (`user.has_perm()`)
* **3rd Party Components**: `djangorestframework`, `rest_framework_simplejwt`, `drf-spectacular`, `openai` (AI Chatbot client), `django-health-check`

---

## 3. Brainstorming & Risk Profile
* **Insecure Direct Object Reference (IDOR/BOLA)**: Viewing project details (`project_details`), downloading attachments (`download`), or viewing task details (`task_details`) via integer IDs without verifying if the requesting user belongs to the assigned project.
* **Severe SQL Injection (SQLi)**: Custom SQL query concatenations or string formats within views (such as the login, forgot password, or task search endpoints).
* **Stored & Reflected XSS**: Unescaped user-supplied inputs rendered in HTML templates using Django's `|safe` filter, or raw output rendering inside API responses.
* **AI Prompt Injection**: Unvalidated user prompts hijacking the OpenAI ReAct loop inside `chatbot/` to run unauthorized tool actions (e.g., extracting other users' files or private tasks).

---

## 4. Route Security Inventory

### Summary
- **Total Routes Identified**: 37 Endpoints
- **External Internet-Exposed Routes**: 37
- **Internal Private Routes**: 0 (Monolithic Django Web Application)
- **Protocols & API Styles**: `HTTPS` (REST / Django Templates / JSON)
- **1st Degree High-Relevance Routes**: 25
- **2nd Degree Connected Routes**: 12
- **Authentication Routes**: 6
- **Debug / Diagnostic Routes**: 3

---

### Route Inventory Table (Sorted by Priority Rank Number)

| Route / Security Attribute | Details / Value |
| :--- | :--- |
| **`#1: POST /taskManager/forgot_password/`** | **Functional Summary**: Authenticates password recovery requests and sends a reset token to user email. |
| ├── **Handler** | `taskManager.views.forgot_password` |
| ├── **Type & Exposure** | `AUTHENTICATION / EXTERNAL_INTERNET_EXPOSED (HTTPS)` |
| ├── **Authentication** | `UNAUTHENTICATED / PUBLIC` |
| ├── **Sensitive Data** | `CREDENTIALS (Reset Tokens), PII (Email)` |
| ├── **Secure Parameters** | `BODY: email (SENSITIVE_PII_PHI)` |
| ├── **Known Flaws / Risks** | `SQL Injection via String Concatenation, User Enumeration` |
| └── **Degree Connection** | `1st Degree (CRITICAL)` |
| **`#2: POST /taskManager/login/`** | **Functional Summary**: Validates user credentials and issues session cookies along with JWT tokens. |
| ├── **Handler** | `taskManager.views.login` |
| ├── **Type & Exposure** | `AUTHENTICATION / EXTERNAL_INTERNET_EXPOSED (HTTPS)` |
| ├── **Authentication** | `UNAUTHENTICATED / PUBLIC` |
| ├── **Sensitive Data** | `CREDENTIALS (Passwords, JWT Tokens), PII` |
| ├── **Secure Parameters** | `BODY: username (PII), BODY: password (CREDENTIALS_SECRET)` |
| ├── **Known Flaws / Risks** | `Password Leaked in Plaintext Debug Logs, User Enumeration` |
| └── **Degree Connection** | `1st Degree (CRITICAL)` |
| **`#3: POST /taskManager/manage_groups/`** | **Functional Summary**: Administrative endpoint allowing assignment of users to roles/groups. |
| ├── **Handler** | `taskManager.views.manage_groups` |
| ├── **Type & Exposure** | `ADMINISTRATIVE / EXTERNAL_INTERNET_EXPOSED (HTTPS)` |
| ├── **Authentication** | `AUTHENTICATED (Django Session)` |
| ├── **Roles Required** | `Staff / Users with auth.change_group permission` |
| ├── **Secure Parameters** | `BODY: userid (HIGH_RISK_CONTROL), BODY: accesslevel (HIGH_RISK_CONTROL)` |
| ├── **Known Flaws / Risks** | `Unchecked Privilege Escalation, BOLA` |
| └── **Degree Connection** | `1st Degree (CRITICAL)` |
| **`#4: POST /taskManager/manage_projects/`** | **Functional Summary**: Administrative endpoint for assigning users to projects. |
| ├── **Handler** | `taskManager.views.manage_projects` |
| ├── **Type & Exposure** | `ADMINISTRATIVE / EXTERNAL_INTERNET_EXPOSED (HTTPS)` |
| ├── **Authentication** | `AUTHENTICATED (Django Session)` |
| ├── **Roles Required** | `Staff / Users with auth.change_group permission` |
| ├── **Secure Parameters** | `BODY: userid (HIGH_RISK_CONTROL), BODY: projectid (HIGH_RISK_CONTROL)` |
| ├── **Known Flaws / Risks** | `BOLA / Unauthorized Project Assignment` |
| └── **Degree Connection** | `1st Degree (CRITICAL)` |
| **`#5: GET /taskManager/search/`** | **Functional Summary**: Searches projects and tasks matching a search keyword. |
| ├── **Handler** | `taskManager.views.search` |
| ├── **Type & Exposure** | `BUSINESS_LOGIC / EXTERNAL_INTERNET_EXPOSED (HTTPS)` |
| ├── **Authentication** | `AUTHENTICATED (Django Session)` |
| ├── **Secure Parameters** | `QUERY: q (HIGH_RISK_CONTROL)` |
| ├── **Known Flaws / Risks** | `SQL Injection in Raw Search Query, BOLA/IDOR` |
| └── **Degree Connection** | `1st Degree (CRITICAL)` |
| **`#6: POST /chat/`** | **Functional Summary**: Sends conversation prompts to the ReAct loop AI Chatbot interface. |
| ├── **Handler** | `chatbot.views` |
| ├── **Type & Exposure** | `BUSINESS_LOGIC / EXTERNAL_INTERNET_EXPOSED (HTTPS)` |
| ├── **Authentication** | `AUTHENTICATED (Django Session)` |
| ├── **Secure Parameters** | `BODY: message (HIGH_RISK_CONTROL)` |
| ├── **Known Flaws / Risks** | `AI Prompt Injection, Insecure Tool Data Access Bypasses` |
| └── **Degree Connection** | `1st Degree (CRITICAL)` |
| **`#7: GET /taskManager/settings/`** | **Functional Summary**: Debug endpoint exposing system configurations and environmental variables. |
| ├── **Handler** | `taskManager.views.tm_settings` |
| ├── **Type & Exposure** | `DEBUG_DIAGNOSTIC / EXTERNAL_INTERNET_EXPOSED (HTTPS)` |
| ├── **Authentication** | `AUTHENTICATED (Django Session)` |
| ├── **Roles Required** | `Staff / Admin` |
| ├── **Privileges Needed** | `SYSTEM_ADMIN` |
| ├── **Known Flaws / Risks** | `Information Disclosure of Secrets / Settings` |
| └── **Degree Connection** | `1st Degree (CRITICAL)` |
| **`#8: GET /taskManager/ping/`** | **Functional Summary**: Debug utility pinging external hosts to verify outbound network connectivity. |
| ├── **Handler** | `taskManager.views.ping` |
| ├── **Type & Exposure** | `DEBUG_DIAGNOSTIC / EXTERNAL_INTERNET_EXPOSED (HTTPS)` |
| ├── **Authentication** | `AUTHENTICATED (Django Session)` |
| ├── **Roles Required** | `Staff / Admin` |
| ├── **Privileges Needed** | `SYSTEM_ADMIN` |
| ├── **Secure Parameters** | `QUERY: host (HIGH_RISK_CONTROL)` |
| ├── **Known Flaws / Risks** | `OS Command Injection` |
| └── **Degree Connection** | `1st Degree (CRITICAL)` |
| **`#9: GET /taskManager/download/:file_id/`** | **Functional Summary**: Downloads project file attachments by file ID. |
| ├── **Handler** | `taskManager.views.download` |
| ├── **Type & Exposure** | `BUSINESS_LOGIC / EXTERNAL_INTERNET_EXPOSED (HTTPS)` |
| ├── **Authentication** | `AUTHENTICATED (Django Session)` |
| ├── **Secure Parameters** | `PATH: :file_id (HIGH_RISK_CONTROL)` |
| ├── **Known Flaws / Risks** | `IDOR / BOLA File Access, Path Traversal` |
| └── **Degree Connection** | `1st Degree (HIGH)` |
| **`#10: POST /taskManager/:project_id/upload/`** | **Functional Summary**: Uploads attachment files to a project directory. |
| ├── **Handler** | `taskManager.views.upload` |
| ├── **Type & Exposure** | `BUSINESS_LOGIC / EXTERNAL_INTERNET_EXPOSED (HTTPS)` |
| ├── **Authentication** | `AUTHENTICATED (Django Session)` |
| ├── **Secure Parameters** | `PATH: :project_id (HIGH_RISK_CONTROL), BODY: file (HIGH_RISK_CONTROL)` |
| ├── **Known Flaws / Risks** | `Arbitrary File Upload / Path Traversal` |
| └── **Degree Connection** | `1st Degree (HIGH)` |
| **`#11: GET /taskManager/downloadprofilepic/:user_id/`** | **Functional Summary**: Downloads user profile pictures by user ID. |
| ├── **Handler** | `taskManager.views.download_profile_pic` |
| ├── **Type & Exposure** | `BUSINESS_LOGIC / EXTERNAL_INTERNET_EXPOSED (HTTPS)` |
| ├── **Authentication** | `UNAUTHENTICATED / PUBLIC` |
| ├── **Sensitive Data** | `PII (Profile Pictures)` |
| ├── **Secure Parameters** | `PATH: :user_id (HIGH_RISK_CONTROL)` |
| ├── **Known Flaws / Risks** | `Missing Authentication, IDOR` |
| └── **Degree Connection** | `1st Degree (HIGH)` |
| **`#12: GET /taskManager/:project_id/project_details/`** | **Functional Summary**: Retrieves details, tasks, and file lists for a specific project. |
| ├── **Handler** | `taskManager.views.project_details` |
| ├── **Type & Exposure** | `BUSINESS_LOGIC / EXTERNAL_INTERNET_EXPOSED (HTTPS)` |
| ├── **Authentication** | `AUTHENTICATED (Django Session)` |
| ├── **Secure Parameters** | `PATH: :project_id (HIGH_RISK_CONTROL)` |
| ├── **Known Flaws / Risks** | `Potential BOLA / IDOR Project Access` |
| └── **Degree Connection** | `1st Degree (HIGH)` |
| **`#13: GET /taskManager/:project_id/:task_id/`** | **Functional Summary**: Displays details and associated notes for a task. |
| ├── **Handler** | `taskManager.views.task_details` |
| ├── **Type & Exposure** | `BUSINESS_LOGIC / EXTERNAL_INTERNET_EXPOSED (HTTPS)` |
| ├── **Authentication** | `AUTHENTICATED (Django Session)` |
| ├── **Secure Parameters** | `PATH: :project_id (HIGH_RISK_CONTROL), PATH: :task_id (HIGH_RISK_CONTROL)` |
| ├── **Known Flaws / Risks** | `Potential BOLA / IDOR Task Access` |
| └── **Degree Connection** | `1st Degree (HIGH)` |
| **`#14: POST /taskManager/register/`** | **Functional Summary**: Registers a new user account. |
| ├── **Handler** | `taskManager.views.register` |
| ├── **Type & Exposure** | `AUTHENTICATION / EXTERNAL_INTERNET_EXPOSED (HTTPS)` |
| ├── **Authentication** | `UNAUTHENTICATED / PUBLIC` |
| ├── **Sensitive Data** | `CREDENTIALS (Passwords), PII` |
| ├── **Secure Parameters** | `BODY: username (PII), BODY: email (PII)` |
| └── **Degree Connection** | `1st Degree (HIGH)` |
| **`#15: GET /taskManager/view_img/`** | **Functional Summary**: Debug endpoint retrieving images from custom URLs. |
| ├── **Handler** | `taskManager.views.view_img` |
| ├── **Type & Exposure** | `DEBUG_DIAGNOSTIC / EXTERNAL_INTERNET_EXPOSED (HTTPS)` |
| ├── **Authentication** | `AUTHENTICATED (Django Session)` |
| ├── **Roles Required** | `Staff` |
| ├── **Secure Parameters** | `QUERY: url (HIGH_RISK_CONTROL)` |
| ├── **Known Flaws / Risks** | `Server-Side Request Forgery (SSRF)` |
| └── **Degree Connection** | `1st Degree (HIGH)` |
| **`#16: GET /taskManager/`** | **Functional Summary**: Renders user dashboard showing assigned tasks and projects. |
| ├── **Handler** | `taskManager.views.index` |
| ├── **Type & Exposure** | `BUSINESS_LOGIC / EXTERNAL_INTERNET_EXPOSED (HTTPS)` |
| ├── **Authentication** | `AUTHENTICATED (Django Session)` |
| └── **Degree Connection** | `2nd Degree (LOW)` |

---

## 5. Authorization Deep Dive Question

### **Challenge: How are users authorized in `VTM`?**

VTM utilizes standard Django session-based authorization and view-level guards, with significant structural bypass risks:

#### **Layer 1: View Authentication Guards (`@login_required`)**
1. **Authentication Decorator**: Standard Django `@login_required` decorators are placed on most views (e.g. `manage_projects`, `manage_tasks`, `upload`, `download`).
2. **REST Framework Filters**: API routes enforce authentication classes globally via Django REST Framework configuration settings (`IsAuthenticated`).

#### **Layer 2: Django Permissions & Group Verification**
VTM enforces permissions using Django's standard DB-backed `has_perm()` helper:
- **Task Management**: `manage_tasks` checks if the authenticated user has explicit task modification permissions:
  ```python
  if user.has_perm('can_change_task'):
  ```
- **Project & Group Management**: `manage_projects` and `manage_groups` check group modification permissions:
  ```python
  if user.has_perm('auth.change_group'):
  ```

#### **Vulnerabilities & Bypass Vectors**:
1. **Complete Lack of Object-Level Scoping (BOLA/IDOR)**:
   While users are verified to be logged in, view functions query database records directly using primary keys (`Project.objects.get(pk=project_id)`) without validating if the user belongs to the assigned project.
2. **Unvalidated Custom AI Chatbot Tools (`chatbot/tools.py`)**:
   VTM's chatbot views execute ReAct database queries. If the underlying prompt or chatbot handlers fail to validate user project memberships, an attacker can ask the AI to retrieve projects and task lists belonging to other users.

---

## Mapping / Authorization Decorators Checklist

- [x] `@login_required` (`taskManager/views.py` views)
- [x] `user.is_authenticated` (Session checks)
- [x] `user.has_perm('can_change_task')` (Task assignments)
- [x] `user.has_perm('auth.change_group')` (Project & Group management)
- [x] `permission_classes = [IsAuthenticated]` (DRF APIs)
- [x] `_project_accessible(user, project)` (Chatbot tool scoping)
