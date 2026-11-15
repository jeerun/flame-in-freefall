"""Optional Edge/Chromium test. Run python tests/browser_view_links.py --channel msedge."""
import argparse
import sys
from pathlib import Path
from threading import Thread
from urllib.parse import parse_qs, urlsplit

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from server.serve import Handler, Server

FILE = (ROOT / "console" / "index.html").as_uri()


def share(page, button):
    page.locator("#" + button).click()
    expect(page.locator("#shareCopy")).to_be_focused()
    return page.locator("#shareOutput").input_value()


def paste_copy(page, value):
    page.locator("#shareCopy").click()
    expect(page.locator("#shareStatus")).to_have_text("Copied.")
    page.locator("#shareImport summary").click()
    input_box = page.locator("#shareInput")
    input_box.focus()
    input_box.press("Control+v")  # Exercise real browser copy/paste, with no API replacement.
    expect(input_box).to_have_value(value)


def check_offline(context):
    page = context.new_page()
    page.goto(FILE)
    page.get_by_role("button", name="Detection").click()
    page.locator("#rank button").nth(1).click()
    chosen = page.locator("#card").get_attribute("data-investigation")
    page.locator("#orbitBtn").click()
    code = share(page, "shareResearch")
    assert code.startswith("#view=v1&") and f"id={chosen}" in code and "&orbit=1" in code
    expect(page.locator("#shareCopy")).to_have_text("Copy code")
    paste_copy(page, code)
    page.keyboard.press("Escape")
    expect(page.locator("#shareResearch")).to_be_focused()

    target = context.new_page()
    target.goto(FILE + code)
    expect(target.locator("#orbit")).to_be_visible()
    expect(target.locator("#card")).to_have_attribute("data-investigation", chosen)
    expect(target.get_by_role("button", name="Detection")).to_have_attribute("aria-pressed", "true")
    expect(target.locator("#hCard")).to_be_focused()
    target.close()

    page.locator("#tabConsole").click()
    for preset in ("moon", "mars"):
        page.locator(f'button[data-preset="{preset}"]').click()
        page.keyboard.press("]")  # Select a real star via the normal control.
        code = share(page, "shareReading")
        pairs = parse_qs(urlsplit(code).fragment)
        assert pairs["p"] == ["0.694"] and pairs["preset"] == [preset] and int(pairs["test"][0]) > 0
        target = context.new_page()
        target.goto(FILE + code)
        expect(target.locator(f'button[data-preset="{preset}"]')).to_have_attribute("aria-pressed", "true")
        expect(target.locator("#hRead")).to_be_focused()
        assert share(target, "shareReading") == code
        target.close()
        page.keyboard.press("Escape")

    page.locator('input[type="range"]').first.fill("29.5")
    custom = share(page, "shareReading")
    assert "o2=29.5" in custom and "&preset=" not in custom
    page.locator("#shareImport summary").click()
    page.locator("#shareInput").fill(custom.replace("o2=29.5", "o2=1000"))
    page.locator("#shareForm button").click()
    expect(page.locator("#shareError")).to_contain_text("could not be opened")
    expect(page.locator("#shareInput")).to_be_focused()
    assert page.locator("#shareOutput").input_value() == custom
    page.locator("#shareInput").fill(custom)
    page.locator("#shareForm button").click()
    expect(page.locator("#shareViewDialog")).to_be_hidden()
    expect(page.locator("#hRead")).to_be_focused()
    page.reload()
    expect(page.locator('input[type="range"]').first).to_have_value("29.5")
    assert share(page, "shareReading") == custom
    page.close()

    for suffix in ("", "#view=v2&garbage"):
        target = context.new_page()
        target.goto(FILE + suffix)
        expect(target.locator("#tabResearch")).to_have_attribute("aria-pressed", "true")
        expect(target.locator("#shareViewDialog")).to_be_hidden()
        target.close()


def check_served(context, port):
    # Resolve an ordinary shareable hostname to our ephemeral loopback HTTP server.
    # /ai is unrelated to view links. Do not attempt to contact the user's model.
    context.route("**/ai", lambda route: route.fulfill(json={"brains": []}))
    page = context.new_page()
    page.set_viewport_size({"width": 390, "height": 844})
    loopback = f"http://127.0.0.1:{port}/"
    origin = f"http://crew-preview.test:{port}/"
    for url, label in ((loopback, "Copy code"), (origin, "Copy link")):
        page.goto(url)
        value = share(page, "shareResearch")
        expect(page.locator("#shareCopy")).to_have_text(label)
        assert value.startswith("#view=" if url == loopback else origin + "#view=")
        dialog = page.locator("#shareViewDialog")
        assert dialog.evaluate("el => el.scrollWidth <= el.clientWidth && el.getBoundingClientRect().right <= innerWidth")
        paste_copy(page, value)
        page.locator("#shareForm button").click()
        expect(dialog).to_be_hidden()
        expect(page.locator("#hCard")).to_be_focused()
    target = context.new_page()
    target.goto(value)
    assert share(target, "shareResearch") == value
    target.close()
    page.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--channel", help="Installed Chromium channel, e.g. msedge or chrome")
    args = parser.parse_args()
    class QuietHandler(Handler):
        def log_message(self, *args):
            pass

    with Server(("127.0.0.1", 0), QuietHandler) as server, sync_playwright() as playwright:
        server.seen = {}
        server.public_origin = f"http://crew-preview.test:{server.server_port}"
        worker = Thread(target=server.serve_forever, daemon=True)
        worker.start()
        try:
            browser = playwright.chromium.launch(channel=args.channel, args=[
                "--no-proxy-server", "--host-resolver-rules=MAP crew-preview.test 127.0.0.1"])
            context = browser.new_context(viewport={"width": 1280, "height": 680})
            errors = []
            context.on("page", lambda page: page.on("pageerror", lambda error: errors.append(str(error))))
            check_offline(context)
            check_served(context, server.server_port)
            assert not errors, errors
            browser.close()
        finally:
            server.shutdown()
            worker.join()
    print("PASS: research orbit and selected record, Moon/Mars/custom and star, malformed views, focus, phone layout and real browser clipboard.")
