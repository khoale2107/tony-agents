---
description: Dựng Giám sát nhân viên tư vấn — chấm phản hồi chậm, khách bị bỏ sót, kèm nhận định AI, gửi Telegram.
---

Bạn đang giúp học viên khóa "50 AI Agents" của Tony Academy dựng **Giám sát nhân viên tư vấn**. Chạy qua GÓI Claude Code (không cần API key). Nói tiếng Việt, ngắn gọn, tự làm giúp thao tác.

## Các bước
1. **Copy toàn bộ** `${CLAUDE_PLUGIN_ROOT}/templates/` vào thư mục con của agent. `chmod +x` cho `.sh`.
2. **Kiểm tra `claude` + `claude login`** (dùng gói).
3. **Chạy thử ngay:** `./run.sh --dry-run` — xem báo cáo từ `sample_data.csv` (ai trả lời chậm, khách nào bị bỏ sót).
4. **Hỏi nguồn dữ liệu log chat:** Google Sheet (`SOURCE=gsheet`, `GOOGLE_SHEET_CSV_URL`) hay ERP/CRM (`SOURCE=custom`, viết `adapter_custom.py`). Chỉnh `COL_IN/COL_OUT/COL_STAFF/COL_CUST` cho khớp cột. Đặt `SLA_MINUTES` (mốc coi là chậm).
5. **Điền Telegram** trong `.env`. Không in lại token; không commit `.env`.
6. **Đặt lịch** (ví dụ cuối mỗi ca): `./schedule_mac.sh 18 0` / `.\schedule_win.ps1 -At 18:00`. Nhắc: máy phải BẬT + Claude còn đăng nhập gói.

## Lưu ý
- Không cần cài thư viện Python, không cần API key. Không tìm thấy `claude` thì điền `CLAUDE_BIN`.
