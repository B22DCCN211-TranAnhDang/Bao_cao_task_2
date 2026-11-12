# REPORT TASK 2

**Người thực hiện:** Trần Anh Đăng  
**Mentor phụ trách:** Hoàng Danh Liêm  
**Ngày khảo sát:** 12/11/2026

## Nội dung

- [Trang mở đầu REPORT_TASK2.md](REPORT_TASK2.md)
- [Báo cáo phân tích mã nguồn và thực nghiệm](report/REPORT_TASK2.md)
- [Script OpenCode v2 API/SDK](experiments/v2-api-example.ts)
- [Plugin v1 gốc](experiments/v1-plugin/index.ts) và [bản port v2](experiments/v2-port-plugin/index.ts)
- [Plugin runtime smoke test](experiments/plugin-smoke.py)
- [Benchmark runner](experiments/benchmark.py) và [hướng dẫn](experiments/BENCHMARK.md)
- `versions/v1`, `versions/v2`, `versions/pi`: package manifest/lockfile để cài riêng. Thư mục `node_modules` không cần đưa vào Git.

## Chạy nhanh

```bash
cd versions/v1 && bun install && ./node_modules/.bin/opencode --version
cd ../v2 && bun install && bun pm trust @opencode/cli && ./node_modules/.bin/opencode --version
cd ../pi && bun install && bun ./node_modules/@earendil-works/pi-coding-agent/dist/bundle/cli.js --version
cd ../../experiments && bun install && bun run typecheck
OPENCODE_MODEL=opencode/beam-free bun v2-api-example.ts
python3 plugin-smoke.py
```

Không cần copy source repository của ba tool vào bundle; báo cáo dẫn đến commit và dòng mã nguồn cố định trên GitHub.
