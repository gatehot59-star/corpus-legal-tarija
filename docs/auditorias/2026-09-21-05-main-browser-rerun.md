# Browser flow rerun on current main

Date: 21-Sep-2026 ART. Read-only runtime check, synthetic fixtures only, no product changes, merge, or deployment.

## Subject

Current `main`: `069d61f8ea6ccc3506a2e87fd8a7a173b3efde1c`.

## Result

The browser flow does **not** pass on current main.

The browser launched correctly with the repaired Fontconfig environment and reached the application. The anonymous workspace check passed with `403`. The login POST then returned `403` CSRF, and the page showed `Prohibido (403)`, so the flow stopped before search, reading, saving, reporting, logout, recovery, and revocation.

This is the expected old-main behavior: current main still has:

```text
SECURE_REFERRER_POLICY = "no-referrer"
```

The fix branch changed that to `same-origin` and added the causal regression. That fix is not present in current main.

## Measured controls

- Chromium: 153.0.8010.12, Playwright 1.63.0.
- `manage.py migrate`: exit 0.
- Synthetic fixture provisioning: exit 0.
- Anonymous workspace: `403`, expected.
- Browser login: `403` CSRF, expected failure for this main head.
- Server stopped cleanly.
- No real accounts, email, external traffic, merge, or deployment.

## Verdict

**Current main is not end-to-end usable in the browser.** The missing same-origin fix is the immediate blocker. The Django backend/unit suite can pass on main, but that is not the complete user flow.

The next product decision is whether to restore the tested PR24 fix into main. The PRs that were closed are not merged, so closing them did not integrate their code.
