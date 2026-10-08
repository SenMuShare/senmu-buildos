#!/usr/bin/env node

const {
  decideCandidate,
  feedbackPaths,
  listCandidates,
  linkCandidate,
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
  senmu-feedback followup [--summary | --json [--limit <n>] [--offset <n>]]
  senmu-feedback submit --component <BuildOS component> --summary <problem> --impact <effect> [--project-root <path>] [--evidence <text>] [--workaround <text>] [--quiet]
  senmu-feedback decide --id <FB-id> --disposition <discard|project|buildos_candidate|needs_evidence> [--note <text>] [--tracking-ref <existing-issue-or-task>]
  senmu-feedback link --id <FB-id> --tracking-ref <existing-issue-or-task> [--note <text>]

pending (alias: unreviewed) means no first decision, not unresolved work.
followup returns classified items whose actual status must be read from their
existing issue/task; it does not query owners or assert that they remain open.`;
}

function nonNegativeIntegerOption(args, name, fallback) {
  const raw = option(args, name, String(fallback));
  if (!/^\d+$/.test(raw)) throw new Error(`${name} must be a non-negative integer`);
  return Number(raw);
}

function queueSemantics(view) {
  if (view === 'pending' || view === 'unreviewed') return 'awaiting_first_decision';
  if (view === 'followup') return 'owner_status_not_queried';
  return 'all_captured_events_not_a_resolution_count';
}

function summarizeCandidates(candidates, view) {
  const counts = (selector) => candidates.reduce((summary, candidate) => {
    const key = selector(candidate) || 'unknown';
    summary[key] = (summary[key] || 0) + 1;
    return summary;
  }, Object.create(null));
  const captured = candidates.map((candidate) => candidate.captured_at).filter(Boolean).sort();
  const followup = candidates.filter(candidate => candidate.decision
    && ['project', 'buildos_candidate', 'needs_evidence'].includes(candidate.decision.disposition));
  const linked = followup.filter(candidate => candidate.tracking_refs.length > 0).length;
  return {
    schema_version: 1,
    view,
    queue_semantics: queueSemantics(view),
    count: candidates.length,
    followup_tracking: { required: followup.length, linked, missing: followup.length - linked },
    by_disposition: counts((candidate) => candidate.decision ? candidate.decision.disposition : 'unreviewed'),
    by_signal_kind: counts((candidate) => candidate.signal && candidate.signal.kind),
    by_source_host: counts((candidate) => candidate.source && candidate.source.host),
    by_source_project: counts((candidate) => candidate.source && candidate.source.project_root),
    by_buildos_component: counts((candidate) => candidate.signal && candidate.signal.component),
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
    process.stdout.write(
      `${candidate.id}${decision}\n`
      + `  component: ${candidate.signal.component || 'unknown'}\n`
      + `  problem: ${candidate.signal.excerpt}\n`
      + `  impact: ${candidate.signal.impact || 'unknown'}\n`
      + `  source project: ${candidate.source.project_root}\n`,
    );
    if (candidate.decision) process.stdout.write(
      `  tracking: ${candidate.tracking_refs.join(', ') || 'not linked'} (owner status not queried)\n`,
    );
  }
}

function main(args = process.argv.slice(2)) {
  const command = args[0];
  if (command === 'path') {
    process.stdout.write(`${feedbackPaths().root}\n`);
    return;
  }
  if (['pending', 'unreviewed', 'all', 'followup'].includes(command)) {
    const limit = args.includes('--limit') ? nonNegativeIntegerOption(args, '--limit', 0) : null;
    const offset = nonNegativeIntegerOption(args, '--offset', 0);
    let candidates = listCandidates(process.env, command === 'all' || command === 'followup');
    if (command === 'followup') candidates = candidates.filter((candidate) =>
      candidate.decision && ['project', 'buildos_candidate', 'needs_evidence'].includes(candidate.decision.disposition));
    printCandidates(candidates, {
      json: args.includes('--json'),
      summary: args.includes('--summary'),
      limit,
      offset,
      view: command,
    });
    return;
  }
  if (command === 'submit') {
    const component = option(args, '--component');
    const summary = option(args, '--summary');
    const impact = option(args, '--impact');
    if (!component || !summary || !impact) {
      throw new Error('--component, --summary and --impact are required');
    }
    const evidence = option(args, '--evidence');
    const result = persistCandidate({
      input: {
        cwd: option(args, '--project-root', process.cwd()),
        session_id: option(args, '--session-id', 'manual-agent-report'),
        transcript_path: evidence,
      },
      host: 'agent',
      sourceKind: 'agent_report',
      signalKind: 'agent_observed_governance_gap',
      reason: 'Agent reported a concrete BuildOS usage problem',
      excerpt: summary,
      component,
      impact,
      workaround: option(args, '--workaround'),
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
    const result = decideCandidate(id, disposition, option(args, '--note'), process.env, { trackingRef: option(args, '--tracking-ref') });
    process.stdout.write(`${result.candidate_id} -> ${result.disposition}\n`);
    return;
  }
  if (command === 'link') {
    const result = linkCandidate(option(args, '--id'), option(args, '--tracking-ref'), option(args, '--note'));
    process.stdout.write(`${result.candidate_id} -> ${result.tracking_ref}${result.created ? ' linked' : ' already linked'}\n`);
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
