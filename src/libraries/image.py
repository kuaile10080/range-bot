import base64, os, requests
from io import BytesIO

from PIL import ImageFont, ImageDraw, Image
from src.libraries.maimaidx_music import get_cover_len5_id


path = 'src/static/high_eq_image.png'
fontpath = "src/static/msyh.ttc"
cover_dir = 'src/static/mai/cover/'

def draw_text(img_pil, text, offset_x):
    draw = ImageDraw.Draw(img_pil)
    font = ImageFont.truetype(fontpath, 48)
    width, height = draw.textsize(text, font)
    x = 5
    if width > 390:
        font = ImageFont.truetype(fontpath, int(390 * 48 / width))
        width, height = draw.textsize(text, font)
    else:
        x = int((400 - width) / 2)
    draw.rectangle((x + offset_x - 2, 360, x + 2 + width + offset_x, 360 + height * 1.2), fill=(0, 0, 0, 255))
    draw.text((x + offset_x, 360), text, font=font, fill=(255, 255, 255, 255))


def text_to_image(text):
    font = ImageFont.truetype(fontpath, 24)
    padding = 10
    margin = 4
    text_list = text.split('\n')
    max_width = 0
    for text in text_list:
        w, h = font.getsize(text)
        max_width = max(max_width, w)
    wa = max_width + padding * 2
    ha = h * len(text_list) + margin * (len(text_list) - 1) + padding * 2
    i = Image.new('RGB', (wa, ha), color=(255, 255, 255))
    draw = ImageDraw.Draw(i)
    for j in range(len(text_list)):
        text = text_list[j]
        draw.text((padding, padding + j * (margin + h)), text, font=font, fill=(0, 0, 0))
    return i


def image_to_base64(img, format='PNG'):
    output_buffer = BytesIO()
    img.save(output_buffer, format)
    byte_data = output_buffer.getvalue()
    base64_str = base64.b64encode(byte_data)
    return base64_str

def get_music_cover(mid) -> Image:
    cover_path = cover_dir + f'{get_cover_len5_id(mid)}.png'
    if os.path.exists(cover_path):
        try:
            return Image.open(cover_path).convert('RGB')
        except:
            pass
    try:
        download_music_cover(mid)
        return Image.open(cover_path).convert('RGB')
    except:
        return Image.open(cover_dir + '00000.png').convert('RGB')

def download_music_cover(mid) -> int:
    cover_path = cover_dir + f'{get_cover_len5_id(mid)}.png'
    if os.path.exists(cover_path):
        return 0
    else:
        try:
            id = (5-len(mid))*'0' + mid
            url = f"https://www.diving-fish.com/covers/{id}.png"
            r = requests.get(url)
            if r.status_code == 200:
                with open(cover_path, "wb") as f:
                    f.write(r.content)
                return 1
            else:
                return id
        except:
            return id