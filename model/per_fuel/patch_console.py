"""The change console/index.html needed to read the per-fuel export.

APPLIED on 15 November 2026, when the console was switched to the per-fuel model. The page now carries
these edits, so this script refuses to run on it ("already patched"). It is kept as the exact record of
what the switch changed on the page. The rest of this text is as it was written before the switch.

    python model/per_fuel/patch_console.py --check    say whether the page can be patched; write nothing
    python model/per_fuel/patch_console.py            patch console/index.html in place

It is a list of exact replacements, so it keeps working while other parts of the page change, and it
stops with a message, writing nothing, if one of these lines is no longer there. A patched page still
reads an export without "fuel_coef" or "meta.watch" and then behaves exactly as before.

What changes on the page:
  - linear() adds each fuel's own slope ("fuel_coef") to the shared one.
  - The explanation's "pushes toward" lines and the zoomed map's 25/50/75 % lines do the same.
  - "Could go either way" starts at the export's "meta.watch" (0.30) instead of a fixed 0.35, and a
    "Watch" banner appears when the reading enters that band. Both only when the export has "meta.watch".
No function is added or renamed, so tests that pull functions out of the page by name keep working.
"""
import argparse
from pathlib import Path
import sys

PAGE = Path(__file__).resolve().parents[2] / "console" / "index.html"

# (text on the page now, text after). Each "now" text must appear exactly once.
EDITS = [
    ('''  var lastLevel = null, lastHigh = false, lastDisagree = false;''',
     '''  var WATCH = (M.meta && M.meta.watch) || 0.35, lastWatch = false;   // where "could go either way" starts
  var lastLevel = null, lastHigh = false, lastDisagree = false;'''),
    ('''    var z = part.intercept + (part.fuel[fuel] || 0);
    M.features.forEach(function (f) { z += (part.coef[f.key] || 0) * values[f.key]; });
''',
     '''    var own = (part.fuel_coef && part.fuel_coef[fuel]) || {};   // this fuel's own slopes, when the model has them
    var z = part.intercept + (part.fuel[fuel] || 0);
    M.features.forEach(function (f) { z += ((part.coef[f.key] || 0) + (own[f.key] || 0)) * values[f.key]; });
'''),
    ('''    var list = M.features.map(function (f) {
      return { label: f.label, f: f, push: -(M.extinction.coef[f.key] || 0) * (state.values[f.key] - f.default) };
    });
    var base = M.extinction.fuel[M.fuels[0].key] || 0;
    list.push({ label: "Fuel", f: null, push: -((M.extinction.fuel[state.fuel] || 0) - base) });
''',
     '''    var own = (M.extinction.fuel_coef && M.extinction.fuel_coef[state.fuel]) || {};
    var list = M.features.map(function (f) {
      return { label: f.label, f: f, push: -((M.extinction.coef[f.key] || 0) + (own[f.key] || 0)) * (state.values[f.key] - f.default) };
    });
    // The fuel's own push: this fuel against the first one, with every setting at its starting value.
    var start = {};
    M.features.forEach(function (f) { start[f.key] = f.default; });
    list.push({ label: "Fuel", f: null, push: -(linear(M.extinction, state.fuel, start) - linear(M.extinction, M.fuels[0].key, start)) });
'''),
    ('''((r.pKeep < 0.35 && nb.done * 2 > seen)''', '''((r.pKeep < WATCH && nb.done * 2 > seen)'''),
    ('''r.pKeep >= 0.35 ? " mid" : "");''', '''r.pKeep >= WATCH ? " mid" : "");'''),
    ('''    var high = rc.level !== "outside" && r.pKeep >= 0.65;
''',
     '''    var high = rc.level !== "outside" && r.pKeep >= 0.65;
    var watch = rc.level !== "outside" && !high && r.pKeep >= WATCH;
'''),
    ('''      if (high && !lastHigh) notify("High fire risk: this flame is likely to burn all its fuel.", "warn");
''',
     '''      if (high && !lastHigh) notify("High fire risk: this flame is likely to burn all its fuel.", "warn");
      else if (M.meta.watch && watch && !lastWatch && !lastHigh) notify("Watch: this flame has a real chance of burning all its fuel.", "info");
'''),
    ('''lastHigh = high; lastDisagree = !!rc.disagree;''', '''lastHigh = high; lastWatch = watch; lastDisagree = !!rc.disagree;'''),
    ('''(r.pKeep < 0.35 ? nb.done + " of " + seen''', '''(r.pKeep < WATCH ? nb.done + " of " + seen'''),
    ('''else if (r.pKeep >= 0.35) line = "Could go either way''', '''else if (r.pKeep >= WATCH) line = "Could go either way'''),
    ('''      var bo = M.extinction.coef.o2, bd = M.extinction.coef.d0 || 0, z0 =''',
     '''      var own = (M.extinction.fuel_coef && M.extinction.fuel_coef[state.fuel]) || {};
      var bo = M.extinction.coef.o2 + (own.o2 || 0), bd = (M.extinction.coef.d0 || 0) + (own.d0 || 0), z0 ='''),
]


def patched(text):
    """The page text with every edit made. Raises ValueError, quoting the line, if the page no longer matches."""
    if "fuel_coef" in text:
        raise ValueError("this page is already patched")
    for now, after in EDITS:
        if text.count(now) != 1:
            raise ValueError(f"expected exactly one copy of this text on the page, found {text.count(now)}:\n{now}")
        text = text.replace(now, after)
    return text


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="only say whether the page can be patched")
    args = parser.parse_args()
    try:
        text = patched(PAGE.read_text(encoding="utf-8"))
    except ValueError as err:
        print(f"Not patched: {err}")
        return 1
    if args.check:
        print(f"{PAGE.name} can be patched ({len(EDITS)} edits). Nothing written.")
        return 0
    PAGE.write_text(text, encoding="utf-8", newline="\n")
    print(f"Patched {PAGE.name} ({len(EDITS)} edits). Now run model/train.py and then model/train_per_fuel.py to write console/model.js.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
