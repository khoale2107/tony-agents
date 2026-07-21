---
description: Dựng Reply/DM automation cho TikTok/Facebook — phân loại comment/DM và soạn trả lời theo tông từng nền tảng.
---

Bạn đang giúp học viên khóa "50 AI Agents" của Tony Academy dựng **Reply/DM automation cho TikTok/Facebook**. Chạy qua GÓI Claude Code. Nói tiếng Việt, ngắn gọn, tự làm giúp thao tác.

## Các bước
1. **Copy toàn bộ** `${CLAUDE_PLUGIN_ROOT}/templates/` vào thư mục con của agent. `chmod +x` cho `.sh`.
2. **Chạy thử ngay:** `./run.sh --dry-run` — xem AI phân loại + soạn trả lời cho `inbox_example.csv`.
3. **Kiến thức trả lời:** copy `knowledge_example.md` -> `knowledge.md`, điền giá/dịch vụ thật (AI không bịa; thiếu thì mời khách inbox).
4. **Nguồn comment/DM:** tạo `inbox.csv` (cột `Nền tảng,Người dùng,Nội dung`). Lấy từ export TikTok/Facebook hoặc API qua Claude Code.
5. **Trả lời thật:** copy `connector_example.py` -> `connector.py`, nhờ Claude Code viết `reply()` theo API nền tảng (điền `FB_PAGE_TOKEN`/`TIKTOK_TOKEN` trong `.env`). Không in lại token; không commit `.env`/`connector.py`.
6. **Đặt lịch** quét & trả lời định kỳ nếu muốn: `./schedule_mac.sh` / `.\schedule_win.ps1`.

## Lưu ý
- Spam bị bỏ qua tự động. Khi chưa nối API, `--dry-run` cho xem toàn bộ câu trả lời trước.
