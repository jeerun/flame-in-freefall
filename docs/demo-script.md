# Demo video script (30 seconds)

Rules from the challenge: up to 30 seconds, English subtitles, hosted outside the
Space Apps site, public, no login.

The sequence below was replayed on the team's PC in a desktop browser with a
simulated gamepad on Nov 15, with Ember answering from the RTX 5080. Nothing has
been checked on the Legion Go itself yet: do the "Before filming" list first.

## Before filming

1. On the PC with the RTX 5080: double-click `Start dashboard.bat` in the repo folder
   (or run `py server/serve.py --lan`). The window prints two addresses and
   "AI: ready". The first time, Windows asks about the firewall: tick the kind of
   network the PC is on (Private, Public, or both) and choose Allow. Leave the window
   open. If the Legion Go cannot connect, see `docs/legion-go-setup.md`.
2. On the Legion Go, on the same Wi-Fi, open Edge at the address the window printed
   for the Legion Go (it looks like `http://192.168.x.x:8000`) and press F11.
3. The start screen must list four things, the last one "Ember: the on-board AI". If
   Ember is missing, the Legion Go is not reaching the PC: check the Wi-Fi and the
   firewall answer.
4. Press A. If nothing happens and the stick moves a mouse pointer instead, the device
   is in desktop mode: switch it to gamepad mode. Top right must read "Controller
   connected".
5. Check that nothing needs scrolling on any of the three pages (RB turns the page).
   On the research page press Y: the Oxygen map must open with "2 Every test" lit.
   If another level is lit, press Left or Right until it is, then B. The page
   remembers the level.
6. Touch the screen once, then press the Menu button and wait for Ember's answer.
   This warms the model up and lets the browser play sound and voice. If you hear
   nothing, sound and voice are simply off on this device: the video still works.
7. Reload the page (F5) to get back to the start screen before filming.
8. Film in landscape with both hands and the screen in frame, screen brightness up,
   room lights down so the screen does not glare.

If the Legion Go cannot reach the PC in time: film everything except shot 3 on the
Legion Go with the page opened as a file (`console/index.html`), and film shot 3 on
the PC screen at `http://localhost:8000`. Say in the subtitle that the AI runs on the PC.

Buttons use the Xbox layout: A bottom, B right, X left, Y top, RB the right bumper,
RT the right trigger, Menu the small button with three lines.

## Shots

| # | Time | Press on the Legion Go | What the screen shows | Subtitle (English) |
|---|---|---|---|---|
| 1 | 0:00 to 0:03 | Nothing, then press A. | Start screen "Flame in Freefall", then the NASA research page. | NASA has decades of microgravity fire data. It is hard to find, compare and read. |
| 2 | 0:03 to 0:09 | D-pad Right three times (Cabin air). Press Y, wait a second, press D-pad Right. | "Ranked for cabin air: 8 of 24 investigations". Then the Oxygen map: every test of seven investigations as a dot, then the same tests against pressure with the Moon Base air marked in orange. Headline: "Of 746 microgravity tests ... 20 were run in Moon Base air". | It ranks 24 NASA investigations for your question, and counts their tests: of 746, only 20 ran in Moon Base air. |
| 3 | 0:09 to 0:14 | Press B, then Menu. | "Ask Ember" opens and answers by itself in a few seconds, aloud: which investigations matter most for a Moon Base cabin. It ends "Answered in ... s by Ember (gemma4:12b on this team's NVIDIA GeForce RTX 5080)". | Ember, an AI model on our own RTX 5080, interprets them. No cloud, no internet. |
| 4 | 0:14 to 0:19 | Press B, then RB (Flame console). Press X. | "Moon Base" lights up, oxygen 30.0 %, pressure 0.69 atm, the big number jumps to 90 %, a banner warns "High fire risk" and the background becomes the lunar surface. Below, the star map: every star is a real NASA test. | It predicts a droplet flame from 252 real FLEX tests. Moon Base air: 90% chance to burn all its fuel. |
| 5 | 0:19 to 0:24 | Push the right stick toward a star, then press RT. | A yellow ring picks a star, the heading names that test, and the flame picture replays it: the droplet shrinks, a timer runs, the flame goes out. | Every star is a real test. Pick one and replay it from NASA's measurements. |
| 6 | 0:24 to 0:28 | Press RB (Fire drill). Press Left or Right to guess. | The settings of a real NASA test, then the reveal: "Correct." or "Not this time.", the test replayed, the score "You" against "Model". | And it is a game: guess how a real test ended, and try to beat the model. |
| 7 | 0:28 to 0:30 | Nothing. End card over the last frame. | Text card: "Flame in Freefall Crew Fire Console. Team Second Toe. Data: NASA PSI. AI runs locally." | Team Second Toe. NASA PSI data. AI on our own hardware. |

Ember writes a different answer each time, the right stick may land on a different
star, and the Fire drill picks its tests at random, so do not script their exact
words. A star with a grey cross cannot be replayed (NASA's record has no end
diameter for it): pick an orange or blue one. If the video runs long, speed up shots
2 and 4 in the edit, or drop shot 6, before cutting Ember's answer or the replay.

Other things worth a few seconds if you would rather show them than the game: LT
(Ignite, one run of the model drawn like FLEX footage), View on the Flame console
(the star map zoomed to the whole screen with the model's 25, 50 and 75 % lines),
or pressing the left stick (the real tests sent to the PC as a CSV file).

One thing the video leaves out for time: with carbon dioxide and helium both above
zero the console turns red, "Outside the tested range", and the controller buzzes.
Mention it in the description, or swap it in for shot 6 if you prefer honesty over
the game.

## After filming

- Burn the subtitles into the video (do not rely on a caption track).
- Check the length is 30 seconds or less.
- Upload somewhere public (for example YouTube, visibility Public), then open the
  link in a private browser window to confirm it plays without logging in.
- Paste the link into `docs/submission.md` and the form.
