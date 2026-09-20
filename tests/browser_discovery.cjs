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
let directory, fixtureNumber = 0;
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
/** Compare to an independent oracle and retain actual/expected on failure. */
function checkExact(name, actual, expected) {
  const equal = require("node:util").isDeepStrictEqual(actual, expected);
  checks.push({name, pass:equal, actual:structuredClone(actual), expected:structuredClone(expected)});
  assert.deepEqual(actual, expected, name);
}
/** Select a non-derived locator, read it, and compare the real download to it. */
async function verifySelectedReference(page, index, uid, text) {
  const version = require("node:crypto").createHash("sha256").update(text,"utf8").digest("hex");
  const prefix = "selection_" + uid;
  await page.locator("#results button").nth(index).click();
  checkExact(prefix+"_clears_previous_text", await page.locator("#text").textContent(), "");
  checkExact(prefix+"_invalidates_previous_reference", await page.locator("#save").isDisabled(), true);
  checkExact(prefix+"_pins_clicked_version", await page.locator("#version-label").textContent(), version);
  await click(page,"read");
  checkExact(prefix+"_reads_clicked_text", await page.locator("#text").textContent(), text);
  checkExact(prefix+"_enables_save_after_read", await page.locator("#save").isEnabled(), true);
  // Attach rejection handling immediately: no unhandled timeout if click fails.
  const pending = page.waitForEvent("download",{timeout:5000})
    .then(download=>({download}), error=>({error}));
  await click(page,"save");
  const outcome = await pending;
  if (outcome.error) throw outcome.error;
  const download = outcome.download;
  const record = JSON.parse(fs.readFileSync(await download.path(),"utf8"));
  checkExact(prefix+"_downloads_clicked_locator",
    [record.uid,record.version,record.text_sha256], [uid,version,version]);
  checkExact(prefix+"_filename_matches_clicked_locator", download.suggestedFilename(),
    `corpus-${uid}-${version}.reference.json`);
  checkExact(prefix+"_provenance_matches_clicked_document",
    [record.source_sha256,record.source_url,record.total_characters,
      record.authority,record.oficial,record.legal_validity,record.environment],
    ["a".repeat(64),"https://example.invalid/discovery/"+uid,Array.from(text).length,
      "secondary",false,"NOT_MEASURED","isolated_test"]);
  checkExact(prefix+"_reference_has_no_text_field", Object.hasOwn(record,"text"), false);
}

async function freshFixture() {
  if (server && server.exitCode===null) {
    const stopped=new Promise((resolve,reject)=>{
      const timer=setTimeout(()=>reject(new Error("fixture server did not stop")),5000);
      server.once("exit",code=>{clearTimeout(timer);code===0 ? resolve() : reject(new Error("server exit "+code));});
    });
    server.kill("SIGTERM");await stopped;
  }
  directory=path.join(temporary,"fixture-"+(++fixtureNumber));
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
  return ready;
}
async function main() {
  let ready=await freshFixture();
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

  // Real pre-revocation failures, not mocked HTTP statuses. Never print the bearer.
  // Separate fixture budgets: do not weaken the persisted five-login rate limit.
  ready=await freshFixture();await page.goto(ready.url);
  for (const failure of [403,503]) {
    const prefix="logout_"+failure;
    const loginResponse=page.waitForResponse(r=>r.url().endsWith("/api/v2/login"));
    await click(page,"login");
    const original=(await (await loginResponse).json()).access_token;
    const originalStatus=async()=> (await page.request.get(ready.url+"/api/v2/buscar?q=derecho",
      {headers:{Authorization:"Bearer "+original}})).status();
    await click(page,"search");await page.locator("#results button").first().click();await click(page,"read");
    check(prefix+"_positive_content",await page.locator("#text").textContent()===expected &&
      await page.locator("#save").isEnabled() && await originalStatus()===200);
    const marker=spawnSync("python3",["-c",
      "import sqlite3,sys,json;d=sqlite3.connect(sys.argv[1]);print(json.dumps(d.execute(\"SELECT * FROM login_environment\").fetchone()));d.close()",
      path.join(directory,"sessions.db")],{encoding:"utf8"});
    assert.equal(marker.status,0,marker.stderr);
    const markerRow=JSON.parse(marker.stdout);
    if(failure===403) sql("DELETE FROM login_environment");
    else sql("ALTER TABLE login_environment RENAME TO retry_marker");
    const restore=()=>{
      if(failure===503) sql("ALTER TABLE retry_marker RENAME TO login_environment");
      else {
        const r=spawnSync("python3",["-c",
          "import sqlite3,sys,json;d=sqlite3.connect(sys.argv[1]);d.execute(\"INSERT INTO login_environment VALUES(?,?)\",json.loads(sys.argv[2]));d.commit();d.close()",
          path.join(directory,"sessions.db"),JSON.stringify(markerRow)],{encoding:"utf8"});
        assert.equal(r.status,0,r.stderr);
      }
    };
    try {
      for(let attempt=1;attempt<=2;attempt++) {
        const response=page.waitForResponse(r=>r.url().endsWith("/api/v2/logout"));
        await click(page,"logout");
        const rejected=await response;
        check(prefix+"_attempt_"+attempt+"_real_status",rejected.status()===failure);
        check(prefix+"_attempt_"+attempt+"_same_bearer",
          (await rejected.request().allHeaders()).authorization==="Bearer "+original);
        check(prefix+"_attempt_"+attempt+"_unconfirmed",
          (await page.locator("#status").textContent()).includes("Cierre NO confirmado"));
        check(prefix+"_attempt_"+attempt+"_retry_enabled",await page.locator("#logout").isEnabled());
        check(prefix+"_attempt_"+attempt+"_cleared",await page.locator("#text").textContent()==="" &&
          await page.locator("#results button").count()===0 &&
          await page.locator("#version-label").textContent()==="ninguna");
        check(prefix+"_attempt_"+attempt+"_only_logout",
          await page.locator("#search").isDisabled() && await page.locator("#read").isDisabled() &&
          await page.locator("#save").isDisabled() && await page.locator("#login").isDisabled() &&
          await page.locator("#identity").isDisabled());
      }
    } finally {restore();}
    check(prefix+"_original_still_live_before_retry",await originalStatus()===200);
    let unexpected=0;
    const watch=()=>unexpected++;
    page.on("request",watch);
    await page.evaluate(()=>{
      for(const id of ["login","search","read","save"])
        document.getElementById(id).dispatchEvent(new MouseEvent("click",{bubbles:true}));
    });
    await page.waitForTimeout(100);
    page.off("request",watch);
    check(prefix+"_programmatic_actions_blocked",unexpected===0 &&
      (await page.locator("#status").textContent()).includes("Cierre NO confirmado"));
    check(prefix+"_no_dom_url_storage_leak",await page.evaluate(value=>
      !document.documentElement.outerHTML.includes(value) && !location.href.includes(value) &&
      !JSON.stringify(localStorage).includes(value) && !JSON.stringify(sessionStorage).includes(value),original));
    const retryResponse=page.waitForResponse(r=>r.url().endsWith("/api/v2/logout"));
    await click(page,"logout");
    const retried=await retryResponse;
    check(prefix+"_retry_same_original",retried.status()===200 &&
      (await retried.request().allHeaders()).authorization==="Bearer "+original);
    check(prefix+"_confirmed_only_after_success",
      (await page.locator("#status").textContent()).includes("revocación confirmada"));
    check(prefix+"_original_revoked",await originalStatus()===403);
    check(prefix+"_login_reenabled",await page.locator("#login").isEnabled() &&
      await page.locator("#logout").isDisabled() && await page.locator("#search").isDisabled());
  }
  ready=await freshFixture();await page.goto(ready.url);
  await page.locator("#identity").selectOption("ben");await click(page,"login");await click(page,"search");
  check("ben_only_own_collection",(await page.locator("#results").textContent()).includes("reservado a Ben") &&
    !(await page.locator("#results").textContent()).includes("DEMO A"));
  await click(page,"logout");
  await page.locator("#identity").selectOption("ana");await click(page,"login");await click(page,"search");
  sql("UPDATE access_documents SET withdrawn_at=1 WHERE uid='fixture-a1'");
  await page.locator("#results button").first().click();await click(page,"read");
  check("revoked_after_results_clears",await page.locator("#text").textContent()==="" &&
    await page.locator("#results button").count()===0 && await page.locator("#save").isDisabled());
  check("ordinary_read_403_requires_fresh_login",await page.locator("#login").isEnabled() &&
    await page.locator("#logout").isDisabled() && await page.locator("#search").isDisabled());
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
  // Regression: a correct first result must not hide a broken selection callback.
  // Fresh fixture keeps this flow independent of the prior five-login budget.
  ready=await freshFixture();await page.goto(ready.url);
  await click(page,"login");await click(page,"search");
  await verifySelectedReference(page,0,"fixture-a1",
    "DEMO A: derechos ficticios\r\nArtículo único: Ñ, ⚖, e\u0301 y 😀. Straße.\r\n");
  await verifySelectedReference(page,1,"fixture-a2",
    "<img src=x onerror=alert(1)> DEMO A\r\nOtro derecho ficticio, sin valor jurídico.\r\n");
  await click(page,"logout");
  checkExact("selection_ana_logout_confirmed",
    (await page.locator("#status").textContent()).includes("revocación confirmada"),true);
  await page.locator("#identity").selectOption("ben");
  await click(page,"login");await click(page,"search");
  await verifySelectedReference(page,1,"fixture-b2",
    "DEMO B: registro ficticio\r\nOtro derecho de prueba, no una ley.\r\n");
  await click(page,"logout");
  checkExact("selection_ben_logout_confirmed",
    (await page.locator("#status").textContent()).includes("revocación confirmada"),true);

  // Regression: an expired session must still be revoked by a pending logout.
  // Alter only this synthetic store's validity window, not the server clock.
  ready=await freshFixture();await page.goto(ready.url);
  const expiryContext=await browser.newContext();
  const expiryOther=await expiryContext.newPage();
  let releaseExpiry;
  let expiryCalls=0, expirySameBearer=true;
  const expirySql=(statement,parameters=[])=>{
    const result=spawnSync("python3",["-c",
      "import sqlite3,sys,json;from contextlib import closing\nwith closing(sqlite3.connect(sys.argv[1],timeout=2)) as db,db:\n print(json.dumps(db.execute(sys.argv[2],json.loads(sys.argv[3])).fetchall()))",
      path.join(directory,"sessions.db"),statement,JSON.stringify(parameters)],
      {encoding:"utf8",timeout:5000});
    assert.equal(result.status,0,result.stderr);
    return JSON.parse(result.stdout);
  };
  const expiryLogin=async target=>{
    const pending=target.waitForResponse(r=>r.url().endsWith("/api/v2/login"),{timeout:5000})
      .then(response=>({response}),error=>({error}));
    await click(target,"login");
    const result=await pending;
    if(result.error)throw result.error;
    const body=await result.response.json();
    assert.equal(result.response.status(),200,"expiry login must succeed");
    assert.equal(typeof body.access_token,"string","expiry bearer must exist");
    return body.access_token;
  };
  try {
    expiryOther.on("pageerror",e=>failures.push(String(e)));
    const expiryA=await expiryLogin(page);
    await click(page,"search");
    await page.locator("#results button").first().click();await click(page,"read");
    checkExact("expiry_positive_text",await page.locator("#text").textContent(),expected);
    checkExact("expiry_reference_ready",await page.locator("#save").isEnabled(),true);
    await expiryOther.goto(ready.url);
    const expiryB=await expiryLogin(expiryOther); // Same identity, separate real session.
    checkExact("expiry_distinct_same_user_sessions",expiryA!==expiryB,true);
    const digest=token=>require("node:crypto").createHash("sha256").update(token).digest("hex");
    const expiryStatus=async token=>{
      const response=await page.request.get(ready.url+"/api/v2/buscar?q=derecho",
        {headers:{Authorization:"Bearer "+token},timeout:5000});
      try {return response.status();} finally {await response.dispose();}
    };
    checkExact("expiry_A_initially_authorized",await expiryStatus(expiryA),200);
    checkExact("expiry_B_initially_authorized",await expiryStatus(expiryB),200);
    const gate=new Promise(resolve=>{releaseExpiry=resolve;});
    await page.route("**/api/v2/logout",async route=>{
      expiryCalls++;
      expirySameBearer=expirySameBearer &&
        route.request().headers().authorization==="Bearer "+expiryA;
      await gate;await route.continue();
    });
    await page.locator("#logout").click();
    await page.waitForFunction(()=>document.querySelector("#status").textContent.includes("Esperando"));
    checkExact("expiry_pending_clears_content",
      [await page.locator("#text").textContent(),await page.locator("#results button").count(),
        await page.locator("#version-label").textContent()],["",0,"ninguna"]);
    checkExact("expiry_pending_disables_actions",await page.evaluate(()=>
      ["login","search","read","save","logout","identity","query"]
        .every(id=>document.getElementById(id).disabled)),true);
    const originalWindow=expirySql(
      "SELECT valid_from,valid_until FROM access_sessions WHERE token_sha256=?",[digest(expiryA)]);
    checkExact("expiry_one_target_session",originalWindow.length,1);
    expirySql("UPDATE access_sessions SET valid_from=0,valid_until=1 WHERE token_sha256=?",
      [digest(expiryA)]);
    checkExact("expiry_A_denied_before_logout_reaches_server",await expiryStatus(expiryA),403);
    checkExact("expiry_B_survives_A_expiration",await expiryStatus(expiryB),200);
    const responsePromise=page.waitForResponse(r=>r.url().endsWith("/api/v2/logout"),{timeout:5000})
      .then(response=>({response}),error=>({error}));
    releaseExpiry();
    const result=await responsePromise;
    if(result.error)throw result.error;
    checkExact("expiry_logout_http_success",result.response.status(),200);
    checkExact("expiry_logout_boolean_confirmation",(await result.response.json()).logged_out,true);
    await page.waitForFunction(()=>!document.querySelector("#status").textContent.includes("Esperando"));
    checkExact("expiry_UI_confirms_revocation",
      (await page.locator("#status").textContent()).includes("revocación confirmada"),true);
    checkExact("expiry_one_request_with_original_bearer",[expiryCalls,expirySameBearer],[1,true]);
    // A403 while expired is not evidence of revocation. Restore its exact former
    // validity window before checking denial and the persisted revocation marker.
    expirySql("UPDATE access_sessions SET valid_from=?,valid_until=? WHERE token_sha256=?",
      [...originalWindow[0],digest(expiryA)]);
    checkExact("expiry_restored_window_does_not_resurrect_A",await expiryStatus(expiryA),403);
    checkExact("expiry_A_persistently_revoked",expirySql(
      "SELECT revoked_at IS NOT NULL FROM access_sessions WHERE token_sha256=?",[digest(expiryA)]),[[1]]);
    checkExact("expiry_same_user_B_not_revoked",expirySql(
      "SELECT revoked_at IS NULL FROM access_sessions WHERE token_sha256=?",[digest(expiryB)]),[[1]]);
    checkExact("expiry_B_still_authorized",await expiryStatus(expiryB),200);
    await click(expiryOther,"search");
    checkExact("expiry_B_browser_still_usable",await expiryOther.locator("#results button").count(),2);
    await click(expiryOther,"logout");
    checkExact("expiry_B_own_logout_confirmed",
      (await expiryOther.locator("#status").textContent()).includes("revocación confirmada"),true);
    checkExact("expiry_B_denied_after_own_logout",await expiryStatus(expiryB),403);
  } finally {
    if(releaseExpiry)releaseExpiry();
    await page.unrouteAll({behavior:"wait"});
    await expiryContext.close();
    // Cleanup of this fixture only; assertions above precede this forced cleanup.
    expirySql("UPDATE access_sessions SET revoked_at=COALESCE(revoked_at,1)");
  }

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
