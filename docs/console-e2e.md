# Console browser checks

Implementation base: `6162bcaabc4d3c88dfa119d0f472f8d51b450662`.

## Status

JavaScript syntax check passed. Browser execution is **not verified** in the
build environment: Chromium failed before navigation because process singleton
socket creation was prohibited (`Operation not permitted`). This is a harness
environment failure, not a Console test failure or pass. Run locally before
claiming the suite passes or marking a PR ready for review.

## Windows setup and run

From the repository root in PowerShell:

```powershell
cd tests/e2e
npm install
npx playwright install chromium
npm test
```

Return to the repository root afterwards with `cd ../..`.
Only test dependencies and Playwright's Chromium browser are installed.
The test runner starts and closes a local static server itself; no separate
server, Python process or Ollama service is required.

Results: `tests/e2e/results/console_e2e_report.json`. Screenshots are saved there
for individual scenario failures when a page exists. Setup failures before a
page opens cannot provide a screenshot. Exit code is nonzero on any failure.
The results folder and node_modules are ignored by this test directory's
.gitignore. A package-lock generated during install may be committed after review.

Optional existing browser: set `E2E_BROWSER_PATH` to its executable. Default uses
Playwright's installed Chromium. `E2E_OUTPUT_DIR` can override the output folder.

## Coverage (38 planned scenarios)

18 scenarios at each of 1280×680 and 1280×800:
- Real model/default display and hidden mock banner.
- Each of the five numeric range-input events and resulting prediction display.
- Both fuel buttons, plus/minus buttons, reset after multiple edits.
- Earth/Moon/Mars presets, including exact 0.694-atm model input and unchanged diameter.
- Negative-rate clamp using a slider-corner numerical stress case.
- Existing out-of-range, exclusive-gas, gas-total and nearest-test gap warnings.
- Document overflow, key element visibility and uncaught JavaScript errors.

Two file:// scenarios: actual exported model and blocked model.js fallback.
Fallback must show the Mock banner and hide the real-model source chip.

## Oracle and scope

Expected predictions are independently calculated in the test runner from the
committed exported coefficients, never by calling the page's predict function.
A read-only `window.__flame.state` hook confirms the unrounded model inputs.
Inputs are changed using range DOM events, browser button clicks and the Reset
keyboard shortcut. No app setter is called and production code is not changed.

This extends numerical parity checks through input event handling and rendering.
It does not independently refit Python (that is Phase 2), establish calibration,
prove scientific warning thresholds, test physical slider dragging/gamepad input,
inspect every element for clipping, or validate live hosted/handheld behavior.
Current warnings are tested as implemented; no new Limited Evidence policy is
introduced. Moon/Mars pressure may display rounded to 0.69 while the intended
model value remains 0.694; the test checks that distinction explicitly.

If warnings or selectors intentionally change, review the expected behavior
before adjusting tests. Do not remove assertions simply to obtain a pass.
