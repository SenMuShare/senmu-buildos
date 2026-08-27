#!/usr/bin/env node

const { capturePromptCandidate, readHookInput } = require('../../../hooks/feedback');

readHookInput()
  .then((input) => {
    capturePromptCandidate(input, 'codex');
    process.stdout.write('{}');
  })
  .catch((error) => {
    process.stderr.write(`Senmu BuildOS feedback capture skipped: ${error.message}\n`);
    process.stdout.write('{}');
  });
