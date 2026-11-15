"""Optional browser regression. Run: python tests/browser_evidence.py [--channel msedge]

Requires Python Playwright and its Chromium browser, or an installed Chromium channel.
The console opens from disk. Only the Gamepad API is simulated.
"""
import argparse
from pathlib import Path

from playwright.sync_api import expect, sync_playwright


CONSOLE = Path(__file__).resolve().parents[1] / "console" / "index.html"
GAMEPAD = """
const pad = { connected: true, axes: [0, 0, 0, 0],
  buttons: Array.from({length: 17}, () => ({pressed: false})) };
Object.defineProperty(navigator, "getGamepads", { value: () => [pad] });
window.pressPad = async index => {
  const frames = () => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)));
  pad.buttons[index].pressed = true;
  await frames();
  pad.buttons[index].pressed = false;
  await frames();
};
"""


def check(page):
    page.add_init_script(GAMEPAD)
    page.goto(CONSOLE.as_uri())
    key = page.keyboard.press
    loc = page.locator

    def pad(button):
        page.evaluate("index => window.pressPad(index)", button)

    expect(loc("#title")).to_be_hidden()
    expect(loc("#tabResearch")).to_have_attribute("aria-current", "page")
    loc("#guideBtn").click()
    expect(loc("#controlGuide")).to_be_visible()
    key("2")  # The open guide owns input.
    expect(loc("#tabResearch")).to_have_attribute("aria-current", "page")
    pad(1)
    expect(loc("#controlGuide")).to_be_hidden()
    expect(loc("#guideBtn")).to_be_focused()
    expect(loc("#gravityCase")).to_be_visible()
    loc("#gravityCase").focus()
    key("Enter")  # Native activation of the launcher.
    evidence = loc("#ev-dialog")
    expect(evidence).to_be_visible()
    expect(loc("#ev-id")).to_contain_text("2-2")
    expect(loc("#ev-measures")).to_contain_text("7.6 cm")
    expect(loc("#ev-measures")).to_contain_text("?")
    key("Enter")
    expect(loc("#ev-measures")).to_contain_text("≈ 0 cm")
    expect(loc("#ev-source")).to_contain_text("CSV line 3")
    key("ArrowDown")
    expect(loc("#ev-id")).to_contain_text("2-5")
    expect(loc("#ev-result")).to_be_empty()
    key("2")
    expect(loc("#tabResearch")).to_have_attribute("aria-pressed", "true")
    key("Escape")
    expect(evidence).to_be_hidden()
    expect(loc("#gravityCase")).to_be_focused()

    pad(7)  # RT opens the sensor case from Research.
    expect(loc("#ev-id")).to_contain_text("B18")
    expect(loc("#ev-measures")).to_contain_text("17.4 → 17.4")
    pad(15)  # D-pad right selects the second answer.
    expect(evidence.locator("[data-choice='1']")).to_have_attribute("aria-pressed", "true")
    pad(0)
    expect(loc("#ev-measures")).to_contain_text("47 → 78")
    expect(loc("#ev-measures")).to_contain_text("0.34 → 0.42")
    expect(loc("#ev-source")).to_contain_text("CSV line 19")
    pad(5)  # The page shoulder button cannot navigate under an open case.
    expect(loc("#tabResearch")).to_have_attribute("aria-pressed", "true")
    pad(1)
    expect(evidence).to_be_hidden()
    pad(6)  # LT reopens Earth/orbit at the first case, with its answer hidden.
    expect(loc("#ev-id")).to_contain_text("2-2")
    expect(loc("#ev-result")).to_be_empty()
    pad(1)

    pad(5)  # RB navigates normally again.
    expect(loc("#tabConsole")).to_have_attribute("aria-pressed", "true")
    key("x")  # Moon preset: the closest test, with no selected star, is disruption #43.
    pad(8)  # View zooms the map; A opens its counterexample panel.
    expect(loc("#mapCounter")).to_be_visible()
    pad(0)
    pair = loc("#counterexample")
    expect(pair).to_contain_text("FLEX #43 records Disruption")
    example = pair.get_by_role("button", name="Show FLEX #108 example")
    expect(example).to_be_focused()
    pad(0)
    expect(pair.get_by_role("columnheader", name="Selected #108")).to_be_visible()
    expect(pair.get_by_role("columnheader", name="Counterexample #183")).to_be_visible()
    for label, values in [
        ("Pressure", ["0.708 atm", "0.703 atm"]),
        ("Starting diameter", ["3.75 mm", "3.72 mm"]),
        ("NASA recorded", ["Burned all its fuel", "Visible flame went out"]),
        ("Model chance of completion", ["25.6%", "25.7%"]),
    ]:
        row = pair.get_by_role("row").filter(has=page.get_by_role("rowheader", name=label))
        expect(row.get_by_role("cell")).to_have_text(values)
    key("3")
    expect(loc("#tabConsole")).to_have_attribute("aria-pressed", "true")
    pad(1)  # First B closes only the case; the second closes the map.
    expect(pair).to_be_hidden()
    expect(loc("#mapCounter")).to_be_visible()
    pad(1)
    expect(loc("#mapCounter")).to_be_hidden()
    key("1")
    expect(loc("#tabResearch")).to_have_attribute("aria-pressed", "true")

    # FLEX 29 has a modelled majority chance of disruption but no observed disruptions nearby.
    settings = "#view=v1&page=console&fuel=methanol&o2=30&p=1.009&co2=0&he=0&d0=2.57"
    page.goto(CONSOLE.as_uri() + settings)
    expect(loc("#confTitle")).to_have_text("Elevated modelled disruption chance")
    expect(loc("#confText")).to_contain_text("52% chance of disruption. 0 of 2 nearby FLEX tests")
    expect(loc("#disNote")).to_be_visible()
    page.goto(CONSOLE.as_uri() + settings.replace("o2=30", "o2=40"))
    expect(loc("#confTitle")).to_have_text("Outside the tested range")
    expect(loc("#disNote")).to_be_hidden()
    assert "Modelled chance that a test like this ends in disruption" not in page.evaluate("window.__flame.readingText()")


def check_phone(page):
    page.set_viewport_size({"width": 390, "height": 844})
    page.goto(CONSOLE.as_uri() + "#title")
    expect(page.locator("#title")).to_be_visible()
    page.get_by_role("button", name="Start exploring").click()
    for tab in ("tabResearch", "tabDrill", "tabConsole"):
        page.locator("#" + tab).click()
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth"), tab
    page.locator("#jumpReading").click()
    expect(page.locator("#read .stage")).to_be_in_viewport()
    page.locator("#jumpSettings").click()
    expect(page.locator("#rows .row").first).to_be_in_viewport()
    page.keyboard.press("1")
    page.locator("#oxBtn").click()
    expect(page.locator("#oxClose")).to_be_in_viewport()
    study = page.get_by_role("combobox", name="Investigation")
    study.select_option(label="CFI-G, normal flames (PSI-159)")
    expect(page.locator("#oxPick")).to_contain_text("Meeting both Moon Base thresholds: 20.")
    page.get_by_role("button", name="3 With pressure").click()
    chart = page.get_by_role("img", name="With pressure: oxygen versus pressure. Selected: CFI-G, normal flames")
    expect(chart).to_be_visible()
    assert chart.evaluate("(svg) => svg.viewBox.baseVal.width <= svg.parentElement.clientWidth + 1")
    study.press("b")  # Native select type-ahead picks BASS-II.
    expect(page.locator("#oxPick")).to_contain_text("The table gives no pressure.")
    page.evaluate("window.pressPad(13)")
    expect(study.locator("option:checked")).to_have_text("Saffire-II (PSI-99)")
    expect(page.locator("#oxPick")).to_contain_text("Saffire-II [PSI-99]")
    page.locator("#oxClose").click()
    expect(page.locator("#ox")).to_be_hidden()
    expect(page.locator("#oxBtn")).to_be_focused()
    page.set_viewport_size({"width": 320, "height": 568})
    page.locator("#tabConsole").click()
    assert page.evaluate("document.documentElement.scrollWidth <= document.documentElement.clientWidth")
    page.keyboard.press("z")
    expect(page.locator("#mapBox")).to_have_class("map big")
    assert page.evaluate("document.documentElement.scrollWidth <= document.documentElement.clientWidth")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--channel", help="Installed Chromium channel, e.g. msedge or chrome")
    args = parser.parse_args()
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel=args.channel)
        page = browser.new_page(viewport={"width": 1280, "height": 680})
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        check(page)
        check_phone(page)
        assert not errors, errors
        browser.close()
    print("Evidence cases, sourced readings, keyboard and gamepad controls, direct entry and phone navigation passed.")
