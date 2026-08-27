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
  senmu-feedback pending [--json]
  senmu-feedback all [--json]
  senmu-feedback submit --summary <text> [--project-root <path>] [--evidence <text>] [--quiet]
  senmu-feedback decide --id <FB-id> --disposition <discard|project|buildos_candidate|needs_evidence> [--note <text>]`;
}

function printCandidates(candidates, json) {
  if (json) {
    process.stdout.write(`${JSON.stringify(candidates, null, 2)}\n`);
    return;
  }
  if (!candidates.length) {
    process.stdout.write('No feedback candidates.\n');
    return;
  }
  for (const candidate of candidates) {
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
    printCandidates(listCandidates(process.env, command === 'all'), args.includes('--json'));
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
