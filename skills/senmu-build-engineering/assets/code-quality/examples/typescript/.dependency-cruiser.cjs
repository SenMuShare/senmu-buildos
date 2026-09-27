// Example-specific ownership, not a universal directory convention.
module.exports = {
  forbidden: [
    {
      name: "pricing-public-entry",
      severity: "error",
      from: { pathNot: "^src/pricing/" },
      to: { path: "^src/pricing/internal\\.ts$" }
    },
    { name: "no-cycles", severity: "error", from: {}, to: { circular: true } },
    { name: "resolved-imports", severity: "error", from: {}, to: { couldNotResolve: true } }
  ],
  options: {
    doNotFollow: { path: "node_modules" },
    tsConfig: { fileName: "tsconfig.json" },
    enhancedResolveOptions: { extensions: [".ts", ".js", ".json"] }
  }
};
