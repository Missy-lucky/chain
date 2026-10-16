from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps


ROOT = Path(r"C:\Users\ZORN\OneDrive\桌面\chain")
SIZE = 1024
FONT_TITLE = r"C:\Windows\Fonts\STXINGKA.TTF"
FONT_BODY = r"C:\Windows\Fonts\STKAITI.TTF"

GOLD = (239, 216, 174, 255)
IVORY = (248, 244, 234, 255)
PALE_BLUE = (218, 235, 241, 255)
LINE = (217, 193, 150, 150)


VERSIONS = [
    ("玄海镇祥", "final-A-原创背景"),
    ("玄海镇祥", "final-B-严格模板"),
    ("玄水藏金", "final-A-原创背景"),
    ("玄水藏金", "final-B-严格模板"),
]


def font(path: str, size: int):
    return ImageFont.truetype(path, size=size)


def load_scene(folder: Path, index: int) -> Image.Image:
    source = Image.open(folder / "assets" / f"{index:02d}-scene.png").convert("RGB")
    return ImageOps.fit(source, (SIZE, SIZE), method=Image.Resampling.LANCZOS).convert("RGBA")


def soft_panel(image: Image.Image, box, opacity=92, radius=24, blur=8):
    layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    draw.rounded_rectangle(box, radius=radius, fill=(2, 7, 12, opacity))
    image.alpha_composite(layer.filter(ImageFilter.GaussianBlur(blur)))


def draw_tracking(draw, xy, text, fnt, fill, spacing=0, anchor="la", stroke=0):
    x, y = xy
    widths = [draw.textlength(ch, font=fnt) for ch in text]
    total = sum(widths) + spacing * max(0, len(text) - 1)
    if anchor.startswith("m"):
        x -= total / 2
    elif anchor.startswith("r"):
        x -= total
    for ch in text:
        draw.text(
            (round(x), round(y)), ch, font=fnt, fill=fill,
            stroke_width=stroke, stroke_fill=(3, 8, 13, 170), anchor="la"
        )
        x += draw.textlength(ch, font=fnt) + spacing


def draw_vertical(draw, x, y, text, fnt, fill, gap, stroke=0):
    for ch in text:
        box = draw.textbbox((0, 0), ch, font=fnt)
        w = box[2] - box[0]
        draw.text(
            (x - w / 2, y), ch, font=fnt, fill=fill,
            stroke_width=stroke, stroke_fill=(3, 8, 13, 170)
        )
        y += gap


def add_top_gradient(image: Image.Image, height=270, alpha=150):
    layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    for y in range(height):
        a = round(alpha * (1 - y / height) ** 1.6)
        ImageDraw.Draw(layer).line((0, y, SIZE, y), fill=(2, 7, 12, a))
    image.alpha_composite(layer)


def add_bottom_gradient(image: Image.Image, start=760, alpha=190):
    layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    for y in range(start, SIZE):
        a = round(alpha * ((y - start) / (SIZE - start)) ** 1.2)
        draw.line((0, y, SIZE, y), fill=(2, 7, 12, a))
    image.alpha_composite(layer)


def make_01(product: str, folder: Path):
    image = load_scene(folder, 1)
    add_top_gradient(image, 285, 170)
    draw = ImageDraw.Draw(image)
    title = product
    subtitle = "祥云纳吉|补水宁神" if product == "玄海镇祥" else "饱满细腻|灵动满满"
    draw_tracking(draw, (SIZE / 2, 34), title, font(FONT_TITLE, 108), GOLD, 12, "ma", 1)
    draw.line((390, 160, 634, 160), fill=LINE, width=2)
    draw.ellipse((509, 156, 515, 162), fill=GOLD)
    draw_tracking(draw, (SIZE / 2, 183), subtitle, font(FONT_BODY, 38), IVORY, 5, "ma", 1)
    image.convert("RGB").save(folder / f"01-{product}-主视觉.jpg", quality=97, subsampling=0)


def make_02(product: str, folder: Path):
    image = load_scene(folder, 2)
    # Keep the copy close to the left edge so the bracelet remains the clear focal point.
    soft_panel(image, (18, 45, 485, 855), opacity=105, radius=30, blur=10)
    draw = ImageDraw.Draw(image)
    if product == "玄海镇祥":
        columns = [
            (435, "金水相生", 38, 53, GOLD),
            (345, "天然纯黑黑曜石", 31, 43, IVORY),
            (250, "圆润海蓝宝·山鬼·祥云手串", 30, 41, PALE_BLUE),
            (78, "玄海镇祥", 57, 74, GOLD),
        ]
    else:
        columns = [
            (505, "天然黑曜石手串", 34, 47, GOLD),
            (382, "7A天然双眼黑曜石.蓝晶石.黑发晶", 29, 40, IVORY),
            (135, "玄水藏金", 57, 74, GOLD),
        ]
    for x, text, size, gap, color in columns:
        draw_vertical(draw, x, 84, text, font(FONT_TITLE if size >= 50 else FONT_BODY, size), color, gap, 1)
    line_x = 480 if product == "玄海镇祥" else 550
    draw.line((line_x, 82, line_x, 690), fill=LINE, width=2)
    image.convert("RGB").save(folder / f"02-{product}-竖排介绍.jpg", quality=97, subsampling=0)


def make_03(product: str, folder: Path):
    image = load_scene(folder, 3)
    soft_panel(image, (28, 30, 595, 322), opacity=88, radius=24, blur=8)
    soft_panel(image, (565, 816, 992, 973), opacity=105, radius=20, blur=7)
    draw = ImageDraw.Draw(image)
    middle = "纯黑黑曜石 +海蓝宝" if product == "玄海镇祥" else "双眼黑曜石 +蓝晶石"
    draw_tracking(draw, (52, 44), "精挑细选", font(FONT_TITLE, 69), GOLD, 6, "la", 1)
    draw_tracking(draw, (54, 144), middle, font(FONT_BODY, 45), IVORY, 1, "la", 1)
    draw_tracking(draw, (54, 214), "无坑无杂质", font(FONT_BODY, 43), PALE_BLUE, 5, "la", 1)
    draw.line((55, 285, 365, 285), fill=LINE, width=2)
    draw.text((778, 850), "珠体圆润 孔口光滑", font=font(FONT_BODY, 31), fill=IVORY,
              stroke_width=1, stroke_fill=(3, 8, 13, 170), anchor="mm")
    draw.text((778, 911), "细节见真章", font=font(FONT_TITLE, 47), fill=GOLD,
              stroke_width=1, stroke_fill=(3, 8, 13, 170), anchor="mm")
    image.convert("RGB").save(folder / f"03-{product}-珠体细节.jpg", quality=97, subsampling=0)


def make_04(product: str, folder: Path):
    image = load_scene(folder, 4)
    add_bottom_gradient(image, 770, 210)
    draw = ImageDraw.Draw(image)
    title = "玄海镇祥" if product == "玄海镇祥" else "五行补水"
    draw.line((425, 846, 599, 846), fill=LINE, width=2)
    draw.ellipse((509, 842, 515, 848), fill=GOLD)
    draw_tracking(draw, (SIZE / 2, 852), title, font(FONT_TITLE, 105), GOLD, 12, "ma", 1)
    image.convert("RGB").save(folder / f"04-{product}-极简展示.jpg", quality=97, subsampling=0)


def make_05(product: str, folder: Path):
    image = load_scene(folder, 5)
    if product == "玄水藏金":
        soft_panel(image, (90, 790, 934, 985), opacity=92, radius=28, blur=8)
        draw = ImageDraw.Draw(image)
        draw.text((SIZE / 2, 842), "沉稳含蓄，内敛雅致", font=font(FONT_TITLE, 61), fill=GOLD,
                  stroke_width=1, stroke_fill=(3, 8, 13, 190), anchor="mm")
        draw.text((SIZE / 2, 918), "佩戴腕间凸显气质，低调不张扬", font=font(FONT_BODY, 33), fill=IVORY,
                  stroke_width=1, stroke_fill=(3, 8, 13, 190), anchor="mm")
    image.convert("RGB").save(folder / f"05-{product}-穿戴展示.jpg", quality=97, subsampling=0)


def make_06(product: str, folder: Path):
    image = load_scene(folder, 6)
    image.convert("RGB").save(folder / f"06-{product}-场景穿戴.jpg", quality=97, subsampling=0)


def make_contact_sheet(product: str, folder: Path):
    names = [
        f"01-{product}-主视觉.jpg", f"02-{product}-竖排介绍.jpg",
        f"03-{product}-珠体细节.jpg", f"04-{product}-极简展示.jpg",
        f"05-{product}-穿戴展示.jpg", f"06-{product}-场景穿戴.jpg",
    ]
    thumb = 512
    sheet = Image.new("RGB", (thumb * 3, thumb * 2), (15, 18, 22))
    for index, name in enumerate(names):
        image = Image.open(folder / name).convert("RGB").resize((thumb, thumb), Image.Resampling.LANCZOS)
        sheet.paste(image, ((index % 3) * thumb, (index // 3) * thumb))
    sheet.save(folder / f"_预览-{product}.jpg", quality=94, subsampling=0)


def main():
    for product, version in VERSIONS:
        folder = ROOT / product / "ouput" / version
        make_01(product, folder)
        make_02(product, folder)
        make_03(product, folder)
        make_04(product, folder)
        make_05(product, folder)
        make_06(product, folder)
        make_contact_sheet(product, folder)
        print(folder)


if __name__ == "__main__":
    main()
