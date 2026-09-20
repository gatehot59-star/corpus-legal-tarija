/* tests/browser_discovery.cjs: real Chromium protected discovery and download. */
"use strict";
const {chromium} = require("playwright");
const {spawn, spawnSync} = require("node:child_process");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const assert = require("node:assert/strict");
const readline = require("node:readline");
const root = path.resolve(__dirname,"..");
const temporary = fs.mkdtempSync(path.join(os.tmpdir(),"corpus-discovery-browser-"));
const directory = path.join(temporary,"fixture");
const cli = path.join(root,"sistema/api/demo_discovery.py");
const checks = [];
let server, browser, stderr = "";
function check(name, condition) {
  checks.push({name,pass:Boolean(condition)});
  assert.ok(condition,name);
}
function sql(statement) {
  const r = spawnSync("python3",["-c",
    "import sqlite3,sys;from contextlib import closing\nwith closing(sqlite3.connect(sys.argv[1])) as d,d:d.execute(sys.argv[2])",
    path.join(directory,"sessions.db"),statement],{encoding:"utf8"});
  assert.equal(r.status,0,r.stderr);
}
async function click(page,id) {
  await page.locator("#"+id).click();
  await page.waitForFunction(()=>!document.querySelector("#status").textContent.includes("Esperando"));
}
async function main() {
  const initialized = spawnSync("python3",[cli,"init","--isolated-demo","--directory",directory],{encoding:"utf8"});
  assert.equal(initialized.status,0,initialized.stderr);
  server = spawn("python3",[cli,"serve","--isolated-demo","--directory",directory],{stdio:["ignore","pipe","pipe"]});
  server.stderr.on("data",d=>stderr+=d);
  const ready = await new Promise((resolve,reject)=>{
    const timer=setTimeout(()=>reject(new Error("ready timeout")),10000);
    const lines=readline.createInterface({input:server.stdout});
    lines.once("line",line=>{clearTimeout(timer);lines.close();resolve(JSON.parse(line));});
    server.once("error",reject);
  });
  browser = await chromium.launch({headless:true,args:["--no-sandbox"]});
  const page = await browser.newPage({acceptDownloads:true});
  const failures=[];
  page.on("pageerror",e=>failures.push(String(e)));
  await page.goto(ready.url);
  check("anonymous_no_results",await page.locator("#results button").count()===0);
  check("anonymous_search_disabled",await page.locator("#search").isDisabled());
  await click(page,"login");await click(page,"search");
  check("ana_only_two_results",await page.locator("#results button").count()===2);
  check("ana_no_ben_text",!(await page.locator("#results").textContent()).includes("reservado a Ben"));
  check("hostile_snippet_inert",await page.locator("#results img").count()===0 &&
    (await page.locator("#results").textContent()).includes("<img"));
  await page.locator("#results button").first().click();await click(page,"read");
  const expected="DEMO A: derechos ficticios\r\nArtículo único: Ñ, ⚖, e\u0301 y 😀. Straße.\r\n";
  check("exact_unicode_crlf_astral",await page.locator("#text").textContent()===expected);
  const downloadPromise=page.waitForEvent("download");
  await click(page,"save");
  const download=await downloadPromise;
  const data=JSON.parse(fs.readFileSync(await download.path(),"utf8"));
  check("download_actual_json_allowlist",Object.keys(data).sort().join() ===
    ["schema","environment","uid","version","text_sha256","source_sha256","source_url","source_url_scope","hash_scope","authority","oficial","legal_validity","total_characters","retrieved_at","permission_checked_at","warnings"].sort().join());
  check("download_no_text_or_credentials",!JSON.stringify(data).includes("access_token") &&
    !JSON.stringify(data).includes("solo-demo-ficticia") && !JSON.stringify(data).includes("Artículo único"));
  check("distinct_source_text_hash",data.source_sha256==="a".repeat(64)&&data.source_sha256!==data.text_sha256);
  check("download_pins_selected_version",download.suggestedFilename()===`corpus-${data.uid}-${data.version}.reference.json`);
  await click(page,"logout");
  check("logout_clears_everything",await page.locator("#results button").count()===0 &&
    await page.locator("#text").textContent()==="" && await page.locator("#save").isDisabled());
  await page.locator("#identity").selectOption("ben");await click(page,"login");await click(page,"search");
  check("ben_only_own_collection",(await page.locator("#results").textContent()).includes("reservado a Ben") &&
    !(await page.locator("#results").textContent()).includes("DEMO A"));
  await click(page,"logout");
  await page.locator("#identity").selectOption("ana");await click(page,"login");await click(page,"search");
  sql("UPDATE access_documents SET withdrawn_at=1 WHERE uid='fixture-a1'");
  await page.locator("#results button").first().click();await click(page,"read");
  check("revoked_after_results_clears",await page.locator("#text").textContent()==="" &&
    await page.locator("#results button").count()===0 && await page.locator("#save").isDisabled());
  sql("UPDATE access_documents SET withdrawn_at=NULL");
  await click(page,"login");await click(page,"search");
  await page.locator("#results button").first().click();
  let pages=0;
  await page.route("**/api/v2/documento/**",async route=>{
    if (++pages===2) sql("UPDATE access_documents SET withdrawn_at=1 WHERE uid='fixture-a1'");
    await route.continue();
  });
  await click(page,"read");await page.unroute("**/api/v2/documento/**");
  check("revoked_between_pages_no_partial",pages>=2&&await page.locator("#text").textContent()==="" &&
    await page.locator("#save").isDisabled());
  sql("UPDATE access_documents SET withdrawn_at=NULL");
  await click(page,"login");await click(page,"search");
  await page.locator("#results button").first().click();await click(page,"read");
  let downloads=0;page.on("download",()=>downloads++);
  sql("UPDATE access_documents SET withdrawn_at=1 WHERE uid='fixture-a1'");
  await click(page,"save");
  check("revoked_before_save_no_download",downloads===0&&await page.locator("#save").isDisabled() &&
    await page.locator("#text").textContent()==="");
  await page.reload();
  check("reload_forgets_token_and_reference",await page.locator("#search").isDisabled() &&
    await page.locator("#save").isDisabled() && await page.locator("#results button").count()===0);
  await page.setViewportSize({width:390,height:844});
  check("mobile_no_horizontal_overflow",await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
  check("no_browser_errors",failures.length===0);
  console.log(JSON.stringify({browser:browser.version(),checks},null,2));
}
main().catch(error=>{
  console.error(JSON.stringify({error:String(error),stack:error.stack,checks,stderr},null,2));
  process.exitCode=1;
}).finally(async()=>{
  if(browser) await browser.close();
  if(server && server.exitCode===null) {
    server.kill("SIGTERM");
    await new Promise((resolve,reject)=>{
      const timer=setTimeout(()=>reject(new Error("server did not stop")),5000);
      server.once("exit",code=>{clearTimeout(timer);if(code!==0)reject(new Error("server exit "+code));else resolve();});
    });
  }
  fs.rmSync(temporary,{recursive:true,force:true});
});
