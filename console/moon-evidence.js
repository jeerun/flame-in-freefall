(() => {
  "use strict";
  const data = window.FLAME_MOON_EVIDENCE;
  const byId = id => document.getElementById(id);
  if (!data || !data.matches.length) {
    byId("reason").textContent = "The bundled evidence could not be loaded. Reopen this page with its data file.";
    return;
  }

  const matches = data.matches.length;
  const sources = [...new Set(data.matches.map(row => data.tables[row.table]))];
  const first = sources[0];
  const solidMatches = data.matches.filter(row => data.tables[row.table].material === "Solid materials").length;
  const limits = data.thresholds;
  const claim = byId("stageTitle").textContent;
  const graphic = byId("graphic");
  let stage = 0;
  let predictedYes = false;

  function el(tag, text) {
    const node = document.createElement(tag);
    node.textContent = text;
    return node;
  }
  function action(label, nextStage, primary = false) {
    const button = el("button", label);
    button.type = "button";
    button.classList.toggle("next", primary);
    button.addEventListener("click", () => {
      if (stage === 0) predictedYes = label === "Yes, the air matches";
      show(nextStage);
    });
    byId("actions").append(button);
  }
  function marks(className, total, highlighted) {
    const box = document.createElement("div");
    box.className = className;
    box.setAttribute("aria-hidden", "true");
    for (let i = 0; i < total; i++) {
      const mark = document.createElement("i");
      if (i < highlighted) mark.className = "match";
      box.append(mark);
    }
    graphic.append(box);
  }
  function measurements() {
    const list = document.createElement("dl");
    list.className = "observations";
    const observations = [
      ["Cabin air thresholds", matches + " matching rows"],
      ["Solid specimens in those rows", String(solidMatches)],
      ["Lunar gravity in those rows", "Unverified"]
    ];
    for (const [field, value] of observations) {
      const item = document.createElement("div");
      item.append(el("dt", field), el("dd", value));
      list.append(item);
    }
    graphic.append(list);
  }
  function plot(title, value, note) {
    byId("plotTitle").textContent = title;
    byId("reading").textContent = value;
    byId("plotNote").textContent = note;
  }

  function show(step, focus = true) {
    stage = step;
    byId("actions").replaceChildren();
    graphic.replaceChildren();
    byId("sourceDetails").open = false;
    byId("sourceDetails").hidden = stage === 0;
    [...byId("trail").children].forEach((item, i) => {
      item.classList.toggle("passed", i + 1 < stage);
      if (i + 1 === stage) item.setAttribute("aria-current", "step");
      else item.removeAttribute("aria-current");
    });
    const title = byId("stageTitle");
    const reason = byId("reason");
    if (stage === 0) {
      byId("stageLabel").textContent = "Your call";
      title.textContent = claim;
      reason.textContent = "The challenge specifies at least " + limits.oxygenPct + "% oxygen and at most " + limits.pressurePsi + " psi. Make a call, then follow the measurements.";
      plot("Rows with ambient oxygen and pressure", data.eligible,
        "Each mark is one published table row. Some source rows repeat.");
      marks("matrix", data.eligible, 0);
      action("Yes, the air matches", 1);
      action("We need more evidence", 1);
    } else if (stage === 1) {
      byId("stageLabel").textContent = "Check 1 of 3 · Atmosphere";
      title.textContent = "The atmosphere matches";
      reason.textContent = (predictedYes ? "You spotted the air match. " : "Your caution is worth testing. ") +
        matches + " of " + data.eligible + " rows meet both limits. That tells us the oxygen and pressure in those tests. What actually burned?";
      plot("Rows meeting both cabin air thresholds", matches + " / " + data.eligible,
        matches + " highlighted rows meet both limits, grouped together so you can count them.");
      marks("matrix", data.eligible, matches);
      action("Check the specimen", 2, true);
    } else if (stage === 2) {
      const example = data.matches[0];
      byId("stageLabel").textContent = "Check 2 of 3 · Specimen";
      title.textContent = "All the matches are gas flames";
      reason.textContent = "Every matching row comes from the CFI-G normal-flame table. The solid-material tables in this collection lack a comparable chamber-pressure field.";
      plot("Gas-flame rows among the atmosphere matches", matches + " / " + matches,
        "Test " + example.test + " used " + example.fuel + " in " + example.oxygenPct +
        "% oxygen at approximately " + example.pressurePsi.toFixed(2) + " psi.");
      marks("specimens", matches, matches);
      action("Check gravity", 3, true);
      action("Previous", 1);
    } else {
      byId("stageLabel").textContent = "Check 3 of 3 · Gravity";
      title.textContent = "The lunar panel is still an open question";
      reason.textContent = "The matching table has no gravity measurement for individual rows. To answer the crew’s question, we need observations of a comparable solid at lunar gravity under the specified cabin air.";
      plot("What the matching rows establish", "", "A missing gravity measurement leaves the lunar comparison open.");
      measurements();
      action("Try again", 0, true);
      action("Previous", 2);
    }
    byId("reading").hidden = !byId("reading").textContent;
    if (focus) title.focus();
  }

  // Pin citations to the source snapshot that supplied the bundled CSVs.
  const snapshot = "https://github.com/jeerun/flame-in-freefall/blob/dd72ee287b1cfebc28253f00956d6106b9704145/data/raw/psi_tables/";
  const body = byId("sourceRows").tBodies[0];
  for (const row of data.matches) {
    const record = body.insertRow();
    for (const value of [row.test, row.fuel, row.oxygenRaw, row.pressureRaw]) {
      record.insertCell().textContent = value;
    }
    const link = el("a", String(row.line));
    link.href = snapshot + encodeURIComponent(data.tables[row.table].file) + "?plain=1#L" + row.line;
    link.target = "_blank";
    link.rel = "noopener noreferrer";
    link.setAttribute("aria-label", "Original CSV line " + row.line + " for test " + row.test);
    record.insertCell().append(link);
  }
  byId("sourceNote").textContent = first.id + " · " + first.name + ". Oxygen is recorded as a fraction and pressure in bar. The filter compares the converted values before rounding.";
  byId("nasaRecord").href = "https://doi.org/" + first.doi;
  show(0, false);

  // Only the focused document responds. Require release after each input.
  let previous = [];
  function poll() {
    const pad = document.hasFocus() && navigator.getGamepads &&
      Array.from(navigator.getGamepads()).find(p => p && p.connected);
    if (pad) {
      const active = [0, 1, 12, 13, 14, 15].map(i => Boolean(pad.buttons[i] && pad.buttons[i].pressed));
      const pressed = index => active[index] && !previous[index];
      if (!active.some((down, i) => down && !previous[i])) {
        previous = active;
        requestAnimationFrame(poll);
        return;
      }
      const controls = [...document.querySelectorAll("button, summary, a[href]")].filter(node => node.getClientRects().length);
      const index = controls.indexOf(document.activeElement);
      if (pressed(0)) {
        if (index >= 0) controls[index].click();
        else byId("actions").firstElementChild.focus();
      } else if (pressed(1)) {
        if (byId("sourceDetails").open) {
          byId("sourceDetails").open = false;
          byId("sourceDetails").querySelector("summary").focus();
        } else if (stage > 0) show(stage - 1);
        else byId("backLink").click();
      } else if (pressed(2) || pressed(3) || pressed(4) || pressed(5)) {
        const direction = pressed(2) || pressed(4) ? -1 : 1;
        if (index < 0) byId("actions").firstElementChild.focus();
        else controls[(index + direction + controls.length) % controls.length].focus();
      }
      previous = active;
    } else previous = [];
    requestAnimationFrame(poll);
  }
  // Some static hosts or embedded previews disable the Gamepad API.
  try {
    if (navigator.getGamepads) { navigator.getGamepads(); requestAnimationFrame(poll); }
  } catch { /* Keyboard and pointer controls remain available. */ }
})();
