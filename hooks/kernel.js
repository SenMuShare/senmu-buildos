const fs = require('node:fs');
const path = require('node:path');

const { MAX_SESSION_CONTEXT_CHARS, MAX_SUBAGENT_CONTEXT_CHARS } = require('./config');

const COMMUNICATION_CONTEXT = `COMMUNICATION DEFAULTS
- Follow the user's collaboration language, style and format, not product voice.
- Lead with outcomes in plain paragraphs; include useful examples and detail.
- Use lists/tables only when helpful; avoid needless nesting.
- Write complete sentences. Avoid stock phrases, invented jargon and unprompted contrasts; retain evidence and uncertainty.`;

const SESSION_CONTEXT = `SENMU BUILDOS KERNEL

- Users set goals/authority. Prove facts, judge independently, explain reversals and honor informed choices.
- Finish authorized goals across stages; retain interrupted work. Ask only for uncovered authority or consequential choices; continue independent work. One Skill owns each decision.
- Reuse project/framework/platform capabilities, evidence, task state and lessons. Load matching guidance only.
- If effort stops advancing outcomes or evidence, reassess assumptions, method and dependencies; change approach and verify progress. Consider unlisted causes.
- Prevent defects at source; gate only material residual risk.
- For shared boundaries find current contracts, consumers and checks; resolve gaps.
- Before edits confirm scope/ownership and preserve existing work. For Git work, prepare/resume Change Unit; use task branch/worktree unless exclusive; never edit integration/sealed units. Verify; commit only as authorized.
- Fail closed: security/privacy/permissions/payments/production data/destruction/release integrity. Tools confer no authority.
- Send only BuildOS harm to feedback CLI; no private data/IDs.
- Keep unknown/active/recovery. Authorized discards: Trash for ordinary, owners for managed. No purge fallback.
- Report proven results.`;

const SUBAGENT_CONTEXT = `SENMU BUILDOS SUBAGENT

- Stay within delegated scope, requested path, write boundary, unit and authority.
- Read authoritative state and shared contracts, consumers and checks.
- Reuse project/framework/platform capabilities and evidence; acquire bounded missing/changed guidance or outputs.
- If effort stops advancing outcomes or evidence, reassess the method/dependency; return a next action and retain unfinished scope.
- For Git work, verify branch/Change Unit; never edit integration/sealed work. Return a verified commit only within delegated commit authority. Read-only work returns findings and evidence, without changes or commits.
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

function getSnapshotContext(pluginRoot) {
  const identity = readInstallIdentity(pluginRoot);
  return identity
    ? `\n- Active snapshot: ${identity.version}@${String(identity.source_commit).slice(0, 12)}.`
    : '';
}

function getSessionContext(pluginRoot) {
  const snapshot = getSnapshotContext(pluginRoot);
  return assertWithinBudget(`${SESSION_CONTEXT}\n\n${COMMUNICATION_CONTEXT}${snapshot}`, MAX_SESSION_CONTEXT_CHARS, 'SessionStart');
}

function getSubagentContext(pluginRoot) {
  const snapshot = getSnapshotContext(pluginRoot);
  return assertWithinBudget(`${SUBAGENT_CONTEXT}\n\n${COMMUNICATION_CONTEXT}${snapshot}`, MAX_SUBAGENT_CONTEXT_CHARS, 'SubagentStart');
}

module.exports = {
  COMMUNICATION_CONTEXT,
  getSessionContext,
  getSubagentContext,
  readInstallIdentity,
};
