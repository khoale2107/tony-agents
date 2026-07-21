---
description: Dựng Zalo blast khách cũ — phân khúc sinh nhật / lâu chưa quay lại, AI soạn tin riêng từng nhóm.
---

Bạn đang giúp học viên khóa "50 AI Agents" của Tony Academy dựng **Zalo blast khách cũ theo phân khúc**. Chạy qua GÓI Claude Code. Nói tiếng Việt, ngắn gọn, tự làm giúp thao tác.

## Các bước
1. **Copy toàn bộ** `${CLAUDE_PLUGIN_ROOT}/templates/` vào thư mục con của agent. `chmod +x` cho `.sh`.
2. **Chạy thử ngay:** `./run.sh --dry-run` — xem AI soạn tin cho từng nhóm từ `customers_example.csv`.
3. **Danh sách khách:** tạo `customers.csv` (cột `Tên,SĐT,Ngày sinh,Lần cuối mua`). Có thể export từ ERP/CRM qua Claude Code.
4. **Cấu hình phân khúc trong `.env`:** `LAPSED_DAYS` (bao nhiêu ngày coi là lâu chưa quay lại, 180 = 6 tháng), `OFFER` (ưu đãi để AI đưa vào tin).
5. **Nối Zalo thật:** copy `connector_example.py` -> `connector.py`, nhờ Claude Code viết `send_message()` theo OA của học viên. Không in lại token; không commit `.env`/`connector.py`.
6. **Đặt lịch chạy sáng mỗi ngày** (bắt sinh nhật hôm nay): `./schedule_mac.sh 8 0` / `.\schedule_win.ps1 -At 08:00`.

## Lưu ý
- Tôn trọng quy định gửi tin của Zalo (khách đã đồng ý nhận). Khi chưa nối, `--dry-run` cho xem trước toàn bộ.
