# Benchmark tái lập được

## Cách chạy

1. Cài các package trong `versions/v1`, `versions/v2`, `versions/pi`; Pi cần Bun vì Node 18 của máy này thiếu `node:module.enableCompileCache`.
2. Tạo `benchmark.config.json` từ `benchmark.config.example.json`. Chọn cùng model nền cho cả bốn tool, xác nhận mỗi CLI có thể gọi provider đó. `codex` dùng model ID, ba tool còn lại dùng `provider/model`.
3. Đảm bảo provider authentication hợp lệ. Script không lấy hoặc sao chép credential từ tool khác. Đặt `CODEX_BIN` nếu `codex` chưa nằm trong `PATH`.
4. Chạy `python3 benchmark.py --config benchmark.config.json`. Mỗi lượt tạo một fixture mới, giữ log JSONL và stderr, xuất `results/runs.csv`.
5. Tổng hợp bằng `python3 summarize.py results/runs.csv`.

## Task và phép chấm

| Task | Việc giao agent | Chấm tự động |
|---|---|
| `read` | Đọc marker trong README | Đáp án chứa `MARKER: THETA-731`; README không đổi |
| `bug` | Sửa hàm tam giác | Test bên ngoài workspace kiểm tra 0, 1, 3, 10 và số âm |
| `feature` | Viết hàm slug | Test bên ngoài workspace kiểm tra khoảng trắng, chữ hoa và chuỗi rỗng |

Test chấm điểm không nằm trong fixture, nên agent không thể sửa test. Runner đặt cả `cwd` lẫn `PWD` về fixture vì OpenCode v2 đọc `PWD`. Thứ tự tool/task được đảo bằng seed cố định. Mỗi lượt đo `perf_counter` từ lúc gọi CLI đến lúc process kết thúc. `passed` cần exit code 0 và checker thành công; task đọc chỉ kiểm tra **assistant text**, không lấy marker từ tool log. Timeout tính là fail. `input_tokens`, `output_tokens`, `cache_read_tokens` đọc từ native JSON event; ô trống nghĩa là không có event phù hợp, không ước lượng.

## Diễn giải

- Cần **ít nhất 5 lượt/tool/task** và đảo thứ tự tool để kết luận so sánh; config mặc định chạy 5 lượt. Pilot một lượt chỉ kiểm tra runner.
- Pin cùng model, provider, mức reasoning, giới hạn thời gian, chính sách permission và phiên bản; nếu model hoặc account khác nhau, không quy khác biệt cho kiến trúc tool.
- OpenCode dùng `--auto` trong fixture tạm, Codex dùng `workspace-write`; Pi chạy quyền của process. Các policy này không hoàn toàn tương đương. Không dùng kết quả để kết luận độ an toàn.
- Usage ở các tool có thể khác định nghĩa cache/reasoning hoặc có model step phụ. Giữ log gốc để kiểm toán.
