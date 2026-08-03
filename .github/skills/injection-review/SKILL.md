---
name: injection-review
description: Use to review code for injection flaws via input validation and output encoding — SQL injection, NoSQL injection, cross-site scripting (XSS), command/LDAP/XML/template injection, SSRF, and open redirect — by tracing untrusted data sources to dangerous sinks. Use standalone or within a secure code review. Uses calibration examples to avoid false positives on parameterized queries and unrelated code.
---

## Purpose

This domain review traces untrusted input from every reachable source to every dangerous sink and confirms whether sanitization, parameterization, or encoding is present at each boundary. Confirmed findings are written to the **Findings In Progress** section of `REVIEW-NOTES.md`.

Load `references/checklist.md` and `references/sqli-examples.md` at the start of the review.

---

## Step 1 — Establish Scope

**When invoked by the `secure-code-review` orchestrator:**
The Application Map is already populated in `REVIEW-NOTES.md`. Read the `Application Map / Routes` section to obtain entry points before proceeding.

**When invoked standalone:**
Enumerate scope yourself:

1. Identify the framework from `package.json`, `Gemfile`, `requirements.txt`, `pom.xml`, or `*.csproj`.
2. Locate entry points: HTTP route handlers, GraphQL resolvers, WebSocket message handlers, CLI argument parsers, job/queue consumers.
3. Locate data stores and OS interfaces: DB drivers, ORM configuration files, shell-exec wrappers, template engine setup, HTTP client configuration.

---

## Step 2 — Build Source and Sink Lists

**Sources** (untrusted input origins):
- HTTP request parameters, headers, body, cookies, multipart fields
- Environment variables read from client-supplied data
- External API responses incorporated without validation
- Database values that were originally user-supplied
- File contents uploaded by users

**Sinks** (dangerous destinations):
- Database queries: raw SQL, ORM raw methods, NoSQL query objects
- OS calls: `exec`, `spawn`, `system`, shell strings
- Template rendering: `render_template_string`, `Environment.from_string`, `{{ var | safe }}`
- HTML output: `innerHTML`, `dangerouslySetInnerHTML`, `document.write`
- Outbound HTTP: `fetch`, `axios`, `requests.get` with a URL parameter
- Redirect targets: `redirect_to`, `res.redirect`, `HttpResponseRedirect`
- Log output: any logger call that interpolates user input without encoding
- Filesystem: `readFile`, `open`, `unlink` with a path derived from user input

---

## Step 3 — Run Search Heuristics

Run the heuristics from `references/checklist.md` over the in-scope directories. At minimum:

```
grep -rEn '\.raw\(|\.query\(|\.extra\(|Sequelize\.literal|createNativeQuery|execute\(' .
grep -rEn 'child_process|\.exec\(|os\.system|subprocess' .
grep -rEn '\| *safe' .
grep -rEn '\$\{.*\}' .
grep -rEn 'eval|execFile|fs\.readFile\(req\.' .
```

For each hit, open the file, identify the source of the value passed to the sink, and trace backward to confirm whether user input can reach it.

---

## Step 4 — Trace Each Source to Each Sink

For every source–sink pair identified:

1. Follow the data flow from the entry point through any intermediate functions, validators, or transformations.
2. Apply the calibration examples in `references/sqli-examples.md` before flagging SQL-related patterns:
   - Parameterized / bound queries are NOT findings — do not flag.
   - String concatenation or `%s` formatting into a SQL string IS a finding.
   - Command injection and form field declarations are NOT SQLi — classify correctly.
3. Confirm the path is reachable: is the route accessible? Is the input actually propagated to the sink, or is it discarded before reaching it?
4. Confirm the input is unsanitized at the point it reaches the sink: no encode/escape/parameterize call between source and sink.

Only flag a finding when both conditions hold: **reachable** and **unsanitized**.

---

## Step 5 — Check ORM Misuse and Template Auto-escaping

**ORM misuse:**
- Search for `.raw()`, `.query()`, `.extra()`, `Sequelize.literal()`, `createNativeQuery()` calls.
- For each, confirm the argument is a string literal (safe) or contains user data (flag).
- Check `JOIN` and `WHERE` fragment builders for dynamic string construction.
- Review default scopes — a scope returning all rows without ownership filtering is a data exposure risk, not an injection finding; note it separately.

**Template auto-escaping:**
- Confirm auto-escaping is enabled in the template engine configuration (Jinja2 `autoescape=True`, Nunjucks `autoescape: true`, etc.).
- Search for explicit `| safe`, `| raw`, or `autoescape off` usage; each instance requires a justification that the value is static or pre-encoded.

---

## Step 6 — Evaluate Mitigating Controls Before Recording a Finding

Before writing a finding, confirm:

- [ ] Is a WAF, input-filtering middleware, or prepared-statement wrapper applied upstream that prevents the payload from reaching the sink?
- [ ] Is the vulnerable code path reachable only by authenticated administrators with no user-controlled input?
- [ ] Is output encoding applied at the framework level (e.g., ORM always parameterizes) even if the call site looks unsafe?

If a mitigating control is present, note it alongside the finding rather than dropping it silently — controls can be misconfigured or removed.

---

## Step 7 — Record Findings in REVIEW-NOTES.md

For each confirmed finding, add an entry under **Findings In Progress** in `REVIEW-NOTES.md`:

```
### [Injection] <Short label>
- **Type:** SQL injection / NoSQL injection / Command injection / Template injection /
             XSS / SSRF / Open redirect / LDAP injection / XXE / (other)
- **Location:** `path/to/file.ext:LINE` — `function_or_route`
- **Source → Sink:** <input origin> → <dangerous call>
- **Mitigating controls:** <none observed> OR <describe control and why insufficient>
- **Evidence:** <grep output, code snippet, or line reference>
```

Record immediately when a finding is confirmed — do not batch until the end of the review.

---

## Completion Criteria

Before marking this domain review complete:

- [ ] Source list and sink list built; all heuristics run.
- [ ] Every source–sink pair traced; calibration examples applied for SQL patterns.
- [ ] ORM raw-query calls reviewed.
- [ ] Template auto-escaping configuration verified.
- [ ] All confirmed findings recorded in `REVIEW-NOTES.md` → Findings In Progress with source→sink path.
- [ ] No finding recorded without confirming the path is reachable and unsanitized.

If invoked by the orchestrator, return to `secure-code-review` to continue with the next domain review or Phase 6 (report-findings).

---

## Reference Files

- `references/checklist.md` — Full injection checklist: input validation, SQLi, NoSQLi, GraphQL, command, LDAP, XML/XXE, template injection, XSS, SSRF, open redirect, ORM misuse, output encoding, and search heuristics.
- `references/sqli-examples.md` — SQL injection calibration examples: vulnerable (string interpolation), safe (parameterized), and non-findings (command injection, form field declaration).
