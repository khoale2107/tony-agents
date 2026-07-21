---
description: Dựng Voucher Maker — bot tạo nội dung voucher/ấn phẩm theo template, xuất voucher.html
---

Bạn đang giúp học viên khóa "50 AI Agents" của Tony Academy dựng **Voucher Maker** vào thư mục hiện tại. Chạy qua GÓI Claude Code (không cần API key). Nói tiếng Việt, ngắn gọn, tự làm giúp thao tác.

## Voucher Maker làm gì
Đưa 1 câu mô tả (VD: "Giảm 20% chụp cưới tháng 8"), AI soạn nội dung voucher hoàn chỉnh (tiêu đề, ưu đãi, điều kiện, thời hạn), tự sinh mã voucher, rồi xuất ra `voucher.html` (đơn giản, tự chứa) và in text ra màn hình. Không cần ảnh, không cần Telegram.

## Các bước
1. **Copy toàn bộ file** trong `${CLAUDE_PLUGIN_ROOT}/templates/` vào thư mục con của agent (tạo nếu chưa có). Cấp quyền chạy cho `.sh` (chmod +x) trên macOS/Linux.
2. **Kiểm tra Claude Code:** máy đã có lệnh `claude` và `claude login` chưa (dùng gói). Nếu chưa, hướng dẫn đăng nhập.
3. **Chạy thử ngay:** `cd <thư mục> && ./run.sh --dry-run` (Windows: đổi `./run.sh` -> `.\run.ps1`). Không cần cấu hình gì — nó dùng các yêu cầu mẫu trong `voucher_maker_example.csv`, in nội dung và tạo `voucher.html`. Mở file HTML cho học viên xem.
4. **Tạo 1 voucher theo yêu cầu thật:** `./run.sh "Giảm 20% chụp cưới tháng 8"`. Mở `voucher.html` để xem kết quả.
5. **Chỉnh template thương hiệu** trong `.env`: `BRAND_NAME`, `TEMPLATE_HINT` (giọng văn), `VOUCHER_PREFIX` (tiền tố mã), `VALID_DAYS` (hạn mặc định), `HOTLINE`. Không in lại token; không commit `.env`.
6. **(Tùy chọn) Tạo hàng loạt:** copy `voucher_maker_example.csv` thành `voucher_maker.csv`, sửa cột `yeu_cau` theo chương trình của bạn, rồi chạy `./run.sh --dry-run` (không truyền tham số) để tạo nhiều voucher trong 1 file HTML.
7. **(Tùy chọn) Đặt lịch** nếu muốn tạo định kỳ: hỏi giờ, chạy `./schedule_mac.sh` (Mac) / `.\schedule_win.ps1` (Win). Nhắc: máy phải BẬT + Claude Code còn đăng nhập gói.

## Lưu ý
- Không cần cài thư viện Python, không cần API key (dùng gói).
- Nếu không tìm thấy `claude`, điền `CLAUDE_BIN` vào `.env`.
- `voucher.html` tự chứa (inline CSS), mở bằng trình duyệt bất kỳ hoặc gửi cho khách.
- Mã voucher sinh ngẫu nhiên mỗi lần chạy — muốn cố định thì lưu lại mã sau khi tạo.
