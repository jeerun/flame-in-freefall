// Lightweight DOM tests of the actual UI functions. Run: node tests/test_console_features.cjs
const fs = require('node:fs'), vm = require('node:vm'), assert = require('node:assert/strict'), path = require('node:path');
const root = path.resolve(__dirname, '..');
const html = fs.readFileSync(path.join(root, 'console/index.html'), 'utf8');
function source(name) {
  const start = html.indexOf('  function ' + name + '('); assert.ok(start >= 0, name);
  const lineEnd = html.indexOf('\n', start), line = html.slice(start, lineEnd);
  return line.trimEnd().endsWith('}') ? line : html.slice(start, html.indexOf('\n  }', start) + 4);
}
class Node {
  constructor(tag='div') { this.tagName=tag.toUpperCase(); this.children=[]; this._text=''; this.hidden=false; this.open=false; }
  appendChild(n) { this.children.push(n); return n; }
  set textContent(s) { this._text=String(s); this.children=[]; }
  get textContent() { return this._text + this.children.map(n=>n.textContent).join(''); }
  set innerHTML(s) { assert.equal(s,'');this._text='';this.children=[]; }
}
const nodes = {};
for(const m of html.matchAll(/id="([^"]+)"/g)) { assert.ok(!nodes[m[1]], 'duplicate ID '+m[1]);nodes[m[1]]=new Node(); }
const document={getElementById:id=>{assert.ok(nodes[id],'missing element '+id);return nodes[id]},createElement:t=>new Node(t),createTextNode:t=>{const n=new Node('#text');n.textContent=t;return n}};
const c=vm.createContext({window:{},document,console});
vm.runInContext(fs.readFileSync(path.join(root,'console/model.js'),'utf8'),c);
vm.runInContext(`var M=window.FLAME_MODEL, $=id=>document.getElementById(id), state={fuel:'heptane',values:{},baseline:null,sheet:false,comparing:false},last,MAP={big:false};
var WATCH=(M.meta&&M.meta.watch)||0.35;
var byKey={}, hasTests=true, TEST_COL={o2:3,p:4,co2:5,he:6,d0:7};M.features.forEach(f=>{byKey[f.key]=f;state.values[f.key]=f.default});var GAS=['o2','co2','he'];
var SHORT={o2:' oxygen',co2:' carbon dioxide',he:' helium',p:'',d0:' droplet'}; var preset=null;function activePreset(){return preset} function mapBig(x){MAP.big=x} var sfx={close(){}};
`,c);
for(const name of ['el','shown','linear','predictFor','predict','nearest','rangeCheck','drivers','fmt','names','at','fuelLabel','trim','gasNames','testSettings','testEnd','outsideReasons','readingSummary','renderSheet','comparisonSnapshot','saveBaseline','clearBaseline','toggleComparison','renderComparison','toggleExplanationDetail','reset']) vm.runInContext(source(name),c);
vm.runInContext(`function render(){var r=predict(),rc=rangeCheck();last={r:r,rc:rc};$('confTitle').textContent=rc.level==='outside'?'Outside the tested range':rc.near.far?'Far from any real test':'Inside the tested range';renderComparison();} render();`,c);
const run=s=>vm.runInContext(s,c);
run('saveBaseline()');const saved=run('JSON.stringify(state.baseline)');
assert.equal(run('state.comparing'),true);assert.equal(run('state.baseline.values.o2'),21);
run('state.values.o2=30;render()');assert.equal(run('JSON.stringify(state.baseline)'),saved,'baseline must remain immutable');
assert.match(nodes.compareRows.textContent,/\+.*pp vs A/);assert.ok(nodes.compareRows.children.some(n=>n.className==='changed'));
run('state.values.co2=5;state.values.he=5;render()');assert.match(nodes.compareRows.textContent,/Delta withheld/);assert.match(nodes.compareWarnings.textContent,/never|No experiment/);
run('saveBaseline();state.values.co2=0;state.values.he=0;render()');assert.match(nodes.compareRows.textContent,/Delta withheld/,'unsupported baseline still blocks delta');assert.match(nodes.compareWarnings.children[0].textContent,/unsupported extrapolations/);
const beforeReset=run('JSON.stringify(state.baseline)');run('reset()');assert.equal(run('JSON.stringify(state.baseline)'),beforeReset,'reset keeps baseline');
run('state.fuel="methanol";render()');assert.match(nodes.compareRows.textContent,/Methanol/);
run('saveBaseline()');assert.equal(run('state.baseline.fuel'),'methanol');
run('clearBaseline()');assert.equal(run('state.baseline'),null);assert.equal(nodes.openCompare.disabled,true);assert.equal(nodes.compareSheet.hidden,true);
run('reset();renderSheet(last.r,last.rc)');assert.match(nodes.summaryPrediction.textContent,/57% completion/);
// The range from refits on resampled tests, the chance of a disruption, and how much of the droplet was gone when nearby flames went out.
assert.match(nodes.summaryPrediction.textContent,/falls between (\d+)% and (\d+)%\./);
{const [,lo,hi]=nodes.summaryPrediction.textContent.match(/falls between (\d+)% and (\d+)%/);assert.ok(+lo<57&&57<+hi,'the reading sits inside its range');assert.ok(+hi-+lo>=20,'199 tests leave a wide range');}
assert.match(nodes.summaryPrediction.textContent,/disrupted instead, with no clear outcome: \d+%\./);
assert.match(nodes.summaryEvidence.textContent,/lost a median of \d+% of its volume/);
assert.match(nodes.sheetFine.textContent,/refits on resampled tests/);assert.match(nodes.sheetFine.textContent,/chance of a disruption/);
assert.doesNotMatch(nodes.summaryLimits.textContent,/at least a 50% chance of disruption/);
// On the settings of a real test whose flame went out, the test list says how much of the droplet was gone by then.
run(`var te=M.tests.find(t=>t[2]==='heptane'&&t[8]==='Extinction'&&t[11]!=null&&t[11]<=t[7]);reset();
  state.values.o2=te[3];state.values.p=te[4];state.values.co2=te[5];state.values.he=te[6];state.values.d0=te[7];render();renderSheet(last.r,last.rc)`);
assert.match(nodes.testList.textContent,/Went out before the fuel was gone\. By then the droplet had lost about \d+% of its volume\./);
run('reset();renderSheet(last.r,last.rc)');
assert.ok(nodes.sheetList.children.length);assert.ok(nodes.testList.children.length);assert.match(nodes.sheetFine.textContent,/AUC/);
// With the per-fuel model: the page never shows 100 %, and it says when the tests do not settle which way a setting pushes.
run('reset();state.values.o2=30;state.values.p=.694;render();renderSheet(last.r,last.rc)');assert.match(nodes.summaryPrediction.textContent,/clear outcome.*99% completion and 1% visible extinction/);
// In Moon Base air nearly every heptane test was recorded as a disruption: the page must say so next to the 99 %.
assert.ok(run('last.r.pDis')>0.9);assert.match(nodes.summaryPrediction.textContent,/disrupted instead, with no clear outcome: 9\d%\./);
assert.match(nodes.summaryLimits.textContent,/model estimates at least a 50% chance of disruption/);
run('saveBaseline();state.values.o2=16;render()');
const disRow=nodes.compareRows.children.find(row=>row.children[0].textContent==='Disruption chance');
assert.match(disRow.children[1].textContent,/^9\d%$/);assert.match(disRow.children[2].textContent,/^\d+%-\d+ pp vs A$/);assert.equal(disRow.className,'changed');
run('clearBaseline();reset();state.values.o2=30;state.values.p=.694;render();renderSheet(last.r,last.rc)');
run('saveBaseline();state.values.o2=31;render()');
const capped=nodes.compareRows.children.find(row=>row.children[0].textContent==='Burns to completion');
assert.equal(capped.children[1].textContent,'99%');assert.match(capped.children[2].textContent,/99%0 pp vs A/);
assert.notEqual(capped.className,'changed');run('clearBaseline()');
run('reset();state.fuel="methanol";state.values.p=.7;render();renderSheet(last.r,last.rc)');assert.match(nodes.sheetList.textContent,/Pressure at 0\.70 atm[^.]*\. The tests do not settle which way this setting pushes for methanol/);
run('reset();state.values.o2=24;render();renderSheet(last.r,last.rc)');assert.doesNotMatch(nodes.sheetList.textContent,/do not settle/,'oxygen is a settled slope for heptane');
run('reset();renderSheet(last.r,last.rc)');
run('toggleExplanationDetail("whyDetails");renderSheet(last.r,last.rc)');assert.equal(nodes.whyDetails.open,true,'rerender preserves expanded state');
run('state.values.p=.694;state.values.o2=30;state.values.d0=3.2;preset={key:"mars"};render();renderSheet(last.r,last.rc)');assert.match(nodes.summaryLimits.textContent,/no clear flame outcome/);assert.match(nodes.summaryLimits.textContent,/assumed scenario/);
assert.equal(run('last.rc.noClear'),true);
assert.equal(run('last.rc.level'),'edge','nearby disruptions must give amber coverage');
assert.match(nodes.summaryPrediction.textContent,/clear outcome/);
run('state.values.co2=33;state.values.p=.94;preset=null;render();renderSheet(last.r,last.rc)');assert.match(nodes.summaryLimits.textContent,/no close experimental match/);
run('state.values.co2=60;state.values.he=55;render();renderSheet(last.r,last.rc)');assert.match(nodes.summaryPrediction.textContent,/Do not rely/);assert.match(nodes.summaryLimits.textContent,/more than 100/);
run('M.meta.mock=true;renderSheet(last.r,last.rc)');assert.match(nodes.summaryLimits.textContent,/Mock model/);
// An export without the third formula or the refits: neither sentence appears, nothing is made up.
run('var keptDis=M.disruption,keptDraws=M.extinction_draws;M.meta.mock=false;delete M.disruption;delete M.extinction_draws;reset();renderSheet(last.r,last.rc)');
assert.doesNotMatch(nodes.summaryPrediction.textContent,/disrupted instead|falls between/);assert.equal(run('last.r.pDis'),null);assert.equal(run('last.r.lo'),null);
run('M.disruption=keptDis;M.extinction_draws=keptDraws;M.meta.mock=true;reset()');
assert.ok(html.includes('#sheetList > li, #testList > li'),'Ember retains test evidence after regrouping');
for(const match of html.matchAll(/<script\b[^>]*>([\s\S]*?)<\/script>/g))new vm.Script(match[1]);
// Exercise the actual keyboard handler, including native disclosure activation.
let keyHandler;
document.addEventListener=(name,fn)=>{if(name==='keydown')keyHandler=fn;};
const keyStart=html.indexOf('  document.addEventListener("keydown", function (e) {');
vm.runInContext(html.slice(keyStart,html.indexOf('\n  });',keyStart)+6),c);
run('var titleOn=false,SIM={open:false},OX={open:false},AI={open:false},view={page:"console"}; function activeCasePanel(){return null;}');
function key(k,target='BODY',extra={}){keyHandler({key:k,target:{tagName:target},preventDefault(){},...extra});}
run('M.meta.mock=false;reset();clearBaseline()');key('h');assert.equal(run('state.comparing'),true);
key('Escape');assert.equal(run('state.comparing'),false);key('c');assert.equal(run('state.comparing'),true);
run('state.sheet=true;state.comparing=false');key('w');assert.equal(nodes.whyDetails.open,false);key('t');assert.equal(nodes.testDetails.open,true);
const fixed=run('JSON.stringify(state.baseline)');run('state.values.o2=28;render()');key('h','BODY',{ctrlKey:true});assert.equal(run('JSON.stringify(state.baseline)'),fixed,'Ctrl+H must not replace baseline');
key('Enter','SUMMARY'); // Browser owns native summary toggle; global handler must not close the sheet.
assert.equal(run('state.sheet'),true);
// FLEX 234 and 267 share the same position, and 234 is drawn last.
for (const name of ['starAt', 'pickStar', 'replayTest', 'say']) run(source(name));
nodes.map.getBoundingClientRect = () => ({left:0, top:0, width:100, height:100});
nodes.map.viewBox = {baseVal:{width:100, height:100}};
run(`var visible=M.tests.find(t=>t[0]===234), underneath=M.tests.find(t=>t[0]===267);
  MAP.stars=[{x:50,y:50,t:underneath},{x:50,y:50,t:visible}];
  MAP.plot={cx:50,cy:50,w:100,h:100};function selectStar(t){MAP.sel=t;}`);
assert.equal(run('starAt({clientX:50,clientY:50},10)[0]'),234);
run('pickStar(0,0)');assert.equal(run('MAP.sel[0]'),234);
run('function stopReplay(){}');
for (const id of [54,109]) assert.equal(run('replayTest(M.tests.find(t=>t[0]==='+id+'),null,null,false)'),false,'replay needs measured inputs for test '+id);
run(`var VOICE={on:true,spoken:0}, voices=[], spoken=[];
  var speechSynthesis=window.speechSynthesis={getVoices:()=>voices,cancel(){},speak(u){spoken.push(u.voice.name)}};
  var SpeechSynthesisUtterance=window.SpeechSynthesisUtterance=function(text){this.text=text};
  voices.push({name:"Aria",lang:"en-US",localService:false});say("remote only");`);
assert.equal(run('spoken.length'),0);
run('voices.push({name:"Local English",lang:"en-US",localService:true});say("local voice");');
assert.equal(run('spoken.join()'),'Local English');
console.log('PASS: baseline and displayed deltas, unsupported A/B warnings, per-fuel estimates and uncertainty, 1–99% display, the range from refits, the chance of a disruption, droplet volume lost at extinction, disclosures, FLEX stars and replay, Ember context and local speech.');
