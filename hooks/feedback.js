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

function persistCandidate({
  input,
  host,
  sourceKind,
  signalKind,
  reason,
  excerpt,
  component = '',
  impact = '',
  workaround = '',
}, env = process.env) {
  const paths = feedbackPaths(env);
  ensurePrivateDirectory(paths.inbox);
  const sessionId = normalizeText(input.session_id || input.sessionId || 'unknown');
  const projectRoot = normalizeText(input.cwd || input.project_root || 'unknown');
  const safeExcerpt = redactSensitive(excerpt);
  const safeComponent = redactSensitive(component);
  const safeImpact = redactSensitive(impact);
  const safeWorkaround = redactSensitive(workaround);
  const id = stableId([
    host,
    sessionId,
    sourceKind,
    projectRoot,
    safeComponent.toLowerCase(),
    normalizeText(safeExcerpt).toLowerCase(),
  ]);
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
      component: safeComponent,
      excerpt: safeExcerpt,
      impact: safeImpact,
      workaround: safeWorkaround,
    },
  };
  const filePath = path.join(paths.inbox, `${id}.json`);
  const created = writeJsonOnce(filePath, payload);
  return { ...payload, created, filePath };
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

module.exports = {
  DISPOSITIONS,
  decideCandidate,
  feedbackPaths,
  listCandidates,
  persistCandidate,
  redactSensitive,
  resolveDataRoot,
};
