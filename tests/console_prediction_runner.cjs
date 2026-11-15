// Execute the actual pure inference functions from console/index.html, not a copy.
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
const html = fs.readFileSync(path.join(root, 'console/index.html'), 'utf8');
const start = html.indexOf('  function linear(part, fuel, values) {');
const end = html.indexOf('  function predict() {', start);
if (start < 0 || end < 0) throw Error('Inference extraction anchors changed; review runner.');
const context = vm.createContext({window: {}});
vm.runInContext(fs.readFileSync(path.join(root, 'console/model.js'), 'utf8'), context, {timeout: 2000});
vm.runInContext('const M = window.FLAME_MODEL;\n' + html.slice(start, end), context, {timeout: 2000});
const cases = JSON.parse(fs.readFileSync(0, 'utf8'));
context.cases = cases;
const predictions = vm.runInContext(`cases.map(c => ({...predictFor(c.fuel,c.values),
  rawK: linear(M.burn_rate,c.fuel,c.values)}))`, context, {timeout: 10000});
process.stdout.write(JSON.stringify({model: context.window.FLAME_MODEL, predictions}));
