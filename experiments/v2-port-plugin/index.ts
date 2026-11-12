import { Plugin } from "@opencode/plugin"

/** Port of v1-plugin: register a domain hook during setup. */
export default Plugin.define({
  id: "task2-tool-audit",
  async setup(ctx) {
    await ctx.tool.hook("execute.before", async (event) => {
      await ctx.storage.set(`last-tool:${event.sessionID}`, {
        tool: event.tool,
        callID: event.id,
        recordedAt: new Date().toISOString(),
      })
    })
  },
})
