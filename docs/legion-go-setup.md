# Setting up the Legion Go

Three ways to use the handheld, from the least to the most set-up. None of this has
been done on the real Legion Go yet: the scripts were dry-run on the PC, and the
two-machine link was tried with two copies of the server on the PC. Tick the boxes
in `docs/checklist.md` as you go.

## A. The Legion Go as the screen, the PC as the brain (nothing to install)

1. On the PC with the GPU, double-click `Start dashboard.bat`. Leave its window open.
   It prints a line like `On the Legion Go (same Wi-Fi): http://192.168.x.x:8000`.
2. The first time, Windows asks whether to let Python through the firewall. Tick the
   kind of network the PC is on (Private, Public, or both) and choose Allow. If you
   are not sure which kind it is, tick both.
3. On the Legion Go, on the same Wi-Fi or router, open Edge at that address and
   press F11. Press A on the start screen.
4. Proof that it got through: the PC window prints `New device connected: ...`, and
   on the PC `http://localhost:8000/who` lists the handheld with a count of its
   requests, its questions to Ember and the files it sent.

If the Legion Go cannot open the address:

- The firewall prompt was closed without Allow. Windows then keeps a blocking rule.
  On the PC open Windows Security, Firewall and network protection, "Allow an app
  through firewall", "Change settings", find the Python entries and tick Private and
  Public for them.
- A VPN is running on the PC. Many VPN apps keep local devices out. Pause it, or
  turn on its "allow local network" setting, and start the dashboard again.
- The two devices are not on the same network, or the network keeps devices apart
  (campus and guest Wi-Fi often do). Use a phone hotspot or a home router for both.
- Double-clicking `Start dashboard.bat` a second time is harmless: it says the
  dashboard is already running and opens it.

## B. The Legion Go with its own small AI model (works with no PC and no network)

Needs internet once, about 5 GB of disk, and about 15 minutes.

1. On the Legion Go open https://github.com/jeerun/flame-in-freefall , choose Code,
   Download ZIP, and unzip it (for example on the Desktop).
2. In that folder double-click `Setup Legion Go.bat`. It installs Python and Ollama
   with winget and downloads the model `gemma4:e2b` (4.3 GB). winget shows each
   licence and asks you to agree. If Ollama was just installed and the script says
   it cannot find it, close the window and run the script again.
3. Double-click `Start on Legion Go.bat`. It asks once for the address the PC
   printed (step A1). Press Enter instead to run without the PC.
4. In the dashboard open Ember (Menu button). With both machines up, a row "Ember
   thinks on:" offers Auto, the PC and the handheld, and X switches. Close the
   dashboard window on the PC: within about 20 seconds a banner says the big machine
   is out of reach, and Ember answers from the handheld.

What to expect: the small model is slower and less careful than the one on the PC.
We have not measured it on the handheld. If its answers are poor, use way A.

## C. Away from the PC's network

Use a private network between your own devices, such as Tailscale. It also gets
around Wi-Fi that keeps devices apart, because the two machines talk through it
directly. Not tried yet.

1. Install Tailscale on the PC and on the Legion Go, signed in to the same account,
   and switch it on (Connect) on both. If another VPN is running on either machine,
   pause it: two VPNs often get in each other's way.
2. On the PC double-click `Start dashboard.bat`. With Tailscale on, the window prints
   a second line: `On the Legion Go (anywhere, both on Tailscale): http://100.x.y.z:8000`.
   If Windows asks about the firewall, tick Private as well: Windows treats the
   Tailscale network as a private one.
3. On the Legion Go open that address in Edge. Or, for the handheld's own model with
   the PC as the big machine, give that address to `Start on Legion Go.bat`.

If nobody is at the PC to answer the firewall question, Tailscale can pass the
dashboard on by itself, with no firewall change. On the PC, in two windows:

    py server/serve.py
    tailscale serve --http=80 8000

The second command prints the address, of the form `http://<pc-name>.<tailnet>.ts.net/`.
Open it on the Legion Go. The numeric address does not work this way, only the
name. It lasts until that window is closed. This was tried from the PC itself on
Nov 15 and answered; the server lists a device that arrives this way under its
Tailscale address in `http://localhost:8000/who`.

Do not use a public tunnel (`tailscale funnel` is one): the dashboard has no login.

## The Legion Go's extra controls

Tried with a simulated mouse and wheel in a desktop browser, not on the device.

- **The wheel on the back of the right controller** (or any mouse wheel). On the
  Flame console it turns the selected setting, one step per notch; point at another
  bar first and it selects that bar. Over the star map, and in the zoomed map, it
  walks through the stars. On the research page and in the Oxygen map it moves
  through the list.
- **FPS mode, the trackpad, or a mouse.** The star map can be aimed at: pointing at
  a star picks it, a click replays that test, a right-click moves the settings onto
  it. With a finger: tap a star to pick it, tap it again to replay. The picked star
  also gets two buttons, "Replay" and "Go there". Which controller buttons click in
  FPS mode depends on the profile in Legion Space.
- **The six extra buttons (Y1 to Y3, M1 to M3).** A browser only sees the standard
  gamepad buttons, so these do nothing by themselves. In Legion Space, under the
  controller settings, each can be set to a keyboard key, and the dashboard has a
  key for every function. A layout that works well:

  | Button | Set it to the key | What it does |
  |---|---|---|
  | Y1 | I | Ignite (Flame console) |
  | Y2 | Z | Zoom the star map |
  | Y3 | O | Oxygen map |
  | M1 | P | Replay the picked test |
  | M2 | G | Move the settings onto the picked test |
  | M3 | / | Ask Ember |

- **Detached controllers** behave like the attached ones: the browser still sees one
  gamepad. Rumble comes through the same way.
- There is no camera on the Legion Go, and the browser cannot read the controllers'
  motion sensors, so neither is used.

## Where the sent file goes

"Send to base" (press the left stick on the Flame console) stores the CSV of real
tests in the folder `exports` on the computer that runs the server, and on the PC
as well when the handheld is linked to it. To make that a shared folder, write its
path on the first line of a file named `exports-folder.txt` next to
`Start dashboard.bat`, for example a folder inside OneDrive or Google Drive.
