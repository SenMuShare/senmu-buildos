#!/usr/bin/env node

const { getSubagentContext } = require('./kernel');

try {
  process.stdout.write(JSON.stringify({
    hookSpecificOutput: {
      hookEventName: 'SubagentStart',
      additionalContext: getSubagentContext(),
    },
  }));
} catch (error) {
  process.stderr.write(`Senmu BuildOS subagent-start hook failed: ${error.message}\n`);
  process.exitCode = 1;
}
