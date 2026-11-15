// Versioned fragments for a selected PSI investigation or a FLEX console reading.
// The page checks each decoded selection against the data and slider limits it loaded.
(function () {
  "use strict";

  const prefix = "#view=v1&";
  const sliders = ["o2", "p", "co2", "he", "d0"];
  const researchFields = ["page", "need", "id", "orbit"];
  const consoleFields = ["page", "fuel", "values", "preset", "test"];
  const consoleParams = ["page", "fuel", ...sliders, "preset", "test"];

  function onlyFields(object, names) {
    return object !== null && typeof object === "object" && !Array.isArray(object) &&
      Object.keys(object).every(name => names.includes(name));
  }

  function key(value) {
    return typeof value === "string" && /^[a-z][a-z0-9_-]{0,39}$/.test(value);
  }

  function accession(value) {
    return typeof value === "string" && /^PSI-[1-9]\d{0,15}$/.test(value) &&
      Number.isSafeInteger(Number(value.slice(4)));
  }

  function validValue(n) {
    return Number.isFinite(n) && n >= 0;
  }

  function encode(view) {
    if (!view || !Object.hasOwn(view, "page")) return null;
    if (view.page === "research") {
      if (!onlyFields(view, researchFields) || !Object.hasOwn(view, "need") || !key(view.need) ||
          !Object.hasOwn(view, "id") || !accession(view.id) ||
          (Object.hasOwn(view, "orbit") && typeof view.orbit !== "boolean")) return null;
      return prefix + "page=research&need=" + view.need + "&id=" + view.id +
        (Object.hasOwn(view, "orbit") && view.orbit ? "&orbit=1" : "");
    }
    if (view.page !== "console" || !onlyFields(view, consoleFields) || !Object.hasOwn(view, "fuel") ||
        !key(view.fuel) || !Object.hasOwn(view, "values") || !onlyFields(view.values, sliders) ||
        !sliders.every(name => Object.hasOwn(view.values, name) && validValue(view.values[name]))) return null;
    const parts = ["page=console", "fuel=" + view.fuel];
    for (const name of sliders) {
      const value = view.values[name];
      parts.push(name + "=" + (Object.is(value, -0) ? "-0" : String(value)));
    }
    if (Object.hasOwn(view, "preset")) {
      if (!key(view.preset)) return null;
      parts.push("preset=" + view.preset);
    }
    if (Object.hasOwn(view, "test")) {
      if (!Number.isSafeInteger(view.test) || view.test < 1) return null;
      parts.push("test=" + view.test);
    }
    return prefix + parts.join("&");
  }

  function decode(hash) {
    if (typeof hash !== "string" || !hash.startsWith(prefix) || hash.length > 512) return null;
    const fields = Object.create(null);
    for (const part of hash.slice(prefix.length).split("&")) {
      const pair = /^([a-z][a-z0-9]*)=([A-Za-z0-9.+_-]+)$/.exec(part);
      if (!pair || Object.hasOwn(fields, pair[1])) return null;
      fields[pair[1]] = pair[2];
    }

    if (fields.page === "research") {
      if (!onlyFields(fields, researchFields) || !key(fields.need) || !accession(fields.id) ||
          (Object.hasOwn(fields, "orbit") && fields.orbit !== "0" && fields.orbit !== "1")) return null;
      return {page: "research", need: fields.need, id: fields.id, orbit: fields.orbit === "1"};
    }
    if (fields.page !== "console" || !onlyFields(fields, consoleParams) || !key(fields.fuel)) return null;
    const view = {page: "console", fuel: fields.fuel, values: {}};
    for (const name of sliders) {
      const source = fields[name];
      if (!source || !/^-?(?:0|[1-9]\d*)(?:\.\d+)?(?:e[+-]?\d+)?$/i.test(source)) return null;
      const value = Number(source);
      if (!validValue(value) || (value === 0 && /[1-9]/.test(source.split(/e/i)[0]))) return null;
      view.values[name] = value;
    }
    if (Object.hasOwn(fields, "preset")) {
      if (!key(fields.preset)) return null;
      view.preset = fields.preset;
    }
    if (Object.hasOwn(fields, "test")) {
      if (!/^[1-9]\d*$/.test(fields.test) || !Number.isSafeInteger(Number(fields.test))) return null;
      view.test = Number(fields.test);
    }
    return view;
  }

  window.FLAME_VIEW_LINK = {encode, decode};
}());
