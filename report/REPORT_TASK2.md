# So sánh OpenCode, Pi, Codex CLI và OpenCode v1/v2

**Người thực hiện:** Trần Anh Đăng  
**Mentor phụ trách:** Hoàng Danh Liêm  
**Ngày:** 12/11/2026

## 1. Phạm vi và phương pháp

Báo cáo đọc mã nguồn ở commit cố định, chạy binary thật và lưu script/log để lặp lại. Mốc phiên bản: OpenCode [v1.19.5](https://github.com/anomalyco/opencode/tree/810c0eba1a7348036f8bdf61e6632d0c36c6876c), [v2.2.7](https://github.com/anomalyco/opencode/tree/fedc6f208aa2bd54c1019227214568083f6380ad); Pi [1.5.2](https://github.com/badlogic/pi-mono/tree/a40abecaaf39e5a11e6c4850ee5cd8ecda4958cc); Codex CLI source [f988ada](https://github.com/openai/codex/tree/f988ada4bf1be6c1786b20b154cef7a0dce837c9), binary cục bộ `codex-cli 0.162.0-alpha.17.2`. Source Codex và binary là hai snapshot khác nhau; đối chiếu source chỉ mô tả commit đã pin.

**Quy ước:** “permission” là quyết định cho tool; “sandbox” là giới hạn OS/filesystem/network. Hai thứ không đồng nghĩa. Token trong bảng là số native event báo, không phải ước lượng. Chất lượng hoàn thành còn phụ thuộc model/provider và prompt.

## 2. So sánh ba tool theo mã nguồn

| Tiêu chí | OpenCode v2.2.7 | Pi 1.5.2 | Codex CLI |
|---|---|---|---|
| **Kiến trúc** | Server tạo chung graph `Session`, `Job`, `Permission`, `LocationServiceMap`; CLI tạo client nối endpoint. [routes.ts L60-L84](https://github.com/anomalyco/opencode/blob/fedc6f208aa2bd54c1019227214568083f6380ad/packages/server/src/routes.ts#L60-L84), [server-connection.ts L33-L40](https://github.com/anomalyco/opencode/blob/fedc6f208aa2bd54c1019227214568083f6380ad/packages/cli/src/services/server-connection.ts#L33-L40) | Lõi TypeScript `agent-loop` độc lập; `AgentSession` bọc persistence, extensions và compaction. [agent-loop.ts L184-L228](https://github.com/badlogic/pi-mono/blob/a40abecaaf39e5a11e6c4850ee5cd8ecda4958cc/packages/agent/src/agent-loop.ts#L184-L228), [agent-session.ts L533-L551](https://github.com/badlogic/pi-mono/blob/a40abecaaf39e5a11e6c4850ee5cd8ecda4958cc/packages/coding-agent/src/core/agent-session.ts#L533-L551) | Rust core quản lý session/turn/task; `RegularTask` gọi `run_turn`. [regular.rs L145-L184](https://github.com/openai/codex/blob/f988ada4bf1be6c1786b20b154cef7a0dce837c9/codex-rs/core/src/tasks/regular.rs#L145-L184), [turn.rs L203-L217](https://github.com/openai/codex/blob/f988ada4bf1be6c1786b20b154cef7a0dce837c9/codex-rs/core/src/session/turn.rs#L203-L217) |
| **Vòng lặp agent** | Một step stream provider, fork các tool call rồi join; runner quyết định bước tiếp. [step.ts L102-L163](https://github.com/anomalyco/opencode/blob/fedc6f208aa2bd54c1019227214568083f6380ad/packages/core/src/session/runner/step.ts#L102-L163) | Hai vòng `while`: vòng ngoài nhận follow-up, vòng trong giải tool call/steering; request có hook chuẩn bị context. [agent-loop.ts L184-L228](https://github.com/badlogic/pi-mono/blob/a40abecaaf39e5a11e6c4850ee5cd8ecda4958cc/packages/agent/src/agent-loop.ts#L184-L228), [L311-L316](https://github.com/badlogic/pi-mono/blob/a40abecaaf39e5a11e6c4850ee5cd8ecda4958cc/packages/agent/src/agent-loop.ts#L311-L316) | `run_turn` lặp sampling; function call trả tool output về vòng sampling tiếp theo. [turn.rs L203-L217](https://github.com/openai/codex/blob/f988ada4bf1be6c1786b20b154cef7a0dce837c9/codex-rs/core/src/session/turn.rs#L203-L217), [L536-L645](https://github.com/openai/codex/blob/f988ada4bf1be6c1786b20b154cef7a0dce837c9/codex-rs/core/src/session/turn.rs#L536-L645) |
| **Tool** | Registry hợp tool built-in, plugin, MCP; tool call đi qua `prepared.executeTool`. [v2 step.ts L102-L105](https://github.com/anomalyco/opencode/blob/fedc6f208aa2bd54c1019227214568083f6380ad/packages/core/src/session/runner/step.ts#L102-L105), [tool plugin domain](https://github.com/anomalyco/opencode/blob/fedc6f208aa2bd54c1019227214568083f6380ad/packages/plugin/src/promise/tool.ts#L13-L80) | Built-in `read/bash/edit/write/grep/find/ls`, cùng pipeline `runToolCall` cho custom/nested tool. [tools/index.ts L95-L153](https://github.com/badlogic/pi-mono/blob/a40abecaaf39e5a11e6c4850ee5cd8ecda4958cc/packages/coding-agent/src/core/tools/index.ts#L95-L153), [agent-loop.ts L821-L826](https://github.com/badlogic/pi-mono/blob/a40abecaaf39e5a11e6c4850ee5cd8ecda4958cc/packages/agent/src/agent-loop.ts#L821-L826) | `ToolRegistry` đăng ký runtime trusted/external và dispatch; có MCP namespace. [registry.rs L456-L628](https://github.com/openai/codex/blob/f988ada4bf1be6c1786b20b154cef7a0dce837c9/codex-rs/core/src/tools/registry.rs#L456-L628), [L752-L818](https://github.com/openai/codex/blob/f988ada4bf1be6c1786b20b154cef7a0dce837c9/codex-rs/core/src/tools/registry.rs#L752-L818) |
| **Permission/sandbox** | Rule `{action,resource,effect}`; rule khớp sau cùng thắng. Permission được hỏi/lưu theo session. [permission.ts L94-L108](https://github.com/anomalyco/opencode/blob/fedc6f208aa2bd54c1019227214568083f6380ad/packages/core/src/permission.ts#L94-L108), [schema](https://github.com/anomalyco/opencode/blob/fedc6f208aa2bd54c1019227214568083f6380ad/packages/schema/src/permission.ts#L60-L66) | Core gọi tool đã chuẩn bị; extension `tool_call` có thể chặn, không thấy profile sandbox OS bắt buộc ở pipeline này. Vì vậy policy phụ thuộc extension/host. [agent-loop.ts L821-L851](https://github.com/badlogic/pi-mono/blob/a40abecaaf39e5a11e6c4850ee5cd8ecda4958cc/packages/agent/src/agent-loop.ts#L821-L851), [agent-session.ts L720-L743](https://github.com/badlogic/pi-mono/blob/a40abecaaf39e5a11e6c4850ee5cd8ecda4958cc/packages/coding-agent/src/core/agent-session.ts#L720-L743) | Có profile filesystem/network và approval riêng; registry áp `ToolPolicy` khi đăng ký/dispatch. [permissions.rs L389-L463](https://github.com/openai/codex/blob/f988ada4bf1be6c1786b20b154cef7a0dce837c9/codex-rs/core/src/config/permissions.rs#L389-L463), [registry.rs L456-L464](https://github.com/openai/codex/blob/f988ada4bf1be6c1786b20b154cef7a0dce837c9/codex-rs/core/src/tools/registry.rs#L456-L464) |
| **Context** | Session/event được lưu và project; step ghi usage, compaction riêng. [step.ts L189-L202](https://github.com/anomalyco/opencode/blob/fedc6f208aa2bd54c1019227214568083f6380ad/packages/core/src/session/runner/step.ts#L189-L202), [compaction.ts](https://github.com/anomalyco/opencode/blob/fedc6f208aa2bd54c1019227214568083f6380ad/packages/core/src/session/compaction.ts) | `SessionManager` lưu nhánh hội thoại; tự compaction khi threshold/overflow, hook có thể đổi summary. [agent-session.ts L2925-L3005](https://github.com/badlogic/pi-mono/blob/a40abecaaf39e5a11e6c4850ee5cd8ecda4958cc/packages/coding-agent/src/core/agent-session.ts#L2925-L3005), [L3099-L3112](https://github.com/badlogic/pi-mono/blob/a40abecaaf39e5a11e6c4850ee5cd8ecda4958cc/packages/coding-agent/src/core/agent-session.ts#L3099-L3112) | Turn giữ history, tự compact khi cần, có checkpoint/retained history. [turn.rs L536-L645](https://github.com/openai/codex/blob/f988ada4bf1be6c1786b20b154cef7a0dce837c9/codex-rs/core/src/session/turn.rs#L536-L645), [compact.rs L85-L118](https://github.com/openai/codex/blob/f988ada4bf1be6c1786b20b154cef7a0dce837c9/codex-rs/core/src/compact.rs#L85-L118) |
| **Mở rộng** | API/SDK, plugin `setup`/domain hooks, MCP và TUI/GUI plugin. [plugin.ts L65-L76](https://github.com/anomalyco/opencode/blob/fedc6f208aa2bd54c1019227214568083f6380ad/packages/plugin/src/promise/plugin.ts#L65-L76), [host.ts L19-L67](https://github.com/anomalyco/opencode/blob/fedc6f208aa2bd54c1019227214568083f6380ad/packages/plugin/src/host.ts#L19-L67) | Extension hooks, custom tools, skills/templates, SDK/RPC; core cài hook trước/sau tool. [agent-session.ts L709-L817](https://github.com/badlogic/pi-mono/blob/a40abecaaf39e5a11e6c4850ee5cd8ecda4958cc/packages/coding-agent/src/core/agent-session.ts#L709-L817) | MCP, skills, plugin injections, app-server/SDK; mở rộng qua contract host/Rust/protocol. [turn.rs L309-L347](https://github.com/openai/codex/blob/f988ada4bf1be6c1786b20b154cef7a0dce837c9/codex-rs/core/src/session/turn.rs#L309-L347), [L399-L403](https://github.com/openai/codex/blob/f988ada4bf1be6c1786b20b154cef7a0dce837c9/codex-rs/core/src/session/turn.rs#L399-L403) |

### Nhận xét kiến trúc

OpenCode phù hợp khi nhiều UI cần cùng trạng thái session/service và API rõ. Pi có loop nhỏ, dễ can thiệp bằng extension và code TypeScript, nhưng policy chạy tool phải do host/extension quản. Codex có lớp policy/sandbox sâu hơn trong runtime và app-server cho tích hợp host. Đây là suy luận từ vị trí các thành phần trong source; chưa phải đo hiệu năng hay an toàn thực nghiệm. [Tài liệu OpenAI chính thức về Codex harness và app-server](https://developers.openai.com/blog/codex-as-a-platform) cũng mô tả harness quản lý loop, context, event và approval.

## 3. OpenCode v1.19.5 so với v2.2.7

### 3.1 Service chung cho TUI, desktop, web

V1 **đã có HTTP server và `attach`**. `run` mặc định tạo server trong process, `--attach` mới nối server bên ngoài; vì vậy nói “v1 không có server” là sai. [run.ts L1-L13](https://github.com/anomalyco/opencode/blob/810c0eba1a7348036f8bdf61e6632d0c36c6876c/packages/opencode/src/cli/cmd/run.ts#L1-L13), [L129-L131](https://github.com/anomalyco/opencode/blob/810c0eba1a7348036f8bdf61e6632d0c36c6876c/packages/opencode/src/cli/cmd/run.ts#L129-L131), [L901-L944](https://github.com/anomalyco/opencode/blob/810c0eba1a7348036f8bdf61e6632d0c36c6876c/packages/opencode/src/cli/cmd/run.ts#L901-L944).

V2 đổi **mặc định** sang background service có đăng ký/discovery; `--standalone` tạo private server và `--server` chọn URL. `Service.ensure()` tìm hoặc khởi động service tương thích. TUI tạo client từ endpoint; desktop gọi `Service.ensure()` và nhiều window chia sẻ một attempt; web có thể nối cùng HTTP endpoint. Điều này không có nghĩa mọi web client tự khởi động local service: browser chỉ là client HTTP. [CLI flags](https://github.com/anomalyco/opencode/blob/fedc6f208aa2bd54c1019227214568083f6380ad/packages/cli/src/commands/commands.ts#L14-L34), [service.ts L17-L69](https://github.com/anomalyco/opencode/blob/fedc6f208aa2bd54c1019227214568083f6380ad/packages/client/src/promise/service.ts#L17-L69), [TUI app.tsx L221-L239](https://github.com/anomalyco/opencode/blob/fedc6f208aa2bd54c1019227214568083f6380ad/packages/tui/src/app.tsx#L221-L239), [desktop background-service-machine.ts L123-L162](https://github.com/anomalyco/opencode/blob/fedc6f208aa2bd54c1019227214568083f6380ad/packages/desktop/src/main/service/background-service-machine.ts#L123-L162), [web SDK docs L78-L86](https://github.com/anomalyco/opencode/blob/fedc6f208aa2bd54c1019227214568083f6380ad/packages/web/src/content/docs/sdk.mdx#L78-L86).

### 3.2 API/SDK đã thử

[Script TypeScript](../experiments/v2-api-example.ts) gọi `Service.ensure`, `OpenCode.make`, `session.create`, đăng ký SSE trước `session.prompt`, lọc event theo `sessionID`, và kết thúc khi nhận `session.execution.succeeded`. Các method/kiểu dữ liệu nằm trong [generated client](https://github.com/anomalyco/opencode/blob/fedc6f208aa2bd54c1019227214568083f6380ad/packages/client/src/promise/generated/client.ts#L597-L625) và [generated types](https://github.com/anomalyco/opencode/blob/fedc6f208aa2bd54c1019227214568083f6380ad/packages/client/src/promise/generated/types.ts#L3319-L3419); event API dùng [SSE `/api/event`](https://github.com/anomalyco/opencode/blob/fedc6f208aa2bd54c1019227214568083f6380ad/packages/client/src/promise/generated/client.ts#L2280-L2294). `SharedEvents` là live stream, subscriber mới không replay toàn bộ lịch sử. [shared-events.ts L58-L124](https://github.com/anomalyco/opencode/blob/fedc6f208aa2bd54c1019227214568083f6380ad/packages/client/src/shared-events.ts#L58-L124).

Đã chạy script với `opencode/inkling-2-small-free` trên folder này: nhận `session.tool.called`, `session.usage.updated`, `session.text.delta`, `session.execution.succeeded`; exit code 0. [Log JSONL](../experiments/results/api-v2-smoke.jsonl) chứa session `ses_e324d0e38ffeoZXuM2PsOMKrK0`; event usage cuối báo input 6,376, output 86, cache read 6,272 token. Đây là **một lần smoke test API**, không phải benchmark chất lượng.

### 3.3 Permission migration

V1 khai báo permission bằng string/object lồng nhau, order của key được giữ để phục vụ last-match-wins. [v1 permission.ts L8-L36](https://github.com/anomalyco/opencode/blob/810c0eba1a7348036f8bdf61e6632d0c36c6876c/packages/core/src/v1/config/permission.ts#L8-L36). V2 có array rule `{action,resource,effect}`, evaluator dùng `.findLast`. [v2 schema](https://github.com/anomalyco/opencode/blob/fedc6f208aa2bd54c1019227214568083f6380ad/packages/schema/src/permission.ts#L60-L66), [evaluator](https://github.com/anomalyco/opencode/blob/fedc6f208aa2bd54c1019227214568083f6380ad/packages/core/src/permission.ts#L94-L108). V2 **có converter cho config v1**, nên config permission cũ không đồng nghĩa hoàn toàn không đọc được; converter ánh xạ `write/patch`→`edit`, `task`→`subagent`, `bash`→`shell`. [migrate.ts L19-L34](https://github.com/anomalyco/opencode/blob/fedc6f208aa2bd54c1019227214568083f6380ad/packages/core/src/v1/config/migrate.ts#L19-L34), [normalize.ts L533-L565](https://github.com/anomalyco/opencode/blob/fedc6f208aa2bd54c1019227214568083f6380ad/packages/core/src/config/normalize.ts#L533-L565).

Ví dụ v2: rule sau cùng khớp sẽ thắng, nên exception cụ thể phải đặt **sau** rule chung:

```json
{"permissions":[
  {"action":"shell","resource":"*","effect":"ask"},
  {"action":"shell","resource":"git status*","effect":"allow"},
  {"action":"edit","resource":"*","effect":"deny"}
]}
```

### 3.4 Subagent và shell chạy nền

V2 `Job` giữ recovery metadata cho `shell`/`subagent`; `Session.background()` gọi `jobs.backgroundAll()` và gửi thông báo để parent tiếp tục công việc khác. Trạng thái background được expose cho session/plugin; CLI noninteractive đợi job con trước khi kết luận prompt. [job.ts L141-L158](https://github.com/anomalyco/opencode/blob/fedc6f208aa2bd54c1019227214568083f6380ad/packages/core/src/job.ts#L141-L158), [session.ts L510-L524](https://github.com/anomalyco/opencode/blob/fedc6f208aa2bd54c1019227214568083f6380ad/packages/core/src/session.ts#L510-L524), [background.ts L30-L49](https://github.com/anomalyco/opencode/blob/fedc6f208aa2bd54c1019227214568083f6380ad/packages/core/src/session/background.ts#L30-L49), [noninteractive.ts L169-L193](https://github.com/anomalyco/opencode/blob/fedc6f208aa2bd54c1019227214568083f6380ad/packages/cli/src/run/noninteractive.ts#L169-L193). So với v1, đây là lifecycle Job/notification rõ ràng; không suy ra rằng v1 tuyệt đối không thể chạy process bất đồng bộ.

### 3.5 Port plugin v1 sang v2

V1 export factory `Plugin(input) => Promise<Hooks>` và trả object có key `"tool.execute.before"`. [v1 interface](https://github.com/anomalyco/opencode/blob/810c0eba1a7348036f8bdf61e6632d0c36c6876c/packages/plugin/src/index.ts#L56-L76), [hook](https://github.com/anomalyco/opencode/blob/810c0eba1a7348036f8bdf61e6632d0c36c6876c/packages/plugin/src/index.ts#L222-L270). V2 yêu cầu default export `{id, setup}` hoặc `{id, effect}`; loader decode và báo lỗi nếu sai shape. [v2 module.ts L84-L101](https://github.com/anomalyco/opencode/blob/fedc6f208aa2bd54c1019227214568083f6380ad/packages/core/src/plugin/module.ts#L84-L101), [L174-L187](https://github.com/anomalyco/opencode/blob/fedc6f208aa2bd54c1019227214568083f6380ad/packages/core/src/plugin/module.ts#L174-L187). Khi nạp plugin v1 vào v2, [log thực tế](../experiments/results/v1-plugin-on-v2-load.txt) ghi `failed to load plugin` và `Missing key ["default"]`. Vì vậy plugin v1 không chạy nguyên trạng trên v2, dù **config v1** có migration.

Bản [v1 gốc](../experiments/v1-plugin/index.ts) ghi tool trước khi chạy. Bản [v2 port](../experiments/v2-port-plugin/index.ts) dùng `Plugin.define`, `ctx.tool.hook("execute.before", ...)` và lưu audit record bằng `ctx.storage`; hook input và storage được định nghĩa tại [tool.ts L49-L80](https://github.com/anomalyco/opencode/blob/fedc6f208aa2bd54c1019227214568083f6380ad/packages/plugin/src/promise/tool.ts#L49-L80) và [storage.ts](https://github.com/anomalyco/opencode/blob/fedc6f208aa2bd54c1019227214568083f6380ad/packages/plugin/src/promise/storage.ts). `bun run typecheck` đã pass với package chính xác 2.2.7. [`plugin-smoke.py`](../experiments/plugin-smoke.py) còn nạp plugin vào server v2 thật, gọi tool `read` và kiểm tra bảng `kv` trong SQLite: exit 0, một bản ghi audit chứa `tool: read` và `callID` ([log](../experiments/results/plugin-smoke.json)).

## 4. Thực nghiệm và kết quả

### 4.1 Cài song song

| Binary | Package pin | Lệnh kiểm chứng | Kết quả |
|---|---|---|---|
| OpenCode v1 | `opencode-ai@1.19.5` | `versions/v1/node_modules/.bin/opencode --version` | `1.19.5` |
| OpenCode v2 | `@opencode/cli@2.2.7` | `versions/v2/node_modules/.bin/opencode --version` | `opencode v2.2.7` |
| Pi | `@earendil-works/pi-coding-agent@1.5.2` | `bun versions/pi/.../cli.js --version` | `1.5.2` |
| Codex | binary IDE | `codex --version` | `codex-cli 0.162.0-alpha.17.2` |

Package/lockfile được giữ trong `versions/`. Pi launcher chạy bằng Bun vì Node 18 ở máy này không hỗ trợ `enableCompileCache`. OpenCode v1 dùng XDG data riêng cho benchmark để tránh DB hiện có không tương thích.

### 4.2 Benchmark

[Runner](../experiments/benchmark.py) cung cấp ba task giống nhau (đọc hiểu, sửa bug, viết hàm), fixture mới cho từng lượt, checker nằm ngoài workspace, timeout, log JSONL và CSV. [Giao thức](../experiments/BENCHMARK.md) quy định 5 lượt/tool/task và cùng model/provider trước khi kết luận. Pilot đã chạy với model miễn phí `opencode/beam-free` cho v1 và v2; Pi trả `not_ready` cho `pi auth check --provider openai` và `--provider openai-codex`, đồng thời không có model `opencode/*` trong `--list-models`. Codex đã đăng nhập ChatGPT nhưng không có cùng provider `opencode/beam-free`. Chạy một model khác sẽ làm số token/thời gian không so sánh được. Vì vậy chưa có tỉ lệ hoàn thành **ba tool** hợp lệ; không điền số giả.

Đã chạy **5 lượt/task/bản OpenCode** với `opencode/beam-free`, timeout 90 giây/lượt, fixture và model chung. Các lượt được đảo thứ tự với seed cố định; `PWD` và `cwd` cùng chỉ vào fixture. [CSV từng lượt](../experiments/results/free-opencode-5x-2026-11-12/runs.csv), [CSV tổng hợp](../experiments/results/free-opencode-5x-2026-11-12/summary.csv) và JSONL gốc nằm trong cùng thư mục. `completion rate` = số lượt pass / 5; các cột token và thời gian là **trung vị của 5 lượt**.

| Task | Bản | Hoàn thành | Thời gian (s) | Input token | Output token | Cache read token |
|---|---|---:|---:|---:|---:|---:|
| Đọc marker | v1 | 5/5 | 4.211 | 5,115 | 57 | 15,360 |
| Đọc marker | v2 | 5/5 | 2.701 | 2,590 | 26 | 6,144 |
| Sửa bug | v1 | 5/5 | 6.108 | 10,493 | 127 | 22,272 |
| Sửa bug | v2 | 5/5 | 7.329 | 3,405 | 286 | 21,568 |
| Viết hàm | v1 | 5/5 | 13.375 | 6,663 | 273 | 33,216 |
| Viết hàm | v2 | 5/5 | 9.657 | 6,307 | 302 | 22,592 |

Trong pilot nhỏ này cả hai bản đều pass 15/15. V2 nhanh hơn ở task đọc và viết hàm, v1 nhanh hơn ở task sửa bug; không có thắng tuyệt đối. Input token đo từ provider event có thể khác vì system prompt, tool schema và số model step khác nhau. Năm lượt/task còn nhỏ, free model có thể đổi theo provider, quota miễn phí có thể hết và thứ tự tài nguyên máy ảnh hưởng thời gian; không suy ra kết luận thống kê rộng. Một batch thử đầu đã bị loại vì biến `PWD` không trỏ vào fixture v2; log được giữ ở `results/invalid-pwd-do-not-use` để kiểm toán, không tính vào bảng.

## 5. Kết luận và giới hạn

- V2 thực sự đổi mặc định sang background service chia sẻ, có API session/event rõ, rule permission dạng danh sách, Job nền và plugin contract mới. V1 vẫn đã có server/attach; v2 còn đọc và migrate một phần config v1.
- Source cho thấy Pi ưu tiên lõi loop/extension đơn giản, Codex ưu tiên host policy/sandbox, OpenCode ưu tiên service/API đa client. Không thể suy luận “tool nào code tốt nhất” từ kiến trúc.
- Benchmark ba tool cần credential cho **một model chung** và ít nhất 5 lượt/task/tool. Số đo pilot chỉ kiểm tra harness và minh họa sự cố timeout, không phải kết luận thống kê.
