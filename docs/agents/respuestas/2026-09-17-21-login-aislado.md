# PR11: isolated login without real credentials

17-sep-2026 ART. [PR11](https://github.com/gatehot59-star/corpus-legal-tarija/pull/11),branch titan/isolated-login on PR10. Tested published code18111862c729b4bfcb32b1087dcb279d01c47dd2; base2fd265827b984c85f36fa7d539ef006a6fe05b47. No merge,deployment,live Corpus/VM changes,real accounts or real credential issuance. Session tokens were created ONLY for fictional accounts in temporary test stores,then stores/listeners removed. No tokens delivered or logged.

## Architecture and contracts

New sistema/api/isolated_login.py composes with PR10; tests/test_isolated_login.py exercises HTTP login and reading. Existing clean-snapshot.yml adds compile/test paths,retaining read-only workflow permissions and prior tests. access_policy.py,exact_http.py,version_text.py and servidor.py are unchanged. No new package,automatic migration,listener or UI.

IsolatedLoginApp(candidate,store,collection,enable_test_login=False,clock=time.time) is disabled by default. Requires explicit opt-in,loopback REMOTE_ADDR,isolated_test store marker and fixture-* identity. LOGIN_SCHEMA declares login_environment,login_passwords and singleton login_budget;only the fixture applies it. No signup/provisioning endpoint.

POST /api/v2/login requires application/json with exactly username/password;body1..4096bytes,password1..1024UTF8bytes,lowercaseASCIIusername1..80. Duplicate keys,extra fields,Origin,Transfer-Encoding and invalid input rejected. No cookies or CORS;no-store,nosniff,redacted errors.

Flow:input/isolation validation -> persisted attempt budget -> password verifier -> fixture session commit -> PR10 permission check on reading. Login writes NO AccessGrant. The positive test demonstrates403after login,then exact paginated text only after the fixture explicitly adds a fictional grant.

Password verifier:scrypt N=2^17,r=8,p=1,16byte salt,32byte digest,maxmem256MiB;hmac.compare_digest. [OWASP Password Storage](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html) checked live. Unknown and disabled users execute a full KDF and receive the same401body as wrong passwords;whole-request timing equivalence NOT measured. Test salts/passwords are fictional. No real password provisioned.

Session token:secrets.token_urlsafe(32),256bits random input,900sTTL;only SHA256stored. A second login gets a fresh token regardless of supplied Authorization. BEGIN IMMEDIATE serializes attempt/KDF/session writes. Global5attempts/60s budget persists,including successes;6th gets429before KDF. Clock rollback/nonfinite time fails closed. This deliberately coarse test budget is NOT production per-user/IP/distributed rate limiting.

## Verification

Code retrieved from Git matched tested module/tests and unchanged dependencies byte for byte. Repeated from published18111862:compile exit0;12login tests13.309s;15access tests5.443s;15HTTPtests1.457s;21SOLtests5.934s. Total63tests,exit0;coverage reruns not counted again.

Positive flow preserves complete text and candidate DB hash. Store contains verifier/session hashes,not plaintext password/token. Negatives cover wrong/unknown/disabled account,default disabled,missing marker,nonloopback,forged forwarding header,malformed JSON,budget,clock failure,session expiry/revocation and store failure. Cleanup stops servers,asserts threads ended and removes temporary stores.

Three local mutants fail:password verifier bypass,attempt-budget bypass,loopback restriction bypass. The latter is a direct WSGI-environ boundary test,not an external ingress test. Mutants are not pushed or run in remote CI.

[CI stable_identity](https://github.com/gatehot59-star/corpus-legal-tarija/actions/runs/35289344683/job/105428586170):completed/success,18-sep00:00:57Z..00:01:08Z (17-sep21:00:57..21:01:08ART). Copilot requested,get_reviews=[]:not approval.

Trace observed124executable lines,100%line coverage of isolated_login,not branches/load/concurrency/whole Corpus. This supplementary measurement does not replace the complete pass/fail test logs below.

## Risks and remaining scope

Isolated engineering progress,NOT D09/M03/pilot completion. No real provisioning,reset,MFA,account UI,logout HTTP,grant issuance,acta verification or payments. Revocation uses fixture SQL updates,not a logout endpoint. No TLS,load/concurrency certification,production logging or deployment.

Do not put this behind a proxy/tunnel:it could make external traffic appear loopback. REMOTE_ADDR/store/clock/filesystem administration are trusted;guards are not containment against malicious operators. WSGI body size is bounded but socket/slow-body timeouts belong to the host. Global budget can block other fixture users;KDF holds a write transaction.10xperformance not measured. No request-timing guarantee,response recall or distributed revocation claim. No host/CVE/historical-secret audit.

Future production onboarding is separately authorized work,not a flag flip. Real issuance and human approvals remain pending. Search,citations,export,OCR and legal validity unchanged.

## TITAN QA

81/90=90/100,isolated module ONLY. Deployment10N/A;CI measured. Completeness14(module/schema/route complete for test scope);executability15(published compile/63tests);security13(isolation/KDF/budget,no auto-grants,host limits);testing13(12new,regressions,3mutants,no load/concurrency);architecture9(reuses PR10,separate store,transaction,throughput unmeasured);documentation9(contracts/limits/logs,no production runbook);improvements4(marker,duplicate-key rejection,rollback-aware budget,no implicit grants);process4(published verification and CI,external review not emitted). NO merge/deploy/onboarding approval.

Roles:Architect,Builder,Security,Tester,QA. No invented external executor. Initial fixture salt corrected before first run. Two prior encoded receipts were invalid;their base64blocks are withdrawn,NOT evidence. Switched to plain JSON logs below and compare their captured fields against originals. Code and measured results did not change.

## Authoritative plain-text evidence

- docs/agents/evidencia/2026-09-17-21-login.json:complete stdout/stderr of12login tests and3mutants,commands,exits,mutation strings.
- docs/agents/evidencia/2026-09-17-21-regression.json:complete stdout/stderr of51previous tests rerun on this published commit.

These JSON files contain original captured strings,not reconstructed summaries. The narrative is interpretation. The compressed payloads in9857e010/89f0f558are invalid and must not be used. Compilation had empty stdout/stderr,exit0,command:python3 -m py_compile sistema/api/isolated_login.py tests/test_isolated_login.py.
