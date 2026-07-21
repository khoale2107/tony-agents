---
description: Dựng Chấm công qua bot Telegram — nhân viên gõ /checkin, /checkout, bot ghi bảng công và tổng hợp theo ngày.
---

Bạn đang giúp học viên khóa "50 AI Agents" của Tony Academy dựng **Bot chấm công Telegram**. Chạy qua GÓI Claude Code (không cần API key). Nói tiếng Việt, ngắn gọn, tự làm giúp thao tác.

## Ý tưởng
Nhân viên nhắn `/checkin` khi đến, `/checkout` khi về. Bot ghi vào `attendance.csv` (Nhân viên, Ngày, Giờ vào, Giờ ra) — tên lấy từ chính người gửi trong Telegram. Cuối ngày chạy `report` để ra bảng công.

## Các bước
1. **Copy toàn bộ** `${CLAUDE_PLUGIN_ROOT}/templates/` vào thư mục con của agent. `chmod +x` cho các file `.sh`.
2. **Chạy thử ngay (không cần cấu hình):** `./run.sh report --dry-run` — bot đọc `attendance_example.csv` và in bảng công hôm nay (Windows: `.\run.ps1 report --dry-run`).
3. **Tạo bot:** trong Telegram nhắn @BotFather → `/newbot` lấy token. Nếu chấm công trong NHÓM: `/setprivacy` → **Disable** để bot đọc được tin nhóm, rồi mời bot vào nhóm.
4. **Điền `.env`:** copy `.env.example` → `.env`, dán `TELEGRAM_BOT_TOKEN`. Muốn gửi bảng tổng hợp cuối ngày thì điền thêm `TELEGRAM_CHAT_ID` (chat/nhóm nhận báo cáo). KHÔNG in lại token; KHÔNG commit `.env`.
5. **Nhận lệnh chấm công:** `./run.sh poll` đọc tin mới, ghi công và trả lời xác nhận. Muốn tự động: đặt lịch chạy `poll` mỗi 1 phút bằng `./schedule_mac.sh` / `.\schedule_win.ps1`.
6. **Chốt bảng công:** cuối ngày chạy `./run.sh report` để gửi bảng công vào `TELEGRAM_CHAT_ID`. Có thể đặt lịch chạy `report` một lần vào cuối giờ làm.

## Lưu ý
- File thật là `attendance.csv` (bot tự tạo khi có lượt chấm đầu tiên). Khi chưa có, mọi lệnh đọc sẽ tạm dùng `attendance_example.csv` để chạy thử.
- `/checkin` chỉ ghi giờ vào lần đầu trong ngày; `/checkout` cập nhật giờ ra mới nhất. Nhân viên gõ `/congtoi` để xem công hôm nay của mình.
- Bật `AI_SUMMARY=1` trong `.env` nếu muốn Claude Code viết 1 câu nhận xét cuối bảng report (đi muộn, chưa check-out...). Mặc định tắt để chạy offline.
- Không cần cài thư viện Python, không cần API key nếu dùng gói Claude Code.
