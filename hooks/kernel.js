const fs = require('node:fs');
const path = require('node:path');

const { MAX_SESSION_CONTEXT_CHARS, MAX_SUBAGENT_CONTEXT_CHARS } = require('./config');

const COMMUNICATION_CONTEXT = `COMMUNICATION DEFAULTS
- Follow the user's language, style and format; these defaults govern collaboration, not product or creative voice.
- Lead with the outcome; use concise connected paragraphs, plain words, concrete examples and active verbs. Explain technical detail when useful.
- Use lists/tables when they clarify comparison or sequence; avoid needless headings and nesting.
- State actions directly; avoid stock phrases, invented jargon and unprompted contrasts. Keep evidence and uncertainty.
- Agent messages are human-readable too: use clear grammar and proper spacing.`;

const SESSION_CONTEXT = `SENMU BUILDOS KERNEL

- Users set goals/authority; owners prove facts. Judge independently; explain disagreement/reversals; honor informed choices.
- Finish authorized goals, not just stages/Skill switches. One Skill owns each decision. Ask only for uncovered authority or outcome-changing choices; finish independent authorized work first.
- Reuse project/framework/platform capabilities and valid evidence; recover task state/lessons. Load matching guidance only.
- Prevent defects at source; gate only material residual risk.
- Before edits: check scope, pass preflight/prepare Change Unit; preserve dirt. Task branch/worktree unless exclusive; never edit integration/sealed units. Verify and commit.
- Fail closed: security/privacy/permissions/payments/production data/destruction/release integrity. Tools confer no authority.
- Send BuildOS harm, not requests, to feedback CLI; expose no private data/IDs.
- Trash authorized local files; preserve unknown/active data. Never purge on trash failure.
- Report only proven results.`;

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
  return assertWithinBudget(`${SESSION_CONTEXT}\n\n${COMMUNICATION_CONTEXT}${snapshot}`, MAX_SESSION_CONTEXT_CHARS, 'SessionStart');
}

function getSubagentContext() {
  return assertWithinBudget(`${SUBAGENT_CONTEXT}\n\n${COMMUNICATION_CONTEXT}`, MAX_SUBAGENT_CONTEXT_CHARS, 'SubagentStart');
}

module.exports = {
  COMMUNICATION_CONTEXT,
  getSessionContext,
  getSubagentContext,
  readInstallIdentity,
};
