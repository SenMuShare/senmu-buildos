#!/usr/bin/env node

const { getSubagentContext } = require('../../../hooks/kernel');
const { writeHookOutput } = require('./runtime');

try {
  writeHookOutput('SubagentStart', getSubagentContext());
} catch (error) {
  process.stderr.write(`Senmu BuildOS Claude Code SubagentStart hook failed: ${error.message}\n`);
  process.exitCode = 1;
}
