// The search behind "What would put this flame out?" (console/advisor.js), checked without a browser.
// Run from the repo root:  node tests/test_advisor.cjs
// The oracle below is written from the model's documented formula and the exported test rows. It does not
// call the page's code, so a slip in either one shows up as a disagreement.
const assert = require("assert");
const fs = require("fs");
const path = require("path");
const vm = require("vm");

const root = path.resolve(__dirname, "..");
function load(file) {
  const sandbox = { window: {} };
  vm.runInNewContext(fs.readFileSync(path.join(root, "console", file), "utf8"), sandbox, { filename: file });
  return sandbox.window;
}
const M = load("model.js").FLAME_MODEL;
const advisor = load("advisor.js").FLAME_ADVISOR;
assert.ok(M && !M.meta.mock && M.tests.length, "console/model.js is the real export");
assert.ok(advisor && typeof advisor.plan === "function", "advisor.js exposes plan()");

const COL = { o2: 3, p: 4, co2: 5, he: 6, d0: 7 };
const byKey = Object.fromEntries(M.features.map(f => [f.key, f]));
function score(part, fuel, values) {
  const own = (part.fuel_coef && part.fuel_coef[fuel]) || {};
  return part.intercept + part.fuel[fuel] + M.features.reduce((sum, f) => sum + (part.coef[f.key] + (own[f.key] || 0)) * values[f.key], 0);
}
const shown = p => Math.min(99, Math.max(1, Math.round(p * 100)));
function evaluator(fuel) {
  return values => {
    const pKeep = 1 - 1 / (1 + Math.exp(-score(M.extinction, fuel, values)));
    const pDis = 1 / (1 + Math.exp(-score(M.disruption, fuel, values)));
    const near = { n: 0, out: 0, done: 0, other: 0 };
    for (const t of M.tests) {
      if (t[2] !== fuel) continue;
      const d = Math.hypot(...M.features.map(f => (values[f.key] - t[COL[f.key]]) / (f.data_max - f.data_min)));
      if (d > M.meta.far_distance) continue;
      near.n++;
      if (t[8] === "Extinction") near.out++; else if (t[8] === "Completion") near.done++; else near.other++;
    }
    const outside = M.features.some(f => values[f.key] < f.data_min - 1e-9 || values[f.key] > f.data_max + 1e-9) ||
      M.meta.exclusive.some(pair => values[pair[0]] > 1e-9 && values[pair[1]] > 1e-9) || values.o2 + values.co2 + values.he > 100 + 1e-9;
    return { pKeep, keep: shown(pKeep), pDis, dis: shown(pDis), level: outside ? "outside" : "inside", near };
  };
}
function plan(fuel, changes) {
  const values = Object.fromEntries(M.features.map(f => [f.key, f.default]));
  Object.assign(values, changes);
  const evaluate = evaluator(fuel);
  return { values, evaluate, result: advisor.plan({ values, features: M.features, exclusive: M.meta.exclusive, unsure: M.meta.unsure[fuel] || [], watch: M.meta.watch, evaluate }) };
}
const goal = Math.round(M.meta.watch * 100);
const option = (run, key) => run.result.options.find(o => o.key === key);

// 1. Heptane at the starting values: each of the three gases gets there, at the first step that does.
let run = plan("heptane", {});
assert.equal(run.result.now.keep, 57);
assert.equal(run.result.already, false);
assert.deepEqual(run.result.options.map(o => o.key).sort(), ["co2", "he", "o2"]);
for (const o of run.result.options) {
  const f = byKey[o.key], dir = Math.sign(o.to - o.from);
  assert.ok(o.reaches && o.e.keep < goal, o.key + " ends under the watch level");
  assert.equal(dir, o.key === "o2" ? -1 : 1, o.key + " moves the way a crew could move it");
  assert.ok(Math.abs(o.to / f.step - Math.round(o.to / f.step)) < 1e-6, o.key + " lands on a slider step");
  assert.ok(o.to >= f.data_min - 1e-9 && o.to <= f.data_max + 1e-9, o.key + " stays inside the tested range");
  const before = Object.assign({}, run.values, { [o.key]: o.to - dir * f.step });
  assert.ok(run.evaluate(before).keep >= goal, o.key + ": one step less is not enough, so the change shown is the smallest");
  assert.deepEqual(Object.keys(o.values).filter(k => o.values[k] !== run.values[k]), [o.key], "one setting changes, the others stay");
}
assert.equal(option(run, "o2").to, 19);
assert.equal(option(run, "co2").to, 10);
assert.equal(run.result.options[0].key, "o2", "the change the nearby tests back best comes first");
assert.equal(run.result.left.length, 0);

// 2. Moon Base air: only less oxygen gets there; the two diluents run out of tested range first.
run = plan("heptane", { o2: 30, p: 0.694 });
assert.equal(run.result.now.keep, 99);
assert.ok(option(run, "o2").reaches && option(run, "o2").to < 30);
for (const key of ["co2", "he"]) {
  assert.equal(option(run, key).reaches, false, key + " is not enough alone");
  assert.equal(option(run, key).to, byKey[key].data_max, key + " is taken to the most FLEX tested");
  assert.ok(option(run, key).e.keep >= goal);
}
assert.equal(run.result.options[0].key, "o2", "a change that gets there is listed before the ones that do not");

// 3. Methanol: carbon dioxide's direction is not settled for this fuel, so it is not offered.
run = plan("methanol", { o2: 30, p: 0.694 });
assert.ok(M.meta.unsure.methanol.includes("co2"));
assert.equal(option(run, "co2"), undefined);
assert.deepEqual(run.result.left.filter(x => x.key === "co2").map(x => x.why), ["unsure"]);
assert.ok(option(run, "o2").reaches);

// 4. No test mixed carbon dioxide and helium: with one in the air the other is not offered.
run = plan("heptane", { he: 10 });
assert.equal(option(run, "co2"), undefined);
assert.deepEqual(JSON.parse(JSON.stringify(run.result.left.find(x => x.key === "co2"))), { key: "co2", why: "never-mixed", other: "he" });
assert.ok(option(run, "he").to > 10);

// 5. Already under the watch level, and outside the tested range: nothing to offer, and it says which.
run = plan("methanol", {});
assert.ok(run.result.already && run.result.now.keep < goal);
run = plan("heptane", { o2: 38 });
assert.equal(run.result.now.level, "outside");
assert.equal(run.result.options.length, 0);
assert.equal(run.result.already, false);

// 6. The sentence about nearby tests follows the counts.
const say = near => advisor.support({ near });
assert.match(say({ n: 0, out: 0, done: 0, other: 0 }).text, /No real test is close/);
assert.match(say({ n: 3, out: 0, done: 0, other: 3 }).text, /All ended in disruption/);
assert.match(say({ n: 1, out: 1, done: 0, other: 0 }).text, /it went out/);
assert.match(say({ n: 13, out: 7, done: 3, other: 3 }).text, /7 of 10 with a clear outcome went out/);
assert.match(say({ n: 4, out: 1, done: 3, other: 0 }).text, /only 1 of 4 .* Trust the tests/);
assert.ok(say({ n: 4, out: 1, done: 3, other: 0 }).rank < say({ n: 13, out: 7, done: 3, other: 3 }).rank);

console.log("PASS: the smallest single change of oxygen, carbon dioxide or helium that takes the reading under the watch level; "
  + "tested-range limits, gases never mixed, unsettled directions, and the wording about nearby tests.");
