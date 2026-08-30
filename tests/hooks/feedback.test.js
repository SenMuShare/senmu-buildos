const assert = require('node:assert/strict');
const childProcess = require('node:child_process');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const test = require('node:test');

const {
  decideCandidate,
  feedbackPaths,
  listCandidates,
  persistCandidate,
} = require('../../hooks/feedback');

const cli = path.join(__dirname, '../../hooks/feedback-cli.js');

function temporaryEnvironment(t) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'senmu-feedback-'));
  t.after(() => fs.rmSync(root, { recursive: true, force: true }));
  return { SENMU_BUILDOS_DATA_DIR: root };
}

function submit(env, ...args) {
  return childProcess.spawnSync(process.execPath, [cli, 'submit', ...args], {
    encoding: 'utf8',
    env: { ...process.env, ...env },
  });
}

function createCandidate(env, index = 0) {
  return persistCandidate({
    input: {
      session_id: `session-${index}`,
      cwd: 'workspace/example-project',
      transcript_path: `transcripts/session-${index}.jsonl`,
    },
    host: 'agent',
    sourceKind: 'agent_report',
    signalKind: 'agent_observed_governance_gap',
    reason: 'Agent reported a concrete BuildOS usage problem',
    component: 'senmu-build-delivery',
    excerpt: `Change Unit guidance caused duplicate work ${index}.`,
    impact: 'The Agent repeated an already completed integration step.',
    workaround: 'Read the Git graph directly.',
  }, env);
}

test('agent submission requires a BuildOS component and concrete impact', (t) => {
  const env = temporaryEnvironment(t);
  const missingBoundary = submit(env, '--summary', 'The guidance was confusing.');
  assert.notEqual(missingBoundary.status, 0);
  assert.match(missingBoundary.stderr, /--component, --summary and --impact are required/);
  assert.equal(listCandidates(env).length, 0);
});

test('quiet agent submission records a BuildOS usage problem without user-facing output', (t) => {
  const env = temporaryEnvironment(t);
  const result = submit(
    env,
    '--component', 'senmu-build-delivery',
    '--summary', 'The release rule sent the Agent back through an already completed step.',
    '--impact', 'It added duplicate work and delayed the result.',
    '--workaround', 'The Agent reconstructed the state from Git.',
    '--project-root', 'workspace/example-project',
    '--session-id', 'session-2',
    '--evidence', 'transcripts/session-2.jsonl',
    '--quiet',
  );

  assert.equal(result.status, 0);
  assert.equal(result.stdout, '');
  assert.equal(result.stderr, '');
  const [candidate] = listCandidates(env);
  assert.equal(candidate.source.host, 'agent');
  assert.equal(candidate.signal.component, 'senmu-build-delivery');
  assert.match(candidate.signal.impact, /duplicate work/);
  assert.match(candidate.signal.workaround, /Git/);
  if (process.platform !== 'win32') {
    const candidatePath = path.join(feedbackPaths(env).inbox, `${candidate.id}.json`);
    assert.equal(fs.statSync(candidatePath).mode & 0o777, 0o600);
  }
});

test('candidate fields are deduplicated and redact sensitive values', (t) => {
  const env = temporaryEnvironment(t);
  const first = createCandidate(env, 1);
  const second = createCandidate(env, 1);
  const secret = persistCandidate({
    input: { session_id: 'secret', cwd: 'workspace/example-project' },
    host: 'agent',
    sourceKind: 'agent_report',
    signalKind: 'agent_observed_governance_gap',
    reason: 'Agent reported a concrete BuildOS usage problem',
    component: 'senmu-build-engineering',
    excerpt: 'Template exposed api_key=sk-secretvalue123456789',
    impact: 'The guidance encouraged unsafe evidence capture.',
  }, env);

  assert.equal(first.id, second.id);
  assert.equal(first.created, true);
  assert.equal(second.created, false);
  assert.match(secret.signal.excerpt, /\[redacted/);
  assert.doesNotMatch(secret.signal.excerpt, /secretvalue/);
});

test('feedback review summarizes BuildOS components and source projects before pagination', (t) => {
  const env = temporaryEnvironment(t);
  for (let index = 0; index < 12; index += 1) createCandidate(env, index);

  const summary = childProcess.spawnSync(process.execPath, [cli, 'pending', '--summary'], {
    encoding: 'utf8', env: { ...process.env, ...env },
  });
  assert.equal(summary.status, 0);
  const payload = JSON.parse(summary.stdout);
  assert.equal(payload.count, 12);
  assert.equal(payload.by_source_host.agent, 12);
  assert.equal(payload.by_source_project['workspace/example-project'], 12);
  assert.equal(payload.by_buildos_component['senmu-build-delivery'], 12);
  assert.equal(payload.next, 'pending --json --limit 10 --offset 0');
  assert.ok(summary.stdout.length < 1200);

  const page = childProcess.spawnSync(process.execPath, [
    cli, 'pending', '--json', '--limit', '5', '--offset', '5',
  ], { encoding: 'utf8', env: { ...process.env, ...env } });
  const pagePayload = JSON.parse(page.stdout);
  assert.equal(pagePayload.total, 12);
  assert.equal(pagePayload.returned, 5);
  assert.equal(pagePayload.has_more, true);
});

test('review decisions close a candidate without deleting its evidence', (t) => {
  const env = temporaryEnvironment(t);
  const candidate = createCandidate(env, 3);

  decideCandidate(candidate.id, 'buildos_candidate', 'Review in the BuildOS source repository.', env);
  assert.equal(listCandidates(env).length, 0);
  const all = listCandidates(env, true);
  assert.equal(all.length, 1);
  assert.equal(all[0].decision.disposition, 'buildos_candidate');
  assert.ok(fs.existsSync(path.join(feedbackPaths(env).inbox, `${candidate.id}.json`)));
});
