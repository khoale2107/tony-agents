---
description: Dựng Zalo ZNS — soạn & gửi tin xác nhận đơn / nhắc lịch hẹn / nhắc thanh toán theo mẫu.
---

Bạn đang giúp học viên khóa "50 AI Agents" của Tony Academy dựng **Zalo ZNS**. Chạy qua GÓI Claude Code cho phần soạn tin. Nói tiếng Việt, ngắn gọn, tự làm giúp thao tác.

## Các bước
1. **Copy toàn bộ** `${CLAUDE_PLUGIN_ROOT}/templates/` vào thư mục con của agent. `chmod +x` cho `.sh`.
2. **Chạy thử ngay:** `./run.sh --dry-run` — xem nội dung ZNS soạn từ `queue_example.csv` (3 loại: xác nhận đơn / nhắc hẹn / nhắc thanh toán).
3. **Nguồn việc:** tạo `queue.csv` (cột `Loại,Khách,SĐT,Thời điểm,Ghi chú`). `Loại` nhận: `xác nhận đơn` | `nhắc hẹn` | `nhắc thanh toán`. Có thể sinh file này từ ERP qua Claude Code.
4. **Muốn AI viết tin mượt hơn:** đặt `AI_POLISH=1` trong `.env` (dùng gói).
5. **Nối Zalo ZNS thật:** copy `connector_example.py` -> `connector.py`, nhờ Claude Code viết `send_zns()` theo ZNS template + OA token của học viên (điền `ZALO_OA_TOKEN`, `ZNS_TEMPLATE_ID` trong `.env`). Không in lại token; không commit `.env`/`connector.py`.
6. **Đặt lịch** nếu muốn quét đơn/nhắc định kỳ: `./schedule_mac.sh` / `.\schedule_win.ps1`.

## Lưu ý
- ZNS thật cần OA đã duyệt template. Khi chưa nối, `--dry-run` vẫn cho xem toàn bộ nội dung sẽ gửi.
