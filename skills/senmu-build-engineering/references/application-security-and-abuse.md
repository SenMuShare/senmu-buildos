# Application Security and Abuse Boundaries

Use for internet-facing services, untrusted input, identities, tenant data, uploads, remote fetches, administrative actions or paid jobs. Identify the exposure and apply matching controls without waiting for the user to say “secure it.” This is implementation guidance; Delivery verifies actual deployment. A small diff does not remove a real trust boundary.

## Choose supported controls before custom code

Use the framework's authentication, authorization, validation, query binding, escaping, sessions and CSRF mechanisms and supported provider SDKs. Keep each policy at its real server boundary, not copied across UI components. Do not invent cryptography, password storage or token validation. Check that the chosen defaults actually match the threat; CORS is not authorization and hiding a button cannot prevent a request.

| Boundary | Implementation decision | Relevant negative check |
| --- | --- | --- |
| Identity and tenancy | Validate authentication and resource/tenant ownership server-side; restrict privileged operations | Another user's identifier or direct API request is denied; public resources remain usable |
| Sessions and browser output | Use secure cookie/session handling and context-aware escaping; CSRF protection where ambient credentials authorize writes | Forged write and stored/reflected script input fail at the intended boundary |
| Files and media | Bound bytes, decoded size, duration and work; isolate storage and execution; validate content as well as declared type | Traversal, misleading type, oversized/expanding data and unauthorized download are rejected |
| Server-side URL fetch | Restrict schemes/destinations and egress; validate resolved addresses and redirects throughout the actual fetch path | Loopback, link-local/metadata and private destinations cannot be reached through redirect or DNS changes |
| Paid API or queued compute | Enforce tenant/account admission, bounded concurrency, total work and stable idempotency; reconcile unknown billing outcomes | Repeated, concurrent and low-rate expensive calls cannot exceed the approved budget boundary |
| SQL, commands and serialization | Bind data through supported APIs; reject unsafe interpretation and excessive parsing complexity | Injection text stays data; invalid/deep inputs yield a bounded failure |

Per-IP throttling is supplementary: shared NAT, rotating addresses and legitimate heavy users require an appropriate identity and cost model. Limit job duration/expansion as well as request count. Cancel or reject before an unaffordable side effect where possible; vendor billing alerts may lag and are not automatically hard spend caps.

## Verify without inventing safety

Use relevant unit/contract/integration checks, dependency/secret scanning and a controlled staging flow. Exercise denial and recovery alongside success, with non-production data and bounded requests. Do not perform load attacks, intrusive network scans, purchase protection or change production access without authorization. Investigate actual reachable conditions before reporting a vulnerability; a protected path is a counterexample, not a reason to remove the control.

Keep evidence in existing tests and the technical/deployment owner. A model review, lint pass, scanner pass or generated configuration proves neither absence of backdoors nor live protection. Security-critical unresolved exposure remains a release gap, not a style suggestion.

Calibration: [REST security](https://cheatsheetseries.owasp.org/cheatsheets/REST_Security_Cheat_Sheet.html), [file upload](https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html), [SSRF](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html), [API resource consumption](https://owasp.org/API-Security/editions/2023/en/0xa4-unrestricted-resource-consumption/). Tailor requirements with the current OWASP ASVS and project threat model.
