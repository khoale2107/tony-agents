---
description: Dựng Báo cáo lead sáng — Điểm danh khách tiềm năng mỗi sáng: lead mới, khách 3+ ngày chưa xử lý, nghi no-
---

Bạn đang giúp học viên khóa "50 AI Agents" của Tony Academy dựng **Báo cáo lead sáng** vào thư mục hiện tại. Chạy qua GÓI Claude Code (không cần API key). Nói tiếng Việt, ngắn gọn, tự làm giúp thao tác.

## Các bước
1. **Copy toàn bộ file** trong `${CLAUDE_PLUGIN_ROOT}/templates/` vào thư mục con của agent (tạo nếu chưa có). Cấp quyền chạy cho `.sh` (chmod +x) trên macOS/Linux.
2. **Kiểm tra Claude Code:** máy đã có lệnh `claude` và `claude login` chưa (dùng gói). Nếu chưa, hướng dẫn đăng nhập.
3. **Chạy thử ngay:** `cd <thư mục> && ./run.sh --dry-run` (Windows: đổi `./run.sh` -> `.\run.ps1`). Cho học viên xem kết quả.
4. **Hỏi nguồn dữ liệu.** Google Sheet (đặt `SOURCE=gsheet`, điền `GOOGLE_SHEET_CSV_URL` link CSV export) hay ERP (đặt `SOURCE=custom`, viết `adapter_custom.py` — xem cách làm ở CFO Agent). Chỉnh `COL_*` cho khớp cột. Nếu chưa có dữ liệu, để trống dùng sample_data.csv.
5. **Điền Telegram + tham số riêng** trong `.env` (token, chat id, và ngân sách/ngưỡng nếu có). Không in lại token; không commit `.env`.
6. **Đặt lịch.** Hỏi giờ, chạy `./schedule_mac.sh` (Mac) / `.\schedule_win.ps1` (Win). Nhắc: máy phải BẬT + Claude Code còn đăng nhập gói.

## Lưu ý
- Không cần cài thư viện Python, không cần API key (dùng gói).
- Nếu không tìm thấy `claude`, điền `CLAUDE_BIN` vào `.env`.
- Dữ liệu/token riêng của học viên chỉ nằm trong `.env`/file cục bộ, không commit công khai.
