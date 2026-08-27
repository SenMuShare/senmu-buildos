#!/usr/bin/env node

const { getSessionContext } = require('../../../hooks/kernel');
const { writeHookOutput } = require('./runtime');

try {
  writeHookOutput('SessionStart', getSessionContext());
} catch (error) {
  process.stderr.write(`Senmu BuildOS Claude Code SessionStart hook failed: ${error.message}\n`);
  process.exitCode = 1;
}
