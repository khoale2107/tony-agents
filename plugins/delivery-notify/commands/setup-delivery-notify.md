---
description: Dựng agent đánh dấu giao hàng + báo khách — AI soạn tin cho đơn "đã giao", gửi qua connector, ghi lại đã báo.
---

Bạn đang giúp học viên khóa "50 AI Agents" của Tony Academy dựng **agent đánh dấu giao hàng + báo khách**. Chạy qua GÓI Claude Code. Nói tiếng Việt, ngắn gọn, tự làm giúp thao tác.

## Các bước
1. **Copy toàn bộ** `${CLAUDE_PLUGIN_ROOT}/templates/` vào thư mục con của agent. `chmod +x` cho `.sh`.
2. **Chạy thử ngay:** `./run.sh --dry-run` — xem AI soạn tin báo cho các đơn "đã giao" trong `deliveries_example.csv` (đơn DH004 đã có ngày ở cột "Đã báo" nên sẽ bị bỏ qua).
3. **Danh sách đơn:** tạo `deliveries.csv` (cột `Mã đơn,Khách,SĐT,Địa chỉ,Trạng thái` — thêm cột `Đã báo` cũng được, agent tự thêm nếu thiếu). Có thể export từ đơn vị vận chuyển / ERP qua Claude Code.
4. **Cấu hình trong `.env`:** `COMPANY_NAME`, `HOTLINE`. Muốn nhận tổng kết thì điền `TELEGRAM_BOT_TOKEN` + `TELEGRAM_CHAT_ID`.
5. **Nối kênh gửi thật:** copy `connector_example.py` -> `connector.py`, nhờ Claude Code viết `send_message()` theo Zalo OA / SMS của học viên. Không in lại token; không commit `.env`/`connector.py`.
6. **Đặt lịch chạy** vài lần/ngày để bắt đơn vừa giao xong: `./schedule_mac.sh 18 0` / `.\schedule_win.ps1 -At 18:00`.

## Cách hoạt động
- Agent chỉ báo đơn có Trạng thái chứa "đã giao" (khớp cả "Đã giao", "Đã giao thành công").
- Sau khi gửi, ghi ngày vào cột `Đã báo` để không nhắn lại đơn cũ. `--dry-run` không ghi file.

## Lưu ý
- Tôn trọng quy định gửi tin (khách đã đồng ý nhận). Khi chưa nối kênh, `--dry-run` cho xem trước toàn bộ tin.
