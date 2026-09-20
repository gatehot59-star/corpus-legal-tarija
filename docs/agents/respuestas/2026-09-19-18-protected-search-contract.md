# Protected search: exact limits and rejection contract

19 September 2026 ART. **Amended in place after review19, 22:30 ART work session.** Specification only, not an implemented/tested endpoint or permission to implement. Refines ten-file scope16 and proposal15. PR19 baseline:31dff1ed1c066d4af8a3c6a1ac45e0e85d21eb05. Existing login/logout/exact-reader responses remain unchanged. [Public contract](https://app.clickup.com/90171457413/docs/2kza6fw5-13597). Amendment receipt: `docs/agents/respuestas/2026-09-19-21-auditores-contrato-corregido.md`.

## Request

Exact GET /api/v2/buscar, no trailing-slash alias. Single Authorization header with existing case-sensitive Bearer syntax; no tokens in query, cookies or body.

- Raw query string cap2048bytes before percent decoding, excluding question mark. Raw non-ASCII target bytes must be percent-encoded.
- Exactly q(required), offset(optional), limit(optional), each at most once; max3fields. Reject unknown names, duplicate decoded names, empty segments, malformed escapes. Strict UTF-8 percent decoding; plus means space; no replacement decoding or second decoding.
- q:1..128Unicode code points AND <=256UTF-8bytes after transport decoding, before normalization. Reject empty, whitespace-only or any Unicode Cc control. Preserve spaces; no trimming/collapsing. NFC then casefold literal substring matching against similarly normalized exact-version text. No regex/wildcards/SQL/stemming. Displayed source remains exact, not normalized.
- offset default0, ASCII decimal regex0|[1-9][0-9]?, range0..8.
- limit default5, ASCII decimal regex[1-5], range1..5.
- No numeric signs, leading zeroes, fractions, exponents or whitespace. No collection/version/sort/cursor/projection parameters.
- Body absent or Content-Length exactly0; any other length or any Transfer-Encoding rejected. Duplicate sensitive headers rejected before WSGI flattening.

## Synthetic resource bounds

Exactly2fixture identities and2server-configured collection scopes. At most8configured UID/version candidates overall; exactly one selected search version per UID. Exact-version text <=4096Unicode code points AND <=16384UTF-8bytes per document. Separate candidate/policy files, each <=1MiB at preflight, with the existing regular/private-file protections. Reject unsafe/mismatched fixtures before binding, never truncate/import real data. Runtime oversized authorized text fails the whole response.

Single synchronous loopback request, no worker pool/background index. Reuse2s socket inactivity timeout and1s SQLite lock wait. Neither is an end-to-end deadline/performance promise. No new search rate limiter; original login budget unchanged. Fixed bounds are design choices, not measured capacity.

## Validation order

1. Transport/harness guards first: loopback, exact Host/Origin/Fetch Metadata, sensitive-header duplicates. Preserve inherited opt-in/isolation-marker checks. Unknown routes delegate to existing app; no v1 fallback. The search-only response boundary below must also cover early rejection paths, including harness failures before application dispatch.
2. Exact search route: method, body framing, raw length, query syntax, field/value bounds. First error wins. Value checks q then offset then limit. No candidate content lookup.
3. Authenticate bearer/session/user using existing store semantics, enabled user, unrevoked session, valid_from<=now<valid_until. Nonfinite/invalid clock or DB failure is unavailable. Empty catalog must not skip authentication.
4. Decide each configured UID/version with existing SQLiteAccessPolicy and fixed server-configured scope. Only literalTrue permits reading. Do not copy grant SQL or trust a client collection. Any policy exception discards all results and returns503, including after an earlier allowed decision. Complete authorization decisions before matching content.
5. Zero authorized candidates returns generic403 ACCESS_DENIED, including valid session plus empty catalog/all withdrawn. Do not disclose which reason. At least one authorized document but zero matches returns200 empty. This clarifies the earlier unspecified authenticated-empty case; it does not issue grants.
6. Integrity-check/read authorized explicit versions only; then match, order, count, paginate and generate previews. No denied title/content, existence diagnostic or global ranking statistic. No implicit current-version fallback. Every later read/save reauthorizes separately.

This is point-in-time authorization, not atomic revocation across a response, constant-time behavior or recall of previously delivered bytes.

## Success response

200 JSON exactly7top-level keys: schema, environment, total, offset, limit, next_offset, results. schema=corpus-search-v1, environment=isolated_test. total counts authorized matching configured versions before pagination, not corpus size. Deterministic ASCII UID ascending then hex version ascending, no relevance score. next_offset=offset+returned_count only if more matches remain, otherwise null. offset>=total returns empty/null, not416.

Each result exactly8keys: uid,version,title,snippet,authority,oficial,legal_validity,source_url_scope. authority=secondary,oficial=false,legal_validity=NOT_MEASURED,source_url_scope=current_document. UID/version are the exact reader locator. No source hash/URL in search; verify these through reading/reference.

Title is a preview label, not legal metadata: first nonempty exact-text line up to80codepoints; fallbackUID. Snippet first160codepoints of exact text, no ellipsis/highlight HTML. Avoid casefold-offset mapping. Render both as textContent. Matching normalized text never rewrites the exact text.

Compact UTF-8 JSON with ensure_ascii=false. Full serialized body cap16384bytes, errors included; buffer before headers, never truncate. Overflow returns503 RESPONSE_LIMIT_EXCEEDED. Default no-match example:

{"schema":"corpus-search-v1","environment":"isolated_test","total":0,"offset":0,"limit":5,"next_offset":null,"results":[]}

## Exact new-route errors

For methods other than HEAD, rejection JSON has exactly one member: {"error":"CODE"}, without query/UID/token/path/SQL/exception details/count/partial data. HEAD has the explicit no-content exception below, regardless of the selected status.

- 405 METHOD_NOT_ALLOWED: any non-GET including HEAD/OPTIONS when method validation is reached; Allow:GET. HEAD has no response content.
- 400 EMPTY_REQUEST_REQUIRED: disallowed Content-Length or any Transfer-Encoding after outer guard precedence.
- 414 QUERY_TOO_LONG: raw query >2048bytes.
- 400 INVALID_QUERY: malformed transport encoding/UTF-8/percent, raw non-ASCII, separators, duplicate/unknown fields, >3fields, missing/invalidq, invalidoffset/limit. One code for all field failures.
- 403 ACCESS_DENIED: absent/malformed/unknown/expired/revoked session, disabled user, or zero authorized candidates. Missing/wrong-group/expired/revoked grant, disabled collection and withdrawal therefore disclose no search content. No reason-specific body or WWW-Authenticate details.
- 503 ACCESS_POLICY_UNAVAILABLE: session/policy DB or clock failure including lock timeout, never partial fallback.
- 503 SEARCH_UNAVAILABLE: candidate DB failure, unavailable version, authorized text integrity/provenance/bounds failure; do not name document, never substitute current text.
- 503 RESPONSE_LIMIT_EXCEEDED: complete serialized body >16384bytes.
- 500 INTERNAL_ERROR: unexpected adapter exception, no traceback returned.

Inherited guards keep403 ISOLATED_LOGIN_DISABLED/BROWSER_ORIGIN_REJECTED and503 ISOLATION_UNAVAILABLE. New outer transport gate returns403 DEMO_LOCAL_REQUEST_REQUIRED like the original browser harness. These can precede method/query validation. Their status and error code are preserved by the search response boundary. Existing login/logout/reader responses are not rewritten.

## Search-only response boundary: decision after review19

Use a dedicated bounded serializer/outer response wrapper for the exact search path, within the already-proposed new `protected_search.py` and `demo_discovery.py`. It must cover application-level inherited rejections AND harness early rejection paths, without editing core helpers. Do not reuse IsolatedLoginApp.reply unchanged as the final search serializer: its405 advertises POST and it lacks the chosen charset/Referrer-Policy headers.

All search responses, including early search-path guard failures, include Content-Type:application/json; charset=utf-8, Cache-Control:no-store, X-Content-Type-Options:nosniff and Referrer-Policy:no-referrer. Non-HEAD responses include accurate byte Content-Length after buffering the complete bounded body. No CORS allowance, cookie, Retry-After or automatic retry. Only405 adds Allow:GET on this path. The wrapper must not turn an earlier403/503 into405 or otherwise reorder validation. Do not silently pass through a malformed/unbounded inherited body.

**HEAD exception:** for the exact search path, suppress ALL response content, including early403/503,405 and unexpected failures; omit Content-Length and Transfer-Encoding. This is not successful HEAD support, a fabricated empty JSON object or a claim that zero is the corresponding GET representation length. Method validation still produces405 when reached; earlier guards retain their chosen status. RFC9110 section9.3.2 forbids HEAD content. Check raw response bytes after the header terminator, not only an HTTP library accessor that hides HEAD payloads.

Requests without a parseable target cannot be classified as this exact path; protocol-parser behavior outside the classified search path is not certified by this specification. Tests must nevertheless cover valid exact-path requests rejected before WSGI dispatch, including duplicate sensitive headers. If the proposed new files cannot cover those guards without editing existing core files, stop and revise the implementation scope.

Old login/logout/reader responses retain their previous behavior, including Allow:POST where appropriate. This contract does not silently repair or reclassify historical non-search HEAD behavior.

Rejections clear pending protected results/text/reference in UI.403requires fresh login or operator resolution;503permits explicit retry with fresh authorization, never automatic token refresh.

## Required boundary tests, not measured results

Independent q length128/129codepoint and256/257byte tests, multibyte input; limit1/5/0/6; offset0/8/9; repeated decoded keys; invalidUTF8/percent; controls/whitespace; NFC/casefold matching with original Unicode/CRLF output intact. Test200authorized no-match versus403invalid/emptycatalog/zeroauthorized, and malformed-query precedence before bearer validation.

Raw-query witnesses: percent-encoding every byte of q=(U+00E9 repeated128times), offset8, limit5, plus every byte of field names/numeric values with literal separators yields815bytes, a valid query-grammar witness. It may pass query validation; success still requires authorized matching content. A2048byte invalid witness is within the coarse cap but must fail later with400 INVALID_QUERY; its2049byte counterpart must fail earlier with414 QUERY_TOO_LONG. These expectations assume prior guards/method/body checks pass. Do not assert that2048must succeed: valid requests cannot reach that size under the other fixed limits.

Exercise raw-wire HEAD with method-level405, early isolation403/503 and harness403: correct status, no bytes after headers, no Content-Length/Transfer-Encoding, required search headers. Exercise non-HEAD search405 with Allow:GET and unchanged login/logout405 with Allow:POST. Assert the search headers on pre-dispatch guard failures, not only happy-path/adapter responses. A local mutant removing outer HEAD suppression or header normalization must fail its exact assertion while the positive passes.

Forbidden-document perturbation stays inside valid fixture envelope and changes no observable results/count/order/paging. Exercise group/collection/grant/session/withdrawal decisions, policy exception after priorpositive, integrity failure, response cap with controlled oversized serializer fixture, and causal authorization/version mutants. These are future acceptance tests, not claims of execution now.

No new implementation file beyond the listed10: incorporate contract into proposed code/runbook/tests. If semantics need existing-core edits, stop and revise scope first. No changes to deployed public contracts, accounts, merge or deployment.

## Custody and method

Original contract at3cfaeca342d865b15381dd915cbf645811751a9a remains available in Git history. This amendment addresses C1/G1/G2/T1 of `docs/auditorias/2026-09-19-19-search-contract-review.md`: HEAD no-content exception, search-only serialization through early guards, correct Allow, and explicit raw-query witnesses. Scope16 remains10implementation files; its proposed file names, immutable-core constraint and approval gate remain binding.

Direct calls to the inherited reply helper were repeated on PR19 source in a fresh archive and matched review19. These are serializer observations, not runtime verification of the future wrapper. The wrapper, HEAD wire behavior and protected endpoint are NOT IMPLEMENTED/NOT MEASURED.17remains reserved for separately confirmed implementation receipt.

--- METODO TITAN ---
Mode: documentation amendment and direct helper observations; future auth/workflow implementation FULL. Machine:brain-env. No product/core/workflow edit, new endpoint, merge, deployment, grant or implementation approval. Contract publication/readback only; receipt21 records evidence and limits.
