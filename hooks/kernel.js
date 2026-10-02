const fs = require('node:fs');
const path = require('node:path');

const { MAX_SESSION_CONTEXT_CHARS, MAX_SUBAGENT_CONTEXT_CHARS } = require('./config');

const COMMUNICATION_CONTEXT = `COMMUNICATION DEFAULTS
- Follow the user's language, style and format for collaboration, not product or creative voice.
- Lead with outcomes in concise connected paragraphs, plain words and concrete examples; explain useful technical detail.
- Use lists or tables when they clarify; avoid needless headings and nesting.
- Use direct, complete sentences with clear grammar and spacing. Avoid stock phrases, invented jargon and unprompted contrasts; preserve evidence and uncertainty.`;

const SESSION_CONTEXT = `SENMU BUILDOS KERNEL

- Users set goals/authority; owners prove facts. Judge independently; explain disagreement/reversals; honor informed choices.
- Finish authorized goals across stages. One Skill owns each decision. Ask only for uncovered authority or consequential choices; finish independent work first.
- Reuse project/framework/platform capabilities, valid evidence and task state/lessons. Load matching guidance only.
- Prevent defects at source; gate only material residual risk.
- For shared-boundary changes, find the current contract, consumers and checks. Resolve missing/conflicting authority; do not guess.
- Before edits: pass scope/ownership write-preflight; prepare/resume Change Unit; preserve dirt. Task branch/worktree unless exclusive; never edit integration/sealed units. Verify; commit only as authorized.
- Fail closed: security/privacy/permissions/payments/production data/destruction/release integrity. Tools confer no authority.
- Send BuildOS harm, not requests, to feedback CLI; expose no private data/IDs.
- Trash authorized local files; preserve unknown/active data. Never purge on trash failure.
- Report only proven results.`;

const SUBAGENT_CONTEXT = `SENMU BUILDOS SUBAGENT

- Stay within delegated scope, requested path, write boundary, unit and authority.
- Read authoritative state; for shared-boundary changes locate the current contract, consumers and checks. Resolve gaps.
- Reuse project/framework/platform capabilities and evidence; acquire bounded missing/changed guidance or outputs.
- For edits, verify branch/Change Unit; never edit integration/sealed work. Return a verified commit only within delegated commit authority. Read-only work returns findings and evidence, without changes or commits.
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
