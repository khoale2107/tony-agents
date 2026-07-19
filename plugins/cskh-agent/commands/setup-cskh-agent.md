---
description: Dựng Trợ lý CSKH — soạn câu trả lời khách hàng dựa trên kiến thức doanh nghiệp. Test được ngay, không cần cấu hình.
---

Bạn đang giúp học viên khóa "50 AI Agents" của Tony Academy dựng **Trợ lý CSKH** vào thư mục hiện tại. Agent này đọc file kiến thức (giá/dịch vụ/chính sách) và soạn câu trả lời cho khách, chạy qua GÓI Claude Code (không cần API key). Nói tiếng Việt, ngắn gọn.

## Các bước

1. **Sao chép template.** Từ `${CLAUDE_PLUGIN_ROOT}/templates/`, copy các file sau vào thư mục con `cskh-agent/` (tạo nếu chưa có):
   `cskh.py`, `knowledge.example.md`, `.env.example`, `run.sh`, `run.ps1`, `README.md`.
   Cấp quyền chạy cho `run.sh` (chmod +x) nếu trên macOS/Linux.

2. **Chạy thử NGAY với kiến thức mẫu** — cho học viên thấy kết quả tức thì:
   - macOS/Linux: `cd cskh-agent && ./run.sh "Thuê váy cưới bao nhiêu tiền một ngày?"`
   - Windows: `cd cskh-agent; .\run.ps1 "Thuê váy cưới bao nhiêu tiền một ngày?"`
   Kiểm tra: máy đã cài Claude Code + đã `claude login` (dùng gói). Nếu chưa, hướng dẫn đăng nhập.

3. **Thay kiến thức thật.** Mở `knowledge.example.md`, giải thích cấu trúc (dịch vụ, bảng giá, chính sách, khuyến mãi, liên hệ). Hỏi thông tin thật của học viên và giúp họ tạo `knowledge.md` (đổi tên/soạn mới) với dữ liệu của họ. Agent tự ưu tiên `knowledge.md` khi có.

4. **(Tùy chọn) Chỉnh giọng điệu / tên doanh nghiệp.** Nếu muốn khác mặc định, tạo `.env` từ `.env.example` và sửa `COMPANY_NAME`, `TONE`.

5. **Chạy lại với kiến thức thật** và thử vài câu hỏi khách hay hỏi. Cho học viên thấy: câu trong kiến thức → trả lời đúng; câu ngoài kiến thức → chuyển tư vấn viên, không bịa.

6. **Gợi ý mở rộng (nếu học viên muốn):** cắm trợ lý này vào Zalo/Messenger/website để trả lời tự động; hoặc để nhân viên dùng như "máy gợi ý câu trả lời". Đây là hướng nâng cấp, không bắt buộc trong buổi setup.

## Lưu ý
- KHÔNG cần cài thư viện Python, KHÔNG cần API key (dùng gói).
- Nếu báo không tìm thấy `claude`: kiểm tra `claude login`, hoặc điền `CLAUDE_BIN` vào `.env`.
- `knowledge.md` là dữ liệu riêng của học viên — không commit lên nơi công khai.
