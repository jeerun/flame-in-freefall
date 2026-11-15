// Two offline readings of NASA's experimental tables. The page routes keyboard and gamepad actions here.
(function () {
  "use strict";
  const modes = {
    gravity: {title: "Earth or orbit?", study: "SAFFIRE-II", unit: "Sample",
      question: "Where did this material burn farther?", choices: ["Earth", "Same extent", "Orbit"]},
    sensors: {title: "What did oxygen miss?", study: "BASS-II", unit: "Test",
      question: "What happened to the carbon monoxide reading?", choices: ["It rose", "It held steady", "It fell"]}
  };
  let dialog, mode, index, choice, revealed, returnFocus;
  const find = id => dialog.querySelector("#ev-" + id);
  const current = () => window.FLAME_EVIDENCE_DATA[mode].cases[index];

  function install() {
    const style = document.createElement("style");
    style.textContent = `
      #ev-dialog { width:min(51rem,calc(100% - 1.2rem)); max-height:calc(100dvh - 1.2rem);
        margin:auto; padding:0; overflow:auto; overscroll-behavior:contain; color:var(--ink);
        background:var(--panel); border:1px solid #465a86; border-radius:1rem;
        box-shadow:0 1rem 5rem #030813af; scrollbar-color:var(--line) var(--panel); }
      #ev-dialog::backdrop { background:#050c1edc; }
      #ev-dialog * { box-sizing:border-box; }
      .ev-head, .ev-nav, .ev-buttons, .ev-group { display:flex; align-items:center; gap:.5rem; }
      .ev-head { justify-content:space-between; padding:1rem 1.3rem .85rem; border-bottom:1px solid var(--line); }
      .ev-id, .ev-source, .ev-keys, .ev-sub { color:var(--ink-2); font-size:.86rem; }
      #ev-dialog h2 { margin:.15rem 0 0; font-size:1.7rem; font-weight:650; line-height:1.13; color:var(--ink); }
      #ev-dialog button { border:1px solid #556b99; background:var(--panel-hi); color:var(--ink);
        border-radius:.42rem; min-height:2.6rem; padding:.38rem .82rem; cursor:pointer; }
      #ev-dialog button:hover { border-color:var(--flame); }
      #ev-dialog button:focus-visible { outline:2px solid var(--flame-core); outline-offset:2px; }
      .ev-pad { padding:.85rem 1.3rem; }
      .ev-nav { justify-content:space-between; gap:1rem; }
      #ev-material { margin:0; font-size:1.22rem; font-weight:600; }
      .ev-sub { margin:.18rem 0 0; }
      .ev-group { flex-shrink:0; }
      #ev-dialog .ev-arrow { min-width:2.6rem; padding:.3rem; }
      .ev-measures { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:.6rem; margin:.7rem 0; }
      .ev-measure { --accent:#8bbdff; background:#101c36; border:1px solid var(--line); border-top:3px solid var(--accent);
        border-radius:.6rem; padding:.7rem .88rem; min-width:0; }
      .ev-measure:nth-child(2) { --accent:#efb66c; }
      .ev-measure:nth-child(3) { --accent:#a99ce9; }
      .ev-measure .ev-value { font-variant-numeric:tabular-nums; color:var(--ink); font-weight:650;
        display:block; font-size:clamp(1.05rem,2.8vw,1.85rem); margin:.32rem 0 .15rem; }
      .ev-measure .ev-type { font-size:.9rem; color:var(--accent); font-weight:600; }
      .ev-measure .ev-note { font-size:.8rem; color:var(--ink-2); }
      .ev-track { height:.45rem; margin:.5rem 0; border:1px solid #425271; background:#24314d; border-radius:1rem; overflow:hidden; }
      .ev-fill { height:100%; background:var(--accent); }
      .ev-track.covered { background:repeating-linear-gradient(120deg,#293751 0 5px,#1a2843 5px 10px); }
      #ev-dialog[data-mode="sensors"] .ev-measures { grid-template-columns:repeat(3,minmax(0,1fr)); }
      .ev-prompt { font-size:1rem; font-weight:600; margin:.65rem 0 .5rem; }
      .ev-buttons { flex-wrap:wrap; }
      #ev-dialog button[aria-pressed="true"] { background:var(--flame-dim); border-color:var(--flame); box-shadow:inset 0 -2px var(--flame); }
      #ev-dialog button:disabled { opacity:.74; cursor:default; }
      #ev-action { margin-left:auto; }
      #ev-dialog #ev-action { background:#cee3ff; color:#152644; border-color:#cee3ff; font-weight:650; }
      #ev-result { margin:.65rem 0 0; color:var(--flame-core); font-size:1rem; }
      .ev-source { margin:.6rem 0 0; font-size:.78rem; overflow-wrap:anywhere; }
      .ev-keys { margin:0; padding:.55rem 1.3rem; border-top:1px solid var(--line); font-size:.8rem; }
      @media (max-width:40rem) {
        .ev-head,.ev-pad,.ev-keys { padding-left:.8rem; padding-right:.8rem; }
        .ev-nav { gap:.35rem; } .ev-group { gap:.28rem; }
        #ev-dialog[data-mode="sensors"] .ev-measures { grid-template-columns:1fr; gap:.3rem; }
        #ev-dialog[data-mode="sensors"] .ev-measure { display:grid; align-items:center; grid-template-columns:1fr 1.4fr; padding:.3rem .65rem; border-top-width:1px; border-left:3px solid var(--accent); }
        #ev-dialog[data-mode="sensors"] .ev-note { grid-column:2; } .ev-buttons { gap:.36rem; }
        #ev-action { margin-left:0; } .ev-measure { padding:.5rem; }
      }
      @media (max-height:29rem) { .ev-pad,.ev-head { padding-top:.45rem; padding-bottom:.45rem; } }
    `;
    document.head.appendChild(style);
    dialog = document.createElement("dialog");
    dialog.id = "ev-dialog";
    dialog.setAttribute("aria-labelledby", "ev-title");
    dialog.innerHTML = `
      <header class="ev-head"><div><div class="ev-id" id="ev-id"></div><h2 id="ev-title"></h2></div>
        <button type="button" data-control="back">Close</button></header>
      <div class="ev-pad"><div class="ev-nav"><div><h3 id="ev-material"></h3><p class="ev-sub" id="ev-conditions"></p></div>
        <div class="ev-group"><button type="button" class="ev-arrow" data-control="up" aria-label="Previous case">‹</button>
        <span id="ev-count"></span><button type="button" class="ev-arrow" data-control="down" aria-label="Next case">›</button></div></div>
        <div class="ev-measures" id="ev-measures"></div>
        <p class="ev-prompt" id="ev-prompt"></p><div class="ev-buttons" role="group" aria-labelledby="ev-prompt">
          <button type="button" data-choice="0"></button><button type="button" data-choice="1"></button><button type="button" data-choice="2"></button>
          <button type="button" id="ev-action" data-control="confirm"></button></div>
        <p id="ev-result" aria-live="polite"></p><p class="ev-source" id="ev-source"></p>
      </div><p class="ev-keys">↑ ↓ case · ← → pick an answer · A / Enter reveal or advance · B / Esc close</p>
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
      if ((event.key === "Enter" || event.key === " ") && event.target.tagName === "BUTTON"
          && event.target !== find("action")) event.stopPropagation();
    });
    dialog.addEventListener("cancel", function (event) { event.preventDefault(); close(); });
  }

  function measure(title, value, note) {
    const panel = document.createElement("div");
    panel.className = "ev-measure";
    [["ev-type", title], ["ev-value", value], ["ev-note", note]].forEach(function (entry) {
      const span = document.createElement("div");
      span.className = entry[0];
      span.textContent = entry[1];
      panel.appendChild(span);
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
    const panel = measure(label, hidden ? "?" : recorded, "Burn length on a " + length + " specimen");
    const track = document.createElement("div");
    track.setAttribute("aria-hidden", "true");
    track.className = "ev-track" + (hidden ? " covered" : "");
    if (!hidden) {
      const bar = document.createElement("div");
      bar.className = "ev-fill";
      bar.style.width = (100 * lengthCm(value, length) / parseFloat(length)) + "%";
      track.appendChild(bar);
    }
    panel.insertBefore(track, panel.lastChild);
  }

  function sensor(label, values, unit, hidden) {
    measure(label, hidden ? "?" : values.join(" → "), unit + " · initial → final");
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
      find("conditions").textContent = "Flight sample · O₂ " + row.oxygen.replace("~ ", "≈ ") + "% · "
        + row.direction.toLowerCase() + " flow at " + row.flow;
      burnStrip("Earth · 1 g", row.earth, row.length, false);
      burnStrip("Orbit · microgravity", row.orbit, row.length, !revealed);
      const difference = lengthCm(row.earth, row.length) - lengthCm(row.orbit, row.length);
      answer = difference > 0 ? 0 : difference < 0 ? 2 : 1;
      reading = ["The Earth test burned farther.", "Both tests recorded the same burn extent.", "The flight test burned farther."][answer];
    } else {
      find("conditions").textContent = "Recorded gas concentrations before and after this test";
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
    dialog.querySelectorAll("[data-choice]").forEach(function (button, i) {
      button.textContent = info.choices[i];
      button.setAttribute("aria-pressed", String(i === choice));
      button.disabled = revealed;
    });
    find("action").textContent = revealed ? "Next case" : "Reveal readings";
    find("result").textContent = revealed ? (answer === choice ? "Correct. " : "") + reading : "";
    find("source").textContent = "NASA " + pack.source + " · " + info.study + " Experimental Table · CSV line " + row.line + " · DOI " + pack.doi;
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
