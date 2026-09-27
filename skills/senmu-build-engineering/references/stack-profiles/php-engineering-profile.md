# PHP Engineering Profile

Confirm supported PHP version, framework, Composer ownership and request/long-running-worker model. Preserve a stable project baseline instead of introducing another framework or blanket strictness migration.

Parse external inputs explicitly. Avoid loose comparison for authentication, identifiers and security decisions; `strict_types` does not validate arbitrary request data. Keep absent, null, empty and zero values distinct where the domain requires them. Type stable boundaries and contain dynamic arrays at adapters.

Use framework parameter binding, output escaping, session/CSRF controls and supported password hashing. Prepared queries protect bound values, not concatenated identifiers or other query structure. Never deserialize untrusted PHP objects, evaluate user-controlled code, or include arbitrary user paths. Uploaded files need separate storage, validation and execution restrictions, not extension checks alone.

Make transaction and connection ownership explicit. In long-running workers, clear tenant/request state and bounded caches; assumptions valid for one-request process lifetime may leak across jobs. Catch actionable failures at boundaries without returning success-shaped values.

Use established Composer install/lock and test/static-analysis commands in an authorized environment; dependency scripts can execute code. Test authorization, invalid type/value input, encoding, session boundaries and worker reuse where applicable. A dependency audit is not proof of absence of vulnerabilities or backdoors.

Calibration: [PHP security manual](https://www.php.net/manual/en/security.php). Framework-specific middleware behavior belongs in the current project/framework owner.
