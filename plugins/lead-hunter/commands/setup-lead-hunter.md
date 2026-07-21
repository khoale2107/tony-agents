---
description: Dựng Lead Hunter — quét bài/bình luận group, fanpage và chấm điểm khách tiềm năng, xếp hạng.
---

Bạn đang giúp học viên khóa "50 AI Agents" của Tony Academy dựng **Lead Hunter**. Chạy qua GÓI Claude Code. Nói tiếng Việt, ngắn gọn, tự làm giúp thao tác.

## Các bước
1. **Copy toàn bộ** `${CLAUDE_PLUGIN_ROOT}/templates/` vào thư mục con của agent. `chmod +x` cho `.sh`.
2. **Chạy thử ngay:** `./run.sh --dry-run` — AI chấm điểm & xếp hạng khách tiềm năng từ `export_example.csv`.
3. **Cấu hình `.env`:** `NGANH_HANG` (để AI hiểu thế nào là khách tiềm năng), `MIN_SCORE`, `TOP_N`, và Telegram.
4. **Nguồn dữ liệu quét:** tạo `export.csv` (cột `Nguồn,Người,Nội dung,Link`). Việc quét thật là 1 seam: copy `collector_example.py` -> `collector.py`, nhờ Claude Code viết bộ thu (export Facebook/group, API, hoặc công cụ scrape) -> ghi ra `export.csv`.
5. **Đặt lịch** quét mỗi sáng: `./schedule_mac.sh 8 0` / `.\schedule_win.ps1 -At 08:00`.

## Lưu ý
- Tôn trọng điều khoản nền tảng khi thu dữ liệu. Không cần API key cho phần chấm điểm (dùng gói). Không commit `.env`/`collector.py`.
