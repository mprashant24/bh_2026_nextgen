# Injection Review Checklist

## Input Validation

- [ ] Validate on both client and server
- [ ] Prefer allow-list (known good) patterns over block-listing dangerous keywords
- [ ] Input sanitized before DB/OS calls
- [ ] Dangerous keywords (e.g., `DROP`, `UNION`, `--`) blocked or neutralized where parameterization is not possible
- [ ] Control characters (e.g., null byte `\x00`, carriage return `\r`) stripped from input

## Injection-Specific Checks

### SQL Injection

- [ ] No raw SQL string concatenation or interpolation with user-supplied input
- [ ] Dynamic `WHERE`, `ORDER BY`, or `JOIN` clauses do not embed unsanitized values
- [ ] `.execute()`, `.raw()`, `.query()`, `Sequelize.literal()`, or `createNativeQuery()` calls reviewed — confirm any user data reaches these only via bind parameters, never via string building
- [ ] Stored procedures and views do not accept user input in dynamic SQL segments

### NoSQL Injection

- [ ] MongoDB / Mongoose: untrusted values not used to construct query shape (e.g., `{ $where: userInput }`, `{ [userField]: value }`)
- [ ] Query operators (`$gt`, `$ne`, `$regex`) cannot be injected by coercing a string field to an object
- [ ] JSON body parsing does not allow callers to supply nested operator objects where scalars are expected

### GraphQL Injection

- [ ] User-constructed query strings or fragments not executed without validation
- [ ] Query depth and complexity limits enforced to prevent resource exhaustion
- [ ] Resolver arguments validated before use in downstream DB or OS calls

### Command Injection

- [ ] No user input passed to shell commands, `child_process.exec`, `os.system`, `subprocess.run(shell=True)`, or equivalent
- [ ] Where shell invocation is required, use argument arrays (not shell strings) and explicit argument separation
- [ ] File paths derived from user input validated against an allowlist before passing to OS calls

### LDAP Injection

- [ ] User-supplied values in LDAP filters escaped with library-provided escaping functions
- [ ] No dynamic LDAP filter construction via string concatenation

### XML / XXE

- [ ] External entity processing disabled in XML parsers (`FEATURE_EXTERNAL_GENERAL_ENTITIES` = false, `resolve_entities=False`, etc.)
- [ ] `DOCTYPE` declarations rejected or stripped before parsing untrusted XML
- [ ] XPath queries do not embed unsanitized user input

### Template Injection

- [ ] Server-side templates (Jinja2, Twig, Nunjucks, Pebble, Freemarker) do not render user-controlled template strings
- [ ] Template auto-escaping enabled in all environments; explicit `| safe` / `| raw` / `autoescape off` usage audited
- [ ] No user input passed to `render_template_string()`, `Environment.from_string()`, or equivalent runtime template compilation

### Cross-Site Scripting (XSS) — Output Encoding

- [ ] All user-controlled values HTML-encoded before insertion into HTML context
- [ ] URL parameters encoded before insertion into `href`, `src`, or `action` attributes
- [ ] JSON output served with `Content-Type: application/json` — never injected into `<script>` blocks without explicit escaping
- [ ] `innerHTML`, `document.write`, `eval`, and `dangerouslySetInnerHTML` reviewed; confirm no unencoded user data reaches these sinks
- [ ] Content Security Policy (CSP) header set and does not contain `unsafe-inline` or `unsafe-eval` without compensating controls

### SSRF (Server-Side Request Forgery)

- [ ] URLs supplied by users not fetched directly by the server without validation
- [ ] Allowlist of permitted schemes (`https` only), hostnames, and ports enforced before outbound requests
- [ ] Internal metadata endpoints (169.254.169.254, 100.100.100.200, `localhost`, `0.0.0.0`) blocked at both application and network level
- [ ] DNS rebinding mitigations in place if allowlisting is based on hostname resolution

### Open Redirect

- [ ] `redirect_to`, `res.redirect()`, `HttpResponseRedirect()`, and similar calls validated against an allowlist of safe destinations
- [ ] Relative URLs and path-only redirects preferred over absolute URLs with user-supplied hostname
- [ ] Post-login and post-logout redirect parameters not freely user-controlled

## ORM Misuse

- [ ] No use of raw query builders (`.raw()`, `.query()`, `.extra()`, `Sequelize.literal()`, `createNativeQuery()`, `executeQuery()`)
- [ ] No input embedded into `JOIN` clauses or `WHERE` fragments dynamically (string concatenation or template literals)
- [ ] Unsafe default scopes reviewed — scopes that return a full record set without ownership filtering flagged
- [ ] Named scopes and query builders validated to confirm user-supplied arguments are bound, not interpolated

## Output Encoding Controls

- [ ] HTML encoding applied consistently — framework auto-escaping verified as enabled
- [ ] JSON responses use a serializer, not manual string construction
- [ ] Logging does not emit raw user input that could cause log injection via newline characters
- [ ] Email bodies and subjects encoded to prevent header injection

---

## Search Heuristics

Run these heuristics over the in-scope directories. For each hit, trace the value from its source to the sink and apply the calibration examples in `sqli-examples.md`.

### SQL injection

```
grep -rEn '\.raw\(|\.query\(|\.extra\(|Sequelize\.literal|createNativeQuery|execute\(' .
```

For every hit: confirm whether the argument is a string literal, a parameterized placeholder, or a concatenated/interpolated expression. Only concatenated/interpolated expressions with reachable user input are findings.

### Command injection

```
grep -rEn 'child_process|\.exec\(|os\.system|subprocess' .
```

For every hit: check whether the invocation uses an argument array (safe) or a shell string that includes user-supplied data (unsafe).

### Template / XSS unsafe output

```
grep -rEn '\| *safe' .
```

```
grep -rEn '\$\{.*\}' .
```

The first heuristic finds Nunjucks/Jinja `| safe` and similar filters that suppress escaping. The second finds JavaScript template literals — check whether the interpolated value is user-controlled and whether it flows into a DOM sink or a server-rendered page.

### Dangerous file operations and eval

```
grep -rEn 'eval|execFile|fs\.readFile\(req\.' .
```

For every hit: confirm whether the argument is a constant or derived from user input. `eval` on a constant is usually safe; `eval` on user-controlled input is a code injection finding.

### SSRF / open redirect

```
grep -rEn 'redirect_to|res\.redirect|HttpResponseRedirect|fetch\(|axios\.get\(|requests\.get\(|requests\.post\(' .
```

For every hit: follow the URL argument back to its source and confirm it is not user-controlled without validation.
