// Run directly with node tests/test_view_link.cjs.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const browser = {window: {}};
vm.runInNewContext(fs.readFileSync(path.join(__dirname, "../console/view-link.js"), "utf8"), browser);
const {encode, decode} = browser.window.FLAME_VIEW_LINK;
const read = hash => structuredClone(decode(hash));
const research = {page: "research", need: "detection", id: "PSI-101", orbit: true};
const values = {o2: 30, p: 0.694, co2: 0, he: 0, d0: 3};
const flame = {page: "console", fuel: "heptane", values};

assert.deepEqual(read(encode(research)), research);
assert.deepEqual(read(encode({page: "research", need: "cabin", id: "PSI-159"})),
  {page: "research", need: "cabin", id: "PSI-159", orbit: false});
assert.deepEqual(read(encode(flame)), flame);
const moon = {...flame, preset: "moon", test: 108};
const mars = {...flame, preset: "mars", test: 108};
assert.notEqual(encode(moon), encode(mars));
for (const view of [moon, mars]) assert.deepEqual(read(encode(view)), view);

// Real presets and replayed tests can have more precision than the visible slider.
for (const p of [0.694, 0.6925000000000001, Number.MIN_VALUE, Number.MAX_VALUE, -0]) {
  const view = {...flame, values: {...values, p}};
  assert.deepEqual(read(encode(view)), view);
}
assert.equal(read("#view=v1&need=cabin&page=research&id=PSI-69&orbit=0").orbit, false);
assert.equal(read(encode(flame).replace("o2=30", "o2=40")).values.o2, 40);

const base = encode(flame);
for (const bad of [
  null, "", "#title", "#anything", "#view=v2&page=console", "#view=v1&",
  base + "&", base + "&o2=21", base + "&test=12&test=13", base + "&orbit=1",
  base + "&mystery=data", base + "&preset=", base + "&test=0", base + "&test=4.5",
  base + "&test=9007199254740992", base + "&preset=earth%26test%3D12",
  base.replace("&he=0", ""), base.replace("fuel=heptane", "fuel=HEPTANE"),
  ...["NaN", "Infinity", "-1", "0x10", "2.0xyz", "1e999", "1e-999", "22%25", "2=5"].map(
    n => base.replace("o2=30", "o2=" + n)),
  encode(research) + "&fuel=heptane", encode(research).replace("orbit=1", "orbit=true"),
  encode(research).replace("PSI-101", "PSI-0"), encode(research).replace("&need=detection", ""),
]) assert.equal(decode(bad), null, String(bad));

for (const bad of [
  null, [], {}, {page: "drill"}, {...research, orbit: 1}, {...research, id: 101},
  {...research, id: "PSI-9007199254740992"}, {...flame, preset: null}, {...flame, test: "1"},
  {...flame, values: null}, {...flame, values: {...values, o2: -1}},
  {...flame, values: {...values, p: NaN}}, {...flame, values: {...values, co2: "0"}},
  {...flame, values: {...values, d0: Infinity}}, {...flame, values: {...values, extra: 0}},
  {...flame, values: {o2: 21}}, {...flame, id: "PSI-69"},
]) assert.equal(encode(bad), null);
console.log("PASS: view-link round trips, exact inputs, distinct presets, optional selections and malformed fragments.");
