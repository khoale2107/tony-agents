---
description: Dựng A/B Test Tracker — tính CTR/CVR mỗi biến thể creative, chọn winner mỗi nhóm, AI nhận định
---

Bạn đang giúp học viên khóa "50 AI Agents" của Tony Academy dựng **A/B Test Tracker** vào thư mục hiện tại. Chạy qua GÓI Claude Code (không cần API key). Nói tiếng Việt, ngắn gọn, tự làm giúp thao tác.

## Các bước
1. **Copy toàn bộ file** trong `${CLAUDE_PLUGIN_ROOT}/templates/` vào thư mục con của agent (tạo nếu chưa có). Cấp quyền chạy cho `.sh` (chmod +x) trên macOS/Linux.
2. **Kiểm tra Claude Code:** máy đã có lệnh `claude` và đã `claude login` (dùng gói) chưa. Nếu chưa, hướng dẫn đăng nhập.
3. **Chạy thử ngay:** `cd <thư mục> && ./run.sh --dry-run   # xem thử` (Windows: đổi `./run.sh` -> `.\run.ps1`). Nó sẽ tự dùng `ab_example.csv` để in kết quả CTR/CVR + winner + nhận định AI.
4. **Hỏi nguồn dữ liệu.** Xuất báo cáo quảng cáo (Meta Ads/TikTok/GA...) ra CSV có 5 cột: Nhóm, Biến thể, Hiển thị, Click, Chuyển đổi. Lưu file tên `ab.csv` cạnh `ab_tracker.py`. Nếu cột đặt tên khác, chỉnh `COL_*` trong `.env`.
5. **Chọn tiêu chí winner** trong `.env`: `WINNER_METRIC=cvr` (chuyển đổi/click) hoặc `ctr`/`conv_rate`. Đặt `MIN_IMPRESSION` để loại biến thể mẫu quá nhỏ.
6. **Điền Telegram** trong `.env` (token, chat id). Không in lại token; không commit `.env`.
7. **Đặt lịch.** Hỏi giờ, chạy `./schedule_mac.sh` (Mac) / `.\schedule_win.ps1` (Win). Nhắc: máy phải BẬT + Claude Code còn đăng nhập gói.

## Lưu ý
- Không cần cài thư viện Python, không cần API key (dùng gói).
- Nếu không tìm thấy `claude`, điền `CLAUDE_BIN` vào `.env`.
- Dữ liệu/token riêng của học viên chỉ nằm trong `.env`/file cục bộ, không commit công khai.
