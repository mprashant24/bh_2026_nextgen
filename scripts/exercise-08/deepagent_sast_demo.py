import os
import sys
import git

# Ensure stdout uses UTF-8 encoding on Windows when redirected to a file
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from langchain_aws import ChatBedrockConverse
from langchain_core.runnables import RunnableLambda
from fetch_url_tool import FetchURLTool
from owasp_cheatsheet_tool import OWASPCheatSheetTool
from dotenv import load_dotenv


load_dotenv()

# Git repo setup
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
repo_url = "https://github.com/redpointsec/vtm.git"
repo_path = os.path.join(SCRIPT_DIR, "repo")

if os.path.isdir(repo_path) and os.path.isdir(os.path.join(repo_path, ".git")):
    print("Directory already contains a git repository.")
else:
    try:
        repo = git.Repo.clone_from(repo_url, repo_path)
        print(f"Repository cloned into: {repo_path}")
    except Exception as e:
        print(f"An error occurred while cloning the repository: {e}")

# LLM setup
llm = ChatBedrockConverse(
    model_id="qwen.qwen3-coder-30b-a3b-v1:0",
    temperature=0.6,
)

# Backend for local filesystem access - strictly scoped to the repo directory
filesystem_backend = FilesystemBackend(root_dir=repo_path, virtual_mode=True)

# Skills setup — loaded into each agent's context as domain expertise
skills_dir = os.path.join(SCRIPT_DIR, "skills")

print(f"Repo path: {repo_path}")
print(f"Skills directory: {skills_dir}")
for skill_name in os.listdir(skills_dir):
    skill_path = os.path.join(skills_dir, skill_name, "SKILL.md")
    if os.path.exists(skill_path):
        print(f"  - {skill_name}")

# --- Prompt 1: Context Collection ---
prompt_collect_context = """You are a security engineer performing reconnaissance on a Python/Django codebase.
Your ONLY job is to collect and organize code context relevant to access control.
Do NOT perform any security analysis yet. Just gather the facts.

### Search Strategy
- Focus all file searches strictly within the current repository directory (`./` or `./taskManager/`).
- Do NOT run broad glob searches on parent directories like `/workspace/nextgen` or root `/`.
- Use targeted globs like `*.py` or `taskManager/*.py` to quickly locate source files.

### What to Collect
1. **Routing & URL configuration** — Find all URL config files (urls.py). List every route and the view it maps to.
2. **Views & API endpoints** — Read every view function and class-based view. Note which ones have authentication/authorization decorators and which do NOT.
3. **Middleware** — Find and read all middleware classes, especially anything related to auth, sessions, or permissions.
4. **Models with ownership** — Identify models that have a user/owner foreign key or any field that ties data to a specific user.
5. **Permission classes & decorators** — Find all custom permission checks, decorators (login_required, permission_required, user_passes_test), and mixins (LoginRequiredMixin, PermissionRequiredMixin, etc.).
6. **Direct object lookups** — Find places where objects are fetched by ID from request parameters (GET/POST params, URL kwargs) without verifying the requesting user owns or has access to that object.

### Output Format
Produce a structured inventory in markdown:
- For each view/endpoint: the route, the view, what auth/authz is applied (or "NONE"), and whether it does object-level ownership checks.
- For each model with ownership: the model name, the ownership field, and which views query it.
- List any middleware that enforces access control globally.

Do NOT make security judgments. Just collect the raw facts.
"""

# --- Prompt 2: Analysis & Review Plan ---
prompt_analysis_plan = """You are a senior security engineer analyzing a Python/Django codebase for
OWASP Top 10 vulnerabilities and Django-specific flaws.

You have received an initial context inventory of the codebase (routes, views, models, middleware, permissions).
Your job is to build an **in-depth, highly accurate security review plan** using structured reflection to minimize false positives.

### File Search Strategy
- All file inspections must be relative to the repository root (`./` or `taskManager/`).
- Do NOT run broad glob searches on parent directories like `/workspace/nextgen` or root `/`.

### Phase 1: Context Triage & Reflection Questions
Before marking any code as insecure, answer these reflection questions:
- *Is this control really bypassed or missing?*
- *Is global authentication/authorization enforced via middleware or URL namespace decorators?*
- *Does the view query automatically scope objects using `request.user` (e.g., `Task.objects.filter(owner=request.user)`)?*
- *Am I certain about this finding, or am I making assumptions without reading the full view definition?*
- *What exact payload or HTTP request would an attacker send to exploit this?*

### Phase 2: Targeted Check Evaluation

Evaluate each category below. For each check, specify if it is APPLICABLE or NOT_APPLICABLE based on the context:

#### Check 1: Missing Authentication (CWE-862)
Views handling sensitive user data or actions lacking `@login_required`, `LoginRequiredMixin`, or DRF `IsAuthenticated`.
- SKIP IF: Global middleware enforces login on all non-public routes.

#### Check 2: Insecure Direct Object References / IDOR (CWE-639)
Objects fetched via user-supplied ID (`pk`, `id` in URL or POST params) without verifying ownership (`object.user == request.user`).
- SKIP IF: All querysets are scoped globally by `request.user`.

#### Check 3: Privilege Escalation & FLAC (CWE-269 / CWE-285)
Endpoints where regular users can execute staff/admin actions, or where POST/PUT/DELETE operations lack auth checks present on GET.

#### Check 4: Parameter Tampering & Mass Assignment (CWE-915)
Views that accept `user_id` or `role` fields directly from client input instead of trusting `request.user` server-side.

#### Check 5: Injection Vulnerabilities (CWE-89 / CWE-79)
Raw SQL string concatenation in ORM queries (`.extra()`, `.raw()`) or unescaped user inputs rendered in templates (`|safe`).

#### Check 6: Security Misconfigurations & CSRF (CWE-352 / CWE-942)
Abuse of `@csrf_exempt`, missing CSRF protection on state-changing endpoints, or overly permissive CORS settings.

#### Check 7: Forced Browsing & Obscurity (CWE-425)
Admin or privileged URL patterns (`/admin/`, `/manage/`) accessible without explicit authorization checks.

### Phase 3: Structured Output Format

Produce a review plan in JSON format:
```json
{{
  "context_summary": "2-3 sentences summarizing the app purpose and authentication posture",
  "checks": [
    {{
      "check_id": "check_1_missing_auth",
      "name": "Missing Authentication",
      "cwe": "CWE-862",
      "status": "APPLICABLE | NOT_APPLICABLE",
      "reason_for_status": "Why this check applies or does not apply",
      "findings": [
        {{
          "file": "file path",
          "location": "function/class name and line range",
          "observation": "Exact code flaw observed",
          "severity": "critical | high | medium | low",
          "confidence": "high | medium | low",
          "needs_validation": "Specific verification required in step 3"
        }}
      ]
    }}
  ]
}}
```

Be specific. Cite exact file paths, function names, and line numbers.
Do NOT pad findings — only report patterns with clear code evidence.
"""

# --- Prompt 3: Review, Validation & Remediation Guidance (Combined) ---
prompt_review_validate = """You are a senior security engineer performing final validation
and generating remediation guidance for OWASP & Django vulnerabilities in a Python/Django codebase.

You have a list of suspected findings from a prior analysis plan.

### File Search Strategy
- All file inspections must be relative to the repository root (`./` or `taskManager/`).
- Do NOT run broad glob searches on parent directories like `/workspace/nextgen` or root `/`.

### Validation & Remediation Steps
1. **Re-read the code** — Go back to the exact file and location cited. Read the full function/class.
2. **Trace the request path** — Follow the request from URL routing through middleware, view logic, and ORM query.
3. **Check for indirect protections** — Is there global middleware enforcing auth? Is the query scoped by `request.user`?
4. **Challenge the finding** — Ask: "Could an attacker actually exploit this?" Downgrade or dismiss if protected.
5. **Confirm or reject** — Mark each finding as CONFIRMED, DOWNGRADED, or FALSE_POSITIVE with an explanation.
6. **Fetch OWASP Remediation Guidance** — For EACH `CONFIRMED` finding, call the `get_owasp_cheatsheet` tool using its CWE ID or vulnerability category (e.g. `CWE-639`, `IDOR`, `CWE-862`, `CWE-89`, `CSRF`) to retrieve authoritative OWASP Cheat Sheet guidance.
7. **Generate Code Remediation Patch** — For EACH `CONFIRMED` finding, provide actionable remediation guidance and a production-ready Python/Django code patch directly inside the validated finding structure.

### Final Validation & Remediation Output Format (Required JSON)
Your final response MUST be in valid JSON format containing these required fields:
```json
{{
  "is_insecure": true,
  "reason": "Detailed summary explaining why the application is considered insecure or secure based on validated findings.",
  "validated_findings": [
    {{
      "finding_id": "FINDING-01",
      "cwe": "CWE-639",
      "title": "Insecure Direct Object Reference (IDOR) in Task Detail View",
      "status": "CONFIRMED | DOWNGRADED | FALSE_POSITIVE",
      "file": "path/to/file.py",
      "location": "function_name() line range",
      "severity": "critical | high | medium | low",
      "confidence": "high | medium | low",
      "evidence": "Exact code snippet or logic flaw",
      "exploit_scenario": "Step-by-step scenario an attacker would use to exploit this",
      "remediation_guidance": {{
        "owasp_guidance": "Authoritative guidance fetched from OWASP Cheat Sheet tool",
        "recommended_fix_description": "Explanation of the required security fix",
        "remediated_code_patch": "Python/Django code snippet showing the secure implementation"
      }}
    }}
  ],
  "overall_assessment": {{
    "total_confirmed": 0,
    "total_downgraded": 0,
    "total_false_positives": 0,
    "risk_rating": "critical | high | medium | low",
    "summary": "2-3 sentence overview of security posture"
  }}
}}
```

Note: For `DOWNGRADED` or `FALSE_POSITIVE` findings, set `"remediation_guidance": null`.
Be ruthless about false positives. A finding with no realistic exploit path is NOT a vulnerability.
"""


# ------------------------------------------------------------------------------
# Step Factory (follows audit.py LCEL pattern)
# ------------------------------------------------------------------------------
def new_step(name: str, system_prompt: str, extra_tools=None):
    step_tools = [FetchURLTool()]
    if extra_tools:
        step_tools.extend(extra_tools)

    agent = create_deep_agent(
        model=llm,
        tools=step_tools,
        backend=filesystem_backend,
        system_prompt=system_prompt,
        skills=[skills_dir],
    )

    def _run_step(input_text: str) -> str:
        print(f"\n[{name.upper()} STEP INPUT]\n", input_text)
        print(f"\n[{name.upper()}] Running (streaming)...")

        final_output = ""
        tool_calls_made = []

        try:
            for event in agent.stream(
                {"messages": [{"role": "user", "content": input_text}]}
            ):
                for key, value in event.items():
                    if "Middleware" in key:
                        continue
                    if isinstance(value, dict) and "messages" in value:
                        for msg in value["messages"]:
                            if hasattr(msg, "tool_calls") and msg.tool_calls:
                                for tc in msg.tool_calls:
                                    tool_calls_made.append(tc["name"])
                                    print(f"  -> {tc['name']}")
                            elif hasattr(msg, "content") and msg.content:
                                final_output = msg.content

        except Exception as e:
            error_type = type(e).__name__
            print(f"\n[{name.upper()}] ERROR: {error_type}")
            print(f"  Message: {str(e)[:200]}...")
            print(f"  Tools called before error: {tool_calls_made}")

            if not final_output:
                final_output = (
                    f"[TIMEOUT ERROR]\n"
                    f"The agent timed out before completing.\n"
                    f"Tools called: {', '.join(tool_calls_made) or 'none'}\n"
                )

        print(f"\n[{name.upper()} STEP RESULT]\n", final_output)

        steps_dir = os.path.join(SCRIPT_DIR, "steps")
        os.makedirs(steps_dir, exist_ok=True)
        with open(os.path.join(steps_dir, f"{name}.txt"), "w", encoding="utf-8") as fh:
            fh.write(final_output)

        # Also save JSON output directly to exercise-08 folder if step produces JSON
        if "```json" in final_output:
            try:
                parts = final_output.split("```json")
                json_content = parts[-1].split("```")[0].strip()
                json_file_path = os.path.join(SCRIPT_DIR, f"{name}.json")
                with open(json_file_path, "w", encoding="utf-8") as fh:
                    fh.write(json_content)
                print(f"  -> Saved {name}.json to exercise-08/")
            except Exception as e:
                print(f"  -> Failed to extract JSON for {name}: {e}")

        return final_output

    return RunnableLambda(_run_step)


# ------------------------------------------------------------------------------
# LCEL Chain — Context Collection | Analysis Plan | Review & Validation (with Remediation)
# ------------------------------------------------------------------------------
collect_step = new_step(name="collect_context", system_prompt=prompt_collect_context)
analyze_step = new_step(name="analysis_plan", system_prompt=prompt_analysis_plan)
validate_step = new_step(
    name="review_validate",
    system_prompt=prompt_review_validate,
    extra_tools=[OWASPCheatSheetTool()],
)

full_chain = (
    RunnableLambda(lambda task: task)
    | collect_step
    | analyze_step
    | validate_step
)


if __name__ == "__main__":
    print("DeepAgent SAST Demo — A01:2025 Broken Access Control")
    print("=" * 60)

    full_chain.invoke(
        "Explore the Python/Django codebase in `./` (such as `./taskManager/`) and collect a full access control inventory. "
        "Use targeted file searches for `.py` files inside `./` and avoid globbing parent workspace directories."
    )
