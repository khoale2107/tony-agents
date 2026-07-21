---
description: Dựng RAG kiến thức công ty — bot trả lời theo bảng giá/chính sách/quy trình riêng, có trích nguồn. Test được ngay.
---

Bạn đang giúp học viên khóa "50 AI Agents" của Tony Academy dựng **RAG kiến thức công ty**. Chạy qua GÓI Claude Code (không cần API key). Nói tiếng Việt, ngắn gọn, tự làm giúp thao tác.

## Các bước
1. **Copy toàn bộ** `${CLAUDE_PLUGIN_ROOT}/templates/` vào thư mục con của agent. `chmod +x` cho `.sh`.
2. **Kiểm tra `claude` + `claude login`** (dùng gói).
3. **Chạy thử ngay (không cần cấu hình):** `./run.sh "gói chụp phóng sự cưới bao nhiêu tiền?"` — bot trả lời từ tài liệu mẫu trong `knowledge_example/`.
4. **Nạp tài liệu thật:** tạo thư mục `knowledge/` cạnh `rag_knowledge.py`, bỏ vào các file `.md`/`.txt` (bảng giá, chính sách, quy trình...). Bot tự đọc hết. Đặt `KNOWLEDGE_DIR` trong `.env` nếu để thư mục khác.
5. **Hỏi tương tác:** `./run.sh` rồi gõ nhiều câu. Tài liệu lớn thì tăng `MAX_CONTEXT_CHARS` trong `.env`.

## Lưu ý
- Bot CHỈ trả lời theo tài liệu, không bịa; thiếu thông tin thì nói chưa có. Cuối câu có (Nguồn: <tên file>).
- Không cần API key. Không tìm thấy `claude` thì điền `CLAUDE_BIN` vào `.env`.
- `knowledge/` (tài liệu thật) không nên commit công khai.
