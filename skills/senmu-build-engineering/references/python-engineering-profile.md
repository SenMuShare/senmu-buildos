# Python Engineering Profile

This profile adds Python-specific decisions only. [Source-Code Quality and AI Collaboration](source-code-quality-and-ai-collaboration.md) owns general responsibility, dependencies, errors, review, and AI collaboration; [Software Testing and Quality Verification](software-testing-and-quality-verification.md) owns test scope/evidence; [Implementation Economy and Overengineering](implementation-economy-and-overengineering.md) owns abstraction/platform/configuration justification.

Load this profile for `.py`, `.pyi`, notebooks, Python dependencies, or `pyproject.toml` only when project rules are missing or standards review is explicit. Current project rules, minimum Python version, and tool configuration prevail.

## 1. Versions, Packages, and Dependencies

- Determine minimum Python from `pyproject.toml`, images, CI, or authority—not the agent environment. Do not use newer syntax or standard-library APIs.
- A Python upgrade synchronizes CI, deployment images, type checker, lockfiles, and framework compatibility, not just a version declaration.
- Evaluate `src/` layout for new installable libraries or stable import boundaries; retain better layouts for one-file tools, framework conventions, and legacy apps.
- Maintain dependencies/version ranges in the project's selected owner. Do not let `requirements*.txt`, lockfiles, and `pyproject.toml` conflict.
- Avoid durable dumping grounds such as `utils.py`, `helpers.py`, or `common.py`; name modules for domain or technical boundaries.

## 2. Format, Naming, and Imports

- New projects may default to Ruff formatter/linter. Preserve stable Black, isort, Flake8, Pylint, or other combinations in existing projects unless migration is in scope.
- Put width, target version, and rule set in project configuration so formatting has one result. Do not mix repository-wide formatting into a business change.
- Use `snake_case` for modules/functions/methods/variables, `PascalCase` for classes/exceptions, `UPPER_CASE_WITH_UNDERSCORES` for constants, and suffix exception classes `Error`.
- Use one leading underscore for internal APIs. Prefer predicate names such as `is_`, `has_`, `can_`, and `should_`.
- Avoid shadowing built-ins such as `list`, `dict`, `str`, and `id`; avoid wildcard imports in ordinary business code.
- Group standard-library, third-party, and project imports. Local imports require a real reason—cycle, optional dependency, startup cost—and a clear boundary.
- Do not patch `sys.path` to conceal package defects. Importing a module must not start services, access networks, or write files; put script actions in `main()` behind `if __name__ == "__main__"`.

## 3. Data Model and Abstraction

- Never use mutable defaults such as `items=[]`; default to `None` and create the object inside.
- Prefer named data objects for grouped parameters/fixed returns. Use `dataclass` for lightweight values; consider Pydantic when external validation, serialization, or framework boundaries require it.
- For substitutable behavior, prefer a small `Protocol`, callable, or explicit interface; use abstract base classes only when shared implementation/state exists.
- Do not import Interface/Impl, Factory, or Manager ceremony mechanically. Metaclasses, descriptors, dynamic injection, and monkey patching require a framework contract or verified benefit and an isolated boundary.
- Properties must be cheap, predictable, and free of material side effects. Use methods for remote calls, expensive work, and state mutation.
- ORM, API, domain, and third-party models should not share one role indefinitely. Add explicit conversion when boundary differences create real errors or maintenance cost.

## 4. Types

- Type public functions, data models, and external boundaries accurately. In legacy work, cover new code and core boundaries first, then tighten incrementally.
- Keep `Any` in irreducibly dynamic/third-party adapters. Scope `cast()`, `# type: ignore[...]`, and `# noqa` narrowly with a specific code and reason.
- Type syntax must support the minimum Python version.
- Distinguish nullable values from omitted/defaulted parameters; `None` must not represent several business states.
- Prefer `Enum`, `Literal`, or constrained models for finite states over scattered strings.
- Pyright is a reasonable default. Preserve an established mypy/tool-plugin owner; do not introduce a second checker for duplicate noise.

Types prove structure, not valid amounts, permissions, state transitions, or data ownership; runtime contracts own those.

## 5. Docstrings and Language

Internal projects default to English identifiers and Simplified Chinese business comments/docstrings. International open-source, public SDK, and multinational projects follow project language; never mix randomly within a module.

- Document public modules, classes, functions, and methods. Do not add empty ceremonial prose to short self-explanatory private functions.
- Use `"""` and one project style. Google-style `Args`, `Returns`, and `Raises` is an acceptable default. Explain business meaning, preconditions, side effects, idempotency, and errors without duplicating types.
- Comments explain complex branching, compatibility, transactions, concurrency, retries, performance, or security tradeoffs—not line-by-line behavior.
- Update or remove comments with implementation; do not retain commented-out old code.

```python
def settle_order(order_id: str) -> SettlementResult:
    """结算指定订单。

    同一订单重复调用不会重复记账；只有已支付订单能够进入结算流程。

    Args:
        order_id: 订单唯一标识。

    Returns:
        本次结算结果；已经结算的订单返回原结果。

    Raises:
        OrderNotFoundError: 订单不存在。
        InvalidOrderStateError: 订单状态不允许结算。
    """
```

The Chinese example is retained deliberately to specify the default internal documentation language, not as a parallel runtime rule.

## 6. Python Boundary Conditions

- Catch specific exceptions you can handle. Catch broad `Exception` only at clear process, job, or HTTP boundaries; preserve causes with `raise NewError(...) from exc`.
- Manage files, connections, transactions, locks, and sessions through `with`, `async with`, or framework lifecycles. Use `sys.exit()` only at program entry.
- Do not run blocking network/file operations directly on async paths. Use async clients, a thread boundary, or a job queue with timeouts, cancellation, and cleanup.
- Use timezone-aware values across regions/persistence. Use `Decimal` or integer minor units for money, never binary floating-point settlement.
- Prefer `pathlib`; validate user paths for traversal and authorization boundaries.
- Parse, validate, and convert external JSON, messages, files, and database rows at boundaries. Do not let arbitrary dictionaries permeate domain logic.
- Module-level mutable state, caches, and connections require explicit owner, lifetime, concurrency semantics, and test reset.

## 7. Tests and Tooling

- New projects may default to pytest; preserve project test layout, naming, fixtures, and import mode.
- New `src/` projects may evaluate `--import-mode=importlib`; before changing legacy projects, verify plugins, relative imports, and test entrypoints.
- Unit tests never call real networks, production databases, or paid services. Use project-defined isolated environments and markers for such boundaries.
- Without an existing owner, Ruff formatter/linter, Pyright, and pytest are a reasonable start. Keep actual arguments in `pyproject.toml`, not a duplicated document configuration.
- Local quick checks and CI use the same configuration. Common forms are `ruff format --check .`, `ruff check .`, `pyright`, and `python -m pytest`, but project commands prevail.

## 8. Legacy Migration

- Establish a baseline, then apply minimum rules to new/changed scope. Separate repository-wide formatting, import sorting, and mass typing from behavior changes.
- Retire historical suppressions incrementally; never globally disable unknown warnings merely for green CI. Exceptions need reason, scope, and closeout condition.
- Query current official sources when Python, framework, or tool details may have changed; this profile does not freeze volatile option catalogs.
- Repeated framework-specific rules belong in project/framework authority, not an ever-growing general Python profile.
