// Two offline readings of NASA's experimental tables. The page routes keyboard and gamepad actions here.
(function () {
  "use strict";
  const modes = {
    gravity: {title: "Earth or orbit?", study: "SAFFIRE-II", unit: "Sample",
      question: "Where did this material burn farther?", choices: ["Earth", "Same extent", "Orbit"]},
    sensors: {title: "Read the gas sensors", study: "BASS-II", unit: "Test",
      question: "How did carbon monoxide change during this test?", choices: ["It rose", "It held steady", "It fell"]}
  };
  let dialog, mode, index, choice, revealed, returnFocus;
  const find = id => dialog.querySelector("#ev-" + id);
  const current = () => window.FLAME_EVIDENCE_DATA[mode].cases[index];

  function install() {
    const style = document.createElement("style");
    style.textContent = `
      #ev-dialog {
        --ev-paper:#202421; --ev-ink:#f2f0e6; --ev-muted:#b4bcb2; --ev-line:#464e45;
        --ev-teal:#82d9c4; --ev-fire:#ffac72; --ev-button:#303730;
        color-scheme:dark; width:min(54rem,calc(100% - 1.25rem)); max-height:calc(100dvh - 1.25rem);
        margin:auto; padding:0; overflow:auto; overscroll-behavior:contain; color:var(--ev-ink);
        border:1px solid var(--ev-line); border-radius:1rem; background:var(--ev-paper);
        font:inherit; font-variant-numeric:tabular-nums; box-shadow:0 1.25rem 5rem #09110e99;
        scrollbar-color:#646d60 var(--ev-paper);
      }
      #ev-dialog::backdrop { background:rgb(12 15 12 / 82%); }
      #ev-dialog * { box-sizing:border-box; }
      #ev-dialog :focus-visible { outline:2px solid #d5f9eb; outline-offset:3px; }
      .ev-head, .ev-nav, .ev-controls, .ev-choices, .ev-group, .ev-keys { display:flex; align-items:center; }
      .ev-head { justify-content:space-between; gap:.8rem; padding:.95rem 1.35rem; border-bottom:1px solid var(--ev-line); }
      .ev-id, .ev-source, .ev-sub { color:var(--ev-muted); font-size:.86rem; }
      .ev-id { color:var(--ev-teal); font-size:.78rem; font-weight:650; letter-spacing:.045em; }
      #ev-dialog h2 { margin:.22rem 0 0; font-size:clamp(1.55rem,3vw,2rem); letter-spacing:-.025em; font-weight:650; line-height:1.15; color:var(--ev-ink); }
      #ev-dialog button { border:1px solid var(--ev-line); background:var(--ev-button); color:var(--ev-ink);
        border-radius:.48rem; min-height:max(44px,2.55rem); padding:.35rem .8rem; cursor:pointer; font:inherit; font-size:.95rem; }
      #ev-dialog button:hover { border-color:var(--ev-teal); background:#3b453d; }
      #ev-dialog .ev-close { flex:none; background:transparent; color:var(--ev-muted); }
      .ev-pad { padding:1rem 1.35rem .8rem; }
      .ev-nav { justify-content:space-between; gap:.8rem; }
      #ev-material { margin:0; font-size:1.13rem; font-weight:650; line-height:1.24; }
      .ev-sub { margin:.2rem 0 0; line-height:1.32; }
      .ev-group { flex-shrink:0; gap:.4rem; }
      #ev-count { color:var(--ev-muted); font-size:.84rem; }
      #ev-dialog .ev-arrow { min-width:max(44px,2.6rem); font-size:1.25rem; padding:.15rem .45rem; }
      .ev-measures { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:.7rem; margin:.85rem 0 .8rem; }
      .ev-measure { --accent:var(--ev-teal); min-width:0; border:1px solid var(--ev-line); border-radius:.7rem;
        background:linear-gradient(120deg,#2c352e,#262b25); padding:.78rem 1rem; }
      .ev-measure:nth-child(2) { --accent:var(--ev-fire); background:linear-gradient(120deg,#383027,#292a24); }
      .ev-measure:nth-child(3) { --accent:#c6d0ad; background:linear-gradient(120deg,#33362c,#292c25); }
      .ev-type { font-size:.86rem; color:var(--accent); font-weight:650; }
      .ev-value { color:var(--ev-ink); font-weight:650; font-size:clamp(1.28rem,2.8vw,2.2rem);
        line-height:1.05; letter-spacing:-.035em; margin:.55rem 0 .4rem; }
      .ev-measure[data-covered] .ev-value { color:var(--ev-muted); }
      .ev-note { color:var(--ev-muted); font-size:.8rem; }
      .ev-track { background:#3a4037; height:.55rem; border-radius:3px; overflow:hidden; }
      .ev-fill { height:100%; background:var(--accent); }
      .ev-track.covered { background:repeating-linear-gradient(120deg,#45463b 0 4px,#30352e 4px 9px); }
      .ev-scale { display:flex; justify-content:space-between; margin-top:.28rem; color:var(--ev-muted); font-size:.73rem; }
      #ev-dialog[data-mode="sensors"] .ev-measures { grid-template-columns:repeat(3,minmax(0,1fr)); }
      .ev-prompt { font-size:1.03rem; font-weight:650; margin:.6rem 0 .42rem; }
      .ev-controls { align-items:flex-end; justify-content:space-between; flex-wrap:wrap; gap:.55rem; }
      .ev-choices { flex-wrap:wrap; gap:.3rem; }
      #ev-dialog button[aria-pressed="true"] { border-color:var(--ev-teal); background:#304d42; color:#e4fff5; }
      #ev-dialog #ev-action { background:var(--ev-teal); border-color:var(--ev-teal); color:#132820; font-weight:700; padding-inline:1rem; }
      #ev-dialog #ev-action:hover { background:#a0e6d2; }
      #ev-result { color:var(--ev-ink); font-weight:600; margin:0; font-size:1.02rem; line-height:1.38; }
      .ev-readout { min-width:0; flex:1; }
      .ev-source { margin:.8rem 0 0; font-size:.78rem; overflow-wrap:anywhere; line-height:1.45; }
      .ev-source a { color:var(--ev-teal); text-decoration:underline; text-underline-offset:.14em; }
      .ev-keys { flex-wrap:wrap; gap:.2rem .95rem; margin:0; padding:.52rem 1.35rem; border-top:1px solid var(--ev-line); color:var(--ev-muted); font-size:.77rem; }
      .ev-keys b { color:var(--ev-ink); font-weight:600; }
      @media (max-width:42rem) {
        .ev-head,.ev-pad,.ev-keys { padding-inline:.85rem; }
        .ev-nav { gap:.4rem; } .ev-group { gap:.25rem; }
        .ev-measures { gap:.42rem; } .ev-measure { padding:.65rem; }
        #ev-dialog[data-mode="sensors"] .ev-measures { grid-template-columns:1fr; gap:.35rem; }
        #ev-dialog[data-mode="sensors"] .ev-measure { display:grid; grid-template-columns:minmax(0,1fr) minmax(0,1.05fr); align-items:center; row-gap:.1rem; }
        #ev-dialog[data-mode="sensors"] .ev-value { margin:0; text-align:right; }
        #ev-dialog[data-mode="sensors"] .ev-note { grid-column:2; text-align:right; }
      }
      @media (max-width:32rem) {
        .ev-nav { align-items:flex-start; }
        .ev-readout { flex-basis:100%; }
        #ev-dialog #ev-action { width:100%; }
        .ev-keys { gap:.2rem .6rem; }
      }
      @media (max-height:31rem) {
        .ev-pad,.ev-head { padding-top:.48rem; padding-bottom:.48rem; }
        .ev-measures { margin:.42rem 0; } .ev-measure { padding:.48rem .7rem; } .ev-source { margin-top:.4rem; }
      }
    `;
    document.head.appendChild(style);
    dialog = document.createElement("dialog");
    dialog.id = "ev-dialog";
    dialog.setAttribute("aria-labelledby", "ev-title");
    dialog.innerHTML = `
      <header class="ev-head"><div><div class="ev-id" id="ev-id"></div><h2 id="ev-title"></h2></div>
        <button type="button" class="ev-close" data-control="back">Close</button></header>
      <div class="ev-pad"><div class="ev-nav"><div><h3 id="ev-material"></h3><p class="ev-sub" id="ev-conditions"></p></div>
        <div class="ev-group"><button type="button" class="ev-arrow" data-control="up" aria-label="Previous case">‹</button>
        <span id="ev-count"></span><button type="button" class="ev-arrow" data-control="down" aria-label="Next case">›</button></div></div>
        <div class="ev-measures" id="ev-measures"></div>
        <div class="ev-controls"><div class="ev-readout"><p class="ev-prompt" id="ev-prompt"></p><div class="ev-choices" id="ev-choices" role="group" aria-labelledby="ev-prompt">
          <button type="button" data-choice="0"></button><button type="button" data-choice="1"></button><button type="button" data-choice="2"></button>
          </div><p id="ev-result" aria-live="polite"></p></div><button type="button" id="ev-action" data-control="confirm"></button></div>
        <p class="ev-source" id="ev-source"><span id="ev-source-row"></span> · <a id="ev-doi" target="_blank" rel="noopener noreferrer"></a></p>
      </div><p class="ev-keys"><span><b>↑ ↓</b> Change case</span><span><b>← →</b> Choose</span><span><b>A / Enter</b> Reveal or advance</span><span><b>B / Esc</b> Close</span></p>
    `;
    document.body.appendChild(dialog);
    dialog.addEventListener("click", function (event) {
      const button = event.target.closest("button");
      if (!button || !dialog.contains(button)) return;
      if (button.hasAttribute("data-choice")) {
        if (!revealed) {
          choice = Number(button.dataset.choice);
          render();
          find("action").focus({preventScroll:true});
        }
      } else {
        handle(button.dataset.control);
      }
    });
    dialog.addEventListener("keydown", function (event) {
      // Tab reaches every native button. Its Enter activation should keep that button's meaning.
      if ((event.key === "Enter" || event.key === " ") && event.target.matches("button, a[href]")
          && event.target !== find("action")) event.stopPropagation();
    });
    dialog.addEventListener("cancel", function (event) { event.preventDefault(); close(); });
  }

  function measure(title, value, note) {
    const panel = document.createElement("div");
    panel.className = "ev-measure";
    [["ev-type", title], ["ev-value", value], ["ev-note", note]].forEach(function (entry) {
      if (entry[1]) {
        const line = document.createElement("div");
        line.className = entry[0];
        line.textContent = entry[1];
        panel.appendChild(line);
      }
    });
    find("measures").appendChild(panel);
    return panel;
  }

  function lengthCm(value, sampleLength) {
    if (value === "Complete") return parseFloat(sampleLength);
    if (value === "~ 0") return 0;
    return parseFloat(value);
  }

  function burnStrip(label, value, length, hidden) {
    const recorded = value === "~ 0" ? "≈ 0 cm" : value;
    const panel = measure(label, hidden ? "?" : recorded, "");
    panel.toggleAttribute("data-covered", hidden);
    const track = document.createElement("div");
    track.setAttribute("aria-hidden", "true");
    track.className = "ev-track" + (hidden ? " covered" : "");
    if (!hidden) {
      const bar = document.createElement("div");
      bar.className = "ev-fill";
      bar.style.width = (100 * lengthCm(value, length) / parseFloat(length)) + "%";
      track.appendChild(bar);
    }
    const scale = document.createElement("div");
    scale.className = "ev-scale";
    const start = document.createElement("span"), end = document.createElement("span");
    start.textContent = "0 cm"; end.textContent = length;
    scale.append(start, end);
    panel.append(track, scale);
  }

  function sensor(label, values, unit, hidden) {
    const panel = measure(label, hidden ? "?" : values.join(" → "), unit + " · before → after");
    panel.toggleAttribute("data-covered", hidden);
  }

  function render() {
    const pack = window.FLAME_EVIDENCE_DATA[mode], row = current(), info = modes[mode];
    dialog.dataset.mode = mode;
    find("id").textContent = info.study + " · " + info.unit + " " + row.id;
    find("title").textContent = info.title;
    find("count").textContent = (index + 1) + " / " + pack.cases.length;
    find("material").textContent = row.material;
    find("measures").replaceChildren();
    let answer, reading;
    if (mode === "gravity") {
      find("conditions").textContent = row.length + " flight specimen · O₂ " + row.oxygen.replace("~ ", "≈ ") + "% · "
        + row.direction.toLowerCase() + " flow at " + row.flow;
      burnStrip("Earth · 1 g", row.earth, row.length, false);
      burnStrip("Orbit · microgravity", row.orbit, row.length, !revealed);
      const difference = lengthCm(row.earth, row.length) - lengthCm(row.orbit, row.length);
      answer = difference > 0 ? 0 : difference < 0 ? 2 : 1;
      reading = ["The Earth test burned farther.", "Both tests recorded the same burn extent.", "The flight test burned farther."][answer];
    } else {
      find("conditions").textContent = "Gas concentrations before and after the test";
      sensor("Oxygen · O₂", row.oxygen, "% by volume", false);
      sensor("Carbon monoxide · CO", row.co, "ppm", !revealed);
      sensor("Carbon dioxide · CO₂", row.co2, "% by volume", !revealed);
      const difference = Number(row.co[1]) - Number(row.co[0]);
      answer = difference > 0 ? 0 : difference < 0 ? 2 : 1;
      const oxygenChange = Number(row.oxygen[1]) === Number(row.oxygen[0]) ? "O₂ had the same reported value at both endpoints." :
        "O₂ changed from " + row.oxygen[0] + "% to " + row.oxygen[1] + "%.";
      reading = "CO went from " + row.co[0] + " to " + row.co[1] + " ppm. " + oxygenChange;
    }
    find("prompt").textContent = info.question;
    find("prompt").hidden = revealed;
    find("choices").hidden = revealed;
    dialog.querySelectorAll("[data-choice]").forEach(function (button, i) {
      button.textContent = info.choices[i];
      button.setAttribute("aria-pressed", String(i === choice));
      button.disabled = revealed;
    });
    find("action").textContent = revealed ? "Next case" : (mode === "gravity" ? "Reveal orbit result" : "Reveal gas readings");
    find("result").textContent = revealed ? (answer === choice ? "Correct. " : "You picked “" + info.choices[choice] + "”. ") + reading : "";
    find("source-row").textContent = "NASA " + pack.source + " · " + info.study + " Experimental Table · CSV line " + row.line;
    find("doi").textContent = "DOI " + pack.doi;
    find("doi").href = "https://doi.org/" + pack.doi;
  }

  function open(nextMode) {
    const data = window.FLAME_EVIDENCE_DATA;
    if (!Object.hasOwn(modes, nextMode) || !data || !data[nextMode] || !data[nextMode].cases.length) return false;
    if (!dialog) install();
    if (!dialog.open) returnFocus = document.activeElement;
    mode = nextMode; index = 0; choice = 0; revealed = false;
    render();
    if (!dialog.open) dialog.showModal();
    find("action").focus({preventScroll:true});
    return true;
  }

  function close() {
    if (!dialog || !dialog.open) return false;
    dialog.close();
    if (returnFocus && returnFocus.isConnected) returnFocus.focus({preventScroll:true});
    returnFocus = null;
    return true;
  }

  function handle(action) {
    if (!dialog || !dialog.open) return false;
    if (action === "back") return close();
    if (revealed && (action === "left" || action === "right")) {
      const target = document.activeElement === find("doi") ? find("action") : find("doi");
      target.focus();
      return true;
    }
    if (revealed && action === "confirm" && document.activeElement === find("doi")) {
      find("doi").click();
      return true;
    }
    const count = window.FLAME_EVIDENCE_DATA[mode].cases.length;
    if (action === "up" || action === "down" || (action === "confirm" && revealed)) {
      index = (index + (action === "up" ? count - 1 : 1)) % count;
      choice = 0; revealed = false;
    } else if (action === "left" || action === "right") {
      if (!revealed) choice = (choice + (action === "left" ? 2 : 1)) % 3;
    } else if (action === "confirm") {
      revealed = true;
    } else { return false; }
    render();
    find("action").focus({preventScroll:true});
    return true;
  }

  window.FLAME_EVIDENCE = { open, close, handle, isOpen: () => !!dialog && dialog.open };
}());
