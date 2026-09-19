# Corpus browser authentication spike: implemented, not merged or deployed

## 1. Request and authorization

Implement the browser authentication spike without merging or deploying. Approved batch: nine repository files, one PR and one public ClickUp Doc, synthetic browser login -> protected read -> logout, preserved default guards and negative tests. Approval action approve_browser_auth_spike, comment 80170047132214. No search, reference export, real accounts/data, deployment or merge. PR1 and PR17 are excluded.

Conclusion: the bounded synthetic spike is implemented and locally measured. This is not production authentication, the complete read-and-save feature, legal approval or commercial validation.

Base: 1b5a4be2799dc576983099043fb016467bd08d7b. Tested code, verified byte-for-byte against Git: a603ef7dea17fb378f337f07eedab5937d88001b. Branch: titan/browser-auth-spike. [PR18](https://github.com/gatehot59-star/corpus-legal-tarija/pull/18) is open and unmerged at receipt preparation.

## 2. Tools, machine and boundaries

Execution: brain-env, via MUDH Gateway build/run. Actual CLI child processes, Python unittest, HTTPConnection, Node and actual Chromium through Playwright; sys.settrace collected child-process line execution. GitHub connector created the branch, pushed code, opened PR18 and was called to request Copilot review. ClickUp public Doc created in Space. No Kaggle runtime, deployment, system-wide apt installation or production database operation. Isolated npm/browser packages and privately extracted Debian libraries are test tooling outside the repository. Existing public-repository CI ran after PR creation; its workflow was not changed.

Repository and open-PR files were read before edits. PR17 changes tests/test_exact_http.py; PR1's full 32-file diff was inspected, not inferred from its title. Neither is incorporated. One operator worked sequentially; this is not independent human approval. Instruments and raw results are separate from this interpretation.

## 3. Behavior and measurements

### Runtime

Three runtime modules add explicit --browser-spike serving only the fixed fictional Ana identity and fixed fixture document. Existing initialization and default launcher behavior remain unchanged: without the new flag there is no browser page and Origin-bearing requests are rejected.

Browser mode derives the exact http://127.0.0.1:PORT Origin from the bound loopback port. Host is literal. State-changing requests require that exact Origin; GET allows no Origin or the exact value. Foreign, empty and opaque/null Origin and conflicting Sec-Fetch-Site values are rejected. Sensitive duplicate headers are detected before WSGI flattening; duplicate Host and Origin were exercised. No CORS, cookie, proxy or header-stripping shortcut was added.

The synthetic HTML collects no credentials. The fixture password is public test data, not a secret. The bearer stays in a JavaScript closure, not DOM, URL, cookies or persistent storage. Fixed-version text is paginated in 11 code points and displayed only after all pages complete. Withdrawal or malformed version clears/rejects partial text. Logout failure remains visibly unconfirmed and offers retry; successful logout must revoke on the server. Reload/pagehide forgets the UI token but is explicitly NOT server revocation. The page uses a hash-based inline CSP, no external assets, no-store, nosniff and anti-framing directives.

### Counts and instruments

118 Python tests passed: 7 browser-auth tests plus 111 existing cases (21 clean snapshot SOL, 15 exact HTTP, 15 access policy, 18 login guards, 10 isolated sessions, 18 isolated demo, 14 restore). Python compilation and Node syntax check passed. Full commands, exit codes, stdout and stderr are in the raw evidence.

Actual Chromium 153.0.8010.12 with Playwright 1.63.0 passed 19 named checkpoints: page_200, no_credential_inputs, anonymous_read_disabled, browser_login_200, real_browser_origin, exact_unicode_crlf, empty_persistent_storage, no_token_in_dom, no_token_in_url, mobile_no_horizontal_overflow, withdrawal_during_pagination_clears_text, wrong_version_not_displayed, failed_logout_retry_available, browser_logout_200, logout_clears_text, logout_disables_read, server_revocation_403, reload_forgets_ui_session, no_javascript_errors. An instrumented repeat passed. These are checkpoints, not 19 independent suites; repeat runs do not increase the independent count.

Two scratch-only mutants proved relevant red outcomes. Unconditional Origin acceptance failed 22 assertions in the negative-origin matrix, including HTTP 200 instead of 403. Suppressing the logout SQL update with WHERE 0 let the browser reach 16 prior successful checkpoints, then failed server_revocation_403. The product source was not mutated in the delivered branch.

Changed Python executable-line coverage: 69/72 = 95.83%. Diff-added/replaced lines were intersected with Python trace executable lines, then actual child-process traces were unioned. Misses: demo_aislada.py:210; isolated_login.py:102,129. All target/hit/miss sets and eight trace captures are preserved. This is NOT whole-project or JavaScript branch coverage.

npm audit of the isolated Playwright dependency tree reported zero advisories. Playwright 1.63.0 was checked against the live npm registry during implementation (https://registry.npmjs.org/playwright/latest); Chromium version was measured from the installed browser. This is not an OS/browser CVE certification.

PR18 check stable_identity, job 105985414607, completed successfully at 2026-09-19T23:25:49Z on code head a603ef7. [Job](https://github.com/gatehot59-star/corpus-legal-tarija/actions/runs/35476067576/job/105985414607). Existing CI DOES NOT execute the two new spike test files. Local browser results are not a claim of browser coverage in CI. Copilot review was requested through the connector, whose response had no content; acceptance is not independently confirmed. At the subsequent read, review threads were empty (totalCount 0, no next page). Silence is NOT approval; external review remains pending.

### Failures and corrections preserved

Initial source transport retained literal plus prefixes and failed before applying edits. The uniformly prefixed envelope was preserved and corrected before execution. A compressed HTML transfer was rejected before writing; the complete direct transfer replaced it. These transport failures are disclosed here, not claimed as separately captured full command transcripts.

The first real Chromium launch failed for missing shared libraries; first-runs.json retains stderr. Actual HOME was /workspace/homebrain, not /root. Debian libraries were downloaded/extracted into a private test sysroot, not installed on the host; the next real browser run passed. Initial outdated library URL returned 404 and was resolved using the live Debian pool. Full available tooling logs are included.

First branch publication bce237d6d908397b85ed38908c2e8564ed93d50b transcribed two isolated_session.py lines incorrectly. Seven-file remote comparison caught it. Corrective commit a603ef7 restores the tested ValueError and marker-or-disabled guard. All seven files subsequently matched the executed source byte-for-byte. Both publication readbacks are retained. No transient mistake reached main.

## 4. Raw evidence, separately from verdict

[Lossless evidence](../evidencia/2026-09-19-10-browser-auth-spike.json) is a JSON wrapper: encoding base64+zlib, uncompressed_bytes 76749, SHA-256 41793340be7cb689181e2bea05911e791a5901e08cd2017f6c33b4acc0c271f8. The payload preserves complete captured stdout/stderr and exit codes, positive and negative controls, browser and regression results, coverage run/summary, dependency audit, publication comparisons, supervisor/instrument source, eight trace files and available tooling logs. It is not a summary substituted for the raw output. PR review/status reads happened after this frozen test bundle and are recorded above, not falsely attributed to its payload.

Decode and verify from repository root:

```python
import base64, hashlib, json, pathlib, zlib
p = pathlib.Path('docs/agents/evidencia/2026-09-19-10-browser-auth-spike.json')
w = json.loads(p.read_text())
raw = zlib.decompress(base64.b64decode(w['payload'], validate=True))
assert len(raw) == w['uncompressed_bytes']
assert hashlib.sha256(raw).hexdigest() == w['sha256']
data = json.loads(raw)
```

Reproduce functional tests with `python3 tests/test_browser_auth.py`. Browser prerequisites and exact CLI commands are in [DEMO-AISLADA.md](../../../sistema/DEMO-AISLADA.md); the browser runner is `node tests/browser_auth.cjs` with NODE_PATH pointing to an external Playwright 1.63.0 installation and its browser/runtime libraries available. No dependency binaries are versioned.

## 5. Files and QA

The approved nine-file delta comprises:

1. sistema/api/demo_aislada.py
2. sistema/api/isolated_login.py
3. sistema/api/isolated_session.py
4. sistema/web/auth_spike.html
5. tests/test_browser_auth.py
6. tests/browser_auth.cjs
7. sistema/DEMO-AISLADA.md
8. docs/agents/respuestas/2026-09-19-10-browser-auth-spike.md
9. docs/agents/evidencia/2026-09-19-10-browser-auth-spike.json

This documentation commit adds the last two files. The preceding seven implementation/runbook files are at the verified code revision above. No generated database, token, PNG, browser binary or other compiled artifact is committed.

QA self-assessment, scoped to the synthetic spike: 80/85 applicable points = 94.12/100. Completeness 15/15: seven complete executed files and bounded runbook; execution 15/15: regression-runs.json and browser-run2.json; security 13/15: negative Origin/header cases, logout mutant and dependency-audit.json, minus unmeasured broader threat/browser scope; testing 14/15: 118 tests, two relevant mutants and coverage-summary.json, minus no JS branch metric/new CI gate; architecture 9/10: opt-in defaults, fixed synthetic flow and no application dependency, minus test-only hosting; documentation 10/10: runbook and this six-field receipt; process 4/5: raw evidence and remote parity, minus independent review still pending. N/A 15 points: deployment 10 explicitly prohibited, unsolicited innovation 5 excluded by the approved bounded spike. This score is not external approval or a merge decision.

## 6. NOT MEASURED and remaining work

Only Chromium was measured. No production readiness, TLS, load, crash/hot-backup guarantees, arbitrary real credentials, real corpus, legal validity, search, saved-reference export or commercial demand. Source URL metadata remains scoped to current_document, not historical provenance. Same-UID/root operator remains trusted. Screenshots were generated locally but no separate visual inspection is claimed. Test cleanup assertions ran; a comprehensive independent process scan was not performed. Existing SQLite fixture-close debt is not fixed here and is not asserted to block this browser experiment. External review acceptance/findings and the new tests in CI remain pending. No issues or agent messages were created.

Public mirror: [Corpus browser auth spike](https://app.clickup.com/90171457413/docs/2kza6fw5-13457), location Space. This branch-only receipt does not change the main project context or grant merge/deployment authority.

--- METODO PROMETEO ---
Accion delicada: SI, authentication boundary.
Modo aplicado: FULL.
Maquina: brain-env; existing public Actions check read separately.
Rubrica: 80/85 -> 94.12/100, self-assessment only.
N/A declarados: 15 (deployment 10 prohibited, unsolicited innovation 5 outside scope).
Review externo: requested through connector; empty response, acceptance unconfirmed; no review threads at read time, pending and not approval.
Instrumento: actual CLI/HTTP/unittest/Chromium, two target mutants and line tracing; exact commands, exits and raw output in the lossless evidence file.
Artefactos: https://github.com/gatehot59-star/corpus-legal-tarija/blob/titan/browser-auth-spike/docs/agents/respuestas/2026-09-19-10-browser-auth-spike.md + https://app.clickup.com/90171457413/docs/2kza6fw5-13457
No merge. No deployment.
