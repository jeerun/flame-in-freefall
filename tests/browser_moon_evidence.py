"""Offline Moon evidence check. Run python tests/browser_moon_evidence.py --channel msedge."""

import argparse
import csv
from urllib.parse import unquote, urlsplit

from playwright.sync_api import expect, sync_playwright

from browser_evidence import CONSOLE, GAMEPAD


CSV = CONSOLE.parents[1] / "data" / "raw" / "psi_tables" / "PSI-159_Experimental table_CFI-G_Normal Flames.csv"


def check_sources(page):
    details = page.locator("#sourceDetails")
    expect(details).to_have_js_property("open", False)
    details.locator("summary").press("Enter")
    table = details.locator("#sourceRows")
    expect(table).to_be_visible()
    expect(table.get_by_role("columnheader", name="O₂ fraction")).to_be_visible()
    expect(table).to_contain_text("bar")
    rows = table.locator("tbody tr")
    expect(rows).to_have_count(20)
    with CSV.open(encoding="utf-8-sig", newline="") as file:
        original = csv.DictReader(file, skipinitialspace=True)
        matching = {r["Test"]: [r["Fuel"], r["XO2 before test"], r["approx p (bar)"], str(original.line_num)]
                    for r in original if float(r["XO2 before test"]) >= .30
                    and 0 < float(r["approx p (bar)"]) * 14.696 / 1.01325 <= 10.2}
    for row in rows.all():
        test_id, *values = row.get_by_role("cell").all_inner_texts()
        assert matching.pop(test_id) == values, test_id
        source = urlsplit(row.get_by_role("link").get_attribute("href"))
        assert unquote(source.path).endswith("/" + CSV.name) and source.fragment == "L" + values[-1], test_id
    assert not matching, matching


def check(page, touch):
    page.goto(CONSOLE.as_uri())
    tools = page.locator("#researchTools")
    entry = tools.locator("#moonCase")
    expect(entry).to_have_attribute("href", "moon-evidence.html")
    if touch:
        expect(entry).to_be_hidden()
        tools.locator("summary").tap()
        entry.tap()
    else:
        expect(entry).to_be_visible()
        entry.press("Enter")
    expect(page).to_have_url(CONSOLE.with_name("moon-evidence.html").as_uri())

    def activate(label, pointer=False):
        button = page.get_by_role("button", name=label, exact=True)
        if touch:
            button.tap()
        elif pointer:
            button.click()
        else:
            button.press("Enter")

    title = page.locator("#stageTitle")

    def check_evidence(topic):
        expect(page.locator('#trail [aria-current="step"]')).to_have_text(topic)
        expect(title).to_be_focused()
        if topic == "Atmosphere":
            expect(title).to_have_text("The atmosphere matches")
            expect(page.locator("#reading")).to_have_text("20 / 746")
            expect(page.locator(".matrix i")).to_have_count(746)
            expect(page.locator(".matrix .match")).to_have_count(20)
        else:
            expect(title).to_have_text("All the matches are gas flames")
            expect(page.locator("#reading")).to_have_text("20 / 20")
            expect(page.locator(".specimens i")).to_have_count(20)
            expect(page.locator("#plotNote")).to_contain_text("21106A4")

    yes, more = "Yes, the air matches", "We need more evidence"
    activate(yes, pointer=True)
    check_evidence("Atmosphere")
    activate("Change answer")
    expect(page.locator("#sourceDetails")).to_be_hidden()
    for answer, first, second, next_button in (
            (more, "Specimen", "Atmosphere", "Check the atmosphere"),
            (yes, "Atmosphere", "Specimen", "Check the specimen")):
        activate(answer, pointer=True)
        check_evidence(first)
        expect(page.locator("#stageLabel")).to_have_text("Check 1 of 3 · " + first)
        expect(page.locator("#reason")).to_contain_text(
            "You chose the air match." if answer == yes else "You asked for more evidence.")
        expect(page.locator("#trail li")).to_have_text([first, second, "Gravity"])
        activate(next_button)
        check_evidence(second)
        expect(page.locator("#stageLabel")).to_have_text("Check 2 of 3 · " + second)
        activate("Previous")
        check_evidence(first)
        activate(next_button)
        activate("Check gravity")
        expect(title).to_have_text("The lunar panel is still an open question")
        expect(page.locator('#trail [aria-current="step"]')).to_have_text("Gravity")
        check_sources(page)
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
        activate("Try again")
        expect(page.get_by_role("button", name=yes)).to_be_visible()
        expect(page.get_by_role("button", name=more)).to_be_visible()
    page.get_by_role("link", name="Back to research").first.press("Enter")
    expect(page.locator("#orbit")).to_be_visible()
    if not touch:
        page.keyboard.press("g")
        expect(page.get_by_role("button", name="We need more evidence")).to_be_visible()


def check_controller(page):
    def pad(index):
        page.evaluate("button => window.pressPad(button)", index)

    page.goto(CONSOLE.as_uri())
    page.evaluate("void window.pressPad(10)")  # L3 on Research opens the Evidence lab.
    expect(page.get_by_role("heading", name="Ember evidence lab")).to_be_visible()
    moon_link = page.locator("#lab-moon-link")
    pad(13)  # Acquire focus, then wrap from the first control to the footer link.
    pad(12)
    expect(moon_link).to_be_focused()
    page.evaluate("void window.pressPad(0)")
    expect(page.get_by_role("heading", name="Moon evidence check")).to_be_visible()
    pad(13)
    expect(page.get_by_role("button", name="Yes, the air matches")).to_be_focused()
    pad(13)
    expect(page.get_by_role("button", name="We need more evidence")).to_be_focused()
    pad(0)
    title = page.locator("#stageTitle")
    expect(title).to_have_text("All the matches are gas flames")
    pad(13)
    pad(13)
    pad(13)
    sources = page.locator("#sourceDetails")
    expect(sources.locator("summary")).to_be_focused()
    pad(0)
    expect(sources).to_have_js_property("open", True)
    pad(1)
    expect(sources).to_have_js_property("open", False)
    expect(sources.locator("summary")).to_be_focused()
    pad(12)
    pad(12)
    pad(0)
    expect(title).to_have_text("The atmosphere matches")
    pad(13)
    pad(0)
    expect(title).to_have_text("The lunar panel is still an open question")
    pad(1)
    expect(title).to_have_text("The atmosphere matches")
    pad(1)
    expect(title).to_have_text("All the matches are gas flames")
    pad(1)
    expect(page.get_by_role("button", name="We need more evidence")).to_be_visible()
    page.evaluate("void window.pressPad(1)")  # B on the first screen leaves this document.
    expect(page.locator("#orbit")).to_be_visible()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--channel", help="Installed Chromium channel, e.g. msedge")
    args = parser.parse_args()
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel=args.channel)
        errors = []
        for touch, width, height in ((False, 1280, 800), (True, 390, 844)):
            context = browser.new_context(viewport={"width": width, "height": height},
                                          offline=True, has_touch=touch, is_mobile=touch)
            if not touch:
                context.add_init_script(GAMEPAD)
            page = context.new_page()
            page.on("pageerror", lambda error: errors.append(str(error)))
            check(page, touch)
            if not touch:
                check_controller(page)
            context.close()
        browser.close()
        assert not errors, errors
    print("PASS: distinct Moon answer paths, charts and trail order, change answer, 20 original PSI rows, "
          "restart, pointer, keyboard, touch and controller navigation offline.")
