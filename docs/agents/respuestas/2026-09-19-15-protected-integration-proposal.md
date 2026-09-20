# Corpus: smallest protected integration proposal

19 September 2026, ART. **PROPOSAL ONLY.** Publication approved through `publish_protected_integration_proposal`, comment80170047134450. This approves Git and a public Doc, not implementation, assignment, merge, deployment or architectural adoption.

## 1. Outcome and selection criterion

A synthetic user signs in, finds a document they may access, reads its exact version, saves its reference and signs out. Add protected discovery to the existing PR18/19 flow rather than building another authentication system. This is the smallest next integration proposed among the inspected options, not a proven global minimum or completion of the real-pilot plan.

## 2. Verified baseline

Main: `ea56a7590e93db8342a95e63f74c0a816d478eee`. PR18: `2231ca8edbe4c0b6eba88156d5abd087bbf9e51f`. PR19: `31dff1ed1c066d4af8a3c6a1ac45e0e85d21eb05`, stacked on PR18. Both remain open. The proposed document path is absent from main and returned open-PR file listings.

[Audit and limitations](https://app.clickup.com/90171457413/docs/2kza6fw5-13537) · [PR18](https://github.com/gatehot59-star/corpus-legal-tarija/pull/18) · [PR19](https://github.com/gatehot59-star/corpus-legal-tarija/pull/19)

Existing evidence supports synthetic browser login, exact reading, logout and reference download. It does not prove protected search. Legacy v1 search/documents do not pass through the v2 authorization boundary and must not be mounted as a shortcut.

## 3. Proposed boundary

Use a separate, explicit opt-in, loopback-only test harness with a small synthetic collection, two synthetic identities and distinct grants. Preserve the existing fixed-fixture demo and its rejection of real data. Reuse the current session and access-policy contracts; no second permission model, real-account provisioning or production mode.

Propose an authenticated search adapter and a minimal browser query/results view. Results carry explicit UID/version locators into the exact reader. Search only authorized, non-withdrawn versioned documents. Authorization must precede ranking, pagination, counts and snippet generation: a denied document must not affect any returned field or ranking score. Avoid whole-corpus ranking statistics that incorporate denied documents. For this tiny fixture, deterministic authorized-subset matching is sufficient; production relevance and performance are not claimed.

Recheck access on every search request, every text page and immediately before reference download. Discovery never grants permission to read. Missing, invalid or unavailable authorization must fail closed; no partial results on authorization-store failure. Keep the existing browser-origin/Host protections, memory-only tokens and no-store behavior. Do not log bearer tokens or query text by default.

Render snippets as text, not HTML. A result links to the selected version, never silently to the current version. Preserve secondary-source, unofficial, legal-validity-not-measured and current-document-source-URL warnings. The browser change replaces the fixed locator only inside the separate harness, not by loosening the old launcher's guards.

## 4. Acceptance required before any integration claim

1. In an actual browser: login, query, select an allowed result, reconstruct exact paginated Unicode/CRLF text, download the metadata-only reference, then confirm logout.
2. A missing grant, wrong group, expired/revoked grant or session, disabled user/collection, and withdrawn document deny access as applicable. Include positive controls before each denial.
3. Add a forbidden matching document, then change its title/text. The caller's results, snippets, count, ordering and pagination remain unchanged. This checks response non-disclosure, not constant-time behavior.
4. Revoke after search and between reading pages: subsequent requests reject access and the UI clears protected pending content. Revoke before saving: no download. Previously delivered bytes cannot be recalled.
5. An authorization-store failure produces no results; hostile snippets remain inert text; version drift cannot substitute another document version.
6. A local mutant omitting authorization must fail the relevant disclosure assertion while the original passes. A version-pinning mutant must fail its version assertion. Preserve complete outputs and repeat with fresh fixtures.

## 5. Proposed work order and stopping rule

Before implementation, obtain separate approval of the exact changed-file set and base, recognizing PR19's dependency on PR18. Do not merge either PR under this publication approval.

Then propose three individually bounded units: synthetic harness/search contract; protected adapter plus browser wiring; adversarial tests, regression and evidence. Each unit has a maximum four-hour timebox, not a measured delivery estimate. Stop and re-scope if it requires a new auth model, framework adoption, real data, deployment or exceeds its bound. Security/workflow changes require the full review process and approved scope.

## 6. Exclusions and next decision

No real users or legal documents, signup/reset, feedback submission, server bookmarks, sharing, payments, production search engine, framework choice, TLS deployment, restore reopening or full pilot approval. This does not complete the plan's find/verify/save/report journey: reporting and operational recovery remain separate.

Before a real pilot, accept the exact sample, legal/privacy review, responsible people, permitted tasks/data and operating limits; verify the protected deployment and recovery. Unknown agreements remain PENDING. General SQLite fixture debt is not automatically a prerequisite.

Publication is the only action authorized here. No new tests were run: acceptance above is proposed, not measured. No instructions were sent to another executor.

--- METODO PROMETEO ---
Action: documentation publication only. Mode: LIGERO; no trust-boundary implementation or workflow modification. Machine: brain-env for read-only Git/PR checks. Runtime QA and new experimental evidence: N/A. External implementation review: pending. Git path: `docs/agents/respuestas/2026-09-19-15-protected-integration-proposal.md`. Public mirror: [Corpus proposal: protected discovery through versioned reading and saved reference](https://app.clickup.com/90171457413/docs/2kza6fw5-13557). Git publication and remote readback are checked before the final chat. Append-only documentation on main follows PROMETEO v6's explicit distinction from product code.
