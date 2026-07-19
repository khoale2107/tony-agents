# CFO Agent — Báo cáo tài chính tự động 7h sáng

Agent này mỗi sáng sẽ: đọc số liệu từ **Google Sheet** của bạn → tính **doanh thu, chi phí, lợi nhuận** → nhờ **AI viết nhận định** → gửi báo cáo qua **Telegram**.

> Bạn nhận được bộ này qua Claude Code. Nếu chưa dựng, mở Claude Code trong thư mục dự án và gõ:
> **`/setup-cfo-agent`** — trợ lý sẽ hỏi thông tin và tự dựng giúp bạn.
> Dưới đây là hướng dẫn làm tay nếu muốn tự chủ động.

## 1. Chuẩn bị (làm 1 lần)

1. **Cài Python 3.10+** (macOS thường có sẵn; Windows tải tại python.org, nhớ tick "Add to PATH").
2. **Trí tuệ AI — dùng GÓI Claude Code của bạn (không tốn thêm tiền):**
   cài Claude Code và đăng nhập gói (`claude login`). Agent sẽ tự gọi `claude` để viết nhận định.
   - Điều kiện: **máy phải BẬT** vào lúc lịch chạy (7h sáng) và Claude Code đã đăng nhập gói.
   - Nếu máy hay tắt/ngủ, hoặc bạn muốn "cắm là chạy" độc lập, xem mục *chế độ API key* trong `.env.example`.
3. **Google Sheet** ghi thu/chi, có các cột: `Ngày`, `Loại` (Doanh thu / Chi phí), `Hạng mục`, `Số tiền`.
   - Chia sẻ: File → Share → *Anyone with the link* (Viewer).
   - Lấy link CSV: `https://docs.google.com/spreadsheets/d/<ID>/export?format=csv&gid=<GID>`
     (ID nằm trong URL của sheet; GID là số ở cuối URL của tab, tab đầu thường `gid=0`).
4. **Telegram**: nhắn `@BotFather` → `/newbot` để lấy **token**; nhắn `@userinfobot` để lấy **chat id** của bạn.

## 2. Cấu hình

Copy `.env.example` thành `.env` rồi điền các giá trị của bạn (key, link sheet, token Telegram).

## 3. Chạy thử

**macOS/Linux:**
```bash
./run.sh --dry-run     # in ra màn hình, chưa gửi Telegram
./run.sh               # gửi báo cáo thật qua Telegram
```
**Windows (PowerShell):**
```powershell
.\run.ps1 --dry-run
.\run.ps1
```
> Chưa điền `GOOGLE_SHEET_CSV_URL`? Agent tự dùng `sample_data.csv` để bạn thấy kết quả ngay.

## 4. Đặt lịch 7h sáng mỗi ngày

**macOS:**
```bash
./schedule_mac.sh          # 7:00 mỗi ngày
./schedule_mac.sh 8 30     # đổi giờ, ví dụ 8:30
./schedule_mac.sh --off    # tắt lịch
```
**Windows (PowerShell):**
```powershell
.\schedule_win.ps1              # 7:00 mỗi ngày
.\schedule_win.ps1 -At 08:30    # đổi giờ
.\schedule_win.ps1 -Off         # tắt lịch
```

## Tùy chỉnh nhanh (trong `.env`)
- `REPORT_PERIOD=day` để báo cáo trong ngày (mặc định `month`).
- `COL_DATE / COL_TYPE / COL_AMOUNT / COL_ITEM` nếu cột trong sheet của bạn đặt tên khác.
- `COMPANY_NAME` tên hiển thị đầu báo cáo.

## Bảo mật
File `.env` chứa key/token của bạn — **không gửi cho ai, không đưa lên mạng.**
