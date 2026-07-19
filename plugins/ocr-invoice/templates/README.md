# OCR hoá đơn

Chụp/đưa ảnh hoá đơn, AI đọc và tự ghi sổ (thêm dòng vào so_ke.csv). Dùng gói Claude Code đọc ảnh, không cần API key.

> Nhận qua Claude Code? Gõ `/setup-ocr-invoice` để dựng tự động.

## Chạy thử (dùng gói Claude Code, không cần API key)
Điều kiện: đã cài Claude Code + `claude login`.

**macOS/Linux:**
```bash
./run.sh duong-dan-anh-hoa-don.jpg      # đọc 1 hoá đơn, ghi sổ
./run.sh anh1.jpg anh2.png            # nhiều ảnh
```
**Windows:** thay `./run.sh` bằng `.\run.ps1`.

## Cấu hình
Sửa file `.env` (copy từ `.env.example`). OCR đọc ảnh trực tiếp, không cần nguồn dữ liệu.
