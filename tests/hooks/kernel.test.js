const assert = require('node:assert/strict');
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
  assert.match(context, /real project authority/);
  assert.match(context, /load only needed Skill/);
  assert.match(context, /declared durable task owner/);
  assert.match(context, /applicable active lessons/);
  assert.match(context, /gates only cover material residual risk/);
  assert.match(context, /feedback CLI/);
  assert.match(context, /silently/i);
  assert.match(context, /never expose markers\/IDs/);
  assert.doesNotMatch(context, /BuildOS feedback candidate:/);
  assert.match(context, /unverified\/undeployed\/unpublished is incomplete/);
});

test('SubagentStart kernel stays shorter than the session kernel', () => {
  const session = getSessionContext();
  const subagent = getSubagentContext();
  assert.ok(subagent.length <= MAX_SUBAGENT_CONTEXT_CHARS);
  assert.ok(subagent.length < session.length);
  assert.match(subagent, /Do not expand scope/);
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
  assert.deepEqual(Object.keys(codexHooksConfig.hooks).sort(), [
    'SessionStart',
    'SubagentStart',
    'UserPromptSubmit',
  ]);
  assert.match(codexHooksConfig.hooks.UserPromptSubmit[0].hooks[0].command, /user-prompt-submit/);
});

test('Claude Code adapter is isolated and only writes the local feedback inbox', () => {
  const session = claudeHooksConfig.hooks.SessionStart[0].hooks[0];
  const subagent = claudeHooksConfig.hooks.SubagentStart[0].hooks[0];
  assert.match(session.command, /\$\{CLAUDE_PLUGIN_ROOT\}/);
  assert.match(subagent.command, /\$\{CLAUDE_PLUGIN_ROOT\}/);
  assert.match(session.command, /adapters\/claude-code/);
  assert.match(subagent.command, /adapters\/claude-code/);
  assert.deepEqual(Object.keys(claudeHooksConfig.hooks).sort(), [
    'SessionStart',
    'SubagentStart',
    'UserPromptSubmit',
  ]);
  assert.match(claudeHooksConfig.hooks.UserPromptSubmit[0].hooks[0].command, /user-prompt-submit/);
  assert.doesNotMatch(JSON.stringify(claudeHooksConfig), /curl|wget|git\s|rm\s|\.claude\//i);
});
