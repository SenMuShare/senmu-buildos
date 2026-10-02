# Executable contract examples

Use these optional, synthetic examples when a project lacks a working contract-to-verification chain. They are not plugin runtime dependencies, a production scaffold, or a required migration from Flask or another framework. Reuse the project's existing equivalent tools. Both examples run only on loopback with a temporary SQLite database and fabricated item data.

## Maintenance sources

| Example | Maintain | Derived artifacts | Real verification |
| --- | --- | --- | --- |
| `definition-first` | `openapi.yaml` and its local `schemas/` references | `generated/openapi.json`, `generated/api.d.ts` | Independent WSGI provider, compiled TypeScript consumer and OpenAPI-core validation of captured traffic |
| `declaration-first` | Models and route declarations in `app.py` | The same two generated artifacts, exported through FastAPI | FastAPI provider, the same compiled consumer and OpenAPI-core validation of captured traffic |

The source format is OpenAPI 3.1, including actual nullable unions. Redocly validates the configured operation-id rule and resolves local references. openapi-typescript generates types; TypeScript compiles the consumer. OpenAPI-core checks the real request/response structures. Separate assertions check values, denied invalid input, retrieval and SQLite state after reopening the provider. Static types do not validate network data.

All references in these shipped examples are trusted and local. This runner accepts only the two example modes, not arbitrary user projects. It does not prove all possible endpoint scenarios, production security, concurrent transactions, crash recovery, browser behavior, native Agent loading or model adherence. The older standard-library `contract_fixture.py` remains a deliberately narrow host fixture, not a general schema validator.

## Run in an isolated copy

Use Python 3.11+ and Node.js 22+. Review dependencies and install in an isolated environment, not in a user's global host. No script below installs tools automatically. Dependency downloads require network access; checks use local references and loopback only. The environment disables Redocly telemetry.

From this example directory after copying it into a disposable workspace:

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-dev.lock
npm ci --ignore-scripts --no-audit --no-fund
export PATH="$PWD/node_modules/.bin:$PATH"
python check.py definition-first
python check.py declaration-first
```

`requirements-dev.txt` declares direct tools; `requirements-dev.lock` pins their tested dependency set. `package-lock.json` records the npm resolution. Update these together after exercising compatibility; a pinned example is not a recommendation to downgrade an existing project. The tools retain their own permissive upstream licenses; no third-party source or installed packages are vendored here.

Default checks regenerate into temporary storage and compare both delivered artifacts before compiling or sending requests. A mismatch fails with `contract-drift` or `client-drift`; it does not silently repair the stale output. After an authorized maintenance-source change, regenerate explicitly:

```sh
python check.py definition-first --generate
python check.py declaration-first --generate
```

Each command writes only the selected example's two generated files and then runs the actual checks. A failed runtime check can leave freshly generated artifacts; it is not a successful delivery. Do not hand-edit these files to hide a source error.

## Prove the checks work

From the BuildOS product root, with the same environment and tools on PATH:

```sh
python tests/recipes/check_contract_pipelines.py
# Focused investigation, rather than rerunning unrelated cases:
python tests/recipes/check_contract_pipelines.py --mode definition-first --case missing-required-response-field
```

The recipe uses disposable copies, checks a valid baseline, injects violations and restores them. It exercises missing required response fields, changed referenced types, broken references, an absent operation ID, stale exports, hand-edited types, invalid caller types and missing persistence. Declaration-based tests also detect model/export drift and a provider bypassing its response model. Each negative must fail at the intended stage, not just with any nonzero exit. The restored counterpart must pass. Source files remain unchanged, and repeated explicit generation is reproducible.

A direct-file hash is not a multi-file contract baseline. These examples regenerate through the reference graph; real work should additionally bind approved intent, relevant working changes, generated artifacts and separately released consumers to the task's actual revision. Schema validity alone is not backward compatibility or product approval.

## Official tool references

- [Redocly configuration and bundling](https://redocly.com/docs/cli/commands/bundle)
- [openapi-typescript CLI and generated drift](https://openapi-ts.dev/cli)
- [OpenAPI-core request/response validation](https://openapi-core.readthedocs.io/en/stable/validation/)
- [FastAPI OpenAPI export](https://fastapi.tiangolo.com/how-to/extending-openapi/)

This example owns execution mechanics only. Authority, rollout and change-kind decisions remain in the [contract method](../../references/api-and-boundary-contract-governance.md).
