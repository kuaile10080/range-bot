from nonebot.adapters.onebot.v11 import Message, MessageSegment
from src.libraries.maimaidx_music import Music
from src.libraries.image import image_to_base64, get_music_cover
from src.libraries.maimai_info import draw_music_info

def song_MessageSegment(music: Music):
    img = get_music_cover(music.id).resize((190, 190))
    return  MessageSegment.text(f"{music.id}. {music.title}\n") + \
            MessageSegment.image(f"base64://{str(image_to_base64(img), encoding='utf-8')}") + \
            MessageSegment.text(f"\n艺术家: {music.artist}\n".replace(".","·")) + \
            MessageSegment.text(f"分类: {music.genre}\n") + \
            MessageSegment.text(f"BPM: {music.bpm}\n") + \
            MessageSegment.text(f"版本: {music.cn_version}\n") + \
            MessageSegment.text(f"定数: {'/'.join(str(ds) for ds in music.ds)}")

def song_MessageSegment2(music: Music):
    return MessageSegment.image(f"base64://{str(image_to_base64(draw_music_info(music)), encoding='utf-8')}")