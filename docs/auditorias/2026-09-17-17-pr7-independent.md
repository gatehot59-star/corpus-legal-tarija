# SOL audit of PR7: stored text survives, the legacy reader can drop repeated clauses

2026-09-17. Requested scope: audit PR7 using independent failure cases. Reviewer role: SOL. **No product code changed, no merge, no deployment, no production database accessed.**

## Verdict

**Changes requested for malformed-input handling; no publication approval.** PR7's ten existing tests pass, and independent synthetic controls confirm useful copy/identity/archive behavior. However, its cited reader can return HTTP 200 while omitting repeated clauses from a newly built candidate. This is an inherited reader defect exposed by the PR7 integration, not evidence that PR7 deletes those clauses from SQLite.

The local CLI also crashes without its promised JSON error for null/integer mapping entries, and a named-pipe HTML input does not return within the three-second probe. The latter two are robustness findings under invalid local input, not remote exploits or proof of data loss.

PR7 already says not to publish: this audit supports that boundary and adds a concrete reader regression. It does not refute the measured claim about BRAIN's three particular real-source texts, which were not rerun here. An isolated-candidate merge decision is distinct from release readiness; this report is not a formal GitHub approval or review submission.

## Exact subjects and instruments

- PR7: https://github.com/gatehot59-star/corpus-legal-tarija/pull/7 ; open head `d78ad5977ec723fa39a421d4eb2f80d19a2a5f62`, checked again during the audit.
- Writer `pipeline/clean_snapshot.py`: SHA256 `a851d3d0157584dac362466d916b6e68a3e3f13994a7b3a7105814727deff257`, matches BRAIN's cited code.
- Legacy reader: `sistema/api/servidor.py` at `84358cc821490cd90e31cb3f049ef7e691ccc4da`, fetched from git, not substituted with a different server. It is the reader cited by PR7's receipt.
- Execution: isolated git-archive tree in brain-env via gateway build.run; Python 3.12.14, SQLite 3.46.1, 2 CPUs measured. Existing trees and production remained untouched.
- Independent fixture writer uses sqlite3 directly with the published schema. It imports neither BRAIN's test fixtures nor Corpus nor the writer to construct test data. The candidate runs through its actual CLI in a separate process. Reader tests use its actual HTTP handler on an ephemeral loopback port; every listener/thread was stopped.
- The reviewer wrote and ran these probes. Independence is structural: fixed synthetic expected content, direct SQLite readback, and a separately versioned consuming reader. It is not a claim of an independent human legal review or an independent second operator.

Existing tests: 10 pass, exit 0. Independent exploration: 16 CLI scenarios plus 4 reader scenarios, with overlapping controls; not 20 distinct defects or 20 new passing unit tests. A final fixed-oracle verifier exits **1** for the reconstruction mismatch. Its short and nonrepetitive long-text controls pass. Complete fresh-run stdout/stderr and every instrument source are retained.

Remote check on the exact head: `stable_identity`, completed/success, https://github.com/gatehot59-star/corpus-legal-tarija/actions/runs/35271636296/job/105372209810 . This workflow compiles the writer and runs its ten synthetic tests. It does not execute the separate legacy reader or the independent cases below.

## R1: P2, inherited reader can silently omit repeated clauses from a valid PR7 candidate

**Confirmed by CLI + independent oracle + the actual reader/HTTP handler. Publication blocker for this reader/candidate combination.**

Synthetic HTML: one `div#normTxtId`, title `Ley 1`, followed by 150 paragraphs containing exactly:

> El pago no procede sin autorizacion judicial.

The source, mapping digest, HTML hash, old hash, UID and source URL are valid. The expected text is specified independently as `"Ley 1\n" + (phrase + "\n") * 150`, not obtained by trusting the extractor's ledger. PR7 accepts it with exit 0 and `ok:true`, preserving UID/doc_id and creating five chunks.

| Observation | Result |
| --- | --- |
| Independent expected characters | 6,906 |
| Expected complete phrase occurrences | 150 |
| Extracted text in version ledger equals independent expected text | true |
| Chunks reassembled using the segmenter's explicit 200-character overlap equal expected text | true |
| Cited legacy reader `documento(uid)` characters | 5,526 |
| Reader complete phrase occurrences | 120 |
| Missing characters / complete occurrences | 1,380 / 30 |
| `/texto?uid=selected&nro=1` status | 200 |
| HTTP `total_caracteres` | 5,526 |
| Reader hash equals stored new-text hash | false |

Expected SHA256: `547aa5dcc3cbc00c663f676b2dbf642658d88dc7caa64021e02ca3607b8a2a05`.
Reader SHA256: `08e1345b17371809fbd2d986d4e55fe90632173c477f42aba9764b1bc832265d`.

**Cause:** the existing reader's `fusionar` searches for the longest equal suffix/prefix up to 600 characters. Repeated text creates a match longer than the actual 200-character overlap; the reader discards legitimate repetitions as if they were overlap. PR7 calls the existing `trozar` and does not validate reconstruction through this consumer before creating its candidate.

Positive controls: 26-character short text and 9,030-character text with 140 individually numbered paragraphs reconstruct exactly, including their independently specified expected strings. The repeated input is not evidence of real-world prevalence or a certified lost legal provision. It is a deterministic counterexample to universal reader compatibility. It is also not merely the already-disclosed old `nro`/`desde` link problem: the reconstructed whole document itself is shorter.

**Requested acceptance:** use deterministic chunk offsets/overlap or serve the archived exact version text; require the served complete document to match its version hash. Keep both the repeated fixture and nonrepeated positives as regressions. Do not suppress repeated clauses to make the expected result match the buggy reader. BRAIN owns the proposed correction; no assignment or code change was made by this audit.

## R2: P3, malformed mapping items bypass the redacted JSON error contract

**Confirmed new CLI handling defect, no source modification or output candidate.**

A correctly pinned mapping file containing `[null]` or `[7]` passes the top-level nonempty-list check. At `main`, line 143, `item.pop('html_file')` raises AttributeError. That exception is not among the caught exceptions.

Observed: exit **1**, empty stdout, full traceback on stderr, no output file. By contrast, a mapping with a missing source field or a list-valued UID produces exit **2** and JSON `ok:false`, without a traceback. Source logical rows and main-file bytes remained unchanged in all these cases.

The caller is local and the mapping is documented as trusted. This is an error-protocol/robustness defect for malformed supplied data, not a demonstrated attack on a remote service. The current tests explicitly require no traceback but do not test non-object entries.

**Requested acceptance:** validate every list element as an object and its required field types before opening HTML files; `[null]`, `[7]`, missing keys and wrong types should all fail with the documented machine-readable error and no candidate. Keep a valid-object positive control. Catching AttributeError alone would mask the symptom without making the input contract explicit.

## R3: P3, named-pipe input blocks before size/hash validation

**Confirmed bounded observation: no return within three seconds; process killed by the test supervisor.**

Use a mapping whose local `html_file` points to an existing FIFO, with no writer. The CLI checks only `path.is_symlink()` and then calls `path.open('rb')`. The call did not produce output or an error before the timeout. Reading at most MAX_BYTES+1 does not bound the open/read time on a stream.

The sibling regular-file control succeeds. Source rows and main-file bytes remain unchanged; no candidate is created. This probe does not prove a remote denial of service, infinite runtime, or an attack within the documented trusted immutable-file precondition. It identifies an avoidable local-input hang. No concurrent attacker or production input was used.

**Suggested acceptance:** require regular mapping/HTML files under the supported local-file contract and reject FIFOs/devices explicitly. A static-file check addresses the tested case; do not claim it closes same-UID races, which PR7 excludes. Probe FIFOs under an external timeout so the regression runner cannot hang.

## Confirmed behavior and unsuccessful failure hunts

The independent ordinary, committed-WAL, long-text and repeated-text builds retained the untouched document/chunks and an unrelated sentinel table. The committed WAL sentinel was included while its source connection stayed open and idle; there were no concurrent writers. Candidate mode was 0600; quick_check returned ok and foreign_key_check was empty on successful outputs.

A bad second mapping leaves no partial output after an earlier valid mapping. Missing prior chunks and a broken document-to-source FK reject. An existing destination file and a dangling destination symlink reject without replacement. These are synthetic checks, not confirmation of all 6,079 real records.

NUL-character hypothesis: rejected as a loss finding. Text after NUL remained searchable via FTS and the actual `/buscar` handler; reader reconstruction matched. The full raw response remains in evidence, including the known authority-label issue.

Duplicate JSON keys use Python's last-key value and can be accepted. A pre-corrupted FTS row whose uid/doc_id disagree is also accepted; FTS5 does not have the document FK. These are observed hardening edges, not declared trust-boundary exploits or claimed corruption introduced by PR7. The existing trusted-input contract matters; do not inflate them into new release blockers without defining those preconditions.

## Claim -> instrument -> could fail for that claim? -> verdict

- Ten existing tests pass -> subprocess exit and complete unittest output -> yes for their ten scenarios -> CONFIRMED.
- Synthetic source/untouched rows survive -> before/after bytes and row comparisons, sentinel, WAL control -> yes -> CONFIRMED within tested cases.
- All 6,079 real records preserved -> no fresh real-copy inspection in this audit -> no -> NOT MEASURED here.
- Cited reader always reproduces newly cleaned text -> independent fixed golden and actual `documento`/HTTP -> yes -> REFUTED by repeated content; no such universal claim is attributed to BRAIN's three-source receipt.
- CLI always returns a redacted JSON error for malformed mappings -> pinned null/integer cases -> yes -> REFUTED.
- A byte cap ensures prompt completion of local input reads -> static FIFO under timeout -> yes for the bounded no-return observation -> REFUTED as a general assumption, not as a quoted PR7 guarantee.
- Ready to publish -> known authority/link/version blockers plus new reader case; no live deployment verification -> no -> NOT APPROVED / NOT MEASURED as production readiness.

## What was not measured that matters?

The existing suite never exercised the consuming reader on ambiguous repeated text. Counting UID, running SQLite/FTS integrity checks and getting HTTP 200 could all stay green while the user reads a shortened document. Deterministic version-to-served-text correspondence is the missing acceptance check.

Other outstanding areas: fresh production snapshot identity, real-copy field comparison, search relevance/citation regeneration, source authority in all API surfaces, old deep links/version access, legal correctness/validity, sensitive jurisprudence privacy, restore/RPO/RTO, power-loss recovery and large-batch memory. PR7 already declares several of these; they are not newly discovered vulnerabilities.

## Durable evidence and reproduction

The two adjacent text files `2026-09-17-17-pr7-independent/evidence.xz.b64.part0` and `.part1` contain the **entire 292,165-byte JSON evidence bundle**, compressed without loss. No logs, instrument sources, input fixtures, HTTP response bodies, API responses or recorded failures were trimmed. They were retrieved from published git and decoded back to the identical original bytes before this report was published.

Original JSON SHA256: `00b96a1d1eb8bd06ee84ef324db58f615f816339b94c25929785b5645e8d9c67`.
Part0 SHA256: `6b9f703f72bc112d8a219755cb697efe0a5fb6892f1ed092a47082b4cb75984d`.
Part1 SHA256: `32c26c6d007a9c4ff76a44fab3a8891a0ccc78507cf045e65bb90b9b9997f51b`.
Each part is 13,496 ASCII bytes. The encoding is xz+base64, split for transport; it is not a summary.

Decode: concatenate part0 and part1 in that order, strict base64-decode, then `lzma.decompress`. Assert the byte count and original SHA256 above, then parse the JSON. Its `files` map preserves each instrument's full content and SHA256, including `probe.py`, `probe_reader.py`, `verify_oracle.py`, `run_all.py`, and the pinned `legacy_reader.py`. The `runs` list records unabridged argv, exit, stdout and stderr.

To reproduce in an isolated directory: extract the exact PR7 tree into `candidate/`; restore those five scripts from the bundle alongside it; create `results/`; run `probe.py candidate results`, then `probe_reader.py candidate results`, then `verify_oracle.py results`. The probes exit 0 when their exploration finishes; this does NOT mean all checks passed. The final verifier is expected to exit 1 on the unmodified reader, with passing positive controls and a false `reader_equals_golden`. The ordinary author suite is `python3 candidate/tests/test_clean_snapshot.py`.

## Method and limitations of this audit

Context: previous SOL audit/implementation attribution, plan v2 and Nexus read before testing. This audit does not re-certify SOL's PR3/PR6 code as independent work. Its new target is BRAIN's PR7 integration and the cited existing reader. No new architecture, task batch, formal review, notification or deployment was performed.

The first encoded probe transfer failed decompression before writing or running; it was discarded. A later literal-source transfer was compiled and executed. The initially unavailable reader revision was fetched explicitly; it was not declared missing from GitHub based on its absence in the local clone. Final complete runs supersede exploratory snippets without hiding the observed failures.

Applicable QA rubric, qualitative rather than a product score: scope complete for the selected writer and reader cases; causal reasoning separates stored bytes from served text and trusted-input limitations; documentation preserves exact revisions, independent expected content and raw outputs; process uses isolated synthetic fixtures and stops listeners. Not an exhaustive security audit, institutional independence claim, legal certification or performance assessment. Suggested corrections are for BRAIN to implement and then re-review; no product fix was authored in this turn.
