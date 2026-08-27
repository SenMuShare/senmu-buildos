function buildClaudeCodeOutput(event, context) {
  return {
    hookSpecificOutput: {
      hookEventName: event,
      additionalContext: context,
    },
  };
}

function writeHookOutput(event, context) {
  process.stdout.write(JSON.stringify(buildClaudeCodeOutput(event, context)));
}

module.exports = {
  buildClaudeCodeOutput,
  writeHookOutput,
};
