# Brief for an AI assistant working ON the Legion Go

You are on the team's Lenovo Legion Go (first generation, Windows 11), the handheld
the demo is filmed on. Another assistant session works on the team's PC (the one with
the RTX 5080) and wrote this brief. Read `CLAUDE.md` in this repo first: it holds the
project, the rules and the current status. Then `docs/legion-go-setup.md` and
`docs/checklist.md`.

Reply to the owner in Thai, short, answer first. Everything in the repo (code, docs,
commit messages) is in English.

## What is already true

- The dashboard is finished and tested on the PC in a desktop browser with a simulated
  gamepad. Almost nothing has been verified on this device. That is your job.
- The PC serves the dashboard and its AI ("Ember") to this device over Tailscale at
  `http://run/` (try `curl http://run/ai`: it must answer with JSON that lists
  "brains"). The owner already opened it in Edge here and Ember answered. Do not
  change anything on the PC, and leave Tailscale as it is.
- Deadline: Sunday Nov 15, 11:59 PM (owner's local time, Pacific). Target: submit by
  9 PM. The feature freeze has passed: fixes only, no new features.

## Update, Nov 15, about 4 AM: a second run is needed

The first run (steps 1 to 7 below) was done on Nov 15 and is written up in `CLAUDE.md`
under "Verified on the real Legion Go". After it the page changed twice: the console
switched to the per-fuel model, and pull request 5 redesigned the page. Nothing of the
redesigned page has been seen on this device. For the second run:

- Bring the clone up to date first: `git fetch`, `git checkout main`, `git pull`. The
  branch `handheld-nov15` is merged and no longer needed. `http://run/` serves the new
  page once the PC's dashboard has been restarted after the merge. If the page looks
  unstyled there, the PC is still running the old server: tell the owner.
- What moved: the page opens on NASA research (the start screen is only at `#title`).
  The controller chip, the sound button and the key hints are in the "Controls" dialog
  in the top bar. The hint bars at the bottom are gone.
- What is new: on the research page LT opens "Earth or orbit?" and RT opens "Read the
  sensors" (D-pad up and down change the case, left and right choose an answer, A
  reveals, B closes). On the Flame console, A in the zoomed star map opens "Find
  counterexample". "Share view" sits on the research card and on the reading. The
  Oxygen map has an investigation picker. Ignite and Ember are dialogs: B must close
  them and return to the control that opened them.
- Readings to expect: heptane at the starting values 57 %. X to Moon Base: 99 %, an
  amber box "No clear outcome in nearby tests" and a banner.
- "Send to base" only accepts the file of the page the server itself serves. From this
  device's own dashboard (`Start on Legion Go.bat`) it reaches the PC only when both
  checkouts are at the same commit.
- Go through "Handheld recheck of the redesigned page" in `docs/checklist.md`, repeat
  step 2, and the controller part of step 3 only if something behaves differently,
  then step 7.

## Do these, in order, and report after each

1. **Get the repo here.** If git is installed, clone
   `https://github.com/jeerun/flame-in-freefall` to the Desktop. If not, download
   `https://github.com/jeerun/flame-in-freefall/archive/refs/heads/main.zip` and
   unzip it there. Say which you did.
2. **Measure the screen as the browser sees it.** Open `http://run/` in Edge, full
   screen (F11), and record `innerWidth`, `innerHeight`, `devicePixelRatio`. On each
   of the three pages, and with each overlay open (explanation sheet, Ember, Ignite,
   Oxygen map, zoomed star map), check that nothing needs scrolling
   (`document.documentElement.scrollHeight` must not exceed `innerHeight`) and that
   the top bar is one line. Note any console errors. The layout was built for
   1280x800 and 1280x680.
3. **Check the real controller.** With the owner pressing each control once, record
   what `navigator.getGamepads()` reports: the id, `mapping` (the code assumes
   "standard"), and the index of every button and axis. The code assumes 0 A, 1 B,
   2 X, 3 Y, 4 LB, 5 RB, 6 LT, 7 RT, 8 View, 9 Menu, 10 left-stick press, 11
   right-stick press, 12 to 15 d-pad, axes 0/1 left stick, 2/3 right stick. Also
   check: does a gamepad button alone start sound and voice, or is a touch needed
   first; does `vibrationActuator` exist and does the controller actually buzz; does
   the wheel on the right controller send `wheel` events; what the right controller
   does in FPS mode (pointer moves, which buttons click). Write down every
   difference from what the code assumes.
4. **Run the checklist.** Go through "Console on the Legion Go" and "Local AI, PC and
   Legion Go together" in `docs/checklist.md` with the owner and tick only what you
   both saw work on this device.
5. **Optional, only if the owner says yes: the handheld's own AI model.** It needs
   about 5 GB of disk and a 4.3 GB download. Tell the owner the sizes and wait for a
   yes before any install or download. Then run `Setup Legion Go.bat` (it installs
   Python and Ollama with winget; the owner answers the licence questions) and
   `Start on Legion Go.bat`, giving it the address `http://run`. Check that
   `http://localhost:8000/ai` lists the PC's model first and this device's second,
   that Ember answers from each (X in the Ember panel switches), and time the
   answers of the small model: if one takes longer than about 20 seconds, say so
   plainly. To see the fallback without touching the PC or Tailscale, start a second
   copy with a peer that cannot answer
   (`py server\serve.py --port 8001 --peer http://127.0.0.1:9 --model gemma4:e2b`)
   and confirm it answers by itself.
6. **Fix only what the real device proves broken**, in the smallest way, and say
   what you changed and how you checked it. Check any change to `console/index.html`
   at this device's size and also at 1280x680 and 1280x800. The PC session keeps
   working on `main` too: pull before you edit, commit small, push, and if a push or
   pull conflicts, stop and tell the owner instead of forcing it. After a change in
   `console/`, republish the live copy:
   `git subtree push --prefix console origin gh-pages`.
7. **Write down what you verified** in the Status section of `CLAUDE.md` (what was
   seen working on the real Legion Go, what was not, with the time) and push it.

## Rules that are easy to break

- Never type a password, a token or a sign-in code. If git needs a sign-in to push,
  the owner does it in the window that opens; if that is not possible, leave your
  change as a patch file and tell the owner.
- Before the first commit here run `git config user.name "Claude"` and
  `git config user.email "noreply@anthropic.com"` inside the repo, as on the PC, so
  the owner's address stays out of a public repository.
- Do not change firewall, VPN or other system settings: ask the owner to click.
  No public tunnels.
- Never present a number you did not measure as a result. Never edit `data/raw`.
  Never copy code from other teams.
- Only the owner films the demo and fills in the Space Apps form. When those come
  up, stop and list what the owner has to do.
