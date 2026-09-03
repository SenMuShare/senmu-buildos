#!/usr/bin/env node

const { getSessionContext } = require('./kernel');

try {
  const context = getSessionContext();
  process.stdout.write(JSON.stringify({
    hookSpecificOutput: {
      hookEventName: 'SessionStart',
      additionalContext: context,
    },
  }));
} catch (error) {
  process.stderr.write(`Senmu BuildOS session-start hook failed: ${error.message}\n`);
  process.exitCode = 1;
}
