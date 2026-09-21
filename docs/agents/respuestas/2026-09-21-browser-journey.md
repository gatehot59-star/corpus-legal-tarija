# Real-browser acceptance: PR22 fails at login

## Exact subject and result

Human request: Test Corpus's full journey in a real browser. BRAIN tested immutable PR22 head ba9646bf89fecb2a2431e9708f876dd0966afe81, read back live from Git. The selected cppcheck document is unrelated. No product source, production data, deployed service or existing PR was changed.

Result: RED at the first authenticated step. Real Chromium153.0.8010.12 driven by Playwright1.63.0 loaded the login form, filled the fictional account fields and clicked Entrar. POST/corpus/login/ returned403 with an actual rendered CSRF rejection. This reproduced twice. The prior38 unit/integration tests and urllib/Gunicorn journey did not establish browser compatibility. This narrows and corrects the prior claim that the journey was usable: HTTP-client usable did not mean browser usable.

## Measured cause and control

Application config/settings.py sets SECURE_REFERRER_POLICY='no-referrer'. Chromium sent Origin: null (the literal string) and no Referer on the same-site form POST. Django rejected it. In an otherwise identical synthetic runtime-only control, SECURE_REFERRER_POLICY='same-origin' made Chromium send its actual origin; loginPOST returned302 and GET/corpus/ returned200. CSRF remained enabled. No null origin was whitelisted and no middleware was disabled.

That is evidence for the policy interaction, NOT a complete fix validation. The control browser then returned TargetClosedError before confirming the workspace heading. The full sequence search/read/save/report/logout/recovery/mobile was NOT completed or accepted. No screenshot was produced; the failure ARIA snapshot and request/response trace are committed. The control browser closure is a separate unresolved runtime observation, not attributed to an application defect without evidence.

## Reproduction and evidence

Committed raw receipt: docs/agents/evidencia/2026-09-21-browser-evidence.json. It preserves complete exceptions, browser version, request origins, HTTP responses, console records and server command/stdout/stderr for original run3 and diagnostic control3. It deliberately excludes duplicate setup logs and other attempts; no claim that all local custody is in this receipt. Complete local custody115587bytes SHA256c51b3a34ece637c47ee1fdd71839916e357092991386c4259a57b79c8a2cc0b8 remains in the persistent test workspace.

Executed instrument: docs/agents/evidencia/2026-09-21-browser-journey.py, SHA256e21275477df87ea2084d935d0f7c39115fa4159cd1a35c6bc9eae8a6ac8cf81a. Python and Playwright1.63.0. Environment: CORPUS_SOURCE points to a clean git archive ofba9646bf, CORPUS_BROWSER_ROOT to a NEW empty scratch directory, CORPUS_PYTHON to the venv containing the app's pinnedrequirements. Run python instrument.py. On this brain-env, LD_LIBRARY_PATH was explicitly set to the existing sysroot browser libraries; ldd verified no unresolved libraries for the headless shell. CORPUS_DIAGNOSTIC_REFERRER=same-origin activates the separately labeled causalcontrol; omit it to test original configuration.

Harness launches Gunicorn on127.0.0.1 with one worker and synthetic database. Only mailcapture differs: file backend into scratch, exclusively.invalid addresses, no SMTP. Logging handlers were added for diagnosis; no permission logic modified. Test clicks and assertions are in the instrument; initial original-run AssertionError propagates as nonzero script failure. The server's exit0 in receipt means successful cleanup, NOT successful browser acceptance. No process returncode was captured for background instrument subprocesses, so do not invent a measured exit1; the unhandled traceback/outcomeFAIL is the observed evidence.

## Attempts and own errors

First heredoc wrapper failed shellsyntax; corrected using python-c. Registry query confirmed Playwright1.63.0; cacheprobe hit/rootpermissiondenied, not absentbrowser. Isolated pip/Chromium install succeeded; first shell launch failed libglib. Reused existing sysroot and verified ldd; Chromium then navigated and reproduced403. same-origin controls reachedHTTP302/200 then TargetClosed; one45second bounded control timed out and its exact test server PIDs were stopped after reading/proc/cmdline. ps is absent, not a permissions outage. Fullchromium-channel attempt failed missinglibcups before navigation; do not conflate it with the headless-shell's actual product result. No apt/system mutation, external exposure, lab events or real credentials.

Original and completed control server finally blocks stopped their own servers. Timed-out control's server was manually stopped by exact PID/command match. No unrelated process intentionally touched. Full browser closure diagnosis, portable library setup and completion of downstream assertions remain outstanding.

## Proposed next change, not applied

Change the referrer policy to same-origin rather than disablingCSRF; add a regression that sends the browser's real Origin and a browser acceptance job; rerun the entire desktop/mobile journey including privateownership, withdrawal and reset. Keep no-store, CSP and CSRF. Inspect openPRfiles before changing them. No merge/deployment authority inferred.

Because the requested full acceptance cannot be completed against the unchanged build, report the blocker and get go-ahead before modifying product code. This evidence branch is not a covertfix.

## QA score, correctly scoped

Measurement/report41/45=91.11/100: completeness13/15 (full acceptance not completed, explicitly bounded); reasoning9/10 (realbrowser/control, runtime closure separate); documentation10/10 (exact source/commands/exceptions); diagnostic improvement4/5 (browserOrigin is new falsifier); QA5/5 (FAIL preserved, no green invented).55points N/A: productexecutability/security/testing/DevOps do not grade this report. Product itself fails browser acceptance; previous84/100 is not upgraded and cannot override the red. RolesTester/Security/QA are same-operator analysis, not external reviewer approval.
