/* A one-minute tour: a card that walks through the three pages, one highlighted part at a time.
   It opens no dialog and changes no setting; it only turns pages and opens the research tools strip. */
(function () {
  "use strict";

  let card, ring, countEl, titleEl, textEl, dotsEl, backButton, nextButton, endButton;
  let api = null, steps = [], index = -1, startPage = null, returnFocus = null, watcher = null, toolsWereOpen = null;

  function element(tag, text, className) {
    const node = document.createElement(tag);
    if (text != null) node.textContent = text;
    if (className) node.className = className;
    return node;
  }
  function shown(node) { return !!node && !node.closest("[hidden]") && node.getClientRects().length > 0; }

  // Each step: the page it is on, what it points at (the first of these that is on screen), and what it says.
  function makeSteps(options) {
    const tools = () => document.getElementById("researchTools");
    const all = [
      { page: "research", targets: ["#orbit", "#rank"], title: "NASA's fire research at a glance",
        text: () => options.investigations + " microgravity combustion investigations from NASA's PSI archive. "
          + (shown(document.getElementById("orbit")) ? "Each mark is one investigation: the closer to the centre, the higher its AI-rated relevance to the safety topic."
            : "Each row is one investigation, ranked by its AI-rated relevance to the safety topic.") },
      { page: "research", targets: ["#needs"], title: "Ask a safety question",
        text: () => "Prevention, detection, suppression or cabin air: the ranking changes with the topic. Left and right switch topic, up and down pick an investigation." },
      { page: "research", targets: [".research-detail"], title: "What one investigation found",
        text: () => "A plain summary of the NASA record, written by AI and labelled as such. NASA source opens the record itself." },
      { page: "research", targets: ["#researchTools"], title: "Dig into the data",
        enter: () => { if (tools()) { toolsWereOpen = tools().open; tools().open = true; } },
        leave: () => { if (tools() && toolsWereOpen === false) tools().open = false; toolsWereOpen = null; },
        text: () => "These tools set NASA's table rows against Moon Base air, compare burn lengths and gas readings, show NASA footage, and check a claim about a lunar cabin." },
      { page: "console", targets: ["#consoleSettings"], title: "Set up a flame",
        text: () => "Choose the fuel and the cabin air. X switches between Earth, Moon and Mars air; the arrows or the D-pad change one setting at a time." },
      { page: "console", targets: ["#read > .stage", "#conf"], union: true, title: "The reading, and how far to trust it",
        text: () => "The model's chance that the droplet burns all its fuel" + (options.tests ? ", learned from " + options.tests + " real FLEX tests" : "")
          + ". The coloured box says whether real tests sit near these settings, and warns when none do." },
      { page: "console", targets: ["#read > .line"], title: "Why, and what would put it out",
        text: () => "Explain reading gives the reasons and the nearest real tests." + (shown(document.getElementById("openAdvisor"))
          ? " Put it out shows how far oxygen, carbon dioxide or helium must change before the model expects the flame to go out." : "") },
      { page: "drill", targets: [".drill-round"], title: "Test yourself",
        text: () => "Ten real FLEX tests. Say whether each flame went out or burned all its fuel, then see what NASA recorded and whether you beat the model." },
      { page: null, targets: ["#guideBtn"], title: "Every button, any time",
        text: () => "Controls lists the buttons for the page you are on. Ask Ember appears beside it when a computer running the language model is linked." }
    ];
    return all.filter(step => step.page === null || options.pages.indexOf(step.page) >= 0);
  }

  function build() {
    const style = element("style");
    style.textContent = `
      #tourRing { position:fixed; z-index:60; pointer-events:none; border:2px solid #ffb184; border-radius:12px;
        box-shadow:0 0 0 200vmax rgb(6 10 11 / 60%); transition:left .26s ease, top .26s ease, width .26s ease, height .26s ease; }
      #tour { position:fixed; z-index:61; width:min(27rem, calc(100vw - 24px)); padding:.9rem 1rem .8rem;
        background:#202421; color:#f2f0e6; border:1px solid #6b7568; border-radius:.9rem; box-shadow:0 1rem 3.5rem #000b;
        font-variant-numeric:tabular-nums; transition:left .26s ease, top .26s ease; }
      #tour * { box-sizing:border-box; }
      #tour .count { color:#82d9c4; font-size:max(12px,.78rem); font-weight:650; letter-spacing:.045em; }
      #tour h2 { margin:.15rem 0 .35rem; color:#f2f0e6; font-size:clamp(1.15rem,2.2vw,1.4rem); line-height:1.15; letter-spacing:-.02em; font-weight:650; }
      #tour p { margin:0; font-size:1rem; line-height:1.42; color:#e3e6dc; }
      #tour .row { display:flex; align-items:center; gap:.5rem; margin-top:.7rem; }
      #tour .dots { display:flex; gap:5px; margin-right:auto; }
      #tour .dots i { width:7px; height:7px; border-radius:50%; background:#515a50; }
      #tour .dots i.on { background:#ffb184; }
      #tour button { display:inline-flex; align-items:center; gap:.35rem; padding:.3rem .8rem; min-height:max(44px,2.5rem);
        border:1px solid #535d52; border-radius:.48rem; background:transparent; color:#d5dcd0; font:inherit; font-size:.93rem; cursor:pointer; white-space:nowrap; }
      #tour button.next { background:#82d9c4; color:#132820; border-color:#82d9c4; font-weight:700; }
      #tour button[disabled] { opacity:.4; cursor:default; }
      #tour kbd { display:inline-grid; place-items:center; min-width:1.3rem; height:1.3rem; padding:0 .25rem; border:1px solid currentColor;
        border-radius:999px; background:transparent; color:inherit; font:600 max(12px,.72rem)/1 ui-monospace,Consolas,monospace; opacity:.8; }
      #tour button:hover:not([disabled]) { filter:brightness(1.15); }
      #tour :focus-visible { outline:2px solid #d5f9eb; outline-offset:3px; }
      @media (prefers-reduced-motion: reduce) { #tourRing, #tour { transition:none; } }
    `;
    document.head.append(style);
    ring = element("div"); ring.id = "tourRing"; ring.setAttribute("aria-hidden", "true");
    card = element("div"); card.id = "tour";
    card.setAttribute("role", "dialog"); card.setAttribute("aria-labelledby", "tourTitle"); card.setAttribute("aria-describedby", "tourText");
    countEl = element("div", null, "count");
    titleEl = element("h2"); titleEl.id = "tourTitle";
    textEl = element("p"); textEl.id = "tourText"; textEl.setAttribute("aria-live", "polite");
    const row = element("div", null, "row");
    dotsEl = element("span", null, "dots"); dotsEl.setAttribute("aria-hidden", "true");
    endButton = element("button"); endButton.type = "button"; endButton.append(element("kbd", "B"), "End");
    backButton = element("button", "Back"); backButton.type = "button";
    nextButton = element("button", null, "next"); nextButton.type = "button";
    endButton.addEventListener("click", () => close(false));
    backButton.addEventListener("click", () => go(index - 1));
    nextButton.addEventListener("click", () => { if (index >= steps.length - 1) close(true); else go(index + 1); });
    row.append(dotsEl, endButton, backButton, nextButton);
    card.append(countEl, titleEl, textEl, row);
    document.body.append(ring, card);
  }

  function targetBox(step) {
    const nodes = step.targets.map(selector => document.querySelector(selector)).filter(shown);
    if (!nodes.length) return null;
    const boxes = (step.union ? nodes : nodes.slice(0, 1)).map(node => node.getBoundingClientRect());
    const left = Math.min(...boxes.map(b => b.left)), top = Math.min(...boxes.map(b => b.top));
    return { node: nodes[0], left, top, right: Math.max(...boxes.map(b => b.right)), bottom: Math.max(...boxes.map(b => b.bottom)) };
  }

  function place() {
    if (!isOpen()) return;
    const step = steps[index], margin = 12, gap = 14, vw = window.innerWidth, vh = window.innerHeight;
    let box = targetBox(step);
    if (box && (box.top < 0 || box.bottom > vh) && box.bottom - box.top < vh) {     // a long page on a phone: bring the part into view
      box.node.scrollIntoView({ block: "center" });
      box = targetBox(step);
    }
    const cw = card.offsetWidth, ch = card.offsetHeight;
    if (!box) {                                                                   // nothing to point at: the card alone, centred
      ring.style.display = "none";
      card.style.left = Math.max(margin, (vw - cw) / 2) + "px"; card.style.top = Math.max(margin, (vh - ch) / 2) + "px";
      return;
    }
    const pad = 6, l = Math.max(4, box.left - pad), t = Math.max(4, box.top - pad);
    const r = Math.min(vw - 4, box.right + pad), b = Math.min(vh - 4, box.bottom + pad);
    ring.style.display = "";
    ring.style.left = l + "px"; ring.style.top = t + "px"; ring.style.width = (r - l) + "px"; ring.style.height = (b - t) + "px";
    const cx = (l + r) / 2, cy = (t + b) / 2;
    let x, y;
    if (b + gap + ch <= vh - margin) { x = cx - cw / 2; y = b + gap; }                 // below
    else if (t - gap - ch >= margin) { x = cx - cw / 2; y = t - gap - ch; }            // above
    else if (r + gap + cw <= vw - margin) { x = r + gap; y = cy - ch / 2; }            // to the right
    else if (l - gap - cw >= margin) { x = l - gap - cw; y = cy - ch / 2; }            // to the left
    else { x = vw - cw - margin; y = vh - ch - margin; }                              // no free side: the lower right corner
    card.style.left = Math.min(vw - cw - margin, Math.max(margin, x)) + "px";
    card.style.top = Math.min(vh - ch - margin, Math.max(margin, y)) + "px";
  }

  function go(next) {
    if (next < 0 || next >= steps.length) return;
    const previous = steps[index];
    if (previous && previous.leave) previous.leave();
    index = next;
    const step = steps[index];
    if (step.page && api.page() !== step.page) api.goPage(step.page);
    if (step.enter) step.enter();
    countEl.textContent = "Tour · " + (index + 1) + " of " + steps.length;
    titleEl.textContent = step.title;
    textEl.textContent = step.text();
    dotsEl.replaceChildren(...steps.map((_, i) => element("i", null, i === index ? "on" : "")));
    backButton.disabled = index === 0;
    nextButton.replaceChildren(element("kbd", "A"), index === steps.length - 1 ? "Finish" : "Next");
    place();
    requestAnimationFrame(place);                  // once more after the page has laid itself out
    nextButton.focus({ preventScroll: true });
  }

  // options: { pages, page(), goPage(name), investigations, tests, ended(finished) }
  function start(options) {
    if (isOpen()) return;
    if (!card) build();
    api = options;
    steps = makeSteps(options);
    if (!steps.length) return;
    startPage = options.page();
    returnFocus = document.activeElement;
    card.hidden = ring.hidden = false;
    index = -1;
    window.addEventListener("resize", place);
    window.addEventListener("scroll", place, true);
    // A dialog opened by hand takes over the screen: the tour steps aside instead of hiding behind it.
    watcher = new MutationObserver(() => { if (document.querySelector("dialog[open]")) close(false); });
    watcher.observe(document.body, { subtree: true, attributes: true, attributeFilter: ["open"] });
    go(0);
  }
  function isOpen() { return !!card && !card.hidden && index >= 0; }
  function close(finished) {
    if (!isOpen()) return;
    const step = steps[index];
    if (step && step.leave) step.leave();
    index = -1;
    card.hidden = ring.hidden = true;
    window.removeEventListener("resize", place);
    window.removeEventListener("scroll", place, true);
    if (watcher) { watcher.disconnect(); watcher = null; }
    if (finished && startPage && api.page() !== startPage) api.goPage(startPage);
    if (returnFocus && returnFocus.isConnected && !document.querySelector("dialog[open]")) returnFocus.focus({ preventScroll: true });
    returnFocus = null;
    if (api.ended) api.ended(!!finished);
  }
  function handle(action) {
    if (!isOpen()) return false;
    if (action === "back") close(false);
    else if (action === "left") go(index - 1);
    else if (action === "right") nextButton.click();
    else if (action === "confirm") {
      const focused = document.activeElement;
      if (card.contains(focused) && focused.matches("button:not([disabled])")) focused.click(); else nextButton.click();
    }
    return true;                                   // up and down do nothing, and nothing else reaches the page
  }

  window.FLAME_TOUR = { start, isOpen, handle, close, step: () => index };
})();
