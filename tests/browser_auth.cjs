/* Actual-browser spike acceptance. Requires external playwright@1.63.0. */
const assert = require("node:assert/strict");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const {spawn, spawnSync} = require("node:child_process");
const {once} = require("node:events");
const {createHash} = require("node:crypto");
const {chromium} = require("playwright");
const root = path.resolve(__dirname, "..");
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "corpus-browser-"));
const fixture = path.join(tmp, "fixture");
const cli = path.join(root, "sistema/api/demo_aislada.py");
const text = "DEMO FICTICIA, SIN VALOR JURIDICO\nArtículo único: Ñ, ⚖ y e\u0301.\r\n";
const version = createHash("sha256").update(text).digest("hex");
const results = [];
function check(name, condition) {results.push({name, pass:Boolean(condition)}); assert.ok(condition, name);}
function sql(statement) {
  const r = spawnSync("python3", ["-c", "import sqlite3,sys; c=sqlite3.connect(sys.argv[1]); c.execute(sys.argv[2]); c.commit(); c.close()", path.join(fixture,"sessions.db"), statement], {encoding:"utf8"});
  assert.equal(r.status,0,r.stderr);
}
async function main() {
  const init = spawnSync("python3",[cli,"init","--directory",fixture,"--isolated-demo"],{encoding:"utf8",timeout:15000});
  assert.equal(init.status,0,init.stderr);
  const server = spawn("python3",[cli,"serve","--directory",fixture,"--isolated-demo","--browser-spike"],{stdio:["ignore","pipe","pipe"]});
  let browser, context, stderr = "";
  server.stderr.on("data", b=>stderr+=b.toString());
  try {
    const ready = await new Promise((resolve,reject)=>{
      const timer=setTimeout(()=>reject(Error("CLI readiness timeout")),15000);
      let data="";
      server.stdout.on("data",b=>{data+=b.toString(); if(data.includes("\n")){clearTimeout(timer);try{resolve(JSON.parse(data.split("\n")[0]));}catch(e){reject(e);}}});
      server.once("exit",code=>{clearTimeout(timer);reject(Error("CLI exited "+code));});
    });
    browser=await chromium.launch({headless:true});
    context=await browser.newContext({viewport:{width:1000,height:850}});
    const page=await context.newPage();
    const errors=[]; page.on("pageerror",e=>errors.push(e.message));
    const origins=[];
    page.on("request",async r=>{if(new URL(r.url()).pathname==="/api/v2/login"){const h=await r.allHeaders();origins.push(h.origin);}});
    const response=await page.goto(ready.url);
    check("page_200",response.status()===200);
    check("no_credential_inputs",await page.locator("input").count()===0);
    check("anonymous_read_disabled",await page.locator("#read").isDisabled());
    check("anonymous_save_disabled",await page.locator("#save").isDisabled());
    const loginResponse=page.waitForResponse(r=>r.url().endsWith("/api/v2/login"));
    await page.locator("#login").click();
    const login=await loginResponse; check("browser_login_200",login.status()===200);
    const token=(await login.json()).access_token; // Never print or persist bearer.
    await page.waitForFunction(()=>document.getElementById("status").textContent.includes("iniciada"));
    check("real_browser_origin",origins[0]===ready.url);
    await page.locator("#read").click();
    await page.waitForFunction(()=>document.getElementById("status").textContent.includes("completo"));
    check("exact_unicode_crlf",await page.locator("#text").textContent()===text);
    check("empty_persistent_storage",await page.evaluate(()=>localStorage.length===0&&sessionStorage.length===0&&document.cookie===""));
    check("no_token_in_dom",!(await page.content()).includes(token));
    check("no_token_in_url",!page.url().includes(token));
    check("save_after_complete_read",await page.locator("#save").isEnabled());
    const downloads=[];page.on("download",d=>downloads.push(d));
    const downloadEvent=page.waitForEvent("download");
    await page.locator("#save").click();
    const download=await downloadEvent;
    const saved=JSON.parse(fs.readFileSync(await download.path(),"utf8"));
    const keys=["schema","environment","uid","version","text_sha256","source_sha256",
      "source_url","source_url_scope","hash_scope","authority","oficial","legal_validity",
      "total_characters","retrieved_at","permission_checked_at","warnings"].sort();
    check("reference_exact_allowlist",JSON.stringify(Object.keys(saved).sort())===JSON.stringify(keys));
    check("reference_version_and_provenance",saved.schema==="corpus-reference-v1"&&
      saved.environment==="isolated_test"&&saved.uid==="fixture-demo"&&saved.version===version&&
      saved.text_sha256===version&&/^[0-9a-f]{64}$/.test(saved.source_sha256)&&
      saved.source_url_scope==="current_document"&&saved.authority==="secondary"&&
      saved.oficial===false&&saved.legal_validity==="NOT_MEASURED"&&saved.hash_scope==="text_utf8"&&
      saved.total_characters===Array.from(text).length&&Number.isFinite(Date.parse(saved.retrieved_at))&&
      Number.isFinite(Date.parse(saved.permission_checked_at))&&saved.warnings.length===4);
    check("reference_contains_no_body_or_bearer",!JSON.stringify(saved).includes(token)&&
      !JSON.stringify(saved).includes("solo-demo-ficticia")&&!JSON.stringify(saved).includes("Artículo único"));
    check("reference_filename",download.suggestedFilename()==="corpus-fixture-demo-"+version+".reference.json");
    await page.waitForFunction(()=>document.getElementById("status").textContent.includes("descargada"));
    // A saved reference is not permission. Revoke AFTER reading, BEFORE saving.
    sql("UPDATE access_grants SET revoked_at=1");
    const beforeDenied=downloads.length;
    await page.locator("#save").click();
    await page.waitForFunction(()=>/HTTP 403|descargada/.test(document.getElementById("status").textContent));
    check("revoked_save_no_download",await page.locator("#save").isDisabled()&&
      await page.locator("#text").textContent()===""&&downloads.length===beforeDenied);
    sql("UPDATE access_grants SET revoked_at=NULL");
    // Changing current text version must not silently replace the pinned ledger version.
    const updateCandidate=spawnSync("python3",["-c",
      "import sqlite3,sys;c=sqlite3.connect(sys.argv[1]);c.execute('UPDATE documentos SET sha256=?',(sys.argv[2],));c.commit();c.close()",
      path.join(fixture,"candidate.db"),"0".repeat(64)],{encoding:"utf8"});
    assert.equal(updateCandidate.status,0,updateCandidate.stderr);
    await page.locator("#read").click();
    await page.waitForFunction(()=>document.getElementById("status").textContent.includes("completo"));
    check("historical_version_stays_readable",await page.locator("#text").textContent()===text);
    const historicalDownload=page.waitForEvent("download");
    await page.locator("#save").click();
    const historical=JSON.parse(fs.readFileSync(await (await historicalDownload).path(),"utf8"));
    check("historical_reference_stays_pinned",historical.version===version&&historical.text_sha256===version);
    await page.waitForFunction(()=>document.getElementById("status").textContent.includes("descargada"));
    await page.route("**/api/v2/documento/**",async route=>{
      const response=await route.fetch();const body=await response.json();
      body.source_sha256="invalid";await route.fulfill({response,json:body});
    });
    await page.locator("#read").click();
    await page.waitForFunction(()=>document.getElementById("status").textContent.includes("Procedencia inválida"));
    check("invalid_provenance_cannot_save",await page.locator("#save").isDisabled()&&await page.locator("#text").textContent()==="");
    await page.unroute("**/api/v2/documento/**");

    // The base fixture reuses the text hash as source hash. Distinguish them.
    await page.route("**/api/v2/documento/**",async route=>{
      const response=await route.fetch();const body=await response.json();
      body.source_sha256="a".repeat(64);await route.fulfill({response,json:body});
    });
    await page.locator("#read").click();
    await page.waitForFunction(()=>document.getElementById("status").textContent.includes("completo"));
    const distinctDownload=page.waitForEvent("download");await page.locator("#save").click();
    const distinct=JSON.parse(fs.readFileSync(await (await distinctDownload).path(),"utf8"));
    check("source_hash_not_text_hash",distinct.source_sha256==="a".repeat(64)&&distinct.text_sha256===version);
    await page.waitForFunction(()=>document.getElementById("status").textContent.includes("descargada"));
    await page.unroute("**/api/v2/documento/**");
    // Restored server metadata differs from what was just read: refuse saving.
    const beforeDrift=downloads.length;await page.locator("#save").click();
    await page.waitForFunction(()=>/Procedencia cambió|descargada/.test(document.getElementById("status").textContent));
    check("save_metadata_drift_denied",downloads.length===beforeDrift&&await page.locator("#save").isDisabled());
    for(const bad of ["javascript:alert(1)","https://user:pass@example.invalid/"]) {
      await page.route("**/api/v2/documento/**",async route=>{
        const response=await route.fetch();const body=await response.json();body.source_url=bad;
        await route.fulfill({response,json:body});
      });
      await page.locator("#read").click();
      await page.waitForFunction(()=>document.getElementById("status").textContent.includes("Fuente inválida"));
      check("unsafe_source_url_denied",await page.locator("#save").isDisabled()&&await page.locator("#text").textContent()==="");
      await page.unroute("**/api/v2/documento/**");
    }
    await page.route("**/api/v2/documento/**",async route=>{
      const response=await route.fetch();const body=await response.json();
      if(body.start>0)body.source_sha256="b".repeat(64);
      await route.fulfill({response,json:body});
    });
    await page.locator("#read").click();
    await page.waitForFunction(()=>document.getElementById("status").textContent.includes("Procedencia cambió"));
    check("page_metadata_drift_denied",await page.locator("#save").isDisabled()&&await page.locator("#text").textContent()==="");
    await page.unroute("**/api/v2/documento/**");
    // Inject only the consumer protocol response: not a legal/hash integrity test.
    // U+1F600 is two UTF-16 units but one API code point. BMP-only text cannot
    // distinguish Array.from(text).length from the incorrect text.length.
    await page.route("**/api/v2/documento/**",async route=>{
      const r=await route.fetch(); const body=await r.json();
      if(body.start===0) body.text=body.text.replace("DEMO",String.fromCodePoint(0x1F600)+"EMO");
      await route.fulfill({response:r,json:body});
    });
    await page.locator("#read").click();
    await page.waitForFunction(()=>/completo|No se pudo/.test(document.getElementById("status").textContent));
    check("astral_codepoint_response_contract",
      await page.locator("#text").textContent()===text.replace("DEMO",String.fromCodePoint(0x1F600)+"EMO"));
    await page.unroute("**/api/v2/documento/**");
    await page.setViewportSize({width:390,height:844});
    check("mobile_no_horizontal_overflow",await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
    await page.screenshot({path:path.join(tmp,"browser-mobile.png"),fullPage:true});
    let first=true;
    await page.route("**/api/v2/documento/**",async route=>{
      const r=await route.fetch();
      if(first){first=false;sql("UPDATE access_grants SET revoked_at=1");}
      await route.fulfill({response:r});
    });
    await page.locator("#read").click();
    await page.waitForFunction(()=>document.getElementById("status").textContent.includes("HTTP 403"));
    check("withdrawal_during_pagination_clears_text",await page.locator("#text").textContent()==="");
    await page.unroute("**/api/v2/documento/**");
    sql("UPDATE access_grants SET revoked_at=NULL");
    await page.route("**/api/v2/documento/**",async route=>{const r=await route.fetch();const b=await r.json();b.version="0".repeat(64);await route.fulfill({response:r,json:b});});
    await page.locator("#read").click();
    await page.waitForFunction(()=>document.getElementById("status").textContent.includes("Respuesta inválida"));
    check("wrong_version_not_displayed",await page.locator("#text").textContent()==="");
    await page.unroute("**/api/v2/documento/**");
    await page.route("**/api/v2/logout",route=>route.fulfill({status:503,contentType:"application/json",body:JSON.stringify({error:"INJECTED"})}));
    await page.locator("#logout").click();
    await page.waitForFunction(()=>document.getElementById("status").textContent.includes("NO confirmado"));
    check("failed_logout_retry_available",await page.locator("#logout").isEnabled());
    await page.unroute("**/api/v2/logout");
    const logoutResponse=page.waitForResponse(r=>r.url().endsWith("/api/v2/logout"));
    await page.locator("#logout").click();
    check("browser_logout_200",(await logoutResponse).status()===200);
    await page.waitForFunction(()=>document.getElementById("status").textContent.includes("revocación confirmada"));
    check("logout_clears_text",await page.locator("#text").textContent()==="");
    check("logout_disables_read",await page.locator("#read").isDisabled());
    check("logout_disables_save",await page.locator("#save").isDisabled());
    const denied=await context.request.get(ready.url+"/api/v2/documento/fixture-demo/texto?version="+version,{headers:{Authorization:"Bearer "+token}});
    check("server_revocation_403",denied.status()===403);
    await page.locator("#login").click();
    await page.waitForFunction(()=>document.getElementById("status").textContent.includes("iniciada"));
    await page.reload();
    check("reload_forgets_ui_session",await page.locator("#read").isDisabled());
    check("reload_forgets_reference",await page.locator("#save").isDisabled());
    check("no_javascript_errors",errors.length===0);
    console.log(JSON.stringify({browser:browser.version(),results,errors,fixture:"synthetic",screenshots:[path.join(tmp,"browser-mobile.png")]},null,2));
  } finally {
    if(context) await context.close();
    if(browser) await browser.close();
    const exited=once(server,"exit"); server.kill("SIGTERM");
    const timer=setTimeout(()=>server.kill("SIGKILL"),8000);
    const [code,signal]=await exited; clearTimeout(timer);
    console.log(JSON.stringify({server_exit:code,signal,stderr,captured_results:results}));
    assert.equal(code,0,"clean server shutdown");
    // Ephemeral synthetic fixtures stay outside Git. No tokens in output.
  }
}
main().catch(e=>{console.error(e.stack);process.exitCode=1;});
