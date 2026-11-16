"""Research home checks. Run python tests/browser_research_home.py --channel msedge."""

import argparse
import math
import re

from playwright.sync_api import expect, sync_playwright

from browser_evidence import CONSOLE, GAMEPAD


def check_orbit_rings(page):
    orbit = page.locator("#orbit")
    legend = page.locator("#orbitLegend")
    expect(legend).to_be_visible()
    for label in ("closer to the centre", "Stated objective", "Directly useful measurements",
                  "Indirect link", "Outside topic", "Dotted outer ring"):
        expect(legend).to_contain_text(label)
    expect(orbit).to_have_accessible_description(re.compile("Direct.*Strong.*Related", re.S | re.I))
    labels = orbit.locator("[data-ring-score]")
    expect(labels).to_have_count(4)
    rings = sorted(orbit.locator(":scope > circle[stroke-dasharray]").all(),
                   key=lambda circle: float(circle.get_attribute("r")))
    assert len(rings) == 4
    previous_boxes = []
    for score, ring in zip((3, 2, 1, 0), rings):
        number = orbit.locator(f'[data-ring-score="{score}"]')
        expect(number).to_be_visible()
        expect(number).to_contain_text(str(score))
        mark = number.bounding_box()
        circle = ring.bounding_box()
        dx = mark["x"] + mark["width"] / 2 - (circle["x"] + circle["width"] / 2)
        dy = mark["y"] + mark["height"] / 2 - (circle["y"] + circle["height"] / 2)
        assert abs(math.hypot(dx, dy) - circle["width"] / 2) < 3, score
        for box in previous_boxes:
            assert (box["x"] + box["width"] <= mark["x"] or mark["x"] + mark["width"] <= box["x"]
                    or box["y"] + box["height"] <= mark["y"] or mark["y"] + mark["height"] <= box["y"]), score
        previous_boxes.append(mark)


def check_home(page, width, height):
    page.set_viewport_size({"width": width, "height": height})
    page.goto(CONSOLE.as_uri())
    orbit = page.locator("#orbit")
    rank = page.locator("#rank")
    tools = page.locator("#researchTools")
    details = page.locator("#investigationDetails")
    summary = details.locator("summary")
    share = page.locator("#shareResearch")
    photo = page.locator('.research-hero img[src$="flex-flame.webp"]')
    expect(photo).to_be_visible()
    expect(photo).to_be_in_viewport()
    photo.evaluate("image => image.decode()")
    expect(orbit).to_be_visible()
    check_orbit_rings(page)
    expect(rank).to_be_hidden()
    expect(tools).to_have_js_property("open", False)
    expect(details).to_have_js_property("open", False)
    expect(share).to_have_accessible_name("Share view")
    expect(share).to_have_attribute("title", "Share view")
    expect(share).to_have_text("Share", use_inner_text=True)
    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
    if width > 820:
        for target in (orbit, summary, share):
            expect(target).to_be_in_viewport()

    tools_summary = tools.locator("summary")
    tools_summary.click()
    expect(tools).to_have_js_property("open", True)
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
    expect(page.locator("#orbitLegend")).to_be_hidden()
    page.locator("#orbitBtn").click()
    expect(orbit).to_be_visible()
    if width == 1280 and height == 800:
        page.get_by_role("button", name="Detection").click()
        check_orbit_rings(page)
        page.set_viewport_size({"width": 320, "height": 568})
        expect(orbit).to_have_attribute("viewBox", re.compile(r"^0 0 [23]\d\d "))
        check_orbit_rings(page)


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


def check_find(page):
    page.goto(CONSOLE.as_uri())
    find = page.get_by_role("button", name="Find", exact=True)
    dialog = page.locator("#findResearchDialog")
    search = dialog.get_by_role("searchbox")
    results = page.locator("#findResearchResults").get_by_role("button")
    card = page.locator("#card")
    original = card.get_attribute("data-investigation")
    expect(find).to_be_visible()
    expect(dialog).to_be_hidden()
    page.keyboard.press("f")
    expect(search).to_be_focused()
    search.press_sequentially("unmatched flight record")
    expect(search).to_have_value("unmatched flight record")
    expect(results).to_have_count(0)
    expect(page.locator("#findResearchStatus")).to_contain_text(re.compile(r"\b(?:no|0)\b", re.I))
    page.keyboard.press("Enter")
    expect(search).to_be_focused()
    page.keyboard.press("Escape")
    expect(find).to_be_focused()
    expect(card).to_have_attribute("data-investigation", original)

    # PSI-47 has zero Prevention relevance and ranks only under Detection.
    find.press("Enter")
    search.fill("dust and aerosol measurement feasibility")
    expect(results).to_have_count(1)
    expect(results).to_contain_text("PSI-47")
    search.press("ArrowDown")
    page.keyboard.press("Enter")
    expect(dialog).to_be_hidden()
    expect(card).to_have_attribute("data-investigation", "PSI-47")
    expect(page.locator("#hCard")).to_be_focused()
    detection = page.get_by_role("button", name="Detection")
    expect(detection).to_have_attribute("aria-pressed", "true")
    expect(page.locator("#orbit")).to_be_visible()
    page.locator("#shareResearch").click()
    page.keyboard.press("f")
    expect(dialog).to_be_hidden()
    code = page.locator("#shareOutput").input_value()
    restored = page.context.new_page()
    restored.goto(CONSOLE.as_uri() + code)
    expect(restored.locator("#card")).to_have_attribute("data-investigation", "PSI-47")
    expect(restored.get_by_role("button", name="Detection")).to_have_attribute("aria-pressed", "true")
    expect(restored.locator("#orbit")).to_be_visible()
    restored.close()
    page.keyboard.press("Escape")

    find.click()
    page.evaluate("window.pressPad(1)")  # B cancels and returns to the Find button.
    expect(dialog).to_be_hidden()
    expect(find).to_be_focused()
    page.locator("#orbitBtn").click()
    find.click()
    search.fill("PSI-10")
    expect(results.first.get_by_text("PSI-10", exact=True)).to_be_visible()
    search.fill("psi-101")
    expect(results).to_have_count(1)
    page.evaluate("window.pressPad(13)")
    expect(results.first).to_be_focused()
    page.evaluate("window.pressPad(0)")
    expect(dialog).to_be_hidden()
    expect(card).to_have_attribute("data-investigation", "PSI-101")
    expect(detection).to_have_attribute("aria-pressed", "true")
    expect(page.locator("#rank .sel")).to_contain_text("SAME-R")

    # FLEX has no Detection score; Suppression outranks both Prevention and Cabin air.
    find.click()
    search.fill("FLEX")
    expect(results.first).to_contain_text("PSI-69")
    search.press("Enter")
    expect(card).to_have_attribute("data-investigation", "PSI-69")
    expect(page.get_by_role("button", name="Suppression")).to_have_attribute("aria-pressed", "true")
    expect(page.locator("#rank .sel")).to_contain_text("FLEX")


def check_find_touch(page):
    page.goto(CONSOLE.as_uri())
    page.get_by_role("button", name="Find", exact=True).tap()
    dialog = page.locator("#findResearchDialog")
    dialog.get_by_role("searchbox").fill("PSI-69")
    result = dialog.get_by_role("button").filter(has_text="PSI-69")
    expect(result).to_be_in_viewport()
    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
    result.tap()
    expect(dialog).to_be_hidden()
    expect(page.locator("#card")).to_have_attribute("data-investigation", "PSI-69")
    expect(page.locator("#hCard")).to_be_in_viewport()
    # Keep the active Prevention topic even though FLEX's highest score is Suppression.
    expect(page.get_by_role("button", name="Prevention")).to_have_attribute("aria-pressed", "true")


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
        for size in ((1280, 800), (1280, 680), (390, 844), (320, 568)):
            page = context.new_page()
            check_home(page, *size)
            page.close()
        check_controller(context.new_page())
        check_find(context.new_page())
        phone = browser.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True)
        phone.on("page", lambda page: page.on("pageerror", lambda error: errors.append(str(error))))
        check_find_touch(phone.new_page())
        phone.close()
        assert not errors, errors
        browser.close()
    print("PASS: four labelled orbit rings, FLEX banner, orbit-first home, disclosures, Find by title and PSI ID, topic fallback, "
          "shared selection, responsive layout, keyboard, touch and controller.")
