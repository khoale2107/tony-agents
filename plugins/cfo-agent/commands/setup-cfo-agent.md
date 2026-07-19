---
description: Dựng CFO Agent — báo cáo tài chính 7h sáng qua Telegram, đọc số từ Google Sheet của học viên.
---

Bạn đang giúp học viên khóa "50 AI Agents" của Tony Academy dựng **CFO Agent** vào thư mục hiện tại của họ. Đây là một dịch vụ chạy nền: mỗi sáng đọc số liệu từ Google Sheet, tính doanh thu/chi phí/lợi nhuận, nhờ AI viết nhận định, rồi gửi báo cáo qua Telegram.

Học viên có thể không rành kỹ thuật. Nói tiếng Việt, ngắn gọn, hướng dẫn từng bước, và tự làm giúp mọi thao tác file/lệnh — chỉ hỏi khi cần thông tin bí mật của họ (key, token, link).

## Các bước thực hiện

1. **Sao chép template vào thư mục làm việc của học viên.**
   Nguồn template nằm ở `${CLAUDE_PLUGIN_ROOT}/templates/`. Copy toàn bộ các file sau vào thư mục con `cfo-agent/` trong thư mục hiện tại của người dùng (tạo nếu chưa có):
   `cfo_agent.py`, `.env.example`, `requirements.txt`, `sample_data.csv`, `run.sh`, `run.ps1`, `schedule_mac.sh`, `schedule_win.ps1`, `README.md`.
   Cấp quyền chạy cho các file `.sh` (chmod +x) nếu đang trên macOS/Linux.

2. **Chạy thử ngay với data mẫu** để học viên thấy kết quả:
   - macOS/Linux: `cd cfo-agent && ./run.sh --dry-run`
   - Windows: `cd cfo-agent; .\run.ps1 --dry-run`
   Cho họ xem báo cáo mẫu in ra (chưa cần key gì).

3. **Thu thập cấu hình.** Tạo file `.env` từ `.env.example` và điền giúp. Hỏi học viên lần lượt (giải thích chỗ lấy từng thứ):
   - `ANTHROPIC_API_KEY` — key Claude tại console.anthropic.com. (Nếu chưa có, hướng dẫn tạo.)
   - `GOOGLE_SHEET_CSV_URL` — link CSV export của Google Sheet. Hướng dẫn: Share → "Anyone with the link"; link dạng `.../export?format=csv&gid=...`. Nếu họ chưa có sheet, đề nghị tạm để trống (agent dùng sample_data.csv), làm sheet sau.
   - `TELEGRAM_BOT_TOKEN` — từ @BotFather (`/newbot`).
   - `TELEGRAM_CHAT_ID` — từ @userinfobot, hoặc chat_id của group.
   - `COMPANY_NAME` — tên hiển thị.
   - Nếu cột trong sheet của họ đặt tên khác mặc định (`Ngày/Loại/Số tiền/Hạng mục`), cập nhật `COL_*` cho khớp.
   Ghi các giá trị vào `.env`. **Tuyệt đối không in lại token/key ra màn hình sau khi đã lưu, và không commit `.env` lên git.**

4. **Gửi thử một báo cáo thật** (nếu học viên đã điền đủ Telegram): chạy `./run.sh` (hoặc `.\run.ps1`) và xác nhận họ nhận được tin nhắn.

5. **Đặt lịch 7h sáng.** Hỏi giờ mong muốn (mặc định 7:00), rồi chạy đúng script theo hệ điều hành:
   - macOS: `./schedule_mac.sh` (hoặc `./schedule_mac.sh <giờ> <phút>`)
   - Windows: `.\schedule_win.ps1` (hoặc `-At HH:MM`)
   Giải thích cách tắt lịch (`--off` / `-Off`).

6. **Tổng kết** cho học viên: agent nằm ở đâu, sửa số liệu ở Google Sheet nào, đổi cấu hình ở file `.env` nào, và cách chạy tay để kiểm tra.

## Lưu ý
- Nếu thiếu Python, hướng dẫn cài (macOS: có sẵn python3; Windows: python.org, tick "Add to PATH").
- Nếu `run.sh`/`run.ps1` báo lỗi thiếu thư viện, chúng tự tạo `.venv` và cài `anthropic` — chỉ cần chạy lại.
- Mọi bí mật chỉ nằm trong `.env` của học viên; template không chứa key của ai.
