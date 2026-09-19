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
    const denied=await context.request.get(ready.url+"/api/v2/documento/fixture-demo/texto?version="+version,{headers:{Authorization:"Bearer "+token}});
    check("server_revocation_403",denied.status()===403);
    await page.locator("#login").click();
    await page.waitForFunction(()=>document.getElementById("status").textContent.includes("iniciada"));
    await page.reload();
    check("reload_forgets_ui_session",await page.locator("#read").isDisabled());
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
