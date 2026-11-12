/** OpenCode v2.2.7: session -> prompt -> live SSE events. Run with `bun v2-api-example.ts`. */
import { OpenCode } from "@opencode/client"
import { Service } from "@opencode/client/service"

const cli = new URL("../versions/v2/node_modules/.bin/opencode", import.meta.url).pathname
const endpoint = process.env.OPENCODE_URL
  ? { url: process.env.OPENCODE_URL }
  : await Service.ensure({
      command: [cli, "serve", "--service"],
      version: (value) => value.startsWith("2.2."),
    })
const client = OpenCode.make({ baseUrl: endpoint.url, headers: Service.headers(endpoint) })
const directory = process.env.TASK_DIRECTORY ?? process.cwd()
const modelName = process.env.OPENCODE_MODEL
const model = modelName
  ? { providerID: modelName.slice(0, modelName.indexOf("/")), id: modelName.slice(modelName.indexOf("/") + 1) }
  : undefined
if (modelName && !modelName.includes("/")) throw new Error("OPENCODE_MODEL must be provider/model")

const session = await client.session.create({
  location: { directory },
  title: "Task 2 API demonstration",
  model,
})
console.log(`session=${session.id} server=${endpoint.url}`)

// The v2 event feed is live. Start consuming before submitting the prompt.
const signal = AbortSignal.timeout(120_000)
const stream = client.event.subscribe({
  types: ["session.text.delta", "session.tool.called", "session.usage.updated", "session.execution.succeeded", "session.execution.failed"],
  signal,
})
const consume = (async () => {
  for await (const event of stream) {
    const data = event.data as { sessionID?: string }
    if (data.sessionID !== session.id) continue
    console.log(JSON.stringify(event))
    if (event.type === "session.execution.succeeded") return
    if (event.type === "session.execution.failed") throw new Error(`Session failed: ${JSON.stringify(event.data)}`)
  }
  throw new Error("Event stream ended before execution completed")
})()

await client.session.prompt({
  sessionID: session.id,
  text: process.env.TASK_PROMPT ?? "List the top-level files in this directory. Do not edit files.",
})
await consume
