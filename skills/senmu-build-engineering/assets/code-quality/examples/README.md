# Wire a selected rule to a real check

Use these small, offline business examples only when an adopted Python or TypeScript rule lacks a working check. They are not new project layouts, runtime dependencies, or automatic migrations. Keep the existing formatter, type checker, framework and quality command when they already satisfy the contract.

## Adopt at the existing owner

Inspect the project's runtime, package manager/lock, configuration inheritance, source roots, nested rules and CI command. Choose one real gap, identify its current owner and preserve accepted exceptions. Add the narrow check there, not a second generic checker or a parallel rules file. Invoke the same quality entrypoint locally and in CI. Keep implementation-time constraints available to the implementer; review does not excuse writing known violations first.

Prove the connection in a disposable copy: the normal path passes; an intentional violation fails for the expected reason; restoration passes. A missing executable, parse error or unrelated failing test is not that negative control. Never inject a defect into production or leave one in the working tree. Preserve the command, tool versions, observed result and remaining limits in the existing task/CI record. File presence or a selector route alone is not adoption.

## Python example

From `python/`, create an isolated virtual environment and install the example-only tools with `python -m pip install -r requirements-dev.txt` within existing dependency authority. Run `python check.py`. It shares Ruff configuration, mypy and Import Linter with the business test entrypoint. The domain is forbidden to import the adapter; its callers may use it. This is a selected dependency rule, not a ban on legitimate internal tests or all dependencies.

In a disposable copy, changing the total to return a string tests type checking; introducing a mutable default tests Ruff B006; calling the adapter from the domain tests the import contract; changing subtraction to addition tests behavior. Restore after each probe. Keep the project's existing Pyright/mypy choice on adoption, rather than installing both.

## TypeScript example

From `typescript/`, install the declared dev dependencies with the project's package manager (the example uses `npm install --ignore-scripts`) and run `npm run check`. Keep the resulting lockfile in the adopting project's existing dependency owner; example pins are a test baseline, not a recommendation to downgrade a current toolchain. The command checks the declared `src` graph, compiles strict TypeScript and runs Node's business tests. `npm run typecheck` is the focused compiler path.

The configuration names this example's actual private pricing module. A caller uses its public entry; pricing's own files may use the implementation. Adapt paths to real ownership, include every relevant entrypoint in the scan, and keep justified local exceptions. Do not impose `src/packages`, universal barrels, or a two-adapter requirement. This example does not replace an established formatter/ESLint setup or validate files outside its declared scope.

## Repeatable check of the examples

With the above tools already installed and available on PATH, from the BuildOS product root run:

```sh
python3 tests/recipes/check_quality_wiring.py
```

This opt-in test copies each example to temporary storage and exercises its real public check command through valid/invalid/restored cases. It installs nothing, edits no existing project and fails if a required tool is missing. The ordinary product unit suite remains offline and dependency-free. Record dependency resolution and versions for the run; these are tool/fixture results, not observations of a model following instructions.

Sources for calibration: [Ruff configuration](https://docs.astral.sh/ruff/configuration/), [Import Linter](https://import-linter.readthedocs.io/en/stable/), [mypy configuration](https://mypy.readthedocs.io/en/stable/config_file.html), [TypeScript strict](https://www.typescriptlang.org/tsconfig/strict.html), [dependency-cruiser rules](https://github.com/sverweij/dependency-cruiser/blob/main/doc/rules-reference.md). Recheck current tool contracts at adoption. The examples are original minimal fixtures, not a copied third-party configuration.
