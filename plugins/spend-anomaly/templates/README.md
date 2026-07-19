# Cảnh báo chi tiêu bất thường

Phát hiện khoản chi vượt trung bình và hoá đơn nghi trùng, kèm nhận định AI. Gửi Telegram.

> Nhận qua Claude Code? Gõ `/setup-spend-anomaly` để dựng tự động.

## Chạy thử (dùng gói Claude Code, không cần API key)
Điều kiện: đã cài Claude Code + `claude login`.

**macOS/Linux:**
```bash
./run.sh --dry-run
./run.sh
```
**Windows:** thay `./run.sh` bằng `.\run.ps1`.

## Cấu hình
Sửa file `.env` (copy từ `.env.example`). Nguồn dữ liệu: Google Sheet (link CSV) hoặc ERP qua adapter — xem CFO Agent.

## Đặt lịch
`./schedule_mac.sh` (Mac) hoặc `.\schedule_win.ps1` (Win). Máy phải bật lúc chạy.
