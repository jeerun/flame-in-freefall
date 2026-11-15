// Print the digest of the CSV produced by this checkout; --csv emits its exact bytes.
// Re-run when changing the shipped model or the dashboard's CSV format.
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const { createHash } = require("node:crypto");

const consoleDir = path.join(__dirname, "..", "console");
const html = fs.readFileSync(path.join(consoleDir, "index.html"), "utf8");
const context = vm.createContext({ window: {} });
vm.runInContext(fs.readFileSync(path.join(consoleDir, "model.js"), "utf8"), context);
const columns = html.match(/^  var TEST_COL = [^;]+;/m);
if (!columns) throw Error("Cannot find the test column mapping in console/index.html");
const functions = ["linear", "predictFor", "drillValues", "testsCsv"].map(name => {
  const start = html.indexOf("  function " + name + "(");
  const end = html.indexOf("\n  }", start);
  if (start < 0 || end < 0) throw Error("Cannot find " + name + " in console/index.html");
  return html.slice(start, end + 4);
});
const code = ["const M = window.FLAME_MODEL;", columns[0], ...functions, "testsCsv()"].join("\n");
const csv = Buffer.from(vm.runInContext(code, context), "utf8");
process.stdout.write(process.argv.includes("--csv") ? csv : createHash("sha256").update(csv).digest("hex") + "\n");
