---
description: Dựng OCR hoá đơn — Chụp/đưa ảnh hoá đơn, AI đọc và tự ghi sổ (thêm dòng vào so_ke.csv). Dùng gói Cl
---

Bạn đang giúp học viên khóa "50 AI Agents" của Tony Academy dựng **OCR hoá đơn** vào thư mục hiện tại. Chạy qua GÓI Claude Code (không cần API key). Nói tiếng Việt, ngắn gọn, tự làm giúp thao tác.

## Các bước
1. **Copy toàn bộ file** trong `${CLAUDE_PLUGIN_ROOT}/templates/` vào thư mục con của agent (tạo nếu chưa có). Cấp quyền chạy cho `.sh` (chmod +x) trên macOS/Linux.
2. **Kiểm tra Claude Code:** máy đã có lệnh `claude` và `claude login` chưa (dùng gói). Nếu chưa, hướng dẫn đăng nhập.
3. **Chạy thử ngay:** `cd <thư mục> && ./run.sh duong-dan-anh-hoa-don.jpg      # đọc 1 hoá đơn, ghi sổ` (Windows: đổi `./run.sh` -> `.\run.ps1`). Cho học viên xem kết quả.
4. **Không cần nguồn dữ liệu.** Chỉ cần máy đã `claude login`. Cho học viên thử với một ảnh hoá đơn thật của họ; kết quả ghi vào so_ke.csv.

## Lưu ý
- Không cần cài thư viện Python, không cần API key (dùng gói).
- Nếu không tìm thấy `claude`, điền `CLAUDE_BIN` vào `.env`.
- Dữ liệu/token riêng của học viên chỉ nằm trong `.env`/file cục bộ, không commit công khai.
