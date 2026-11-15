# Pre-submission checklist

Target: submit by 9 PM Sunday Nov 15. The form closes at 11:59 PM in the team
owner's local time (confirm on the team page). "Submit for Judging" is final.

## Repo

- [ ] Repo is Public. Checked Nov 14 without being signed in:
      https://github.com/jeerun/flame-in-freefall opens and shows the files.
- [ ] `console/model.js`, `console/research.js` and `console/tables.js` are committed,
      so a fresh download shows real numbers, the NASA research page and the Oxygen map.
- [ ] The live copy opens without signing in (checked Nov 15):
      https://jeerun.github.io/flame-in-freefall/ . After any later change to
      `console/`, republish it: `git subtree push --prefix console origin gh-pages`.
- [ ] Final check from a clean copy: on github.com use Code > Download ZIP, unzip,
      open `console/index.html`. The header must read "Model: NASA PSI-69 FLEX,
      199 tests" with no yellow banner, and show the tabs "Flame console" and
      "NASA research".
- [ ] README status section matches reality on the day.
- [ ] No file in `data/raw/` was edited.

## Console on the Legion Go (owner only)

How to get it onto the handheld, three ways, with fixes for a connection that
fails: `docs/legion-go-setup.md`.

Every box in this section and the next is open again. On Nov 15 the owner and a
Claude session on the handheld went through this list on the page as it was before
the redesign (pull request 5), and 17 boxes were ticked: what was seen then, and how,
is in "Verified on the real Legion Go" in `CLAUDE.md`. The redesign moved controls and
changed wording, and the server now checks the sent file differently, so the new page
needs its own run. Notes in brackets that begin "Nov 15" are from that earlier run.

- [ ] Opens in Edge, F11, with all six Flame console settings visible in landscape.
- [ ] Controls reads "Controller connected" after pressing a button. If the stick moves a
      mouse pointer, switch the device to gamepad mode.
- [ ] D-pad picks and changes settings one step at a time. The left stick slides the
      selected bar: a light push creeps, a full push sweeps. A opens the explanation,
      B closes it, Y resets.
- [ ] The first page is "NASA research". At `/#title` the optional start screen appears and A starts.
- [ ] RB goes to "Flame console", then "Fire drill"; LB goes back.
- [ ] NASA research: Left and Right change the question (four of them), Up and Down
      move through the list, X switches to the orbit view, and there the right stick
      points at an investigation. Y opens the Oxygen map: Up and Down pick an
      investigation, Left and Right change the level of detail, B closes.
- [ ] Flame console: X steps the cabin air through "Earth air", "Moon Base" and "Mars
      (assumed)", and the background becomes the Earth, the Moon or Mars. The star map
      shows under the reading. The right stick picks a star
      (yellow ring), RT replays that test in the flame picture, pressing the right
      stick moves the settings onto it.
- [ ] Flame console: LT opens Ignite (A runs it again, B closes). The View button
      zooms the star map to the whole screen (Left and Right change the detail, B
      closes).
- [ ] Research: LT opens Earth or orbit?, RT opens Read the sensors, A reveals and B returns. In the zoomed FLEX map, A opens Find counterexample.
- [ ] A banner appears at the top, with a sound and a buzz, when the settings leave
      what NASA tested (set carbon dioxide and helium both above zero) and when the
      Moon preset has only inconclusive nearby outcomes (press X at the default heptane settings).
- [ ] Flame console: A opens the explanation with three boxes (prediction, evidence,
      limitations). There, X and Y open the two sections and LT saves a baseline and
      opens the comparison. Changing a bar updates column B; B closes.
- [ ] Fire drill: Left and Right guess, the test replays, A goes on, Y starts a new game.
- [ ] Sound plays after the first touch or key press, and M mutes it. The controller
      buzzes when the red box appears and on a wrong Fire drill answer. If sound or
      rumble is missing, nothing is broken: not every browser and controller has them.
      (Nov 15 on the handheld: the sound started from the A button alone, with no
      touch. Key M was not tried, there is no keyboard: the Sound button muted it.)

## Local AI, PC and Legion Go together (owner only)

- [ ] On the PC, `Start dashboard.bat` prints "AI: ready, gemma4:12b on this team's
      NVIDIA GeForce RTX 5080". The first time, Windows asks about the firewall: tick
      the kind of network the PC is on (Private, Public, or both) and choose Allow.
      A VPN on the PC can keep the handheld out: pause it for the test.
- [ ] When the Legion Go opens the address, the PC window prints "New device
      connected", and `http://localhost:8000/who` on the PC lists it.
- [ ] On the Legion Go, on the same Wi-Fi, the address the window printed opens the
      dashboard and the "Ask Ember" button is in the top bar.
- [ ] The Menu button opens Ember and an answer appears within a few seconds, ending
      with the model name and the graphics card. With "Voice: on" it is read aloud.
      (Nov 15 on the handheld: 2.2 s.)
- [ ] In Fire drill, a line "Ember, the team's on-board AI, thinks: ..." appears
      after each answer.
- [ ] On the Flame console, pressing the left stick (or the "Send to base" button)
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
- [ ] The red "Outside the tested range" box appears with carbon dioxide and helium
      both above zero.

## Demo video (owner only)

- [ ] Record the demo (`docs/demo-script.md`). The desktop recording made for pull
      request 5 shows the earlier model (35 % and 90 %) and must not be used.
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
