const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const test = require('node:test');

const { MAX_SESSION_CONTEXT_CHARS, MAX_SUBAGENT_CONTEXT_CHARS } = require('../../hooks/config');
const { getSessionContext, getSubagentContext } = require('../../hooks/kernel');
const { buildCodexOutput } = require('../../adapters/codex/hooks/runtime');
const { buildClaudeCodeOutput } = require('../../adapters/claude-code/hooks/runtime');
const codexHooksConfig = require('../../hooks/hooks.json');
const claudeHooksConfig = require('../../adapters/claude-code/hooks/hooks.json');

test('SessionStart kernel stays short and preserves core boundaries', () => {
  const context = getSessionContext();
  assert.ok(context.length <= MAX_SESSION_CONTEXT_CHARS);
  assert.match(context, /project authority\/runtime/);
  assert.match(context, /requested path/);
  assert.match(context, /tools\/sessions grant no authority/);
  assert.match(context, /project\/framework\/platform/);
  assert.match(context, /reuse evidence/);
  assert.match(context, /bound missing\/changed reads\/outputs/);
  assert.match(context, /durable task/);
  assert.match(context, /active lessons/);
  assert.match(context, /gates cover only material residual risk/);
  assert.match(context, /Valid output beats bookkeeping/);
  assert.match(context, /stale records alone do not invalidate it/);
  assert.match(context, /identity\/safety\/authorization\/side-effect\/release controls/);
  assert.match(context, /preflight\/Delivery Change Unit/);
  assert.match(context, /task branch/);
  assert.match(context, /worktree unless exclusive/);
  assert.match(context, /never edit integration lines\/reuse sealed work/);
  assert.match(context, /verify\/commit/);
  assert.match(context, /feedback CLI/);
  assert.match(context, /not user requests/i);
  assert.match(context, /expose no IDs/);
  assert.doesNotMatch(context, /BuildOS feedback candidate:/);
  assert.match(context, /unverified\/undeployed\/unpublished is incomplete/);
});

test('SessionStart identifies the exact installed internal snapshot', () => {
  const pluginRoot = fs.mkdtempSync(path.join(os.tmpdir(), 'senmu-buildos-kernel-'));
  fs.writeFileSync(path.join(pluginRoot, '.senmu-buildos-install.json'), JSON.stringify({
    version: '1.14.2',
    source_commit: '1234567890abcdef',
  }));
  const context = getSessionContext(pluginRoot);
  assert.match(context, /Active snapshot: 1\.14\.2@1234567890ab/);
  assert.ok(context.length <= MAX_SESSION_CONTEXT_CHARS);
});

test('SubagentStart kernel stays shorter than the session kernel', () => {
  const session = getSessionContext();
  const subagent = getSubagentContext();
  assert.ok(subagent.length <= MAX_SUBAGENT_CONTEXT_CHARS);
  assert.ok(subagent.length < session.length);
  assert.match(subagent, /Stay within delegated scope/);
  assert.match(subagent, /requested path/);
  assert.match(subagent, /project\/framework\/platform capabilities and evidence/);
  assert.match(subagent, /bounded missing\/changed guidance or outputs/);
  assert.match(subagent, /verified stable commit/);
  assert.match(subagent, /never edit integration lines or reuse sealed work/);
  assert.match(subagent, /gaps, blockers and risk/);
});

test('Codex output uses lifecycle additionalContext', () => {
  const output = buildCodexOutput('SessionStart', 'context');
  assert.equal(output.systemMessage, undefined);
  assert.deepEqual(output.hookSpecificOutput, {
    hookEventName: 'SessionStart',
    additionalContext: 'context',
  });
});

test('Claude Code output uses its documented lifecycle additionalContext', () => {
  const output = buildClaudeCodeOutput('SessionStart', 'context');
  assert.equal(output.systemMessage, undefined);
  assert.deepEqual(output.hookSpecificOutput, {
    hookEventName: 'SessionStart',
    additionalContext: 'context',
  });
});

test('plugin hooks use Codex-native plugin paths and bounded context', () => {
  const session = codexHooksConfig.hooks.SessionStart[0].hooks[0];
  const subagent = codexHooksConfig.hooks.SubagentStart[0].hooks[0];
  const sessionContext = getSessionContext();
  const subagentContext = getSubagentContext();
  assert.match(session.command, /\$\{PLUGIN_ROOT\}/);
  assert.match(subagent.command, /\$\{PLUGIN_ROOT\}/);
  assert.ok(session.additionalContextLimit > 0);
  assert.ok(subagent.additionalContextLimit > 0);
  assert.ok(subagent.additionalContextLimit < session.additionalContextLimit);
  assert.ok(sessionContext.length <= session.additionalContextLimit);
  assert.ok(subagentContext.length <= subagent.additionalContextLimit);
  assert.deepEqual(Object.keys(codexHooksConfig.hooks).sort(), ['SessionStart', 'SubagentStart']);
  assert.doesNotMatch(JSON.stringify(codexHooksConfig), /UserPromptSubmit|user-prompt-submit/);
});

test('Claude Code adapter is isolated and does not inspect user prompts', () => {
  const session = claudeHooksConfig.hooks.SessionStart[0].hooks[0];
  const subagent = claudeHooksConfig.hooks.SubagentStart[0].hooks[0];
  assert.match(session.command, /\$\{CLAUDE_PLUGIN_ROOT\}/);
  assert.match(subagent.command, /\$\{CLAUDE_PLUGIN_ROOT\}/);
  assert.match(session.command, /adapters\/claude-code/);
  assert.match(subagent.command, /adapters\/claude-code/);
  assert.deepEqual(Object.keys(claudeHooksConfig.hooks).sort(), ['SessionStart', 'SubagentStart']);
  assert.doesNotMatch(JSON.stringify(claudeHooksConfig), /UserPromptSubmit|user-prompt-submit/);
  assert.doesNotMatch(JSON.stringify(claudeHooksConfig), /curl|wget|git\s|rm\s|\.claude\//i);
});
