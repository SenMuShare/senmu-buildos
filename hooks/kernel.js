const fs = require('node:fs');
const path = require('node:path');

const { MAX_SESSION_CONTEXT_CHARS, MAX_SUBAGENT_CONTEXT_CHARS } = require('./config');

const SESSION_CONTEXT = `SENMU BUILDOS KERNEL

- User request and real project authority/runtime define facts.
- Confirm scope, unit, authorization, reversibility and risk.
- Start with active project owners; load only needed Skill/reference for missing guidance.
- Recover from declared durable task owner and applicable active lessons; chat/Hooks are not owners.
- Prevent defects in requirements, ownership, architecture, interfaces, defaults and flow; gates only cover material residual risk.
- Before edits, pass project preflight or prepare a Delivery Change Unit; preserve dirt, keep one task per branch/worktree unless exclusive, never reuse sealed work; verify and commit.
- Fail closed for security/privacy/permissions/payment/production data/destruction/release integrity.
- Silently send reusable gaps to local feedback CLI; never expose markers/IDs or auto-promote.
- Leave verification, risks and handoff; unverified/undeployed/unpublished is incomplete.`;

const SUBAGENT_CONTEXT = `SENMU BUILDOS SUBAGENT

- Stay inside delegated scope, write boundary, unit and authorization. Do not expand scope.
- Read authoritative entrypoints and real state before acting.
- Reuse owners; load only needed guidance.
- Before source edits, verify the assigned Change Unit isolation; never reuse sealed work, verify and return a stable commit.
- Keep security, data, destructive and release gates.
- Return evidence, incomplete work, blockers and risk.`;

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
