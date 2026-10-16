from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter, ImageFont


V2_PATH = Path(r"C:\Users\ZORN\OneDrive\桌面\chain\scripts\compose_xuanhai_v2.py")
spec = spec_from_file_location("xuanhai_v2", V2_PATH)
v2 = module_from_spec(spec)
spec.loader.exec_module(v2)

ROOT = Path(r"C:\Users\ZORN\OneDrive\桌面\chain\玄海镇祥")
OUT = ROOT / "ouput" / "v3-focus"
ASSETS = ROOT / "ouput" / "v2-real" / "assets"
CUTOUT = ROOT / "ouput" / "assets" / "玄海镇祥-真实像素抠图.png"
SIZE = 1024

FONT_XINGKAI = r"C:\Windows\Fonts\STXINGKA.TTF"
FONT_KAI = r"C:\Windows\Fonts\STKAITI.TTF"
FONT_SANS = r"C:\Windows\Fonts\msyh.ttc"
FONT_SANS_BOLD = r"C:\Windows\Fonts\msyhbd.ttc"

GOLD = (240, 218, 172, 255)
IVORY = (246, 244, 236, 255)
BLUE_WHITE = (218, 237, 244, 255)
MUTED = (190, 205, 211, 255)


def font(path, size):
    return ImageFont.truetype(path, size=size)


def plate(index):
    image = v2.fit_cover(Image.open(ASSETS / f"bg-{index:02d}.png")).convert("RGBA")
    image = image.filter(ImageFilter.GaussianBlur(1.4))
    image = ImageEnhance.Brightness(image).enhance(0.78)
    image = ImageEnhance.Contrast(image).enhance(0.94)
    return image


def add_spotlight(image, center, radius, color=(104, 165, 194), opacity=105):
    yy, xx = np.mgrid[0:SIZE, 0:SIZE]
    cx, cy = center
    rx, ry = radius
    dist = ((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2
    alpha = np.clip(1 - dist, 0, 1) ** 1.8 * opacity
    light = Image.new("RGBA", image.size, (*color, 0))
    light.putalpha(Image.fromarray(alpha.astype(np.uint8), "L").filter(ImageFilter.GaussianBlur(20)))
    return Image.alpha_composite(image, light)


def load_product():
    product = Image.open(CUTOUT).convert("RGBA")
    alpha = product.getchannel("A").filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(0.35))
    rgb = product.convert("RGB")
    # Lift photographed shadow detail without changing bead geometry or hue.
    lut = [min(255, round((i / 255) ** 0.78 * 255)) for i in range(256)]
    rgb = rgb.point(lut * 3)
    rgb = ImageEnhance.Contrast(rgb).enhance(1.12)
    rgb = ImageEnhance.Color(rgb).enhance(1.07)
    rgb = ImageEnhance.Sharpness(rgb).enhance(1.26)
    result = rgb.convert("RGBA")
    result.putalpha(alpha)
    return result


def place_product(base, x, y, width, rim=120):
    product = load_product()
    scale = width / product.width
    product = product.resize((width, round(product.height * scale)), Image.Resampling.LANCZOS)
    alpha = product.getchannel("A")

    shadow = Image.new("RGBA", product.size, (0, 0, 0, 0))
    shadow.putalpha(alpha.point(lambda p: p * 175 // 255).filter(ImageFilter.GaussianBlur(22)))
    base.alpha_composite(shadow, (x, y + 22))

    outer = alpha.filter(ImageFilter.MaxFilter(25))
    rim_alpha = ImageChops.subtract(outer, alpha).filter(ImageFilter.GaussianBlur(7))
    rim_alpha = rim_alpha.point(lambda p: p * rim // 255)
    glow = Image.new("RGBA", product.size, (128, 204, 232, 0))
    glow.putalpha(rim_alpha)
    base.alpha_composite(glow, (x, y))
    base.alpha_composite(product, (x, y))


def draw_vertical(layer, x, y, text, fnt, fill, gap):
    draw = ImageDraw.Draw(layer)
    for ch in text:
        box = draw.textbbox((0, 0), ch, font=fnt)
        w = box[2] - box[0]
        draw.text((x - w / 2, y), ch, font=fnt, fill=fill)
        y += gap


def save(image, name):
    OUT.mkdir(parents=True, exist_ok=True)
    image.convert("RGB").save(OUT / name, quality=97, subsampling=0)


def make_01():
    image = add_spotlight(plate(1), (520, 620), (470, 390), opacity=130)
    top = Image.new("RGBA", (SIZE, 245), (2, 8, 14, 105))
    image.alpha_composite(top, (0, 0))
    place_product(image, 112, 232, 800, rim=175)
    text = Image.new("RGBA", image.size, (0, 0, 0, 0))
    v2.draw_tracking(text, (SIZE / 2, 30), "玄海镇祥", font(FONT_XINGKAI, 110), GOLD, 12, "ma")
    v2.add_rule(text, 150, 148, 150)
    v2.draw_tracking(text, (SIZE / 2, 174), "祥云纳吉|补水宁神", font(FONT_KAI, 35), IVORY, 6, "ma")
    save(Image.alpha_composite(image, text), "01-玄海镇祥-主视觉-v3.jpg")


def make_02():
    image = add_spotlight(plate(2), (690, 660), (410, 340), opacity=135)
    panel = Image.new("RGBA", image.size, (0, 0, 0, 0))
    ImageDraw.Draw(panel).rounded_rectangle((34, 42, 490, 905), radius=28, fill=(2, 8, 14, 122))
    image = Image.alpha_composite(image, panel.filter(ImageFilter.GaussianBlur(8)))
    place_product(image, 372, 350, 635, rim=180)
    text = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw_vertical(text, 455, 78, "金水相生", font(FONT_KAI, 39), GOLD, 54)
    draw_vertical(text, 370, 78, "天然纯黑黑曜石", font(FONT_KAI, 31), IVORY, 43)
    draw_vertical(text, 278, 78, "圆润海蓝宝·山鬼·祥云手串", font(FONT_KAI, 30), BLUE_WHITE, 41)
    draw_vertical(text, 115, 78, "玄海镇祥", font(FONT_XINGKAI, 61), GOLD, 77)
    d = ImageDraw.Draw(text)
    d.line((505, 76, 505, 704), fill=(227, 204, 164, 115), width=2)
    save(Image.alpha_composite(image, text), "02-玄海镇祥-竖排介绍-v3.jpg")


def make_03():
    image = add_spotlight(plate(3), (670, 650), (470, 380), opacity=140)
    place_product(image, 318, 338, 700, rim=190)
    text = Image.new("RGBA", image.size, (0, 0, 0, 0))
    v2.draw_tracking(text, (62, 44), "精挑细选", font(FONT_XINGKAI, 78), GOLD, 6)
    v2.draw_tracking(text, (64, 150), "纯黑黑曜石 +海蓝宝", font(FONT_KAI, 43), IVORY, 1)
    v2.draw_tracking(text, (64, 218), "无坑无杂质", font(FONT_KAI, 41), BLUE_WHITE, 5)
    d = ImageDraw.Draw(text)
    d.line((65, 286, 380, 286), fill=(227, 204, 164, 145), width=2)
    d.rounded_rectangle((560, 825, 958, 938), radius=18, fill=(2, 8, 14, 135))
    d.text((760, 854), "珠体圆润 孔口光滑", font=font(FONT_KAI, 31), fill=IVORY, anchor="mm")
    d.text((760, 902), "细节见真章", font=font(FONT_XINGKAI, 45), fill=GOLD, anchor="mm")
    save(Image.alpha_composite(image, text), "03-玄海镇祥-珠体细节-v3.jpg")


def make_04():
    image = add_spotlight(plate(4), (515, 560), (470, 360), opacity=145)
    place_product(image, 118, 182, 790, rim=190)
    text = Image.new("RGBA", image.size, (0, 0, 0, 0))
    v2.add_rule(text, 846, 140, 160)
    v2.draw_tracking(text, (SIZE / 2, 847), "玄海镇祥", font(FONT_XINGKAI, 112), GOLD, 12, "ma")
    save(Image.alpha_composite(image, text), "04-玄海镇祥-极简展示-v3.jpg")


def ring_mask(center, outer, inner):
    yy, xx = np.mgrid[0:SIZE, 0:SIZE]
    cx, cy = center
    ro = ((xx - cx) / outer[0]) ** 2 + ((yy - cy) / outer[1]) ** 2
    ri = ((xx - cx) / inner[0]) ** 2 + ((yy - cy) / inner[1]) ** 2
    mask = np.clip((1.14 - ro) / 0.22, 0, 1) * np.clip((ri - 0.62) / 0.30, 0, 1)
    return Image.fromarray((mask * 255).astype(np.uint8), "L").filter(ImageFilter.GaussianBlur(12))


def finish_wear(image, mask):
    base = ImageEnhance.Brightness(image).enhance(0.93).filter(ImageFilter.GaussianBlur(1.2))
    hero = ImageEnhance.Contrast(image).enhance(1.16)
    hero = ImageEnhance.Color(hero).enhance(1.05)
    hero = ImageEnhance.Brightness(hero).enhance(1.08)
    hero = ImageEnhance.Sharpness(hero).enhance(1.32)
    merged = Image.composite(hero, base, mask).convert("RGBA")
    merged = v2.add_vignette(merged, 0.22)
    frame = Image.new("RGBA", merged.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(frame)
    d.rounded_rectangle((25, 25, 998, 998), radius=22, outline=(240, 218, 172, 105), width=2)
    return Image.alpha_composite(merged, frame)


def make_05():
    image = v2.photo_crop(ROOT / "example" / "6.jpg", (0, 355, 810, 1165))
    mask = ring_mask((485, 640), (455, 420), (305, 265))
    save(finish_wear(image, mask), "05-玄海镇祥-手背穿戴-v3.jpg")


def make_06():
    image = v2.photo_crop(ROOT / "example" / "7.jpg", (0, 250, 810, 1060))
    mask = ring_mask((505, 520), (410, 370), (270, 225))
    save(finish_wear(image, mask), "06-玄海镇祥-手心展示-v3.jpg")


def main():
    make_01(); make_02(); make_03(); make_04(); make_05(); make_06()
    print(OUT)


if __name__ == "__main__":
    main()
