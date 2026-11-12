# REPORT TASK 2

**Người thực hiện:** Trần Anh Đăng  
**Mentor phụ trách:** Hoàng Danh Liêm  
**Ngày:** 12/11/2026

Bản báo cáo đầy đủ, dẫn đến mã nguồn theo commit và dòng cụ thể: [report/REPORT_TASK2.md](report/REPORT_TASK2.md).

Code thực nghiệm: [OpenCode v2 API/SDK](experiments/v2-api-example.ts), [plugin v1](experiments/v1-plugin/index.ts), [plugin đã port v2](experiments/v2-port-plugin/index.ts), [benchmark runner](experiments/benchmark.py).

OpenCode v1.19.5 và v2.2.7 đã cài song song trong `versions/`. Benchmark cùng model `opencode/beam-free`, 5 lượt cho mỗi task và mỗi bản OpenCode: cả hai pass 15/15. Bảng thời gian/token trung vị, giới hạn phương pháp và log gốc nằm trong báo cáo. Chưa có benchmark ba tool cùng model vì Pi chưa có provider credential tương ứng; báo cáo ghi rõ phần này.
