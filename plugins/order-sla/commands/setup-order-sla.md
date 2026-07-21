---
description: Dựng Order SLA — Nhắc khâu/đơn trễ deadline: so hạn xử lý với hôm nay, cảnh báo trễ/sắp hạn kèm lời nhắc AI
---

Bạn đang giúp học viên khóa "50 AI Agents" của Tony Academy dựng **Order SLA** vào thư mục hiện tại. Chạy qua GÓI Claude Code (không cần API key). Nói tiếng Việt, ngắn gọn, tự làm giúp thao tác.

## Các bước
1. **Copy toàn bộ file** trong `${CLAUDE_PLUGIN_ROOT}/templates/` vào thư mục con của agent (tạo nếu chưa có). Cấp quyền chạy cho `.sh` (chmod +x) trên macOS/Linux.
2. **Kiểm tra Claude Code:** máy đã có lệnh `claude` và `claude login` chưa (dùng gói). Nếu chưa, hướng dẫn đăng nhập.
3. **Chạy thử ngay:** `cd <thư mục> && ./run.sh --dry-run   # xem thử` (Windows: đổi `./run.sh` -> `.\run.ps1`). Chưa có dữ liệu thật thì nó tự dùng `orders_example.csv`. Cho học viên xem kết quả.
4. **Hỏi nguồn dữ liệu.** Xuất đơn hàng ra file `orders.csv` đặt cạnh `order_sla.py` (mỗi dòng = 1 khâu của 1 đơn, có cột **Hạn xử lý** dạng ngày dd/mm/yyyy). Nếu tên cột khác, chỉnh các biến `COL_*` trong `.env` cho khớp. Khâu nào ghi trạng thái "Xong/Hoàn thành" sẽ được bỏ qua.
5. **Điền `.env`:** `COMPANY_NAME`, `SOON_DAYS` (số ngày coi là sắp tới hạn), và `TELEGRAM_BOT_TOKEN` + `TELEGRAM_CHAT_ID`. Không in lại token; không commit `.env`.
6. **Đặt lịch.** Hỏi giờ (gợi ý mỗi sáng), chạy `./schedule_mac.sh` (Mac) / `.\schedule_win.ps1` (Win). Nhắc: máy phải BẬT + Claude Code còn đăng nhập gói.

## Lưu ý
- Không cần cài thư viện Python, không cần API key (dùng gói).
- Nếu không tìm thấy `claude`, điền `CLAUDE_BIN` vào `.env`.
- Dữ liệu/token riêng của học viên chỉ nằm trong `.env`/file cục bộ, không commit công khai.
