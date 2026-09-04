# TypeScript Engineering Profile

This profile owns only TypeScript-specific rules for types, runtime boundaries, modules, and tooling. The general source-quality standard owns responsibility, dependencies, side effects, errors, testing, and review. Preserve registered project formatter, lint, module, and framework conventions; this profile is not a second project configuration.

## Types and Runtime Boundaries

- Use `strict` as the new-project baseline. In legacy projects, record current errors and supported versions, then tighten by module. Any disabled strict check needs scope, reason, risk, and restoration trigger; never hide migration cost with a global relaxation.
- Network responses, JSON, environment variables, messages, and third-party input remain untrusted at runtime. Accept them as `unknown`, validate and narrow them, then enter domain logic. Static types do not replace parsing, schemas, or boundary tests.
- Confine `any`, double assertions, non-null assertions, and suppressions to the smallest adapter boundary. State why modeling is infeasible, impact scope, and removal condition. Do not manufacture false green results with `@ts-ignore`, `@ts-nocheck`, or broad assertions.
- Avoid annotations when inference is clear. Explicitly type public boundaries, complex returns, and empty collections/generics likely to infer incorrectly. Use complex mapped/conditional types only when they reduce real duplication and callers can still understand errors.

## State, Modules, and Dependencies

- Model mutually exclusive business states as discriminated unions with a stable discriminator, not boolean combinations that permit invalid states. Use `never` or equivalent for exhaustive critical switches; preserve and test unknown branches in open protocols.
- Use the project's standard ES-module strategy and `import type`/`export type` when type and value spaces differ. Side-effect imports must be explicit, never hidden behind apparently type-only dependencies.
- Do not use TypeScript `namespace`, global patching, or nonstandard runtime features instead of clear modules. Isolate CommonJS, legacy declarations, and third-party globals in controlled adapters.
- Types describe contracts; they do not own business facts. Generated types, API schemas, and runtime validation must point to one authority. Repair the generation/contract chain on drift, not several copies manually.

## Tools, Tests, and Completion

- Declare unified formatter, lint, `tsc`/build, and test commands, with local and CI using the same configuration. Treat new compiler errors as visible migration work; do not silently disable strictness.
- Test invalid external input, nullability, new union members, async rejection, cancellation, and side-effect failure. Type tests do not replace runtime behavior tests.
- Keep legacy-file diffs focused. Put behavior-neutral mass formatting, import sorting, or mechanical type migration in a separate commit or governance task.

Before completion, confirm the affected `tsconfig` inheritance and module target, runtime validation of untrusted input, exhaustive new state, contained suppressions, and project-contracted format, lint, type, test, and build checks. Report omissions truthfully.
