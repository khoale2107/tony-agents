---
description: Dựng Ads Reporter — đọc ads.csv (Meta/TikTok), tính CPM/CPC/CPL từng kênh & chiến dịch, AI nhận định nên tăng/tắt, gửi Telegram mỗi sáng
---

Bạn đang giúp học viên khóa "50 AI Agents" của Tony Academy dựng **Ads Reporter (Meta/TikTok)** vào thư mục hiện tại. Chạy qua GÓI Claude Code (không cần API key). Nói tiếng Việt, ngắn gọn, tự làm giúp thao tác.

## Các bước
1. **Copy toàn bộ file** trong `${CLAUDE_PLUGIN_ROOT}/templates/` vào thư mục con của agent (tạo nếu chưa có). Cấp quyền chạy cho `.sh` (chmod +x) trên macOS/Linux.
2. **Kiểm tra Claude Code:** máy đã có lệnh `claude` và đã `claude login` chưa (dùng gói). Nếu chưa, hướng dẫn đăng nhập.
3. **Chạy thử ngay:** `cd <thư mục> && ./run.sh --dry-run` (Windows: đổi `./run.sh` -> `.\run.ps1`). Agent sẽ dùng `ads_example.csv` và in báo cáo theo kênh + chiến dịch (CPM/CPC/CPL) kèm nhận định AI ra màn hình.
4. **Hỏi nguồn dữ liệu.** Đặt file thật tên `ads.csv` cạnh `ads_reporter.py`, đủ 7 cột: `Ngày, Kênh, Chiến dịch, Chi phí, Hiển thị, Click, Lead`. Thường export từ Meta Ads Manager / TikTok Ads (gộp các dòng của ngày cần báo cáo). Nếu tên cột khác, chỉnh `COL_CHANNEL/COL_CAMPAIGN/COL_COST/COL_IMPR/COL_CLICK/COL_LEAD` trong `.env`. Muốn dùng tên file khác thì đổi `ADS_FILE`.
5. **Điền Telegram** trong `.env` (`TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`). Không in lại token; không commit `.env`.
6. **Đặt lịch.** Hỏi giờ chạy (thường sáng sớm, ví dụ 08:00 mỗi ngày để xem số qua đêm), chạy `./schedule_mac.sh` (Mac) / `.\schedule_win.ps1` (Win). Nhắc: máy phải BẬT + Claude Code còn đăng nhập gói.

## Lưu ý
- Không cần cài thư viện Python, không cần API key (dùng gói).
- CPM = chi/1000 hiển thị, CPC = chi/click, CPL = chi/lead. CPL càng thấp càng tốt; chiến dịch 0 lead sẽ hiện CPL "— (0 lead)".
- Nếu không tìm thấy `claude`, điền `CLAUDE_BIN` vào `.env`.
- Dữ liệu/token riêng của học viên chỉ nằm trong `.env`/file cục bộ, không commit công khai.
