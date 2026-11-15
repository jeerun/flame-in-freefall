"""Check the Ember lab on disk and with simulated local table service responses.

Run python tests/browser_ember_lab.py --channel msedge with Playwright installed.
"""
import argparse
import mimetypes
from pathlib import Path
from urllib.parse import urlparse

from playwright.sync_api import expect, sync_playwright

from browser_evidence import GAMEPAD


CONSOLE = Path(__file__).resolve().parents[1] / "console"


def check_offline(page):
    page.add_init_script(GAMEPAD)
    page.goto((CONSOLE / "ember-lab.html").as_uri() + "#table")
    expect(page.get_by_role("tab", name="Ask the table")).to_have_attribute("aria-selected", "true")
    expect(page.locator("#question")).to_be_disabled()
    expect(page.locator("#table-status")).to_contain_text("23 matching records")
    expect(page.locator(".filter-note")).to_contain_text("initial to final")
    page.locator(".sensor-row summary").first.click()
    expect(page.locator(".raw-row")).to_contain_text("Original CSV fields · line 2")
    expect(page.locator(".raw-row caption")).to_contain_text("Initial and final gas readings")
    expect(page.locator(".raw-row tr").filter(has_text="Final CO (ppm)")).to_contain_text("6")
    page.get_by_role("button", name="Next", exact=True).click()
    expect(page.locator(".result-pages")).to_contain_text("5–8 of 23")
    page.get_by_role("button", name="Show all readings for test B1.").click()
    expect(page.locator("#table-status")).to_contain_text("1 matching record")
    expect(page.locator(".sensor-row")).to_contain_text("0 → 6")
    page.evaluate("window.pressPad(5)")
    expect(page.locator("#film-tab")).to_be_focused()
    expect(page.locator("video")).to_be_visible()
    expect(page.locator("#film-live")).to_be_hidden()
    page.locator("#film-saved").click()
    page.locator(".film-frames button").last.click()
    page.wait_for_function("""() => {
      const v = document.querySelector("video");
      return !v.seeking && v.currentTime === FLEX_FILM_ANALYSIS.after;
    }""")
    page.locator("#film-tab").focus()
    page.keyboard.press("ArrowRight")
    expect(page.locator("#table-tab")).to_be_focused()
    assert page.url.endswith("#table")
    page.set_viewport_size({"width": 320, "height": 568})
    for tab in ["table-tab", "film-tab"]:
        page.locator("#" + tab).click()
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
    page.evaluate("void window.pressPad(1)")
    page.wait_for_url("**/index.html")
    assert urlparse(page.url).path.endswith("/index.html")


def check_server(page):
    requests = []
    server_results = []

    def serve(route):
        path = urlparse(route.request.url).path
        if path == "/lab/status":
            return route.fulfill(json={"table": True, "film": True})
        if path == "/lab/film":
            return route.fulfill(json={"before": None, "after": None})
        if path == "/lab/table":
            requests.append(route.request.post_data_json["question"])
            status, body = server_results.pop(0)
            return route.fulfill(status=status, json=body)
        asset = CONSOLE / path.lstrip("/")
        assert asset.resolve().is_relative_to(CONSOLE)
        if not asset.is_file():
            return route.fulfill(status=404, body="")
        return route.fulfill(body=asset.read_bytes(), content_type=mimetypes.guess_type(asset.name)[0] or "application/octet-stream")

    page.route("http://console.test/**", serve)
    page.goto("http://console.test/ember-lab.html#table")
    expect(page.locator("#question")).to_be_enabled()
    sample = page.evaluate("window.LAB_TABLE_EXAMPLES[2].result")
    server_results.extend([(200, sample), (200, {"status": "unsupported"}), (503, {"error": "Ember is busy."})])
    for query, message in [
        ("What did the instruments record for B1?", "1 matching record"),
        ("Which tests had stable oxygen throughout the test?", "only those two measurements"),
        ("Find B3 for me", "Ember is busy."),
    ]:
        page.locator("#question").fill(query)
        page.locator("#question").press("Enter")
        expect(page.locator("#table-status")).to_contain_text(message)
        expect(page.locator("#ask-question")).to_be_enabled()
    assert len(requests) == 3
    page.locator(".question-sample").first.click()
    expect(page.locator("#table-status")).to_contain_text("23 matching records")
    assert len(requests) == 3
    page.locator("#film-tab").click()
    page.locator("#film-live").click()
    expect(page.locator("#film-status")).to_contain_text("no single clear transition")
    page.locator("#film-saved").click()
    expect(page.locator(".film-frames button")).to_have_count(2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--channel", default="msedge")
    args = parser.parse_args()
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel=args.channel)
        for check in (check_offline, check_server):
            page = browser.new_page(viewport={"width": 1280, "height": 800})
            errors = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            check(page)
            assert not errors, errors
            page.close()
        browser.close()
    print("PASS: offline rows and clip seeking, mobile layout, keyboard/gamepad navigation, local table and vision states.")
