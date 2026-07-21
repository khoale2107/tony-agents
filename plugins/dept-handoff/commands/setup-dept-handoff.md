---
description: Dựng Dept Handoff — điều phối đơn giữa các bộ phận SALES → SẢN XUẤT → GIAO, AI soạn thông báo bàn giao cho bộ phận nhận
---

Bạn đang giúp học viên khóa "50 AI Agents" của Tony Academy dựng **Dept Handoff** vào thư mục hiện tại. Chạy qua GÓI Claude Code (không cần API key). Nói tiếng Việt, ngắn gọn, tự làm giúp thao tác.

## Các bước
1. **Copy toàn bộ file** trong `${CLAUDE_PLUGIN_ROOT}/templates/` vào thư mục con của agent (tạo nếu chưa có). Cấp quyền chạy cho `.sh` (chmod +x) trên macOS/Linux.
2. **Kiểm tra Claude Code:** máy đã có lệnh `claude` và đã `claude login` chưa (dùng gói). Nếu chưa, hướng dẫn đăng nhập.
3. **Chạy thử ngay:**
   - `cd <thư mục> && ./run.sh list --dry-run`   (xem bảng đơn theo bộ phận)
   - `./run.sh handoff DH001 --dry-run`   (xem thử AI soạn thông báo bàn giao, chưa ghi file, chưa gửi)
   - Windows: đổi `./run.sh` → `.\run.ps1`.
4. **Nối dữ liệu thật.** Tạo `orders.csv` đúng cột `Mã đơn,Khách,SĐT,Sản phẩm,Bộ phận,Ghi chú,Cập nhật` (Bộ phận là 1 trong: SALES, SẢN XUẤT, GIAO). Có thể export từ Google Sheet ra CSV. Đổi tên/đường dẫn thì chỉnh `ORDERS_FILE` trong `.env`. Chưa có thì cứ dùng `orders_example.csv`.
5. **Điền Telegram** trong `.env`:
   - `TELEGRAM_BOT_TOKEN` (một bot chung).
   - `CHAT_SALES`, `CHAT_SANXUAT`, `CHAT_GIAO` = chat id (nhóm hoặc cá nhân) của từng bộ phận nhận thông báo. Lấy chat id bằng cách thêm bot vào nhóm rồi gọi `getUpdates`, hoặc dùng @userinfobot.
   - Không in lại token; không commit `.env`.
6. **Cách dùng hằng ngày.**
   - `./run.sh list`   → xem nhanh đơn đang nằm ở bộ phận nào.
   - `./run.sh handoff <mã>`   → đẩy đơn sang bộ phận kế (SALES → SẢN XUẤT → GIAO), AI soạn thông báo và gửi thẳng vào chat của bộ phận NHẬN, tự ghi lại `orders.csv`.
7. **Đặt lịch (tùy chọn).** Việc bàn giao thường chạy tay theo lệnh nên ít cần lịch. Nếu muốn tự động gửi bảng `list` mỗi sáng thì hỏi giờ rồi chạy `./schedule_mac.sh` (Mac) / `.\schedule_win.ps1` (Win). Nhắc: máy phải BẬT + Claude Code còn đăng nhập gói.

## Lưu ý
- Không cần cài thư viện Python, không cần API key (dùng gói).
- Nếu không tìm thấy `claude`, điền `CLAUDE_BIN` vào `.env`.
- `handoff` ghi đè `orders.csv` — giữ file này trong git/back-up riêng của học viên, KHÔNG commit công khai cùng `.env`.
