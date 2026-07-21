---
description: Dựng Bot lệnh trong group Telegram — nhân viên gõ keyword, bot đọc file dữ liệu và trả lời ngay trong nhóm.
---

Bạn đang giúp học viên khóa "50 AI Agents" của Tony Academy dựng **Bot lệnh trong group Telegram**. Chạy qua GÓI Claude Code (không cần API key). Nói tiếng Việt, ngắn gọn, tự làm giúp thao tác.

## Ý tưởng
Nhân viên gõ một keyword trong nhóm (vd `/donmoi`, `/tonkho`) -> bot đọc file CSV tương ứng, lọc dữ liệu và trả lời ngay trong group. Keyword -> hành động khai báo trong `.env` (biến `CMD_<keyword>`).

## Các bước
1. **Copy toàn bộ** `${CLAUDE_PLUGIN_ROOT}/templates/` vào thư mục con của agent. `chmod +x` cho `.sh`.
2. **Kiểm tra `claude` + `claude login`** (dùng gói, chỉ cần khi có lệnh bật `ai:1`). Chưa có thì hướng dẫn đăng nhập.
3. **Chạy thử ngay:** `./run.sh --dry-run /donmoi` rồi `./run.sh --dry-run /tonkho` — xem bot đọc `orders_example.csv` / `stock_example.csv` (Windows: `.\run.ps1 --dry-run /donmoi`). `./run.sh --dry-run /help` để xem danh sách lệnh.
4. **Tạo bot & mời vào nhóm:** trong Telegram nhắn @BotFather -> `/newbot` lấy token. Quan trọng: `/setprivacy` -> **Disable** để bot đọc được tin nhắn nhóm. Mời bot vào nhóm làm việc.
5. **Điền `.env`:** copy `.env.example` -> `.env`, dán `TELEGRAM_BOT_TOKEN`. Không in lại token; không commit `.env`.
6. **Khai báo lệnh:** hỏi học viên muốn những lệnh gì (đọc file nào, lọc cột nào). Mỗi lệnh là một dòng `CMD_<keyword>=<file>.csv | filter:Cột=GiáTrị | title:... | lowstock:1 | ai:1`. Đặt file dữ liệu thật (vd `orders.csv`, `stock.csv`) cạnh `group_bot.py`; chưa có thì bot tự dùng `<ten>_example.csv`.
7. **Chạy nhận lệnh:** `./run.sh poll` đọc tin mới trong nhóm, khớp keyword và trả lời. Muốn tự động: đặt lịch chạy `poll` mỗi 1-2 phút bằng `./schedule_mac.sh` / `.\schedule_win.ps1`.

## Lưu ý
- Bot chỉ trả lời tin khớp keyword đã khai báo (và `/help`), các tin khác im lặng.
- `filter:` khớp kiểu "chứa" và không phân biệt hoa thường. Nhiều `filter:` = lọc chồng.
- `ai:1` nhờ Claude Code viết câu tự nhiên; không có `claude` thì điền `CLAUDE_BIN` vào `.env`.
- Không cần cài thư viện Python, không cần API key nếu dùng gói Claude Code.
