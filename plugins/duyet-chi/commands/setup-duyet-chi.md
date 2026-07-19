---
description: Dựng Duyệt chi đa cấp — Duyệt chi đa cấp qua Telegram: định tuyến theo số tiền (<5tr trưởng nhóm, 5-20tr
---

Bạn đang giúp học viên khóa "50 AI Agents" của Tony Academy dựng **Duyệt chi đa cấp** vào thư mục hiện tại. Chạy qua GÓI Claude Code (không cần API key). Nói tiếng Việt, ngắn gọn, tự làm giúp thao tác.

## Các bước
1. **Copy toàn bộ file** trong `${CLAUDE_PLUGIN_ROOT}/templates/` vào thư mục con của agent (tạo nếu chưa có). Cấp quyền chạy cho `.sh` (chmod +x) trên macOS/Linux.
2. **Kiểm tra Claude Code:** máy đã có lệnh `claude` và `claude login` chưa (dùng gói). Nếu chưa, hướng dẫn đăng nhập.
3. **Chạy thử ngay:** `cd <thư mục> && ./run.sh submit "Mua vật tư" 8000000            # gửi yêu cầu duyệt` (Windows: đổi `./run.sh` -> `.\run.ps1`). Cho học viên xem kết quả.
4. **Cấu hình duyệt chi** trong `.env`: `TELEGRAM_BOT_TOKEN` (từ @BotFather), ngưỡng `TIER1_MAX`/`TIER2_MAX`, và chat id 3 cấp `CHAT_TRUONG_NHOM`/`CHAT_QUAN_LY`/`CHAT_CEO` (từ @userinfobot hoặc chat id group). Không in lại token; không commit `.env`.
5. **Giải thích vận hành:** `submit` để gửi yêu cầu, `poll` để nhận quyết định (có thể đặt lịch chạy `poll` định kỳ, hoặc chạy tay).

## Lưu ý
- Không cần cài thư viện Python, không cần API key (dùng gói).
- Nếu không tìm thấy `claude`, điền `CLAUDE_BIN` vào `.env`.
- Dữ liệu/token riêng của học viên chỉ nằm trong `.env`/file cục bộ, không commit công khai.
