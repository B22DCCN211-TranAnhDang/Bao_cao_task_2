import type { Plugin } from "@opencode-ai/plugin"

/** v1 hook shape: factory returning a Hooks object. */
export const AuditPlugin: Plugin = async () => ({
  "tool.execute.before": async (input) => {
    console.log(JSON.stringify({ kind: "tool-before", tool: input.tool, sessionID: input.sessionID }))
  },
})
