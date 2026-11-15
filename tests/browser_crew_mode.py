"""Run python tests/browser_crew_mode.py --channel msedge for the Crew training layout."""

import argparse

from playwright.sync_api import expect, sync_playwright

from browser_evidence import CONSOLE, GAMEPAD


def check_crew(page, touch):
    page.goto(CONSOLE.as_uri())
    page.locator("#tabConsole").click()
    toggle = page.get_by_role("button", name="Crew mode", exact=True)
    context = page.locator("#crewContext")
    expect(toggle).to_have_attribute("aria-pressed", "false")
    expect(context).to_be_hidden()
    moon = page.locator('#presets [data-preset="moon"]')
    moon.click()
    evidence = page.locator("#conf").inner_text()
    estimate = page.locator("#pKeep").inner_text()

    if touch:
        toggle.tap()
        page.locator("#jumpReading").tap()
        expect(page.locator("#conf")).to_be_in_viewport()
    else:
        toggle.focus()
        page.keyboard.press("Enter")
    expect(toggle).to_have_attribute("aria-pressed", "true")
    expect(context).to_contain_text("Crew training")
    expect(context).to_contain_text("Moon Base (expected)")
    expect(page.locator("#conf")).to_have_text(evidence, use_inner_text=True)
    expect(page.locator("#pKeep")).to_have_text(estimate)
    scope = page.locator("#conf").bounding_box()
    prediction = page.locator("#read > .stage").bounding_box()
    assert scope["y"] + scope["height"] <= prediction["y"]
    target = page.get_by_role("button", name="Raise Oxygen", exact=True)
    assert target.bounding_box()["width"] >= 44 and target.bounding_box()["height"] >= 44
    target.click()
    expect(context).to_contain_text("Custom cabin air")
    expect(page.locator("#openSheet")).to_be_enabled()
    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")

    page.reload()
    page.locator("#tabConsole").click()
    expect(toggle).to_have_attribute("aria-pressed", "true")
    toggle.click()
    expect(context).to_be_hidden()
    expect(toggle).to_have_attribute("aria-pressed", "false")
    page.reload()
    page.locator("#tabConsole").click()
    expect(toggle).to_have_attribute("aria-pressed", "false")


def check_controller(page):
    page.add_init_script(GAMEPAD)
    page.goto(CONSOLE.as_uri())
    def pad(index):
        page.evaluate("button => window.pressPad(button)", index)

    pad(5)  # RB from Research to console.
    toggle = page.locator("#crewMode")
    expect(toggle.locator("kbd")).to_be_visible()
    pad(1)
    expect(toggle).to_have_attribute("aria-pressed", "true")
    pad(0)
    expect(page.locator("#sheet")).to_be_visible()
    pad(1)
    expect(page.locator("#sheet")).to_be_hidden()
    expect(toggle).to_have_attribute("aria-pressed", "true")
    pad(8)
    expect(page.locator("#mapBox")).to_have_class("map big")
    pad(1)
    expect(toggle).to_have_attribute("aria-pressed", "true")
    pad(1)
    expect(toggle).to_have_attribute("aria-pressed", "false")


if __name__ == "__main__":
    args = argparse.ArgumentParser(description=__doc__)
    args.add_argument("--channel", help="Installed Chromium channel, e.g. msedge")
    channel = args.parse_args().channel
    with sync_playwright() as pw:
        browser = pw.chromium.launch(channel=channel)
        for width, height, touch in ((1280, 800, False), (844, 390, False), (320, 568, True)):
            page = browser.new_page(viewport={"width": width, "height": height}, has_touch=touch)
            errors = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            check_crew(page, touch)
            assert not errors, errors
            page.close()
        check_controller(browser.new_page())
        browser.close()
    print("PASS: Crew layout, preset and custom air, preserved Moon reading and scope, large targets, "
          "keyboard, touch, controller context and saved preference.")
