# Smallest useful Corpus feature: read one document and keep its reference

## Recommendation

Build one local browser flow: **sign in, open a known document at an explicit version, read its exact text, and save a reference file**. Start from an operator-provided UID/version link and synthetic fixture, not a search screen. This is the smallest useful user-facing slice identified among the alternatives inspected, not a mathematically proven global minimum.

The user outcome is a reusable reference to what they actually read, without constructing API requests. It is an internal demo deliverable, not permission to sell legal access or publish real documents. Product demand remains untested.

## What already exists and what is missing

Inspected main b6c290bd5f24f6a93513c17569ced45a164b864a: README and complete web UI, legacy server, demo launcher, exact reader, version reader, access policy, login and logout modules.

**Find:** the old page calls `/api/v1/buscar`. Its server searches chunks and emits document text/snippets without the v2 authorization boundary. Reusing that endpoint would introduce a separate protected-search task; do not expose it as a shortcut. For this increment a known versioned locator replaces discovery, not a claim that search is complete.

**Verify:** the v2 reader already requires an explicit version, checks access on every page, verifies text integrity and returns provenance. Add a browser consumer that follows the returned page locators, never silently switches versions, and distinguishes partial from complete text.

**Save:** no save action appears in the complete inspected UI. Add a local reference download containing UID, version/text hash, source hash, observed source URL, its `current_document` scope, retrieval time and warnings. No bearer, password, private notes or document body. It is a reference, not a legal certificate or a server bookmark service. Reopening requires fresh authorization; an old reference never grants access.

**Report:** `/api/v1/revision` is a GET queue reader, not a submission endpoint. Defer user reports, case management and server-side persistence. They are not necessary to finish the read-and-reference job.

## Important constraints found in code

The demo serves the session app, not the historical web page. The launcher, login and logout reject Origin headers. Browser authentication therefore needs an explicit same-origin design and browser tests; adding an HTML file alone is insufficient. Preserve literal loopback Host checks, deny foreign/null origins and reject ambiguous requests. Do not strip Origin headers or generally relax the existing guard. Keep any browser mode explicitly opt-in and preserve the current default behavior.

The exact API reports `authority=secondary`, `oficial=False`, `legal_validity=NOT_MEASURED`. Its source URL is from the current document row, not the historical version ledger. The page and saved reference must retain those qualifications. A matching text hash is not proof of legal validity or historical source provenance. Do not reuse the old UI's blanket “official source” presentation.

## Proposed implementation boundary, not work already done

Add `sistema/web/lector_demo.html` and browser-flow tests; extend the opt-in demo composition and narrowly scoped Origin handling in `demo_aislada.py`, `isolated_login.py` and `isolated_session.py`, with regression tests. Update `sistema/DEMO-AISLADA.md`. Reuse `exact_http.py`, `version_text.py` and `access_policy.py` unchanged unless a concrete failing contract requires otherwise. No new framework, database schema, search endpoint, real account, live corpus or deployment.

Use a first implementation timebox of four hours to prove browser login/read/logout with the existing boundary. This is a timebox, not a measured estimate for the complete feature. If that cannot be demonstrated safely, stop with the specific blocker rather than broadening authentication architecture or calling the feature shipped.

## Acceptance: one complete job, with failure cases

1. A user opens the local page, signs in and opens the supplied UID/version without curl or manual token handling. Token stays in memory, never URL or persistent browser storage.
2. A synthetic document spanning several pages is reconstructed exactly, including Unicode and CRLF. The browser must use Unicode code-point offsets from the API, not JavaScript UTF-16 string length. A denied or missing page must not appear as a complete document.
3. The user downloads a reference with the exact version, both distinct hash fields and source-scope/validity warnings. No secret or body text is exported. The same approved version can be reopened after a later current-version change; an unavailable version fails explicitly.
4. Withdraw the grant between page requests: the next request is denied. The UI stops further reading and clears its displayed protected text/reference state; it cannot recall bytes already delivered or a file already saved.
5. Actual-browser same-origin login/read/logout succeeds, while foreign/null Origin and forged Host requests fail. Logout is confirmed before showing success; failed logout is not disguised as server-side revocation.
6. Existing functional tests remain passing, plus targeted negative controls that detect removed version pinning and relaxed Origin checks. A green legacy suite alone is not acceptance of the new browser flow.

## Priority correction

The criterion is the shortest path to a complete user outcome with minimal new authorization/storage surface. A CLI client is less UI work but does not test the intended nontechnical reader experience; a complete search/save/report workflow adds more boundaries than necessary.

My previous status note put the remaining SQLite fixture repairs first. Source inspection does not establish those repairs as a prerequisite for this feature: PR17 changes `tests/test_exact_http.py`, while the new increment uses already-integrated runtime modules and needs its own tests. Keep the repairs as test debt, not a blanket product blocker. Shared test-suite reliability must still be handled if it actually obstructs acceptance. PR17 and PR1 remain open; neither is merged or authorized here.

## Evidence, tools and limits

This is a source-based feature selection, not a runtime audit or a claim that the feature is ready. Gateway brain-env performed Git fetch/read/hash inspection; GitHub listed open PRs. No new tests, Actions, browser session, product edits, merge or deployment. No claim about all three machines' current capacity was needed.

Pinned evidence: [UI](https://github.com/gatehot59-star/corpus-legal-tarija/blob/b6c290bd5f24f6a93513c17569ced45a164b864a/sistema/web/index.html#L293), [legacy routes](https://github.com/gatehot59-star/corpus-legal-tarija/blob/b6c290bd5f24f6a93513c17569ced45a164b864a/sistema/api/servidor.py#L342), [demo guard](https://github.com/gatehot59-star/corpus-legal-tarija/blob/b6c290bd5f24f6a93513c17569ced45a164b864a/sistema/api/demo_aislada.py#L167), [login guard](https://github.com/gatehot59-star/corpus-legal-tarija/blob/b6c290bd5f24f6a93513c17569ced45a164b864a/sistema/api/isolated_login.py#L126), [version response](https://github.com/gatehot59-star/corpus-legal-tarija/blob/b6c290bd5f24f6a93513c17569ced45a164b864a/sistema/api/version_text.py#L59), [URL scope](https://github.com/gatehot59-star/corpus-legal-tarija/blob/b6c290bd5f24f6a93513c17569ced45a164b864a/sistema/api/exact_http.py#L108).

Verbatim source observations: `result["source_url_scope"] = "current_document"`; login rejects `environ.get("HTTP_ORIGIN")`; logout rejects `"HTTP_ORIGIN" in environ`. These immutable source files are the evidence, not new runtime measurements. Browser behavior, duration, usability and willingness to pay are NOT MEASURED.

Artifact: [2026-09-19-09-smallest-useful-feature.md](https://github.com/gatehot59-star/corpus-legal-tarija/blob/main/docs/agents/respuestas/2026-09-19-09-smallest-useful-feature.md). Documentation only; implementation requires a separate scoped action.

--- METODO PROMETEO ---
Machine: brain-env, read-only product inspection. Git: file linked above. Public ClickUp mirror, Space: [Corpus: ship a version-pinned reader and saved reference before search](https://app.clickup.com/90171457413/docs/2kza6fw5-13437). No implementation, merge or deployment authorization inferred.
