"""Serve the fixed FLEX film and translate BASS-II questions on the dashboard's model."""

import http.client
from contextlib import contextmanager
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request

if __package__:
    from . import film_review, table_questions
else:
    import film_review
    import table_questions


ASSETS = (
    "ember-lab.html", "ember-lab.css", "table-lab.js", "lab-table-examples.js",
    "flex-film.js", "lab-media/flex-analysis.js", "lab-media/flex-iss.webm",
    "lab-media/flex-before.jpg", "lab-media/flex-after.jpg",
    "lab-media/saffire-1.webm", "lab-media/saffire-1-poster.jpg",
    "lab-media/flex-2.webm", "lab-media/flex-2-poster.jpg",
    "lab-media/sofie-gel.webm", "lab-media/sofie-gel-poster.jpg",
    "lab-media/saffire-5.webm", "lab-media/saffire-5-poster.jpg",
    "lab-media/saffire-6.webm", "lab-media/saffire-6-poster.jpg",
)
POST_ROUTES = {"/lab/table", "/lab/table-plan", "/lab/film", "/lab/film-local"}


def send_film(handler, path):
    """Allow the browser to seek to a saved frame before it downloads the full movie."""
    size = path.stat().st_size
    start, end = 0, size - 1
    byte_range = handler.headers.get("Range")
    if byte_range:
        match = re.fullmatch(r"bytes=(\d{0,15})-(\d{0,15})", byte_range)
        if match and any(match.groups()):
            left, right = match.groups()
            if left:
                start = int(left)
                end = min(int(right), end) if right else end
            else:
                start = max(0, size - int(right))
        else:
            start = size
        if start > end:
            handler.send_response(416)
            handler.send_header("Content-Range", f"bytes */{size}")
            handler.send_header("Content-Length", "0")
            return handler.end_headers()
    length = end - start + 1
    handler.send_response(206 if byte_range else 200)
    if byte_range:
        handler.send_header("Content-Range", f"bytes {start}-{end}/{size}")
    handler.send_header("Accept-Ranges", "bytes")
    handler.send_header("Content-Type", "video/webm")
    handler.send_header("Content-Length", str(length))
    handler.end_headers()
    with path.open("rb") as film:
        film.seek(start)
        while length:
            chunk = film.read(min(length, 65536))
            if not chunk:
                break
            handler.wfile.write(chunk)
            length -= len(chunk)


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class ModelUnavailable(Exception):
    pass


def post_json(url, payload, timeout):
    request = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                     headers={"Content-Type": "application/json"})
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())
    with opener.open(request, timeout=timeout) as response:
        raw = response.read(32769)
    if len(raw) > 32768:
        raise ValueError("Response limit exceeded")
    return json.loads(raw)


@contextmanager
def model_slot(server):
    if not server.one_at_a_time.acquire(blocking=False):
        raise ModelUnavailable("Ember is busy. Try again in a moment.")
    try:
        yield
    except (OSError, http.client.HTTPException, ValueError, KeyError, TypeError):
        raise ModelUnavailable("The local model could not answer. Try a saved result or check Ollama.") from None
    finally:
        server.one_at_a_time.release()


def translate_locally(server, ollama, messages, schema):
    with model_slot(server):
        data = post_json(ollama + "/api/chat", {
            "model": server.model, "messages": messages, "format": schema, "stream": False,
            "think": False, "options": {"temperature": 0, "num_predict": 256},
        }, timeout=40)
        content = data["message"]["content"]
        return json.loads(content)


def handle_request(handler, ollama):
    if len(handler.headers.get_all("Content-Type", [])) != 1 or handler.headers.get_content_type() != "application/json":
        return handler.send_json({"error": "Send an application/json question."}, 415)
    origin = handler.headers.get("Origin")
    if origin and origin != getattr(handler.server, "public_origin", None):
        try:
            parts = urllib.parse.urlsplit(origin)
            valid = parts.scheme in ("http", "https") and parts.netloc.lower() == handler.headers.get("Host", "").lower()
        except ValueError:
            valid = False
        if not valid:
            return handler.send_json({"error": "Open the question on this dashboard."}, 403)
    try:
        if len(handler.headers.get_all("Content-Length", [])) != 1:
            return handler.send_json({"error": "Supply the request length."}, 400)
        length = int(handler.headers.get("Content-Length", "0"))
        if not 0 < length <= 4096:
            return handler.send_json({"error": "Use one short question."}, 413)
        handler.connection.settimeout(10)
        raw = handler.rfile.read(length)
        if len(raw) != length:
            return handler.send_json({"error": "The request was incomplete."}, 400)
        payload = json.loads(raw)
    except (ValueError, OSError, RecursionError):
        return handler.send_json({"error": "Could not read the request."}, 400)

    server = handler.server
    try:
        if handler.path.startswith("/lab/film"):
            if payload != {}:
                return handler.send_json({"error": "Choose the bundled FLEX clip."}, 400)
            result = film_result(server, ollama, handler.path == "/lab/film")
        else:
            question = payload.get("question") if isinstance(payload, dict) else None
            if not isinstance(question, str) or not 0 < len(question.strip()) <= 300:
                return handler.send_json({"error": "Enter a question of up to 300 characters."}, 400)
            result = table_result(server, ollama, handler.path, question.strip())
    except ModelUnavailable as error:
        return handler.send_json({"error": str(error)}, 503)
    return handler.send_json(result)


def table_result(server, ollama, route, question):
    def local(messages, schema):
        return translate_locally(server, ollama, messages, schema)

    def preferred(messages, schema):
        if server.peer:
            try:
                response = post_json(server.peer + "/lab/table-plan", {"question": question}, timeout=45)
                plan = response["plan"]
                if isinstance(plan, dict):
                    return plan
            except (OSError, http.client.HTTPException, ValueError, KeyError, TypeError):
                pass
        return local(messages, schema)

    if route == "/lab/table-plan":
        return {"plan": table_questions.model_plan(question, local)}
    return table_questions.answer_question(question, preferred)


def film_result(server, ollama, use_peer):
    if use_peer and server.peer:
        try:
            result = post_json(server.peer + "/lab/film-local", {}, timeout=55)
            return film_review.validate_pair(result)
        except (OSError, http.client.HTTPException, ValueError, KeyError, TypeError):
            pass
    with model_slot(server):
        deadline = time.monotonic() + 45

        def vision_api(path, payload):
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise ModelUnavailable("The frame review timed out. The saved frames are still available.")
            return post_json(ollama + "/api/" + path, payload, timeout=remaining)

        return film_review.review_clip(server.model, vision_api)
