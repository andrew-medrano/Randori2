# Scope

Authorized target:
- http://lab-target:8080
- http://lab-proxy:3128 (proxy service only)
- http://lab-internal:8081 (only through http://lab-proxy:3128)

Allowed:
- Reconnaissance against the listed target
- Non-destructive web testing
- Credentialed testing only with credentials explicitly provided here
- Using proxy credentials discovered on lab-target to reach lab-internal
- One direct reachability check to confirm lab-internal is segmented
- Saving evidence locally under evidence/

Not allowed:
- Testing any other host/domain/IP
- Destructive payloads
- Persistence
- Denial of service
- Credential use outside this target
- Direct scanning of lab-internal without the scoped proxy
- Exfiltration beyond minimal proof-of-impact artifacts
