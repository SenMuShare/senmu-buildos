# {{PROJECT_NAME}} Agent Register

> Document state: draft
> Calibration date: {{DATE}}

This is the project's agent index, not a second prompt body. Register only actual business agents, never root `AGENTS.md` or Skill display metadata such as `agents/openai.yaml`. Localize human-readable prose according to project language; keep stable keys and machine field labels unchanged.

## Identity and Placement

The default definition is `agents/{agent-key}/AGENT.md`; keep the stable lowercase kebab-case key when changing the display name. Existing projects may retain their registered authoritative layout. Use Git/version evidence and run records instead of parallel definition copies; versioned runtime artifacts need an actual parallel consumer.

| Agent Key | Agent Name | Agent Version | Status | Definition Path | Owner | Workflow / Runtime |
| --- | --- | --- | --- | --- | --- | --- |

Allowed states: `draft`, `active`, `deprecated`, `retired`. An empty draft does not invent active agents. Runs identify the actual key, prompt version, source commit/artifact and runtime entrypoint.

## Change and Retirement

Update definition/version evidence, this index and affected consumers together after an authorized content or contract change. Single-run subjects, steps, attempts and checkpoints belong to the existing run owner, not a new definition version. `deprecated` permits approved compatibility; `retired` must not start new runs. Record replacements and recovery in the definition or existing project map. Registration is not approval to activate, execute or publish.
