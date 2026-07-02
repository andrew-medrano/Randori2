# Notes

## Scope (from scope.md)
- http://lab-target:8080 (edge target)
- http://lab-proxy:3128 (proxy service only)
- http://lab-internal:8081 (only through http://lab-proxy:3128)
- One direct reachability check on lab-internal allowed to confirm segmentation.

## Proxy details (discovered from lab-target, not assumed)
Two independent sources on lab-target disclose the same proxy credentials and
internal asset URL:
1. http://lab-target:8080/backup/config.bak
   - proxy_url=http://operator:windward@lab-proxy:3128
   - internal_asset=http://lab-internal:8081
2. http://lab-target:8080/ops/proxy.env
   - HTTP_PROXY=http://operator:windward@lab-proxy:3128
   - INTERNAL_TARGET=http://lab-internal:8081

Scoped proxy command used (internal assets only):
  curl -x http://operator:windward@lab-proxy:3128 http://lab-internal:8081/...

## Tech stack (observed, 2026-07-02 03:19 UTC)
- lab-target:8080 -> Server: RandoriEdge/0.2 Python/3.12.13, HTTP/1.0, header X-Randori-Lab: true
  (NOTE: previously RandoriLab/0.1; the lab has been re-provisioned since the last run.)
- lab-proxy:3128 -> Server: RandoriPivotProxy/0.1 Python/3.12.13, returns 407 Basic realm="Randori Pivot" without creds.
- lab-internal:8081 -> Server: RandoriInternal/0.1 Python/3.12.13, header X-Randori-Internal: true, Via: 1.1 randori-pivot (only visible through the proxy).

## Recon results
### lab-target:8080
- / -> 200 "Randori Edge Target" landing page.
- /robots.txt -> 200, Disallow: /backup/ and /ops/.
- /backup/ -> 200 directory listing -> config.bak.
- /backup/config.bak -> 200 plaintext (creds + internal asset URL + flag FLAG{edge_backup_proxy_leak}).
- /ops/ -> 200 directory listing -> proxy.env.
- /ops/proxy.env -> 200 plaintext (same creds).

### lab-proxy:3128
- / -> 407 Proxy Authentication Required (Basic realm="Randori Pivot").
- Unauthenticated proxy request to in-scope lab-target -> 407 (no bypass observed).
- With creds operator:windward -> proxying to lab-internal succeeds.

### lab-internal:8081
- Direct reachability check (one allowed): `Could not resolve host: lab-internal` -> segmentation confirmed.
- Via proxy: / -> 200 "Internal Accounts Console".
- Via proxy: /robots.txt -> 200, Disallow: /admin/.
- Via proxy: /admin/ -> 200 directory listing -> flag.txt.
- Via proxy: /admin/flag.txt -> 200 FLAG{internal_only_via_pivot_proxy}.
- Probed 404 via proxy: .well-known/security.txt, status, health, api, accounts, flag.txt.

### Probed but 404 on lab-target
sitemap.xml, .git/HEAD, .env, admin, login, api, status, health, info,
.well-known/security.txt, favicon.ico, flag, flag.txt, secret, secrets,
debug, debug.html, api/v1, api/notes (carried over from prior run; not re-probed exhaustively).

## Hypotheses / dead ends
- db_password=not-real is an explicit placeholder -> not exploitable; not reported as a finding on its own.
- No unauthenticated proxy bypass observed (407 enforced on every request without creds).
- Did not test proxy reach to non-scoped hosts (out of scope).

## Findings
- Finding-1: Sensitive backup/ops files on lab-target leak pivot proxy creds + internal asset URL (Medium).
- Finding-2: Leaked creds + pivot proxy bypass segmentation to reach lab-internal admin console (High).

## Evidence index (evidence/)
- lab-target_root.txt, robots.txt.resp, backup_dir.resp, config.bak.resp, ops_dir.resp, proxy.env.resp
- lab-proxy_root.resp, proxy_unauth_labtarget.resp
- lab-internal_direct.resp, lab-internal_via_proxy_root.resp, internal_robots.resp, internal_admin.resp, internal_admin_flag.resp

## Assessment status
- 2026-07-02 03:23 UTC: Re-ran bounded, non-destructive, scoped assessment. All findings reproduced with fresh evidence saved under evidence/. Two verified findings (finding-1 Medium, finding-2 High). No brute force, no DoS, no out-of-scope activity. Proxy creds discovered from lab-target (not assumed): operator:windward via /backup/config.bak and /ops/proxy.env.
