function buildCodexOutput(event, context) {
  return {
    hookSpecificOutput: {
      hookEventName: event,
      additionalContext: context,
    },
  };
}

function writeHookOutput(event, context) {
  process.stdout.write(JSON.stringify(buildCodexOutput(event, context)));
}

module.exports = {
  buildCodexOutput,
  writeHookOutput,
};
