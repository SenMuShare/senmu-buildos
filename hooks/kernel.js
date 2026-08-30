const fs = require('node:fs');
const path = require('node:path');

const { MAX_SESSION_CONTEXT_CHARS, MAX_SUBAGENT_CONTEXT_CHARS } = require('./config');

const SESSION_CONTEXT = `SENMU BUILDOS KERNEL

- User request and real project authority/runtime define facts.
- Confirm scope/unit, authority, requested path and risk/reversibility; tools/sessions grant no authority.
- Start with owners and project/framework/platform; reuse evidence; bound missing/changed reads and outputs.
- Recover from durable task and active lessons; chat/Hooks are not owners.
- Prevent requirement/ownership/architecture/interface/flow defects; gates cover only material residual risk.
- Before edits, pass preflight or prepare a Delivery Change Unit; preserve dirt; use a task branch and worktree unless exclusive; never edit integration lines or reuse sealed work; verify and commit.
- Fail closed for security/privacy/permissions/payment/production data/destruction/release integrity.
- Report BuildOS harm via feedback CLI, not user requests; expose no IDs.
- Leave verification, risks and handoff; unverified/undeployed/unpublished is incomplete.`;

const SUBAGENT_CONTEXT = `SENMU BUILDOS SUBAGENT

- Stay within delegated scope, requested path, write boundary, unit and authority.
- Read authoritative owners and real state.
- Reuse project/framework/platform capabilities and evidence; acquire bounded missing/changed guidance or outputs.
- Before edits, verify task branch/Change Unit; never edit integration lines or reuse sealed work; return a verified stable commit.
- Keep security, data, destructive and release gates.
- Return evidence, gaps, blockers and risk.`;

function assertWithinBudget(context, maxChars, label) {
  if (context.length > maxChars) {
    throw new Error(`${label} context exceeds ${maxChars} characters`);
  }
  return context;
}

function readInstallIdentity(pluginRoot = path.resolve(__dirname, '..')) {
  const identityPath = path.join(pluginRoot, '.senmu-buildos-install.json');
  if (!fs.existsSync(identityPath)) return null;
  try {
    const identity = JSON.parse(fs.readFileSync(identityPath, 'utf8'));
    if (!identity.version || !identity.source_commit) return null;
    return identity;
  } catch {
    return null;
  }
}

function getSessionContext(pluginRoot) {
  const identity = readInstallIdentity(pluginRoot);
  const snapshot = identity
    ? `\n- Active snapshot: ${identity.version}@${String(identity.source_commit).slice(0, 12)}.`
    : '';
  return assertWithinBudget(`${SESSION_CONTEXT}${snapshot}`, MAX_SESSION_CONTEXT_CHARS, 'SessionStart');
}

function getSubagentContext() {
  return assertWithinBudget(SUBAGENT_CONTEXT, MAX_SUBAGENT_CONTEXT_CHARS, 'SubagentStart');
}

module.exports = {
  getSessionContext,
  getSubagentContext,
  readInstallIdentity,
};
