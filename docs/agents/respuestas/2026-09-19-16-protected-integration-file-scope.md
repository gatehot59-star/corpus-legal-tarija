# Protected integration: exact file scope before approval

19 September 2026 ART. Documentation only. Request: identify the exact files needed before approving implementation. No implementation, merge, deployment, workflow run or executor message is authorized by this identification.

## Baseline and outcome

Future branch `titan/protected-discovery` should start from PR19 head `31dff1ed1c066d4af8a3c6a1ac45e0e85d21eb05`, with PR base `titan/builder-saved-reference` while the stack is open. PR19 depends on PR18 head `2231ca8edbe4c0b6eba88156d5abd087bbf9e51f`. Revalidate heads before implementation; no merge or rebase now.

Outcome: synthetic login -> protected discovery -> explicit-version exact reading -> metadata-only saved reference -> logout. This extends the [proposal](https://app.clickup.com/90171457413/docs/2kza6fw5-13557), not the real-pilot approval. Full readable scope: [public Doc](https://app.clickup.com/90171457413/docs/2kza6fw5-13577).

## Exact implementation-delivery boundary: 10 files

1. NEW `sistema/api/protected_search.py`: bounded authenticated search adapter plus guarded session composition. Proposed GET /api/v2/buscar dispatched after inherited guards; other routes delegate to existing session behavior. Reuse SQLiteAccessPolicy per UID/version without copying its grant SQL. Authenticate even for an empty catalog. Read text, compute snippets, counts, order and pagination only from authorized versions. Policy errors discard the whole response. No legacy search or global ranking statistics influenced by denied documents.
2. NEW `sistema/api/demo_discovery.py`: explicit opt-in synthetic initializer, validator and loopback server. Own fixed multi-document manifest/identity marker, exclusive private directory, no arbitrary DB import. Two fixture identities, distinct grants and at least two server-configured collection scopes. Reuse safe unchanged path/HTTP helpers, not the old single-document initializer/validator. Preserve Host/Origin/duplicate-header/CSP/no-store/shutdown and non-overwrite protections. Generate fixtures, never commit databases; candidate catalog exposes only UID/version internally, not protected titles before authorization.
3. NEW `sistema/web/discovery_spike.html`: separate minimal query/results page adapting the audited PR19 reading/reference consumer to selected explicit UID/version. Preserve metadata allowlist, separate hashes and source/legal warnings, memory-only token, text-only snippet rendering and denial clearing. Do not change the old auth_spike.html or embed the protected catalog in public HTML.
4. NEW `tests/test_protected_search.py`: contract/authorization/query-bound tests with independently fixed expectations. Include empty-catalog authentication, wrong group/collection, disabled/expired/revoked access, withdrawal, policy errors, version pinning, authorized-only counts/order/pagination, and forbidden-document perturbations. Repeatable local mutants skipping authorization and version pinning must fail the relevant assertion while the baseline passes. Never mutate committed production sources.
5. NEW `tests/test_demo_discovery.py`: actual CLI/loopback HTTP tests for exclusive synthetic init, manifest/file safety, unchanged old-demo rejection, origin/Host/duplicate headers, isolation marker removal, real login/logout and process closure. No external listener or real users/data.
6. NEW `tests/browser_discovery.cjs`: actual Chromium flow for both identities, forbidden matching document, exact Unicode/CRLF pagination, real JSON download, logout, revocation after results/between pages/before save, inert hostile snippets, cross-identity isolation and clearing. Reuse external Playwright tools, no new dependency tree.
7. MODIFY `.github/workflows/clean-snapshot.yml`: add relevant paths, compile/run the two Python banks, run browser_discovery.cjs in the existing isolated Playwright step. Preserve all old banks, checkout pin, contents:read, dependency pin and current job timeout unless measured evidence leads to separately reviewed scope. PR18 already edits this file and PR19 inherits it: use the PR19 version, not older main. No second workflow.
8. NEW `sistema/DEMO-DISCOVERY.md`: actual init/serve/test commands, fixture/route/response limits, rejections, source caveats and shutdown/cleanup instructions. Clearly synthetic and separate from original demo and production. Commands must match code actually delivered.
9. NEW `docs/agents/respuestas/2026-09-19-17-protected-discovery-implementation.md`: future authorized-scope/code/test/failure/limitations receipt and public Doc link. Proposed output only, no claim it exists or passed. If date changes or path is occupied, re-list before approval, never overwrite.
10. NEW `docs/agents/evidencia/2026-09-19-17-protected-discovery.json`: complete future commands, fixtures/instruments/mutants, stdout/stderr/exits, hashes and CI observations. Text or reversible encoding, no databases, screenshot binaries, bearer or credentials. Remote decode/hash/byte verification before closure. Same path-collision rule as receipt.

Nine new files and one modified existing file. This scope note and its public Doc are NOT members of the future ten-file implementation delivery.

## Why no existing authentication files need editing

The actual IsolatedLoginApp.__call__ applies loopback/opt-in, browser and fixture-marker checks before dispatching through self.reader. IsolatedSessionApp sets that dispatch to session_route, which handles logout and otherwise delegates to its exact reader. A new composition can override session_route for search and call super for existing behavior. No bypassing inherited __call__, private-reader monkey-patch or new grant model is needed by this design.

The fixed demo validates exactly one UID/version/body. It is inappropriate to remove that check to support search. A separate harness owns its manifest and validates its multi-document fixture. The new page adapts the current hard-coded UID/version checks; they must not simply be deleted. All pages/reference metadata must still agree with the selected immutable locator.

The current policy binds a configured collection and document membership is collection-scoped. Two users in the same collection alone do not establish different per-document visibility. Use two fixed server-configured scopes and existing policy instances, never blindly trust a collection supplied by the client. Explicit scope/reader routing stays in the new composition and wrong-collection tests. No authorization-schema change.

A per-document callback cannot authenticate an empty candidate set. Define session eligibility and authenticated-empty versus rejected identity in the new adapter using the existing store semantics, while keeping SQLiteAccessPolicy authoritative for each document. Add drift tests against reader outcomes rather than inventing a second grant decision.

## Explicit no-touch list

Keep `sistema/api/access_policy.py`, `isolated_login.py`, `isolated_session.py`, `exact_http.py`, `version_text.py`, `demo_aislada.py`, `demo_restore.py`, `servidor.py`, `sistema/web/index.html`, `sistema/web/auth_spike.html`, existing tests, production schema, dependency declarations and deployment configuration unchanged. Imports are not permission to edit. PR1/17/18/19 are not changed or merged by this scope.

If the composition cannot preserve inherited guards, multi-scope routing requires a core edit, or another file becomes necessary, stop and revise the exact list before writing. Ten is a scope boundary, not permission to hide problems inside new files.

## Acceptance and limits

The proposal's complete acceptance remains binding: actual browser outcome, denied-document perturbation leaves result/count/order/pagination unchanged, every read/save reauthorizes, causal mutants fail specific assertions, fresh-fixture repeat, existing regressions pass. Search permission never grants subsequent reading. Old already-delivered bytes/downloads cannot be recalled.

Define exact query/page/fixture numeric bounds and error semantics before code; reject malformed or duplicate fields. Point-in-time authorization does not claim atomic revocation across a whole response or constant-time behavior. Production relevance, performance, legal validity, operational recovery and real pilot readiness remain out of scope.

## Inspection and closure

Read pinned login/session, fixed launcher, exact HTTP and complete workflow sources. PR19 API still reports open at the exact head above. Checked proposed code/runbook paths and this scope path absent from main. Returned open-PR file listings intersect only the existing workflow in PR18, inherited by PR19; PR1/17/19 add no intersection. Recheck future receipt/evidence availability before writing them.

Initial local remote-tracking-name lookup failed after fetch because that tracking ref was absent. Reading the exact commit and verifying the head with the GitHub API succeeded; not a capability limit or product error. No new runtime tests or CI were run. This is a source-supported implementation boundary, not a measured implementation or time estimate.

Publish this note and public Doc only. Eventual ten-file implementation requires explicit approval, FULL security/QA for the new trust boundary/workflow, and evidence of actual execution. No implementation approval is inferred here.

--- METODO PROMETEO ---
Action delicate: NO for this documentation-only publication; future boundary/workflow implementation is FULL. Mode: LIGERO. Machine: brain-env, read-only Git/GitHub inspection. Runtime QA: N/A; new testing results: NOT MEASURED. External implementation review: pending. Git: docs/agents/respuestas/2026-09-19-16-protected-integration-file-scope.md. Public Doc: https://app.clickup.com/90171457413/docs/2kza6fw5-13577. Append-only main documentation follows PROMETEO v6 distinction from product code; no product writes.
