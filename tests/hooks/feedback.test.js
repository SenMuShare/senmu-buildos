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
  extractUserAuthoredSignalText,
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

test('host-generated suggestions and quoted conversation text are not feedback signals', () => {
  const generated = `# Overview

Generate 0 to 3 hyperpersonalized suggestions based on this context.

The quoted text says: 不对，你又理解错了。`;
  assert.equal(detectPromptSignal(generated), null);

  const referencedConversation = `## Referenced conversation

Assistant: 不对，你又把旧规则读了一遍。

## My request:
请总结这段讨论。`;
  assert.equal(detectPromptSignal(referencedConversation), null);
});

test('only current requests and annotation comments are inspected in structured prompts', () => {
  const correctedRequest = `## Referenced conversation

Assistant: ordinary quoted material

## My request:
不对，你又把一个项目的约定写成通用规则了。`;
  assert.equal(detectPromptSignal(correctedRequest).kind, 'user_correction');

  const neutralAnnotation = `<response-annotations>
[{"text":"不对，你又理解错了。","annotation":"请解释这个结论。"}]
</response-annotations>

## My request:
继续审视。`;
  assert.equal(detectPromptSignal(neutralAnnotation), null);

  const correctiveAnnotation = `<response-annotations>
[{"text":"ordinary selected response","comment":"不能这样，这条规则必须适用于不同项目。"}]
</response-annotations>

## My request:
继续处理。`;
  assert.equal(detectPromptSignal(correctiveAnnotation).kind, 'user_correction');
  assert.equal(
    extractUserAuthoredSignalText(correctiveAnnotation),
    '不能这样，这条规则必须适用于不同项目。\n继续处理。',
  );
});

test('captured excerpts exclude wrappers and quoted material', (t) => {
  const env = temporaryEnvironment(t);
  const candidate = capturePromptCandidate({
    session_id: 'session-wrapper',
    cwd: 'workspace/example-project',
    prompt: `## Referenced conversation

Assistant: quoted material that should not be stored

## My request:
记录反馈：只保存本轮用户真正写下的内容。`,
  }, 'codex', env);

  assert.equal(candidate.signal.excerpt, '记录反馈：只保存本轮用户真正写下的内容。');
  assert.doesNotMatch(candidate.signal.excerpt, /quoted material|Referenced conversation/);
});

test('explicit correction is captured once, locally, with secret redaction', (t) => {
  const env = temporaryEnvironment(t);
  const input = {
    session_id: 'session-1',
    cwd: 'workspace/example-project',
    transcript_path: 'transcripts/session-1.jsonl',
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
        cwd: 'workspace/example-project',
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
    '--project-root', 'workspace/example-project',
    '--session-id', 'session-2',
    '--quiet',
  ], { encoding: 'utf8', env: { ...process.env, ...env } });

  assert.equal(result.status, 0);
  assert.equal(result.stdout, '');
  assert.equal(result.stderr, '');
  assert.equal(listCandidates(env).length, 1);
  assert.equal(listCandidates(env)[0].signal.kind, 'agent_observed_governance_gap');
});

test('feedback review starts with a bounded summary and paginates full candidates', (t) => {
  const env = temporaryEnvironment(t);
  for (let index = 0; index < 12; index += 1) {
    capturePromptCandidate({
      session_id: `session-summary-${index}`,
      cwd: 'workspace/example-project',
      prompt: `记录反馈：第 ${index} 条规则造成了重复返工。`,
    }, 'codex', env);
  }
  const cli = path.join(__dirname, '../../hooks/feedback-cli.js');
  const summary = childProcess.spawnSync(process.execPath, [cli, 'pending', '--summary'], {
    encoding: 'utf8', env: { ...process.env, ...env },
  });
  assert.equal(summary.status, 0);
  const summaryPayload = JSON.parse(summary.stdout);
  assert.equal(summaryPayload.count, 12);
  assert.equal(summaryPayload.by_source_host.codex, 12);
  assert.equal(summaryPayload.next, 'pending --json --limit 10 --offset 0');
  assert.ok(summary.stdout.length < 1000);

  const legacy = childProcess.spawnSync(process.execPath, [cli, 'pending', '--json'], {
    encoding: 'utf8', env: { ...process.env, ...env },
  });
  assert.equal(legacy.status, 0);
  assert.equal(JSON.parse(legacy.stdout).length, 12);

  const page = childProcess.spawnSync(process.execPath, [
    cli, 'pending', '--json', '--limit', '5', '--offset', '5',
  ], { encoding: 'utf8', env: { ...process.env, ...env } });
  assert.equal(page.status, 0);
  const pagePayload = JSON.parse(page.stdout);
  assert.equal(pagePayload.total, 12);
  assert.equal(pagePayload.returned, 5);
  assert.equal(pagePayload.offset, 5);
  assert.equal(pagePayload.has_more, true);
  assert.equal(pagePayload.candidates.length, 5);
});

test('review decisions remove candidates from the pending inbox without deleting evidence', (t) => {
  const env = temporaryEnvironment(t);
  const candidate = capturePromptCandidate({
    session_id: 'session-3',
    cwd: 'workspace/example-project',
    prompt: '记录反馈：这个规则在两个项目里都造成了返工。',
  }, 'claude-code', env);

  decideCandidate(candidate.id, 'buildos_candidate', 'Review in the BuildOS source repository.', env);
  assert.equal(listCandidates(env).length, 0);
  const all = listCandidates(env, true);
  assert.equal(all.length, 1);
  assert.equal(all[0].decision.disposition, 'buildos_candidate');
  assert.ok(fs.existsSync(path.join(feedbackPaths(env).inbox, `${candidate.id}.json`)));
});
