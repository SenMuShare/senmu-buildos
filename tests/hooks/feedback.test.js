const assert = require('node:assert/strict');
const childProcess = require('node:child_process');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const test = require('node:test');

const {
  capturePromptCandidate,
  decideCandidate,
  detectPromptSignal,
  feedbackPaths,
  listCandidates,
} = require('../../hooks/feedback');

function temporaryEnvironment(t) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'senmu-feedback-'));
  t.after(() => fs.rmSync(root, { recursive: true, force: true }));
  return { SENMU_BUILDOS_DATA_DIR: root };
}

test('ordinary prompts do not create feedback candidates', () => {
  assert.equal(detectPromptSignal('Please add a normal unit test.'), null);
  assert.equal(detectPromptSignal('Please implement a customer feedback form.'), null);
  assert.equal(detectPromptSignal('你又可以帮我写一份 README 吗？'), null);
  assert.equal(detectPromptSignal('What does BuildOS feedback candidate mean?'), null);
  assert.equal(detectPromptSignal('这个 BuildOS 反馈候选和意见箱是干嘛的？'), null);
});

test('explicit feedback actions still create a capture signal', () => {
  assert.equal(detectPromptSignal('Please record this feedback.').kind, 'explicit_feedback');
  assert.equal(detectPromptSignal('记录反馈：这个边界需要收紧。').kind, 'explicit_feedback');
});

test('explicit correction is captured once, locally, with secret redaction', (t) => {
  const env = temporaryEnvironment(t);
  const input = {
    session_id: 'session-1',
    cwd: '/work/private-project',
    transcript_path: '/transcripts/session-1.jsonl',
    prompt: '不对，你又让 POC 阻塞发布了，api_key=sk-secretvalue123456789',
  };
  const first = capturePromptCandidate(input, 'codex', env);
  const second = capturePromptCandidate(input, 'codex', env);

  assert.equal(first.id, second.id);
  assert.equal(first.created, true);
  assert.equal(second.created, false);
  assert.match(first.signal.excerpt, /\[redacted/);
  assert.doesNotMatch(first.signal.excerpt, /secretvalue/);
  assert.equal(listCandidates(env).length, 1);
  if (process.platform !== 'win32') {
    assert.equal(fs.statSync(first.filePath).mode & 0o777, 0o600);
  }
});

test('prompt hooks capture corrections without injecting model context', (t) => {
  for (const [host, script] of [
    ['codex', '../../adapters/codex/hooks/user-prompt-submit.js'],
    ['claude-code', '../../adapters/claude-code/hooks/user-prompt-submit.js'],
  ]) {
    const env = temporaryEnvironment(t);
    const result = childProcess.spawnSync(process.execPath, [path.join(__dirname, script)], {
      encoding: 'utf8',
      env: { ...process.env, ...env },
      input: JSON.stringify({
        session_id: `session-${host}`,
        cwd: '/work/project',
        prompt: '不对，你又把项目规则重复写进 Skill 了。',
      }),
    });

    assert.equal(result.status, 0);
    assert.equal(result.stdout, '{}');
    assert.equal(result.stderr, '');
    assert.equal(listCandidates(env).length, 1);
    assert.equal(listCandidates(env)[0].source.host, host);
  }
});

test('quiet agent submission writes locally without user-facing output', (t) => {
  const env = temporaryEnvironment(t);
  const result = childProcess.spawnSync(process.execPath, [
    path.join(__dirname, '../../hooks/feedback-cli.js'),
    'submit',
    '--summary', 'Release scope was coupled to an unrelated POC branch.',
    '--project-root', '/work/project',
    '--session-id', 'session-2',
    '--quiet',
  ], { encoding: 'utf8', env: { ...process.env, ...env } });

  assert.equal(result.status, 0);
  assert.equal(result.stdout, '');
  assert.equal(result.stderr, '');
  assert.equal(listCandidates(env).length, 1);
  assert.equal(listCandidates(env)[0].signal.kind, 'agent_observed_governance_gap');
});

test('review decisions remove candidates from the pending inbox without deleting evidence', (t) => {
  const env = temporaryEnvironment(t);
  const candidate = capturePromptCandidate({
    session_id: 'session-3',
    cwd: '/work/project',
    prompt: '记录反馈：这个规则在两个项目里都造成了返工。',
  }, 'claude-code', env);

  decideCandidate(candidate.id, 'buildos_candidate', 'Review in the BuildOS source repository.', env);
  assert.equal(listCandidates(env).length, 0);
  const all = listCandidates(env, true);
  assert.equal(all.length, 1);
  assert.equal(all[0].decision.disposition, 'buildos_candidate');
  assert.ok(fs.existsSync(path.join(feedbackPaths(env).inbox, `${candidate.id}.json`)));
});
