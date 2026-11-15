# Console browser checks

Written by a team member (ppppreawaaaa, pull request #4) for the page as it was at
commit `6162bca`. Brought up to date with the per-fuel model and run on the team's
PC on 15 November 2026.

## Status

The draft PR passed all 40 scenarios again in Microsoft Edge 157.0.4341.46 with
Playwright 1.65.1. The suite now opens the default dashboard directly, reads the
model source from Controls, and checks the completion meter’s conditional-outcome
label. It retains the per-fuel numeric comparisons. The tested dashboard is in
commit `69c3424`. The earlier run is recorded below.

**40 of 40 scenarios pass.** Run on 15 November 2026:

| | |
|---|---|
| Page tested | `console/` at commit `f8374e5` |
| `index.html` SHA-256 | `a0d568a3c6e6990be59ab428e6ce4e255006a4332e8756c0935d4d0ba873b731` |
| `model.js` SHA-256 | `148248e0e18c84eb74747935bd59c59868acf7054a107242235aaa3591e15372` |
| Browser | Microsoft Edge 157.0.4341.46, headless, Windows 11 |
| Driver | Playwright 1.65.1, the copy inside Python's `playwright` package |

Not run on this PC: the npm setup below (`playwright` 1.62.1 with its own Chromium).
The pull request reports 38 of 38 with it, on the page before the model switch.
Not covered by any run: the published GitHub Pages copy, a real gamepad, the real
Legion Go.

## What changed on 15 November 2026

The suite was written for the earlier one-slope model. Run as written against
today's page it passed 34 of 38 scenarios. The four failures were exactly the two
things that had changed on the page since:

- **Each fuel has its own slopes.** The oracle's formula is now
  `intercept + fuel[fuel] + sum((coef[key] + fuel_coef[fuel][key]) * value)`, the
  one in `docs/per-fuel-model.md`. It still reads an export without `fuel_coef`.
- **The page shows no chance below 1 % or above 99 %.** The oracle applies the same
  limit after rounding.

Added at the same time:

- One scenario for each screen size, `display_limits_1_and_99`. Heptane in Moon
  Base air: the model's own number is 99.87 %, the page must show 99 and 1. Heptane
  with oxygen at its lowest setting: 0.01 %, the page must show 1 and 99.
- `E2E_PLAYWRIGHT_PATH`, so the suite runs without npm (below).

No assertion was removed or loosened.

## Does the suite notice a broken page?

Checked on 15 November 2026 by running it on four temporary copies of the page,
each with one deliberate fault. All four were caught:

| Fault put into the copy | Scenarios that failed, at both screen sizes |
|---|---|
| The page ignores each fuel's own slopes | `fuel_switch` |
| No 1 to 99 % display limit | `negative_rate_clamp`, `display_limits_1_and_99` |
| Burning rate not held at zero or above | `negative_rate_clamp` |
| Moon Base preset pressure 0.69 instead of 0.694 atm | `preset_moon`, `display_limits_1_and_99` |

## Run it

The runner starts and closes its own local web server. No Python server and no
Ollama are needed. From the repository root in PowerShell, one of:

### With Python's Playwright package (what the run above used)

Needs `pip install playwright` and Microsoft Edge or Chrome.

```powershell
$driver = python -c "import playwright, pathlib; print(pathlib.Path(playwright.__file__).parent / 'driver')"
$env:E2E_PLAYWRIGHT_PATH = "$driver\package"
$env:E2E_BROWSER_PATH = "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
& "$driver\node.exe" tests\e2e\console_e2e.cjs
```

### With npm

```powershell
cd tests/e2e
npm install
npx playwright install chromium
npm test
```

Return to the repository root afterwards with `cd ../..`.
Only test dependencies and Playwright's Chromium browser are installed.

Results: `tests/e2e/results/console_e2e_report.json`. Screenshots are saved there
for individual scenario failures when a page exists. Setup failures before a
page opens cannot provide a screenshot. Exit code is nonzero on any failure.
The results folder and node_modules are ignored by this test directory's
.gitignore.

Optional settings: `E2E_BROWSER_PATH` is the browser to use instead of Playwright's
installed Chromium. `E2E_PLAYWRIGHT_PATH` is the folder of a Playwright package to
use instead of the one installed with npm. `E2E_OUTPUT_DIR` overrides the output
folder.

## Coverage (40 scenarios)

19 scenarios at each of 1280×680 and 1280×800:
- Real model/default display and hidden mock banner.
- Each of the five numeric range-input events and resulting prediction display.
- Both fuel buttons, plus/minus buttons, reset after multiple edits.
- Earth/Moon/Mars presets, including exact 0.694-atm model input and unchanged diameter.
- Negative-rate clamp using a slider-corner numerical stress case.
- The 1 % and 99 % display limits.
- Existing out-of-range, exclusive-gas, gas-total and nearest-test gap warnings.
- Document overflow, key element visibility and uncaught JavaScript errors.

Two file:// scenarios: actual exported model and blocked model.js fallback.
Fallback must show the Mock banner and hide the real-model source chip.

Not covered yet: the explanation panel, Save baseline and Compare (their logic is
tested by `tests/test_console_features.cjs`), the star map, the Oxygen map, the
NASA research page, Fire drill and Ember.

## Oracle and scope

Expected predictions are independently calculated in the test runner from the
committed exported coefficients, never by calling the page's predict function.
A read-only `window.__flame.state` hook confirms the unrounded model inputs.
Inputs are changed using range DOM events, browser button clicks and the Reset
keyboard shortcut. No app setter is called and production code is not changed.

This extends numerical parity checks through input event handling and rendering.
It does not independently refit Python (`model/check_parity.py` does), establish
calibration, prove scientific warning thresholds, test physical slider
dragging/gamepad input, inspect every element for clipping, or validate live
hosted/handheld behavior. Current warnings are tested as implemented; no new
Limited Evidence policy is introduced. Moon/Mars pressure may display rounded to
0.69 while the intended model value remains 0.694; the test checks that
distinction explicitly.

If warnings or selectors intentionally change, review the expected behavior
before adjusting tests. Do not remove assertions simply to obtain a pass.

## Use of AI

We could not confirm whether AI tools helped write the suite, so treat it as
possibly AI-assisted. The update of 15 November (the oracle, the added scenario,
the first run and the fault check) was done with Claude (Anthropic).
