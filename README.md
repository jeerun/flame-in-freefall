# Flame in Freefall crew fire console

Team Second Toe, 2026 NASA Space Apps Challenge (Universal Event).
Challenge: Flame in Freefall: SI-Powered Fire Safety Insights from Microgravity Combustion Data.

## What it is

A handheld fire-safety console for spacecraft crew. Set the cabin oxygen, pressure,
carbon dioxide, fuel and droplet size, and it shows the chance a droplet flame keeps
burning, the burning rate, and a plain-language explanation. It warns when the
settings fall outside what the experiments actually tested.

Status: work in progress. The console currently runs on mock numbers until
`console/model.js` is exported from real NASA data.

## Folders, and who owns each

| Folder | Owner (role) | What goes here |
|---|---|---|
| `data/raw/` | 1 Data | Files exactly as downloaded from NASA PSI. Never edit these. |
| `data/clean/` | 1 Data | One tidy CSV built from the raw files, plus notes on each column. |
| `model/` | 2 Model | Training script. It writes `console/model.js`. |
| `console/` | 3 Console | `index.html`, the page that runs on the Legion Go. |
| `docs/sources.md` | 4 Science | Every NASA dataset and source we use. |
| `docs/submission.md` | 5 Submission | Draft text for the submission form. |

One owner per folder. If you need a change in someone else's folder, ask them.

## Run the console

Open `console/index.html` in Edge or Chrome and press F11. No install, no internet.
Controls: Up/Down pick a setting, Left/Right change it, A explain, B close, Y reset.
Touch and keyboard also work.

## Working together

1. Pull before you start. Push small changes often.
2. Stay in your own folder.
3. Not using git? On github.com open your folder, then Add file > Upload files.
4. Stuck for more than 30 minutes? Say so in the group chat.

## Data

To be filled in by role 1 and role 4: dataset names, PSI identifiers, links, date downloaded.

## Use of AI

We used Claude (Anthropic) for planning, for the first version of the console code,
and for help with data-cleaning and training scripts. Keep this section current:
the submission form asks where and how AI was used.
