---
description: Dựng KPI hàng ngày — đọc kpi.csv, tính % đạt từng nhân viên, xếp hạng, AI nhận định ai vượt/ai hụt, gửi Telegram
---

Bạn đang giúp học viên khóa "50 AI Agents" của Tony Academy dựng **KPI hàng ngày từng nhân viên** vào thư mục hiện tại. Chạy qua GÓI Claude Code (không cần API key). Nói tiếng Việt, ngắn gọn, tự làm giúp thao tác.

## Các bước
1. **Copy toàn bộ file** trong `${CLAUDE_PLUGIN_ROOT}/templates/` vào thư mục con của agent (tạo nếu chưa có). Cấp quyền chạy cho `.sh` (chmod +x) trên macOS/Linux.
2. **Kiểm tra Claude Code:** máy đã có lệnh `claude` và đã `claude login` chưa (dùng gói). Nếu chưa, hướng dẫn đăng nhập.
3. **Chạy thử ngay:** `cd <thư mục> && ./run.sh --dry-run` (Windows: đổi `./run.sh` -> `.\run.ps1`). Agent sẽ dùng `kpi_example.csv` và in bảng xếp hạng + nhận định AI ra màn hình.
4. **Hỏi nguồn dữ liệu.** Đặt file KPI thật tên `kpi.csv` cạnh `daily_kpi.py`, đủ 3 cột: `Nhân viên, Chỉ tiêu, Thực đạt` (chỉ tiêu/thực đạt có thể là doanh số, số đơn, số cuộc gọi... miễn cùng đơn vị). Nếu tên cột khác, chỉnh `COL_NAME/COL_TARGET/COL_ACTUAL` trong `.env`. Muốn dùng tên file khác thì đổi `KPI_FILE`.
5. **Điền Telegram** trong `.env` (`TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`). Không in lại token; không commit `.env`.
6. **Đặt lịch.** Hỏi giờ chạy (thường cuối giờ làm, ví dụ 18:00 mỗi ngày), chạy `./schedule_mac.sh` (Mac) / `.\schedule_win.ps1` (Win). Nhắc: máy phải BẬT + Claude Code còn đăng nhập gói.

## Lưu ý
- Không cần cài thư viện Python, không cần API key (dùng gói).
- Nếu không tìm thấy `claude`, điền `CLAUDE_BIN` vào `.env`.
- Dữ liệu/token riêng của học viên chỉ nằm trong `.env`/file cục bộ, không commit công khai.
