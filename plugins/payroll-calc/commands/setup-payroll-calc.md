---
description: Dựng Payroll Calc — Tính lương theo sản phẩm/ca/show từ work.csv, tổng quỹ lương, AI tóm tắt, gửi Telegram
---

Bạn đang giúp học viên khóa "50 AI Agents" của Tony Academy dựng **Payroll Calc** vào thư mục hiện tại. Chạy qua GÓI Claude Code (không cần API key). Nói tiếng Việt, ngắn gọn, tự làm giúp thao tác.

## Các bước
1. **Copy toàn bộ file** trong `${CLAUDE_PLUGIN_ROOT}/templates/` vào thư mục con của agent (tạo nếu chưa có). Cấp quyền chạy cho `.sh` (chmod +x) trên macOS/Linux.
2. **Kiểm tra Claude Code:** máy đã có lệnh `claude` và đã `claude login` chưa (dùng gói). Nếu chưa, hướng dẫn đăng nhập.
3. **Chạy thử ngay:** `cd <thư mục> && ./run.sh --dry-run   # xem bảng lương mẫu` (Windows: đổi `./run.sh` -> `.\run.ps1`). Lúc này agent tự dùng `work_example.csv`, cho học viên xem kết quả.
4. **Đưa dữ liệu thật.** Tạo `work.csv` với 4 cột: `Nhân viên, Loại, Số lượng, Đơn giá`. Cột `Loại` nhận `sản phẩm | ca | show`. Nếu cột đặt tên khác, sửa các biến `COL_*` trong `.env`. Chưa có file thật thì cứ để agent chạy với `work_example.csv`.
5. **Điền cấu hình + Telegram** trong `.env` (`COMPANY_NAME`, `PERIOD`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`). Không in lại token; không commit `.env`.
6. **Đặt lịch.** Hỏi giờ chốt lương (ví dụ cuối tháng), chạy `./schedule_mac.sh` (Mac) / `.\schedule_win.ps1` (Win). Nhắc: máy phải BẬT + Claude Code còn đăng nhập gói.

## Lưu ý
- Không cần cài thư viện Python, không cần API key (dùng gói).
- Nếu không tìm thấy `claude`, điền `CLAUDE_BIN` vào `.env`.
- Đơn giá có thể ghi `15.000` hay `15000` đều đọc được. Mỗi nhân viên nhiều dòng (nhiều loại) sẽ được cộng gộp.
- Dữ liệu/token riêng của học viên chỉ nằm trong `.env`/file cục bộ, không commit công khai.
