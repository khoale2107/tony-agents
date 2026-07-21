#!/usr/bin/env python3
"""
Bot ghép ảnh quảng cáo — đưa nhiều ảnh, AI chọn 4 ảnh đẹp nhất và ghép
thành 1 ảnh quảng cáo 1080×1080 (1 ảnh MAIN cột trái + 3 ảnh phụ cột phải).

  ./run.sh <thư mục ảnh>              # AI chọn trong thư mục rồi ghép
  ./run.sh anh1.jpg anh2.jpg ...      # đưa thẳng danh sách ảnh (>=4)
  ./run.sh <...> --hd                 # xuất bản HD 3240×3240 để in
  ./run.sh --demo                     # tự sinh ảnh mẫu rồi ghép (chạy thử ngay)

AI chọn ảnh dùng GÓI Claude Code (đọc ảnh), KHÔNG cần API key.
Cần thư viện xử lý ảnh Pillow:  pip3 install Pillow
Kết quả lưu trong ./output/.
"""
from __future__ import annotations

import json
import random
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import finlib as fl

try:
    from PIL import Image, ImageChops
except ImportError:
    print("[!] Thiếu thư viện Pillow. Cài bằng:  pip3 install Pillow")
    sys.exit(1)

HERE = Path(__file__).resolve().parent
fl.load_env(HERE / ".env")

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".heic"}
CANVAS = int(fl.cfg("ADS_CANVAS", "1080"))
GAP = int(fl.cfg("ADS_GAP", "16"))
WHITE_THRESHOLD = int(fl.cfg("ADS_WHITE_THRESHOLD", "15"))
POOL_SIZE = int(fl.cfg("POOL_SIZE", "12"))
OUT = HERE / "output"


# ───────── ghép ảnh (Pillow) ─────────
def trim_white_border(img: "Image.Image", threshold: int = WHITE_THRESHOLD) -> "Image.Image":
    rgb = img.convert("RGB")
    diff = ImageChops.difference(rgb, Image.new("RGB", rgb.size, (255, 255, 255)))
    r, g, b = diff.split()
    max_diff = ImageChops.lighter(ImageChops.lighter(r, g), b)
    mask = max_diff.point(lambda p: 255 if p > (255 - threshold) else 0)
    bbox = mask.getbbox()
    return img.crop(bbox) if bbox else img


def crop_fill(img: "Image.Image", target_w: int, target_h: int, face_top: bool = True) -> "Image.Image":
    """Scale để cover target rồi crop: căn giữa ngang, dọc anchor TOP (giữ khuôn mặt)."""
    src_w, src_h = img.size
    scale = max(target_w / src_w, target_h / src_h)
    new_w = max(1, int(round(src_w * scale)))
    new_h = max(1, int(round(src_h * scale)))
    resized = img.resize((new_w, new_h), Image.LANCZOS)
    x = (new_w - target_w) // 2
    y = 0 if face_top else (new_h - target_h) // 2
    return resized.crop((x, y, x + target_w, y + target_h))


def compose_ads(main_path: Path, side_paths, scale: int = 1) -> Path:
    """1 main (cột trái 2/3) + 3 side (cột phải xếp dọc) → PNG."""
    canvas = CANVAS * scale
    gap = GAP * scale
    left_w = canvas * 2 // 3
    right_w = canvas - left_w - gap
    right_h = (canvas - 2 * gap) // 3

    out = Image.new("RGB", (canvas, canvas), (255, 255, 255))
    main_img = trim_white_border(Image.open(main_path))
    out.paste(crop_fill(main_img, left_w, canvas, face_top=True), (0, 0))
    for i, p in enumerate(side_paths[:3]):
        side = trim_white_border(Image.open(p))
        y = i * (right_h + gap)
        out.paste(crop_fill(side, right_w, right_h, face_top=True), (left_w + gap, y))

    OUT.mkdir(exist_ok=True)
    suffix = "_hd" if scale > 1 else ""
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = OUT / f"ads_{stamp}{suffix}.png"
    out.save(out_path, "PNG", optimize=True)
    return out_path


# ───────── AI chọn 4 ảnh (GÓI Claude Code) ─────────
PICK_PROMPT = (
    "Bạn là art director. Dưới đây là danh sách ảnh (đánh số từ 0). "
    "Hãy XEM từng ảnh (dùng công cụ Read với đường dẫn) rồi chọn 4 ảnh đẹp nhất để ghép 1 tấm quảng cáo: "
    "1 ảnh MAIN (dọc, rõ mặt/chủ thể, đặt cột trái) + 3 ảnh phụ (cột phải). "
    "Ưu tiên ảnh nét, ánh sáng đẹp, bố cục thoáng, tránh ảnh mờ/trùng nhau. "
    'CHỈ trả về JSON đúng dạng: {"main_index": <số>, "other_indexes": [<3 số khác nhau>], "reason": "<ngắn gọn>"}. '
    "Không thêm chữ nào ngoài JSON."
)


def ai_pick(pool: list[Path]) -> dict | None:
    claude = fl.find_claude()
    if not claude:
        return None
    listing = "\n".join(f"[{i}] {p}" for i, p in enumerate(pool))
    prompt = f"{PICK_PROMPT}\n\nDanh sách ảnh:\n{listing}"
    try:
        r = subprocess.run([claude, "-p", prompt, "--allowedTools", "Read"],
                           capture_output=True, text=True, timeout=240)
    except Exception as e:
        print(f"[!] Lỗi gọi Claude Code: {e}")
        return None
    raw = (r.stdout or "").strip()
    try:
        s, e = raw.find("{"), raw.rfind("}")
        data = json.loads(raw[s:e + 1])
        mi = int(data["main_index"])
        others = [int(x) for x in data["other_indexes"]][:3]
        if mi in range(len(pool)) and all(o in range(len(pool)) for o in others):
            return {"main_index": mi, "other_indexes": others,
                    "reason": data.get("reason", "")}
    except Exception:
        print("[!] AI trả về không đúng JSON, dùng cách chọn dự phòng.")
    return None


def fallback_pick(pool: list[Path]) -> dict:
    """Dự phòng: 4 ảnh ngẫu nhiên, file lớn nhất làm main."""
    chosen = random.sample(pool, min(4, len(pool)))
    chosen.sort(key=lambda p: p.stat().st_size, reverse=True)
    return {"main_index": pool.index(chosen[0]),
            "other_indexes": [pool.index(p) for p in chosen[1:4]],
            "reason": "chọn dự phòng (ngẫu nhiên)"}


# ───────── gom ảnh đầu vào ─────────
def gather_images(args: list[str]) -> list[Path]:
    imgs: list[Path] = []
    for a in args:
        p = Path(a).expanduser()
        if p.is_dir():
            imgs += [q for q in sorted(p.iterdir())
                     if q.suffix.lower() in IMAGE_EXTS and not q.name.startswith("._")]
        elif p.suffix.lower() in IMAGE_EXTS and p.exists():
            imgs.append(p)
    return imgs


def make_demo_images() -> list[Path]:
    """Sinh 6 ảnh mẫu nhiều màu để chạy thử khi chưa có ảnh thật."""
    folder = HERE / "sample_images"
    folder.mkdir(exist_ok=True)
    colors = [(214, 69, 65), (33, 102, 172), (244, 165, 66),
              (76, 175, 80), (156, 39, 176), (0, 150, 136)]
    paths = []
    for i, c in enumerate(colors):
        fp = folder / f"mau_{i+1}.png"
        if not fp.exists():
            Image.new("RGB", (900, 1200 if i == 0 else 900), c).save(fp)
        paths.append(fp)
    return paths


def main() -> None:
    argv = sys.argv[1:]
    hd = "--hd" in argv
    demo = "--demo" in argv
    args = [a for a in argv if not a.startswith("-")]

    if demo:
        pool = make_demo_images()
        print(f"[i] Chế độ demo: dùng {len(pool)} ảnh mẫu trong sample_images/.")
    else:
        if not args:
            print('Cách dùng: ./run.sh <thư mục ảnh | các file ảnh>  [--hd]   (hoặc --demo để thử ngay)')
            return
        pool = gather_images(args)

    if len(pool) < 4:
        print(f"[!] Cần ít nhất 4 ảnh, hiện có {len(pool)}.")
        return
    if len(pool) > POOL_SIZE:
        pool = random.sample(pool, POOL_SIZE)

    pick = ai_pick(pool) or fallback_pick(pool)
    main_path = pool[pick["main_index"]]
    side_paths = [pool[i] for i in pick["other_indexes"]]
    print(f"🖼️  Main: {main_path.name} | Phụ: {', '.join(p.name for p in side_paths)}")
    if pick.get("reason"):
        print(f"    Lý do: {pick['reason']}")

    out = compose_ads(main_path, side_paths, scale=3 if hd else 1)
    print(f"✅ Đã ghép: {out}  ({'HD 3240×3240' if hd else '1080×1080'})")


if __name__ == "__main__":
    main()
