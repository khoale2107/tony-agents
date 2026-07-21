---
description: Dựng Content Calendar — lịch content, nhắc bài hôm nay + 3 ngày tới chưa đăng, cảnh báo ngày trống, AI gợi ý, gửi Telegram
---

Bạn đang giúp học viên khóa "50 AI Agents" của Tony Academy dựng **Content Calendar** vào thư mục hiện tại. Chạy qua GÓI Claude Code (không cần API key). Nói tiếng Việt, ngắn gọn, tự làm giúp thao tác.

## Các bước
1. **Copy toàn bộ file** trong `${CLAUDE_PLUGIN_ROOT}/templates/` vào thư mục con của agent (tạo nếu chưa có). Cấp quyền chạy cho `.sh` (chmod +x) trên macOS/Linux.
2. **Kiểm tra Claude Code:** máy đã có lệnh `claude` và đã `claude login` chưa (dùng gói). Nếu chưa, hướng dẫn đăng nhập.
3. **Chạy thử ngay:** `cd <thư mục> && ./run.sh --dry-run` (Windows: đổi `./run.sh` -> `.\run.ps1`). Chạy được ngay với `calendar_example.csv`, cho học viên xem kết quả.
4. **Hỏi nguồn dữ liệu.** Tạo file `calendar.csv` thật (4 cột: Ngày,Kênh,Chủ đề,Trạng thái) — có thể export từ Google Sheet/Notion/Trello. Định dạng ngày `dd/mm/yyyy`. Nếu chưa có, agent tự dùng `calendar_example.csv`. Chỉnh `COL_*` trong `.env` nếu tên cột khác, đặt `HORIZON_DAYS` nếu muốn soi xa hơn 3 ngày.
5. **Điền Telegram** trong `.env` (`TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`). Không in lại token; không commit `.env`.
6. **Đặt lịch.** Hỏi giờ (ví dụ 8h sáng mỗi ngày), chạy `./schedule_mac.sh` (Mac) / `.\schedule_win.ps1` (Win). Nhắc: máy phải BẬT + Claude Code còn đăng nhập gói.

## Lưu ý
- Không cần cài thư viện Python, không cần API key (dùng gói).
- Nếu không tìm thấy `claude`, điền `CLAUDE_BIN` vào `.env`.
- Bài có trạng thái "đã đăng / xong / hủy" được tự bỏ qua. Ngày không có bài nào -> cảnh báo NGÀY TRỐNG.
- Dữ liệu/token của học viên chỉ nằm trong `.env`/file cục bộ, không commit công khai.
