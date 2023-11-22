import base64, os, requests
from io import BytesIO

from PIL import ImageFont, ImageDraw, Image

fontpath = "src/static/msyh.ttc"
cover_dir = 'src/static/mai/cover/'

def get_cover_len5_id(mid) -> str:
    return f'{int(mid):05d}'

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


def text_to_image(text:str)->Image:
    text = text.replace(' ', '  ')
    font = ImageFont.truetype(fontpath, 24)
    padding = 10
    margin = 4
    text_list = text.split('\n')
    max_width = 0
    max_height = 0
    for text in text_list:
        text_bbox = font.getbbox(text)
        w, h = text_bbox[2], text_bbox[3]
        max_width = max(max_width, w)
        max_height = max(max_height, h)
    h = max_height
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

def get_music_cover(mid) -> Image.Image:
    cover_path = f'{cover_dir}{get_cover_len5_id(mid)}.png'
    if os.path.exists(cover_path):
        return Image.open(cover_path).convert('RGB')
    else:
        mid = int(mid)
        if 1000<mid<2000:
            mid += 10000
        elif 10000<mid<11000:
            mid -= 10000
        new_cover_path = f'{cover_dir}{get_cover_len5_id(mid)}.png'
        if os.path.exists(new_cover_path):
            with open(new_cover_path, 'rb') as fp:
                content = fp.read()
                with open(cover_path, 'wb') as fp2:
                    fp2.write(content)
            return Image.open(BytesIO(content)).convert('RGB')
        else:
            try:
                url = f"https://www.diving-fish.com/covers/{get_cover_len5_id(mid)}.png"
                r = requests.get(url)
                if r.status_code == 200:
                    with open(new_cover_path, 'wb') as fp:
                        fp.write(r.content)
                    if cover_path != new_cover_path:
                        with open(cover_path, 'wb') as fp:
                            fp.write(r.content)
                    return Image.open(BytesIO(r.content)).convert('RGB')
            except:
                return Image.open('src/static/mai/cover/00000.png').convert('RGB')

def get_qq_logo(qq:any,mode=1) -> Image.Image:
    if mode == 0:
        return Image.open('src/static/mai/icon/no_qlogo.png').convert('RGBA')
    elif mode != 2 and os.path.exists(f'src/static/mai/icon/{qq}.png'):
        return Image.open(f'src/static/mai/icon/{qq}.png').convert('RGBA')
    else:
        r = requests.get(f"https://q.qlogo.cn/g?b=qq&nk={qq}&s=640")
        if r.status_code == 200:
            logo = Image.open(BytesIO(r.content))
            logo = logo.convert('RGBA')
            return logo
        else:
            return Image.open('src/static/mai/icon/default.png').convert('RGBA')