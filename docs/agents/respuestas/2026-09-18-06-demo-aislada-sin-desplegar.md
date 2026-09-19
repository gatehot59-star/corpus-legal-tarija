# Corpus isolated demo launcher: implemented, tested, not merged or deployed

18-sep-2026 ART. User explicitly approved the nine-item implementation/test/publication batch in ClickKit (approve_corpus_demo_launcher, implement_test_publish_no_merge_no_deploy). No deployment or merge is authorized or performed.

## 1. Request and conclusion

Request: implement the isolated Corpus demo launcher without deploying. CONCLUSION: implemented on `titan/isolated-demo-launcher`, [PR14](https://github.com/gatehot59-star/corpus-legal-tarija/pull/14), open and unmerged. The real CLI mounts the integrated IsolatedSessionApp instead of changing the historical server. It creates and accepts only its own synthetic demo candidate and separate fixture store, never a real Corpus database.

Code commit: `5ac0da781c53de9ffbe2a0752e33ab7aa87b33d2`; base `7505bd8ef82714d1d43285f32fab55f2b19b400f`. Three new files, one grouped feature commit, 624 added lines. All three were recovered from Git and compared byte-for-byte with the tested sources: equal. Main receives only append-only documentation/evidence. Its diff outside docs from the base through evidence commit7cbbc46223b597c70af303010fa7a025534e28d7 is empty.

## 2. Tools and machine

GitHub personal connector selected earlier in this thread for branch/push/PR; MUDH Gateway `build/run` for brain-env execution; ClickUp for public Doc; Nexus for own continuity record. Current Python3.12.14, SQLite3.46.1 and an actual ephemeral127.0.0.1 bind were measured. The environment inventory was read, not treated as a current capability guarantee. No Actions/Kaggle job, production listener, VM connection, package installation or workflow change was initiated.

Repo tree, integrated-session modules, versioned reader, current integration receipt, audit09 and workflow were read before implementation. No CONTEXTO/AGENTS file exists in the enumerated Corpus tree at the base; latest receipts supplied live context. Open PR1 was enumerated and its complete32-file diff list obtained through Git after a tool diff was truncated. It touches historical server/README, not the three new paths; these remain unchanged and PR1 remains excluded.

Roles performed sequentially by one operator: repository inspection, architecture/contract, implementation, security guard design, tests, documentation and final QA. No claim of independent reviewers based on these roles. Scope/test-selection priorities also come from the preceding Astra audit and the explicit approved request.

## 3. What was implemented and measured

### Contract

`init --directory NEW --isolated-demo` creates only a new directory0700, candidate.db0600 and sessions.db0600. It inserts a fixed fictional Unicode/CRLF document, two fixture identities, explicit fictional grants, the existing login schema and a demo marker. Source URL example.invalid, textual warning and SYNTHETIC-NOT-APPROVAL distinguish the fixture. The reader-compatible provenance field is not a claim that LexiVox published this fictional text.

`serve --directory EXISTING --isolated-demo` validates before binding, mounts IsolatedSessionApp on literal127.0.0.1 and preserves existing revocations/budget. No migration, grant reset or provisioning on serve. No parameter to load another corpus, no production mode, host override, proxy or daemon. Host must equal127.0.0.1:PORT and any Origin is rejected. Default port0 is ephemeral. Occupied port fails without killing another process. SIGINT/SIGTERM stop the owned listener.

Filesystem checks reject symlinks, hardlinks, FIFO, non-private files, wrong candidate, unexpected sidecars, incomplete schema and missing markers. Initialization refuses to overwrite even its own previous directory. An interrupted init leaves its directory for inspection, not automatic deletion/recovery. The directory owner/root remains trusted: this is not protection against hostile same-UID races.

Public fixture accounts ana/ben use `solo-demo-ficticia`, intentionally not a real secret. Grants last24h; sessions15min. Login does not grant access or refresh grants. Shared five-attempt/minute budget and clock guards are inherited unchanged. HTTP is local development only, not TLS or a production boundary.

### Measurements

- `python3 -m py_compile sistema/api/demo_aislada.py tests/test_demo_aislada.py`: exit0.
- `python3 tests/test_demo_aislada.py`:18tests,36.523s,exit0.
- `python3 tests/test_login_guards.py`:18tests,33.937s,exit0.
- `python3 tests/test_isolated_session.py`:10tests,21.635s,exit0.

46 selected tests, not a full repository test suite. The12 inherited login tests are included within18guard tests, not counted twice. New tests run actual CLI subprocesses, HTTP and SQL, not an alternative server hidden inside the test. Exact paginated text, distinct-process persistence, selective/idempotent logout, revoked grant separation, opt-in, paths, permissions, missing tables, occupied port and candidate byte preservation are asserted.

Two broken copies demonstrate detection, with exact replacements preserved in raw evidence:

1. Disable opt-in condition: `test_init_requires_opt_in_without_writes` fails AssertionError0!=2.
2. Clear revoked_at at server startup: `test_cli_lifecycle_pagination_selective_logout_restart` fails AssertionError200!=403 after restarting a distinct process. This is an intentional mutant, not a defect in delivered code.

Baseline passed. Both mutated verifiers exit1 for the target assertions, not imports/timeouts. Processes created by these tests are terminated and port closure checked in finally blocks.

Coverage instrumentation via stdlib sys.settrace in actual child processes:169/182 executable line entries=92.8571428571%, separate18-test pass98.098s. Denominator conservatively includes synthetic line0 from trace._find_executable_linenos. Line coverage only, no branch coverage claim. Instrument sources and every per-process traced-line file are preserved. No coverage dependency added to product.

Runbook client executed after replacing fixed8765 with the actual ephemeral test port: stdout exactly `read: 200 exact: True`, `logout: 200`, `read after logout: 403`. Server exited0 and port closed. Final /proc scan found no active demo_aislada.py serve process. This is a snapshot of own demo cleanup, not a claim that the entire shared machine has no other services.

### Corrections made, not hidden

Initial source transfer retained literal leading patch plus-signs; compile/test failed before functioning code execution. Every line was verified to carry that prefix, then transport normalization removed it. Full failed stdout/stderr and correction record remain; final source was compiled and tested successfully, then compared to remote Git.

The first runbook capture stored a shared mutable command list: changing it to serve also changed the earlier captured init command. Original capture remains verbatim with a separate note reconstructing the initial command. Its initialized stdout is genuine; no claim that serve provisions. No product behavior is inferred from this capture bookkeeping mistake.

## 4. Raw evidence and custody

[Evidence wrapper](https://github.com/gatehot59-star/corpus-legal-tarija/blob/7cbbc46223b597c70af303010fa7a025534e28d7/docs/agents/evidencia/2026-09-18-06-demo-launcher.json), xz+base64 in JSON. Original decoded length64612bytes; SHA256 `33cff09f81f51e5e450a116a0d7ff86d477fb79b3dba37f902e89daf95b4fdad`.

Publication was fetched from Git and decoded with strict base64 then lzma; equality with the captured original is byte-for-byte TRUE. Commit belongs to main. No binaries committed. Wrapper has codec,bytes,sha256,payload. To inspect, parse JSON, base64.b64decode(payload,validate=True), lzma.decompress, verify length/hash and parse JSON. This exact algorithm was executed on the remote file.

The decoded files map includes complete initial/final run outputs, all supervisor logs, mutations and exact replacement instrument, coverage results/hook/instrument and all per-process lines, runbook execution and capture correction, transport correction and Git source equality. No outputs shortened. Normalized source is referenced by verified commit, not duplicated; the erroneous plus-prefixed source transfer is not included again. Runtime HTTP bodies/bearer values were not captured: assertions and published source define those oracles. The public synthetic password appears in reproducible source/runbook, not as an actual account credential. Publication verification necessarily occurred after freezing these bytes and is recorded here separately.

Source SHA256 values verified remotely:

- sistema/api/demo_aislada.py:e9c0de76fb1c8f4917706210a1a8f74a9552434430c86f77e865fdb00c31f775
- tests/test_demo_aislada.py:55d5e0d94271d0d6fb211b110ac3a6131e82db3dbb48a2d2035550acf11f0aac
- sistema/DEMO-AISLADA.md:7ceab6c9b9c51f797aa7e160355c7661367cb60476f783562f23a3e6d8ab38ab

## 5. Files and public delivery

Code is grouped in the branch commit above; documentation/evidence is append-only on main, not a product merge:

- [sistema/api/demo_aislada.py](https://github.com/gatehot59-star/corpus-legal-tarija/blob/5ac0da781c53de9ffbe2a0752e33ab7aa87b33d2/sistema/api/demo_aislada.py)
- [tests/test_demo_aislada.py](https://github.com/gatehot59-star/corpus-legal-tarija/blob/5ac0da781c53de9ffbe2a0752e33ab7aa87b33d2/tests/test_demo_aislada.py)
- [sistema/DEMO-AISLADA.md](https://github.com/gatehot59-star/corpus-legal-tarija/blob/5ac0da781c53de9ffbe2a0752e33ab7aa87b33d2/sistema/DEMO-AISLADA.md)
- docs/agents/evidencia/2026-09-18-06-demo-launcher.json
- This receipt:docs/agents/respuestas/2026-09-18-06-demo-aislada-sin-desplegar.md

[Public Doc: Corpus isolated demo launcher: implemented and tested, no merge or deployment](https://app.clickup.com/90171457413/docs/2kza6fw5-13177), Space > Doc. Created public and read back. [PR14](https://github.com/gatehot59-star/corpus-legal-tarija/pull/14) reread open, merged:false, exact expected head5ac0da7. Copilot review request submitted; get_reviews returned[] at closure inspection. No review approval claimed.

Actual check_runs response for PR14:total_count0,check_runs[]. Existing clean-snapshot path filters do not include the three new files; no workflow edits or manual CI dispatch were authorized here. This is measured local execution, NOT a new green CI. CI integration is a separate proposed follow-up, not silently added to this batch.

## 6. NO MEDIDO, unchanged scope and QA

NO MEDIDO: production/live-host configuration, TLS, crash/power-loss recovery, machine restart, hostile-owner filesystem races, arbitrary concurrency/load, other Python/OS versions, legal validity/privacy review or commercial usefulness. No fresh dependency/CVE scan; only unchanged stdlib/existing modules used. No real credentials, real corpus data, deployment, merge, live-store mutation, issue creation or messages to other agents. Public synthetic credentials are explicitly fixtures. No serving process intentionally left active.

Older joint-review publication, historical local audit deliveries and with/without-skill evaluation remain separately pending. This delivery does not close those or imply an audit of6079documents. A UI and real-account provisioning are explicitly outside this unit.

### Scoped QA assessment

Completeness15/15:all three full files, actual CLI and no placeholders. Executability15/15:compiler,46tests,runbook and verified remote source. Security13/15:synthetic-only,strict filesystem and Host/Origin checks; minus2 for no fresh CVE scan/hostile-owner proof. Testing14/15:46selected tests,two pertinent mutants,92.86%line coverage; minus1 for no arbitrary crash/concurrency coverage. Architecture9/10:explicit composition/no changes to existing boundaries, deliberately monothread; minus1 for limited scaling. Documentation10/10:source contract, lifecycle/error behavior and executable runbook. QA process5/5:exact versions, raw outputs, errors disclosed and remote custody.

TOTAL81/85=95.29/100 for the local demo only. N/A15points:DevOps10 because deployment prohibited; Innovation5 because unrequested extras would enlarge scope. Not certification of production safety or an authorization to merge. Roles are one operator; external review has not approved.

Before user-facing closure, fetch this receipt from Git, confirm ancestry/main docs-only delta, update public Doc with receipt/evidence links and record own Nexus continuity. These final publication checks are not assumed from writing this paragraph; the continuity record carries their observed result.

--- METODO PROMETEO ---
Accion delicada: SI, explicit fixture-authentication composition.
Modo aplicado: FULL.
Maquina: brain-env via MUDH Gateway build/run; no Actions/Kaggle launch.
Rubrica:81/85 ->95.29/100, N/A15points as declared.
Review externo: Copilot requested; no findings/approval emitted at inspection, pending review is not approval.
Instrumento: compiler exit0, CLI18+guards18+session10 exit0, two mutant verifiers exit1 for target assertions, trace coverage and executable runbook; raw evidence file above.
Artefactos:docs/agents/respuestas/2026-09-18-06-demo-aislada-sin-desplegar.md + https://app.clickup.com/90171457413/docs/2kza6fw5-13177; code in PR14 only.
