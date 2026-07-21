---
description: Dựng Xác nhận thanh toán — gửi nút [✅ Đã nhận tiền][❌ Chưa] cho kế toán qua Telegram, ghi payments.csv, poll cập nhật kết quả.
---

Bạn đang giúp học viên khóa "50 AI Agents" của Tony Academy dựng **Xác nhận thanh toán qua nút bấm** vào thư mục hiện tại. Chạy qua GÓI Claude Code (không cần API key). Nói tiếng Việt, ngắn gọn, tự làm giúp thao tác.

## Các bước
1. **Copy toàn bộ file** trong `${CLAUDE_PLUGIN_ROOT}/templates/` vào thư mục con của agent (tạo nếu chưa có). Cấp quyền chạy cho `.sh` trên macOS/Linux: `chmod +x *.sh`.
2. **Kiểm tra Claude Code:** máy đã có lệnh `claude` và đã `claude login` (dùng gói) chưa. Nếu chưa, hướng dẫn đăng nhập.
3. **Chạy thử ngay (không cần cấu hình):**
   `python3 payment_confirm.py submit DH001 5000000 --dry-run`
   Nó in ra tin sẽ gửi kèm 2 nút. Cho học viên xem kết quả.
4. **Cấu hình `.env`** (copy từ `.env.example`):
   - `TELEGRAM_BOT_TOKEN`: tạo bot ở @BotFather.
   - `TELEGRAM_CHAT_ID`: chat của kế toán — lấy id cá nhân qua @userinfobot, hoặc id group.
   Không in lại token; không commit `.env`.
5. **Chạy thật:**
   - Gửi yêu cầu: `python3 payment_confirm.py submit DH002 12500000`
   - Kế toán bấm nút trên Telegram.
   - Nhận kết quả: `python3 payment_confirm.py poll` (cập nhật `payments.csv`, sửa lại tin, lưu offset ở `.tg_offset`).
6. **Đặt lịch (tùy chọn):** cho `poll` chạy định kỳ bằng `schedule_mac.sh` (macOS) hoặc `schedule_win.ps1` (Windows) để tự nhận kết quả bấm nút.

## Lưu ý
- Không cần cài thư viện Python, không cần API key (dùng gói).
- Nếu không tìm thấy `claude`, điền `CLAUDE_BIN` vào `.env`.
- `payments.csv` là sổ trạng thái thật; `payments_example.csv` chỉ là mẫu minh họa định dạng.
- Token/chat id riêng chỉ nằm trong `.env` cục bộ, không commit công khai.
