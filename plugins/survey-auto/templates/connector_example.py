"""
connector_example.py — SEAM gửi tin thật (Zalo/SMS/email).
Copy thành connector.py rồi nhờ Claude Code điền theo kênh của bạn.
Chỉ cần 1 hàm:  send_message(phone: str, text: str) -> None
"""

def send_message(phone, text):
    # Ví dụ Zalo OA (điền OA token của bạn vào .env, đọc bằng finlib.cfg):
    #   import finlib as fl, json, urllib.request
    #   token = fl.cfg("ZALO_OA_TOKEN")
    #   ...gọi API Zalo OA gửi tin...
    raise NotImplementedError("Nhờ Claude Code viết send_message cho kênh của bạn.")
