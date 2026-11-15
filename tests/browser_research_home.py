"""Research home checks. Run python tests/browser_research_home.py --channel msedge."""

import argparse

from playwright.sync_api import expect, sync_playwright

from browser_evidence import CONSOLE, GAMEPAD


def check_home(page, width, height):
    page.set_viewport_size({"width": width, "height": height})
    page.goto(CONSOLE.as_uri())
    orbit = page.locator("#orbit")
    rank = page.locator("#rank")
    tools = page.locator("#researchTools")
    details = page.locator("#investigationDetails")
    summary = details.locator("summary")
    share = page.locator("#shareResearch")
    expect(orbit).to_be_visible()
    expect(rank).to_be_hidden()
    expect(tools).to_have_js_property("open", False)
    expect(details).to_have_js_property("open", False)
    expect(share).to_have_accessible_name("Share view")
    expect(share).to_have_attribute("title", "Share view")
    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
    if width > 820:
        for target in (orbit, summary, share):
            expect(target).to_be_in_viewport()

    tools_summary = tools.locator("summary")
    tools_summary.press("Enter")
    for control_id in ("oxBtn", "gravityCase", "sensorCase", "evidenceLab"):
        page.keyboard.press("Tab")
        expect(page.locator("#" + control_id)).to_be_focused()
    tools_summary.press("Enter")
    expect(tools).to_have_js_property("open", False)

    summary.focus()
    page.keyboard.press("Enter")
    expect(details).to_have_js_property("open", True)
    expect(details.get_by_text("Hardware", exact=True)).to_be_visible()
    page.keyboard.press("Space")
    expect(details).to_have_js_property("open", False)

    share.focus()
    page.keyboard.press("Enter")
    expect(page.locator("#shareCopy")).to_be_focused()
    code = page.locator("#shareOutput").input_value()
    assert "orbit=1" in code
    page.keyboard.press("Escape")
    expect(share).to_be_focused()
    page.goto(CONSOLE.as_uri() + code.replace("orbit=1", "orbit=0"))
    expect(rank).to_be_visible()
    expect(orbit).to_be_hidden()
    page.locator("#orbitBtn").click()
    expect(orbit).to_be_visible()


def check_controller(page):
    page.goto(CONSOLE.as_uri())
    details = page.locator("#investigationDetails")
    page.evaluate("window.pressPad(0)")  # A opens the selected investigation's details.
    expect(details).to_have_js_property("open", True)
    page.evaluate("window.pressPad(1)")  # B closes only that disclosure.
    expect(details).to_have_js_property("open", False)
    selected = page.locator("#card").get_attribute("data-investigation")
    page.evaluate("window.pressPad(13)")  # D-pad down selects the next record.
    expect(page.locator("#card")).not_to_have_attribute("data-investigation", selected)
    expect(details).to_have_js_property("open", False)
    page.evaluate("window.pressPad(2)")  # X switches to the ranked list.
    expect(page.locator("#rank")).to_be_visible()
    page.evaluate("window.pressPad(2)")
    expect(page.locator("#orbit")).to_be_visible()
    page.evaluate("window.pressPad(11)")  # R3 opens Share view for the selected investigation.
    expect(page.locator("#shareViewDialog")).to_be_visible()
    page.evaluate("window.pressPad(1)")
    expect(page.locator("#shareViewDialog")).to_be_hidden()
    expect(page.locator("#shareResearch")).to_be_focused()
    page.reload()  # Direct controller shortcuts also work before a page control takes focus.
    page.evaluate("window.pressPad(6)")  # LT still opens an activity with the tools collapsed.
    expect(page.locator("#ev-dialog")).to_be_visible()
    page.evaluate("window.pressPad(1)")
    expect(page.locator("#ev-dialog")).to_be_hidden()
    expect(page.locator("#researchTools summary")).to_be_focused()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--channel", help="Installed Chromium channel, e.g. msedge")
    args = parser.parse_args()
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel=args.channel)
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        context.add_init_script(GAMEPAD)
        errors = []
        context.on("page", lambda page: page.on("pageerror", lambda error: errors.append(str(error))))
        for size in ((1280, 800), (1280, 680), (390, 844)):
            page = context.new_page()
            check_home(page, *size)
            page.close()
        check_controller(context.new_page())
        assert not errors, errors
        browser.close()
    print("PASS: orbit-first home, disclosures, share focus, list links, responsive layout and controller.")
