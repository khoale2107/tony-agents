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
| **CSKH Agent** | `/setup-cskh-agent` | Trợ lý trả lời khách hàng theo kiến thức doanh nghiệp. **Test được ngay**, không cần cấu hình. |
| **CFO Agent** | `/setup-cfo-agent` | Báo cáo tài chính 7h sáng qua Telegram: doanh thu, chi phí, lợi nhuận + nhận định AI. Nguồn: Google Sheet hoặc ERP. |
| **Budget Controller** | `/setup-budget-controller` | Cảnh báo ngân sách theo phòng ban (vượt/sắp vượt) + nhận định AI. |
| **Profit Center** | `/setup-profit-center` | Lãi/lỗ theo chi nhánh/cửa hàng, xếp hạng + nhận định AI. |
| **Báo cáo doanh thu tuần** | `/setup-weekly-revenue` | So doanh thu tuần này với tuần trước, cho ban lãnh đạo. |
| **Cảnh báo chi tiêu bất thường** | `/setup-spend-anomaly` | Khoản chi vượt trung bình + hoá đơn nghi trùng. |
| **Báo cáo lead sáng** | `/setup-lead-morning` | Lead mới, khách tồn 3+ ngày, nghi no-show + gợi ý ưu tiên. |
| **OCR hoá đơn** | `/setup-ocr-invoice` | Chụp hoá đơn → AI đọc → tự ghi sổ. |
| **Duyệt chi đa cấp** | `/setup-duyet-chi` | Duyệt chi qua Telegram theo ngưỡng (<5tr/5-20tr/>20tr). |
