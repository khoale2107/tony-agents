# Duyệt chi đa cấp

Duyệt chi đa cấp qua Telegram: định tuyến theo số tiền (<5tr trưởng nhóm, 5-20tr quản lý, >20tr CEO), nút Duyệt/Từ chối, ghi log.

> Nhận qua Claude Code? Gõ `/setup-duyet-chi` để dựng tự động.

## Chạy thử (dùng gói Claude Code, không cần API key)
Điều kiện: đã cài Claude Code + `claude login`.

**macOS/Linux:**
```bash
./run.sh submit "Mua vật tư" 8000000            # gửi yêu cầu duyệt
./run.sh submit "..." 8000000 --dry-run     # xem sẽ gửi cho ai
./run.sh poll                               # nhận quyết định
```
**Windows:** thay `./run.sh` bằng `.\run.ps1`.

## Cấu hình
Sửa file `.env` (copy từ `.env.example`). Điền token Telegram + chat id người duyệt từng cấp.
