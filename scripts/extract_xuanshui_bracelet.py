from pathlib import Path

import cv2
import numpy as np


ROOT = Path(r"C:\Users\ZORN\OneDrive\桌面\chain")
SOURCE = ROOT / "玄水藏金" / "玄水藏金.jpg"
OUTPUT = ROOT / "玄水藏金" / "ouput" / "assets" / "玄水藏金-真实像素抠图.png"


def read_image(path: Path) -> np.ndarray:
    data = np.fromfile(str(path), dtype=np.uint8)
    image = cv2.imdecode(data, cv2.IMREAD_COLOR)
    if image is None:
        raise RuntimeError(f"Unable to read {path}")
    return image


def write_image(path: Path, image: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    ok, encoded = cv2.imencode(path.suffix, image)
    if not ok:
        raise RuntimeError(f"Unable to encode {path}")
    encoded.tofile(str(path))


def main() -> None:
    image = read_image(SOURCE)
    height, width = image.shape[:2]

    # Exact photographed order: 13 black/smoky beads, 5 blue beads,
    # and 2 transparent black-hair crystal beads = 20 beads total.
    beads = [
        (435, 440, 51, "blue"),
        (371, 505, 42, "hair"),
        (325, 574, 48, "blue"),
        (293, 659, 48, "blue"),
        (272, 744, 48, "blue"),
        (253, 830, 43, "hair"),
        (271, 915, 48, "blue"),
        (344, 1026, 59, "black"),
        (451, 1090, 60, "black"),
        (576, 1114, 60, "black"),
        (709, 1106, 59, "black"),
        (824, 1056, 58, "black"),
        (925, 965, 58, "black"),
        (982, 855, 58, "black"),
        (993, 735, 59, "black"),
        (965, 624, 59, "black"),
        (891, 520, 58, "black"),
        (788, 442, 58, "black"),
        (670, 408, 58, "black"),
        (558, 400, 57, "black"),
    ]

    mask = np.full((height, width), cv2.GC_BGD, dtype=np.uint8)
    for index, (x1, y1, _, kind) in enumerate(beads):
        x2, y2, _, next_kind = beads[(index + 1) % len(beads)]
        special = kind != "black" or next_kind != "black"
        cv2.line(mask, (x1, y1), (x2, y2), cv2.GC_PR_FGD, 28 if special else 18)
    for x, y, radius, _ in beads:
        cv2.circle(mask, (x, y), radius + 7, cv2.GC_PR_FGD, -1)
        cv2.circle(mask, (x, y), max(radius - 10, 8), cv2.GC_FGD, -1)

    bg_model = np.zeros((1, 65), np.float64)
    fg_model = np.zeros((1, 65), np.float64)
    cv2.grabCut(image, mask, None, bg_model, fg_model, 9, cv2.GC_INIT_WITH_MASK)
    alpha = np.where(
        (mask == cv2.GC_FGD) | (mask == cv2.GC_PR_FGD), 255, 0
    ).astype(np.uint8)

    # Clamp segmentation to the known 20-bead geometry while preserving the
    # photographed caps, spacers and elastic links in the special blue arc.
    scale = 4
    geometry = np.zeros((height * scale, width * scale), dtype=np.uint8)
    for index, (x1, y1, _, kind) in enumerate(beads):
        x2, y2, _, next_kind = beads[(index + 1) % len(beads)]
        special = kind != "black" or next_kind != "black"
        cv2.line(
            geometry,
            (x1 * scale, y1 * scale),
            (x2 * scale, y2 * scale),
            255,
            (34 if special else 13) * scale,
            cv2.LINE_AA,
        )
    for x, y, radius, _ in beads:
        cv2.circle(
            geometry,
            (x * scale, y * scale),
            (radius + 3) * scale,
            255,
            -1,
            cv2.LINE_AA,
        )
    geometry = cv2.resize(geometry, (width, height), interpolation=cv2.INTER_LANCZOS4)
    alpha = cv2.min(alpha, geometry)
    alpha = cv2.morphologyEx(alpha, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
    alpha = cv2.erode(alpha, np.ones((2, 2), np.uint8), iterations=1)
    alpha = cv2.GaussianBlur(alpha, (3, 3), 0.45)

    bgra = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)
    bgra[:, :, 3] = alpha
    ys, xs = np.where(alpha > 8)
    if len(xs) == 0:
        raise RuntimeError("Empty foreground mask")
    pad = 24
    x0 = max(int(xs.min()) - pad, 0)
    x1 = min(int(xs.max()) + pad + 1, width)
    y0 = max(int(ys.min()) - pad, 0)
    y1 = min(int(ys.max()) + pad + 1, height)
    write_image(OUTPUT, bgra[y0:y1, x0:x1])
    print(OUTPUT)


if __name__ == "__main__":
    main()
