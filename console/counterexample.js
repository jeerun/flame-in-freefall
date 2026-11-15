/* Find a real FLEX test with the same fuel and gas mix and the opposite recorded outcome. */
(function () {
  "use strict";

  const exampleId = 108;
  let dialog, content, title, exampleButton, closeButton, sourceLink, returnFocus;
  let model, predictCompletion;

  function oppositeOf(outcome) {
    if (outcome === "Completion") return "Extinction";
    if (outcome === "Extinction") return "Completion";
    return null;
  }

  function findCounterexample(row, data) {
    const opposite = oppositeOf(row[8]);
    if (!opposite) return null;
    const span = key => {
      const feature = data.features.find(item => item.key === key);
      return feature ? feature.data_max - feature.data_min : 0;
    };
    const pressureSpan = span("p"), diameterSpan = span("d0");
    if (!(pressureSpan > 0 && diameterSpan > 0)) return null;

    let nearest = null, best = Infinity;
    for (const other of data.tests) {
      if (other[8] !== opposite || other[2] !== row[2] || other[3] !== row[3] ||
          other[5] !== row[5] || other[6] !== row[6]) continue;
      const distance = Math.hypot((other[4] - row[4]) / pressureSpan, (other[7] - row[7]) / diameterSpan);
      if (distance < best || (distance === best && nearest && other[0] < nearest[0])) {
        nearest = other;
        best = distance;
      }
    }
    return nearest;
  }

  function element(tag, text, className) {
    const node = document.createElement(tag);
    if (text != null) node.textContent = text;
    if (className) node.className = className;
    return node;
  }

  function makeDialog() {
    const style = element("style");
    style.textContent = `
      #counterexample {
        color-scheme:dark; width:min(47rem,calc(100% - 1.25rem)); max-height:calc(100dvh - 1.25rem);
        margin:auto; padding:0; overflow:auto; overscroll-behavior:contain; background:#202421;
        border:1px solid #464e45; border-radius:1rem; color:#f2f0e6; font:inherit;
        font-variant-numeric:tabular-nums; box-shadow:0 1.25rem 5rem #09110e99; scrollbar-color:#646d60 #202421;
      }
      #counterexample::backdrop { background:rgb(12 15 12 / 82%); }
      #counterexample * { box-sizing:border-box; }
      #counterexample header { display:flex; align-items:center; justify-content:space-between; gap:.8rem;
        padding:.95rem 1.3rem; border-bottom:1px solid #464e45; }
      #counterexample .source-id { color:#82d9c4; font-size:.78rem; font-weight:650; letter-spacing:.045em; }
      #counterexample h2 { margin:.22rem 0 0; color:#f2f0e6; font-size:clamp(1.5rem,3vw,1.95rem); line-height:1.12; letter-spacing:-.025em; font-weight:650; }
      #counterexample .pair-body { padding:.85rem 1.3rem .8rem; }
      #counterexample p { margin:0 0 .7rem; font-size:1rem; line-height:1.42; }
      #counterexample .mix { color:#d8dfd4; }
      #counterexample .pair { width:100%; border-collapse:separate; border-spacing:0; table-layout:fixed;
        border:1px solid #464e45; border-radius:.55rem; overflow:hidden; font-size:.93rem; }
      #counterexample .pair th, #counterexample .pair td { padding:.46rem .65rem; border-bottom:1px solid #40473e; text-align:left; vertical-align:middle; }
      #counterexample .pair th + th, #counterexample .pair td { border-left:1px solid #40473e; }
      #counterexample .pair tr:last-child td, #counterexample .pair tbody tr:last-child th { border-bottom:0; }
      #counterexample .pair th:first-child { width:33%; }
      #counterexample .pair th[scope=row] { color:#c4cbbf; font-weight:500; }
      #counterexample .pair thead { background:#292f29; color:#e8ebdf; }
      #counterexample .pair thead th:first-child { font-size:.8rem; color:#b4bcb2; font-weight:500; }
      #counterexample .recorded td { font-weight:650; font-size:1.16rem; }
      #counterexample .recorded td[data-end="Completion"] { background:#3b3127; color:#ffb789; }
      #counterexample .recorded td[data-end="Extinction"] { background:#263b32; color:#9ee3cf; }
      #counterexample .pair .fitted td { color:#edece3; font-weight:600; }
      #counterexample .method { margin-top:.65rem; color:#b4bcb2; font-size:.86rem; }
      #counterexample details { color:#c6d0c1; font-size:.84rem; line-height:1.4; }
      #counterexample details summary { color:#d9e8d9; width:fit-content; padding:.35rem 0; cursor:pointer; }
      #counterexample details p { font-size:inherit; margin:0 0 .25rem; }
      #counterexample .actions { display:flex; flex-wrap:wrap; justify-content:space-between; align-items:center;
        gap:.6rem; padding:.55rem 1.3rem; border-top:1px solid #464e45; }
      #counterexample .actions[hidden] { display:none; }
      #counterexample button { padding:.3rem .8rem; border:1px solid #535d52; border-radius:.48rem; min-height:max(44px,2.55rem);
        background:transparent; color:#d5dcd0; font:inherit; font-size:.93rem; cursor:pointer; }
      #counterexample .actions button { background:#82d9c4; color:#132820; border-color:#82d9c4; font-weight:700; }
      #counterexample a { color:#82d9c4; text-decoration:underline; text-underline-offset:.15em; font-size:.83rem; }
      #counterexample button:hover, #counterexample summary:hover, #counterexample a:hover { filter:brightness(1.17); }
      #counterexample :focus-visible { outline:2px solid #d5f9eb; outline-offset:3px; }
      @media (max-width:38rem) {
        #counterexample .pair th, #counterexample .pair td { padding:.4rem .38rem; overflow-wrap:anywhere; }
        #counterexample .recorded td { font-size:1rem; }
        #counterexample .pair-body, #counterexample header, #counterexample .actions { padding-inline:.8rem; }
      }
      @media (max-height:30rem) {
        #counterexample .pair-body, #counterexample header { padding-top:.5rem; padding-bottom:.45rem; }
        #counterexample .pair th, #counterexample .pair td { padding-block:.3rem; }
      }
    `;
    document.head.append(style);
    dialog = element("dialog");
    dialog.id = "counterexample";
    const header = element("header"), heading = element("div");
    title = element("h2", "Find a counterexample");
    title.id = "counterexampleTitle";
    dialog.setAttribute("aria-labelledby", title.id);
    heading.append(element("div", "FLEX · NASA PSI-69", "source-id"), title);
    content = element("div", null, "pair-body");
    content.setAttribute("aria-live", "polite");
    const actions = element("div", null, "actions");
    exampleButton = element("button", "Show FLEX #108 example");
    exampleButton.type = "button";
    exampleButton.addEventListener("click", () => {
      showRow(model.tests.find(row => row[0] === exampleId));
      closeButton.focus({ preventScroll: true });
    });
    closeButton = element("button", "Close");
    closeButton.type = "button";
    closeButton.addEventListener("click", close);
    header.append(heading, closeButton);
    sourceLink = element("a", "NASA PSI-69 FLEX experimental table ↗");
    sourceLink.href = "https://psi.nasa.gov/physci/repo/data/investigations/PSI-69";
    sourceLink.target = "_blank";
    sourceLink.rel = "noopener noreferrer";
    actions.append(sourceLink, exampleButton);
    dialog.append(header, content, actions);
    dialog.addEventListener("cancel", event => { event.preventDefault(); close(); });
    document.body.append(dialog);
  }

  function modelValue(row) {
    const p = typeof predictCompletion === "function" ? predictCompletion(row) : null;
    if (!Number.isFinite(p) || p < 0 || p > 1) return "Unavailable";
    return Math.min(99, Math.max(1, p * 100)).toFixed(1) + "%";
  }

  function pairTable(selected, match) {
    const table = element("table", null, "pair");
    table.setAttribute("aria-label", "Recorded FLEX test outcomes and fitted estimates");
    const head = table.createTHead().insertRow();
    ["Measurement", "Selected #" + selected[0], "Counterexample #" + match[0]].forEach(label => {
      const th = element("th", label);
      th.scope = "col";
      head.append(th);
    });
    const body = table.createTBody();
    function add(label, value, className) {
      const tr = body.insertRow(), th = element("th", label);
      th.scope = "row";
      if (className) tr.className = className;
      tr.append(th);
      for (const test of [selected, match]) {
        const cell = element("td", value(test));
        if (className === "recorded") cell.dataset.end = test[8];
        tr.append(cell);
      }
    }
    add("NASA recorded", row => row[8] === "Completion" ? "Burned all its fuel" : "Visible flame went out", "recorded");
    add("Model chance of completion¹", modelValue, "fitted");
    add("Pressure", row => row[4].toFixed(3) + " atm");
    add("Starting diameter", row => row[7].toFixed(2) + " mm");
    return table;
  }

  function showRow(selected) {
    const hasData = model && model.meta && !model.meta.mock && Array.isArray(model.tests) &&
      model.tests.length > 0 && Array.isArray(model.features);
    const row = hasData && selected && model.tests.find(test => test[0] === selected[0]);
    const match = row && findCounterexample(row, model);
    content.replaceChildren();
    title.textContent = match ? "Same gas mix, opposite outcomes" : "Find a counterexample";
    if (match) {
      const fuel = row[2][0].toUpperCase() + row[2].slice(1);
      content.append(element("p", fuel + " in both tests · " + row[3] + "% oxygen · " + row[5] +
        "% carbon dioxide · " + row[6] + "% helium.", "mix"), pairTable(row, match),
        element("p", "¹ These estimates apply to clear outcomes and are displayed from 1% to 99%. Both rows were used to train the model.", "method"));
      const details = element("details");
      details.append(element("summary", "How was this pair chosen?"), element("p",
        "Among tests with the same fuel and gas mix, the console finds the nearest opposite outcome by pressure and starting diameter. It scales each difference by its observed FLEX range. The pair cannot establish why the outcomes differed."));
      content.append(details);
    } else {
      let message;
      if (!hasData) message = "This comparison needs the real FLEX test table. Keep model.js beside the console.";
      else if (!row) message = "Pick a real FLEX test on the star map to find its closest opposite outcome.";
      else if (!oppositeOf(row[8])) message = "FLEX #" + row[0] + " records " + row[8] + ". An opposite outcome can only be identified for a test that burned to completion or went out.";
      else message = "The in-scope FLEX table has no opposite outcome for #" + row[0] + " with the same fuel and starting gas mix.";
      content.append(element("p", message));
    }
    const example = hasData && model.tests.find(test => test[0] === exampleId);
    exampleButton.hidden = !example || (row && row[0] === exampleId) || !findCounterexample(example, model);
    sourceLink.hidden = !hasData;
    sourceLink.parentNode.hidden = sourceLink.hidden && exampleButton.hidden;
    dialog.scrollTop = 0;
  }

  function open(test, data, predictor) {
    if (!dialog) makeDialog();
    if (!dialog.open) returnFocus = document.activeElement;
    model = data;
    predictCompletion = predictor;
    showRow(test);
    if (!dialog.open) dialog.showModal();
    const hasPair = content.querySelector("table");
    (hasPair || exampleButton.hidden ? closeButton : exampleButton).focus({ preventScroll: true });
  }

  function isOpen() { return !!(dialog && dialog.open); }
  function close() {
    if (!isOpen()) return;
    dialog.close();
    if (returnFocus && returnFocus.isConnected) returnFocus.focus({ preventScroll: true });
    returnFocus = null;
  }
  function handle(action) {
    if (!isOpen()) return false;
    if (action === "back") close();
    else if (action === "up" || action === "down") dialog.scrollBy(0, action === "up" ? -90 : 90);
    else if (action === "confirm") {
      const focused = document.activeElement;
      if (dialog.contains(focused) && focused.matches("button, a[href], summary")) focused.click();
    } else if (action === "left" || action === "right") {
      const controls = Array.from(dialog.querySelectorAll("a[href]:not([hidden]), button:not([hidden]), summary"));
      const index = controls.indexOf(document.activeElement);
      controls[(index + (action === "left" ? -1 : 1) + controls.length) % controls.length].focus();
    } else return false;
    return true;
  }

  window.FLAME_COUNTER = { open, isOpen, handle, close };
})();
