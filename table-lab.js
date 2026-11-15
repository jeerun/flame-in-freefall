(function () {
  "use strict";

  const byId = id => document.getElementById(id);
  const tabs = [byId("film-tab"), byId("table-tab")];
  const question = byId("question");
  const ask = byId("ask-question");
  const status = byId("table-status");
  const results = byId("table-results");
  const samples = Array.isArray(window.LAB_TABLE_EXAMPLES) ? window.LAB_TABLE_EXAMPLES : [];
  const gases = { o2: "O₂", co: "CO", co2: "CO₂" };
  const changes = { up: "increased", down: "decreased", same: "unchanged" };
  const pageSize = 4;
  let pending = null;
  let live = false;

  function element(tag, content, className) {
    const node = document.createElement(tag);
    if (content !== undefined) node.textContent = content;
    if (className) node.className = className;
    return node;
  }

  function showTab() {
    const current = location.hash === "#table" ? tabs[1] : tabs[0];
    for (const tab of tabs) {
      const selected = tab === current;
      tab.setAttribute("aria-selected", String(selected));
      tab.tabIndex = selected ? 0 : -1;
      byId(tab.getAttribute("aria-controls")).hidden = !selected;
    }
    if (current === tabs[1]) byId("lab-film").querySelector("video")?.pause();
  }
  function activate(tab) {
    location.hash = tab === tabs[1] ? "table" : "film";
    showTab();
    tab.focus();
  }
  for (const tab of tabs) {
    tab.addEventListener("click", () => activate(tab));
    tab.addEventListener("keydown", event => {
      let next;
      if (event.key === "ArrowLeft" || event.key === "ArrowRight") next = tabs.find(item => item !== tab);
      else if (event.key === "Home") next = tabs[0];
      else if (event.key === "End") next = tabs[1];
      if (next) {
        event.preventDefault();
        activate(next);
      }
    });
  }
  window.addEventListener("hashchange", showTab);
  showTab();

  function returnToConsole() {
    if (document.fullscreenElement) return;
    if (document.activeElement === question) question.blur();
    else window.location.assign(byId("lab-back-link").href);
  }
  document.addEventListener("keydown", event => {
    if (event.key === "Escape" && !event.defaultPrevented && !event.isComposing) returnToConsole();
  });

  function moveFocus(direction) {
    const selector = "a[href], button:not(:disabled), textarea:not(:disabled), video[controls], summary";
    const choices = Array.from(document.querySelectorAll(selector)).filter(node =>
      node.getClientRects().length && node.getAttribute("tabindex") !== "-1");
    if (!choices.length) return;
    const previous = choices.indexOf(document.activeElement);
    const next = previous < 0 ? 0 : (previous + direction + choices.length) % choices.length;
    choices[next].focus();
  }
  function selectFocused() {
    const target = document.activeElement;
    if (target instanceof HTMLVideoElement) {
      if (target.paused) target.play().catch(() => {});
      else target.pause();
    } else if (target === document.body) moveFocus(1);
    else if (target instanceof HTMLElement) target.click();
  }
  let polling = false;
  let lastButtons = [];
  function pollPad() {
    let pad;
    try { pad = Array.from(navigator.getGamepads()).find(Boolean); } catch { /* Gamepad access is optional. */ }
    if (!pad) { polling = false; lastButtons = []; return; }
    const buttons = pad.buttons.map(value => value.pressed);
    const tapped = n => buttons[n] && !lastButtons[n];
    if (!document.hidden) {
      if (tapped(4) || tapped(5)) activate(tabs.find(tab => tab.getAttribute("aria-selected") === "false"));
      else if (tapped(1)) returnToConsole();
      else if (tapped(0)) selectFocused();
      else if (tapped(12) || tapped(14)) moveFocus(-1);
      else if (tapped(13) || tapped(15)) moveFocus(1);
    }
    lastButtons = buttons;
    requestAnimationFrame(pollPad);
  }
  function startPad() {
    if (!polling && typeof navigator.getGamepads === "function") {
      polling = true;
      requestAnimationFrame(pollPad);
    }
  }
  window.addEventListener("gamepadconnected", startPad);
  startPad();

  function rawSource(row) {
    const wrapper = element("div", undefined, "raw-row");
    const raw = element("table");
    raw.append(element("caption", "Original CSV fields · line " + row.line));
    const body = element("tbody");
    for (const [name, value] of row.source) {
      const tr = element("tr");
      const label = element("th", name);
      label.scope = "row";
      tr.append(label, element("td", value === "" ? "(empty cell)" : value));
      body.append(tr);
    }
    raw.append(body);
    wrapper.append(raw);
    return wrapper;
  }

  function rowCard(row) {
    const details = element("details", undefined, "sensor-row");
    const summary = element("summary");
    const top = element("span", undefined, "row-head");
    top.append(element("strong", "Test " + row.id), element("span", "CSV line " + row.line, "row-open"));
    const readings = element("span", undefined, "sensor-grid");
    for (const gas of Object.keys(gases)) {
      const value = element("span", undefined, "reading");
      value.append(element("small", gases[gas] + (gas === "co" ? " (ppm)" : " (% vol)")));
      const pair = row[gas].map(n => n === "" || n == null ? "—" : String(n));
      value.append(element("span", pair.join(" → ")));
      readings.append(value);
    }
    summary.append(top, readings);
    details.append(summary);
    details.addEventListener("toggle", () => {
      if (details.open && !details.querySelector("table")) details.append(rawSource(row));
    });
    return details;
  }

  function renderPage(rows, page, host, focusNavigation) {
    host.replaceChildren();
    const first = page * pageSize;
    for (const row of rows.slice(first, first + pageSize)) host.append(rowCard(row));
    if (rows.length <= pageSize) return;
    const nav = element("nav", undefined, "result-pages");
    nav.setAttribute("aria-label", "Result pages");
    const previous = element("button", "Previous", "lab-btn");
    const next = element("button", "Next", "lab-btn");
    previous.type = next.type = "button";
    previous.disabled = first === 0;
    next.disabled = first + pageSize >= rows.length;
    previous.addEventListener("click", () => renderPage(rows, page - 1, host, "previous"));
    next.addEventListener("click", () => renderPage(rows, page + 1, host, "next"));
    nav.append(previous, element("span", (first + 1) + "–" + Math.min(first + pageSize, rows.length) + " of " + rows.length), next);
    host.append(nav);
    if (focusNavigation) {
      const preferred = focusNavigation === "previous" ? previous : next;
      (preferred.disabled ? (preferred === previous ? next : previous) : preferred).focus();
    }
  }

  function display(query, result) {
    results.replaceChildren();
    if (result?.status === "unsupported") {
      status.textContent = "This question could not be matched to a test ID or a supported gas change. Try one of the examples.";
      return;
    }
    if (result?.status === "unavailable") {
      status.textContent = "The local Ember model is unavailable. Choose a bundled question or try again when the model is running.";
      return;
    }
    if (result?.status !== "ok" || !Array.isArray(result.rows) || !Array.isArray(result.filters)) {
      throw new Error("The table server returned an unreadable result. Try a bundled question.");
    }
    status.textContent = result.matched + (result.matched === 1 ? " matching record" : " matching records") +
      " in the BASS-II table.";
    results.append(element("h3", query, "result-question"));
    const terms = result.filters.map(filter => gases[filter.gas] + " " + changes[filter.change]);
    if (result.test_id) terms.unshift("Test " + result.test_id);
    if (terms.length) results.append(element("p", "Filter applied · " + terms.join(" and "), "filter-note"));
    if (result.excluded) results.append(element("p", result.excluded +
      (result.excluded === 1 ? " record lacks" : " records lack") +
      " two exact readings for a requested comparison.", "lab-subtle"));
    if (result.rows.length) {
      results.append(element("p", "Initial → final. Select a test to inspect the original CSV fields.", "lab-subtle"));
      const list = element("div");
      results.append(list);
      renderPage(result.rows, 0, list);
    }
  }

  function highlight(index) {
    Array.from(byId("example-questions").children).forEach((button, i) =>
      button.setAttribute("aria-pressed", String(index === i)));
  }
  function cancelPending() {
    if (pending) pending.abort();
    pending = null;
    results.removeAttribute("aria-busy");
    ask.disabled = !live;
  }
  function focusPhoneResults() {
    if (window.matchMedia("(max-width: 760px)").matches) byId("result-heading").focus();
  }
  function showSample(index, userInitiated = true) {
    cancelPending();
    const sample = samples[index];
    question.value = sample.question;
    highlight(index);
    display(sample.question, sample.result);
    if (userInitiated) focusPhoneResults();
  }
  samples.forEach((sample, index) => {
    const button = element("button", sample.question, "question-sample");
    button.type = "button";
    const arrow = element("span", "↗");
    arrow.setAttribute("aria-hidden", "true");
    button.append(arrow);
    button.addEventListener("click", () => showSample(index));
    byId("example-questions").append(button);
  });
  if (samples.length) showSample(0, false);
  else status.textContent = "No bundled results were loaded.";
  question.addEventListener("input", () => {
    highlight(-1);
    if (pending) {
      cancelPending();
      status.textContent = "Question changed. Search again to see matching records.";
    }
  });
  question.addEventListener("keydown", event => {
    if (event.key === "Enter" && !event.shiftKey && !event.isComposing) {
      event.preventDefault();
      byId("question-form").requestSubmit();
    }
  });

  async function submit(event) {
    event.preventDefault();
    const query = question.value.trim();
    if (!query) { question.focus(); return; }
    const example = samples.findIndex(sample => sample.question.toLowerCase() === query.toLowerCase());
    if (example !== -1) { showSample(example); return; }
    if (!live) return;
    cancelPending();
    highlight(-1);
    const request = new AbortController();
    pending = request;
    const timeout = setTimeout(() => request.abort(), 90000);
    results.replaceChildren();
    results.setAttribute("aria-busy", "true");
    status.textContent = "Looking up the question in the BASS-II table…";
    focusPhoneResults();
    ask.disabled = true;
    try {
      const response = await fetch("/lab/table", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: query }), signal: request.signal, mode: "same-origin", redirect: "error"
      });
      const result = await response.json();
      if (pending !== request) return;
      if (!response.ok) throw new Error(typeof result.error === "string" ? result.error : "Table search is unavailable. Try a bundled question.");
      display(query, result);
    } catch (error) {
      if (pending === request) {
        status.textContent = error.name === "AbortError" ? "Table search timed out. Try again or choose a bundled question." :
          error.name === "TypeError" || error.name === "SyntaxError" ? "The local dashboard could not answer. Try a bundled question." : error.message;
      }
    } finally {
      clearTimeout(timeout);
      if (pending === request) {
        pending = null;
        results.removeAttribute("aria-busy");
        ask.disabled = !live;
      }
    }
  }
  byId("question-form").addEventListener("submit", submit);

  async function checkServer() {
    const mode = byId("question-mode");
    mode.textContent = "Bundled questions work offline. Start the local dashboard to enter your own.";
    if (!/^https?:$/.test(location.protocol) || /(^|\.)github\.io$/i.test(location.hostname)) return;
    const probe = new AbortController();
    const timeout = setTimeout(() => probe.abort(), 4000);
    try {
      const response = await fetch("/lab/status", { signal: probe.signal, mode: "same-origin", redirect: "error", cache: "no-store" });
      if (!response.ok) return;
      const capabilities = await response.json();
      document.dispatchEvent(new CustomEvent("lab-capabilities", { detail: capabilities }));
      if (capabilities.table !== true) return;
      live = true;
      ask.disabled = question.disabled = false;
      byId("question-entry").hidden = false;
      mode.textContent = "Enter an English question. The local dashboard filters the source CSV.";
    } catch { /* Other static hosts retain the offline examples. */ }
    finally { clearTimeout(timeout); }
  }
  checkServer();
})();
