# SQLite locks did not falsely report successful logout in the tested cases

18 September 2026, ART. Requested follow-up to the Astra handoff: test whether SQLite locks can falsely signal successful logout. No production changes, deployment, real accounts, or edits to product code.

## Verdict

**No false success reproduced.** With a real competing SQLite lock, the HTTP endpoint returned503, not200/logged_out. After releasing the lock, direct SQL showed revoked_at still NULL and the same session could still read (200). A fresh logout then returned200, persisted revoked_at1000, and the next read returned403. This distinction matters: **an error response means logout has not been confirmed; the tested session remained active.**

This includes the more subtle case where UPDATE executes but COMMIT fails: tracing observed UPDATE, COMMIT, ROLLBACK; HTTP reported503 and the revocation did not persist. Merely checking failure to acquire BEGIN would not cover that case.

## Exact subject and environment

Repository gatehot59-star/corpus-legal-tarija; frozen main `c19e4344367e3bc885dccfdf45e2c979caa1bb5c`. Product is unchanged from the integrated tree reviewed in `2026-09-18-06-brain-main-encargo-astra.md`. A new git archive was extracted into scratch. Tested `IsolatedSessionApp` in sistema/api/isolated_session.py, inherited dispatch guards in isolated_login.py and the actual access-policy/exact-reader path.

Environment: brain-env through the MUDH build gateway, Python recorded in evidence, SQLite3.46.1. Real HTTP via wsgiref loopback, separate SQLite connections, fictional identity, actual login-issued bearer, explicit SQL grant and a fixed Unicode/repetitive text oracle. No imported author test helpers. scrypt expected verifier was constructed directly. All own SQLite and HTTP connections closed explicitly; lock rollback/close and server shutdown/join in finally.

## Contract and measurements

For a known active fixture session with a successful pre-lock read, a lock that prevents persisting revocation must not yield successful logout. After the error, query the row rather than assuming whether it committed. Once the lock is released, the same endpoint must revoke successfully and deny the next read. The other session/unknown-token semantics are outside this focused test and were covered separately in the previous review.

Four lock situations were tested, with the COMMIT case repeated in a new temporary store:

1. **DELETE journal, competing BEGIN IMMEDIATE writer.** Dispatch can read the marker, logout cannot acquire its write transaction.503 LOGOUT_UNAVAILABLE after approximately1.010s; trace PRAGMA, SELECT, BEGIN. No UPDATE reached.
2. **DELETE journal, competing shared reader held across logout.** Another connection executes BEGIN and SELECT and keeps the transaction open. Logout can BEGIN IMMEDIATE and UPDATE but cannot acquire the exclusive lock needed for COMMIT.503 LOGOUT_UNAVAILABLE after1.006s; trace PRAGMA, SELECT, BEGIN, SELECT, UPDATE, COMMIT, ROLLBACK. This is a real commit-time failure, not an earlier dispatch failure.
3. **DELETE journal, competing BEGIN EXCLUSIVE.** The inherited isolation check itself cannot access the store.503 ISOLATION_UNAVAILABLE after1.006s; traced PRAGMA attempt, no logout UPDATE. This validates failure propagation at a different layer and is not labeled a commit failure.
4. **WAL journal, competing BEGIN IMMEDIATE writer.** Mode explicitly switched on the synthetic store and read back as wal.503 LOGOUT_UNAVAILABLE after1.006s; no UPDATE reached.
5. **Repeat of case2 in fresh scratch.** Same503, UPDATE→COMMIT→ROLLBACK, NULL revocation and successful retry. Approximately1.006s.

For EVERY case: login200; initial read200; revoked_atNULL; lock transaction active before and after the blocked request; no logged_out:true on failure; after releasing lock, revoked_atNULL and read200; retry logout200; revoked_at1000; read403; repeated logout200; candidate file hash unchanged; listener terminated. Clock fixed1000.8, session/grant valid throughout, so expiration did not explain denied access. Journal modes were queried, not assumed.

These are assertions within five scenario runs, not independent statistical samples or a general load test. The traced runs contain17,18,17,18,18 assertions respectively. The initial untraced five runs also passed and remain in the evidence. They are not counted as additional scenarios or new properties.

## Falsifier: can this instrument catch false success?

A separate copy changed only the error branch in session_route:

Original: `status, body = 503, {"error": "LOGOUT_UNAVAILABLE"}`

Mutant: `status, body = 200, {"logged_out": True, "environment": "isolated_test"}`

This deliberately lies after the same underlying lock/rollback, without changing the SQL. The shared-reader COMMIT test fails exactly `locked_logout_status`, `no_false_logged_out`, and `locked_error`; exit1. The baseline passes those same assertions. Both traced and untraced mutant runs reproduce the detection. Direct SQL and subsequent reads still show the session active after the failed transaction. No failure is attributed to imports, timeout or a preexisting red baseline.

Operation-name tracing was added in a second instrument, preserving the first. It observes SQLite callbacks but does not replace transaction semantics. Logs deliberately retain only the SQL operation keyword, never bound token values; UPDATE/COMMIT/ROLLBACK visibility establishes which phase was attempted, while persisted rows establish the result.

## Interpretation and remaining work

CONFIRMED within the tested environment: contention and commit-time busy failures do not become a successful HTTP logout, and retry after lock release succeeds. REFUTED for these cases: HTTP200/logged_out while the transaction rolled back. NO MEDIDO: arbitrary lock interleavings, release during the timeout window, heavy/concurrent HTTP load, filesystem/I/O failures, disk full, network filesystems, a killed process, machine restart, crash recovery, client UI behavior and production exposure.

No UI currently exists in this wrapper. A future client must not present503 as server-confirmed logout. Clearing its local token is a separate client action, not evidence that every copy of the bearer was revoked. This test does not implement retry UX or claim logout is available under sustained contention.

No new product defect was demonstrated, so no product fix or issue was created. The Astra handoff item about lock-induced false success is now measured for these four situations. The separate request to verify persistence in a NEW PROCESS remains untested here; recreating an app in the previous review was not that test.

## Evidence, reproduction and custody

Evidence file: `docs/auditorias/2026-09-18-07-logout-locks/evidencia.json`, evidence commit `fa578fc2d8142e6ad125dc81ff4d815849ab0195`.

190,533 original bytes, SHA256 `17809661c802995ad3199e02d302026f8104fab15bc1506a4586fd46bbc7f46f`. xz+base64 wrapper was fetched from the published commit, decompressed and compared against the local original: byte_identical true. No output was cut to fit transport.

The bundle contains complete executed instrument sources, the product session source, each full created JSON result, complete subprocess command/returncode/stdout/stderr, head and Python/SQLite versions, original and traced runs, and exact mutant edit. HTTP JSON bodies and response headers are retained; synthetic access_token fields replaced at capture by REDACTED_SYNTHETIC_BEARER. Request passwords and Authorization were not captured. SQL trace records operation keywords only, not full SQL or values. This is the explicit capture scope, not a claim of unredacted network traces.

Reproduction: recover the pinned git archive into repo; extract lock_probe_traced.py from the evidence files; run `python3 lock_probe_traced.py repo result.json writer`, replacing writer with commit_reader, exclusive or wal_writer. Each invocation creates and closes a new temporary fixture. Apply the exact mutant only to a copy, then run commit_reader and require the target assertions to change from pass to fail. No databases or bearer credentials are needed from the original run.

## Gates

Gate I PASSES for the properties tested: correct known active session, pre-lock positive, direct committed-state oracle, failure response, positive retry, targeted falsifier and fresh repetition of the decisive commit case. Gate II: scoped conclusions and exclusions above, not approval of production. Gate III: evidence published and verified; report and public ClickUp Doc plus Nexus continuity complete the delivery in this turn. Reconsult main after documentary publication and ensure no product delta.

Review, experimental verification and final checks are functions of this one operator, not multiple independent people. The expectation does not derive from product output. No production/VM/real accounts/grants modified, no merge/deployment or messages sent to another auditor. Historical pending publication of the earlier4,700,035-byte combined-auditor review is not resolved by this smaller new delivery.
