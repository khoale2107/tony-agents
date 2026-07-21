---
description: Dựng Competitor Intel — đọc competitor.csv (ad|post của đối thủ), AI tóm tắt động thái + cảnh báo đe dọa/cơ hội, gửi Telegram
---

Bạn đang giúp học viên khóa "50 AI Agents" của Tony Academy dựng **Competitor Intel (Tình báo đối thủ)** vào thư mục hiện tại. Chạy qua GÓI Claude Code (không cần API key). Nói tiếng Việt, ngắn gọn, tự làm giúp thao tác.

## Các bước
1. **Copy toàn bộ file** trong `${CLAUDE_PLUGIN_ROOT}/templates/` vào thư mục con của agent (tạo nếu chưa có). Cấp quyền chạy cho `.sh` (chmod +x) trên macOS/Linux.
2. **Kiểm tra Claude Code:** máy đã có lệnh `claude` và đã `claude login` chưa (dùng gói). Nếu chưa, hướng dẫn đăng nhập.
3. **Chạy thử ngay:** `cd <thư mục> && ./run.sh --dry-run` (Windows: đổi `./run.sh` -> `.\run.ps1`). Agent sẽ dùng `competitor_example.csv` và in bản tóm tắt động thái từng đối thủ + đe dọa/cơ hội ra màn hình.
4. **Hỏi nguồn dữ liệu.** Đặt file thật tên `competitor.csv` cạnh `competitor_intel.py`, đủ 4 cột: `Đối thủ, Loại, Nội dung, Ngày`. Cột `Loại` chỉ nhận `ad` (đối thủ đang chạy quảng cáo) hoặc `post` (bài đăng thường). Nội dung gom từ Meta Ad Library, fanpage, TikTok của đối thủ. Nếu tên cột khác, chỉnh `COL_NAME/COL_TYPE/COL_CONTENT/COL_DATE` trong `.env`. Muốn đổi tên file thì sửa `COMPETITOR_FILE`.
5. **Điền Telegram** trong `.env` (`TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`). Không in lại token; không commit `.env`.
6. **Đặt lịch.** Hỏi tần suất (thường 1-2 lần/tuần, ví dụ sáng thứ Hai 08:00), chạy `./schedule_mac.sh` (Mac) / `.\schedule_win.ps1` (Win). Nhắc: máy phải BẬT + Claude Code còn đăng nhập gói.

## Lưu ý
- Không cần cài thư viện Python, không cần API key (dùng gói).
- `ad` nghĩa là đối thủ đang bỏ tiền chạy — ưu tiên theo dõi. Meta Ad Library (facebook.com/ads/library) là nguồn xem đối thủ chạy ad gì miễn phí.
- Nếu không tìm thấy `claude`, điền `CLAUDE_BIN` vào `.env`.
- Dữ liệu/token riêng của học viên chỉ nằm trong `.env`/file cục bộ, không commit công khai.
