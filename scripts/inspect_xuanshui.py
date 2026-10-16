from pathlib import Path
import cv2
import numpy as np

src = Path(r"C:\Users\ZORN\OneDrive\桌面\chain\玄水藏金\玄水藏金.jpg")
dst = Path(r"C:\Users\ZORN\.codex\visualizations\2026\10\15\01a13e16-e405-78d2-adec-4906d3d9cb14\xuanshui-grid.jpg")
img = cv2.imdecode(np.fromfile(str(src), dtype=np.uint8), cv2.IMREAD_COLOR)
for x in range(0, img.shape[1], 100):
    cv2.line(img, (x, 0), (x, img.shape[0]), (40, 40, 220), 1)
    cv2.putText(img, str(x), (x + 3, 24), cv2.FONT_HERSHEY_SIMPLEX, .55, (20, 20, 210), 1, cv2.LINE_AA)
for y in range(0, img.shape[0], 100):
    cv2.line(img, (0, y), (img.shape[1], y), (40, 40, 220), 1)
    cv2.putText(img, str(y), (4, y + 20), cv2.FONT_HERSHEY_SIMPLEX, .55, (20, 20, 210), 1, cv2.LINE_AA)
ok, enc = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, 94])
if not ok:
    raise RuntimeError("encode failed")
enc.tofile(str(dst))
print(img.shape, dst)
