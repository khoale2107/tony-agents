# Tony Agents — Marketplace cho khóa "50 AI Agents"

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

## Dành cho tác giả (Tony) — cấu trúc repo

```
tony-agents/
├── .claude-plugin/marketplace.json   # khai báo marketplace + danh sách plugin
├── .gitignore                        # chặn .env / secret lọt ra ngoài
└── plugins/
    └── cfo-agent/
        ├── .claude-plugin/plugin.json
        ├── commands/setup-cfo-agent.md   # lệnh bootstrap (Claude làm theo)
        ├── skills/cfo-report/SKILL.md     # kỹ năng viết nhận định
        └── templates/                     # app standalone phát cho học viên
            ├── cfo_agent.py, .env.example, requirements.txt, sample_data.csv
            ├── run.sh / run.ps1
            ├── schedule_mac.sh / schedule_win.ps1
            └── README.md
```

**Nguyên tắc:** template KHÔNG chứa key/token của ai. Mỗi học viên tự điền `.env` của họ.
Thêm agent mới = thêm 1 thư mục trong `plugins/` và 1 mục trong `marketplace.json`, theo đúng khuôn CFO Agent.
