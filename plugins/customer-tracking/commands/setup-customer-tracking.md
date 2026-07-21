---
description: Dựng Tra trạng thái đơn theo SĐT — Khách nhập số điện thoại, AI trả lời tự nhiên trạng thái từng đơn từ orders.csv.
---

Bạn đang giúp học viên khóa "50 AI Agents" của Tony Academy dựng **Tra trạng thái đơn theo số điện thoại** vào thư mục hiện tại. Chạy qua GÓI Claude Code (không cần API key). Nói tiếng Việt, ngắn gọn, tự làm giúp thao tác.

## Các bước
1. **Copy toàn bộ file** trong `${CLAUDE_PLUGIN_ROOT}/templates/` vào thư mục con của agent (tạo nếu chưa có). Cấp quyền chạy cho `.sh` (chmod +x) trên macOS/Linux.
2. **Kiểm tra Claude Code:** máy đã có lệnh `claude` và đã `claude login` (dùng gói) chưa. Nếu chưa, hướng dẫn đăng nhập.
3. **Chạy thử ngay:** `cd <thư mục> && ./run.sh 0901234567 --dry-run` (Windows: đổi `./run.sh` -> `.\run.ps1`). Không cần cấu hình gì — nó tự dùng `orders_example.csv`. Cho học viên xem đơn tìm được + câu trả lời AI cho khách. Thử tiếp một SĐT không có trong file để xem lời báo lịch sự.
4. **Nối dữ liệu thật.** Xuất đơn hàng thành `orders.csv` đặt cạnh `customer_tracking.py` (giữ đúng các cột, đặc biệt cột **SĐT** và **Trạng thái**). Nếu tên cột khác, chỉnh `COL_*` trong `.env`.
5. **Dùng thật:** đưa số điện thoại của khách vào lệnh, ví dụ `./run.sh 0912345678`. Agent tự chuẩn hoá số (bỏ +84/khoảng trắng) rồi để AI soạn câu trả lời gửi khách.
6. (Tuỳ chọn) **Đặt lịch** không cần thiết cho agent này vì chạy theo yêu cầu từng lần. Nếu muốn nối vào bot Zalo/CSKH thì gọi `customer_tracking.py` với SĐT khách nhắn tới.

## Lưu ý
- Không cần cài thư viện Python, không cần API key (dùng gói). Agent này **không** gửi Telegram.
- Nếu không tìm thấy `claude`, điền `CLAUDE_BIN` vào `.env`.
- Dữ liệu khách (file `orders.csv`, `.env`) chỉ nằm cục bộ, KHÔNG commit công khai; không in lại token của bất kỳ dịch vụ nào.
