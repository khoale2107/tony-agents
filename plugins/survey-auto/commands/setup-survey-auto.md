---
description: Dựng Survey tự động sau dịch vụ — gửi khảo sát cho khách vừa xong và tổng hợp phản hồi bằng AI.
---

Bạn đang giúp học viên khóa "50 AI Agents" của Tony Academy dựng **Survey tự động sau dịch vụ**. Chạy qua GÓI Claude Code. Nói tiếng Việt, ngắn gọn, tự làm giúp thao tác.

## Các bước
1. **Copy toàn bộ** `${CLAUDE_PLUGIN_ROOT}/templates/` vào thư mục con của agent. `chmod +x` cho `.sh`.
2. **Chạy thử ngay:**
   - `./run.sh send --dry-run` — xem tin mời khảo sát soạn cho khách trong `done_example.csv`.
   - `./run.sh summarize --dry-run` — xem AI tổng hợp phản hồi từ `responses_example.csv`.
3. **Cấu hình `.env`:** `SURVEY_LINK` (link Google Form của học viên), Telegram (cho phần tổng hợp).
4. **Dữ liệu thật:** `done.csv` (khách vừa xong: `Khách,SĐT,Dịch vụ,Ngày xong`) và `responses.csv` (phản hồi: `Khách,Điểm,Nhận xét`) — có thể lấy từ Form/ERP qua Claude Code.
5. **Gửi tin thật:** copy `connector_example.py` -> `connector.py`, nhờ Claude Code viết `send_message()` (Zalo/SMS/email).
6. **Đặt lịch:** gửi khảo sát cuối ngày + tổng hợp sáng hôm sau bằng `./schedule_mac.sh` / `.\schedule_win.ps1` (chạy 2 lịch với lệnh khác nhau nếu cần).

## Lưu ý
- Không cần API key. Không tìm thấy `claude` thì điền `CLAUDE_BIN`. Không commit `.env`/`connector.py`.
