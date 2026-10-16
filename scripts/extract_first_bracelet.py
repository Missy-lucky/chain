from pathlib import Path

import cv2
import numpy as np


ROOT = Path(r"C:\Users\ZORN\OneDrive\桌面\chain")
SOURCE = ROOT / "玄海镇祥" / "玄海镇祥.jpg"
OUTPUT = ROOT / "玄海镇祥" / "ouput" / "assets" / "玄海镇祥-真实像素抠图.png"


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

    # 21 black beads + 3 pale beads, traced from the original product photo.
    # Ordered clockwise starting at the upper-left black bead.
    beads = [
        (350, 596, 40),
        (414, 555, 40),
        (482, 526, 40),
        (556, 510, 39),
        (630, 511, 39),
        (695, 535, 40),
        (761, 564, 40),
        (814, 617, 39),
        (862, 675, 40),
        (895, 750, 41),
        (910, 830, 41),
        (887, 910, 41),
        (837, 977, 41),
        (771, 1026, 41),
        (692, 1060, 41),
        (610, 1077, 41),
        (531, 1078, 42),
        (450, 1069, 42),
        (380, 1025, 42),
        (329, 960, 37),   # pale bead 3
        (291, 894, 39),   # black separator 2
        (289, 817, 36),   # pale bead 2
        (286, 742, 39),   # black separator 1
        (311, 667, 36),   # pale bead 1
    ]

    mask = np.full((height, width), cv2.GC_BGD, dtype=np.uint8)

    # A narrow probable-foreground bridge retains strings and the six spacers.
    for index, (x1, y1, _) in enumerate(beads):
        x2, y2, _ = beads[(index + 1) % len(beads)]
        width_px = 42 if index >= 18 or index == len(beads) - 1 else 22
        cv2.line(mask, (x1, y1), (x2, y2), cv2.GC_PR_FGD, width_px)

    # Probable outlines and definite interiors keep the source pixels intact.
    for x, y, radius in beads:
        cv2.circle(mask, (x, y), radius + 5, cv2.GC_PR_FGD, -1)
        cv2.circle(mask, (x, y), max(radius - 8, 8), cv2.GC_FGD, -1)

    background_model = np.zeros((1, 65), np.float64)
    foreground_model = np.zeros((1, 65), np.float64)
    cv2.grabCut(
        image,
        mask,
        None,
        background_model,
        foreground_model,
        8,
        cv2.GC_INIT_WITH_MASK,
    )

    alpha = np.where(
        (mask == cv2.GC_FGD) | (mask == cv2.GC_PR_FGD), 255, 0
    ).astype(np.uint8)
    alpha = cv2.morphologyEx(alpha, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))

    # Clamp GrabCut to the known round-bead geometry. This removes retained
    # tabletop/wood patches while keeping original pixels inside every bead.
    scale = 4
    geometry = np.zeros((height * scale, width * scale), dtype=np.uint8)
    for index, (x1, y1, _) in enumerate(beads):
        x2, y2, _ = beads[(index + 1) % len(beads)]
        line_width = 42 if index >= 18 or index == len(beads) - 1 else 12
        cv2.line(
            geometry,
            (x1 * scale, y1 * scale),
            (x2 * scale, y2 * scale),
            255,
            line_width * scale,
            cv2.LINE_AA,
        )
    for x, y, radius in beads:
        cv2.circle(
            geometry,
            (x * scale, y * scale),
            radius * scale,
            255,
            -1,
            cv2.LINE_AA,
        )
    geometry = cv2.resize(
        geometry, (width, height), interpolation=cv2.INTER_LANCZOS4
    )
    alpha = cv2.min(alpha, geometry)
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
