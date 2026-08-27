#!/usr/bin/env node

const { capturePromptCandidate, feedbackContext, readHookInput } = require('../../../hooks/feedback');
const { writeHookOutput } = require('./runtime');

readHookInput()
  .then((input) => {
    const candidate = capturePromptCandidate(input, 'claude-code');
    if (candidate) writeHookOutput('UserPromptSubmit', feedbackContext(candidate));
    else process.stdout.write('{}');
  })
  .catch((error) => {
    process.stderr.write(`Senmu BuildOS feedback capture skipped: ${error.message}\n`);
    process.stdout.write('{}');
  });
