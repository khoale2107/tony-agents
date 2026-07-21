---
description: Dựng Theo dõi trạng thái đơn theo khâu — Đọc orders.csv, đếm đơn ở mỗi khâu, tra chi tiết 1 đơn, gửi Telegram tổng quan.
---

Bạn đang giúp học viên khóa "50 AI Agents" của Tony Academy dựng **Theo dõi trạng thái đơn theo khâu** vào thư mục hiện tại. Chạy qua GÓI Claude Code (không cần API key). Nói tiếng Việt, ngắn gọn, tự làm giúp thao tác.

## Các bước
1. **Copy toàn bộ file** trong `${CLAUDE_PLUGIN_ROOT}/templates/` vào thư mục con của agent (tạo nếu chưa có). Cấp quyền chạy cho `.sh` (chmod +x) trên macOS/Linux.
2. **Kiểm tra Claude Code:** máy đã có lệnh `claude` và đã `claude login` (dùng gói) chưa. Nếu chưa, hướng dẫn đăng nhập.
3. **Chạy thử ngay:** `cd <thư mục> && ./run.sh --dry-run` (Windows: đổi `./run.sh` -> `.\run.ps1`). Không cần cấu hình gì — nó tự dùng `orders_example.csv`. Cho học viên xem bảng theo khâu + nhận định AI.
4. **Tra 1 đơn:** `./run.sh DH-1025` -> in chi tiết đơn + khâu hiện tại + thanh tiến trình.
5. **Nối dữ liệu thật.** Xuất đơn hàng thành `orders.csv` đặt cạnh `order_status.py` (giữ đúng các cột). Nếu tên cột khác, chỉnh `COL_*` trong `.env`. Nếu quy trình có các khâu khác, sửa danh sách `STAGES` trong `order_status.py`.
6. **Điền Telegram** trong `.env` (`TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`) để chạy thật `./run.sh` gửi tổng quan. Không in lại token; không commit `.env`.
7. **Đặt lịch.** Hỏi giờ (vd 8h sáng mỗi ngày), chạy `./schedule_mac.sh` (Mac) / `.\schedule_win.ps1` (Win). Nhắc: máy phải BẬT + Claude Code còn đăng nhập gói.

## Lưu ý
- Không cần cài thư viện Python, không cần API key (dùng gói).
- Nếu không tìm thấy `claude`, điền `CLAUDE_BIN` vào `.env`.
- Dữ liệu/token riêng của học viên chỉ nằm trong `.env`/file cục bộ, không commit công khai.
