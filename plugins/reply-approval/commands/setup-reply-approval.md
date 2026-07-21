---
description: Dựng Human-in-the-loop — AI soạn trả lời khách, bạn bấm Duyệt/Sửa/Bỏ trên Telegram trước khi gửi.
---

Bạn đang giúp học viên khóa "50 AI Agents" của Tony Academy dựng **Human-in-the-loop (duyệt trả lời)**. Chạy qua GÓI Claude Code (không cần API key). Nói tiếng Việt, ngắn gọn, tự làm giúp thao tác.

## Các bước
1. **Copy toàn bộ** `${CLAUDE_PLUGIN_ROOT}/templates/` vào thư mục con của agent. `chmod +x` cho `.sh`.
2. **Kiểm tra `claude` + `claude login`** (dùng gói). Chưa có thì hướng dẫn đăng nhập.
3. **Chạy thử ngay:** `./run.sh submit --dry-run` — xem AI soạn trả lời từ `queue_example.csv` (Windows: `.\run.ps1`).
4. **Kiến thức trả lời (tuỳ chọn):** copy `knowledge_example.md` -> `knowledge.md`, điền giá/chính sách thật để AI không bịa.
5. **Điền Telegram** trong `.env` (`TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` — nơi bạn nhận và bấm Duyệt/Bỏ). Không in lại token; không commit `.env`.
6. **Nối kênh gửi khách:** để gửi câu đã duyệt cho khách thật, copy `connector_example.py` -> `connector.py` rồi nhờ Claude Code viết `send_message()` cho Zalo/Messenger của học viên.
7. **Quy trình chạy:** `./run.sh submit` (đẩy lên Telegram) rồi `./run.sh poll` (nhận Duyệt/Sửa/Bỏ). Muốn tự động: đặt lịch `poll` vài phút/lần bằng `./schedule_mac.sh` / `.\schedule_win.ps1`.

## Lưu ý
- Muốn SỬA: trên Telegram reply vào tin đó bằng nội dung mới -> bản của bạn sẽ được gửi.
- Không cần cài thư viện Python, không cần API key. Không tìm thấy `claude` thì điền `CLAUDE_BIN` vào `.env`.
