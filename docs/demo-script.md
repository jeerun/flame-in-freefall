# Demo video script (30 seconds)

Rules from the challenge: up to 30 seconds, English subtitles, hosted outside the
Space Apps site, public, no login.

The readings below were checked on the team's PC in a desktop browser with a
simulated gamepad. They have not been checked on the Legion Go itself yet: do the
"Before filming" list first.

## Before filming

1. On the PC with the RTX 5080: double-click `Start dashboard.bat` in the repo folder
   (or run `py server/serve.py --lan`). The window prints two addresses and
   "Local AI: ready". The first time, Windows asks about the firewall: choose Allow on
   private networks. Leave the window open.
2. On the Legion Go, on the same Wi-Fi, open Edge at the address the window printed
   for the Legion Go (it looks like `http://192.168.x.x:8000`) and press F11.
3. Top right must show the button "Ask the AI" and "Model: NASA PSI-69 FLEX, 199
   tests", and the top bar the tabs "Flame console" and "NASA research". No "Ask the
   AI" button means the Legion Go is not reaching the PC: check the Wi-Fi and the
   firewall answer.
4. Press any button. The chip must change to "Controller connected". If the stick
   moves a mouse pointer instead, the device is in desktop mode: switch it to
   gamepad mode.
5. Check that nothing needs scrolling.
6. Press Y to reset. Fuel reads Heptane, Oxygen 21.0 %, the big number 35 %.
7. Ask the AI one question now and wait for the answer, so the model is warm.
8. Film in landscape with both hands and the screen in frame, screen brightness up,
   room lights down so the screen does not glare.

If the Legion Go cannot reach the PC in time: film shots 1, 2, 4 and 5 on the Legion
Go with the page opened as a file (`console/index.html`), and film shot 3 on the PC
screen at `http://localhost:8000`. Say in the subtitle that the AI runs on the PC.

Buttons use the Xbox layout: A bottom, B right, X left, Y top, RB the right bumper,
Menu the small button with three lines.

## Shots

| # | Time | Press on the Legion Go | What the screen shows | Subtitle (English) |
|---|---|---|---|---|
| 1 | 0:00 to 0:03 | Nothing. Hold the device still. | Heptane, oxygen 21.0 %, big number 35 %, green "Inside the tested range". | Fire in space does not behave like fire on Earth. |
| 2 | 0:03 to 0:08 | Press X once. | "Moon Base (expected)" lights up. Oxygen 30.0 %, pressure 0.69 atm. Big number jumps to 90 %, bar turns red, the flame picture grows. | Moon Base air, 30% oxygen: our model gives this flame a 90% chance to burn all its fuel. |
| 3 | 0:08 to 0:15 | Press Menu. | "Ask the AI" opens and answers by itself in a few seconds: a short interpretation of the reading, ending "Answered in ... s by gemma4:12b on this team's NVIDIA GeForce RTX 5080". | An AI model on our own RTX 5080, no cloud, explains it from NASA data only. |
| 4 | 0:15 to 0:19 | Press B. D-pad Down three times (Carbon dioxide), tap Right 5 times. Down once (Helium), tap Right once. | Red box: "Outside the tested range. No experiment mixed carbon dioxide and helium. Do not rely on these numbers." The numbers dim, the flame picture becomes a question mark and the controller buzzes. | Where NASA never tested, it says so instead of guessing. |
| 5 | 0:19 to 0:24 | Press RB. D-pad Right twice (Suppression). Down once. | "NASA research" page. "Ranked for suppression: 9 of 24 investigations", BASS first, FLEX second and selected, its summary on the right. | It summarizes and ranks 24 NASA combustion investigations by what you need. |
| 6 | 0:24 to 0:28 | Press RB. Then Left or Right to guess. | "Fire drill" page: the settings of a real NASA test, then the reveal: a green "Correct." or red "Not this time." box, the flame burning out its droplet or dying, and the score "You" against "Model". | And it is a game: guess how a real NASA test ended, and try to beat the model. |
| 7 | 0:28 to 0:30 | Nothing. End card over the last frame. | Text card: "Flame in Freefall Crew Fire Console. Team Second Toe. Data: NASA PSI. AI runs locally." | Team Second Toe. NASA PSI data. AI on our own hardware. |

The AI writes a different answer for a different reading, and the Fire drill picks
its tests at random, so do not script their exact words. If the video runs long,
speed up shots 4 and 5 in the edit, or drop shot 6, before cutting the AI answer or
the red warning.

## After filming

- Burn the subtitles into the video (do not rely on a caption track).
- Check the length is 30 seconds or less.
- Upload somewhere public (for example YouTube, visibility Public), then open the
  link in a private browser window to confirm it plays without logging in.
- Paste the link into `docs/submission.md` and the form.
