# Trợ lý CSKH — trả lời khách hàng bằng AI

Đọc file kiến thức của bạn (giá, dịch vụ, chính sách) và soạn câu trả lời cho khách. **Chỉ trả lời dựa trên kiến thức bạn cung cấp — không bịa.** Câu ngoài phạm vi → lịch sự chuyển tư vấn viên.

> Nhận qua Claude Code? Gõ `/setup-cskh-agent` để được dựng tự động.

## Chạy thử ngay (không cần cấu hình gì)

Điều kiện: máy đã cài **Claude Code** và đã đăng nhập gói (`claude login`). Không cần API key, không cần cài thư viện.

**macOS/Linux:**
```bash
./run.sh "Thuê váy cưới bao nhiêu tiền một ngày?"   # trả lời 1 câu
./run.sh                                            # hỏi-đáp liên tục
```
**Windows (PowerShell):**
```powershell
.\run.ps1 "Thuê váy cưới bao nhiêu tiền một ngày?"
.\run.ps1
```
Lần đầu dùng **kiến thức mẫu** trong `knowledge.example.md` để bạn thấy ngay.

## Dùng kiến thức thật

Đổi tên `knowledge.example.md` → `knowledge.md` rồi thay bằng thông tin của bạn (giá, dịch vụ, chính sách, khuyến mãi, liên hệ). Agent tự ưu tiên `knowledge.md`.

## Tùy chỉnh (tùy chọn, trong `.env`)
- `COMPANY_NAME` — tên doanh nghiệp.
- `TONE` — giọng điệu trả lời.

## Ghi chú
- `knowledge.md` là dữ liệu riêng của bạn — đừng đưa lên nơi công khai.
- Muốn dùng API key thay vì gói: xem hướng dẫn trong `.env.example`.
