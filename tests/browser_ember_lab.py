"""Check the Ember lab on disk and with simulated local table service responses.

Run python tests/browser_ember_lab.py --channel msedge with Playwright installed.
"""
import argparse
import mimetypes
from pathlib import Path
import re
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
    player = page.locator("video")
    page.get_by_role("button", name="FLEX · Droplet").focus()
    page.evaluate("window.pressPad(13)")
    fabric = page.get_by_role("button", name="Saffire-I · Fabric")
    expect(fabric).to_be_focused()
    page.evaluate("window.pressPad(0)")
    expect(fabric).to_have_attribute("aria-pressed", "true")
    expect(page.locator("#film-title")).to_have_text("Saffire-I aboard Cygnus")
    expect(page.locator("#film-saved")).to_be_hidden()
    page.wait_for_function("""() => {
      const v = document.querySelector("video");
      return v.paused && v.currentTime === 0 && v.videoWidth === 320 && v.videoHeight === 230
        && Math.abs(v.duration - 22.96) < 0.01 && v.currentSrc.endsWith("/saffire-1.webm");
    }""")
    for seconds in (2, 22):
        page.locator(f'button[data-seconds="{seconds}"]').press("Enter")
        page.wait_for_function("""time => {
          const clip = document.querySelector("video");
          return clip.paused && !clip.seeking && Math.abs(clip.currentTime - time) < .01;
        }""", arg=seconds)
    page.locator("#observation-answer summary").click()
    expect(page.locator("#observation-answer p")).to_contain_text("Green LEDs")
    player.evaluate("clip => clip.play()")
    page.locator("#film-tab").focus()
    page.keyboard.press("ArrowRight")
    expect(page.locator("#table-tab")).to_be_focused()
    assert page.url.endswith("#table")
    expect(player).to_have_js_property("paused", True)
    expect(player).to_have_js_property("currentTime", 0)
    page.locator("#film-tab").click()
    expect(page.locator("#observation-answer")).to_have_js_property("open", False)
    page.get_by_role("button", name="FLEX · Droplet").click()
    expect(page.locator("#film-title")).to_have_text("FLEX on the space station")
    expect(page.locator("#film-result")).to_be_hidden()
    expect(page.locator("#film-saved")).to_be_enabled()
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
    page.get_by_role("button", name="Saffire-I · Fabric").click()
    expect(page.locator("#film-live")).to_be_hidden()
    expect(page.locator(".film-frames button")).to_have_count(0)


def check_more_footage(page):
    page.goto((CONSOLE / "ember-lab.html").as_uri())
    picker = page.get_by_role("group", name="Choose an experiment")
    expect(picker.get_by_role("button")).to_have_count(6)
    player = page.locator("video")
    answer = page.locator("#observation-answer")
    for clip, file, credit, cues in [
        ("FLEX-2 · Soot", "flex-2", "Science@NASA", [2, 12]),
        ("SoFIE-GEL · Extinction", "sofie-gel", "NASA", [3, 36]),
        ("Saffire-V · Ribbed plastic", "saffire-5", "NASA Glenn", [4, 15]),
        ("Saffire-VI · Acrylic", "saffire-6", "NASA Glenn", [30, 47]),
    ]:
        button = picker.get_by_role("button", name=clip, exact=True)
        button.tap()
        expect(button).to_have_attribute("aria-pressed", "true")
        expect(picker.locator('[aria-pressed="true"]')).to_have_count(1)
        expect(page.locator("#film-note")).to_contain_text(credit)
        expect(page.locator("#film-source")).to_have_attribute("href", re.compile(r"^https://"))
        expect(page.locator("#film-saved")).to_be_hidden()
        expect(page.locator("#film-live")).to_be_hidden()
        expect(answer).to_have_js_property("open", False)
        page.wait_for_function("""file => {
          const v = document.querySelector("video");
          return v.currentSrc.endsWith("/" + file + ".webm") && v.readyState >= 1
            && v.videoWidth > 0 && v.videoHeight > 0 && v.paused && v.currentTime === 0;
        }""", arg=file)
        assert player.evaluate("""async v => { const image = new Image(); image.src = v.poster;
            await image.decode(); return image.naturalWidth > 0; }""")
        for seconds in cues:
            page.locator(f'button[data-seconds="{seconds}"]').tap()
            page.wait_for_function("""seconds => {
              const v = document.querySelector("video");
              return !v.seeking && v.paused && Math.abs(v.currentTime - seconds) < .01;
            }""", arg=seconds)
        answer.locator("summary").tap()
        expect(answer.locator("p")).to_be_visible()
        related = page.locator("#film-related")
        if file.startswith("saffire"):
            expect(related).to_be_visible()
            expect(related).to_contain_text("Saffire-IV fabric footage online")
            expect(related).to_have_attribute("href", re.compile(r"^https://www\.nasa\.gov/.*/the-flame-of-discovery-"))
        elif file == "flex-2":
            expect(related).to_be_visible()
            expect(related).to_contain_text("FLEX-2 flame oscillations online")
            expect(related).to_have_attribute("href", "https://www.youtube.com/watch?v=qQQ1OHW1_F4")
            expect(page.locator("#film-source")).to_have_attribute("href", "https://svs.gsfc.nasa.gov/11640/")
        else:
            expect(related).to_be_hidden()
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
    page.get_by_role("button", name="FLEX · Droplet").tap()
    expect(page.locator("#film-saved")).to_be_enabled()
    expect(page.locator("#observation")).to_be_hidden()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--channel", default="msedge")
    args = parser.parse_args()
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel=args.channel)
        for check in (check_offline, check_server, check_more_footage):
            phone = check == check_more_footage
            page = browser.new_page(viewport={"width": 320 if phone else 1280, "height": 568 if phone else 800},
                                    offline=check != check_server, has_touch=phone, reduced_motion="reduce")
            errors = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            check(page)
            assert not errors, errors
            page.close()
        browser.close()
    print("PASS: all six offline clips, paused observations, mobile touch, keyboard/gamepad navigation, table and FLEX vision states.")
