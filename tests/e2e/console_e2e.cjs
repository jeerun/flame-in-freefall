/* Actual browser UI tests. Never call app setters or predict() as the oracle. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const http = require('node:http');
const crypto = require('node:crypto');
const {pathToFileURL} = require('node:url');
// E2E_PLAYWRIGHT_PATH: folder of a Playwright package to use instead of one installed with npm, for
// example the copy inside Python's playwright package (<site-packages>/playwright/driver/package).
const playwrightFrom = process.env.E2E_PLAYWRIGHT_PATH ? path.resolve(process.env.E2E_PLAYWRIGHT_PATH) : null;
const {chromium} = require(playwrightFrom || 'playwright');
const playwrightVersion = require(playwrightFrom ? path.join(playwrightFrom,'package.json') : 'playwright/package.json').version;
const root = path.resolve(__dirname, '../..');
const web = path.join(root, 'console');
const output = process.env.E2E_OUTPUT_DIR ? path.resolve(process.env.E2E_OUTPUT_DIR) : path.join(__dirname, 'results');
const source = fs.readFileSync(path.join(web,'model.js'),'utf8');
const match = source.match(/window\.FLAME_MODEL\s*=\s*([\s\S]*);\s*$/);
assert.ok(match, 'Export format changed; review model parser');
const model = JSON.parse(match[1]);
assert.equal(model.meta.mock, false);
const defaults = Object.fromEntries(model.features.map(f=>[f.key,f.default]));
const reports = [];
fs.mkdirSync(output,{recursive:true});
const mime={'.html':'text/html; charset=utf-8','.js':'text/javascript; charset=utf-8','.css':'text/css'};
const server=http.createServer((req,res)=>{
  const relative=decodeURIComponent(new URL(req.url,'http://localhost').pathname).replace(/^\/+/, '') || 'index.html';
  const target=path.resolve(web,relative);
  if(!target.startsWith(web+path.sep)){res.writeHead(403).end(); return;}
  if(!fs.existsSync(target)||!fs.statSync(target).isFile()){res.writeHead(404).end(); return;}
  res.writeHead(200,{'Content-Type':mime[path.extname(target)]||'application/octet-stream'});
  fs.createReadStream(target).pipe(res);
});
// The export's formula, written out here on purpose: intercept + fuel + sum((coef + this fuel's own coef) * value).
// An export of the earlier one-slope model has no "fuel_coef", and then nothing is added.
function linear(part,fuel,values){
  const own=(part.fuel_coef&&part.fuel_coef[fuel])||{};
  return part.intercept+part.fuel[fuel]+Object.entries(part.coef).reduce((sum,[key,c])=>sum+(c+(own[key]||0))*values[key],0);
}
// The model's own chance of burning all the fuel, in percent, before any rounding.
function rawKeep(fuel,values){return 100*(1-1/(1+Math.exp(-linear(model.extinction,fuel,values))));}
function expected(fuel,values){
  // The page shows no chance below 1 % or above 99 %: the tests cannot support more certainty than that.
  const keep=Math.min(99,Math.max(1,Math.round(rawKeep(fuel,values))));
  return {keep, K:Math.max(0,linear(model.burn_rate,fuel,values)).toFixed(2)};
}
async function assertDisplay(page,fuel,values){
  // Read-only test hook checks the unrounded values received by the model.
  const state=await page.evaluate(()=>({fuel:window.__flame.state.fuel,values:window.__flame.state.values}));
  assert.equal(state.fuel,fuel);
  for(const [key,value] of Object.entries(values)) assert.ok(Math.abs(state.values[key]-value)<1e-9,`${key}: ${state.values[key]} != ${value}`);
  const e=expected(fuel,values);
  assert.equal((await page.locator('#pKeep').innerText()).trim(),String(e.keep));
  assert.equal((await page.locator('#pOut').innerText()).trim(),String(100-e.keep));
  assert.equal((await page.locator('#kVal').innerText()).trim(),e.K);
  assert.match(await page.locator('#meter').getAttribute('aria-label'),new RegExp(`fuel is gone: ${e.keep} percent`));
}
async function reset(page){
  await page.locator('body').click({position:{x:5,y:100}});
  await page.keyboard.press('r');
}
async function setSlider(page,key,value){
  const f=model.features.find(f=>f.key===key);
  const slider=page.getByRole('slider',{name:f.label+' in '+f.unit,exact:true});
  // Native range input plus bubbling event; app state is never set directly.
  await slider.evaluate((el,v)=>{el.value=String(v);el.dispatchEvent(new Event('input',{bubbles:true}));},value);
}
async function runCase(page,name,fn){
  try{await fn();reports.push({name,passed:true});}
  catch(error){
    const file=name.replace(/[^a-zA-Z0-9_-]/g,'_')+'.png';
    await page.screenshot({path:path.join(output,file),fullPage:true}).catch(()=>{});
    reports.push({name,passed:false,error:error.stack,screenshot:file});
  }
}
(async()=>{
 let browser;
 try{
  await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
  browser=await chromium.launch({headless:true,...(process.env.E2E_BROWSER_PATH?{executablePath:process.env.E2E_BROWSER_PATH}:{})});
  const url=`http://127.0.0.1:${server.address().port}/index.html#notitle`;
  for(const height of [680,800]){
   const context=await browser.newContext({viewport:{width:1280,height},reducedMotion:'reduce'});
   const page=await context.newPage();
   const errors=[];page.on('pageerror',e=>errors.push(e.message));
   await page.goto(url);await page.waitForFunction(()=>!!window.__flame);
   await page.locator('#tabConsole').click();
   const label=n=>`${height}_${n}`;
   await runCase(page,label('default_and_real_model'),async()=>{
    await assertDisplay(page,'heptane',defaults);
    assert.equal(await page.locator('#mockChip').isVisible(),false);
    assert.match(await page.locator('#srcChip').innerText(),/NASA PSI-69 FLEX/);
   });
   for(const [key,value] of Object.entries({o2:26,p:.85,co2:10,he:10,d0:4})){
    await runCase(page,label('slider_'+key),async()=>{await reset(page);await setSlider(page,key,value);await assertDisplay(page,'heptane',{...defaults,[key]:value});});
   }
   await runCase(page,label('fuel_switch'),async()=>{
    await reset(page);await page.locator('[data-fuel="methanol"]').click();await assertDisplay(page,'methanol',defaults);
    await page.locator('[data-fuel="heptane"]').click();await assertDisplay(page,'heptane',defaults);
   });
   await runCase(page,label('raise_lower_buttons'),async()=>{
    await reset(page);await page.getByRole('button',{name:'Raise Oxygen',exact:true}).click();
    await assertDisplay(page,'heptane',{...defaults,o2:21.5});
    await page.getByRole('button',{name:'Lower Oxygen',exact:true}).click();await assertDisplay(page,'heptane',defaults);
   });
   await runCase(page,label('negative_rate_clamp'),async()=>{
    const corner=[];
    for(const fuel of model.fuels.map(f=>f.key)) for(let bits=0;bits<(1<<model.features.length);bits++){
     const values=Object.fromEntries(model.features.map((f,i)=>[f.key,(bits&(1<<i))?f.max:f.min]));
     if(linear(model.burn_rate,fuel,values)<0)corner.push({fuel,values});
    }
    assert.ok(corner.length,'No negative-rate fixture within current sliders; review test coverage');
    const c=corner[0];await reset(page);
    await page.locator(`[data-fuel="${c.fuel}"]`).click();
    for(const [key,value] of Object.entries(c.values))await setSlider(page,key,value);
    await assertDisplay(page,c.fuel,c.values);
    assert.equal((await page.locator('#kVal').innerText()).trim(),'0.00');
   });
   await runCase(page,label('display_limits_1_and_99'),async()=>{
    // Upper limit, inside the tested range: heptane in Moon Base air, where the model's own number is above 99.5 %.
    const moon={...defaults,o2:30,p:.694,co2:0,he:0};
    assert.ok(rawKeep('heptane',moon)>=99.5,'Moon Base fixture is no longer above 99.5 %; pick another');
    await reset(page);await page.locator('[data-preset="moon"]').click();
    await assertDisplay(page,'heptane',moon);
    assert.equal((await page.locator('#pKeep').innerText()).trim(),'99');
    assert.equal((await page.locator('#pOut').innerText()).trim(),'1');
    // Lower limit: the first fuel and single slider end where the model's own number is below 0.5 %.
    const low=[];
    for(const fuel of model.fuels.map(f=>f.key)) for(const f of model.features) for(const end of [f.min,f.max]){
     const values={...defaults,[f.key]:end};
     if(rawKeep(fuel,values)<0.5)low.push({fuel,key:f.key,end,values});
    }
    assert.ok(low.length,'No fixture below 0.5 % with one slider at its end; review test coverage');
    const c=low[0];await reset(page);
    await page.locator(`[data-fuel="${c.fuel}"]`).click();await setSlider(page,c.key,c.end);
    await assertDisplay(page,c.fuel,c.values);
    assert.equal((await page.locator('#pKeep').innerText()).trim(),'1');
    assert.equal((await page.locator('#pOut').innerText()).trim(),'99');
   });
   await runCase(page,label('reset_after_changes'),async()=>{
    await setSlider(page,'d0',4);await setSlider(page,'o2',26);await page.locator('[data-fuel="methanol"]').click();
    await reset(page);await assertDisplay(page,'heptane',defaults);
   });
   for(const [preset,values] of Object.entries({earth:{o2:21,p:1,co2:0,he:0},moon:{o2:30,p:.694,co2:0,he:0},mars:{o2:30,p:.694,co2:0,he:0}})){
    await runCase(page,label('preset_'+preset),async()=>{
     await reset(page);await setSlider(page,'d0',4);await setSlider(page,'co2',10);
     await page.locator(`[data-preset="${preset}"]`).click();
     await assertDisplay(page,'heptane',{...defaults,d0:4,...values});
     assert.equal(await page.locator(`[data-preset="${preset}"]`).getAttribute('aria-pressed'),'true');
    });
   }
   await runCase(page,label('outside_pressure_warning'),async()=>{
    await reset(page);await setSlider(page,'p',1.5);
    assert.match(await page.locator('#confTitle').innerText(),/Outside the tested range/);
    assert.match(await page.locator('#read').getAttribute('class'),/untrusted/);
    await assertDisplay(page,'heptane',{...defaults,p:1.5});
   });
   await runCase(page,label('exclusive_gases_warning'),async()=>{
    await reset(page);await setSlider(page,'co2',10);await setSlider(page,'he',10);
    assert.match(await page.locator('#rows').innerText(),/never tested together/);
    assert.match(await page.locator('#confTitle').innerText(),/Outside the tested range/);
   });
   await runCase(page,label('gas_total_warning'),async()=>{
    await reset(page);await setSlider(page,'o2',40);await setSlider(page,'co2',60);await setSlider(page,'he',55);
    // Gas total warning is displayed in the confidence panel, not the settings rows.
    // The three selected gases total 155%; their combined fraction is invalid.
    const confidenceText = await page.locator('#confText').innerText();
    assert.match(confidenceText, /add up to\s*155(?:\.0)?\s*%,\s*more than 100\s*%/i);
    assert.match(await page.locator('#conf').getAttribute('class'), /\boutside\b/);
    assert.match(await page.locator('#read').getAttribute('class'),/untrusted/);
   });
   await runCase(page,label('pressure_gap_existing_warning'),async()=>{
    await reset(page);await setSlider(page,'p',.85);
    assert.match(await page.locator('#confTitle').innerText(),/Far from any real test/);
   });
   await runCase(page,label('layout_and_page_errors'),async()=>{
    await reset(page);
    const dims=await page.evaluate(()=>({w:document.documentElement.scrollWidth,h:document.documentElement.scrollHeight,iw:innerWidth,ih:innerHeight}));
    assert.ok(dims.w<=dims.iw+1&&dims.h<=dims.ih+1,JSON.stringify(dims));
    for(const selector of ['#pKeep','#pOut','#kVal','#presets']) assert.equal(await page.locator(selector).isVisible(),true);
    assert.deepEqual(errors,[]);
   });
   await context.close();
  }
  // Offline file mode: no local server or AI service required.
  for(const mock of [false,true]){
   const context=await browser.newContext({viewport:{width:1280,height:800},reducedMotion:'reduce'});
   const page=await context.newPage();const errors=[];page.on('pageerror',e=>errors.push(e.message));
   if(mock) await page.route('**/model.js',route=>route.abort());
   await page.goto(pathToFileURL(path.join(web,'index.html')).href+'#notitle');
   await page.waitForFunction(()=>!!window.__flame);await page.locator('#tabConsole').click();
   await runCase(page,mock?'file_missing_model_fallback':'file_real_model',async()=>{
    assert.equal(await page.locator('#mockChip').isVisible(),mock);
    if(mock){assert.match(await page.locator('#mockText').innerText(),/Mock numbers/);assert.equal(await page.locator('#srcChip').isVisible(),false);}
    else await assertDisplay(page,'heptane',defaults);
    assert.deepEqual(errors,[]);
   });
   await context.close();
  }
 }catch(error){reports.push({name:'harness_setup',passed:false,error:error.stack});}
 finally{
  const browserVersion=browser?browser.version():null;
  if(browser)await browser.close();await new Promise(resolve=>server.close(resolve));
  const hashes=Object.fromEntries(['index.html','model.js','research.js','tables.js'].filter(f=>fs.existsSync(path.join(web,f))).map(f=>[f,crypto.createHash('sha256').update(fs.readFileSync(path.join(web,f))).digest('hex')]));
  const report={passed:reports.length>0&&reports.every(r=>r.passed),plannedTests:40,tests:reports.length,passedTests:reports.filter(r=>r.passed).length,browser:browserVersion,playwright:playwrightVersion,source_sha256:hashes,results:reports,limitations:['Local Chromium only; not live hosting, real gamepad, or real handheld hardware.','Range inputs use native DOM input events; button/reset/preset interactions use browser clicks and keyboard.','Checks current UI behavior; does not validate scientific warning policy or model accuracy.','Read-only __flame.state hook verifies unrounded model inputs; no application setters or predict functions are called.']};
  fs.writeFileSync(path.join(output,'console_e2e_report.json'),JSON.stringify(report,null,2)+'\n');
  console.log(JSON.stringify(report,null,2));process.exitCode=report.passed?0:1;
 }
})();
