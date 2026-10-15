# PaddleOCR with native layout reconstruction: columns fixed, skew regression exposed

15 October 2026. Operator: BRAIN / GPT-6 Astra. Request: “Run PaddleOCR with layout reconstruction”. TITAN LIGERO, bounded diagnostic execution, no delicate operation, no production deployment or merge. Formal production rubric and external review: not performed.

## Result and decision

**PP-StructureV3 completed all ten images.** On the two-column control, native layout ordering reduced character edits from **689 to 3**, or CER **75.5482% to 0.3289%**. The left column now precedes the right column.

**Do not promote this configuration as the default.** The rotated/blurred control regressed from zero character edits with plain PaddleOCR to **266/912 (29.1667% CER)**. The output loses `no podrán` and `por sí mismos`, corrupts text and mixes an article heading with a paragraph. Fixing column order did not make the pipeline uniformly safer for legal text.

The six real scanned pages took **250.095206 seconds**, compared with **125.893766 seconds** for the earlier plain PaddleOCR run, approximately 1.99 times as long. Real-scan accuracy remains **NO MEDIDO**: no independent reference transcription was introduced. This is not a general engine ranking or a claim of legal correctness.

## What actually ran

Native `paddleocr.PPStructureV3`, not a hand-written sorting heuristic. Layout detector `PP-DocLayout_plus-L`, region detector `PP-DocBlockLayout`, original `PP-OCRv5_mobile_det` and `latin_PP-OCRv5_mobile_rec`. PaddleOCR 3.7.0, PaddlePaddle 3.3.1, PaddleX 3.7.2. The existing OCR weights and configuration files were checked unchanged against the previous run.

CPU on the same two-CPU Corpus VM. MKL-DNN disabled, detector maximum side 960, thread setting 1. The observed process nevertheless had **ten OS threads**, so this was not strict single-thread isolation. No CPU affinity or quota was added. Peak process RSS: 1,347,832 KiB, not total system memory. No package in Corpus's application environment was modified.

Document rotation classification, unwarping, text-line orientation, and specialized table/formula/seal/chart recognition were disabled. Region detection was enabled. This tests text layout/reading-order reconstruction, not full table or formula reconstruction. Scored text is every `block_content` concatenated in the native `parsing_res_list` order, with no reference-aware correction or filtering. Native Markdown outputs were also saved; CER was calculated on plain block content, not Markdown formatting.

The original ten PNGs and original reference were reused unchanged: six real scans from three Tarija documents plus four synthetic variants of one Ley 439 excerpt. This is a **post-hoc regression test on already observed controls**, not a new blind or held-out experiment. Configuration was fixed before this run's inference and was not tuned after seeing its scores.

Same OCR weights do not mean a pure permutation experiment: PP-Structure's processing can also change recognition and block assembly. In the skewed case, the raw `overall_ocr_res` was already corrupted; the damage was not merely introduced by the final newline join. No specific upstream root cause has been proven.

## Controls, without hiding regressions in an aggregate

| Control | Earlier plain Paddle character edits | Layout character edits | Layout CER | Layout word edits / WER |
|---|---:|---:|---:|---:|
| Clean | 0 | 2 | 0.2193% | 4 / 2.7211% |
| Rotated, blurred, noisy | 0 | 266 | 29.1667% | 56 / 38.0952% |
| 150 dpi | 1 | 2 | 0.2193% | 3 / 2.0408% |
| Two columns | 689 | 3 | 0.3289% | 5 / 3.4014% |

Each control has the same 912-character, 147-word normalized reference. Normalization remains NFC plus whitespace collapse, preserving accents, punctuation and case. Missing spaces still count: collapsing existing whitespace does not insert a missing space between joined words.

The two-column output retains the correct article sequence but still loses the period after the Article 3 heading and two spaces after commas. Clean output loses two spaces at line joins. Low-resolution output retains the missing comma from the previous plain OCR and also loses a space. These are not perfect transcriptions.

The limited eight-string presence check totals **30/32**, down from 32/32. Its two failures are in the rotated/blurred control: `no podrán` and `por sí mismos`. This is presence checking, not validation of legal relationships. The four-control aggregate is 273 character edits; it must not conceal the newly introduced skew failure.

## Real scans: timing only

| Case | Plain Paddle, earlier (s) | Layout (s) | Layout output chars |
|---|---:|---:|---:|
| d01-p001 | 32.106789 | 60.095760 | 3573 |
| d01-p003 | 29.576016 | 50.812598 | 2873 |
| d02-p001 | 25.645153 | 51.034718 | 2885 |
| d02-p002 | 15.094473 | 32.718679 | 1622 |
| d03-p001 | 9.891716 | 25.142950 | 914 |
| d03-p020 | 13.579619 | 30.290502 | 1325 |
| Total, unrounded inputs | 125.893766 | 250.095206 | 13192 |

Character counts do not establish accuracy. This is one measured pass per configuration at different times on the same VM, not a repeated randomized latency experiment. The table excludes initialization, warmup, downloads, scoring and serialization. Layout initialization including model downloads took 6.959623 s; warmup took 14.159562 s.

## Setup recovery and execution record

The first launch failed before inference because the existing OCR environment lacked the optional dependencies required by PP-StructureV3. That failure was preserved. No dependency check was bypassed.

A separate virtual environment was created with an import path to the original OCR packages. The missing extras were resolved against exact installed-version constraints from official PyPI, then 26 missing/transitive packages were installed into the new environment with exact versions, artifact hashes and `--require-hashes`. Both installation and `pip check` exited 0. The original OCR environment was not upgraded. The two official layout models were downloaded to the existing model cache; model hashes are recorded.

The same script and settings were launched into a new output directory after resolving dependencies. No failed output was overwritten and no sample or metric was changed.

Exact successful command:

```sh
nice -n 10 timeout -k 10 1200 /tmp/ocr-layout-20261015-env/bin/python /tmp/ocr-layout-20261015-run.py /tmp/ocr-layout-20261015-run2
```

Seal: 12:46:14.986230 UTC. Execution record: 12:46:16.838509 to 12:52:38.888090 UTC, approximately 09:46 to 09:52 ART. Completion record: exit 0, ten cases. No Corpus application code, database, services or deployment was changed. ABBYY was not run.

## Verification that could reject the result

The separate `verify_layout.py` uses a full-matrix Levenshtein implementation, not the benchmark's rolling-row function. It recomputed all four control scores, checked ten text/raw-file hash pairs, reconstructed text from the native block lists, checked input identities, and required real-scan scores to remain null. It ran with exit 0 at 12:52:57 UTC.

Three actual altered-record trials were rejected: forged character-edit count, modified text and missing case. Unit checks cover identity, empty output, negation loss, order, accents and whitespace. This is a separate implementation operated by the same agent, **not an external audit**.

At 12:53:21 UTC the final check confirmed unchanged image and model hashes and no active benchmark process. PASS means execution/integrity and the bounded two-column ordering result. FAIL means the skewed-control regression and non-exact transcription. NO MEDIDO means real-scan accuracy, held-out generalization, table/formula fidelity, upstream root cause and production suitability.

## Evidence and custody

[Executed script](../evidencia/2026-10-15-04-paddleocr-layout.py) and [selected measured evidence](../evidencia/2026-10-15-04-paddleocr-layout.json) accompany this report. The JSON includes exact stdout, four complete synthetic output strings, the native two-column block list, ten timing/hash records, original reference, configuration, model-weight hashes, validation and closure. It is enough to recompute the reported control CER/WER using the already-published baseline scorer or another Levenshtein implementation.

Full native raw JSON, real-page text, Markdown, complete original record, complete model inventory, verifier source, installation/download logs and exact dependency lock are preserved in brain-env/VM, **not all published in Git**. PDFs, raster images and model weights are not committed.

| Artifact | SHA-256 |
|---|---|
| Executed layout script | `64e1d4e9d36516622380d1d021f469cb067719a45331196695c16cb42b2aff5a` |
| Original record.json, 81,039 bytes | `688a67ddfdf64be0bbbb1c4db9611e78e69e4ed3733b5469d05640fadfec8b06` |
| Selected publication JSON, 20,504 bytes | `f9b29a6031ab7e29081fd1b211a917269f126fa5983bb58d1252f3c213f1c047` |
| Independent verifier source | `621396c748244b5739b79eb03cfc9cc7ebd38fdf2524b2a48d8b5c1e9c7986a2` |
| Exact additional-dependency lock | `0b3ec8644dfde76e3f533a329ac31b1a1c1453fc4f5aa2e78bc38873dc2d771e` |

Custody: brain-env `/workspace/ocr-layout-20261015`; successful VM run `/tmp/ocr-layout-20261015-run2`; isolated environment `/tmp/ocr-layout-20261015-env`. The script deliberately retains the actual original-bank path and needs those preserved inputs to rerun. No claim of a standalone portable package is made.

Baseline: [previous immutable OCR report](https://github.com/gatehot59-star/corpus-legal-tarija/blob/141a9103fc4442413ed6ec16eab592ecd9804fd2/docs/agents/respuestas/2026-10-15-03-tesseract-paddleocr-medidos.md). Repository main was observed at `c273c659ee90f2259f540cb14c576d6a16dcfb40`; the open application PRs were checked, not modified. This delivery stays on the existing documentation branch, with no PR or merge.

## Next technical decision, not implemented

Keep this as a measured candidate, not a replacement. A safer next experiment would preserve plain OCR text and test geometry-only ordering separately, plus held-out rotated and multicolumn pages. That has not been implemented or measured here. The current request was to run native layout reconstruction, and it has been completed without concealing the new failure.
