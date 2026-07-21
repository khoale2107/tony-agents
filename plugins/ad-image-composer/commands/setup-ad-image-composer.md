---
description: Dựng Bot ghép ảnh quảng cáo — AI chọn 4 ảnh đẹp nhất và ghép thành ảnh 1080×1080 (1 main + 3 phụ).
---

Bạn đang giúp học viên khóa "50 AI Agents" của Tony Academy dựng **Bot ghép ảnh quảng cáo**. Phần AI chọn ảnh chạy qua GÓI Claude Code (không cần API key). Nói tiếng Việt, ngắn gọn, tự làm giúp thao tác.

## Các bước
1. **Copy toàn bộ** `${CLAUDE_PLUGIN_ROOT}/templates/` vào thư mục con của agent. `chmod +x` cho `.sh`.
2. **Cài thư viện ảnh Pillow** (agent này cần xử lý ảnh):
   - macOS/Linux: `pip3 install Pillow`
   - Windows: `pip install Pillow`
3. **Kiểm tra `claude` + `claude login`** (dùng gói để AI xem & chọn ảnh).
4. **Chạy thử ngay:** `./run.sh --demo` — tự sinh ảnh mẫu và ghép ra `output/`. Mở file `output/ads_*.png` để xem.
5. **Ghép ảnh thật:**
   - Cả thư mục: `./run.sh /đường-dẫn/thư-mục-ảnh`
   - Hoặc chọn tay: `./run.sh anh1.jpg anh2.jpg anh3.jpg anh4.jpg ...`
   - Bản HD để in: thêm `--hd` (xuất 3240×3240).
6. **Tinh chỉnh** trong `.env` nếu muốn: `ADS_GAP` (khoảng hở), `ADS_WHITE_THRESHOLD` (cắt viền trắng), `POOL_SIZE` (số ảnh đưa AI xem).

## Lưu ý
- Layout: 1 ảnh MAIN dọc cột trái + 3 ảnh phụ cột phải, nền trắng, tự cắt viền + căn khuôn mặt lên trên.
- Không có `claude` hoặc AI lỗi → agent tự chọn dự phòng (4 ảnh ngẫu nhiên, file lớn nhất làm main).
- Ảnh nguồn/kết quả là file cục bộ của học viên, không commit.
