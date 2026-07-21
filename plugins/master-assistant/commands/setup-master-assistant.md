---
description: Dựng Trợ lý tổng (router) — hỏi một câu, AI đọc danh mục agent đã cài và chỉ đúng agent/lệnh nên dùng.
---

Bạn đang giúp học viên khóa "50 AI Agents" của Tony Academy dựng **Trợ lý tổng (router)** vào thư mục hiện tại. Đây là công cụ CLI: học viên gõ một câu hỏi, AI đọc danh mục các agent đã cài (agents.csv) rồi chỉ ra nên dùng agent nào, lệnh gì, làm ngay bước nào. Không gửi Telegram — kết quả in thẳng ra màn hình.

Học viên có thể không rành kỹ thuật. Nói tiếng Việt, ngắn gọn, làm giúp mọi thao tác file/lệnh; chỉ hỏi khi cần thông tin của họ.

## Các bước thực hiện

1. **Sao chép template.** Nguồn ở `${CLAUDE_PLUGIN_ROOT}/templates/`. Copy vào thư mục con `master-assistant/` trong thư mục hiện tại (tạo nếu chưa có) các file:
   `master_assistant.py`, `.env.example`, `agents_example.csv`, `run.sh`, `run.ps1`, `schedule_mac.sh`, `schedule_win.ps1`.
   File `finlib.py` dùng chung sẽ được cấp sẵn — không cần tạo. Cấp quyền chạy cho các file `.sh` (`chmod +x`) nếu trên macOS/Linux.

2. **Chạy thử ngay với danh mục mẫu** để học viên thấy kết quả (chưa cần cấu hình gì):
   - macOS/Linux: `cd master-assistant && ./run.sh "sáng nay có lead nào mới không?"`
   - Windows: `cd master-assistant; .\run.ps1 "sáng nay có lead nào mới không?"`
   - Xem danh mục: `./run.sh --list`
   AI sẽ đọc `agents_example.csv` và chỉ nên dùng agent nào.

3. **Trí tuệ AI — mặc định dùng GÓI Claude Code, KHÔNG cần API key.**
   Kiểm tra máy đã có lệnh `claude` và đã đăng nhập gói chưa. Nếu chưa, hướng dẫn `claude login`. Chỉ khi học viên chủ động muốn dùng API key mới điền `ANTHROPIC_API_KEY` vào `.env` và `pip install anthropic`.

4. **Tạo danh mục agent thật.** Đây là bước quan trọng nhất — danh mục càng đúng, trợ lý chỉ càng chuẩn.
   - Tạo file `agents.csv` cùng thư mục (giữ nguyên 3 cột: `Tên agent, Lệnh, Mô tả`).
   - Điền các agent mà học viên ĐÃ cài từ bộ 50 (mỗi agent một dòng). Có thể copy từ `agents_example.csv` rồi bỏ/thêm dòng cho khớp thực tế. Mô tả nên nêu rõ agent đó lo việc gì để AI chọn đúng.
   - Chưa tạo `agents.csv` thì trợ lý tự dùng `agents_example.csv`.

5. **Cấu hình (nếu cần).** Tạo `.env` từ `.env.example`, điền `COMPANY_NAME`. Nếu cột trong `agents.csv` đặt tên khác mặc định thì sửa `COL_NAME/COL_CMD/COL_DESC`. **Không in lại token/key ra màn hình, không commit `.env` lên git.**

6. **Dùng thật.** Hướng dẫn học viên cứ gõ câu hỏi hằng ngày, ví dụ:
   - `./run.sh "cần gửi tin chăm sóc khách cũ qua Zalo"`
   - `./run.sh "muốn báo cáo doanh thu tháng cho sếp"`
   Trợ lý sẽ chỉ đúng agent/lệnh. Đây là công cụ hỏi tay khi cần, không cần đặt lịch (nếu học viên muốn, vẫn có sẵn `schedule_mac.sh/schedule_win.ps1`).

7. **Tổng kết:** trợ lý nằm ở đâu, cập nhật danh mục ở `agents.csv` khi cài thêm agent mới, và cách gõ câu hỏi để tra.

## Lưu ý
- Bản mặc định dùng GÓI Claude Code nên KHÔNG cần cài thư viện Python nào, KHÔNG cần API key.
- Cập nhật `agents.csv` mỗi khi cài thêm agent để trợ lý luôn chỉ đúng.
- Nếu lịch/terminal báo không tìm thấy `claude`, điền `CLAUDE_BIN=<đường dẫn>` (tìm bằng `which claude`) vào `.env`.
