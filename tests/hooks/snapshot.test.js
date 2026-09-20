const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const test = require('node:test');

const { getSessionContext, getSubagentContext } = require('../../hooks/kernel');
const { MAX_SESSION_CONTEXT_CHARS, MAX_SUBAGENT_CONTEXT_CHARS } = require('../../hooks/config');

function fixture(t, identity) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'buildos-snapshot-'));
  t.after(() => fs.rmSync(root, { recursive: true, force: true }));
  if (identity !== undefined) {
    fs.writeFileSync(path.join(root, '.senmu-buildos-install.json'), JSON.stringify(identity));
  }
  return root;
}

// These test Hook output, isolation and budgets, not model adherence or host activation.
test('both lifecycle contexts identify the same supplied installation', (t) => {
  const root = fixture(t, { version: '2.10.0', source_commit: 'abcdef0123456789' });
  const suffix = '\n- Active snapshot: 2.10.0@abcdef012345.';
  assert.ok(getSessionContext(root).endsWith(suffix));
  assert.ok(getSubagentContext(root).endsWith(suffix));
});

test('subagents do not reuse another installation identity', (t) => {
  const a = fixture(t, { version: '2.10.0', source_commit: 'aaaaaaaaaaaa1111' });
  const b = fixture(t, { version: '2.10.1', source_commit: 'bbbbbbbbbbbb2222' });
  assert.match(getSubagentContext(a), /2\.10\.0@aaaaaaaaaaaa/);
  assert.match(getSubagentContext(b), /2\.10\.1@bbbbbbbbbbbb/);
  assert.doesNotMatch(getSubagentContext(b), /aaaaaaaaaaaa/);
});

test('an updated installation is read again instead of reporting a cached snapshot', (t) => {
  const root = fixture(t, { version: '2.10.0', source_commit: 'aaaaaaaaaaaa1111' });
  assert.match(getSubagentContext(root), /aaaaaaaaaaaa/);
  fs.writeFileSync(path.join(root, '.senmu-buildos-install.json'), JSON.stringify({
    version: '2.10.1', source_commit: 'bbbbbbbbbbbb2222',
  }));
  assert.match(getSubagentContext(root), /2\.10\.1@bbbbbbbbbbbb/);
});

test('missing optional metadata does not invent snapshot evidence', (t) => {
  const root = fixture(t);
  for (const getContext of [getSessionContext, getSubagentContext]) {
    assert.doesNotMatch(getContext(root), /Active snapshot:/);
  }
});

test('invalid optional JSON does not break either lifecycle context', (t) => {
  const root = fixture(t);
  fs.writeFileSync(path.join(root, '.senmu-buildos-install.json'), '{');
  for (const getContext of [getSessionContext, getSubagentContext]) {
    assert.doesNotMatch(getContext(root), /Active snapshot:/);
  }
});

test('incomplete optional identity is not presented as an installed revision', (t) => {
  const root = fixture(t, { version: '2.10.0' });
  for (const getContext of [getSessionContext, getSubagentContext]) {
    assert.doesNotMatch(getContext(root), /Active snapshot:/);
  }
});

test('both populated contexts retain the existing length budgets', (t) => {
  const root = fixture(t, { version: '9999.9999.9999', source_commit: '1234567890abcdef' });
  const session = getSessionContext(root);
  const subagent = getSubagentContext(root);
  assert.ok(session.length <= MAX_SESSION_CONTEXT_CHARS);
  assert.ok(subagent.length <= MAX_SUBAGENT_CONTEXT_CHARS);
  assert.ok(subagent.length < session.length);
});

test('reading either context leaves the installation metadata unchanged', (t) => {
  const root = fixture(t, { version: '2.10.0', source_commit: 'abcdef0123456789' });
  const file = path.join(root, '.senmu-buildos-install.json');
  const before = fs.readFileSync(file);
  getSessionContext(root);
  getSubagentContext(root);
  assert.deepEqual(fs.readFileSync(file), before);
  assert.deepEqual(fs.readdirSync(root), ['.senmu-buildos-install.json']);
});
