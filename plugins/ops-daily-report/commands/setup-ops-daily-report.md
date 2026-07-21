---
description: Dựng Ops Daily Report — báo cáo vận hành cuối ngày: đếm đơn theo khâu, phát hiện khâu tắc, AI đề xuất xử lý
---

Bạn đang giúp học viên khóa "50 AI Agents" của Tony Academy dựng **Ops Daily Report** vào thư mục hiện tại. Chạy qua GÓI Claude Code (không cần API key). Nói tiếng Việt, ngắn gọn, tự làm giúp thao tác.

## Các bước
1. **Copy toàn bộ file** trong `${CLAUDE_PLUGIN_ROOT}/templates/` vào thư mục con của agent (tạo nếu chưa có). Cấp quyền chạy cho `.sh` (`chmod +x *.sh`) trên macOS/Linux.
2. **Kiểm tra Claude Code:** máy đã có lệnh `claude` và đã `claude login` chưa (dùng gói). Nếu chưa, hướng dẫn đăng nhập.
3. **Chạy thử ngay:** `cd <thư mục> && ./run.sh --dry-run` (Windows: `.\run.ps1 --dry-run`). Không cấu hình gì vẫn ra kết quả nhờ `orders_example.csv`. Cho học viên xem bản báo cáo mẫu.
4. **Hỏi nguồn dữ liệu.** Học viên xuất đơn hàng ra file CSV (đặt tên `orders.csv`, cùng thư mục). Cột tối thiểu: `Mã đơn, Khâu, Hạn giao, Cập nhật`. Nếu tên cột khác, chỉnh `COL_STAGE/COL_DEADLINE/COL_UPDATE` trong `.env`. Nếu quy trình xưởng có các khâu khác, điền `STAGES` (khâu cuối cùng = đã xong).
5. **Chỉnh ngưỡng tắc** trong `.env`: `STALE_DAYS` (bao lâu không cập nhật = ứ đọng), `PILEUP_THRESHOLD` (tồn bao nhiêu đơn 1 khâu = dồn ứ).
6. **Điền Telegram** trong `.env` (`TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`). Không in lại token; không commit `.env`.
7. **Đặt lịch cuối ngày.** Hỏi giờ (vd 18:00), chạy `./schedule_mac.sh` (Mac) / `.\schedule_win.ps1` (Win). Nhắc: máy phải BẬT + Claude Code còn đăng nhập gói.

## Lưu ý
- Không cần cài thư viện Python, không cần API key (dùng gói Claude Code).
- Nếu không tìm thấy `claude`, điền `CLAUDE_BIN` vào `.env`.
- `--dry-run` chỉ in ra màn hình, không gửi Telegram — dùng khi thử nghiệm.
- Dữ liệu/token riêng của học viên chỉ nằm trong `.env`/file cục bộ, không commit công khai.
