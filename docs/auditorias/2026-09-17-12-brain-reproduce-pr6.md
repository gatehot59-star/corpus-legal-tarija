# SOL bypass reproduced before parser changes

Pedido: Reproduce SOL's bypass before changing the parser.
Doc: https://app.clickup.com/90171457413/docs/2kza6fw5-12757

## Subject and result
PR6 commit452a75678d5e8160ee62dd8829f9b85fb6f4a072; pipeline/legal_html.py SHA256867444ece1574270d97c6dfbd2fee3674a82711563d8dc9b0e6db1d9312ea1e0. Verified exact git blob; unchanged after execution. New Python run2026-09-17T13:07:18.750648+00:00.

All six inputs/results exactly match SOL. Visible and closed-hidden-sibling accept; balanced-hidden rejects. Cross-table, cross-template and cross-object accept incorrectly relative to Chromium DOM ancestry/template membership. Accepted text is exactly Ley sintetica 1\nNo pagar 390000.\n.

Fresh detached Chromium DOMParser text/html run confirms cross-table/object still under DIV hidden and cross-template inside template.content. Browser HeadlessChrome140.0.0.0. No network/script execution or DOM insertion. This is tree comparison, not full CSS rendering, XSS or proof of actual corrupted source data.

## Baseline
Unmodified test file tests/test_legal_html.py:29tests,0.445s,OK,exit0. Thus this scenario is missing from the existing passing suite. Full stderr retained in /workspace/repro-sol-pr6-20260917/python.json; companion below records baseline summary explicitly, not a full log.

## Cause
Outside body, handle_endtag deletes from the last matching ancestor through the top. Crossed </div> over table/template/object removes the hidden/inactive context. Browser recovery keeps it. Title/hash checks do not discriminate the tree discrepancy.

## Changes
Only this report and evidence committed. No parser/test/PR edits, no merge, no deployment or production changes. Recommended next step, NOT implemented: reject crossed external closes, add regression inputs, then recheck real sources.

## Evidence/method
Companion JSON contains six exact new extractor outcomes and six browser trees. Python: temp copy from exact git blobs; full SHA match before and after. Browser: DOMParser detached text/html, ancestry and template.content. Historical inputs read from docs/auditorias/2026-09-17-11-pr6-cierres-cruzados.json on28e299c8b82003df52d894ee75338ba35c556906. No conclusions beyond these six cases and this revision.
