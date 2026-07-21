"""
connector_example.py — SEAM áp lệnh quảng cáo lên nền tảng thật.
Copy thành connector.py, nhờ Claude Code điền theo Ads API của bạn
(Facebook Marketing API / Google Ads API / TikTok Ads...).

Chỉ cần đúng một hàm:
    apply_action(action: str, campaign: str, value) -> None

Trong đó:
  action   = "tat" | "bat" | "nsach"
  campaign = tên (hoặc id) campaign
  value    = số VND ngân sách/ngày khi action == "nsach", ngược lại None

Ví dụ định hướng cho Facebook Marketing API:
  - "tat"   -> POST /{campaign_id}?status=PAUSED
  - "bat"   -> POST /{campaign_id}?status=ACTIVE
  - "nsach" -> POST /{campaign_id}?daily_budget=<value*100 (đơn vị cent)>
Cần map tên campaign -> campaign_id và một access_token đọc từ .env.
"""
from __future__ import annotations


def apply_action(action, campaign, value):
    raise NotImplementedError(
        "Nhờ Claude Code viết apply_action cho Ads API của bạn "
        "(Facebook/Google/TikTok). Xem hướng dẫn trong connector_example.py."
    )
