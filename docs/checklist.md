# Pre-submission checklist

Target: submit by 9 PM Sunday Nov 15. The form closes at 11:59 PM in the team
owner's local time (confirm on the team page). "Submit for Judging" is final.

## Repo

- [x] Repo is Public. Checked Nov 14 without being signed in:
      https://github.com/jeerun/flame-in-freefall opens and shows the files.
- [x] `console/model.js` and `console/research.js` are committed, so a fresh download
      shows real numbers and the NASA research page.
- [ ] Final check from a clean copy: on github.com use Code > Download ZIP, unzip,
      open `console/index.html`. The header must read "Model: NASA PSI-69 FLEX,
      199 tests" with no yellow banner, and show the tabs "Flame console" and
      "NASA research".
- [ ] README status section matches reality on the day.
- [ ] No file in `data/raw/` was edited.

## Console on the Legion Go (owner only)

- [ ] Opens in Edge, F11, nothing needs scrolling.
- [ ] Chip reads "Controller connected" after pressing a button. If the stick moves a
      mouse pointer, switch the device to gamepad mode.
- [ ] D-pad and left stick pick and change settings, A opens the explanation, B closes
      it, Y resets.
- [ ] X switches the cabin air between "Earth-like air" and "Moon Base (expected)".
- [ ] RB goes to the "NASA research" page, then to "Fire drill"; LB goes back. On the
      research page Left and Right change the question, Up and Down move through the
      list. On Fire drill, Left and Right guess, A goes on, Y starts a new game.
- [ ] The controller buzzes when the red box appears and on a wrong Fire drill answer.
      If it does not, nothing is broken: some browsers and controllers have no rumble.

## Local AI, PC and Legion Go together (owner only)

- [ ] On the PC, `Start dashboard.bat` prints "Local AI: ready, gemma4:12b on NVIDIA
      GeForce RTX 5080". The first time, Windows asks about the firewall: choose Allow
      on private networks.
- [ ] On the Legion Go, on the same Wi-Fi, the address the window printed opens the
      dashboard and the "Ask the AI" button is in the top bar.
- [ ] The Menu button opens "Ask the AI" and an answer appears within a few seconds,
      ending with the model name and the graphics card.
- [ ] With the PC window closed, `console/index.html` opened as a file still works,
      without the "Ask the AI" button.
- [ ] The red "Outside the tested range" box appears with carbon dioxide and helium
      both above zero.

## Demo video (owner only)

- [ ] Filmed following `docs/demo-script.md`.
- [ ] 30 seconds or less.
- [ ] English subtitles burned into the picture.
- [ ] Hosted outside the Space Apps site.
- [ ] The link opens and plays in a private browser window without logging in.
- [ ] Link pasted into `docs/submission.md`.

## Form on the Space Apps site (owner only)

Copy each field from `docs/submission.md`.

- [ ] Project name, in English.
- [ ] High-level summary, in English.
- [ ] Link to project demo.
- [ ] Link to final project: https://github.com/jeerun/flame-in-freefall
- [ ] Detailed project description, in English.
- [ ] NASA data: names the PSI repository and PSI-69 FLEX with their links. Needed to
      be eligible for global awards.
- [ ] Space agency partner and other data: "None".
- [ ] Use of artificial intelligence, in English, including anything teammates did
      with AI outside this repo.
- [ ] Every "TO ADD" in `docs/submission.md` is filled before copying.
- [ ] No Thai or other non-English text in any field.

## Team

- [ ] All five members have joined the team on the Space Apps site.
- [ ] "Looking for members" is unticked after all five are in.
- [ ] Everyone has read the summary and agrees with it.

## Last step

- [ ] Read the whole form once more, then press "Submit for Judging".
