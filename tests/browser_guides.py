"""The tour, "What would put this flame out?", and the handheld sizes. Run python tests/browser_guides.py --channel msedge

Requires Python Playwright and its Chromium browser, or an installed Chromium channel.
The console opens from disk. Only the Gamepad API is simulated.
"""
import argparse

from playwright.sync_api import expect, sync_playwright

from browser_evidence import CONSOLE, GAMEPAD

# What is on screen now: text under 12 px, controls under 38 px, and chart labels that lie on one another.
MEASURE = """() => {
  const seen = e => { const r = e.getBoundingClientRect(); return r.width > 0 && r.height > 0 && r.bottom > 0 && r.top < innerHeight && !e.closest('[hidden]') && getComputedStyle(e).visibility !== 'hidden'; };
  const top = [...document.querySelectorAll('dialog[open]')].pop() || [...document.querySelectorAll('.sheet:not([hidden])')].pop();
  const all = (top ? [top] : [...document.querySelectorAll('main:not([hidden]), header.top')]).flatMap(r => [...r.querySelectorAll('*')]).filter(seen);
  const small = all.filter(e => [...e.childNodes].some(n => n.nodeType === 3 && n.textContent.trim()) && parseFloat(getComputedStyle(e).fontSize) < 11.95)
    .map(e => e.textContent.trim().slice(0, 24));
  const tiny = all.filter(e => e.matches('button, a[href], select')).filter(e => e.getBoundingClientRect().height < 38)
    .map(e => (e.id || e.textContent.trim().slice(0, 16)) + ' ' + Math.round(e.getBoundingClientRect().height));
  const clash = [];
  all.filter(e => e.matches('svg')).forEach(svg => {
    const labels = [...svg.querySelectorAll('text')].filter(t => t.textContent.trim()).map(t => [t.textContent.trim().slice(0, 18), t.getBoundingClientRect()]);
    labels.forEach(([a, p], i) => labels.slice(i + 1).forEach(([b, q]) => {
      if (p.left < q.right - 1 && q.left < p.right - 1 && p.top < q.bottom - 1 && q.top < p.bottom - 1) clash.push(a + ' / ' + b);
    }));
  });
  const d = document.documentElement;
  return { small, tiny, clash, scrolls: d.scrollWidth > innerWidth || d.scrollHeight > innerHeight };
}"""

TOUR = """() => {
  const card = document.getElementById('tour'), ring = document.getElementById('tourRing');
  const c = card.getBoundingClientRect(), r = ring.getBoundingClientRect();
  return { count: card.querySelector('.count').textContent, page: document.body.dataset.page,
    inside: c.left >= 0 && c.top >= 0 && c.right <= innerWidth && c.bottom <= innerHeight,
    covers: c.left < r.right && r.left < c.right && c.top < r.bottom && r.top < c.bottom,
    ring: [r.left, r.top, r.right, r.bottom], tools: document.getElementById('researchTools').open };
}"""


def clean(page, what, allow_small=()):
    m = page.evaluate(MEASURE)
    small = [t for t in m["small"] if not any(t.startswith(a) for a in allow_small)]
    assert not small, f"{what}: text under 12 px: {small}"
    assert not m["tiny"], f"{what}: controls under 38 px: {m['tiny']}"
    assert not m["clash"], f"{what}: labels overlap: {m['clash']}"
    assert not m["scrolls"], f"{what}: the page scrolls"


def check_sizes(page):
    """A handheld in full screen: 1280 x 800."""
    page.set_viewport_size({"width": 1280, "height": 800})
    page.goto(CONSOLE.as_uri())
    key, loc = page.keyboard.press, page.locator
    expect(loc("#orbit")).to_be_visible()
    expect(loc(".research-lead")).to_have_text("Fire safety for the Moon and Mars, from NASA's microgravity experiments")
    clean(page, "research, orbit")
    key("x")
    clean(page, "research, list")
    key("x")
    for level in "123":
        key("o")
        key(level)
        expect(loc("#ox")).to_be_visible()
        clean(page, "Oxygen map " + level)
        if level == "3":   # the pressure scale sits to the right of the plot, clear of the data
            edge = page.evaluate("""() => { const t = [...document.querySelectorAll('#oxSvg text')];
              const axis = t.filter(e => /^[\\d.]+ atm$/.test(e.textContent)).map(e => e.getBoundingClientRect().left);
              const dots = [...document.querySelectorAll('#oxSvg circle')].map(e => e.getBoundingClientRect().right);
              return { axis: axis.length, right: Math.min(...axis) > Math.max(...dots) }; }""")
            assert edge == {"axis": 6, "right": True}, edge
        key("Escape")
    key("2")
    expect(loc("#viewConsole")).to_be_visible()
    clean(page, "console")
    step = loc("#rows .step").first.bounding_box()
    assert step["width"] >= 40 and step["height"] >= 40, step
    key("i")
    expect(loc("#sim")).to_be_visible()
    clean(page, "Ignite")
    key("Escape")
    key("3")
    expect(loc("#drillLogEmpty")).to_be_visible()
    for _ in range(2):
        loc("#drillBurn").click()
        loc("#drillNext").click()
    expect(loc("#drillLog li")).to_have_count(2)
    expect(loc("#drillLogEmpty")).to_be_hidden()
    first = loc("#drillLog li").first
    expect(first).to_contain_text("FLEX ")
    assert page.evaluate("""() => { const t = window.__flame.drill().rounds[0], li = document.querySelector('#drillLog li');
      return li.textContent.includes('FLEX ' + t[0]) && li.querySelector('.end').textContent === (t[8] === 'Completion' ? 'Burned all its fuel' : 'Went out first')
        && li.querySelectorAll('.hit, .miss').length === 2; }""")
    clean(page, "Fire drill")
    # A lower window keeps the earlier sizes, and still nothing scrolls.
    page.set_viewport_size({"width": 1280, "height": 680})
    for tab in ("#tabResearch", "#tabConsole", "#tabDrill"):
        loc(tab).click()
        assert not page.evaluate(MEASURE)["scrolls"], tab


def check_advisor(page):
    page.set_viewport_size({"width": 1280, "height": 800})
    page.add_init_script(GAMEPAD)
    page.goto(CONSOLE.as_uri())
    key, loc = page.keyboard.press, page.locator
    values = lambda: page.evaluate("() => Object.assign({ fuel: window.__flame.state.fuel, sheet: window.__flame.state.sheet }, window.__flame.state.values)")

    def pad(button):
        page.evaluate("index => window.pressPad(index)", button)

    key("2")
    expect(loc("#openAdvisor")).to_be_visible()
    key("q")
    panel = loc("#advisor")
    expect(panel).to_be_visible()
    expect(panel.locator("h2")).to_have_text("What would put this flame out?")
    expect(panel.locator(".now")).to_contain_text("57 %")
    options = panel.locator("li")
    expect(options).to_have_count(3)
    expect(options.nth(0).locator("strong")).to_have_text("Lower oxygen to 19 %")
    expect(options.nth(0).locator(".evidence")).to_have_text("Nearby real tests: 7 of 10 with a clear outcome went out.")
    expect(options.nth(1).locator("strong")).to_have_text("Add carbon dioxide to 10 %")
    expect(options.nth(2).locator("strong")).to_contain_text("Add helium to ")
    expect(panel.locator(".left")).to_contain_text("Pressure is not offered")
    expect(panel.locator(".fine")).to_contain_text("Not a crew procedure")
    expect(panel.locator(".fine")).to_contain_text("does not check that the changed air is safe to breathe")
    clean(page, "advisor")
    promised = options.nth(0).locator(".result b").inner_text()
    expect(options.nth(0).locator("button")).to_be_focused()
    key("ArrowDown")
    expect(options.nth(1).locator("button")).to_be_focused()
    key("ArrowUp")
    key("Enter")
    expect(panel).to_be_hidden()
    assert values()["o2"] == 19 and values()["co2"] == 0
    assert loc("#pKeep").inner_text() + " %" == promised, "the console shows the number the panel promised"
    expect(loc("#toasts")).to_contain_text("Trying oxygen 21 % to 19 %")
    key("q")
    expect(panel.locator(".goal")).to_contain_text("already expects this flame to go out")
    expect(panel.locator(".undo")).to_contain_text("You tried: oxygen 21 % to 19 %.")
    expect(panel.locator(".undo button")).to_be_focused()
    key("Enter")
    assert values()["o2"] == 21
    expect(options).to_have_count(3)
    expect(panel.locator(".undo")).to_have_count(0)
    key("Escape")
    expect(panel).to_be_hidden()

    # Moon Base air, with the controller: A opens the explanation, RT asks what would put it out.
    key("x")
    assert values()["o2"] == 30
    pad(7)                                           # with no panel open RT still replays a test
    expect(panel).to_be_hidden()
    pad(0)
    assert values()["sheet"]
    expect(loc("#sheetAdvisor")).to_be_visible()
    pad(7)
    expect(panel).to_be_visible()
    expect(options.nth(0).locator("strong")).to_have_text("Lower oxygen to 19 %")
    expect(options.nth(0).locator(".detail")).to_contain_text("under the 30 % oxygen of Moon Base (expected) air")
    expect(options.nth(1).locator(".result span")).to_have_text("not enough alone")
    expect(options.nth(2).locator(".result span")).to_have_text("not enough alone")
    pad(13)
    expect(options.nth(1).locator("button")).to_be_focused()
    pad(1)                                           # B closes this panel only
    expect(panel).to_be_hidden()
    assert values()["sheet"]
    pad(1)
    assert not values()["sheet"]
    expect(loc("#viewConsole")).not_to_have_class("crew-mode")
    pad(0); pad(7); pad(0)                           # A, RT, then A on the first option
    expect(panel).to_be_hidden()
    assert values()["o2"] == 19 and not values()["sheet"], "A applied the change and did not reopen the explanation"

    # Methanol, a gas already in the air, and settings outside the tests.
    page.evaluate("() => { const f = window.__flame; f.reset(); f.state.fuel = 'methanol'; f.state.values.o2 = 30; f.state.values.p = 0.694; f.render(); }")
    loc("#openAdvisor").click()
    expect(panel.locator(".left")).to_contain_text("Carbon dioxide is left out: for methanol the tests do not settle which way it pushes.")
    assert not page.evaluate("() => [...document.querySelectorAll('#advisor li strong')].some(e => /carbon dioxide/.test(e.textContent))")
    key("Escape")
    page.evaluate("() => { const f = window.__flame; f.reset(); f.state.values.he = 10; f.render(); }")
    loc("#openAdvisor").click()
    expect(panel.locator(".left")).to_contain_text("no FLEX test mixed it with helium")
    key("Escape")
    page.evaluate("() => { const f = window.__flame; f.reset(); f.state.values.o2 = 38; f.render(); }")
    loc("#openAdvisor").click()
    expect(panel.locator(".now")).to_contain_text("outside what FLEX tested")
    expect(options).to_have_count(0)
    key("Escape")
    page.evaluate("() => window.__flame.reset()")
    loc("#crewMode").click()
    expect(loc("#openAdvisor")).to_be_visible()       # the crew briefing keeps the door
    loc("#crewMode").click()


def check_tour(page):
    page.set_viewport_size({"width": 1280, "height": 800})
    page.goto(CONSOLE.as_uri())                       # the simulated controller is installed by the caller
    key, loc = page.keyboard.press, page.locator
    tour = lambda: page.evaluate(TOUR)

    def pad(button):
        page.evaluate("index => window.pressPad(index)", button)

    button = loc("#tourBtn")
    expect(button).to_be_visible()
    expect(button).to_contain_text("Take the tour")
    expect(button).to_have_class("guide-button tour-button fresh")
    key("t")
    card = loc("#tour")
    expect(card).to_be_visible()
    pages = []
    for n in range(1, 10):
        expect(card.locator(".count")).to_have_text(f"Tour · {n} of 9")
        page.wait_for_timeout(330)                    # the card and the ring glide to their place
        step = tour()
        pages.append(step["page"])
        assert step["inside"] and not step["covers"], step
        assert step["tools"] == (n == 4), "the research tools open for their step only"
        assert not page.evaluate(MEASURE)["scrolls"]
        if n == 1:
            box = loc("#orbit").bounding_box()
            assert abs(step["ring"][0] - (box["x"] - 6)) < 2 and abs(step["ring"][3] - (box["y"] + box["height"] + 6)) < 2, step
            key("2")                                  # other keys do not reach the page during the tour
            key("x")
            assert page.evaluate("() => document.body.dataset.page === 'research' && window.__flame.view.orbit")
            key("ArrowRight"); key("ArrowLeft")       # and Left goes back a step
            expect(card.locator(".count")).to_have_text("Tour · 1 of 9")
        expect(card.locator("button.next")).to_have_text("AFinish" if n == 9 else "ANext")
        key("ArrowRight")
    assert pages == ["research"] * 4 + ["console"] * 3 + ["drill"] * 2, pages
    expect(card).to_be_hidden()
    expect(loc("#tourRing")).to_be_hidden()
    assert page.evaluate("() => document.body.dataset.page") == "research", "Finish returns to where the tour began"
    assert page.evaluate("() => localStorage.getItem('flame.tour')") == "true"
    expect(button).to_have_class("guide-button tour-button")
    expect(button).to_contain_text("Tour")

    # Controller: View starts it on the research page, A goes on, Left goes back, B ends it and does nothing else.
    pad(8)
    expect(card.locator(".count")).to_have_text("Tour · 1 of 9")
    for _ in range(4):
        pad(0)
    expect(card.locator(".count")).to_have_text("Tour · 5 of 9")
    pad(14)
    expect(card.locator(".count")).to_have_text("Tour · 4 of 9")
    pad(15)
    pad(1)
    expect(card).to_be_hidden()
    assert page.evaluate("() => document.body.dataset.page === 'console' && !window.__flame.state.sheet && !document.getElementById('viewConsole').classList.contains('crew-mode')")
    # From Controls; and a dialog opened by hand ends the tour instead of covering it.
    loc("#guideBtn").click()
    loc("#guideTour").click()
    expect(loc("#controlGuide")).to_be_hidden()
    expect(card.locator(".count")).to_have_text("Tour · 1 of 9")
    loc("#guideBtn").click(force=True)
    expect(loc("#controlGuide")).to_be_visible()
    expect(card).to_be_hidden()
    key("Escape")
    # Escape ends it too, and focus goes back to where it was.
    button.click()
    expect(card).to_be_visible()
    key("Escape")
    expect(card).to_be_hidden()
    expect(button).to_be_focused()


def check_phone(page):
    page.set_viewport_size({"width": 390, "height": 844})
    page.goto(CONSOLE.as_uri())
    loc = page.locator
    expect(loc("#tourBtn")).to_be_visible()
    loc("#tourBtn").click()
    card = loc("#tour")
    for n in range(1, 10):
        expect(card.locator(".count")).to_have_text(f"Tour · {n} of 9")
        page.wait_for_timeout(330)
        assert page.evaluate(TOUR)["inside"], n
        assert page.evaluate("document.documentElement.scrollWidth <= document.documentElement.clientWidth")
        card.locator("button.next").click()
    expect(card).to_be_hidden()
    loc("#tabConsole").click()
    loc("#openAdvisor").scroll_into_view_if_needed()
    loc("#openAdvisor").click()
    expect(loc("#advisor li")).to_have_count(3)
    assert page.evaluate("""() => { const d = document.getElementById('advisor').getBoundingClientRect();
      return d.left >= 0 && d.right <= innerWidth && document.documentElement.scrollWidth <= document.documentElement.clientWidth; }""")
    loc("#advisor li button").first.click()
    assert page.evaluate("() => window.__flame.state.values.o2") == 19
    loc("#tabDrill").click()
    loc("#drillBurn").click()
    expect(loc("#drillLog li")).to_have_count(1)
    assert page.evaluate("document.documentElement.scrollWidth <= document.documentElement.clientWidth")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--channel", help="Installed Chromium channel, e.g. msedge or chrome")
    args = parser.parse_args()
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel=args.channel)
        errors = []
        for check in (check_sizes, check_advisor, check_tour, check_phone):
            context = browser.new_context(viewport={"width": 1280, "height": 800})   # a fresh visitor each time
            page = context.new_page()
            page.on("pageerror", lambda error: errors.append(str(error)))
            if check is check_tour:
                page.add_init_script(GAMEPAD)
            check(page)
            context.close()
        assert not errors, errors
        browser.close()
    print("PASS: text and control sizes at 1280x800, Oxygen map labels, the drill's round log; what would put the flame out "
          "by keyboard, touch and controller with undo; the nine-step tour by keyboard, controller, Controls and phone.")
