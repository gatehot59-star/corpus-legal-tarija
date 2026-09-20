# Search contract review: one protocol contradiction, two reuse gaps, one test clarification

19 September 2026 ART. Subject: docs/agents/respuestas/2026-09-19-18-protected-search-contract.md at3cfaeca342d865b15381dd915cbf645811751a9a and its public Doc https://app.clickup.com/90171457413/docs/2kza6fw5-13597. I authored that contract. This is self-review with external HTTP rules and calls to the actual inherited serializer, not review by another person or an implemented-search security audit. The contract remains unchanged by this report.

## Decision

Do not implement the contract verbatim. Correct the HEAD exception and explicitly choose how search-route responses are serialized, including inherited guard failures. Keep the ten-file scope unless those decisions need core changes. Publication of this review is not approval to implement, merge or deploy.

## C1 CONFIRMED: HEAD cannot have the mandatory JSON error body

Contract18 requires all rejection bodies to be exactly a one-member JSON object and expressly includes HEAD among405 METHOD_NOT_ALLOWED cases. RFC9110 section9.3.2 states: the server MUST NOT send content in a HEAD response. Thus the blanket body requirement cannot apply to HEAD, regardless of whether the status is405 or an earlier403/503 guard rejection. This is a protocol contradiction in the spec, not a reproduced flaw in a new endpoint.

Correction proposed, not applied: preserve chosen guard/method status precedence, but suppress all HEAD response content at the search-route outer boundary, including early failures. Declare an explicit exception to JSON-body and Content-Length rules. Prefer omitting Content-Length on HEAD rather than pretending the empty wire body is the hypothetical GET representation length. Keep405 Allow:GET when method validation is reached. Verify raw wire bytes, not just an HTTP client's HEAD body accessor, which can hide sent bytes.

Source: https://www.rfc-editor.org/rfc/rfc9110.txt section9.3.2. Full retrieved section preserved in evidence. No requirement to implement successful HEAD search is inferred here.

## G1 CONFIRMED integration gap: all-response headers are not inherited

Contract18 says all new search responses include application/json;charset=utf-8 and Referrer-Policy:no-referrer. Existing IsolatedLoginApp.reply emits application/json without charset and no Referrer-Policy. Direct calls to the actual method on PR19head31dff1ed return that result for403 ISOLATED_LOGIN_DISABLED and503 ISOLATION_UNAVAILABLE. Those failures occur before the new session_route adapter can serialize its own response.

This is NOT proof that the no-core-edit constraint is impossible: the new harness may wrap responses for the exact search path, or the contract may explicitly limit universal headers to adapter responses while documenting inherited exceptions. Choose one. Recommended: search-path-only outer response handling in the already-proposed new harness, preserving inherited codes, no-store and existing routes. It must cover earlier guards and HEAD without silently rewriting login/logout/reader behavior. Future HTTP tests must exercise failures before dispatch, not only adapter-level403.

## G2 CONFIRMED reuse hazard: inherited405 advertises POST, not GET

Actual IsolatedLoginApp.reply(405,{error:METHOD_NOT_ALLOWED}) returns Allow:POST because it belongs to login/logout. Search contract demands Allow:GET. Reusing that helper unchanged for the new search405 would be wrong. It does not prove search already does so: no search implementation exists.

Correction proposed: search-specific response serializer, or narrow response adapter, inside the existing new-file budget. Keep the parent serializer unchanged. Acceptance: a valid same-origin request using unsupported method reaches method validation and emits Allow:GET; old login/logout405 behavior remains POST. HEAD still has no content perC1.

## T1 CONFIRMED arithmetic; NOT a contradiction: 2048 cannot be a valid positive query

All valid decoded q bytes<=256, field names total12ASCIIbytes, numeric values total2bytes, and3equals/2ampersands. Even percent-encoding every name and value byte gives at most256*3+12*3+2*3+5=815rawbytes. An actual witness with128 U+00E9 characters, offset8 and limit5 reaches815; the output is preserved. Consequently a2048byte query cannot satisfy all other grammar/value limits. The2048cap is still a coherent coarse defensive limit.

Clarify the future tests rather than falsely claiming the limit itself conflicts:815byte valid witness can pass query validation;2048bytes fails later INVALID_QUERY;2049bytes is rejected earlier QUERY_TOO_LONG. These status expectations assume method/body/outer guards pass. Contract18 asked for2048/2049boundary tests but did not say2048must succeed, so this is a missing expected-result clarification, not a confirmed contradiction.

## Checks that did not establish contradictions

- q<=128codepoints AND<=256UTF8bytes is consistent. Independent multibyte fixtures can hit either boundary. NFC/casefold affects matching, not displayed original text.
- offset0..8 with<=8candidates is consistent; offset>=total returns empty200 for an otherwise authorized query. It is not a416 case.
- Valid session plus zero authorized candidates403 versus authorized documents with zero query matches200 is explicitly specified. It is a design choice, not an accidental contradiction or new grant issuance.
- Fixed server collection routing can coexist with UID/version-only public locators when the manifest gives an unambiguous server mapping; implementation still must prove no scope confusion.
- Point-in-time authorization and inability to recall previously delivered bytes are already declared limits, not new bypass findings.
- The16KiB response cap may be a defensive condition unreachable with ordinary bounded results; a serializer fault-injection test is explicitly identified as such, not a valid-production-input overflow exploit.

## Evidence and reproduction

PR19 archived in fresh /workspace/search-contract-review-401ldm4o. Imported actual sistema/api/isolated_login.py via that archive's path; called static reply directly at403,503,405 with a capturing start_response. No new endpoint, HTTP listener or database was opened. Evidence preserves exact returned headers/bodies, source revision,815byte witness with arithmetic, and full RFC HEAD section. These are method calls and arithmetic, not full network behavior.

Reproduction of inherited outputs: import IsolatedLoginApp from the pinned archive; capture start_response and join the bytes returned by IsolatedLoginApp.reply for the three status/code pairs above. For the URL witness percent-encode every UTF8byte of q=(U+00E9 repeated128times), and every byte of q/offset/limit field names and values8/5, using literal separators. The command assertion len(query)==815 passed, exit0. RFC retrieved from its canonical URL.

Evidence: docs/agents/evidencia/2026-09-19-19-search-contract-review.json, zlib+base64,4955decodedbytes SHA2569240e241d0bb94189248b1e6477cbf81b46b35877eab34e795322f79beb72ece. No tokens/credentials captured. Source comparison, RFC and returned headers are the oracles; mutation testing of a not-yet-written endpoint is N/A, not a passed security gate.

An initial git log invocation described the checkout's old local HEAD, not current origin/main. It was not used to date the contract; origin/main was explicitly resolved and later logged correctly. No product error was inferred.

## Gates and next action

GateI: documentary/protocol review plus direct existing-helper calls; source/ref and outputs captured. New-endpoint baseline/mutants/network cleanup N/A because no endpoint/listener was run. Arithmetic witness executed. No production/runtime safety certification.
GateII: one real contradiction distinguished from two integration hazards and a test clarification; fixes proposed, not applied. No numeric score or external-review claim.
GateIII: report/evidence are appended to main; remote decode and byte comparison, public Doc and Nexus are required before final chat.

What matters but remains NOT MEASURED: actual new route, raw HEAD wire behavior of its future wrapper, full guard precedence, search authorization/privacy and concurrency. Before implementation, amend the contract in place to avoid competing instructions; this review alone does not amend it or authorize that implementation.

--- METODO PROMETEO ---
Mode: bounded audit of specification, not feature implementation. Machine:brain-env. No product/core/workflow changes, merge, deployment or executor messages. Contract18 untouched. Evidence/report separate; public Doc and Nexus close the delivery.
