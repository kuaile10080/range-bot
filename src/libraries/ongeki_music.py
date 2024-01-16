import json, unicodedata, os
from PIL import Image
from nonebot.adapters.onebot.v11 import MessageSegment
from src.libraries.image import image_to_base64


path = "src/static/ongeki/"

with open(path + "id2title.json","r",encoding="utf-8") as f:
    id2title = json.load(f)

with open(path + "my_ongeki_music.json","r",encoding="utf-8") as f:
    my_ongeki_music = json.load(f)

def lowwidth(input_str:str) -> str:
    return ''.join([unicodedata.normalize('NFKC', char) for char in input_str])

def get_music_by_id(id) -> dict:
    return my_ongeki_music[id2title[str(id)]] if str(id) in id2title else None

def search_music_by_parttitle(s:str) -> list:
    s = lowwidth(s).lower()
    res = []
    for title in my_ongeki_music:
        if s in lowwidth(title).lower():
            res.append(my_ongeki_music[title])
    return res

def search_music_by_artist(s:str) -> list:
    s = lowwidth(s).lower()
    res = []
    for title in my_ongeki_music:
        if s in lowwidth(my_ongeki_music[title]["artist"]).lower():
            res.append(my_ongeki_music[title])
    return res

def get_ongeki_cover_by_id(id:str) -> Image.Image:
    if os.path.exists(path + "cover/" + str(id) + ".png"):
        return Image.open(path + "cover/" + str(id) + ".png")
    else:
        return Image.open(path + "cover/000000.png")

def osong_txt(music: dict):
    s = ""
    for ds in music['ds']:
        if ds:
            s += f"{ds}/"
        else:
            s += "-/"
    s = s[:-1]
    return MessageSegment.text(f"{music['id']}. {music['title']}\n") + \
        MessageSegment.image(f"base64://{str(image_to_base64(get_ongeki_cover_by_id(music['id'])), encoding='utf-8')}") + \
        MessageSegment.text(f"\n定数:{s}\n") + \
        MessageSegment.text(f"艺术家: {music['artist']}\n") + \
        MessageSegment.text(f"分类: {music['category']}\n") + \
        MessageSegment.text(f"章节: {music['chapter']}\n") + \
        MessageSegment.text(f"角色: {music['character']}\n")