const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const test = require('node:test');
const { spawnSync } = require('node:child_process');
const root = path.resolve(__dirname, '../..');

function registrations(event) {
  const manifest = JSON.parse(fs.readFileSync(path.join(root, '.claude-plugin/plugin.json')));
  const defaults = JSON.parse(fs.readFileSync(path.join(root, 'hooks/hooks.json')));
  const configs = [defaults];
  for (const value of manifest.hooks ? [].concat(manifest.hooks) : []) {
    configs.push(typeof value === 'string' ? JSON.parse(fs.readFileSync(path.join(root, value))) : value);
  }
  return configs.flatMap(config => (config.hooks[event] || []).flatMap(group => group.hooks));
}

function invoke(command, event, source, variable, pluginRoot) {
  const env = { ...process.env, PLUGIN_ROOT: '', CLAUDE_PLUGIN_ROOT: '', ZCODE_PLUGIN_ROOT: '' };
  env[variable] = pluginRoot;
  const result = spawnSync(command, { shell: true, encoding: 'utf8', env,
    input: JSON.stringify({ hook_event_name: event, source }), timeout: 10000 });
  assert.equal(result.status, 0, result.stderr);
  const output = JSON.parse(result.stdout);
  assert.deepEqual(Object.keys(output), ['hookSpecificOutput']);
  assert.equal(output.hookSpecificOutput.hookEventName, event);
  return output.hookSpecificOutput.additionalContext;
}

for (const event of ['SessionStart', 'SubagentStart']) {
  test(`${event} has exactly one effective packaged Claude registration`, () => {
    assert.equal(registrations(event).length, 1);
  });
}

test('every lifecycle source emits once in fresh processes without persistent dedup state', () => {
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'buildos hook space-'));
  try {
    fs.cpSync(path.join(root, 'hooks'), path.join(tmp, 'hooks'), { recursive: true });
    const before = fs.readdirSync(tmp).sort();
    const expected = require(path.join(tmp, 'hooks/kernel'));
    for (const source of ['startup', 'resume', 'clear', 'compact', 'fork']) {
      const outputs = registrations('SessionStart').map(hook => invoke(hook.command, 'SessionStart', source, 'CLAUDE_PLUGIN_ROOT', tmp));
      assert.deepEqual(outputs, [expected.getSessionContext(tmp)]);
    }
    const outputs = registrations('SubagentStart').map(hook => invoke(hook.command, 'SubagentStart', '', 'CLAUDE_PLUGIN_ROOT', tmp));
    assert.deepEqual(outputs, [expected.getSubagentContext(tmp)]);
    assert.deepEqual(fs.readdirSync(tmp).sort(), before);
  } finally { fs.rmSync(tmp, { recursive: true, force: true }); }
});

for (const variable of ['PLUGIN_ROOT', 'ZCODE_PLUGIN_ROOT']) {
  test(`shared dispatch still resolves ${variable} for both events`, () => {
    const expected = require('../../hooks/kernel');
    assert.equal(invoke(registrations('SessionStart')[0].command, 'SessionStart', 'startup', variable, root), expected.getSessionContext(root));
    assert.equal(invoke(registrations('SubagentStart')[0].command, 'SubagentStart', '', variable, root), expected.getSubagentContext(root));
  });
}
