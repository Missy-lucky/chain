from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "scripts" / "xuanhai_source.jpg"
OUT_DIR = ROOT / "玄海镇祥" / "ouput" / "final-B-严格模板"

# The 24 real bead centers detected in the source photo.  These are the actual
# 21 obsidian + 3 aquamarine beads; two false detections from cast shadows were
# deliberately removed.
BEADS = [
    (289, 746, 40), (311, 671, 45), (350, 599, 40), (417, 560, 39),
    (483, 527, 39), (557, 512, 41), (633, 512, 38), (694, 535, 39),
    (760, 565, 40), (812, 617, 41), (857, 677, 43), (893, 753, 43),
    (909, 837, 43), (886, 922, 45), (836, 989, 42), (772, 1041, 42),
    (692, 1069, 42), (613, 1083, 43), (529, 1078, 42), (446, 1071, 41),
    (377, 1027, 45), (327, 967, 36), (295, 891, 48), (292, 817, 36),
]


def build_product_mask(source: Image.Image) -> Image.Image:
    mask = Image.new("L", source.size, 0)
    draw = ImageDraw.Draw(mask)

    # Individual circles keep every real bead and avoid including the original
    # white tabletop.  A narrow connector preserves all six real silver spacers.
    for x, y, radius in BEADS:
        pad = 1
        r = radius + pad
        draw.ellipse((x - r, y - r, x + r, y + r), fill=255)

    decorated_run = [
        (311, 671), (289, 746), (292, 817), (295, 891),
        (327, 967), (377, 1027), (446, 1071),
    ]
    draw.line(decorated_run, fill=255, width=45, joint="curve")
    return mask.filter(ImageFilter.GaussianBlur(2.2))


def main() -> None:
    source = Image.open(SOURCE).convert("RGB")
    product_mask = build_product_mask(source)

    # Grade the original tabletop/wood in place.  Because the background is
    # derived from the very same photo, the contact shadows and edge pixels stay
    # natural; only the scene around the untouched bracelet changes tonality.
    gray = ImageOps.autocontrast(ImageOps.grayscale(source), cutoff=1)
    background = ImageOps.colorize(gray, black=(2, 7, 13), white=(48, 65, 78))
    background = ImageEnhance.Contrast(background).enhance(1.14)
    background = ImageEnhance.Brightness(background).enhance(0.78)
    background = background.filter(ImageFilter.GaussianBlur(0.65))

    # A unified grade (instead of a hard subject cutout) keeps every original
    # contact edge and eliminates any pale extraction halo.  A restrained amount
    # of source color retains the obsidian, aquamarine and silver identities.
    scene = Image.blend(background, source, 0.36)
    scene = ImageEnhance.Contrast(scene).enhance(1.12)
    scene = ImageEnhance.Brightness(scene).enhance(1.06)
    # A broad overhead pool of light lifts the entire original scene around the
    # bracelet, avoiding any subject-shaped halo while keeping the product clear.
    gamma_lut = [round(255 * ((value / 255) ** 0.72)) for value in range(256)]
    lifted = scene.point(gamma_lut * 3)
    pool = Image.new("L", source.size, 0)
    ImageDraw.Draw(pool).ellipse((145, 365, 1055, 1245), fill=220)
    pool = pool.filter(ImageFilter.GaussianBlur(95))
    scene = Image.composite(lifted, scene, pool)
    # Square crop keeps the full bracelet and leaves the lower title zone clear.
    scene = scene.crop((100, 325, 1100, 1325)).resize((1250, 1250), Image.Resampling.LANCZOS)
    scene_path = OUT_DIR / "assets" / "04-scene.png"
    scene.save(scene_path, quality=100)

    # Save a transparent QA cutout next to other exact-product assets.
    qa = source.convert("RGBA")
    qa.putalpha(product_mask)
    qa.crop((235, 455, 965, 1145)).save(
        ROOT / "玄海镇祥" / "ouput" / "assets" / "玄海镇祥-24珠精细抠图.png"
    )


if __name__ == "__main__":
    main()
