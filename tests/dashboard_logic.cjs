// Dependency-free logic regression harness. This is not a browser or layout test.
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const html=fs.readFileSync('dashboard/index.html','utf8');
const payload=html.match(/<script id="telemetry" type="application\/json">([\s\S]*?)<\/script>/)[1];
const code=html.match(/<script>\n([\s\S]*?)<\/script>/)[1];
const elements=new Map();
function element(id){if(!elements.has(id))elements.set(id,{value:'',innerHTML:'',textContent:'',add(){},classList:{toggle(){}},setAttribute(){}});return elements.get(id)}
element('telemetry').textContent=payload;
const context={console,Intl,Date,JSON,Number,String,Set,Map,Math,Object,Option:function(){},setTimeout(){},URL:{},Blob:function(){},
 document:{getElementById:element,querySelectorAll(){return []}}};
vm.createContext(context);vm.runInContext(code,context);
const run=s=>vm.runInContext(s,context);
assert.equal(run('filtered.length'),1200);
assert.match(run('overview()'),/97\.1%/);
assert.match(run('overview()'),/84\.3%/);
assert.equal(run('recovery().failed.length'),263);
assert.equal(run('recovery().recovered.length'),227);
for(const name of ['overview','errors','prompts','outcomes','memory','traces'])assert.ok(run(`${name}()`).length>200,name);
run("$('task').value='order_status';$('version').value='v1.1';render()");
assert.ok(run('filtered.length')>0&&run('filtered.length')<1200);
assert.ok(run("filtered.every(s=>s.task_type==='order_status'&&s.prompt_version==='v1.1')"));
run("$('from').value='2030-01-01';render()");assert.equal(run('filtered.length'),0);
assert.match(element('view').innerHTML,/No sessions match/);
run('reset()');assert.equal(run('filtered.length'),1200);
run("$('session').value='session-00001';renderTrace()");
assert.match(element('trace').innerHTML,/user input/);
assert.match(element('trace').innerHTML,/user action/);
assert.equal(run("esc('<script>')"),'&lt;script&gt;');
assert.equal(run('quantile([1,2,3,4],.95)'),3.8499999999999996);
assert.equal(run('pct(1,0)'),'—');
console.log('PASS: six view render functions, metric values, recovery denominators, combined filters, empty state, reset, trace content, escaping and percentile logic. Browser layout not tested.');
