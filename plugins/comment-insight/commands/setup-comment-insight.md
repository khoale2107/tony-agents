---
description: Dựng Comment Insight — gom comment khách thành 3-5 insight + gợi ý chủ đề content nên làm, gửi Telegram.
---

Bạn đang giúp học viên khóa "50 AI Agents" của Tony Academy dựng **Comment Insight** vào thư mục hiện tại. Chạy qua GÓI Claude Code (không cần API key). Nói tiếng Việt, ngắn gọn, tự làm giúp thao tác.

## Các bước
1. **Copy toàn bộ file** trong `${CLAUDE_PLUGIN_ROOT}/templates/` vào thư mục con của agent (tạo nếu chưa có). Cấp quyền chạy cho `.sh` (chmod +x) trên macOS/Linux.
2. **Kiểm tra Claude Code:** máy đã có lệnh `claude` và đã `claude login` (dùng gói) chưa. Nếu chưa, hướng dẫn đăng nhập.
3. **Chạy thử ngay:** `cd <thư mục> && ./run.sh --dry-run` (Windows: đổi `./run.sh` -> `.\run.ps1`). Agent dùng sẵn `comments_example.csv` để in bản insight mẫu ra màn hình cho học viên xem.
4. **Hỏi nguồn dữ liệu.** Mỗi lần chạy ai gom comment khách vào `comments.csv` (2 cột: Nguồn, Nội dung)? Có thể export comment Facebook/TikTok/Instagram, hoặc dán tay comment đáng chú ý vào file. Đặt tên file thật ở `COMMENTS_FILE`, chỉnh `COL_SOURCE`/`COL_CONTENT` nếu tên cột khác.
5. **Điền `.env`:** `COMPANY_NAME`, `NGANH_HANG`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` (nơi nhận insight). KHÔNG in lại token ra màn hình; KHÔNG commit `.env`.
6. **Đặt lịch (tuỳ chọn):** muốn chạy hằng ngày thì hỏi giờ, `./schedule_mac.sh` (Mac) / `.\schedule_win.ps1` (Win). Nhắc: máy phải BẬT + Claude Code còn đăng nhập gói lúc chạy.

## Lưu ý
- Không cần cài thư viện Python, không cần API key (dùng gói).
- Nếu không tìm thấy `claude`, điền `CLAUDE_BIN` vào `.env`.
- Dữ liệu/token riêng của học viên chỉ nằm trong `.env`/file cục bộ, không commit công khai.
