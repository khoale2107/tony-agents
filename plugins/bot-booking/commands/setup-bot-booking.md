---
description: Dựng Bot booking — đọc tin nhắn khách, xem lịch trống và soạn báo giá + xác nhận đặt lịch. Test được ngay.
---

Bạn đang giúp học viên khóa "50 AI Agents" của Tony Academy dựng **Bot booking**. Chạy qua GÓI Claude Code (không cần API key). Nói tiếng Việt, ngắn gọn, tự làm giúp thao tác.

## Các bước
1. **Copy toàn bộ** `${CLAUDE_PLUGIN_ROOT}/templates/` vào thư mục con của agent. `chmod +x` cho `.sh`.
2. **Kiểm tra `claude` + `claude login`** (dùng gói).
3. **Chạy thử ngay:** `./run.sh "chụp cưới thứ 7 tuần này còn trống không, giá sao?"` — bot báo giá + lịch trống từ file mẫu.
4. **Bảng giá thật:** tạo `pricing.md` (đặt tên khác thì sửa `PRICING_FILE` trong `.env`).
5. **Lịch trống thật:** tạo `slots.csv` (cột `Ngày,Giờ,Trạng thái` — Trạng thái chứa "Trống" là còn nhận). Có thể đồng bộ từ Google Calendar/ERP qua Claude Code.
6. **Nối vào kênh chat** (Zalo/Messenger) nếu muốn tự động trả lời: nhờ Claude Code bọc `bot_booking.py` bằng webhook — đây là phần mở rộng, nói với học viên khi họ cần.

## Lưu ý
- Bot CHỈ báo giá/lịch có trong file, không bịa. Không cần API key. Không tìm thấy `claude` thì điền `CLAUDE_BIN`.
