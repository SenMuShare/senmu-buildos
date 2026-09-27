# Public Service Deployment Security Baseline

Select for a new public service, a changed exposure/identity/runtime boundary, or an explicit deployment-security review. Assess existing equivalent controls first. Public-service deployment is not the ordinary local-edit fast path. Offline/source-only projects do not acquire fictional firewalls or cloud services.

Engineering owns safe application behavior; this standard owns actual edge, host, container and operational protection. Use mature platform capabilities and safe defaults, then verify their configuration and observable result. A Skill provides neither a DDoS scrubbing network nor a no-backdoor guarantee.

## Record actual protection at its owner

Use the existing deployment/operations document. For each applicable row keep the target, control/configuration owner, verification and time, result, unresolved risk and remediation/exception owner. `planned`, `configured`, `verified`, `failed`, `unverified` and justified `not_applicable` are different states; a configuration file alone is not runtime proof. Reuse current evidence unless affected inputs or time-sensitive facts changed.

### Network exposure

Enumerate intended public entrypoints and listening ports. Keep databases, caches, orchestration sockets and administrative ports private or behind explicitly authorized access; inspect effective cloud and host rules, not just an example file.

### Edge and origin

Match provider DDoS/WAF/CDN capabilities to actual exposure. Where proxying is the protection boundary, restrict direct origin access using platform identity, private connectivity or verified source rules. Test normal routing and authorized direct-origin denial without load attacks. CDN enabled is not proof against bypass.

### HTTPS and proxy trust

Configure TLS and certificate renewal; trust forwarded headers only from known proxies. Verify secure redirects/cookies and prevent forged client identity from bypassing limits.

### Availability and spend

Set measured request/body/time/concurrency/queue/storage limits and tenant cost admission with Engineering. Identify provider spend behavior, alert delivery, degradation and recovery. A WAF alone does not constrain authenticated expensive work.

### Host and containers

Use supported patched systems and least privilege. Avoid privileged containers, writable host roots and Docker socket mounts unless a scoped need and isolation are verified. Prefer non-root processes; evaluate rootless/user namespaces against volume and platform compatibility. Restrict capabilities and writes to required resources.

### Secrets and supply chain

Inject secrets through approved mechanisms, exclude them from source/images/logs and rotate exposed values. Verify image/package identity and dependency/build provenance; scan actual shipped surfaces with configured tools, not a claimed tool name.

### Runtime configuration

Disable production debug consoles, development servers, default accounts and unnecessary diagnostics. Test safe startup failure for missing critical configuration; a health endpoint must not expose secrets.

### Detection and response

Observe denial/error/latency/saturation and spend anomalies, verify an alert reaches its owner, and retain sufficient redacted diagnostics. Document who can contain abuse and rotate/recover access.

### Backup and recovery

Protect backup access separately, state retention and recovery targets, and verify a restore in an isolated authorized environment. A rollback image is not a backup of persistent data.

## Delivery decision

Before first public exposure, verify applicable critical controls and the user flow. A missing critical control, unknown exposure or failed negative check returns to its owner; do not label the system safe because tests or deployment commands exited zero. Existing protected services need impact-based rechecks, not a complete security ceremony for every copy edit.

Configure scanning through the existing quality/deployment entrypoint. For example, a dependency scan, a secret scan and an infrastructure misconfiguration scan cover different surfaces and may need different options. Do not add every scanner, duplicate policies or accept an empty scan as clean. A tool installation, read-only assessment or recommendation is not authority to mutate production, run intrusive probes or incur charges.

For an approved exception, retain concrete exposure, compensating controls, owner and expiry/revisit trigger. Do not invent universal ports, traffic thresholds or a mandatory vendor. Volumetric attacks need appropriate upstream protection; application limits address a different layer. Recovery and source identity continue to use existing Delivery standards.

Calibration: [OWASP DoS](https://cheatsheetseries.owasp.org/cheatsheets/Denial_of_Service_Cheat_Sheet.html), [Cloudflare proactive defense](https://developers.cloudflare.com/ddos-protection/best-practices/proactive-defense/), [Docker security](https://docs.docker.com/engine/security/). Recheck provider capabilities and platform options at adoption.
