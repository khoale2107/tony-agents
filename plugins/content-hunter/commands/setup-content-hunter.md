---
description: Dựng Content Hunter — quét TikTok/YouTube tìm format viral trong ngách, AI rút hook + cách áp dụng cho ngành của bạn.
---

Bạn đang giúp học viên khóa "50 AI Agents" của Tony Academy dựng **Content Hunter**. Chạy qua GÓI Claude Code. Nói tiếng Việt, ngắn gọn, tự làm giúp thao tác.

## Các bước
1. **Copy toàn bộ** `${CLAUDE_PLUGIN_ROOT}/templates/` vào thư mục con của agent. `chmod +x` cho các file `.sh`.
2. **Chạy thử ngay:** `./run.sh --dry-run` — AI phân tích `videos_example.csv` và in ra format viral + cách áp dụng. Không cần cấu hình gì.
3. **Cấu hình `.env`:** `NGANH_HANG` (để AI gợi ý áp dụng đúng ngành), `COMPANY_NAME`, `TOP_N_PHAN_TICH`, `TOP_N_HIEN`, và Telegram nếu muốn gửi.
4. **Nạp dữ liệu thật:** tạo `videos.csv` (cột `Nền tảng,Tiêu đề,View,Like,Link`) từ bản export TikTok/YouTube. Có `videos.csv` thì tự động dùng thay `videos_example.csv`.
5. **Quét thật để mở rộng nguồn (seam):** copy `collector_example.py` -> `collector.py`, nhờ Claude Code viết bộ thu theo TikTok/YouTube API hoặc công cụ scrape của bạn -> ghi ra `videos.csv`, rồi chạy lại agent.
6. **Đặt lịch** quét định kỳ (vd mỗi sáng): `./schedule_mac.sh 8 0` / `.\schedule_win.ps1 -At 08:00`.

## Lưu ý
- Phần phân tích dùng GÓI Claude Code, KHÔNG cần API key.
- Tôn trọng điều khoản nền tảng khi thu dữ liệu.
- KHÔNG in lại token ra màn hình. KHÔNG commit `.env` / `collector.py`.
