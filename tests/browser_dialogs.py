"""Optional regression. Run: python tests/browser_dialogs.py [--channel msedge]."""
import argparse
from urllib.parse import urlparse

from playwright.sync_api import expect, sync_playwright

from browser_evidence import CONSOLE, GAMEPAD


def check(browser):
    page = browser.new_page()
    page.add_init_script(GAMEPAD)
    # Deliberately allow an aborted request to finish late so we exercise the UI's
    # stale-answer guard as well as its AbortSignal. No question leaves the page.
    page.add_init_script("""
      const originalFetch = window.fetch.bind(window);
      window.pendingAnswers = [];
      window.fetch = (url, options) => url === '/ask'
        ? new Promise(resolve => pendingAnswers.push({
            signal: options.signal, finish: text => resolve(new Response(text))
          }))
        : originalFetch(url, options);
    """)
    status = {"ok": True, "brains": [{"id": "fixture", "up": True, "label": "Local fixture"}]}

    def serve(route):
        url = urlparse(route.request.url)
        if url.hostname != "console.invalid":
            return route.abort()
        if url.path == "/ai":
            return route.fulfill(json=status)
        filename = url.path.rsplit("/", 1)[-1] or "index.html"
        asset = CONSOLE.parent / filename
        if asset.is_file():
            return route.fulfill(path=asset)
        return route.fulfill(status=404, body="")

    page.route("**/*", serve)
    page.goto("http://console.invalid/")
    loc, key = page.locator, page.keyboard.press
    loc("#tabConsole").click()
    loc("#igniteBtn").focus()
    key("Enter")
    expect(loc("#sim:modal")).to_be_visible()
    expect(loc("#simAgain")).to_be_focused()
    key("Shift+Tab")
    expect(loc("#simClose")).to_be_focused()
    key("Tab")
    expect(loc("#simAgain")).to_be_focused()
    key("3")
    page.evaluate("pressPad(5)")  # The right shoulder normally changes pages.
    expect(loc("#tabConsole")).to_have_attribute("aria-current", "page")
    page.evaluate("pressPad(1)")
    expect(loc("#igniteBtn")).to_be_focused()

    loc("#aiBtn").click()
    expect(loc("#ai:modal")).to_be_visible()
    questions = loc("#aiQs button")
    expect(questions.first).to_be_focused()
    key("ArrowDown")
    expect(questions.nth(1)).to_be_focused()
    key("Enter")
    assert page.evaluate("pendingAnswers.length === 2 && pendingAnswers[0].signal.aborted")
    loc("#aiInput").fill("x3?")
    key("Backspace")
    expect(loc("#aiInput")).to_have_value("x3")
    key("Escape")
    expect(loc("#aiBtn")).to_be_focused()
    assert page.evaluate("pendingAnswers[1].signal.aborted")

    page.evaluate("pressPad(9)")  # Reopen with a fresh request.
    expect(loc("#ai:modal")).to_be_visible()
    page.evaluate("""() => {
      pendingAnswers[2].finish('Current response.');
      pendingAnswers[1].finish('Stale response.');
      pendingAnswers[0].finish('Stale response.');
    }""")
    expect(loc("#aiAns")).to_contain_text("Current response.")
    expect(loc("#aiAns")).not_to_contain_text("Stale response.")
    expect(loc("#aiAns .took")).to_have_count(1)
    key("3")
    page.evaluate("pressPad(5)")
    expect(loc("#tabConsole")).to_have_attribute("aria-current", "page")
    status.update(ok=False, brains=[])
    page.evaluate("window.__flame.refreshAI(false)")
    expect(loc("#aiWho")).to_have_text("Ember is offline.")
    page.evaluate("pressPad(1)")
    expect(loc("#tabConsole")).to_be_focused()  # The offline launcher is now hidden.
    page.close()

    disk = browser.new_page()
    disk.goto(CONSOLE.as_uri())
    expect(disk.locator("#aiBtn")).to_be_hidden()
    disk.locator("#tabConsole").click()
    disk.locator("#igniteBtn").click()
    expect(disk.locator("#sim:modal")).to_be_visible()
    disk.keyboard.press("Escape")
    expect(disk.locator("#igniteBtn")).to_be_focused()
    disk.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--channel", help="Installed Chromium channel, e.g. msedge")
    args = parser.parse_args()
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel=args.channel)
        check(browser)
        print("Ignite and Ember modal focus, controller isolation, stale answers and offline fallback passed.")
