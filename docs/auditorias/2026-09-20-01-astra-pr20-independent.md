# PR20: independent tests pass for isolation; failed logout loses its retry

20 September 2026 ART. User requested independent audit, no merge/deployment. Subject PR20 head a8aeb301f8840caa547e48730a46e1b9406927bc, base PR19 31dff1ed1c066d4af8a3c6a1ac45e0e85d21eb05. Both the subject and its base are exact, not main. I authored earlier browser work and the search proposal: this is not total personal independence. New expectations and instruments here are separate from Brain's test implementation.

## Verdict: changes requested, not merge approval

One reproduced functional/session-lifecycle regression in the new browser page. No cross-collection disclosure was demonstrated by the scoped independent tests. Correct the failed-logout retry before treating this browser flow as ready to integrate. No product, PR, workflow or deployment was changed during this audit.

## H1 CONFIRMED: a403 during logout discards the bearer but promises a retry

Location: sistema/web/discovery_spike.html, request(), action() catch and controls(). request() sets token empty for EVERY403, including logout. The catch tells the user: Cierre NO confirmado. Reintentá Cerrar sesión. controls() then disables logout because the token is gone.

Reproduction, actual Chromium and real HTTP, no mocked response:
1. Start a fresh synthetic CLI fixture and log in as Ana through the page. Browser login200 and a request using that issued bearer search200 establish the positive.
2. In the auditor-owned fixture only, delete login_environment's marker. Click Cerrar sesión. The inherited dispatcher returns403, before persistent revocation.
3. The page says to retry but the logout button is disabled.
4. Restore the marker. The SAME ORIGINAL bearer still obtains search200; the page can no longer retry its logout. Creating another session would not revoke the first one.
5. Auditor explicitly revokes that bearer through the real logout endpoint before stopping the test. Bearer never printed or persisted.

Two fresh fixture runs reproduced the same result. Positive fault control: rename the marker table to make the inherited guard return503 instead; the same instrument observes retry enabled, restores the table, clicks retry, and verifies original bearer search403. Thus the failure is not a broken browser button or inability to revoke sessions generally. PR19's earlier request helper did not clear the token on errors: the broad403 clearing is new in PR20.

Impact: medium functional/session-lifecycle defect, not a remote authorization bypass or a claim of false logout success. A valid session can outlive the UI's ability to revoke it until its existing expiry or trusted-operator action. Preconditions include an actual early403 without completed logout; the demonstrated cause is trusted local fixture-marker intervention. The UI correctly says closure is unconfirmed, but its promised recovery is impossible. General search403 fresh-login policy does not require losing the only revocation handle during failed logout.

Correction recommendation only: distinguish access-denial handling from unconfirmed logout; preserve a safe retry path for the original session while clearing displayed protected data. Add actual-browser403 early-guard and503 controls, assert retry availability and subsequent original-bearer rejection after confirmed revocation. Any correction belongs in a separately authorized product change, not this audit.

## Independent HTTP bank:38 checks pass, repeated; causal mutant fails

New audit_wire.py uses actual CLI login and raw TCP HTTP, not imported author test fixtures or direct policy-only calls. Fixed expected visible IDs are independent literals. Positive and fresh-archive repeat each pass38assertions; servers exit0, listeners verified closed. No repeat is counted as a new unique case.

Covered both identities' isolated results; original bearer read allowed versus other identity denied; corrupted forbidden document ignored for Ana but produces SEARCH_UNAVAILABLE for authorized Ben; disabled user, membership, collection, revoked grant, expired session and withdrawn documents rejected consistently by search and reader; valid controls before each intervention; duplicate-decoded query keys, invalidUTF8 and2048/2049raw limits; raw HEAD method405, missing-marker403 and missing-table503 with no body/Content-Length/Transfer-Encoding and required search headers.

Falsifier in a fresh test archive only: replace the allowed-list condition `if self.policies[c.collection](environ, c.uid, c.version) is True]` with `if True]`. Actual logins and search200 still pass; `ana_isolated_ids` fails because other-collection IDs appear. Exact assertion and output preserved. No mutant committed as product.

## Author baseline and custody

Reexecuted the new author banks:15Python adapter tests +7CLI/wire tests, and18Chromium checkpoints, all exit0. Those are baseline tests, not independent cases. Did NOT rerun all140Python or37legacy browser checkpoints. Author-bank raw reruns remain in the full local capture, not the focused Git evidence; the independently reproduced finding does not rely on those counts.

Strictly decoded Brain's Git evidence at the subject head:68208bytes SHA256ab06e374c2a8d4303e98e7b20bde4f8d278ed45b126d686dd53861c844841112, matching its wrapper. Final PR readback: open, mergedfalse, same head. CI job106005274126 reports success for that head; this is status metadata, not a new remote-log test count. Delta fromPR19 is the declared10files; inherited authentication/policy core unchanged.

## Inconclusive exploration, excluded from findings

Tried to test native input maxlength versus valid astral queries. The browser keyboard/fill experiment failed its ASCII/clear positive control: input remained derecho even after requested clearing. Therefore NO claim that the UI truncates queries is made here. Both attempted observations and scripts are retained in the full local capture; they are explicitly outside the focused published finding evidence. Their supervisor exit0 was data collection, not a passing assertion. No product change was made to accommodate the instrument.

Preparation corrections before first execution: counted q= bytes correctly for raw-query boundary inputs; repaired nested JS quoting before node syntax check. No experimental failures discarded. Browser exploratory scripts deliberately report observations: exit0 means collection completed, never that retry passed. The403finding has retry_enabledfalse and original-session200 in both records.

## Evidence, limits and gates

Published focused evidence: docs/agents/evidencia/2026-09-20-01-astra-pr20-independent.json, xz+base64,34024decodedbytes SHA25637f7d27f4bda6aebc14737f579c9866aac48e201db61e337e3d31d51c612cff0. Includes complete independent wire/browsers runs relevant toH1, repeats, failed mutant, both executed instruments, commands/environment and scoped process scan. No independent finding run is shortened. Excluded author reruns/CI response and invalid keyboard experiments are identified above, not represented as a complete whole-turn archive. Full local capture47733bytes SHA25685caa6f13f9bbba85c63223d4425203e70199bce50d079d79a399d45e9a5bc29 remains at /workspace/astra-pr20-ggkem0rb/evidence-raw.json.

GateI: scoped HTTP instrument discriminates positive versus causal mutant; browserH1 has actual positive login and503recovery plus repeat403. Browser failure investigation is not an all-green bank. Servers/listeners closed; scoped /proc scan found no own CLI/Python runners. Not a total host process inventory.
GateII: one confirmed functional defect, successful isolation cases and invalid instrument exploration separated. No external-person review or security certification claimed.
GateIII: Git recovery, strict decode/byte comparison, public Doc readback and Nexus recorded before final chat. No auto-approval from CI.

NOT MEASURED: complete authentication/Origin matrix, all query boundaries, concurrency/atomic revocation, timing channels, browser compatibility, accessibility, dependency CVEs, production/TLS, real legal data, utility or pilot readiness. Existing tests/CI cannot close those claims.

--- METODO PROMETEO ---
Bounded independent-instrument audit on brain-env. Synthetic owned fixtures only. Product role unchanged; no fix, merge, deployment, new agents, comments or assignments. Archive /workspace/astra-pr20-ggkem0rb. Main documentation only; report plus focused raw evidence, public Doc and Nexus continuity.
