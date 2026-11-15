"""Serve the dashboard and answer its "Ask the AI" questions with a language model running on this PC.

Easiest: double-click "Start dashboard.bat" in the repo folder. Or, from the repo root:
    py server/serve.py            this PC only:  http://localhost:8000
    py server/serve.py --lan      also other devices on the same Wi-Fi (the Legion Go)
    add --open to open the dashboard in this PC's browser

Needs only the Python standard library, plus Ollama (https://ollama.com) running on this PC
with the model pulled once:   ollama pull gemma4:12b

What it does:
  GET  /            the files in console/ (index.html, model.js, research.js), nothing else
  GET  /ai          is the local model ready, and is it on the GPU
  POST /ask         builds a prompt from the NASA PSI records in this repo plus what the page sent,
                    asks the local model, and streams the answer back as plain text

The model only ever sees NASA PSI text from data/raw/psi_search, the dashboard's own notes and
numbers, and the question. Nothing is sent to the internet.
"""
import argparse
import json
import re
import socket
import subprocess
import threading
import time
import urllib.error
import urllib.request
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONSOLE = ROOT / "console"
RAW = ROOT / "data" / "raw" / "psi_search" / "combustion_investigations.json"
NOTES = ROOT / "data" / "clean" / "research_notes.json"
OLLAMA = "http://127.0.0.1:11434"
STATIC = {"/": "index.html", "/index.html": "index.html", "/model.js": "model.js", "/research.js": "research.js"}
TYPES = {".html": "text/html; charset=utf-8", ".js": "text/javascript; charset=utf-8"}
MAX_BODY = 16000

SYSTEM = (
    "You are the assistant inside a fire-safety dashboard for spacecraft crews, students and engineers. "
    "The dashboard is built on NASA's Physical Sciences Informatics (PSI) records of microgravity combustion investigations. "
    "Answer ONLY from the material given after the question. "
    "Refer to an investigation by its name followed by its PSI id in square brackets, like FLEX [PSI-69]. "
    "If the material does not contain the answer, say so plainly instead of guessing. "
    "Never invent numbers, test results, dates or investigation names. "
    "Copy every number exactly as it is written in that investigation's own record, and never attach a number from the "
    "question, the challenge brief or another investigation to it. "
    "Write plain English for a non-specialist, in at most 110 words. No headings, no tables, no markdown symbols. "
    "When you rank things, use short numbered lines."
)
SYSTEM_READING = (
    " The percentages in the current reading come from a small statistical model trained on 199 FLEX tests. "
    "They are estimates, not physics and not a crew procedure, so do not present them as certain. "
    "If the reading says the settings are outside the tested range, say that the fire risk there is unknown. "
    "'Goes out' means the visible flame only."
)
STOP = set("the a an and or of to in on for with by is are was were be been it this that these those what which who how why "
           "do does did can could should would will most more less than then about into from at as its their them they you "
           "your our we not no yes me my new still any all each one two investigation investigations nasa fire safety".split())


def flat(text, limit=None):
    out = re.sub(r"\s+", " ", str(text or "")).strip()
    return out[:limit] if limit else out


def load_records():
    hits = {h["_source"]["Accession"]: h["_source"] for h in json.loads(RAW.read_text(encoding="utf-8"))["hits"]["hits"]}
    notes = json.loads(NOTES.read_text(encoding="utf-8"))["notes"]
    records = []
    for acc, n in notes.items():
        s = hits[acc]
        hardware = s.get("Experiment Hardware") or {}
        records.append({
            "id": acc, "name": n["name"], "fuel": n["fuel"], "summary": n["summary"], "scores": n["scores"],
            "title": flat(s.get("Title")),
            "kind": "flight experiment" if flat(s.get("Project Type")) == "Microgravity Investigation" else "ground study",
            "objectives": flat(s.get("Objectives"), 1500), "approach": flat(s.get("Approach"), 900),
            "keywords": flat(s.get("Keywords"), 300),
            "hardware": flat(hardware.get("Name") if isinstance(hardware, dict) else hardware, 200),
        })
    records.sort(key=lambda r: int(r["id"].split("-")[1]))
    return records


def words(text):
    return [w for w in re.findall(r"[a-z0-9][a-z0-9\-]+", text.lower()) if len(w) > 2 and w not in STOP]


def pick(records, question, selected, k=4):
    """The k records whose NASA text shares the most words with the question. The one on screen always comes along."""
    q = set(words(question))
    scored = []
    for r in records:
        body = " ".join([r["title"], r["keywords"], r["objectives"], r["approach"], r["fuel"]]).lower()
        score = sum(min(body.count(w), 5) for w in q)
        score += 25 * sum(1 for w in set(words(r["name"] + " " + r["id"])) if w in q)
        if r["id"] == selected:
            score += 1000
        scored.append((score, r))
    scored.sort(key=lambda x: -x[0])
    return [r for score, r in scored[:k] if score > 0]


def research_material(records, question, selected, need):
    lines = ["CATALOG: every combustion investigation in NASA PSI (id | name | fuel | flight or ground | note written for this dashboard)"]
    lines += [f"{r['id']} | {r['name']} | {r['fuel']} | {r['kind']} | {r['summary']}" for r in records]
    chosen = pick(records, question, selected)
    lines.append("\nDETAILED NASA PSI RECORDS for the investigations closest to the question")
    for r in chosen:
        lines.append(f"\n{r['id']} {r['name']}: {r['title']} ({r['kind']})\nObjectives: {r['objectives']}\nApproach: {r['approach']}"
                     f"\nKeywords: {r['keywords']}\nHardware: {r['hardware']}")
    lines.append("\nBACKGROUND FROM THE 2026 NASA SPACE APPS CHALLENGE BRIEF (use it for questions about future missions and about what is "
                 "missing; its numbers do not belong to any investigation above): NASA's spacecraft fire-safety work is prevention, "
                 "detection and suppression. The Moon Base and pressurized rovers will likely have 30% oxygen or more at 10.2 psi or "
                 "less. A known gap: PSI has no partial-gravity combustion data yet, so nothing in it was measured at Moon or Mars "
                 "gravity; microgravity and normal-gravity results can only bound what happens in between.")
    on_screen = next((r for r in records if r["id"] == selected), None)
    if on_screen:
        lines.append(f"\nTHE USER IS LOOKING AT: {on_screen['id']} {on_screen['name']}" + (f", in the list ranked for {need}." if need else "."))
    return "\n".join(lines), [r["id"] for r in chosen]


def reading_material(records, reading):
    flex = next(r for r in records if r["id"] == "PSI-69")
    return ("CURRENT READING ON THE FLAME CONSOLE PAGE (numbers from the dashboard's model and from the NASA FLEX test table, PSI-69)\n"
            + reading.strip()[:4000]
            + f"\n\nNASA PSI RECORD PSI-69 FLEX: {flex['title']}\nObjectives: {flex['objectives']}\nApproach: {flex['approach']}"), ["PSI-69"]


def ollama_json(path, timeout=4):
    with urllib.request.urlopen(OLLAMA + path, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def gpu_name():
    try:
        out = subprocess.run(["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"], capture_output=True, text=True, timeout=4)
        return out.stdout.strip().splitlines()[0].strip() if out.returncode == 0 and out.stdout.strip() else ""
    except (OSError, subprocess.SubprocessError, IndexError):
        return ""


def ai_status(model):
    """Is Ollama up, is the model pulled, and how much of it sits in GPU memory right now."""
    try:
        names = [m.get("name", "") for m in ollama_json("/api/tags").get("models", [])]
    except (OSError, ValueError) as err:
        return {"ok": False, "model": model, "reason": f"Ollama is not answering on this PC ({err.__class__.__name__})."}
    if model not in names and model + ":latest" not in names:
        return {"ok": False, "model": model, "reason": f"Model {model} is not pulled. Run: ollama pull {model}"}
    status = {"ok": True, "model": model, "gpu": GPU, "on_gpu": None}
    try:
        for m in ollama_json("/api/ps").get("models", []):
            if m.get("name") == model and m.get("size"):
                status["on_gpu"] = round(100 * m.get("size_vram", 0) / m["size"])      # percent of the loaded model in GPU memory
    except (OSError, ValueError):
        pass
    return status


def ask_model(model, system, user):
    """Yield the answer piece by piece. Thinking output, if the model produces any, is dropped."""
    body = {"model": model, "stream": True, "think": False, "keep_alive": "30m",
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
            "options": {"temperature": 0.2, "seed": 7, "num_ctx": 8192, "num_predict": 420}}
    for attempt in (1, 2):
        req = urllib.request.Request(OLLAMA + "/api/chat", data=json.dumps(body).encode("utf-8"),
                                     headers={"Content-Type": "application/json"})
        try:
            resp = urllib.request.urlopen(req, timeout=180)
            break
        except urllib.error.HTTPError as err:
            detail = err.read().decode("utf-8", "replace")
            if attempt == 1 and "think" in detail.lower():
                body.pop("think")                          # this model has no thinking switch
                continue
            raise RuntimeError(f"Ollama answered {err.code}: {detail[:200]}")
    with resp:
        for raw in resp:
            if not raw.strip():
                continue
            event = json.loads(raw)
            piece = (event.get("message") or {}).get("content") or ""
            if piece:
                yield piece
            if event.get("done"):
                break


def warm_up(server):
    """Load the model into GPU memory before the first real question (a cold start takes about a minute)."""
    started = time.time()
    try:
        with server.one_at_a_time:
            "".join(ask_model(server.model, SYSTEM, "QUESTION: Reply with the single word ready.\n\nMATERIAL\nnone"))
        print(f"Local AI warmed up in {time.time() - started:.0f} s. First answers will be quick now.")
    except (OSError, RuntimeError, ValueError) as err:
        print(f"Local AI warm-up failed: {err}")


class Handler(BaseHTTPRequestHandler):
    server_version = "FlameConsole/1"

    def log_message(self, fmt, *args):
        print(f"{self.address_string()} {fmt % args}")

    def send_json(self, obj, code=200):
        data = json.dumps(obj).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path == "/ai":
            return self.send_json(ai_status(self.server.model))
        if path == "/favicon.ico":                         # browsers ask for one; there is none
            self.send_response(204)
            self.send_header("Content-Length", "0")
            return self.end_headers()
        name = STATIC.get(path)
        file = CONSOLE / name if name else None
        if not file or not file.is_file():
            return self.send_error(404)
        data = file.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", TYPES[file.suffix])
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self):
        if self.path != "/ask":
            return self.send_error(404)
        try:
            length = int(self.headers.get("Content-Length") or 0)
            if not 0 < length <= MAX_BODY:
                return self.send_error(413)
            ask = json.loads(self.rfile.read(length).decode("utf-8"))
            question = flat(ask.get("question"), 400)
            if not question:
                return self.send_error(400)
        except (ValueError, UnicodeDecodeError):
            return self.send_error(400)

        records = self.server.records
        if ask.get("page") == "console":
            material, used = reading_material(records, str(ask.get("reading") or ""))
            system = SYSTEM + SYSTEM_READING
        else:
            material, used = research_material(records, question, flat(ask.get("selected"), 12), flat(ask.get("need"), 20))
            system = SYSTEM
        user = f"QUESTION: {question}\n\nMATERIAL\n{material}"

        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Records-Used", ",".join(used))
        self.send_header("Connection", "close")
        self.end_headers()
        started, count = time.time(), 0
        try:
            with self.server.one_at_a_time:
                for piece in ask_model(self.server.model, system, user):
                    self.wfile.write(piece.encode("utf-8"))
                    self.wfile.flush()
                    count += len(piece)
        except (OSError, RuntimeError, ValueError) as err:
            try:
                self.wfile.write(f"\n[The local model could not answer: {err}]".encode("utf-8"))
            except OSError:
                pass
        print(f"   asked ({ask.get('page')}): {question[:70]!r} -> {count} chars in {time.time() - started:.1f} s, records {used}")
        self.close_connection = True


def lan_address():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("10.255.255.255", 1))               # no packet is sent; this only picks the outgoing interface
            return s.getsockname()[0]
    except OSError:
        return None


def main():
    parser = argparse.ArgumentParser(description="Serve the dashboard and its local AI.")
    parser.add_argument("--lan", action="store_true", help="also accept other devices on the same network")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--model", default="gemma4:12b", help="Ollama model name")
    parser.add_argument("--open", action="store_true", help="open the dashboard in this PC's browser")
    args = parser.parse_args()

    global GPU
    GPU = gpu_name()
    server = ThreadingHTTPServer(("0.0.0.0" if args.lan else "127.0.0.1", args.port), Handler)
    server.model, server.records, server.one_at_a_time = args.model, load_records(), threading.Lock()
    status = ai_status(args.model)
    print(f"Dashboard: http://localhost:{args.port}")
    if args.lan:
        print(f"On the Legion Go (same Wi-Fi): http://{lan_address() or '<this PC address>'}:{args.port}")
        print("If Windows asks whether to allow Python through the firewall, choose Allow on private networks.")
    print(f"Local AI: {'ready, ' + args.model + (' on ' + GPU if GPU else '') if status['ok'] else 'NOT ready. ' + status['reason']}")
    print(f"NASA PSI records loaded: {len(server.records)}. Press Ctrl+C to stop.")
    if status["ok"]:
        threading.Thread(target=warm_up, args=(server,), daemon=True).start()
    if args.open:
        threading.Timer(1.0, webbrowser.open, args=(f"http://localhost:{args.port}",)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("stopped")


GPU = ""
if __name__ == "__main__":
    main()
