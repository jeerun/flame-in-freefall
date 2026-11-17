"""Run python tests/browser_crew_mode.py --channel msedge for the Crew training layout."""

import argparse

from playwright.sync_api import expect, sync_playwright

from browser_evidence import CONSOLE, GAMEPAD


def check_settings_layout(page):
    page.goto(CONSOLE.as_uri())
    page.locator("#tabConsole").click()
    page.locator('[data-preset="earth"]').click()
    page.locator('#rows button[aria-label^="Raise Carbon dioxide"]').click()
    expect(page.locator("#cabinContext")).to_have_text("Custom cabin air")

    presets = page.locator("#presets button").all()
    fuel_controls = page.locator("#rows .row:first-child .name, .fuels button").all()
    assert len(presets) == 3 and len(fuel_controls) == 3
    preset_boxes = [button.bounding_box() for button in presets]
    fuel_top = min(control.bounding_box()["y"] for control in fuel_controls)
    assert max(box["y"] + box["height"] for box in preset_boxes) <= fuel_top

    page.locator('[data-fuel="methanol"]').click()
    expect(page.locator('[data-fuel="methanol"]')).to_have_attribute("aria-pressed", "true")
    export = page.locator("#csvBtn")
    export.click(trial=True)
    expect(export).to_be_in_viewport(ratio=.99)
    footer = page.locator("#settingsExport").bounding_box()
    settings = page.locator("#consoleSettings").bounding_box()
    assert footer["y"] + footer["height"] <= settings["y"] + settings["height"] + 1


def check_crew(page, touch):
    page.goto(CONSOLE.as_uri())
    page.locator("#tabConsole").click()
    toggle = page.locator("#crewMode")
    context = page.locator("#crewContext")
    settings = page.locator("#crewSettingsToggle")
    rows = page.locator("#rows")
    map_toggle = page.locator("#crewMapToggle")
    chart = page.locator("#mapBox")
    expect(toggle).to_have_attribute("aria-pressed", "false")
    expect(context).to_be_hidden()
    expect(rows).to_be_visible()
    expect(chart).to_be_visible()
    moon = page.locator('#presets [data-preset="moon"]')
    moon.click()
    evidence = page.locator("#conf").inner_text()
    estimate = page.locator("#pKeep").inner_text()

    if touch:
        toggle.tap()
    else:
        toggle.focus()
        page.keyboard.press("Enter")
    expect(toggle).to_have_attribute("aria-pressed", "true")
    expect(toggle).to_have_accessible_name("Exit Crew mode")
    expect(context).to_contain_text("Cabin briefing")
    expect(context).to_contain_text("Moon Base (expected)")
    expect(context).to_be_in_viewport(ratio=1)
    expect(page.locator("#conf")).to_be_in_viewport()
    conditions = page.locator("#crewConditions")
    expect(conditions).to_contain_text("30% oxygen")
    expect(rows).to_be_hidden()
    expect(chart).to_be_hidden()
    expect(settings).to_have_attribute("aria-expanded", "false")
    expect(map_toggle).to_have_attribute("aria-expanded", "false")
    expect(page.locator("#conf")).to_have_text(evidence, use_inner_text=True)
    expect(page.locator("#pKeep")).to_have_text(estimate)
    scope = page.locator("#conf").bounding_box()
    prediction = page.locator("#read > .stage").bounding_box()
    assert scope["y"] + scope["height"] <= prediction["y"]

    map_toggle.click()
    expect(map_toggle).to_have_attribute("aria-expanded", "true")
    expect(chart).to_be_visible()
    page.locator("#mapBigBtn").click()
    expect(page.locator("#mapFine")).to_be_visible()
    page.keyboard.press("Escape")
    expect(chart).to_be_visible()
    map_toggle.click()
    page.keyboard.press("z")
    expect(page.locator("#mapFine")).to_be_visible()
    page.keyboard.press("Escape")
    expect(chart).to_be_hidden()
    expect(map_toggle).to_have_attribute("aria-expanded", "false")

    settings.focus()
    page.keyboard.press("Enter")
    expect(settings).to_have_attribute("aria-expanded", "true")
    target = page.get_by_role("button", name="Raise Oxygen", exact=True)
    assert target.bounding_box()["width"] >= 44 and target.bounding_box()["height"] >= 44
    target.click()
    expect(context).to_contain_text("Custom cabin air")
    oxygen = page.get_by_role("slider", name="Oxygen in %", exact=True)
    expect(conditions).to_contain_text(f"{float(oxygen.input_value()):g}% oxygen")
    settings.click()
    expect(rows).to_be_hidden()
    page.keyboard.press("ArrowDown")
    expect(rows).to_be_visible()
    expect(settings).to_have_attribute("aria-expanded", "true")
    expect(page.locator("#openSheet")).to_be_enabled()
    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")

    page.reload()
    page.locator("#tabConsole").click()
    expect(toggle).to_have_attribute("aria-pressed", "true")
    expect(rows).to_be_hidden()
    expect(chart).to_be_hidden()
    toggle.click()
    expect(context).to_be_hidden()
    expect(toggle).to_have_attribute("aria-pressed", "false")
    expect(settings).to_be_hidden()
    expect(map_toggle).to_be_hidden()
    expect(rows).to_be_visible()
    expect(chart).to_be_visible()
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
    expect(page.locator("#mapFine")).to_be_visible()
    pad(1)
    expect(toggle).to_have_attribute("aria-pressed", "true")
    expect(page.locator("#mapBox")).to_be_hidden()
    pad(15)
    expect(page.locator("#rows")).to_be_visible()
    expect(page.locator("#crewSettingsToggle")).to_have_attribute("aria-expanded", "true")
    page.locator("#crewSettingsToggle").click()
    pad(1)
    expect(toggle).to_have_attribute("aria-pressed", "false")


if __name__ == "__main__":
    args = argparse.ArgumentParser(description=__doc__)
    args.add_argument("--channel", help="Installed Chromium channel, e.g. msedge")
    channel = args.parse_args().channel
    with sync_playwright() as pw:
        browser = pw.chromium.launch(channel=channel)
        for width, height in ((1366, 760), (1920, 864)):
            page = browser.new_page(viewport={"width": width, "height": height})
            check_settings_layout(page)
            page.close()
        for width, height, touch in ((1280, 800, False), (844, 390, False), (320, 568, True)):
            page = browser.new_page(viewport={"width": width, "height": height}, has_touch=touch)
            errors = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            check_crew(page, touch)
            assert not errors, errors
            page.close()
        check_controller(browser.new_page())
        browser.close()
    print("PASS: Crew briefing on desktop, handheld and phone; on-demand settings and FLEX map; "
          "preserved Moon reading and evidence; keyboard, touch, controller and saved mode.")
