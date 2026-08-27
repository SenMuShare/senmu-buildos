const { MAX_SESSION_CONTEXT_CHARS, MAX_SUBAGENT_CONTEXT_CHARS } = require('./config');

const SESSION_CONTEXT = `SENMU BUILDOS KERNEL

- User request and real project authority/runtime evidence define facts.
- Confirm scope, unit, authorization, reversibility and G0-G4 risk.
- Start with active project owners; if they answer, stop; otherwise load only needed Skill/reference.
- Recover from declared durable task owner and applicable active lessons; chat and Hooks are not owners.
- Prevent defects in requirements, ownership, architecture, interfaces, defaults and flow; gates only cover material residual risk.
- Preserve user changes; separate sources, runtime, deliveries, evidence and archives.
- Keep fail-closed gates for security/privacy/permissions/payment/production data/destructive actions/release integrity.
- Silently submit reusable governance gaps with the local feedback CLI when available; never expose markers/IDs or auto-promote them.
- Leave verification, risks and handoff; unverified/undeployed/unpublished is incomplete.`;

const SUBAGENT_CONTEXT = `SENMU BUILDOS SUBAGENT BOUNDARY

- Stay inside the delegated task, write boundary, project or release unit, and authorization. Do not expand scope.
- Read authoritative entrypoints and real state before acting.
- Reuse existing owners; load only guidance needed for this subtask.
- Do not bypass security, data, destructive-action, or release-integrity gates.
- Return paths, evidence, verification, incomplete work, blockers, and residual risk to the parent.`;

function assertWithinBudget(context, maxChars, label) {
  if (context.length > maxChars) {
    throw new Error(`${label} context exceeds ${maxChars} characters`);
  }
  return context;
}

function getSessionContext() {
  return assertWithinBudget(SESSION_CONTEXT, MAX_SESSION_CONTEXT_CHARS, 'SessionStart');
}

function getSubagentContext() {
  return assertWithinBudget(SUBAGENT_CONTEXT, MAX_SUBAGENT_CONTEXT_CHARS, 'SubagentStart');
}

module.exports = {
  getSessionContext,
  getSubagentContext,
};
