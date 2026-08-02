"""
OWASP Cheat Sheet Remediation Guidance Tool for DeepAgent SAST.
Provides authoritative remediation principles and code patterns based on OWASP Cheat Sheets.
"""

from typing import Optional, Type
from langchain_core.callbacks.manager import CallbackManagerForToolRun
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field


class OWASPCheatSheetInput(BaseModel):
    vulnerability_or_cwe: str = Field(
        description="The vulnerability name, category, or CWE ID (e.g., 'CWE-639', 'IDOR', 'CWE-862', 'Broken Access Control', 'CSRF', 'SQL Injection', 'Mass Assignment')."
    )


CHEATSHEET_DATABASE = {
    "cwe-639": """### OWASP Authorization & IDOR Cheat Sheet Guidance (CWE-639)
1. **Enforce Indirect Object References**: Avoid exposing direct database primary keys or internal IDs in URLs/params. Use unpredictable mapping tokens (e.g. UUIDv4).
2. **Server-Side Ownership Verification**: On every access or state change, query the database filtering directly by `request.user`:
   ```python
   # DO THIS:
   task = Task.objects.get(id=task_id, owner=request.user)
   ```
3. **Deny by Default**: Block access unless explicit ownership or permission policy is met.""",

    "idor": """### OWASP Authorization & IDOR Cheat Sheet Guidance (CWE-639)
1. **Server-Side Ownership Verification**: Always verify that `object.owner == request.user` before returning or modifying data.
2. **Scope Querysets**:
   ```python
   # Correct Django Pattern
   user_tasks = Task.objects.filter(owner=request.user)
   task = get_object_or_404(user_tasks, pk=task_id)
   ```
3. **Pundit / Policy Enforcers**: Use policy enforcement classes or Django permission mixins on class-based views.""",

    "cwe-862": """### OWASP Access Control Cheat Sheet Guidance (CWE-862: Missing Auth)
1. **Centralized Authentication**: Annotate views with `@login_required` or inherit `LoginRequiredMixin` for class-based views.
2. **Deny-by-Default Architecture**: Require explicit access control grants for every view.
3. **Django Implementation**:
   ```python
   @login_required
   def sensitive_view(request):
       ...
   ```""",

    "broken access control": """### OWASP Authorization Cheat Sheet Guidance
1. **Enforce Access Control in Trusted Server Code**: Never trust client-side parameters for user identity or roles.
2. **Validate State-Changing Requests**: Ensure POST/PUT/DELETE operations verify authorization policies identically to GET operations.
3. **Centralize Policy Logic**: Maintain reusable permission checkers (e.g., `user.has_perm()` or custom permission classes).""",

    "cwe-269": """### OWASP Privilege Management Cheat Sheet Guidance (CWE-269)
1. **Principle of Least Privilege**: Users should operate with minimal required access rights.
2. **Role Verification**: Explicitly verify staff/admin status using `@user_passes_test(lambda u: u.is_staff)` or permission decorators before executing privileged operations.
3. **Prevent Self-Elevation**: Block regular users from modifying role attributes in user update forms.""",

    "cwe-89": """### OWASP SQL Injection Prevention Cheat Sheet Guidance (CWE-89)
1. **Use Parameterized Queries / ORM**: Never build SQL queries via string concatenation or formatting (`%`, `f-strings`, `.format()`).
2. **Django ORM Practice**: Use standard ORM filter calls:
   ```python
   # Safe:
   User.objects.filter(username=user_input)
   ```
3. **Avoid Raw Execution**: Refactor `.raw()` or `.extra()` calls to parameterized query syntax.""",

    "cwe-79": """### OWASP Cross-Site Scripting (XSS) Prevention Cheat Sheet (CWE-79)
1. **Context-Aware Output Encoding**: Ensure dynamic variables rendered in HTML templates are escaped automatically.
2. **Avoid Unsafe Filters**: Never use `|safe` or `mark_safe()` on untrusted, user-supplied content.
3. **Content Security Policy (CSP)**: Deploy strict HTTP CSP headers to restrict executable script origins.""",

    "cwe-352": """### OWASP Cross-Site Request Forgery (CSRF) Prevention Cheat Sheet (CWE-352)
1. **Anti-CSRF Tokens**: Ensure all POST/PUT/DELETE forms include `{% csrf_token %}`.
2. **Avoid Disabling CSRF**: Do not use `@csrf_exempt` unless integrating verified external webhook endpoints with signature validation.
3. **SameSite Cookies**: Set `SESSION_COOKIE_SAMESITE = 'Lax'` or `'Strict'`.""",

    "cwe-915": """### OWASP Mass Assignment Prevention Cheat Sheet (CWE-915)
1. **Explicit Field Allowlisting**: Explicitly define `fields` in ModelForms or DRF Serializers rather than `fields = '__all__'`.
2. **Bind User Identity Server-Side**: Set user/owner references directly from `request.user` in view logic, ignoring client-provided `user_id` fields."""
}


class OWASPCheatSheetTool(BaseTool):
    name: str = "get_owasp_cheatsheet"
    description: str = (
        "Retrieves authoritative OWASP Cheat Sheet remediation guidance and code patterns for a given vulnerability type or CWE ID."
    )
    args_schema: Type[OWASPCheatSheetInput] = OWASPCheatSheetInput

    def _run(
        self, vulnerability_or_cwe: str, run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        key = vulnerability_or_cwe.strip().lower()

        # Exact match or substring search
        for db_key, guidance in CHEATSHEET_DATABASE.items():
            if db_key in key or key in db_key:
                return guidance

        # Default fallback guidance for general application security
        return (
            f"### OWASP Remediation Guidance for: {vulnerability_or_cwe}\n"
            "1. **Apply Principle of Least Privilege**: Grant users minimum required permissions.\n"
            "2. **Validate Input & Encode Output**: Perform server-side validation and context-aware escaping.\n"
            "3. **Verify Server-Side Authorization**: Perform explicit ownership checks (`object.owner == request.user`) for all resource operations.\n"
            "4. **Use Framework Defenses**: Rely on built-in Django ORM parameterization, CSRF middleware, and form allowlisting."
        )
