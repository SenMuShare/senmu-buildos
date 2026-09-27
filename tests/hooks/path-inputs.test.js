const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const test = require('node:test');
const { spawnSync } = require('node:child_process');
const root = path.resolve(__dirname, '../..');
const config = JSON.parse(fs.readFileSync(path.join(root, 'hooks/hooks.json')));

function run(event, values) {
  const env = { ...process.env, PLUGIN_ROOT: '', CLAUDE_PLUGIN_ROOT: '', ZCODE_PLUGIN_ROOT: '', ...values };
  return spawnSync(config.hooks[event][0].hooks[0].command, {
    shell: true, encoding: 'utf8', env, timeout: 5000,
    input: JSON.stringify({ hook_event_name: event, source: 'startup' }),
  });
}

for (const variable of ['PLUGIN_ROOT', 'CLAUDE_PLUGIN_ROOT', 'ZCODE_PLUGIN_ROOT']) {
  for (const event of ['SessionStart', 'SubagentStart']) {
    test(`${event}: ${variable} treats special paths as data`, () => {
      const temp = fs.mkdtempSync(path.join(os.tmpdir(), 'buildos-path-'));
      try {
        for (const name of ['plain plugin', "owner's plugin", '中文 技能', 'quotes" $HOME `literal`']) {
          const install = path.join(temp, name);
          fs.mkdirSync(install);
          fs.cpSync(path.join(root, 'hooks'), path.join(install, 'hooks'), { recursive: true });
          const result = run(event, { [variable]: install });
          assert.equal(result.status, 0, result.stderr);
          const output = JSON.parse(result.stdout);
          assert.deepEqual(Object.keys(output), ['hookSpecificOutput']);
          assert.equal(output.hookSpecificOutput.hookEventName, event);
          const kernel = require(path.join(install, 'hooks/kernel'));
          const expected = event === 'SessionStart' ? kernel.getSessionContext(install) : kernel.getSubagentContext(install);
          assert.equal(output.hookSpecificOutput.additionalContext, expected);
        }
      } finally { fs.rmSync(temp, { recursive: true, force: true }); }
    });
    test(`${event}: ${variable} missing script is an explicit failure`, () => {
      const temp = fs.mkdtempSync(path.join(os.tmpdir(), 'buildos-empty-'));
      try {
        const result = run(event, { [variable]: temp });
        assert.notEqual(result.status, 0);
        assert.equal(result.stdout, '');
        assert.ok(result.stderr.length > 0);
      } finally { fs.rmSync(temp, { recursive: true, force: true }); }
    });
  }
}
for (const event of ['SessionStart', 'SubagentStart']) {
  test(`${event}: missing root does not report silent success`, () => {
    const result = run(event, {});
    assert.equal(result.status, 1);
    assert.equal(result.stdout, '');
    assert.match(result.stderr, /plugin root is unavailable/);
  });
}
