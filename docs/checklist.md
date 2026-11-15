# Pre-submission checklist

Target: submit by 9 PM Sunday Nov 15. The form closes at 11:59 PM in the team
owner's local time (confirm on the team page). "Submit for Judging" is final.

## Repo

- [x] Repo is Public. Checked Nov 14 without being signed in:
      https://github.com/jeerun/flame-in-freefall opens and shows the files.
- [x] `console/model.js`, `console/research.js` and `console/tables.js` are committed,
      so a fresh download shows real numbers, the NASA research page and the Oxygen map.
- [x] The live copy opens without signing in (checked Nov 15):
      https://jeerun.github.io/flame-in-freefall/ . After any later change to
      `console/`, republish it: `git subtree push --prefix console origin gh-pages`.
- [ ] Final check from a clean copy: on github.com use Code > Download ZIP, unzip,
      open `console/index.html`. The header must read "Model: NASA PSI-69 FLEX,
      199 tests" with no yellow banner, and show the tabs "Flame console" and
      "NASA research".
- [ ] README status section matches reality on the day.
- [ ] No file in `data/raw/` was edited.

## Draft PR handheld recheck

- [ ] Open the draft build in landscape. NASA research opens directly. Check the
      controller status under Controls and all six settings on the Flame console.
      The optional `/#title` presentation screen still accepts A.
- [ ] In the Oxygen map, select an investigation and switch between the three chart
      views. LT and RT on Research open the two evidence activities. A reveals a
      result and B returns. In the zoomed FLEX map, A opens Find counterexample.
- [ ] On the Moon Base preset, check the warning about three nearby disruptions.
      In Ignite or Ember, B should close the dialog and return to the previous control.

## Earlier Legion Go runs recorded by the owner

How to get it onto the handheld, three ways, with fixes for a connection that
fails: `docs/legion-go-setup.md`.

Ticked on Nov 15 from the run on the real handheld, with the owner pressing the
controls: see "Verified on the real Legion Go" in `CLAUDE.md` for what was seen and how.
Both controller runs were on the page before the model switch of Nov 15. The page with
the per-fuel model has had a screen check on the handheld, not a controller run.

- [x] Opens in Edge, F11, nothing needs scrolling. (Full screen came from Edge's
      start-fullscreen switch, not the F11 key: 1280x800, no page scrolls.)
- [x] Chip reads "Controller connected" after pressing a button. If the stick moves a
      mouse pointer, switch the device to gamepad mode.
- [x] D-pad picks and changes settings one step at a time. The left stick slides the
      selected bar: a light push creeps, a full push sweeps. A opens the explanation,
      B closes it, Y resets.
- [x] The start screen appears and A starts. The first page is "NASA research".
- [x] RB goes to "Flame console", then "Fire drill"; LB goes back.
- [x] NASA research: Left and Right change the question (four of them), Up and Down
      move through the list, X switches to the orbit view, and there the right stick
      points at an investigation. Y opens the Oxygen map: Up and Down pick an
      investigation, Left and Right change the level of detail, B closes.
- [x] Flame console: X steps the cabin air through "Earth air", "Moon Base" and "Mars
      (assumed)", and the background becomes the Earth, the Moon or Mars. The star map
      shows under the reading. The right stick picks a star
      (yellow ring), RT replays that test in the flame picture, pressing the right
      stick moves the settings onto it.
- [x] Flame console: LT opens Ignite (A runs it again, B closes). The View button
      zooms the star map to the whole screen (Left and Right change the detail, B
      closes).
- [x] A banner appears at the top, with a sound and a buzz, when the settings leave
      what NASA tested (set carbon dioxide and helium both above zero) and when the
      risk turns high (press X for Moon Base).
- [x] Flame console: A opens the explanation with three boxes (prediction, evidence,
      limitations). There, X and Y open the two sections and LT saves a baseline and
      opens the comparison. Changing a bar updates column B; B closes.
- [x] Fire drill: Left and Right guess, the test replays, A goes on, Y starts a new game.
- [x] Sound plays after the first touch or key press, and M mutes it. The controller
      buzzes when the red box appears and on a wrong Fire drill answer. If sound or
      rumble is missing, nothing is broken: not every browser and controller has them.
      (On the handheld the sound started from the A button alone, with no touch. Key M
      was not tried, there is no keyboard: the Sound button on screen muted it.)

## Local AI, PC and Legion Go together (owner only)

- [ ] On the PC, `Start dashboard.bat` prints "AI: ready, gemma4:12b on this team's
      NVIDIA GeForce RTX 5080". The first time, Windows asks about the firewall: tick
      the kind of network the PC is on (Private, Public, or both) and choose Allow.
      A VPN on the PC can keep the handheld out: pause it for the test.
- [ ] When the Legion Go opens the address, the PC window prints "New device
      connected", and `http://localhost:8000/who` on the PC lists it.
- [x] On the Legion Go, on the same Wi-Fi, the address the window printed opens the
      dashboard, the start screen lists "Ember: the on-board AI", and the "Ask Ember"
      button is in the top bar. (Seen on Nov 15 over Tailscale at `http://run/`, not
      over the Wi-Fi address.)
- [x] The Menu button opens Ember and an answer appears within a few seconds, ending
      with the model name and the graphics card. With "Voice: on" it is read aloud.
      (2.2 s on Nov 15.)
- [x] In Fire drill, a line "Ember, the team's on-board AI, thinks: ..." appears
      after each answer.
- [x] On the Flame console, pressing the left stick (or the "Send to base" button)
      shows "Sent 252 real FLEX tests to ...", and the file
      `flex_psi69_tests_with_predictions.csv` is in the folder `exports` on the PC.
      (Nov 15 on the handheld: the banner read "Sent 252 real FLEX tests to RUN,
      folder "exports"" and `http://run/tests.csv` answered with 252 rows. The folder
      on the PC itself was not opened.)
- [ ] Optional, the handheld's own model: on the Legion Go, `Setup Legion Go.bat` ran
      to the end (Python, Ollama, the model `gemma4:e2b`), and `Start on Legion Go.bat`
      was given the PC's address. In Ember, a row "Ember thinks on:" offers both
      machines and X switches. Close the window on the PC: within about 20 seconds a
      banner says the big machine is out of reach, and Ember still answers.
      This has only been tried with two copies of the server on the PC.
      (Nov 15 on the handheld: the setup ran to the end after a fix to its two winget
      lines, both machines are offered and X on the controller switches, the handheld's
      model answered in 3.7 to 14.5 s, and a copy with a peer that cannot answer
      answered by itself. Not ticked: the PC's window was not closed, so the "out of
      reach" banner was not seen. Details in `CLAUDE.md`.)
- [ ] A teammate has read `docs/ember-check.md` and filled in the "Human verdict"
      line under each of the 18 answers. Until then, say "not checked by a person"
      wherever Ember's accuracy comes up.
- [ ] With the PC window closed, `console/index.html` opened as a file still works,
      without Ember.
- [x] The red "Outside the tested range" box appears with carbon dioxide and helium
      both above zero.

## Demo video (owner only)

- [ ] Review the included captioned desktop demo or record the alternative handheld demo in `docs/demo-script.md`.
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
- [ ] NASA data: names the PSI repository, PSI-69 FLEX and the seven other
      investigations whose test tables feed the Oxygen map, with their links. Needed
      to be eligible for global awards.
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
