const crypto = require('node:crypto');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');

const SCHEMA_VERSION = 1;
const MAX_EXCERPT_CHARS = 800;
const DISPOSITIONS = new Set([
  'discard',
  'project',
  'buildos_candidate',
  'needs_evidence',
]);

const EXPLICIT_PATTERNS = [
  /\b(?:record|save|submit|add|put|log|remember)\s+(?:this\s+)?(?:as\s+(?:a\s+)?)?(?:buildos\s+)?(?:feedback|feedback candidate|learning candidate|lesson)\b/i,
  /(?:记录|保存|提交|收集|放入|加入|记到|记入).{0,8}(?:BuildOS\s*)?(?:意见箱|反馈候选|反馈|问题|经验)/iu,
];

const CORRECTION_PATTERNS = [
  /(?:不对|不是这个意思|理解错|怎么又|不能这样|不要这样|我再(?:说|强调|提醒)|头痛医头|脚痛医脚)/u,
  /(?:(?:你)?又.{0,18}(?:漏|错|回退|返工|冲突|浪费|弄乱|误解)|(?:导致|造成).{0,18}(?:回退|返工|冲突|浪费))/u,
  /\b(?:that's wrong|that is wrong|not what i meant|you misunderstood|don't do (?:that|this)|regression|rework)\b/i,
];

const AUTOMATED_OVERVIEW_PATTERN = /^\s*# Overview[\s\S]{0,400}\bGenerate 0 to 3 hyperpersonalized suggestions\b/i;
const MY_REQUEST_MARKER = '## My request:';

function normalizeText(value) {
  return String(value || '').replace(/\s+/g, ' ').trim();
}

function redactSensitive(value) {
  return normalizeText(value)
    .replace(/-----BEGIN [^-]+PRIVATE KEY-----[\s\S]*?-----END [^-]+PRIVATE KEY-----/gi, '[redacted:private-key]')
    .replace(/\bBearer\s+[A-Za-z0-9._~+\/-]+=*/gi, 'Bearer [redacted:token]')
    .replace(/\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b/g, '[redacted:jwt]')
    .replace(/\b(?:sk|ghp|github_pat|xox[baprs])-[-A-Za-z0-9_]{12,}\b/gi, '[redacted:token]')
    .replace(/\b(api[_-]?key|access[_-]?token|auth[_-]?token|password|passwd|secret)\b\s*[:=]\s*[^\s,;]+/gi, '$1=[redacted]')
    .slice(0, MAX_EXCERPT_CHARS);
}

function latestUserRequest(value) {
  const markerIndex = value.lastIndexOf(MY_REQUEST_MARKER);
  return markerIndex === -1 ? '' : value.slice(markerIndex + MY_REQUEST_MARKER.length).trim();
}

function responseAnnotationComments(value) {
  const match = value.match(/<response-annotations>\s*([\s\S]*?)\s*<\/response-annotations>/i);
  if (!match) return null;
  try {
    const annotations = JSON.parse(match[1]);
    if (!Array.isArray(annotations)) return [];
    return annotations
      .map((item) => normalizeText(item && (item.annotation || item.comment || item.user_comment)))
      .filter(Boolean);
  } catch {
    return [];
  }
}

function extractUserAuthoredSignalText(prompt) {
  const raw = String(prompt || '');
  if (!raw.trim() || AUTOMATED_OVERVIEW_PATTERN.test(raw)) return '';

  const annotationComments = responseAnnotationComments(raw);
  const request = latestUserRequest(raw);
  if (annotationComments !== null) {
    return [...annotationComments, request].filter(Boolean).join('\n');
  }
  if (request) return request;
  return raw;
}

function detectPromptSignal(prompt) {
  const excerpt = extractUserAuthoredSignalText(prompt);
  const normalized = normalizeText(excerpt);
  if (!normalized) return null;
  if (EXPLICIT_PATTERNS.some((pattern) => pattern.test(normalized))) {
    return { kind: 'explicit_feedback', reason: 'explicit feedback or remember signal', excerpt };
  }
  if (CORRECTION_PATTERNS.some((pattern) => pattern.test(normalized))) {
    return { kind: 'user_correction', reason: 'possible correction, regression, or repeated rework', excerpt };
  }
  return null;
}

function resolveDataRoot(env = process.env) {
  const configured = normalizeText(env.SENMU_BUILDOS_DATA_DIR);
  return configured ? path.resolve(configured) : path.join(os.homedir(), '.senmu-buildos');
}

function feedbackPaths(env = process.env) {
  const root = path.join(resolveDataRoot(env), 'feedback');
  return {
    root,
    inbox: path.join(root, 'inbox'),
    decisions: path.join(root, 'decisions'),
  };
}

function ensurePrivateDirectory(directory) {
  fs.mkdirSync(directory, { recursive: true, mode: 0o700 });
  try {
    fs.chmodSync(directory, 0o700);
  } catch {
    // Permission normalization is best effort on platforms without POSIX modes.
  }
}

function stableId(parts) {
  const digest = crypto.createHash('sha256').update(parts.join('\u0000')).digest('hex');
  return `FB-${digest.slice(0, 16)}`;
}

function writeJsonOnce(filePath, payload) {
  try {
    fs.writeFileSync(filePath, `${JSON.stringify(payload, null, 2)}\n`, {
      encoding: 'utf8',
      flag: 'wx',
      mode: 0o600,
    });
    return true;
  } catch (error) {
    if (error.code === 'EEXIST') return false;
    throw error;
  }
}

function persistCandidate({ input, host, sourceKind, signalKind, reason, excerpt }, env = process.env) {
  const paths = feedbackPaths(env);
  ensurePrivateDirectory(paths.inbox);
  const sessionId = normalizeText(input.session_id || input.sessionId || 'unknown');
  const projectRoot = normalizeText(input.cwd || input.project_root || 'unknown');
  const safeExcerpt = redactSensitive(excerpt);
  const id = stableId([host, sessionId, sourceKind, projectRoot, normalizeText(safeExcerpt).toLowerCase()]);
  const payload = {
    schema_version: SCHEMA_VERSION,
    id,
    status: 'candidate',
    captured_at: new Date().toISOString(),
    source: {
      host,
      kind: sourceKind,
      project_root: projectRoot,
      session_id: sessionId,
      transcript_path: normalizeText(input.transcript_path || ''),
    },
    signal: {
      kind: signalKind,
      reason,
      excerpt: safeExcerpt,
    },
  };
  const filePath = path.join(paths.inbox, `${id}.json`);
  const created = writeJsonOnce(filePath, payload);
  return { ...payload, created, filePath };
}

function capturePromptCandidate(input, host, env = process.env) {
  const signal = detectPromptSignal(input.prompt);
  if (!signal) return null;
  return persistCandidate({
    input,
    host,
    sourceKind: 'user_prompt',
    signalKind: signal.kind,
    reason: signal.reason,
    excerpt: signal.excerpt,
  }, env);
}

function readJsonFiles(directory) {
  if (!fs.existsSync(directory)) return [];
  return fs.readdirSync(directory)
    .filter((name) => name.endsWith('.json'))
    .sort()
    .map((name) => JSON.parse(fs.readFileSync(path.join(directory, name), 'utf8')));
}

function listCandidates(env = process.env, includeDecided = false) {
  const paths = feedbackPaths(env);
  const candidates = readJsonFiles(paths.inbox);
  const decisions = new Map(readJsonFiles(paths.decisions).map((item) => [item.candidate_id, item]));
  return candidates
    .filter((candidate) => includeDecided || !decisions.has(candidate.id))
    .map((candidate) => ({ ...candidate, decision: decisions.get(candidate.id) || null }));
}

function decideCandidate(candidateId, disposition, note, env = process.env) {
  if (!DISPOSITIONS.has(disposition)) {
    throw new Error(`invalid disposition: ${disposition}`);
  }
  const paths = feedbackPaths(env);
  const candidatePath = path.join(paths.inbox, `${candidateId}.json`);
  if (!fs.existsSync(candidatePath)) throw new Error(`unknown candidate: ${candidateId}`);
  ensurePrivateDirectory(paths.decisions);
  const payload = {
    schema_version: SCHEMA_VERSION,
    candidate_id: candidateId,
    disposition,
    note: redactSensitive(note),
    decided_at: new Date().toISOString(),
  };
  const decisionPath = path.join(paths.decisions, `${candidateId}.json`);
  if (!writeJsonOnce(decisionPath, payload)) {
    throw new Error(`candidate already decided: ${candidateId}`);
  }
  return { ...payload, filePath: decisionPath };
}

async function readHookInput(stream = process.stdin) {
  let raw = '';
  for await (const chunk of stream) raw += chunk;
  if (!raw.trim()) return {};
  const parsed = JSON.parse(raw);
  return parsed && typeof parsed === 'object' ? parsed : {};
}

module.exports = {
  DISPOSITIONS,
  capturePromptCandidate,
  decideCandidate,
  detectPromptSignal,
  extractUserAuthoredSignalText,
  feedbackPaths,
  listCandidates,
  persistCandidate,
  readHookInput,
  redactSensitive,
  resolveDataRoot,
};
