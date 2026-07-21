---
description: Dựng Order Pipeline — quản lý đơn hàng qua các khâu NHẬN → XỬ LÝ → QC → TẠO ĐƠN → XONG, có AI tóm tắt tình hình
---

Bạn đang giúp học viên khóa "50 AI Agents" của Tony Academy dựng **Order Pipeline** vào thư mục hiện tại. Chạy qua GÓI Claude Code (không cần API key). Nói tiếng Việt, ngắn gọn, tự làm giúp thao tác.

## Các bước
1. **Copy toàn bộ file** trong `${CLAUDE_PLUGIN_ROOT}/templates/` vào thư mục con của agent (tạo nếu chưa có). Cấp quyền chạy cho `.sh` (chmod +x) trên macOS/Linux.
2. **Kiểm tra Claude Code:** máy đã có lệnh `claude` và đã `claude login` chưa (dùng gói). Nếu chưa, hướng dẫn đăng nhập.
3. **Chạy thử ngay:**
   - `cd <thư mục> && ./run.sh list --dry-run`   (xem bảng đơn theo khâu + AI tóm tắt)
   - `./run.sh advance DH001 --dry-run`   (xem thử chuyển khâu, chưa ghi file)
   - Windows: đổi `./run.sh` → `.\run.ps1`.
4. **Nối dữ liệu thật.** Tạo `orders.csv` đúng cột `Mã đơn,Khách,SĐT,Sản phẩm,Khâu,Người phụ trách,Cập nhật` (Khâu là 1 trong: NHẬN, XỬ LÝ, QC, TẠO ĐƠN, XONG). Có thể export từ Google Sheet ra CSV. Nếu đổi tên/đường dẫn file, chỉnh `ORDERS_FILE` trong `.env`. Chưa có thì cứ dùng `orders_example.csv`.
5. **Điền Telegram** trong `.env` (`TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`). Không in lại token; không commit `.env`.
6. **Cách dùng hằng ngày.**
   - `./run.sh list`   → gửi bảng pipeline + nhận định AI vào Telegram.
   - `./run.sh advance <mã> [người phụ trách mới]`   → đẩy đơn sang khâu kế, tự ghi lại `orders.csv` và báo Telegram.
7. **Đặt lịch (tùy chọn).** Muốn tự động gửi bảng `list` mỗi sáng: hỏi giờ rồi chạy `./schedule_mac.sh` (Mac) / `.\schedule_win.ps1` (Win). Nhắc: máy phải BẬT + Claude Code còn đăng nhập gói.

## Lưu ý
- Không cần cài thư viện Python, không cần API key (dùng gói).
- Nếu không tìm thấy `claude`, điền `CLAUDE_BIN` vào `.env`.
- `advance` ghi đè `orders.csv` — nên giữ file này trong git/back-up riêng của học viên, KHÔNG commit công khai cùng `.env`.
