# Corpus browser fix: main journey passes in real Chromium

## Subject and change

The approved action `fix_corpus_browser_login` was applied to branch `titan/fix-corpus-browser-login`, based on the browser evidence branch and exact PR22 source. Commit `8462b1a63c52dc29465a2ec218ca730f424be0cf` changes one security setting: `SECURE_REFERRER_POLICY` from `no-referrer` to `same-origin`. CSRF middleware remains enabled. Literal `Origin: null` remains rejected. A causal regression was added: same-origin `Origin` without `Referer` passes the CSRF login, while null does not.

No merge, deployment, real accounts/data/email, lab event or unrelated PR changed.

## Local proof

In brain-env: `check` passed, migration drift check reported `No changes detected`, and 39 tests passed in 5.611 seconds. Application coverage is 93% excluding tests/migrations. The new regression passed. The code was tested from the exact fix commit, not from an uncommitted working tree.

## Connected real-browser proof

A connected Playwright browser running Chromium153.0.8010.12 tested the actual Gunicorn service bound temporarily to the measured internal build-container address. Synthetic fixtures only.

The browser now completed: login with POST302 and workspace200, search, exact-version read with the secondary/legal-validity warning, private reference save, private feedback with escaped `<script>` text, logout, stale-session replay403, `fixture-ben` isolation, mobile390x844 read with no horizontal overflow, password-recovery request, recovery confirmation, new password login, old password rejection, one-use reset-token rejection403, and withdrawal of an already-seen locator producing read403 and hiding the reference on the next request.

The browser service also returned a full-page screenshot for the real read state. No public service was left running as part of the test.

## Important distinction

The local Playwright harness still has a runtime-specific TargetClosed failure after it receives the fixed app's HTTP302/200 responses. The connected browser service is the instrument used for the completed checkpoints above. This is not hidden: both results are in the raw evidence JSON. The full Chromium channel also lacked `libcups`; the headless shell used an existing verified sysroot. No system package installation was performed.

The initial failure was real and remains in PR23 evidence. The fix does not trust null origins or disable CSRF. The browser regression now proves the exact interaction that caused the 403.

## Evidence

Raw receipt: `docs/agents/evidencia/2026-09-21-browser-fix.json`. It preserves the exact commit, local command/exit/count/coverage, and each connected-browser checkpoint. Historical failure receipt remains `docs/agents/evidencia/2026-09-21-browser-evidence.json` in PR23. The original application branch stays unchanged except for the approved fix branch.

## QA verdict

**Browser acceptance: PASS for the requested product journey and security boundaries measured here.** Remaining limits: no production deployment, no real accounts/mail, no load/10x measurement, and no independent human review. CI on the fix PR is still the final repository check; no merge is authorized.

--- METODO TITAN ---
Accion delicada: SI
Modo aplicado: TITAN FULL
Rubrica: 90/100 provisional before fix-PR CI; 0 N/A for product code
Review externo: PR23 evidence exists; new review pending
Instrumento: brain-env local suite + connected Chromium; raw checkpoint receipt committed
