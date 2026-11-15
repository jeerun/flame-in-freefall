/* Find a real FLEX test with the same fuel and gas mix and the opposite recorded outcome. */
(function () {
  "use strict";

  const exampleId = 108;
  let dialog, content, exampleButton, closeButton;
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
      #counterexample { width: min(38rem, 94vw); max-height: 90dvh; margin: auto; padding: 1.2rem;
        overflow: auto; border: 1px solid var(--line); border-radius: .85rem; background: var(--panel);
        color: var(--ink); font: inherit; box-shadow: 0 1rem 4rem #060a17aa; }
      #counterexample::backdrop { background: #070d20ca; }
      #counterexample h2 { color: var(--ink); font-size: 1.45rem; margin: 0 0 .7rem; }
      #counterexample p { line-height: 1.4; margin: .6rem 0; }
      #counterexample .pair { width: 100%; border-collapse: collapse; font-size: .95rem; }
      #counterexample .pair th, #counterexample .pair td { padding: .48rem .35rem; border-bottom: 1px solid var(--line); text-align: left; }
      #counterexample .pair th[scope=row] { color: var(--ink-2); font-weight: 500; }
      #counterexample .pair thead { color: var(--flame); }
      #counterexample .method { font-size: .86rem; color: var(--ink-2); }
      #counterexample .actions { display: flex; gap: .55rem; flex-wrap: wrap; margin-top: .9rem; }
      #counterexample button { padding: .4rem .8rem; border: 1px solid var(--line); border-radius: .45rem; background: var(--panel-hi); cursor: pointer; }
      #counterexample a { color: var(--flame); }
      #counterexample :focus-visible { outline: 2px solid var(--flame); outline-offset: 2px; }
    `;
    document.head.append(style);
    dialog = element("dialog");
    dialog.id = "counterexample";
    const title = element("h2", "Find the counterexample");
    title.id = "counterexampleTitle";
    dialog.setAttribute("aria-labelledby", title.id);
    content = element("div");
    content.setAttribute("aria-live", "polite");
    const actions = element("div", null, "actions");
    exampleButton = element("button", "Show FLEX #108 example");
    exampleButton.type = "button";
    exampleButton.addEventListener("click", () => {
      showRow(model.tests.find(row => row[0] === exampleId));
      closeButton.focus();
    });
    closeButton = element("button", "Close");
    closeButton.type = "button";
    closeButton.addEventListener("click", close);
    actions.append(exampleButton, closeButton);
    dialog.append(title, content, actions);
    document.body.append(dialog);
  }

  function modelValue(row) {
    const p = typeof predictCompletion === "function" ? predictCompletion(row) : null;
    return Number.isFinite(p) && p >= 0 && p <= 1 ? (p * 100).toFixed(1) + "%" : "Unavailable";
  }

  function pairTable(selected, match) {
    const table = element("table", null, "pair");
    table.setAttribute("aria-label", "Recorded FLEX test outcomes and fitted estimates");
    const head = table.createTHead().insertRow();
    ["", "Selected #" + selected[0], "Counterexample #" + match[0]].forEach(label => {
      const th = element("th", label);
      th.scope = "col";
      head.append(th);
    });
    const body = table.createTBody();
    function add(label, value) {
      const tr = body.insertRow(), th = element("th", label);
      th.scope = "row";
      tr.append(th, element("td", value(selected)), element("td", value(match)));
    }
    add("Pressure", row => row[4].toFixed(3) + " atm");
    add("Starting diameter", row => row[7].toFixed(2) + " mm");
    add("NASA recorded", row => row[8] === "Completion" ? "Burned all its fuel" : "Visible flame went out");
    add("Model chance of completion¹", modelValue);
    return table;
  }

  function showRow(selected) {
    const hasData = model && model.meta && !model.meta.mock && Array.isArray(model.tests) &&
      model.tests.length > 0 && Array.isArray(model.features);
    const row = hasData && selected && model.tests.find(test => test[0] === selected[0]);
    const match = row && findCounterexample(row, model);
    content.replaceChildren();
    if (match) {
      const fuel = row[2][0].toUpperCase() + row[2].slice(1);
      content.append(element("p", fuel + " in both tests · " + row[3] + "% oxygen · " + row[5] +
        "% carbon dioxide · " + row[6] + "% helium."), pairTable(row, match),
        element("p", "¹ Fitted estimates for tests with a clear outcome. Both rows were used for training. These observations cannot establish what caused their outcomes to differ.", "method"),
        element("p", "Both tests have the same recorded fuel, oxygen, CO₂ and helium. Pressure and diameter each count in proportion to their observed FLEX range when choosing the closest opposite outcome.", "method"));
      const source = element("a", "NASA PSI-69 FLEX experimental table ↗");
      source.href = "https://psi.nasa.gov/physci/repo/data/investigations/PSI-69";
      source.target = "_blank";
      source.rel = "noopener noreferrer";
      content.append(source);
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
    dialog.scrollTop = 0;
  }

  function open(test, data, predictor) {
    if (!dialog) makeDialog();
    model = data;
    predictCompletion = predictor;
    showRow(test);
    if (!dialog.open) dialog.showModal();
    const hasPair = content.querySelector("table");
    (hasPair || exampleButton.hidden ? closeButton : exampleButton).focus({ preventScroll: true });
  }

  function isOpen() { return !!(dialog && dialog.open); }
  function close() { if (isOpen()) dialog.close(); }
  function handle(action) {
    if (!isOpen()) return false;
    if (action === "back") close();
    else if (action === "up" || action === "down") dialog.scrollBy(0, action === "up" ? -90 : 90);
    else if (action === "confirm") {
      const focused = document.activeElement;
      if (dialog.contains(focused) && focused.matches("button, a[href]")) focused.click();
    } else if (action === "left" || action === "right") {
      const controls = Array.from(dialog.querySelectorAll("a[href], button:not([hidden])"));
      const index = controls.indexOf(document.activeElement);
      controls[(index + (action === "left" ? -1 : 1) + controls.length) % controls.length].focus();
    } else return false;
    return true;
  }

  window.FLAME_COUNTER = { open, isOpen, handle, close };
})();
