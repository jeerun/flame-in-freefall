# Setting up the Legion Go

On Nov 15 the owner ran the earlier dashboard on a Legion Go 8APU1 in Edge, using
the PC over Tailscale and the handheld's own Ollama installation. Controller
operation, sound and rumble were checked before the model switch. The per-fuel
build at `f8374e5` received a separate 1280×800 screen check. The newer activities,
shared views and controls were tested in desktop Edge with simulated gamepad input.
The direct Wi-Fi route in A still needs a device test. [Device test record](../CLAUDE.md)

## A. The Legion Go as the screen, the PC as the brain (nothing to install)

1. Find the handheld's IPv4 address in its Wi-Fi properties. On the GPU PC,
   stop an existing PC-only dashboard. From the repo root run
   `py server/serve.py --lan --allow-device 192.168.1.42 --open`, substituting
   the **handheld's** address for the example. The server prints the **PC's**
   address for the handheld to open. Leave the server window open.
2. Use a trusted Private network. If Windows requests firewall access, enable
   only the Private profile and scope the inbound rule to the handheld’s address.
3. On the Legion Go, on the same Wi-Fi or router, open Edge at that address and
   press F11. NASA research opens immediately. Open Controls to check the gamepad connection.
4. On the PC, open `http://localhost:8000/who`. At the browser prompt use
   `crew` and the per-run password printed in the PC's server window. The page
   lists connected devices and counts requests, questions and exports.

If the Legion Go cannot open the address:

- Check that the handheld still has the address passed to `--allow-device`.
  If it changed, restart with the new address and update the Private firewall rule.
- Check whether the VPN permits the local network or use the Tailscale route below.
- The two devices are not on the same network, or the network keeps devices apart
  (campus and guest Wi-Fi often do). Use a phone hotspot or a home router for both.
- Double-clicking `Start dashboard.bat` starts PC-only mode. To change modes,
  stop the running server before starting the private-LAN command above.

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
   thinks on:" offers Auto, the PC and the handheld. Press X to switch. On this
   Legion Go the owner switched from Auto on the PC to the handheld and received
   a local answer. A second server on the device answered with an unreachable
   peer configured. The PC stayed up, so the live disconnect banner is unverified.

The handheld's CPU generated the observed local answers in 3.7–14.5 seconds.
One answer confused the rate of change of droplet diameter with the rate of
change of its square. Check scientific explanations against the cited PSI data.

## C. Away from the PC's network

Use a private network between your own devices, such as Tailscale. It also gets
around Wi-Fi that keeps devices apart, because the two machines talk through it
over the private network. The tested route used `http://run/` on Tailscale.

1. Connect the PC and the Legion Go to the same private Tailscale network.
2. On the PC, stop any existing dashboard and run `tailscale serve --http=80 8000`
   in one window. In another, start the dashboard with the exact origin the
   handheld will open. For the team's hostname, the command is
   `py server/serve.py --public-origin http://run`. If using the full tailnet
   name printed by Tailscale, enter that name with its scheme instead.
   The Python server remains bound to loopback. Limit the tailnet's access
   policy to the devices that should use this service.
3. Open that same origin in the handheld’s Edge browser, or give it to
   `Start on Legion Go.bat` when configuring Ember's peer.

On Nov 15 the handheld reached the PC at `http://run/`. The dashboard
confirmed a CSV export to RUN and the PC's `/tests.csv` returned 252 rows.
The team did not inspect the PC's export folder during the handheld test.

Keep this route inside your tailnet. The dashboard and Ember accept requests from
clients allowed through the proxy. The PC's device log has a separate password.

## Built for this screen

In full screen (F11) the Legion Go's browser is 1280x800. At that size the page uses no
text under 12 px and makes its controls thumb-sized: tabs, the plus and minus steps and
their tracks, fuel, **Explain reading**, **Put it out**, the CSV buttons and the dialog
buttons. In a lower window it keeps the earlier sizes so that nothing scrolls. This was
measured in desktop Edge at 1280x800 and 1280x680, not on the device.

Two things help a first-time user on the handheld: **Take the tour** in the top bar
(View on the research page) and, on the Flame console, **Put it out** (A, then RT).

## The Legion Go's extra controls

On the earlier dashboard, the owner verified the physical wheel moved the
selected setting one step per notch. FPS mode was not tried on the device.

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

- **Controller detection.** Edge reported one standard Xbox 360 controller with
  17 buttons and four axes during the checklist run. The owner felt rumble on
  an out-of-range setting and a wrong drill answer. Detached operation is unverified.
- There is no camera on the Legion Go, and the browser cannot read the controllers'
  motion sensors, so neither is used.

## Where the sent file goes

"Send to base" (press the left stick on the Flame console) stores the CSV of real
tests in the folder `exports` on the computer that runs the server, and on the PC
as well when the handheld is linked to it. To make that a shared folder, write its
path on the first line of a file named `exports-folder.txt` next to
`Start dashboard.bat`, for example a folder inside OneDrive or Google Drive.
