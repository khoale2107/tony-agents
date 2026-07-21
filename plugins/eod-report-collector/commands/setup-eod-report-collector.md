---
description: Dựng Bot thu báo cáo cuối ngày — gom báo cáo từng phòng, AI tổng hợp gọn gửi sếp qua Telegram ~21h.
---

Bạn đang giúp học viên khóa "50 AI Agents" của Tony Academy dựng **Bot thu báo cáo cuối ngày** vào thư mục hiện tại. Chạy qua GÓI Claude Code (không cần API key). Nói tiếng Việt, ngắn gọn, tự làm giúp thao tác.

## Các bước
1. **Copy toàn bộ file** trong `${CLAUDE_PLUGIN_ROOT}/templates/` vào thư mục con của agent (tạo nếu chưa có). Cấp quyền chạy cho `.sh` (chmod +x) trên macOS/Linux.
2. **Kiểm tra Claude Code:** máy đã có lệnh `claude` và đã `claude login` (dùng gói) chưa. Nếu chưa, hướng dẫn đăng nhập.
3. **Chạy thử ngay:** `cd <thư mục> && ./run.sh --dry-run` (Windows: đổi `./run.sh` -> `.\run.ps1`). Bot dùng sẵn `reports_example.csv` để in bản tổng hợp mẫu ra màn hình cho học viên xem.
4. **Hỏi nguồn dữ liệu.** Mỗi ngày ai gom báo cáo nhân viên vào `reports.csv` (3 cột: Nhân viên, Phòng, Nội dung báo cáo)? Có thể là Google Form xuất CSV, hoặc để nhân viên nhắn rồi dán vào file. Đặt tên file thật ở `REPORTS_FILE`, chỉnh `COL_*` nếu tên cột khác.
5. **Điền `.env`:** `COMPANY_NAME`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` (chat của sếp). KHÔNG in lại token ra màn hình; KHÔNG commit `.env`.
6. **Đặt lịch ~21h:** hỏi giờ chạy, `./schedule_mac.sh` (Mac) / `.\schedule_win.ps1` (Win). Nhắc: máy phải BẬT + Claude Code còn đăng nhập gói lúc chạy.

## Lưu ý
- Không cần cài thư viện Python, không cần API key (dùng gói).
- Nếu không tìm thấy `claude`, điền `CLAUDE_BIN` vào `.env`.
- Dữ liệu/token riêng của học viên chỉ nằm trong `.env`/file cục bộ, không commit công khai.
