---
description: Dựng Xin nghỉ phép / chi phí có luồng duyệt — bot Telegram gửi nút Duyệt/Từ chối tới quản lý, ghi log requests.csv
---

Bạn đang giúp học viên khóa "50 AI Agents" của Tony Academy dựng **Xin nghỉ phép / chi phí có luồng duyệt** vào thư mục hiện tại. Chạy qua GÓI Claude Code (không cần API key). Nói tiếng Việt, ngắn gọn, tự làm giúp thao tác.

## Các bước
1. **Copy toàn bộ file** trong `${CLAUDE_PLUGIN_ROOT}/templates/` vào thư mục con của agent (tạo nếu chưa có). Cấp quyền chạy cho `.sh` (chmod +x) trên macOS/Linux.
2. **Chạy thử ngay** (không cần cấu hình gì):
   ```
   cd <thư mục> && ./run.sh submit-leave "Nguyễn Văn A" 25/07/2026 "Về quê có việc" --dry-run
   ./run.sh submit-expense "Trần Thị B" 850000 "Taxi đi khảo sát" --dry-run
   ```
   (Windows: đổi `./run.sh` -> `.\run.ps1`). Cho học viên xem tin sẽ gửi + 2 nút.
3. **Tạo bot Telegram:** nhắn @BotFather lấy `TELEGRAM_BOT_TOKEN`; nhắn @userinfobot để lấy chat id của quản lý (hoặc chat id group duyệt) cho `TELEGRAM_CHAT_ID`. Điền vào `.env`. Không in lại token; không commit `.env`.
4. **Chạy thật:**
   - `submit-leave "<Nhân viên>" <ngày> "<lý do>"` hoặc `submit-expense "<Nhân viên>" <số tiền> "<nội dung>"` — bắn tin có nút [✅ Duyệt][❌ Từ chối] tới quản lý, ghi vào `requests.csv`.
   - Quản lý bấm nút -> chạy `./run.sh poll` để nhận quyết định: cập nhật `requests.csv` và sửa lại nội dung tin đã gửi.
5. **Đặt lịch (tùy chọn):** cho `poll` chạy định kỳ vài phút/lần bằng `schedule_mac.sh` (macOS) hoặc `schedule_win.ps1` (Windows) để tự thu quyết định; `submit-*` thì chạy tay mỗi khi có yêu cầu.

## Lưu ý
- Không cần cài thư viện Python, không cần API key (dùng gói Claude Code).
- File `requests_example.csv` chỉ để tham khảo cấu trúc log; khi chạy thật hệ thống tự tạo/ghi `requests.csv`.
- `offset` của Telegram lưu ở `.tg_offset` — đừng xóa nếu không muốn xử lý lại các quyết định cũ.
- Token và `.env` chỉ nằm cục bộ, tuyệt đối không commit công khai.
