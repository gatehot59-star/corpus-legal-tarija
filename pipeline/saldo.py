import json, os, urllib.request
K = os.environ.get("ABACUS_API_KEY", "")
print("key presente:", bool(K), "| largo:", len(K))
RUTAS = ["getOrganizationComputePoints", "getComputePointInfo", "describeOrganization",
         "getBillingInfo", "listApiKeys", "getUsage"]
for p in RUTAS:
    u = "https://api.abacus.ai/api/v0/" + p
    r = urllib.request.Request(u, headers={"apiKey": K})
    try:
        with urllib.request.urlopen(r, timeout=30) as f:
            print("%-32s http=%s %s" % (p, f.status, f.read()[:300].decode("utf8", "replace")))
    except Exception as e:
        b = ""
        try: b = e.read()[:200].decode("utf8", "replace")
        except Exception: pass
        print("%-32s ERR=%s %s" % (p, getattr(e, "code", type(e).__name__), b))
