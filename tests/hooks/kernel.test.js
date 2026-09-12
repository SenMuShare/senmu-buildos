const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const test = require('node:test');

const { MAX_SESSION_CONTEXT_CHARS, MAX_SUBAGENT_CONTEXT_CHARS } = require('../../hooks/config');
const { COMMUNICATION_CONTEXT, getSessionContext, getSubagentContext } = require('../../hooks/kernel');
const { buildCodexOutput } = require('../../adapters/codex/hooks/runtime');
const { buildClaudeCodeOutput } = require('../../adapters/claude-code/hooks/runtime');
const codexHooksConfig = require('../../hooks/hooks.json');
const claudeHooksConfig = require('../../adapters/claude-code/hooks/hooks.json');

// Structural transport checks only. Model adherence is evaluated by real tasks.
test('SessionStart kernel stays within budget and preserves transport boundaries', () => {
  const context = getSessionContext();
  assert.ok(context.length <= MAX_SESSION_CONTEXT_CHARS);
  assert.ok(context.startsWith('SENMU BUILDOS KERNEL'));
  assert.equal(context.split(COMMUNICATION_CONTEXT).length - 1, 1);
  assert.doesNotMatch(context, /BuildOS feedback candidate:/);
});

test('bootstrap adapters receive the same core contract as lifecycle hooks', () => {
  const core = getSessionContext().split('\n\n' + COMMUNICATION_CONTEXT)[0];
  for (const adapter of ['doubao', 'workbuddy', 'zcode']) {
    const source = fs.readFileSync(path.join(__dirname, '../../adapters', adapter, 'kernel/SKILL.md'), 'utf8');
    const actual = source.split('<!-- kernel-contract:start -->')[1].split('<!-- kernel-contract:end -->')[0].trim();
    assert.equal(actual, core, adapter);
  }
});

test('SessionStart identifies the exact installed internal snapshot', () => {
  const pluginRoot = fs.mkdtempSync(path.join(os.tmpdir(), 'senmu-buildos-kernel-'));
  fs.writeFileSync(path.join(pluginRoot, '.senmu-buildos-install.json'), JSON.stringify({
    version: '9999.9999.9999',
    source_commit: '1234567890abcdef',
  }));
  const context = getSessionContext(pluginRoot);
  assert.match(context, /Active snapshot: 9999\.9999\.9999@1234567890ab/);
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

test('shared plugin hooks resolve the plugin root across runtimes', () => {
  const session = codexHooksConfig.hooks.SessionStart[0].hooks[0];
  const subagent = codexHooksConfig.hooks.SubagentStart[0].hooks[0];
  // The dispatch command must keep the Codex-native textual token and the
  // ZCode/Claude Code environment variables, filtering unexpanded literals.
  assert.match(session.command, /\$\{PLUGIN_ROOT\}/);
  assert.match(session.command, /process\.env\.CLAUDE_PLUGIN_ROOT/);
  assert.match(session.command, /process\.env\.ZCODE_PLUGIN_ROOT/);
  assert.match(session.command, /charCodeAt\(0\)!==36/);
  assert.match(session.command, /hooks\/session-start\.js/);
  assert.match(subagent.command, /hooks\/subagent-start\.js/);
  // No matcher so every runtime's SessionStart sources are covered.
  assert.equal(codexHooksConfig.hooks.SessionStart[0].matcher, undefined);
});

test('shared session-start script emits lifecycle additionalContext', () => {
  const { execFileSync } = require('node:child_process');
  const stdout = execFileSync('node', [path.join(__dirname, '..', '..', 'hooks', 'session-start.js')], {
    encoding: 'utf8',
    cwd: path.join(__dirname, '..', '..'),
  });
  const output = JSON.parse(stdout);
  assert.deepEqual(Object.keys(output), ['hookSpecificOutput']);
  assert.equal(output.hookSpecificOutput.hookEventName, 'SessionStart');
  assert.equal(output.hookSpecificOutput.additionalContext, getSessionContext());
});


test('communication defaults reach both lifecycle events and bootstrap installers', () => {
  for (const context of [getSessionContext(), getSubagentContext()]) {
    assert.equal(context.split(COMMUNICATION_CONTEXT).length - 1, 1);
  }
  for (const adapter of ['doubao', 'workbuddy', 'zcode']) {
    const source = fs.readFileSync(path.join(__dirname, '../../adapters', adapter, 'kernel/SKILL.md'), 'utf8');
    const start = '<!-- communication-defaults:start -->';
    const end = '<!-- communication-defaults:end -->';
    assert.equal(source.split(start).length, 2);
    assert.equal(source.split(end).length, 2);
    assert.equal(source.split(start)[1].split(end)[0].trim(), COMMUNICATION_CONTEXT);
  }
});
