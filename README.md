# Báo cáo Task 2: OpenCode, Pi và Codex CLI

**Người thực hiện:** Trần Anh Đăng  
**Mentor phụ trách:** Hoàng Danh Liêm  
**Ngày khảo sát:** 12/11/2026

Repository này chứa [báo cáo đầy đủ](report/REPORT_TASK2.md), code thử API/plugin và dữ liệu thực nghiệm. Báo cáo so sánh OpenCode, Pi, Codex CLI theo mã nguồn; khảo sát sự thay đổi từ OpenCode v1 sang v2; và đo cùng ba task trên hai phiên bản OpenCode. Các nhận định kỹ thuật trong báo cáo dẫn tới commit và dòng mã nguồn cụ thể.

## Đọc nhanh

| Nội dung | Kết quả và nơi kiểm chứng |
| --- | --- |
| So sánh ba tool | [Bảng kiến trúc, agent loop, tool, permission, context và mở rộng](report/REPORT_TASK2.md#2-so-sánh-ba-tool-theo-mã-nguồn). Đây là phân tích source, không phải xếp hạng chất lượng model. |
| OpenCode v1 → v2 | [Phân tích service, SDK, permission, background job và plugin](report/REPORT_TASK2.md#3-opencode-v1195-so-với-v227). V1 đã có HTTP server/attach; v2 chuyển mặc định sang background service có discovery. |
| API v2 | [Script TypeScript](experiments/v2-api-example.ts) tạo session, gửi prompt và đọc event SSE theo `sessionID`; [log chạy thật](experiments/results/api-v2-smoke.jsonl). |
| Plugin | [Plugin v1](experiments/v1-plugin/index.ts) không nạp nguyên trạng trên v2 ([log lỗi](experiments/results/v1-plugin-on-v2-load.txt)); [bản port v2](experiments/v2-port-plugin/index.ts) đã typecheck và ghi audit record khi gọi tool ([smoke test](experiments/results/plugin-smoke.json)). |
| Benchmark đã hoàn thành | OpenCode v1 và v2 cùng model `opencode/beam-free`, ba task, năm lượt mỗi task/bản: **15/15 lượt pass cho từng bản**. [CSV tổng hợp](experiments/results/free-opencode-5x-2026-11-12/summary.csv), [CSV từng lượt](experiments/results/free-opencode-5x-2026-11-12/runs.csv) và JSONL gốc. |
| Benchmark ba tool | **Chưa có kết quả so sánh hợp lệ** cho OpenCode, Pi và Codex CLI trên cùng model/provider. Pi và Codex chưa có quyền truy cập cùng model đã dùng trong lần đo OpenCode. [Giới hạn và điều kiện chạy lại](experiments/BENCHMARK.md). |

## Phiên bản và phạm vi

| Tool | Phiên bản binary/package dùng để chạy | Snapshot source dùng để phân tích |
| --- | --- | --- |
| OpenCode v1 | `opencode-ai@1.19.5` | [`810c0eba`](https://github.com/anomalyco/opencode/tree/810c0eba1a7348036f8bdf61e6632d0c36c6876c) |
| OpenCode v2 | `@opencode/cli@2.2.7` | [`fedc6f20`](https://github.com/anomalyco/opencode/tree/fedc6f208aa2bd54c1019227214568083f6380ad) |
| Pi | `@earendil-works/pi-coding-agent@1.5.2` | [`a40abeca`](https://github.com/badlogic/pi-mono/tree/a40abecaaf39e5a11e6c4850ee5cd8ecda4958cc) |
| Codex CLI | `codex-cli 0.162.0-alpha.17.2` trong môi trường khảo sát | [`f988ada4`](https://github.com/openai/codex/tree/f988ada4bf1be6c1786b20b154cef7a0dce837c9) |

Source Codex và binary được khảo sát là hai snapshot khác nhau. Các kết luận về code Codex chỉ áp dụng cho commit đã pin. Package/lockfile của ba tool đầu nằm riêng trong [`versions/`](versions/); không đưa `node_modules` vào Git.

## Kết quả đo OpenCode v1/v2

Mỗi ô thời gian và token là **trung vị của năm lượt**; tỉ lệ hoàn thành là số lượt vượt qua checker. Cả hai bản dùng `opencode/beam-free`, cùng fixture và timeout 90 giây/lượt. Runner đảo thứ tự task/tool theo seed cố định và lưu output gốc cho từng lượt.

| Task | v1: pass; thời gian; input/output token | v2: pass; thời gian; input/output token |
| --- | ---: | ---: |
| Đọc marker trong file | 5/5; 4.211 s; 5,115 / 57 | 5/5; 2.701 s; 2,590 / 26 |
| Sửa bug hàm tam giác | 5/5; 6.108 s; 10,493 / 127 | 5/5; 7.329 s; 3,405 / 286 |
| Viết hàm tạo slug | 5/5; 13.375 s; 6,663 / 273 | 5/5; 9.657 s; 6,307 / 302 |

V2 nhanh hơn trong hai task ở mẫu này, v1 nhanh hơn ở task sửa bug. Mẫu năm lượt/task nhỏ; free model và quota có thể đổi. Token là số đọc từ event của từng tool, chịu ảnh hưởng của system prompt, tool schema và số bước, nên không thể dùng riêng bảng này để kết luận tool nào tốt hơn. Cách tạo fixture, checker và diễn giải metric nằm trong [giao thức benchmark](experiments/BENCHMARK.md).

## Cấu trúc repository

```text
README.md                         Trang giới thiệu và cách chạy lại
REPORT_TASK2.md                  Trang mở đầu ngắn
report/REPORT_TASK2.md           Báo cáo chi tiết kèm liên kết source theo dòng
experiments/v2-api-example.ts    Tạo session, gửi prompt, nhận SSE với SDK v2
experiments/v1-plugin/           Plugin gốc theo contract v1
experiments/v2-port-plugin/      Plugin đã port sang contract v2
experiments/plugin-smoke.py      Kiểm chứng plugin trong server v2 thật
experiments/benchmark.py         Runner cho read/bug/feature
experiments/summarize.py         Tổng hợp pass rate, thời gian và token
experiments/BENCHMARK.md         Giao thức, checker và giới hạn đo
experiments/results/             Log API, plugin và 30 lượt OpenCode hợp lệ
versions/{v1,v2,pi}/            Manifest và lockfile cài từng bản riêng
REPORT_TASK2_submission.zip      Bản nén để nộp
```

## Cài đặt và kiểm tra phiên bản

Cần **Bun** và **Python 3**; máy khảo sát dùng Bun 1.4.4 và Python 3.12.3. Các lệnh dưới đây chạy từ thư mục gốc sau khi clone repository. Pi dùng Bun vì Node 18 trong môi trường khảo sát thiếu `node:module.enableCompileCache`. Khi chạy API, plugin hoặc benchmark cần một model/provider mà tài khoản hiện tại truy cập được.

```bash
git clone https://github.com/B22DCCN211-TranAnhDang/Bao_cao_task_2.git
cd Bao_cao_task_2

(cd versions/v1 && bun install)
(cd versions/v2 && bun install)
(cd versions/pi && bun install)
(cd experiments && bun install && bun run typecheck)

versions/v1/node_modules/.bin/opencode --version
versions/v2/node_modules/.bin/opencode --version
bun versions/pi/node_modules/@earendil-works/pi-coding-agent/dist/bundle/cli.js --version
```

`bun run typecheck` kiểm tra script API và hai plugin. Nếu cài v2 báo thiếu binary, chạy `cd versions/v2 && bun pm trust @opencode/cli && bun install` rồi quay lại thư mục gốc.

## Chạy lại API và plugin

Script API tự tìm/khởi động service v2, tạo session, đăng ký luồng SSE **trước** khi gửi prompt, rồi in event cho đến khi session hoàn tất. `OPENCODE_MODEL` phải có dạng `provider/model`; ví dụ dưới đây dùng model của lần đo, có thể cần thay bằng model đang khả dụng:

```bash
cd experiments
OPENCODE_MODEL=opencode/beam-free bun v2-api-example.ts
OPENCODE_MODEL=opencode/beam-free python3 plugin-smoke.py
```

Smoke test plugin tạo workspace tạm, nạp [plugin v2](experiments/v2-port-plugin/index.ts), yêu cầu model dùng tool `read` và kiểm tra audit record đã được lưu trong SQLite. Log tham chiếu: [API](experiments/results/api-v2-smoke.jsonl) và [plugin](experiments/results/plugin-smoke.json). Chạy lại có thể tạo session và token usage mới.

## Chạy lại benchmark

Để tái lập riêng lần đo OpenCode, chạy từ thư mục gốc:

```bash
python3 experiments/benchmark.py \
  --config experiments/benchmark.free-opencode.json \
  --output experiments/results/replay
python3 experiments/summarize.py experiments/results/replay/runs.csv
```

Config này chạy **30 lượt gọi model**: 3 task × 2 bản × 5 lần, mỗi lượt tối đa 90 giây. Runner tạo fixture mới cho từng lượt, đặt cả `cwd` và `PWD` về fixture, chấm bằng checker ngoài workspace rồi ghi `runs.csv`, JSONL và stderr vào thư mục output. Dữ liệu đã chạy nằm ở [`experiments/results/free-opencode-5x-2026-11-12/`](experiments/results/free-opencode-5x-2026-11-12/).

Để chạy **đủ OpenCode, Pi và Codex CLI**, sao chép [`benchmark.config.example.json`](experiments/benchmark.config.example.json) thành `experiments/benchmark.config.json`, chỉnh cùng model/provider có thể truy cập cho tất cả tool, xác thực provider cho từng CLI và bảo đảm `codex` có trong `PATH` (hoặc đặt `CODEX_BIN`). Sau đó chạy `python3 experiments/benchmark.py --config experiments/benchmark.config.json`. File config cục bộ được `.gitignore` bỏ qua. Chỉ so sánh trực tiếp khi model, provider, quyền thực thi, timeout và số lượt tương đương; xem [giao thức](experiments/BENCHMARK.md).

## Tính minh bạch của kết quả

- Kết quả pass cần **exit code 0** và checker ngoài workspace thành công; timeout tính là fail. Task đọc chỉ chấm câu trả lời của assistant, không lấy marker từ tool log.
- Thời gian đo từ lúc gọi CLI đến khi process kết thúc. Input/output/cache token lấy từ native JSON event; giá trị thiếu được để trống, không tự ước lượng.
- Log gốc và CSV được giữ để kiểm toán. Một batch thử sai `PWD` đã bị loại khỏi bảng kết quả; folder đó được `.gitignore` bỏ qua.
- Kết quả benchmark ba tool cùng model **chưa được báo cáo** vì chưa đủ điều kiện provider; không suy diễn từ số đo hai bản OpenCode.
