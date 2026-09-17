#!/usr/bin/env python3
"""產生 iOS 主畫面與資訊清單所需的 PNG 圖示。

只用標準程式庫的 zlib 與 struct 手寫 PNG。為兩個純色圓角圖示引入影像處理套件
（Pillow 之類）並不成比例，而 iOS 主畫面圖示不接受 SVG，所以也不能改用向量。

可重複執行：每次都覆寫輸出檔，不需要先刪除。

用法：
    python3 tools/make_icons.py
"""

import pathlib
import struct
import zlib

# 與頁面主題一致的配色：深藍底、紅色定位圓點。
BG = (26, 26, 46)        # #1a1a2e，與 body 背景相同
FG = (233, 69, 96)       # #e94560，與標題和標記同色
RING = (78, 204, 163)    # #4ecca3，與狀態良好的指示色相同

# iOS 主畫面用 180、資訊清單用 512。兩者都是 PNG。
SIZES = (180, 512)

OUT_DIR = pathlib.Path(__file__).resolve().parent.parent / "static" / "icons"


def _chunk(tag: bytes, data: bytes) -> bytes:
    """組出一個 PNG 區塊：長度、標記、資料、CRC。"""
    return (
        struct.pack(">I", len(data))
        + tag
        + data
        + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
    )


def _pixels(size: int) -> bytearray:
    """畫出圖示的像素。

    圓角矩形底色，中央一個實心圓點外加一圈環——夠像個定位標記，而且不需要
    任何字型或向量算繪。
    """
    r = size * 22 // 100            # 圓角半徑
    cx = cy = (size - 1) / 2
    dot_r = size * 0.17             # 中央圓點
    ring_r = size * 0.32            # 外環中線
    ring_w = max(1.0, size * 0.045)  # 外環粗細

    rows = bytearray()
    for y in range(size):
        rows.append(0)              # 每列的濾波器位元組：0 表示無濾波
        for x in range(size):
            # 圓角：四個角落之外的區域留白（透明）
            ax = min(x, size - 1 - x)
            ay = min(y, size - 1 - y)
            if ax < r and ay < r and ((r - ax) ** 2 + (r - ay) ** 2) > r * r:
                rows.extend((0, 0, 0, 0))
                continue

            d = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
            if d <= dot_r:
                rows.extend((*FG, 255))
            elif abs(d - ring_r) <= ring_w / 2:
                rows.extend((*RING, 255))
            else:
                rows.extend((*BG, 255))
    return rows


def write_png(path: pathlib.Path, size: int) -> None:
    """寫出一個 size×size 的 RGBA PNG。"""
    ihdr = struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0)  # 8 位元、RGBA
    png = (
        b"\x89PNG\r\n\x1a\n"
        + _chunk(b"IHDR", ihdr)
        + _chunk(b"IDAT", zlib.compress(bytes(_pixels(size)), 9))
        + _chunk(b"IEND", b"")
    )
    path.write_bytes(png)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for size in SIZES:
        path = OUT_DIR / f"app-icon-{size}.png"
        write_png(path, size)
        print(f"wrote {path.relative_to(OUT_DIR.parent.parent)} ({size}x{size}, {path.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
