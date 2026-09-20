# Protected search: exact limits and rejection contract

19 September 2026 ART. Specification only, not implemented/tested or permission to implement. Refines the ten-file scope16 and proposal15. PR19 remains open at31dff1ed1c066d4af8a3c6a1ac45e0e85d21eb05. Existing login/logout/exact-reader responses remain unchanged. Full readable contract: [public Doc](https://app.clickup.com/90171457413/docs/2kza6fw5-13597).

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

1. Transport/harness guards first: loopback, exact Host/Origin/Fetch Metadata, sensitive-header duplicates. Preserve inherited opt-in/isolation-marker checks. Unknown routes delegate to existing app; no v1 fallback.
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

All rejection bodies exactly {"error":"CODE"}, no query/UID/token/path/SQL/exception details/count/partial data.

- 405 METHOD_NOT_ALLOWED: any non-GET includingHEAD/OPTIONS; Allow:GET.
- 400 EMPTY_REQUEST_REQUIRED: disallowed Content-Length or any Transfer-Encoding after outer guard precedence.
- 414 QUERY_TOO_LONG: raw query >2048bytes.
- 400 INVALID_QUERY: malformed transport encoding/UTF-8/percent, raw non-ASCII, separators, duplicate/unknown fields, >3fields, missing/invalidq, invalidoffset/limit. One code for all field failures.
- 403 ACCESS_DENIED: absent/malformed/unknown/expired/revoked session, disabled user, or zero authorized candidates. Missing/wrong-group/expired/revoked grant, disabled collection and withdrawal therefore disclose no search content. No reason-specific body or WWW-Authenticate details.
- 503 ACCESS_POLICY_UNAVAILABLE: session/policy DB or clock failure including lock timeout, never partial fallback.
- 503 SEARCH_UNAVAILABLE: candidate DB failure, unavailable version, authorized text integrity/provenance/bounds failure; do not name document, never substitute current text.
- 503 RESPONSE_LIMIT_EXCEEDED: complete serialized body >16384bytes.
- 500 INTERNAL_ERROR: unexpected adapter exception, no traceback returned.

Inherited guards keep403 ISOLATED_LOGIN_DISABLED/BROWSER_ORIGIN_REJECTED and503 ISOLATION_UNAVAILABLE. New outer transport gate returns403 DEMO_LOCAL_REQUEST_REQUIRED like the original browser harness. These can precede method/query validation. Existing login/logout/reader errors are not rewritten.

All new search responses include Content-Type:application/json; charset=utf-8, Cache-Control:no-store, X-Content-Type-Options:nosniff, Referrer-Policy:no-referrer and accurate byte Content-Length. No CORS allowance/cookie/Retry-After/automatic retry. Only405 adds Allow:GET. Rejections clear pending protected results/text/reference in UI.403requires fresh login or operator resolution;503permits explicit retry with fresh authorization, never automatic token refresh.

## Required boundary tests, not measured results

Independent q length128/129codepoint and256/257byte tests, multibyte input; raw2048/2049; limit1/5/0/6; offset0/8/9; repeated decoded keys; invalidUTF8/percent; controls/whitespace; NFC/casefold matching with original Unicode/CRLF output intact. Test200authorized no-match versus403invalid/emptycatalog/zeroauthorized, and malformed-query precedence before bearer validation.

Forbidden-document perturbation stays inside valid fixture envelope and changes no observable results/count/order/paging. Exercise group/collection/grant/session/withdrawal decisions, policy exception after priorpositive, integrity failure, response cap with controlled oversized serializer fixture, and causal authorization/version mutants. These are future acceptance tests, not claims of execution now.

No new implementation file beyond the listed10: incorporate contract into proposed code/runbook/tests. If semantics need existing-core edits, stop and revise scope first. No changes to deployed public contracts, accounts, merge or deployment.

## Custody and method

Read current scope16 and pinned access_policy.py, fetchedmain and confirmedPR19head. New note path absent before publication. No implementation/runtime/CI experiments.17remains reserved for separately approved implementation receipt. Specification appended to main, not product.

--- METODO PROMETEO ---
Mode:LIGERO documentation only; future auth/workflow implementation FULL. Machine:brain-env for Git/API/source inspection. RuntimeQA:NOT MEASURED,N/A to specification publication. Git:docs/agents/respuestas/2026-09-19-18-protected-search-contract.md. Public Doc:https://app.clickup.com/90171457413/docs/2kza6fw5-13597. Publication/readback only, no implementation authorization.
