# Instructions

You are running inside a Kali-style assessment container.
Only test the target listed in scope.md.

Maintain durable state:
- notes.md for discoveries, hypotheses, credentials, and dead ends
- evidence/ for raw artifacts
- findings/ for verified issues

Do not report a vulnerability unless you have reproduced it and saved supporting evidence.
Prefer safe, non-destructive checks. Ask before running noisy, destructive, credentialed, or out-of-scope actions.
If proxy credentials are discovered on a scoped target, use them only for scoped internal assets and record the exact proxy command in notes.md.

For each verified finding, create findings/finding-N.md with:
- Title
- Severity
- Affected asset
- Evidence
- Reproduction steps
- Impact
- Remediation
