#!/usr/bin/env node

const {
  decideCandidate,
  feedbackPaths,
  listCandidates,
  persistCandidate,
} = require('./feedback');

function option(args, name, fallback = '') {
  const index = args.indexOf(name);
  return index >= 0 && index + 1 < args.length ? args[index + 1] : fallback;
}

function usage() {
  return `Usage:
  senmu-feedback path
  senmu-feedback pending [--summary | --json [--limit <n>] [--offset <n>]]
  senmu-feedback all [--summary | --json [--limit <n>] [--offset <n>]]
  senmu-feedback submit --summary <text> [--project-root <path>] [--evidence <text>] [--quiet]
  senmu-feedback decide --id <FB-id> --disposition <discard|project|buildos_candidate|needs_evidence> [--note <text>]`;
}

function nonNegativeIntegerOption(args, name, fallback) {
  const raw = option(args, name, String(fallback));
  if (!/^\d+$/.test(raw)) throw new Error(`${name} must be a non-negative integer`);
  return Number(raw);
}

function summarizeCandidates(candidates, view) {
  const counts = (selector) => candidates.reduce((summary, candidate) => {
    const key = selector(candidate) || 'unknown';
    summary[key] = (summary[key] || 0) + 1;
    return summary;
  }, Object.create(null));
  const captured = candidates.map((candidate) => candidate.captured_at).filter(Boolean).sort();
  return {
    schema_version: 1,
    view,
    count: candidates.length,
    by_signal_kind: counts((candidate) => candidate.signal && candidate.signal.kind),
    by_source_host: counts((candidate) => candidate.source && candidate.source.host),
    captured_range: captured.length ? { oldest: captured[0], newest: captured[captured.length - 1] } : null,
    next: candidates.length
      ? `${view} --json --limit 10 --offset 0`
      : null,
  };
}

function printCandidates(candidates, { json, summary, limit, offset, view }) {
  if (summary) {
    process.stdout.write(`${JSON.stringify(summarizeCandidates(candidates, view), null, 2)}\n`);
    return;
  }
  const selected = candidates.slice(offset, limit === null ? undefined : offset + limit);
  if (json) {
    if (limit === null && offset === 0) {
      process.stdout.write(`${JSON.stringify(selected, null, 2)}\n`);
      return;
    }
    process.stdout.write(`${JSON.stringify({
      schema_version: 1,
      view,
      total: candidates.length,
      offset,
      limit,
      returned: selected.length,
      has_more: offset + selected.length < candidates.length,
      candidates: selected,
    }, null, 2)}\n`);
    return;
  }
  if (!selected.length) {
    process.stdout.write('No feedback candidates.\n');
    return;
  }
  for (const candidate of selected) {
    const decision = candidate.decision ? ` -> ${candidate.decision.disposition}` : '';
    process.stdout.write(`${candidate.id}${decision}\n  ${candidate.signal.excerpt}\n  ${candidate.source.project_root}\n`);
  }
}

function main(args = process.argv.slice(2)) {
  const command = args[0];
  if (command === 'path') {
    process.stdout.write(`${feedbackPaths().root}\n`);
    return;
  }
  if (command === 'pending' || command === 'all') {
    const limit = args.includes('--limit') ? nonNegativeIntegerOption(args, '--limit', 0) : null;
    const offset = nonNegativeIntegerOption(args, '--offset', 0);
    printCandidates(listCandidates(process.env, command === 'all'), {
      json: args.includes('--json'),
      summary: args.includes('--summary'),
      limit,
      offset,
      view: command,
    });
    return;
  }
  if (command === 'submit') {
    const summary = option(args, '--summary');
    if (!summary) throw new Error('--summary is required');
    const evidence = option(args, '--evidence');
    const result = persistCandidate({
      input: {
        cwd: option(args, '--project-root', process.cwd()),
        session_id: option(args, '--session-id', 'manual-agent-report'),
        transcript_path: evidence,
      },
      host: option(args, '--host', 'agent'),
      sourceKind: 'agent_report',
      signalKind: 'agent_observed_governance_gap',
      reason: 'agent explicitly submitted a feedback candidate',
      excerpt: summary,
    });
    if (!args.includes('--quiet')) {
      process.stdout.write(`${result.id}${result.created ? ' created' : ' already exists'}\n`);
    }
    return;
  }
  if (command === 'decide') {
    const id = option(args, '--id');
    const disposition = option(args, '--disposition');
    if (!id || !disposition) throw new Error('--id and --disposition are required');
    const result = decideCandidate(id, disposition, option(args, '--note'));
    process.stdout.write(`${result.candidate_id} -> ${result.disposition}\n`);
    return;
  }
  throw new Error(usage());
}

try {
  main();
} catch (error) {
  process.stderr.write(`${error.message}\n`);
  process.exitCode = 1;
}

module.exports = { main };
