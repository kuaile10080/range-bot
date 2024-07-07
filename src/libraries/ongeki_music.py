import json, unicodedata, os
from PIL import Image
from nonebot.adapters.onebot.v11 import MessageSegment
from src.libraries.image import image_to_base64


path = "src/static/ongeki/"

diffs = ["Basic", "Advanced", "Expert", "Master","Lunatic"]

with open(path + "ongeki_music.json","r",encoding="utf-8") as f:
    ongeki_music = json.load(f)

def lowwidth(input_str:str) -> str:
    return ''.join([unicodedata.normalize('NFKC', char) for char in input_str])

def get_music_by_id(id) -> dict:
    if str(int(id)) in ongeki_music:
        return ongeki_music[str(int(id))]
    else:
        return None

def search_music_by_parttitle(s:str) -> list:
    s = lowwidth(s).lower()
    res = []
    for id in ongeki_music:
        if s in lowwidth(ongeki_music[id]["title"]).lower():
            res.append(ongeki_music[id])
    return res

def search_music_by_artist(s:str) -> list:
    s = lowwidth(s).lower()
    res = []
    for id in ongeki_music:
        if s in lowwidth(ongeki_music[id]["artist"]).lower():
            res.append(ongeki_music[id])
    return res



def get_len4_id(id) -> str:
    return str(int(id)).zfill(4)

def get_ongeki_cover_by_id(id) -> Image.Image:
    if os.path.exists(f"{path}cover/{get_len4_id(id)}.png"):
        return Image.open(f"{path}cover/{get_len4_id(id)}.png")
    if os.path.exists(f"{path}cover/UI_Jacket_{get_len4_id(id)}.png"):
        return Image.open(f"{path}cover/UI_Jacket_{get_len4_id(id)}.png")
    elif os.path.exists(f"{path}cover/{ongeki_music[str(int(id))]['sort_id']}.png"):
        return Image.open(f"{path}cover/{ongeki_music[str(int(id))]['sort_id']}.png")
    else:
        return Image.open(f"{path}cover/0.png")

def osong_txt(music: dict):

    s = ""
    for i in range(5):
        if music["charts"][i] != {}:
            if music["charts"][i]["charter"] != "":
                s += f"{diffs[i]}谱师:{music['charts'][i]['charter']}\n"
    s = s.strip()
    
    img = get_ongeki_cover_by_id(music['id']).resize((190, 190))

    return MessageSegment.text(f"{music['id']}. {music['title']}\n") + \
        MessageSegment.image(f"base64://{str(image_to_base64(img), encoding='utf-8')}") + \
        MessageSegment.text(f"\n定数:{music['ds']}\n") + \
        MessageSegment.text(f"BPM:{music['bpm']}\n") + \
        MessageSegment.text(f"艺术家: {music['artist']}\n") + \
        MessageSegment.text(f"分类: {music['category']}\n") + \
        MessageSegment.text(f"章节: {music['chapter']}\n") + \
        MessageSegment.text(f"角色: {music['character']}\n") + \
        MessageSegment.text(s)