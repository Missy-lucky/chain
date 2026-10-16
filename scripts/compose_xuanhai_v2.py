from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont


ROOT = Path(r"C:\Users\ZORN\OneDrive\桌面\chain\玄海镇祥")
OUT = ROOT / "ouput" / "v2-real"
ASSETS = OUT / "assets"
CUTOUT = ROOT / "ouput" / "assets" / "玄海镇祥-真实像素抠图.png"

SIZE = 1024
FONT_SERIF = r"C:\Windows\Fonts\STSONG.TTF"
FONT_SANS = r"C:\Windows\Fonts\msyh.ttc"
FONT_SANS_BOLD = r"C:\Windows\Fonts\msyhbd.ttc"

CHAMPAGNE = (231, 215, 183, 255)
IVORY = (239, 237, 229, 255)
SILVER = (202, 213, 220, 255)
MUTED = (171, 184, 191, 255)


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size=size)


def fit_cover(image: Image.Image, size=(SIZE, SIZE), center=(0.5, 0.5)) -> Image.Image:
    image = image.convert("RGB")
    target_w, target_h = size
    scale = max(target_w / image.width, target_h / image.height)
    resized = image.resize(
        (round(image.width * scale), round(image.height * scale)),
        Image.Resampling.LANCZOS,
    )
    x = round((resized.width - target_w) * center[0])
    y = round((resized.height - target_h) * center[1])
    x = max(0, min(x, resized.width - target_w))
    y = max(0, min(y, resized.height - target_h))
    return resized.crop((x, y, x + target_w, y + target_h))


def tracking_width(draw: ImageDraw.ImageDraw, text: str, fnt, spacing: int) -> int:
    widths = [draw.textlength(ch, font=fnt) for ch in text]
    return round(sum(widths) + spacing * max(0, len(text) - 1))


def draw_tracking(
    layer: Image.Image,
    xy,
    text: str,
    fnt,
    fill,
    spacing: int = 0,
    anchor: str = "la",
):
    draw = ImageDraw.Draw(layer)
    x, y = xy
    total = tracking_width(draw, text, fnt, spacing)
    if anchor.startswith("m"):
        x -= total / 2
    elif anchor.startswith("r"):
        x -= total
    for char in text:
        draw.text((round(x), round(y)), char, font=fnt, fill=fill, anchor="la")
        x += draw.textlength(char, font=fnt) + spacing


def add_rule(layer: Image.Image, y: int, width=180, alpha=130):
    draw = ImageDraw.Draw(layer)
    x0 = (SIZE - width) // 2
    draw.line((x0, y, x0 + width, y), fill=(205, 183, 145, alpha), width=2)
    draw.ellipse((SIZE // 2 - 3, y - 3, SIZE // 2 + 3, y + 3), fill=CHAMPAGNE)


def load_product() -> Image.Image:
    product = Image.open(CUTOUT).convert("RGBA")
    # Remove one-pixel extraction fringe while retaining the photographed pixels.
    alpha = product.getchannel("A").filter(ImageFilter.MinFilter(3)).filter(
        ImageFilter.GaussianBlur(0.45)
    )
    product.putalpha(alpha)
    return product


def product_layer(width: int) -> Image.Image:
    product = load_product()
    ratio = width / product.width
    return product.resize(
        (width, round(product.height * ratio)), Image.Resampling.LANCZOS
    )


def place_product(base: Image.Image, x: int, y: int, width: int, shadow=(0, 22, 22, 150)):
    product = product_layer(width)
    dx, dy, blur, opacity = shadow
    alpha = product.getchannel("A")
    sh = Image.new("RGBA", product.size, (0, 0, 0, 0))
    sh.putalpha(alpha.point(lambda p: p * opacity // 255).filter(ImageFilter.GaussianBlur(blur)))
    base.alpha_composite(sh, (x + dx, y + dy))
    base.alpha_composite(product, (x, y))


def add_vignette(image: Image.Image, strength=0.48) -> Image.Image:
    yy, xx = np.mgrid[0:SIZE, 0:SIZE]
    nx = (xx - SIZE / 2) / (SIZE / 2)
    ny = (yy - SIZE / 2) / (SIZE / 2)
    distance = np.sqrt(nx * nx + ny * ny)
    alpha = np.clip((distance - 0.35) / 0.75, 0, 1) * 255 * strength
    layer = Image.new("RGBA", (SIZE, SIZE), (3, 10, 16, 0))
    layer.putalpha(Image.fromarray(alpha.astype(np.uint8), "L"))
    return Image.alpha_composite(image.convert("RGBA"), layer)


def plate(index: int) -> Image.Image:
    return fit_cover(Image.open(ASSETS / f"bg-{index:02d}.png")).convert("RGBA")


def save(image: Image.Image, name: str):
    OUT.mkdir(parents=True, exist_ok=True)
    image.convert("RGB").save(OUT / name, quality=96, subsampling=0)


def make_01():
    image = add_vignette(plate(1), 0.25)
    # Top title receives a calm dark veil for legibility.
    veil = Image.new("RGBA", (SIZE, 260), (3, 10, 17, 82))
    image.alpha_composite(veil, (0, 0))
    place_product(image, 190, 292, 650, shadow=(0, 24, 24, 160))
    text = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw_tracking(text, (SIZE / 2, 52), "玄海镇祥", font(FONT_SERIF, 92), CHAMPAGNE, 12, "ma")
    add_rule(text, 164, 168)
    draw_tracking(text, (SIZE / 2, 184), "祥云纳吉|补水宁神", font(FONT_SANS, 31), IVORY, 5, "ma")
    image = Image.alpha_composite(image, text)
    save(image, "01-玄海镇祥-主视觉-v2.jpg")


def draw_vertical(layer, x: int, y: int, text: str, fnt, fill, gap: int):
    draw = ImageDraw.Draw(layer)
    current_y = y
    for char in text:
        bbox = draw.textbbox((0, 0), char, font=fnt)
        w = bbox[2] - bbox[0]
        draw.text((x - w / 2, current_y), char, font=fnt, fill=fill)
        current_y += gap


def make_02():
    image = add_vignette(plate(2), 0.33)
    # Readability panel stays subtle and preserves the photographed setting.
    shade = Image.new("RGBA", image.size, (0, 0, 0, 0))
    shade_draw = ImageDraw.Draw(shade)
    shade_draw.rounded_rectangle((45, 55, 530, 830), radius=32, fill=(3, 10, 16, 92))
    image = Image.alpha_composite(image, shade.filter(ImageFilter.GaussianBlur(10)))
    place_product(image, 492, 510, 500, shadow=(0, 20, 18, 160))

    text = Image.new("RGBA", image.size, (0, 0, 0, 0))
    # The supplied order is mapped right-to-left exactly.
    draw_vertical(text, 486, 116, "金水相生", font(FONT_SANS_BOLD, 34), CHAMPAGNE, 48)
    draw_vertical(text, 398, 116, "天然纯黑黑曜石", font(FONT_SANS, 30), IVORY, 43)
    draw_vertical(text, 304, 116, "圆润海蓝宝·山鬼·祥云手串", font(FONT_SANS, 29), IVORY, 41)
    draw_vertical(text, 153, 116, "玄海镇祥", font(FONT_SERIF, 52), CHAMPAGNE, 70)
    d = ImageDraw.Draw(text)
    d.line((535, 110, 535, 750), fill=(202, 183, 149, 95), width=1)
    image = Image.alpha_composite(image, text)
    save(image, "02-玄海镇祥-竖排介绍-v2.jpg")


def make_03():
    image = add_vignette(plate(3), 0.28)
    place_product(image, 455, 410, 535, shadow=(0, 22, 22, 170))
    text = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw_tracking(text, (72, 80), "精挑细选", font(FONT_SERIF, 62), CHAMPAGNE, 8)
    draw_tracking(text, (74, 178), "纯黑黑曜石 +海蓝宝", font(FONT_SANS_BOLD, 42), IVORY, 1)
    draw_tracking(text, (74, 246), "无坑无杂质", font(FONT_SANS, 38), SILVER, 5)
    d = ImageDraw.Draw(text)
    d.line((75, 324, 360, 324), fill=(205, 183, 145, 145), width=2)
    d.text((660, 830), "珠体圆润 孔口光滑", font=font(FONT_SANS, 29), fill=IVORY, anchor="mm")
    d.text((660, 882), "细节见真章", font=font(FONT_SERIF, 40), fill=CHAMPAGNE, anchor="mm")
    image = Image.alpha_composite(image, text)
    save(image, "03-玄海镇祥-珠体细节-v2.jpg")


def make_04():
    image = add_vignette(plate(4), 0.30)
    place_product(image, 170, 218, 684, shadow=(0, 26, 24, 165))
    text = Image.new("RGBA", image.size, (0, 0, 0, 0))
    add_rule(text, 848, 156)
    draw_tracking(text, (SIZE / 2, 864), "玄海镇祥", font(FONT_SERIF, 92), CHAMPAGNE, 12, "ma")
    image = Image.alpha_composite(image, text)
    save(image, "04-玄海镇祥-极简展示-v2.jpg")


def photo_crop(path: Path, crop_box) -> Image.Image:
    source = Image.open(path).convert("RGB").crop(crop_box)
    return source.resize((SIZE, SIZE), Image.Resampling.LANCZOS)


def restrained_grade(image: Image.Image, contrast=1.06, color=0.96, brightness=1.02):
    image = ImageEnhance.Contrast(image).enhance(contrast)
    image = ImageEnhance.Color(image).enhance(color)
    image = ImageEnhance.Brightness(image).enhance(brightness)
    image = ImageEnhance.Sharpness(image).enhance(1.08)
    return image


def editorial_finish(image: Image.Image, strength=0.34) -> Image.Image:
    image = add_vignette(image.convert("RGBA"), strength)
    frame = Image.new("RGBA", image.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(frame)
    d.rounded_rectangle((24, 24, 999, 999), radius=22, outline=(224, 211, 182, 90), width=2)
    d.line((64, 72, 178, 72), fill=(224, 211, 182, 115), width=2)
    d.line((846, 952, 960, 952), fill=(224, 211, 182, 115), width=2)
    return Image.alpha_composite(image, frame)


def make_05():
    # Original hand-back wearing photo; only crop, restrained grade and framing.
    image = photo_crop(ROOT / "example" / "6.jpg", (0, 355, 810, 1165))
    image = restrained_grade(image, contrast=1.07, color=0.91, brightness=1.03)
    image = editorial_finish(image, 0.24)
    save(image, "05-玄海镇祥-手背穿戴-v2.jpg")


def make_06():
    # Original palm photo. A blurred copy quiets the busy studio background while
    # the central hand and bracelet remain the untouched photographed subject.
    sharp = photo_crop(ROOT / "example" / "7.jpg", (0, 250, 810, 1060))
    sharp = restrained_grade(sharp, contrast=1.06, color=0.90, brightness=1.01)
    soft = sharp.filter(ImageFilter.GaussianBlur(13))

    yy, xx = np.mgrid[0:SIZE, 0:SIZE]
    ellipse = ((xx - 510) / 435) ** 2 + ((yy - 520) / 455) ** 2
    mask = np.clip((1.16 - ellipse) / 0.22, 0, 1) * 255
    mask = Image.fromarray(mask.astype(np.uint8), "L").filter(ImageFilter.GaussianBlur(18))
    image = Image.composite(sharp, soft, mask)
    image = editorial_finish(image, 0.30)
    save(image, "06-玄海镇祥-手心展示-v2.jpg")


def main():
    make_01()
    make_02()
    make_03()
    make_04()
    make_05()
    make_06()
    print(OUT)


if __name__ == "__main__":
    main()
