# Tony Agents

**Marketplace plugin của Claude Code** cho học viên khóa "50 AI Agents" của Tony Academy. Cài một lần, mỗi agent tự dựng thành một dịch vụ chạy trên máy bạn (macOS/Windows) bằng chính tài khoản Claude của bạn. Toàn bộ agent gọi AI **qua gói Claude Code — không cần API key**.

## Bước 1 — Cài marketplace (làm một lần)

Mở **Claude Code** ở bất kỳ thư mục nào rồi gõ:

```
/plugin marketplace add khoale2107/tony-agents
```

> Đã cài trước đó mà chưa thấy agent mới? Gõ `/plugin marketplace update tony-agents` để cập nhật danh sách.

## Bước 2 — Cài & dựng từng agent

Với mỗi agent bên dưới: gõ lệnh **cài** rồi lệnh **dựng** (`/setup-...`). Trợ lý sẽ tự copy file, chạy thử, hỏi nguồn dữ liệu / Telegram (nếu cần) và đặt lịch giúp bạn.

Yêu cầu chung: máy đã cài `claude` và đã `claude login` (dùng gói). Không cần cài thư viện Python, không cần API key.

### 1. cfo-agent

CFO Agent — dựng một dịch vụ báo cáo tài chính tự động chạy 7h sáng mỗi ngày, đọc số từ Google Sheet, tính doanh thu/chi phí/lợi nhuận, nhờ AI viết nhận định, rồi gửi qua Telegram.

```
/plugin install cfo-agent@tony-agents
/setup-cfo-agent
```

- Chạy thử: `./run.sh --dry-run`
- Điền dữ liệu thật + `.env` khi được hỏi (không commit `.env`).
- Đặt lịch tự động: `./schedule_mac.sh` (Mac) / `.\schedule_win.ps1` (Windows).

### 2. cskh-agent

Trợ lý CSKH — soạn câu trả lời khách hàng dựa trên kiến thức doanh nghiệp (giá, dịch vụ, chính sách). Chạy qua gói Claude Code, test được ngay không cần cấu hình.

```
/plugin install cskh-agent@tony-agents
/setup-cskh-agent
```

- Chạy thử ngay: ./run.sh "Thuê váy cưới bao nhiêu tiền một ngày?"     # trả lời 1 câu · ./run.sh                                              # chế độ hỏi-đáp liên tục
- Điền dữ liệu thật + `.env` khi được hỏi (không commit `.env`).

### 3. budget-controller

Cảnh báo ngân sách theo phòng ban: so chi thực tế với ngân sách tháng, cảnh báo vượt/sắp vượt kèm nhận định AI. Gửi Telegram.

```
/plugin install budget-controller@tony-agents
/setup-budget-controller
```

- Chạy thử ngay: ./run.sh --dry-run   in ra màn hình (không gửi) · ./run.sh             gửi báo cáo Telegram
- Điền dữ liệu thật + `.env` khi được hỏi (không commit `.env`).
- Đặt lịch tự động: `./schedule_mac.sh` (Mac) / `.\schedule_win.ps1` (Windows).

### 4. duyet-chi

Duyệt chi đa cấp qua Telegram: định tuyến theo số tiền (<5tr trưởng nhóm, 5-20tr quản lý, >20tr CEO), nút Duyệt/Từ chối, ghi log.

```
/plugin install duyet-chi@tony-agents
/setup-duyet-chi
```

- Chạy thử ngay: ./run.sh submit "Mua vật tư tiệc cưới" 8000000     gửi 1 yêu cầu duyệt · ./run.sh submit "..." 8000000 --dry-run            chỉ xem sẽ gửi cho ai · ./run.sh poll                                       nhận quyết định Duyệt/Từ chối
- Điền dữ liệu thật + `.env` khi được hỏi (không commit `.env`).
- Đặt lịch tự động: `./schedule_mac.sh` (Mac) / `.\schedule_win.ps1` (Windows).

### 5. profit-center

Lãi/lỗ theo chi nhánh/cửa hàng: tính doanh thu-chi phí-lợi nhuận từng chi nhánh, xếp hạng, nhận định AI. Gửi Telegram.

```
/plugin install profit-center@tony-agents
/setup-profit-center
```

- Chạy thử ngay: ./run.sh --dry-run   in ra màn hình · ./run.sh             gửi Telegram
- Điền dữ liệu thật + `.env` khi được hỏi (không commit `.env`).
- Đặt lịch tự động: `./schedule_mac.sh` (Mac) / `.\schedule_win.ps1` (Windows).

### 6. lead-morning

Điểm danh khách tiềm năng mỗi sáng: lead mới, khách 3+ ngày chưa xử lý, nghi no-show, kèm gợi ý ưu tiên từ AI. Gửi Telegram.

```
/plugin install lead-morning@tony-agents
/setup-lead-morning
```

- Chạy thử ngay: ./run.sh --dry-run   |   ./run.sh
- Điền dữ liệu thật + `.env` khi được hỏi (không commit `.env`).
- Đặt lịch tự động: `./schedule_mac.sh` (Mac) / `.\schedule_win.ps1` (Windows).

### 7. ocr-invoice

Chụp/đưa ảnh hoá đơn, AI đọc và tự ghi sổ (thêm dòng vào so_ke.csv). Dùng gói Claude Code đọc ảnh, không cần API key.

```
/plugin install ocr-invoice@tony-agents
/setup-ocr-invoice
```

- Chạy thử ngay: ./run.sh duong-dan-anh-hoa-don.jpg · ./run.sh anh1.jpg anh2.png ...        (nhiều ảnh một lượt)
- Điền dữ liệu thật + `.env` khi được hỏi (không commit `.env`).

### 8. spend-anomaly

Phát hiện khoản chi vượt trung bình và hoá đơn nghi trùng, kèm nhận định AI. Gửi Telegram.

```
/plugin install spend-anomaly@tony-agents
/setup-spend-anomaly
```

- Chạy thử ngay: ./run.sh --dry-run   |   ./run.sh
- Điền dữ liệu thật + `.env` khi được hỏi (không commit `.env`).
- Đặt lịch tự động: `./schedule_mac.sh` (Mac) / `.\schedule_win.ps1` (Windows).

### 9. weekly-revenue

Báo cáo doanh thu tuần cho ban lãnh đạo: so 7 ngày gần nhất với tuần trước, bóc theo ngày, nhận định AI. Gửi Telegram.

```
/plugin install weekly-revenue@tony-agents
/setup-weekly-revenue
```

- Chạy thử ngay: ./run.sh --dry-run   in ra màn hình · ./run.sh             gửi Telegram
- Điền dữ liệu thật + `.env` khi được hỏi (không commit `.env`).
- Đặt lịch tự động: `./schedule_mac.sh` (Mac) / `.\schedule_win.ps1` (Windows).

### 10. reply-approval

Human-in-the-loop: AI soạn câu trả lời khách, đẩy qua Telegram để bạn bấm Duyệt/Sửa/Bỏ trước khi gửi.

```
/plugin install reply-approval@tony-agents
/setup-reply-approval
```

- Chạy thử ngay: ./run.sh submit --dry-run    xem các câu AI soạn (không gửi Telegram) · ./run.sh submit              soạn + đẩy lên Telegram chờ bạn bấm · ./run.sh poll                nhận quyết định, câu đã Duyệt sẽ gửi cho khách (qua connector seam)
- Điền dữ liệu thật + `.env` khi được hỏi (không commit `.env`).
- Đặt lịch tự động: `./schedule_mac.sh` (Mac) / `.\schedule_win.ps1` (Windows).

### 11. rag-knowledge

RAG kiến thức công ty: bot học bảng giá/chính sách/quy trình từ thư mục tài liệu, trả lời có trích nguồn. Test được ngay.

```
/plugin install rag-knowledge@tony-agents
/setup-rag-knowledge
```

- Chạy thử ngay: ./run.sh "gói chụp phóng sự cưới bao nhiêu tiền?" · ./run.sh                       # hỏi tương tác nhiều câu
- Điền dữ liệu thật + `.env` khi được hỏi (không commit `.env`).

### 12. cskh-monitor

Giám sát nhân viên tư vấn: chấm điểm phản hồi chậm, khách bị bỏ sót, kèm nhận định AI. Gửi Telegram.

```
/plugin install cskh-monitor@tony-agents
/setup-cskh-monitor
```

- Chạy thử ngay: ./run.sh --dry-run   |   ./run.sh
- Điền dữ liệu thật + `.env` khi được hỏi (không commit `.env`).
- Đặt lịch tự động: `./schedule_mac.sh` (Mac) / `.\schedule_win.ps1` (Windows).

### 13. zalo-zns

Zalo ZNS: xác nhận đơn, nhắc lịch hẹn, nhắc thanh toán theo mẫu. Soạn nội dung tự động, gửi qua connector Zalo (seam).

```
/plugin install zalo-zns@tony-agents
/setup-zalo-zns
```

- Chạy thử ngay: ./run.sh --dry-run   |   ./run.sh
- Điền dữ liệu thật + `.env` khi được hỏi (không commit `.env`).

### 14. zalo-blast

Zalo blast khách cũ theo phân khúc: sinh nhật, 6 tháng chưa quay lại... AI soạn tin riêng từng nhóm. Gửi qua connector (seam).

```
/plugin install zalo-blast@tony-agents
/setup-zalo-blast
```

- Chạy thử ngay: ./run.sh --dry-run   |   ./run.sh
- Điền dữ liệu thật + `.env` khi được hỏi (không commit `.env`).

### 15. survey-auto

Survey tự động sau dịch vụ: gửi khảo sát cho khách vừa xong dịch vụ và tổng hợp phản hồi bằng AI. Gửi Telegram.

```
/plugin install survey-auto@tony-agents
/setup-survey-auto
```

- Chạy thử ngay: ./run.sh send --dry-run · ./run.sh summarize --dry-run   |   ./run.sh summarize
- Điền dữ liệu thật + `.env` khi được hỏi (không commit `.env`).
- Đặt lịch tự động: `./schedule_mac.sh` (Mac) / `.\schedule_win.ps1` (Windows).

### 16. bot-booking

Bot booking: đọc tin nhắn khách, trích nhu cầu, kiểm tra lịch trống và soạn báo giá + xác nhận đặt lịch nhanh. Test được ngay.

```
/plugin install bot-booking@tony-agents
/setup-bot-booking
```

- Chạy thử ngay: ./run.sh "cho mình hỏi chụp cưới thứ 7 tuần này còn trống không, giá sao?"
- Điền dữ liệu thật + `.env` khi được hỏi (không commit `.env`).

### 17. social-dm

Reply/DM automation cho TikTok/Facebook: phân loại comment/DM và soạn câu trả lời theo tông từng nền tảng. Gửi qua connector (seam).

```
/plugin install social-dm@tony-agents
/setup-social-dm
```

- Chạy thử ngay: ./run.sh --dry-run   |   ./run.sh
- Điền dữ liệu thật + `.env` khi được hỏi (không commit `.env`).

### 18. lead-hunter

Lead Hunter: quét bài/bình luận từ group, fanpage (bản export), AI chấm điểm khách tiềm năng và xếp hạng. Gửi Telegram top khách.

```
/plugin install lead-hunter@tony-agents
/setup-lead-hunter
```

- Chạy thử ngay: ./run.sh --dry-run   |   ./run.sh
- Điền dữ liệu thật + `.env` khi được hỏi (không commit `.env`).
- Đặt lịch tự động: `./schedule_mac.sh` (Mac) / `.\schedule_win.ps1` (Windows).

### 19. order-pipeline

Quản lý đơn hàng đa bước qua các khâu NHẬN → XỬ LÝ → QC → TẠO ĐƠN → XONG: xem bảng theo khâu kèm AI tóm tắt tình hình, chuyển đơn sang khâu kế và ghi lại orders.csv. Báo Telegram.

```
/plugin install order-pipeline@tony-agents
/setup-order-pipeline
```

- Chạy thử ngay: ./run.sh list                  in bảng đơn theo khâu + AI tóm tắt (gửi Telegram) · ./run.sh list --dry-run        chỉ in ra màn hình, không gửi · ./run.sh advance DH001         chuyển đơn DH001 sang khâu kế, ghi lại orders.csv + báo Telegram · ./run.sh advance DH001 --dry-run   xem thử, không ghi file, không gửi
- Điền dữ liệu thật + `.env` khi được hỏi (không commit `.env`).
- Đặt lịch tự động: `./schedule_mac.sh` (Mac) / `.\schedule_win.ps1` (Windows).

### 20. group-command-bot

Bot lệnh trong group Telegram: nhân viên gõ keyword (vd /donmoi, /tonkho), bot đọc file CSV, lọc dữ liệu và trả lời ngay trong nhóm.

```
/plugin install group-command-bot@tony-agents
/setup-group-command-bot
```

- Chạy thử ngay: ./run.sh --dry-run /donmoi   mô phỏng 1 lệnh, in kết quả ra màn hình (không gửi Telegram) · ./run.sh --dry-run /tonkho   thử lệnh khác · ./run.sh poll                đọc getUpdates, khớp keyword, trả lời trong group · ./run.sh help                liệt kê các lệnh đang cấu hình
- Điền dữ liệu thật + `.env` khi được hỏi (không commit `.env`).
- Đặt lịch tự động: `./schedule_mac.sh` (Mac) / `.\schedule_win.ps1` (Windows).

### 21. order-status

Đọc orders.csv, đếm đơn ở mỗi khâu và tra chi tiết từng đơn; gửi Telegram tổng quan.

```
/plugin install order-status@tony-agents
/setup-order-status
```

- Chạy thử ngay: ./run.sh --dry-run     -> in bảng: mỗi khâu bao nhiêu đơn + liệt kê mã (không gửi) · ./run.sh <mã đơn>      -> in chi tiết 1 đơn + khâu hiện tại · ./run.sh               -> gửi Telegram tổng quan (chạy thật)
- Điền dữ liệu thật + `.env` khi được hỏi (không commit `.env`).
- Đặt lịch tự động: `./schedule_mac.sh` (Mac) / `.\schedule_win.ps1` (Windows).

### 22. order-sla

Nhắc SLA khâu trễ deadline: so hạn xử lý từng khâu/đơn với hôm nay, cảnh báo trễ/sắp hạn kèm người phụ trách và lời nhắc đốc thúc AI. Gửi Telegram.

```
/plugin install order-sla@tony-agents
/setup-order-sla
```

- Chạy thử ngay: ./run.sh --dry-run   in ra màn hình (không gửi) · ./run.sh             gửi cảnh báo Telegram
- Điền dữ liệu thật + `.env` khi được hỏi (không commit `.env`).
- Đặt lịch tự động: `./schedule_mac.sh` (Mac) / `.\schedule_win.ps1` (Windows).

### 23. payment-confirm

Xác nhận thanh toán qua nút bấm Telegram: gửi tin [✅ Đã nhận tiền][❌ Chưa] tới kế toán, ghi payments.csv trạng thái CHỜ, poll cập nhật ĐÃ XÁC NHẬN/CHƯA và sửa lại tin.

```
/plugin install payment-confirm@tony-agents
/setup-payment-confirm
```

- Chạy thử: `./run.sh --dry-run`
- Điền dữ liệu thật + `.env` khi được hỏi (không commit `.env`).
- Đặt lịch tự động: `./schedule_mac.sh` (Mac) / `.\schedule_win.ps1` (Windows).

### 24. delivery-notify

Đọc deliveries.csv, với đơn 'đã giao' thì AI soạn tin báo khách, gửi qua connector (seam) và ghi lại trạng thái đã báo.

```
/plugin install delivery-notify@tony-agents
/setup-delivery-notify
```

- Chạy thử ngay: ./run.sh --dry-run   |   ./run.sh
- Điền dữ liệu thật + `.env` khi được hỏi (không commit `.env`).
- Đặt lịch tự động: `./schedule_mac.sh` (Mac) / `.\schedule_win.ps1` (Windows).

### 25. customer-tracking

Khách tự tra trạng thái đơn theo số điện thoại; AI trả lời tự nhiên trạng thái từng đơn từ orders.csv.

```
/plugin install customer-tracking@tony-agents
/setup-customer-tracking
```

- Chạy thử ngay: ./run.sh 0901234567            -> tìm đơn của SĐT đó, AI trả lời trạng thái từng đơn · ./run.sh 0901234567 --dry-run  -> giống trên nhưng ghi rõ đây là bản chạy thử (không khác biệt, không gửi đi) · ./run.sh                       -> hướng dẫn cách dùng
- Điền dữ liệu thật + `.env` khi được hỏi (không commit `.env`).

### 26. dept-handoff

Điều phối đơn giữa các bộ phận SALES → SẢN XUẤT → GIAO: bàn giao đơn, AI soạn thông báo và gửi Telegram vào chat của bộ phận nhận.

```
/plugin install dept-handoff@tony-agents
/setup-dept-handoff
```

- Chạy thử ngay: ./run.sh list                  in bảng đơn theo bộ phận (in ra màn hình) · ./run.sh handoff DH001         chuyển đơn DH001 sang bộ phận kế: AI soạn thông báo, · ./run.sh handoff DH001 --dry-run   xem thử, KHÔNG ghi file, KHÔNG gửi Telegram
- Điền dữ liệu thật + `.env` khi được hỏi (không commit `.env`).
- Đặt lịch tự động: `./schedule_mac.sh` (Mac) / `.\schedule_win.ps1` (Windows).

### 27. ops-daily-report

Báo cáo vận hành cuối ngày: đếm đơn theo từng khâu, phát hiện khâu tắc (tồn nhiều/quá hạn/ứ đọng), AI nhận định và đề xuất xử lý. Gửi Telegram.

```
/plugin install ops-daily-report@tony-agents
/setup-ops-daily-report
```

- Chạy thử: `./run.sh --dry-run`
- Điền dữ liệu thật + `.env` khi được hỏi (không commit `.env`).
- Đặt lịch tự động: `./schedule_mac.sh` (Mac) / `.\schedule_win.ps1` (Windows).

### 28. eod-report-collector

Bot thu báo cáo cuối ngày: đọc reports.csv của từng nhân viên, AI tổng hợp điểm chính từng phòng và việc tồn/rủi ro, gửi Telegram sếp ~21h.

```
/plugin install eod-report-collector@tony-agents
/setup-eod-report-collector
```

- Chạy thử: `./run.sh --dry-run`
- Điền dữ liệu thật + `.env` khi được hỏi (không commit `.env`).
- Đặt lịch tự động: `./schedule_mac.sh` (Mac) / `.\schedule_win.ps1` (Windows).

### 29. daily-kpi

KPI hàng ngày từng nhân viên: đọc kpi.csv, tính % đạt, xếp hạng, AI nhận định ai vượt/ai hụt cần hỗ trợ. Gửi Telegram.

```
/plugin install daily-kpi@tony-agents
/setup-daily-kpi
```

- Chạy thử: `./run.sh --dry-run`
- Điền dữ liệu thật + `.env` khi được hỏi (không commit `.env`).
- Đặt lịch tự động: `./schedule_mac.sh` (Mac) / `.\schedule_win.ps1` (Windows).

### 30. payroll-calc

Tính lương theo sản phẩm/ca/show từ work.csv: lương mỗi người = tổng (số lượng × đơn giá), cộng tổng quỹ lương, AI tóm tắt. Gửi Telegram.

```
/plugin install payroll-calc@tony-agents
/setup-payroll-calc
```

- Chạy thử ngay: ./run.sh --dry-run   in bảng lương ra màn hình (không gửi) · ./run.sh             gửi bảng lương qua Telegram
- Điền dữ liệu thật + `.env` khi được hỏi (không commit `.env`).
- Đặt lịch tự động: `./schedule_mac.sh` (Mac) / `.\schedule_win.ps1` (Windows).

### 31. task-reminder

Nhắc việc checklist (onboarding, deadline, lịch trực) từ tasks.csv: lọc việc quá hạn/đến hạn/chưa xong, AI sắp thứ tự ưu tiên. Gửi Telegram.

```
/plugin install task-reminder@tony-agents
/setup-task-reminder
```

- Chạy thử ngay: ./run.sh --dry-run   in ra màn hình (không gửi) · ./run.sh             gửi lời nhắc Telegram
- Điền dữ liệu thật + `.env` khi được hỏi (không commit `.env`).
- Đặt lịch tự động: `./schedule_mac.sh` (Mac) / `.\schedule_win.ps1` (Windows).

### 32. attendance-checkin

Chấm công qua bot Telegram: nhân viên gõ /checkin hoặc /checkout, bot ghi attendance.csv (Nhân viên, Ngày, Giờ vào, Giờ ra) và in bảng công trong ngày.

```
/plugin install attendance-checkin@tony-agents
/setup-attendance-checkin
```

- Chạy thử ngay: ./run.sh poll                 đọc tin mới (getUpdates), ghi công, lưu offset .tg_offset · ./run.sh report --dry-run     in bảng công HÔM NAY ra màn hình (không gửi Telegram) · ./run.sh report               gửi bảng công hôm nay vào Telegram (chốt ca cuối ngày) · ./run.sh --dry-run            = report --dry-run
- Điền dữ liệu thật + `.env` khi được hỏi (không commit `.env`).
- Đặt lịch tự động: `./schedule_mac.sh` (Mac) / `.\schedule_win.ps1` (Windows).

### 33. leave-expense-approval

Bot Telegram luồng duyệt nghỉ phép / chi phí: nhân viên gửi yêu cầu, quản lý bấm nút Duyệt/Từ chối, tự cập nhật trạng thái và ghi log requests.csv.

```
/plugin install leave-expense-approval@tony-agents
/setup-leave-expense-approval
```

- Chạy thử ngay: ./run.sh submit-leave "Nguyễn Văn A" 25/07/2026 "Về quê có việc"     xin nghỉ · ./run.sh submit-expense "Trần Thị B" 850000 "Taxi đi khảo sát"       xin chi phí · ./run.sh submit-leave "..." 25/07/2026 "..." --dry-run               chỉ xem, không gửi · ./run.sh poll                                                        nhận quyết định
- Điền dữ liệu thật + `.env` khi được hỏi (không commit `.env`).
- Đặt lịch tự động: `./schedule_mac.sh` (Mac) / `.\schedule_win.ps1` (Windows).

### 34. master-assistant

Trợ lý tổng (router) — hỏi một câu bằng tiếng Việt, AI đọc danh mục agent đã cài (agents.csv) rồi chỉ ra nên dùng agent/lệnh nào và làm ngay bước gì.

```
/plugin install master-assistant@tony-agents
/setup-master-assistant
```

- Chạy thử ngay: ./run.sh "sáng nay có lead nào mới không?" · ./run.sh "làm báo cáo doanh thu tháng" · ./run.sh --dry-run "gửi tin nhắn Zalo cho khách"   # giống nhau: in ra màn hình · ./run.sh --list                                     # xem danh mục agent đã cài
- Điền dữ liệu thật + `.env` khi được hỏi (không commit `.env`).

### 35. ads-reporter

Báo cáo Meta/TikTok Ads mỗi sáng: đọc ads.csv, tính tổng chi và CPM/CPC/CPL từng kênh & chiến dịch, AI nhận định nên tăng ngân sách hay tắt. Gửi Telegram.

```
/plugin install ads-reporter@tony-agents
/setup-ads-reporter
```

- Chạy thử: `./run.sh --dry-run`
- Điền dữ liệu thật + `.env` khi được hỏi (không commit `.env`).
- Đặt lịch tự động: `./schedule_mac.sh` (Mac) / `.\schedule_win.ps1` (Windows).

### 36. ads-manager-chat

Điều khiển quảng cáo bằng lệnh Telegram: bật/tắt campaign, đổi ngân sách. Áp lên nền tảng qua connector (seam), ghi actions.csv, hiểu cả câu nói tự nhiên nhờ Claude Code.

```
/plugin install ads-manager-chat@tony-agents
/setup-ads-manager-chat
```

- Chạy thử ngay: ./run.sh --dry-run tat "Mùa Cưới 2026"          mô phỏng tắt 1 campaign (không gửi, không áp thật) · ./run.sh --dry-run bat "Combo Chụp Ảnh"          mô phỏng bật · ./run.sh --dry-run nsach "Mùa Cưới 2026" 800000  mô phỏng đổi ngân sách/ngày · ./run.sh poll                                     đọc lệnh mới trong chat, áp qua connector, ghi actions.csv, trả lời
- Điền dữ liệu thật + `.env` khi được hỏi (không commit `.env`).
- Đặt lịch tự động: `./schedule_mac.sh` (Mac) / `.\schedule_win.ps1` (Windows).

### 37. ab-test-tracker

Theo dõi A/B test creative: tính CTR/CVR mỗi biến thể, chọn winner mỗi nhóm, AI nhận định nên nhân bản/cắt. Gửi Telegram.

```
/plugin install ab-test-tracker@tony-agents
/setup-ab-test-tracker
```

- Chạy thử ngay: ./run.sh --dry-run   in ra màn hình (không gửi) · ./run.sh             gửi báo cáo Telegram
- Điền dữ liệu thật + `.env` khi được hỏi (không commit `.env`).
- Đặt lịch tự động: `./schedule_mac.sh` (Mac) / `.\schedule_win.ps1` (Windows).

### 38. content-hunter

Content Hunter: quét TikTok/YouTube (bản export) tìm format viral trong ngách, AI rút ra hook đang lên và cách áp dụng cho ngành của bạn. Gửi Telegram.

```
/plugin install content-hunter@tony-agents
/setup-content-hunter
```

- Chạy thử ngay: ./run.sh --dry-run   |   ./run.sh
- Điền dữ liệu thật + `.env` khi được hỏi (không commit `.env`).
- Đặt lịch tự động: `./schedule_mac.sh` (Mac) / `.\schedule_win.ps1` (Windows).

### 39. competitor-intel

Tình báo đối thủ: đọc competitor.csv (ad|post), AI tóm tắt động thái từng đối thủ và cảnh báo mối đe dọa/cơ hội. Gửi Telegram.

```
/plugin install competitor-intel@tony-agents
/setup-competitor-intel
```

- Chạy thử: `./run.sh --dry-run`
- Điền dữ liệu thật + `.env` khi được hỏi (không commit `.env`).
- Đặt lịch tự động: `./schedule_mac.sh` (Mac) / `.\schedule_win.ps1` (Windows).

### 40. voucher-maker

Bot tạo nội dung voucher/ấn phẩm theo template: AI soạn tiêu đề, ưu đãi, điều kiện, thời hạn và sinh mã voucher, xuất ra voucher.html tự chứa. Không cần ảnh, không cần Telegram.

```
/plugin install voucher-maker@tony-agents
/setup-voucher-maker
```

- Chạy thử ngay: ./run.sh "Giảm 20% chụp cưới tháng 8"     tạo 1 voucher · ./run.sh --dry-run                          chạy thử với yêu cầu mẫu (CSV) · ./run.sh --dry-run "Tặng album ảnh cưới"    chạy thử, không cần cấu hình
- Điền dữ liệu thật + `.env` khi được hỏi (không commit `.env`).

### 41. comment-insight

Đọc comments.csv (Nguồn, Nội dung), AI gom mối quan tâm/thắc mắc của khách thành 3-5 insight kèm gợi ý chủ đề content nên làm, gửi Telegram.

```
/plugin install comment-insight@tony-agents
/setup-comment-insight
```

- Chạy thử ngay: ./run.sh --dry-run   |   ./run.sh
- Điền dữ liệu thật + `.env` khi được hỏi (không commit `.env`).
- Đặt lịch tự động: `./schedule_mac.sh` (Mac) / `.\schedule_win.ps1` (Windows).

### 42. content-calendar

Lịch content: nhắc bài đăng hôm nay và 3 ngày tới chưa đăng, cảnh báo ngày trống, AI gợi ý, gửi Telegram.

```
/plugin install content-calendar@tony-agents
/setup-content-calendar
```

- Chạy thử ngay: ./run.sh --dry-run   in ra màn hình (không gửi) · ./run.sh             gửi nhắc lịch Telegram
- Điền dữ liệu thật + `.env` khi được hỏi (không commit `.env`).
- Đặt lịch tự động: `./schedule_mac.sh` (Mac) / `.\schedule_win.ps1` (Windows).

---

Bảo mật: template không chứa key của ai. Dữ liệu/token của bạn chỉ nằm trong `.env` và file cục bộ — `.gitignore` đã chặn không cho commit.
