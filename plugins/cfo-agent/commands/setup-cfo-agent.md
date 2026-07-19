---
description: Dựng CFO Agent — báo cáo tài chính 7h sáng qua Telegram, đọc số từ Google Sheet của học viên.
---

Bạn đang giúp học viên khóa "50 AI Agents" của Tony Academy dựng **CFO Agent** vào thư mục hiện tại của họ. Đây là một dịch vụ chạy nền: mỗi sáng đọc số liệu từ Google Sheet, tính doanh thu/chi phí/lợi nhuận, nhờ AI viết nhận định, rồi gửi báo cáo qua Telegram.

Học viên có thể không rành kỹ thuật. Nói tiếng Việt, ngắn gọn, hướng dẫn từng bước, và tự làm giúp mọi thao tác file/lệnh — chỉ hỏi khi cần thông tin bí mật của họ (key, token, link).

## Các bước thực hiện

1. **Sao chép template vào thư mục làm việc của học viên.**
   Nguồn template nằm ở `${CLAUDE_PLUGIN_ROOT}/templates/`. Copy toàn bộ các file sau vào thư mục con `cfo-agent/` trong thư mục hiện tại của người dùng (tạo nếu chưa có):
   `cfo_agent.py`, `.env.example`, `requirements.txt`, `sample_data.csv`, `adapter_custom.example.py`, `run.sh`, `run.ps1`, `schedule_mac.sh`, `schedule_win.ps1`, `README.md`.
   Cấp quyền chạy cho các file `.sh` (chmod +x) nếu đang trên macOS/Linux.

2. **Chạy thử ngay với data mẫu** để học viên thấy kết quả:
   - macOS/Linux: `cd cfo-agent && ./run.sh --dry-run`
   - Windows: `cd cfo-agent; .\run.ps1 --dry-run`
   Cho họ xem báo cáo mẫu in ra (chưa cần key gì).

3. **Trí tuệ AI — mặc định dùng GÓI Claude Code, KHÔNG cần API key.**
   Kiểm tra máy đã có lệnh `claude` và đã đăng nhập gói chưa (`claude` phải chạy được). Nếu chưa đăng nhập, hướng dẫn `claude login`. Giải thích điều kiện: máy phải BẬT lúc lịch chạy + Claude Code đăng nhập gói; phần nhận định sẽ gọi `claude -p` qua gói của họ (không tốn thêm tiền). Chỉ khi học viên chủ động muốn dùng API key (máy hay tắt, muốn chạy độc lập) thì mới điền `ANTHROPIC_API_KEY` và cài `anthropic`.

4. **HỎI NGUỒN DỮ LIỆU** — câu hỏi quan trọng nhất. Hỏi học viên: *"Số liệu thu/chi của bạn đang nằm ở đâu?"* và xử lý theo câu trả lời:

   **a) Google Sheet / Excel / file CSV** (mặc định, dễ nhất) → đặt `SOURCE=gsheet`.
   Hướng dẫn lấy link: Google Sheet → Share → "Anyone with the link" (Viewer); dùng link dạng `.../export?format=csv&gid=...`, điền vào `GOOGLE_SHEET_CSV_URL`. Nếu chưa có sheet, để trống (agent dùng `sample_data.csv`), làm sau. Nếu cột đặt tên khác mặc định (`Ngày/Loại/Số tiền/Hạng mục`), cập nhật `COL_*` cho khớp.

   **b) ERP / phần mềm kế toán** (Odoo, KiotViet, Sapo, Misa, ERP nhà…) → đặt `SOURCE=custom`.
   - Hỏi kỹ: ERP tên gì? Có API không? Cách xác thực (token/tài khoản/API key)? Có link tài liệu API không? Trường nào là ngày / thu-chi / số tiền / hạng mục?
   - Đổi tên `adapter_custom.example.py` thành `adapter_custom.py`, rồi **tự viết hàm `fetch_rows()`** trong đó để gọi API/đọc dữ liệu của ERP đó và trả về đúng hợp đồng (list[dict] có khoá `Ngày/Loại/Hạng mục/Số tiền`). Với Odoo dùng `xmlrpc.client` CHỈ ĐỌC (search_read/read), KHÔNG create/write/unlink.
   - Ghi các thông tin kết nối (token, URL, DB…) vào `.env` (đúng biến mà adapter dùng). Chạy `./run.sh --dry-run` để kiểm tra adapter lấy đúng số trước khi đi tiếp.
   - Nếu ERP không có API mà chỉ xuất được Excel/CSV → quay lại phương án (a): cho họ xuất định kỳ ra Google Sheet.

5. **Thu thập cấu hình còn lại.** Tạo `.env` từ `.env.example`, điền giúp:
   - `TELEGRAM_BOT_TOKEN` — từ @BotFather (`/newbot`).
   - `TELEGRAM_CHAT_ID` — từ @userinfobot, hoặc chat_id của group.
   - `COMPANY_NAME` — tên hiển thị.
   - `REPORT_PERIOD` — `month` (mặc định) hoặc `day`.
   Ghi vào `.env`. **Tuyệt đối không in lại token/key ra màn hình sau khi đã lưu, và không commit `.env` lên git.**

6. **Gửi thử một báo cáo thật** (nếu học viên đã điền đủ Telegram): chạy `./run.sh` (hoặc `.\run.ps1`) và xác nhận họ nhận được tin nhắn. Phần nhận định lần đầu có thể mất ~15-30s vì gọi Claude Code.

7. **Đặt lịch 7h sáng.** Hỏi giờ mong muốn (mặc định 7:00), rồi chạy đúng script theo hệ điều hành:
   - macOS: `./schedule_mac.sh` (hoặc `./schedule_mac.sh <giờ> <phút>`)
   - Windows: `.\schedule_win.ps1` (hoặc `-At HH:MM`)
   Giải thích cách tắt lịch (`--off` / `-Off`). Nhắc lại: lịch chỉ chạy khi máy BẬT và Claude Code còn đăng nhập gói.

8. **Tổng kết** cho học viên: agent nằm ở đâu, sửa số liệu ở nguồn nào (Google Sheet hay ERP), đổi cấu hình ở file `.env` nào, và cách chạy tay để kiểm tra.

## Lưu ý
- Bản mặc định dùng GÓI Claude Code nên KHÔNG cần cài thư viện Python nào, KHÔNG cần API key.
- Nếu thiếu Python, hướng dẫn cài (macOS: có sẵn python3; Windows: python.org, tick "Add to PATH").
- Nếu lịch chạy báo không tìm thấy `claude`, điền `CLAUDE_BIN=<đường dẫn>` vào `.env` (tìm bằng `which claude`).
- Mọi bí mật chỉ nằm trong `.env` của học viên; template không chứa key của ai.
