---
description: Dựng Ads Manager qua chat — bật/tắt campaign & đổi ngân sách bằng lệnh Telegram, áp lên nền tảng qua connector.
---

Bạn đang giúp học viên khóa "50 AI Agents" của Tony Academy dựng **Ads Manager qua chat**. Chạy qua GÓI Claude Code (không cần API key). Nói tiếng Việt, ngắn gọn, tự làm giúp thao tác.

## Ý tưởng
Marketer gõ lệnh trong Telegram để điều khiển quảng cáo mà không cần vào trình quản lý:
- `tat <campaign>` — tắt campaign
- `bat <campaign>` — bật campaign
- `nsach <campaign> <số>` — đổi ngân sách/ngày (VND)

Bot đọc lệnh mới, áp lên nền tảng qua `connector.py`, ghi nhật ký `actions.csv`, và trả lời ngay trong chat. Câu nói tự nhiên ("tắt chiến dịch mùa cưới giúp") được Claude Code diễn giải thành lệnh.

## Các bước
1. **Copy toàn bộ** `${CLAUDE_PLUGIN_ROOT}/templates/` vào thư mục con của agent. `chmod +x` cho các file `.sh`.
2. **Kiểm tra `claude` + `claude login`** (dùng GÓI để diễn giải câu tự nhiên). Chưa có thì hướng dẫn đăng nhập, hoặc điền `CLAUDE_BIN` vào `.env`.
3. **Chạy thử ngay (không cần cấu hình gì):**
   - `./run.sh --dry-run tat "Mùa Cưới 2026"`
   - `./run.sh --dry-run nsach "Combo Chụp Ảnh Cưới" 800000`
   - Windows: `.\run.ps1 --dry-run bat "Ưu Đãi Tháng 7"`
   Bot đọc `campaigns_example.csv`, in ra lệnh sẽ áp (chưa gửi, chưa ghi log).
4. **Tạo bot & lấy token:** nhắn @BotFather -> `/newbot`. Nếu dùng trong nhóm: `/setprivacy` -> **Disable** để bot đọc được tin nhóm; rồi mời bot vào nhóm marketing.
5. **Điền `.env`:** copy `.env.example` -> `.env`, dán `TELEGRAM_BOT_TOKEN`. Không in lại token; không commit `.env`.
6. **Danh sách campaign thật:** tạo `campaigns.csv` cạnh `ads_manager.py` (cột `Campaign,TrangThai,NganSach,NenTang`). Chưa có thì bot tự dùng `campaigns_example.csv` để chạy thử.
7. **Nối nền tảng thật (bắt buộc để áp lệnh):** copy `connector_example.py` -> `connector.py`, rồi nhờ Claude Code viết hàm `apply_action(action, campaign, value)` cho Ads API của bạn (Facebook Marketing API / Google Ads / TikTok Ads). Chưa cấu hình thì bot vẫn ghi log và báo "connector chưa cấu hình".
8. **Chạy nhận lệnh:** `./run.sh poll` đọc lệnh mới, áp và trả lời. Muốn tự động: đặt lịch chạy `poll` mỗi 1–2 phút bằng `./schedule_mac.sh` / `.\schedule_win.ps1`.

## Lưu ý
- Bot chỉ phản hồi tin khớp lệnh ads (`tat/bat/nsach` hoặc câu tự nhiên tương đương); tin khác im lặng.
- Tên campaign khớp kiểu "chứa", bỏ dấu, không phân biệt hoa thường — gõ gần đúng vẫn nhận.
- Mọi lệnh áp thật được ghi vào `actions.csv` (thời gian, lệnh, campaign, giá trị, kết quả) để đối soát.
- Không cần cài thư viện Python; không cần API key nếu dùng gói Claude Code.
- Không in lại token ra màn hình, không commit `.env` và `connector.py` (chứa khoá nền tảng).
