/* "What would put this flame out?" One change of the cabin air at a time, read off the console's own model
   and checked against the real FLEX tests near the changed settings. A study aid, not a crew procedure. */
(function () {
  "use strict";

  // The changes a crew could make to the air. Droplet size is a property of the fuel, so it is not offered.
  const LEVERS = [
    { key: "o2", dir: -1, verb: "Lower oxygen", gas: "oxygen" },
    { key: "co2", dir: 1, verb: "Add carbon dioxide", gas: "carbon dioxide" },
    { key: "he", dir: 1, verb: "Add helium", gas: "helium" }
  ];
  const GASES = ["o2", "co2", "he"];
  // Held-out check of the outcome formula (model/per_fuel/comparison.json, "calibration_held_out"): of the tests it
  // rated between 20 and 30 %, this share burned all their fuel. tests/test_advisor.cjs keeps the figure in step.
  const HELD_OUT = { from: 20, to: 30, burned: 22 };

  function tidy(value) { return String(Math.round(value * 100) / 100); }

  // How the real tests near a setting bear on the model's reading there.
  function support(e) {
    const near = e.near || { n: 0, out: 0, done: 0, other: 0 }, clear = near.out + near.done;
    if (!near.n) return { rank: 1, text: "No real test is close to these settings, so the model is filling a gap." };
    if (!clear) return { rank: 1, text: "Nearby real tests: " + near.n + ". " + (near.n === 1 ? "It" : "All") + " ended in disruption, with no clear outcome." };
    if (clear === 1) {
      return near.out ? { rank: 2, text: "One nearby real test has a clear outcome: it went out." }
        : { rank: 0, text: "One nearby real test has a clear outcome: it burned all its fuel. Trust the test over the model." };
    }
    if (near.out * 2 > clear) return { rank: 3, text: "Nearby real tests: " + near.out + " of " + clear + " with a clear outcome went out." };
    return { rank: 0, text: "Nearby real tests: only " + near.out + " of " + clear + " with a clear outcome went out. Trust the tests over the model." };
  }

  // input: { values, features, exclusive, unsure, watch, evaluate(values) -> { pKeep, keep, pDis, dis, level, near } }
  // "keep" is the whole percentage the console would show; a change counts once that number is under the watch level.
  function plan(input) {
    const byKey = {};
    input.features.forEach(f => { byKey[f.key] = f; });
    const goal = Math.round(input.watch * 100);
    const now = input.evaluate(input.values);
    const result = { now, goal, options: [], left: [], already: now.level !== "outside" && now.keep < goal };
    if (now.level === "outside") return result;

    LEVERS.forEach(lever => {
      const f = byKey[lever.key];
      if (!f) return;
      if ((input.unsure || []).indexOf(lever.key) >= 0) { result.left.push({ key: lever.key, why: "unsure" }); return; }
      const clash = (input.exclusive || []).map(pair => pair[0] === lever.key ? pair[1] : pair[1] === lever.key ? pair[0] : null)
        .filter(other => other && byKey[other] && input.values[other] > 1e-9)[0];
      if (lever.dir > 0 && clash) { result.left.push({ key: lever.key, why: "never-mixed", other: clash }); return; }

      let best = null, hit = null;
      for (let i = 1; i < 5000 && !hit; i++) {
        const value = Math.round((input.values[lever.key] + lever.dir * f.step * i) / f.step) * f.step;
        if (value < f.data_min - 1e-9 || value > f.data_max + 1e-9 || value < f.min - 1e-9 || value > f.max + 1e-9) break;
        const values = Object.assign({}, input.values, { [lever.key]: value });
        if (GASES.reduce((sum, key) => sum + (byKey[key] ? values[key] : 0), 0) > 100 + 1e-9) break;
        const e = input.evaluate(values);
        if (e.level === "outside") break;
        if (!best || e.pKeep < best.e.pKeep) best = { value, e };
        if (e.keep < goal) hit = { value, e };
      }
      if (!best) { result.left.push({ key: lever.key, why: "at-limit", dir: lever.dir }); return; }
      if (!hit && best.e.keep >= now.keep) { result.left.push({ key: lever.key, why: "no-effect" }); return; }
      const end = hit || best;
      result.options.push({
        key: lever.key, verb: lever.verb, from: input.values[lever.key], to: end.value, reaches: !!hit, e: end.e,
        span: Math.abs(end.value - input.values[lever.key]) / ((f.data_max - f.data_min) || 1),
        values: Object.assign({}, input.values, { [lever.key]: end.value }), support: support(end.e)
      });
    });
    // Changes that get there come first; among them, the ones the nearby tests back, then the smallest change.
    result.options.sort((a, b) => (b.reaches - a.reaches) || (b.support.rank - a.support.rank) || (a.span - b.span));
    return result;
  }

  /* ---------- the panel ---------- */
  let dialog, body, closeButton, returnFocus, reader, api, undo = null;

  function element(tag, text, className) {
    const node = document.createElement(tag);
    if (text != null) node.textContent = text;
    if (className) node.className = className;
    return node;
  }

  function makeDialog() {
    const style = element("style");
    style.textContent = `
      #advisor {
        color-scheme:dark; width:min(46rem,calc(100% - 1.25rem)); max-height:calc(100dvh - 1.25rem);
        margin:auto; padding:0; overflow:auto; overscroll-behavior:contain; background:#202421;
        border:1px solid #464e45; border-radius:1rem; color:#f2f0e6; font:inherit;
        font-variant-numeric:tabular-nums; box-shadow:0 1.25rem 5rem #09110e99; scrollbar-color:#646d60 #202421;
      }
      #advisor::backdrop { background:rgb(12 15 12 / 82%); }
      #advisor * { box-sizing:border-box; }
      #advisor header { display:flex; align-items:center; justify-content:space-between; gap:.8rem;
        padding:.85rem 1.3rem; border-bottom:1px solid #464e45; }
      #advisor .source-id { color:#82d9c4; font-size:max(12px,.78rem); font-weight:650; letter-spacing:.045em; }
      #advisor h2 { margin:.2rem 0 0; color:#f2f0e6; font-size:clamp(1.4rem,2.8vw,1.85rem); line-height:1.12; letter-spacing:-.025em; font-weight:650; }
      #advisor .advice { padding:.8rem 1.3rem .9rem; display:grid; gap:.6rem; }
      #advisor p { margin:0; font-size:1rem; line-height:1.42; }
      #advisor .now { color:#d8dfd4; }
      #advisor .now b { color:#ffb789; font-weight:650; }
      #advisor .goal { color:#b4bcb2; font-size:.93rem; }
      #advisor ol { list-style:none; margin:0; padding:0; display:grid; gap:.5rem; }
      #advisor li { display:grid; grid-template-columns:minmax(0,1fr) auto auto; gap:.3rem .9rem; align-items:center;
        padding:.6rem .8rem; border:1px solid #464e45; border-left:.28rem solid #82d9c4; border-radius:.6rem; background:#262b27; }
      #advisor li.short { border-left-color:#ffb789; }
      #advisor li strong { display:block; font-size:1.08rem; font-weight:650; }
      #advisor li .detail { color:#d8dfd4; font-size:.93rem; }
      #advisor li .evidence { grid-column:1 / -1; color:#b9c2b6; font-size:max(12px,.88rem); line-height:1.4; }
      #advisor li .result { text-align:right; white-space:nowrap; }
      #advisor li .result b { display:block; font-size:1.45rem; font-weight:650; letter-spacing:-.03em; color:#9ee3cf; }
      #advisor li.short .result b { color:#ffb789; }
      #advisor li .result span { color:#b9c2b6; font-size:max(12px,.78rem); }
      #advisor .left { display:grid; gap:.25rem; color:#b9c2b6; font-size:max(12px,.88rem); line-height:1.4; }
      #advisor .left p { font-size:inherit; }
      #advisor .fine { color:#aeb7ab; font-size:max(12px,.84rem); line-height:1.45; border-top:1px solid #464e45; padding-top:.6rem; }
      #advisor .undo { display:flex; flex-wrap:wrap; align-items:center; justify-content:space-between; gap:.5rem .9rem;
        padding:.5rem .8rem; border:1px dashed #6b7568; border-radius:.6rem; color:#d8dfd4; font-size:.93rem; }
      #advisor button { padding:.3rem .85rem; border:1px solid #535d52; border-radius:.48rem; min-height:max(44px,2.55rem);
        background:transparent; color:#d5dcd0; font:inherit; font-size:.93rem; cursor:pointer; white-space:nowrap; }
      #advisor li button { background:#82d9c4; color:#132820; border-color:#82d9c4; font-weight:700; }
      #advisor li.short button { background:transparent; color:#f2f0e6; border-color:#8a7a66; font-weight:600; }
      #advisor kbd { display:inline-grid; place-items:center; min-width:1.3rem; height:1.3rem; margin-right:.35rem; padding:0 .25rem;
        border:1px solid currentColor; border-radius:999px; font:600 max(12px,.72rem)/1 ui-monospace,Consolas,monospace; opacity:.8; }
      #advisor .keys { color:#aeb7ab; font-size:max(12px,.8rem); }
      #advisor button:hover { filter:brightness(1.15); }
      #advisor :focus-visible { outline:2px solid #d5f9eb; outline-offset:3px; }
      @media (max-width:38rem) {
        #advisor header, #advisor .advice { padding-inline:.8rem; }
        #advisor li { grid-template-columns:minmax(0,1fr) auto; }
        #advisor li button { grid-column:1 / -1; }
      }
      @media (max-height:44rem) {
        #advisor header { padding-block:.55rem; }
        #advisor .advice { gap:.45rem; padding-top:.6rem; padding-bottom:.65rem; }
        #advisor li { padding-block:.4rem; }
      }
    `;
    document.head.append(style);
    dialog = element("dialog");
    dialog.id = "advisor";
    const header = element("header"), heading = element("div"), title = element("h2", "What would put this flame out?");
    title.id = "advisorTitle";
    dialog.setAttribute("aria-labelledby", title.id);
    heading.append(element("div", "FLEX · NASA PSI-69 · model estimate", "source-id"), title);
    closeButton = element("button");
    closeButton.type = "button";
    closeButton.append(element("kbd", "B"), "Close");
    closeButton.addEventListener("click", close);
    header.append(heading, closeButton);
    body = element("div", null, "advice");
    body.setAttribute("aria-live", "polite");
    dialog.append(header, body);
    dialog.addEventListener("cancel", event => { event.preventDefault(); close(); });
    document.body.append(dialog);
  }

  function label(key) { return api.features.find(f => f.key === key); }
  function amount(key, value) { const f = label(key); return tidy(value) + " " + f.unit; }

  function settingsLine() {
    return [api.fuelLabel].concat(api.features.filter(f => GASES.indexOf(f.key) < 0 || f.key === "o2" || api.values[f.key] > 0)
      .map(f => tidy(api.values[f.key]) + " " + f.unit + (f.key === "p" ? "" : " " + (f.key === "d0" ? "droplet" : f.label.toLowerCase())))).join(" · ");
  }

  function leftOut(item) {
    const f = label(item.key), name = f.label.toLowerCase();
    if (item.why === "unsure") return f.label + " is left out: for " + api.fuelLabel.toLowerCase() + " the tests do not settle which way it pushes.";
    if (item.why === "never-mixed") return f.label + " is left out: no FLEX test mixed it with " + label(item.other).label.toLowerCase() + ", which is already in this air.";
    if (item.why === "at-limit") return f.label + " is left out: " + amount(item.key, api.values[item.key]) + " is already the " + (item.dir < 0 ? "lowest" : "highest") + " FLEX tested.";
    return f.label + " is left out: within what FLEX tested, changing " + name + " does not lower this reading.";
  }

  function show() {
    const result = plan(api), now = result.now;
    body.replaceChildren();
    const nowLine = element("p", null, "now");
    nowLine.append("Now: " + settingsLine() + ". ");
    if (now.level === "outside") nowLine.append("These settings are outside what FLEX tested.");
    else { nowLine.append("Model: "); nowLine.append(element("b", now.keep + " %")); nowLine.append(" chance of burning all the fuel."); }
    body.append(nowLine);

    const canUndo = undo && api.fuel === undo.fuel && api.features.every(f => Math.abs(api.values[f.key] - undo.after[f.key]) < 1e-9);
    if (!canUndo) undo = null;
    if (canUndo) {
      const box = element("div", null, "undo"), back = element("button", "Put it back");
      back.type = "button"; back.dataset.act = "undo";
      back.addEventListener("click", () => { const previous = undo; undo = null; api.apply(previous.before, "Put back: " + previous.text + "."); refresh(); });
      box.append(element("span", "You tried: " + undo.text + "."), back);
      body.append(box);
    }

    if (now.level === "outside") {
      body.append(element("p", "There is no usable reading to improve here. Bring the settings back inside the tested range first.", "goal"));
    } else if (result.already) {
      body.append(element("p", "The model already expects this flame to go out: the reading is under its " + result.goal + " % watch level. " + support(now).text, "goal"));
    } else {
      body.append(element("p", "One change at a time: how far must each go before the reading drops under the model's " + result.goal + " % watch level?", "goal"));
      const list = element("ol");
      result.options.forEach(option => {
        const item = element("li", null, option.reaches ? "" : "short"), text = element("div"), res = element("div", null, "result");
        const edge = !option.reaches && option.key !== "o2" ? " (the most FLEX tested)" : !option.reaches ? " (the least FLEX tested)" : "";
        text.append(element("strong", option.verb + " to " + amount(option.key, option.to)),
          element("div", "from " + amount(option.key, option.from) + edge
            + (option.key === "o2" && api.cabin && option.to < api.cabin.o2 - 1e-9 ? " · under the " + tidy(api.cabin.o2) + " % oxygen of " + api.cabin.name + " air" : "")
            + (option.e.dis != null && option.e.pDis >= 0.5 ? " · modelled disruption chance " + option.e.dis + " %" : ""), "detail"));
        res.append(element("b", option.e.keep + " %"), element("span", option.reaches ? "under the watch level" : "not enough alone"));
        const tryIt = element("button", "Try it");
        tryIt.type = "button"; tryIt.dataset.act = "try";
        tryIt.setAttribute("aria-label", "Try it: " + option.verb.toLowerCase() + " to " + amount(option.key, option.to));
        tryIt.addEventListener("click", () => {
          const words = label(option.key).label.toLowerCase() + " " + amount(option.key, option.from) + " to " + amount(option.key, option.to);
          undo = { fuel: api.fuel, before: Object.assign({}, api.values), after: Object.assign({}, option.values), text: words };
          api.apply(option.values, "Trying " + words + ". Open this panel again to put it back.");
          close();
        });
        item.append(text, res, tryIt, element("div", option.support.text, "evidence"));
        list.append(item);
      });
      if (result.options.length) body.append(list);
      if (!result.options.some(option => option.reaches)) {
        body.append(element("p", result.options.length
          ? "No single change gets there within what FLEX tested. The model has no tested way to put this flame out by changing one gas."
          : "Within what FLEX tested, none of these changes lowers this reading.", "goal"));
      }
    }
    const left = element("div", null, "left");
    result.left.forEach(item => left.append(element("p", leftOut(item))));
    if (api.features.some(f => f.key === "p")) left.append(element("p", "Pressure is not offered: the tests sat at two pressures, about 0.7 and 1 atm, so its direction is not known."));
    body.append(left);
    body.append(element("p", "A reading of the console's model" + (api.rows ? " (" + api.rows + " FLEX droplet tests)" : "")
      + ", for study and planning. Not a crew procedure. It reads how FLEX tests with such settings ended. It is not a proven effect of making the change."
      + (result.goal === HELD_OUT.to ? " Under the watch level is not \"out\": held out of training, " + HELD_OUT.burned + " % of the tests the model rated "
        + HELD_OUT.from + " to " + HELD_OUT.to + " % still burned all their fuel." : "")
      + " It looks only at the flame: it does not check that the changed air is safe to breathe."
      + " \"Out\" means the visible flame; FLEX found that fuel can keep reacting after it, in a cool flame.", "fine"));
    body.append(element("p", "D-pad or arrows: choose · A or Enter: try it · B or Esc: close", "keys"));
  }

  function refresh() {
    api = reader();
    show();
    focusFirst();
  }
  function controls() { return Array.from(dialog.querySelectorAll("button")).filter(b => !b.hidden); }
  function focusFirst() {
    const first = dialog.querySelector("button[data-act]") || closeButton;
    first.focus({ preventScroll: true });
    dialog.scrollTop = 0;
  }

  // open(read): read() returns the console's present state and the two things the panel may do with it:
  // { fuel, fuelLabel, values, features, exclusive, unsure, watch, rows, cabin, evaluate(values), apply(values, message) }
  // cabin: { name, o2 } when the settings stand for a named cabin air other than Earth's, else null.
  function open(read) {
    if (!dialog) makeDialog();
    if (!dialog.open) returnFocus = document.activeElement;
    reader = read;
    api = read();
    show();
    if (!dialog.open) dialog.showModal();
    focusFirst();
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
    else if (action === "confirm") {
      const focused = document.activeElement;
      if (dialog.contains(focused) && focused.matches("button")) focused.click();
    } else if (action === "up" || action === "down" || action === "left" || action === "right") {
      const list = controls(), index = list.indexOf(document.activeElement);
      const step = action === "up" || action === "left" ? -1 : 1;
      list[(index + step + list.length) % list.length].focus();
    } else return false;
    return true;
  }

  window.FLAME_ADVISOR = { open, isOpen, handle, close, plan, support, heldOut: HELD_OUT };
})();
