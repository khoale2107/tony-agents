# Tony Agents
Đây là **marketplace plugin của Claude Code**. Học viên cài cả bộ agent bằng vài lệnh, rồi mỗi người tự chạy trên máy mình (macOS hoặc Windows) với tài khoản Claude của chính họ.

## Dành cho học viên — cách cài

Mở **Claude Code** ở bất kỳ thư mục dự án nào, rồi gõ:

```
/plugin marketplace add khoale2107/tony-agents
/plugin install cfo-agent@tony-agents
```

> Cài từ máy (thử tại chỗ, không cần mạng): `/plugin marketplace add /Users/tonyacademy/tony-agents`

Sau khi cài, gõ lệnh của agent để nó tự dựng cho bạn — ví dụ:

```
/setup-cfo-agent
```

Trợ lý sẽ hỏi thông tin (Google Sheet, key Claude, Telegram) và dựng một dịch vụ báo cáo chạy 7h sáng mỗi ngày.

## Các agent trong bộ

| Agent | Lệnh | Mô tả |
|-------|------|-------|
| **CFO Agent** | `/setup-cfo-agent` | Báo cáo tài chính 7h sáng qua Telegram: doanh thu, chi phí, lợi nhuận + nhận định AI. Nguồn: Google Sheet. |
| _(sắp có)_ Budget Controller | — | Cảnh báo vượt ngân sách theo phòng ban. |
| _(sắp có)_ Duyệt chi Telegram | — | Duyệt chi đa cấp theo ngưỡng qua Telegram. |
