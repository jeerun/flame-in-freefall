"""Ask Ember a fixed list of questions and write the answers to docs/ember-check.md, ready for a person to check.

    1. start the dashboard:   py server/serve.py
    2. in another window:     py server/ember_check.py

Each answer is stored with the NASA PSI records the model was given, and with two automatic checks that need no
judgement: is every number in the answer present in the material the model was given, and does every PSI id sit next
to the right investigation name. Those checks catch invented numbers and mixed-up ids. They do not show that an
answer is a good answer: that is what the empty "Human verdict" line under each answer is for.
"""
import datetime
import json
import re
import sys
import time
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import serve  # noqa: E402  (the same code the server runs, used here to rebuild the material for the checks)

URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
OUT = serve.ROOT / "docs" / "ember-check.md"

MOON = ("Fuel: Heptane. Oxygen 30.0 %, Pressure 0.69 atm, Carbon dioxide 0 %, Helium 0 %, Droplet diameter 3.0 mm. Cabin air preset: Moon Base (expected).\n"
        "Model output conditional on completion or visible extinction (disruptions excluded): chance the flame burns until the fuel is gone 99 %; chance it goes out before the fuel is gone 1 %; burning rate 0.75 mm2/s; "
        "droplet gone in about 12 s if the flame lasts.\n"
        "Confidence box: No clear outcome in nearby tests. Nearby FLEX rows: 3. All ended in disruption. The percentage relies on tests farther away.\n"
        "One-line reading: Nearby tests cannot confirm the estimated outcome.")
OUTSIDE = ("Fuel: Heptane. Oxygen 40.0 %, Pressure 0.69 atm, Carbon dioxide 0 %, Helium 0 %, Droplet diameter 3.0 mm.\n"
           "Model output conditional on completion or visible extinction (disruptions excluded): chance the flame burns until the fuel is gone 99 %; chance it goes out before the fuel is gone 1 %; burning rate 0.96 mm2/s; "
           "droplet gone in about 9 s if the flame lasts.\n"
           "Confidence box: Outside the tested range. No experiment was run at this oxygen setting. Do not rely on these numbers.\n"
           "One-line reading: These settings exceed the model's scope.")

# (question, page, selected investigation, need, reading)
QUESTIONS = [
    ("Which investigations matter most for a Moon Base cabin with 30 percent oxygen at 10.2 psi?", "research", "", "Cabin air", ""),
    ("How many tests were run in Moon Base air, and in which investigations?", "research", "", "Cabin air", ""),
    ("Which investigations tested the highest oxygen levels, and how high?", "research", "", "Cabin air", ""),
    ("What did FLEX measure, and what did it change from test to test?", "research", "PSI-69", "Suppression", ""),
    ("How did carbon dioxide and helium matter in FLEX?", "research", "PSI-69", "Suppression", ""),
    ("How are FLEX, FLEX-2 and CFI alike, and how do they differ?", "research", "PSI-68", "", ""),
    ("What did SAME and SAME-R study about smoke, and why does it matter for detectors?", "research", "PSI-101", "Detection", ""),
    ("What does DAFT have to do with smoke detection?", "research", "PSI-47", "Detection", ""),
    ("What did BASS-II burn, and at which oxygen levels?", "research", "PSI-25", "Prevention", ""),
    ("What is Saffire, and why does it matter for spacecraft fire safety?", "research", "PSI-98", "Prevention", ""),
    ("What did ACME BRE measure, and with which instruments?", "research", "PSI-20", "Prevention", ""),
    ("Which hardware did the ACME experiments share?", "research", "PSI-23", "", ""),
    ("What is a cool flame, and which investigations studied it?", "research", "PSI-39", "", ""),
    ("Which investigations help design fire-suppression equipment?", "research", "", "Suppression", ""),
    ("Is there any data at Moon or Mars gravity in PSI?", "research", "", "", ""),
    ("How could this research help fire safety on Earth?", "research", "", "", ""),
    ("Interpret this reading for the crew in three sentences.", "console", "", "", MOON),
    ("Interpret this reading for the crew in three sentences.", "console", "", "", OUTSIDE),
]


def ask(body):
    req = urllib.request.Request(URL + "/ask", data=json.dumps(body).encode("utf-8"), headers={"Content-Type": "application/json"})
    started = time.time()
    with urllib.request.urlopen(req, timeout=240) as resp:
        text = resp.read().decode("utf-8").strip()
        return text, resp.headers.get("X-Brain-Label") or "", [u for u in (resp.headers.get("X-Records-Used") or "").split(",") if u], time.time() - started


def numbers(text):
    """Number tokens, without list numbering ("1.", "2)") and without the digits of PSI ids."""
    text = re.sub(r"PSI-\d+", " ", text)
    text = re.sub(r"(?m)^\s*\d+[.)]\s", " ", text)
    return {n.rstrip(".").lstrip("0") or "0" for n in re.findall(r"\d+(?:\.\d+)?", text.replace(",", ""))}


def check(answer, question, material, records):
    notes = []
    known = numbers(material + " " + question)
    stray = sorted(n for n in numbers(answer) if n not in known and (n + "0") not in known)
    notes.append("every number in the answer is in the material it was given" if not stray
                 else "NUMBERS NOT IN THE MATERIAL: " + ", ".join(stray))
    by_id = {r["id"]: r for r in records}
    wrong = []
    for m in re.finditer(r"\[(PSI-\d+)\]", answer):
        before = answer[max(0, m.start() - 60):m.start()].lower()
        rec = by_id.get(m.group(1))
        if not rec:
            wrong.append(m.group(1) + " is not a combustion investigation in the catalog")
        elif not any(part in before for part in re.findall(r"[a-z0-9]{3,}", rec["name"].lower())):
            wrong.append(f"{m.group(1)} is {rec['name']}, but the words before it are \"{answer[max(0, m.start() - 40):m.start()].strip()}\"")
    notes.append("every PSI id sits next to its own investigation name" if not wrong else "ID DOES NOT MATCH THE NAME: " + "; ".join(wrong))
    return notes, bool(stray or wrong)


def main():
    records = serve.load_records()
    status = json.loads(urllib.request.urlopen(URL + "/ai", timeout=10).read().decode("utf-8"))
    if not status.get("ok"):
        raise SystemExit("Ember is not ready on " + URL)
    out = ["# Ember answer check", "",
           f"Made by `server/ember_check.py` on {datetime.date.today().isoformat()}. Ember is the local AI model in the dashboard. "
           "Every answer below was written by that model, not by a person.", "",
           "How to use this page: read each answer, open the NASA PSI pages listed under it, and fill in the **Human verdict** line. "
           "The two automatic checks only catch invented numbers and mixed-up ids. An answer that passes them can still be wrong, vague or beside the point.", ""]
    flagged = 0
    for i, (question, page, selected, need, reading) in enumerate(QUESTIONS, 1):
        if page == "console":
            material, _ = serve.reading_material(records, reading)
        else:
            material, _ = serve.research_material(records, question, selected, need)
        answer, label, used, took = ask({"question": question, "page": page, "selected": selected, "need": need, "reading": reading, "brain": "auto"})
        notes, bad = check(answer, question, material, records)
        flagged += bad
        print(f"{i:2d}. {took:4.1f} s {'FLAG' if bad else 'ok  '} {question[:70]}")
        out += [f"## {i}. {question}", ""]
        if page == "console":
            out += ["Asked from the Flame console with this reading on screen:", "", "```", reading, "```", ""]
        elif selected or need:
            out += [f"Asked from the research page ({'looking at ' + selected if selected else 'nothing picked'}{', list ranked for ' + need if need else ''}).", ""]
        out += ["> " + answer.replace("\n", "\n> "), "",
                f"- Answered by: {label}, in {took:.1f} s",
                "- NASA PSI records the model was given in full: " + (", ".join(f"[{u}](https://psi.nasa.gov/physci/repo/data/investigations/{u})" for u in used) or "none"),
                "- Automatic check: " + "; ".join(notes) + ".",
                "- Human verdict (correct / wrong / unsure, and why): ", ""]
    out.insert(4, f"Automatic checks flagged {flagged} of {len(QUESTIONS)} answers. No person has checked any of them yet." if flagged
               else f"Automatic checks flagged none of the {len(QUESTIONS)} answers. No person has checked any of them yet.")
    out.insert(5, "")
    out += ["## What these answers cannot tell you", "",
            "- The model only sees the PSI records and the counts this dashboard made from the PSI test tables. It has not read the papers.",
            "- It answers in at most about 110 words, so lists are often incomplete. Treat a missing investigation as \"not mentioned\", not as \"not relevant\".",
            "- For inverse gas flames the oxygen value is the burner flow, not a cabin atmosphere. The model does not always say so.", ""]
    OUT.write_text("\n".join(out), encoding="utf-8", newline="\n")
    print(f"wrote {OUT} ({flagged} flagged)")


if __name__ == "__main__":
    main()
