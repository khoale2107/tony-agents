# Tony Agents

**Marketplace plugin của Claude Code** cho học viên khóa "50 AI Agents" của Tony Academy. Gồm **43 agent** — cài một lần, mỗi agent tự dựng thành dịch vụ chạy trên máy bạn (macOS/Windows) bằng chính tài khoản Claude của bạn. Tất cả gọi AI **qua gói Claude Code — không cần API key**.

## Bước 1 — Cài marketplace (một lần duy nhất)

Mở **Claude Code** ở bất kỳ thư mục nào rồi gõ:

```
/plugin marketplace add khoale2107/tony-agents
```
> Đã cài trước đó mà chưa thấy agent mới? Gõ `/plugin marketplace update tony-agents`.

## Bước 2 — Cài & dựng agent bạn cần

Mỗi agent cài bằng **2 lệnh**: `/plugin install <tên>@tony-agents` rồi `/setup-<tên>`. Trợ lý sẽ tự copy file, chạy thử, hỏi nguồn dữ liệu / Telegram (nếu cần) và đặt lịch giúp bạn.

Yêu cầu chung: máy đã cài `claude` và đã `claude login` (dùng gói). Không cần cài thư viện Python, không cần API key.

## Danh sách agent

| Agent | Mô tả | Cài & dựng |
|-------|-------|------------|
| **cfo-agent** | CFO Agent — dựng một dịch vụ báo cáo tài chính tự động chạy 7h sáng mỗi ngày, đọc số từ Google Sheet, tính… | `/plugin install cfo-agent@tony-agents`<br>`/setup-cfo-agent` |
| **cskh-agent** | Trợ lý CSKH — soạn câu trả lời khách hàng dựa trên kiến thức doanh nghiệp (giá, dịch vụ, chính sách) | `/plugin install cskh-agent@tony-agents`<br>`/setup-cskh-agent` |
| **budget-controller** | Cảnh báo ngân sách theo phòng ban: so chi thực tế với ngân sách tháng, cảnh báo vượt/sắp vượt kèm nhận định AI | `/plugin install budget-controller@tony-agents`<br>`/setup-budget-controller` |
| **duyet-chi** | Duyệt chi đa cấp qua Telegram: định tuyến theo số tiền (<5tr trưởng nhóm, 5-20tr quản lý, >20tr CEO), nút… | `/plugin install duyet-chi@tony-agents`<br>`/setup-duyet-chi` |
| **profit-center** | Lãi/lỗ theo chi nhánh/cửa hàng: tính doanh thu-chi phí-lợi nhuận từng chi nhánh, xếp hạng, nhận định AI | `/plugin install profit-center@tony-agents`<br>`/setup-profit-center` |
| **lead-morning** | Điểm danh khách tiềm năng mỗi sáng: lead mới, khách 3+ ngày chưa xử lý, nghi no-show, kèm gợi ý ưu tiên từ AI | `/plugin install lead-morning@tony-agents`<br>`/setup-lead-morning` |
| **ocr-invoice** | Chụp/đưa ảnh hoá đơn, AI đọc và tự ghi sổ (thêm dòng vào so_ke.csv) | `/plugin install ocr-invoice@tony-agents`<br>`/setup-ocr-invoice` |
| **spend-anomaly** | Phát hiện khoản chi vượt trung bình và hoá đơn nghi trùng, kèm nhận định AI | `/plugin install spend-anomaly@tony-agents`<br>`/setup-spend-anomaly` |
| **weekly-revenue** | Báo cáo doanh thu tuần cho ban lãnh đạo: so 7 ngày gần nhất với tuần trước, bóc theo ngày, nhận định AI | `/plugin install weekly-revenue@tony-agents`<br>`/setup-weekly-revenue` |
| **reply-approval** | Human-in-the-loop: AI soạn câu trả lời khách, đẩy qua Telegram để bạn bấm Duyệt/Sửa/Bỏ trước khi gửi. | `/plugin install reply-approval@tony-agents`<br>`/setup-reply-approval` |
| **rag-knowledge** | RAG kiến thức công ty: bot học bảng giá/chính sách/quy trình từ thư mục tài liệu, trả lời có trích nguồn | `/plugin install rag-knowledge@tony-agents`<br>`/setup-rag-knowledge` |
| **cskh-monitor** | Giám sát nhân viên tư vấn: chấm điểm phản hồi chậm, khách bị bỏ sót, kèm nhận định AI | `/plugin install cskh-monitor@tony-agents`<br>`/setup-cskh-monitor` |
| **zalo-zns** | Zalo ZNS: xác nhận đơn, nhắc lịch hẹn, nhắc thanh toán theo mẫu | `/plugin install zalo-zns@tony-agents`<br>`/setup-zalo-zns` |
| **zalo-blast** | Zalo blast khách cũ theo phân khúc: sinh nhật, 6 tháng chưa quay lại.. | `/plugin install zalo-blast@tony-agents`<br>`/setup-zalo-blast` |
| **survey-auto** | Survey tự động sau dịch vụ: gửi khảo sát cho khách vừa xong dịch vụ và tổng hợp phản hồi bằng AI | `/plugin install survey-auto@tony-agents`<br>`/setup-survey-auto` |
| **bot-booking** | Bot booking: đọc tin nhắn khách, trích nhu cầu, kiểm tra lịch trống và soạn báo giá + xác nhận đặt lịch nhanh | `/plugin install bot-booking@tony-agents`<br>`/setup-bot-booking` |
| **social-dm** | Reply/DM automation cho TikTok/Facebook: phân loại comment/DM và soạn câu trả lời theo tông từng nền tảng | `/plugin install social-dm@tony-agents`<br>`/setup-social-dm` |
| **lead-hunter** | Lead Hunter: quét bài/bình luận từ group, fanpage (bản export), AI chấm điểm khách tiềm năng và xếp hạng | `/plugin install lead-hunter@tony-agents`<br>`/setup-lead-hunter` |
| **order-pipeline** | Quản lý đơn hàng đa bước qua các khâu NHẬN → XỬ LÝ → QC → TẠO ĐƠN → XONG: xem bảng theo khâu kèm AI tóm… | `/plugin install order-pipeline@tony-agents`<br>`/setup-order-pipeline` |
| **group-command-bot** | Bot lệnh trong group Telegram: nhân viên gõ keyword (vd /donmoi, /tonkho), bot đọc file CSV, lọc dữ liệu… | `/plugin install group-command-bot@tony-agents`<br>`/setup-group-command-bot` |
| **order-status** | Đọc orders.csv, đếm đơn ở mỗi khâu và tra chi tiết từng đơn; gửi Telegram tổng quan. | `/plugin install order-status@tony-agents`<br>`/setup-order-status` |
| **order-sla** | Nhắc SLA khâu trễ deadline: so hạn xử lý từng khâu/đơn với hôm nay, cảnh báo trễ/sắp hạn kèm người phụ… | `/plugin install order-sla@tony-agents`<br>`/setup-order-sla` |
| **payment-confirm** | Xác nhận thanh toán qua nút bấm Telegram: gửi tin [✅ Đã nhận tiền][❌ Chưa] tới kế toán, ghi payments.csv… | `/plugin install payment-confirm@tony-agents`<br>`/setup-payment-confirm` |
| **delivery-notify** | Đọc deliveries.csv, với đơn 'đã giao' thì AI soạn tin báo khách, gửi qua connector (seam) và ghi lại trạng… | `/plugin install delivery-notify@tony-agents`<br>`/setup-delivery-notify` |
| **customer-tracking** | Khách tự tra trạng thái đơn theo số điện thoại; AI trả lời tự nhiên trạng thái từng đơn từ orders.csv. | `/plugin install customer-tracking@tony-agents`<br>`/setup-customer-tracking` |
| **dept-handoff** | Điều phối đơn giữa các bộ phận SALES → SẢN XUẤT → GIAO: bàn giao đơn, AI soạn thông báo và gửi Telegram… | `/plugin install dept-handoff@tony-agents`<br>`/setup-dept-handoff` |
| **ops-daily-report** | Báo cáo vận hành cuối ngày: đếm đơn theo từng khâu, phát hiện khâu tắc (tồn nhiều/quá hạn/ứ đọng), AI nhận… | `/plugin install ops-daily-report@tony-agents`<br>`/setup-ops-daily-report` |
| **eod-report-collector** | Bot thu báo cáo cuối ngày: đọc reports.csv của từng nhân viên, AI tổng hợp điểm chính từng phòng và việc… | `/plugin install eod-report-collector@tony-agents`<br>`/setup-eod-report-collector` |
| **daily-kpi** | KPI hàng ngày từng nhân viên: đọc kpi.csv, tính % đạt, xếp hạng, AI nhận định ai vượt/ai hụt cần hỗ trợ | `/plugin install daily-kpi@tony-agents`<br>`/setup-daily-kpi` |
| **payroll-calc** | Tính lương theo sản phẩm/ca/show từ work.csv: lương mỗi người = tổng (số lượng × đơn giá), cộng tổng quỹ… | `/plugin install payroll-calc@tony-agents`<br>`/setup-payroll-calc` |
| **task-reminder** | Nhắc việc checklist (onboarding, deadline, lịch trực) từ tasks.csv: lọc việc quá hạn/đến hạn/chưa xong, AI… | `/plugin install task-reminder@tony-agents`<br>`/setup-task-reminder` |
| **attendance-checkin** | Chấm công qua bot Telegram: nhân viên gõ /checkin hoặc /checkout, bot ghi attendance.csv (Nhân viên, Ngày,… | `/plugin install attendance-checkin@tony-agents`<br>`/setup-attendance-checkin` |
| **leave-expense-approval** | Bot Telegram luồng duyệt nghỉ phép / chi phí: nhân viên gửi yêu cầu, quản lý bấm nút Duyệt/Từ chối, tự cập… | `/plugin install leave-expense-approval@tony-agents`<br>`/setup-leave-expense-approval` |
| **master-assistant** | Trợ lý tổng (router) — hỏi một câu bằng tiếng Việt, AI đọc danh mục agent đã cài (agents.csv) rồi chỉ ra… | `/plugin install master-assistant@tony-agents`<br>`/setup-master-assistant` |
| **ads-reporter** | Báo cáo Meta/TikTok Ads mỗi sáng: đọc ads.csv, tính tổng chi và CPM/CPC/CPL từng kênh & chiến dịch, AI… | `/plugin install ads-reporter@tony-agents`<br>`/setup-ads-reporter` |
| **ads-manager-chat** | Điều khiển quảng cáo bằng lệnh Telegram: bật/tắt campaign, đổi ngân sách | `/plugin install ads-manager-chat@tony-agents`<br>`/setup-ads-manager-chat` |
| **ab-test-tracker** | Theo dõi A/B test creative: tính CTR/CVR mỗi biến thể, chọn winner mỗi nhóm, AI nhận định nên nhân bản/cắt | `/plugin install ab-test-tracker@tony-agents`<br>`/setup-ab-test-tracker` |
| **content-hunter** | Content Hunter: quét TikTok/YouTube (bản export) tìm format viral trong ngách, AI rút ra hook đang lên và… | `/plugin install content-hunter@tony-agents`<br>`/setup-content-hunter` |
| **competitor-intel** | Tình báo đối thủ: đọc competitor.csv (ad|post), AI tóm tắt động thái từng đối thủ và cảnh báo mối đe… | `/plugin install competitor-intel@tony-agents`<br>`/setup-competitor-intel` |
| **voucher-maker** | Bot tạo nội dung voucher/ấn phẩm theo template: AI soạn tiêu đề, ưu đãi, điều kiện, thời hạn và sinh mã… | `/plugin install voucher-maker@tony-agents`<br>`/setup-voucher-maker` |
| **comment-insight** | Đọc comments.csv (Nguồn, Nội dung), AI gom mối quan tâm/thắc mắc của khách thành 3-5 insight kèm gợi ý chủ… | `/plugin install comment-insight@tony-agents`<br>`/setup-comment-insight` |
| **content-calendar** | Lịch content: nhắc bài đăng hôm nay và 3 ngày tới chưa đăng, cảnh báo ngày trống, AI gợi ý, gửi Telegram. | `/plugin install content-calendar@tony-agents`<br>`/setup-content-calendar` |
| **ad-image-composer** | Bot ghép ảnh quảng cáo: đưa nhiều ảnh, AI (gói Claude Code) chọn 4 ảnh đẹp nhất và ghép thành ảnh quảng… | `/plugin install ad-image-composer@tony-agents`<br>`/setup-ad-image-composer` |

> Mỗi agent có sẵn dữ liệu mẫu để chạy thử `--dry-run` ngay. Riêng **ad-image-composer** cần `pip3 install Pillow`.

---

Bảo mật: template không chứa key của ai. Dữ liệu/token của bạn chỉ nằm trong `.env` và file cục bộ — `.gitignore` đã chặn không cho commit.
