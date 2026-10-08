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

test('classification, follow-up and resolution are not conflated', (t) => {
  const env = temporaryEnvironment(t);
  const needs = createCandidate(env, 21);
  const accepted = createCandidate(env, 22);
  const discarded = createCandidate(env, 23);
  decideCandidate(needs.id, 'needs_evidence', 'Need a local execution receipt.', env,
    { trackingRef: 'issue:example/repo#7' });
  decideCandidate(accepted.id, 'buildos_candidate', 'Accepted, implementation not verified.', env);
  decideCandidate(discarded.id, 'discard', 'Synthetic duplicate; original is tracked separately.', env);
  function query(...args) {
    const result = childProcess.spawnSync(process.execPath, [cli, ...args], {
      encoding: 'utf8', env: { ...process.env, ...env },
    });
    assert.equal(result.status, 0, result.stderr);
    return JSON.parse(result.stdout);
  }
  const pending = query('pending', '--summary');
  assert.equal(pending.count, 0);
  assert.equal(pending.queue_semantics, 'awaiting_first_decision');
  const followup = query('followup', '--summary');
  assert.equal(followup.count, 2);
  assert.equal(followup.queue_semantics, 'owner_status_not_queried');
  assert.equal(followup.by_disposition.needs_evidence, 1);
  const page = query('followup', '--json', '--limit', '10');
  assert.equal(page.returned, 2);
  const all = query('all', '--json');
  assert.equal(all.length, 3);
  assert.equal(all.find(c => c.id === needs.id).decision.tracking_ref, 'issue:example/repo#7');
  assert.throws(() => decideCandidate(needs.id, 'discard', 'Do not overwrite.', env), /already decided/);
});

test('decision IDs cannot traverse outside the feedback inbox', (t) => {
  const env = temporaryEnvironment(t);
  assert.throws(() => decideCandidate('../outside', 'discard', 'no', env), /invalid candidate ID/);
  assert.equal(fs.existsSync(feedbackPaths(env).decisions), false);
});

test('legacy decisions can acquire idempotent tracking links without rewriting evidence', (t) => {
  const env = temporaryEnvironment(t);
  const candidate = createCandidate(env, 30);
  const decision = decideCandidate(candidate.id, 'buildos_candidate', 'Accepted for investigation.', env);
  const original = fs.readFileSync(decision.filePath);
  const rawCandidate = fs.readFileSync(candidate.filePath);
  const args = [cli, 'link', '--id', candidate.id, '--tracking-ref', 'tasks/repair.md',
    '--note', 'Implementation has not been verified.'];
  for (let attempt = 0; attempt < 2; attempt += 1) {
    const linked = childProcess.spawnSync(process.execPath, args, {
      encoding: 'utf8', env: { ...process.env, ...env },
    });
    assert.equal(linked.status, 0, linked.stderr);
  }
  assert.deepEqual(fs.readFileSync(decision.filePath), original);
  assert.deepEqual(fs.readFileSync(candidate.filePath), rawCandidate);
  const [item] = listCandidates(env, true);
  assert.deepEqual(item.tracking_refs, ['tasks/repair.md']);
  assert.equal(item.decision.disposition, 'buildos_candidate');
  const summary = childProcess.spawnSync(process.execPath, [cli, 'followup', '--summary'], {
    encoding: 'utf8', env: { ...process.env, ...env },
  });
  const payload = JSON.parse(summary.stdout);
  assert.deepEqual(payload.followup_tracking, { required: 1, linked: 1, missing: 0 });
  assert.equal(payload.queue_semantics, 'owner_status_not_queried');
  assert.equal(payload.count, 1);
});

test('followup exposes missing links and retains both initial and later owners', (t) => {
  const env = temporaryEnvironment(t);
  const tracked = createCandidate(env, 31);
  const missing = createCandidate(env, 32);
  decideCandidate(tracked.id, 'project', 'Project repair.', env, { trackingRef: 'issues/31' });
  decideCandidate(missing.id, 'needs_evidence', 'Reproduction pending.', env);
  const linked = childProcess.spawnSync(process.execPath, [cli, 'link', '--id', tracked.id,
    '--tracking-ref', 'tasks/followup.md'], { encoding: 'utf8', env: { ...process.env, ...env } });
  assert.equal(linked.status, 0, linked.stderr);
  const item = listCandidates(env, true).find(c => c.id === tracked.id);
  assert.deepEqual(item.tracking_refs, ['issues/31', 'tasks/followup.md']);
  const summary = childProcess.spawnSync(process.execPath, [cli, 'followup', '--summary'], {
    encoding: 'utf8', env: { ...process.env, ...env },
  });
  assert.deepEqual(JSON.parse(summary.stdout).followup_tracking, { required: 2, linked: 1, missing: 1 });
});

test('tracking links require a classified existing candidate and nonempty reference', (t) => {
  const env = temporaryEnvironment(t);
  const candidate = createCandidate(env, 33);
  for (const args of [
    ['--id', candidate.id, '--tracking-ref', 'tasks/not-yet.md'],
    ['--id', '../outside', '--tracking-ref', 'tasks/unsafe.md'],
    ['--id', 'FB-0000000000000000', '--tracking-ref', 'tasks/missing.md'],
  ]) {
    const result = childProcess.spawnSync(process.execPath, [cli, 'link', ...args], {
      encoding: 'utf8', env: { ...process.env, ...env },
    });
    assert.notEqual(result.status, 0);
  }
  decideCandidate(candidate.id, 'project', 'Project work.', env);
  const blank = childProcess.spawnSync(process.execPath, [cli, 'link', '--id', candidate.id,
    '--tracking-ref', '  '], { encoding: 'utf8', env: { ...process.env, ...env } });
  assert.notEqual(blank.status, 0);
});
