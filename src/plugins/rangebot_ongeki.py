from nonebot import on_command, on_regex
from nonebot.params import CommandArg
from nonebot.adapters import Event
from nonebot.adapters.onebot.v11 import Message, MessageSegment

from src.libraries.ongeki_music import *
from src.libraries.image import *

import re, random
DEFAULT_PRIORITY = 10

diffs = ["Basic", "Advanced", "Expert", "Master","Lunatic"]

osearch_music = on_regex(r"^o(.*)查歌(.+)",priority = DEFAULT_PRIORITY, block=True)
@osearch_music.handle()
async def _jrog(event: Event):
    msg = str(event.get_message())
    pattern = r"^o(.*)查歌(.+)"
    match = re.match(pattern, msg)
    msg2 = match.group(2).strip()
    if match:
        if match.group(1) == "":
            res = search_music_by_parttitle(msg2)
            if len(res) == 0:
                await osearch_music.finish("没有找到这样的歌")
            elif len(res) == 1:
                await osearch_music.finish(osong_txt(res[0]))
            else:
                s = "\n"
                for music in res:
                    s += f"{music['id']}. {music['title']}\n"
                await osearch_music.finish(MessageSegment.image(f"base64://{str(image_to_base64(text_to_image(s)), encoding='utf-8')}"))

        elif match.group(1) == "曲师":
            res = search_music_by_artist(msg2)
            if len(res) == 0:
                await osearch_music.finish("没有找到这样的歌")
            elif len(res) == 1:
                await osearch_music.finish(osong_txt(res[0]))
            else:
                s = "\n"
                for music in res:
                    s += f"{music['id']}. {music['title']}\n"
                await osearch_music.finish(MessageSegment.image(f"base64://{str(image_to_base64(text_to_image(s)), encoding='utf-8')}"))

        elif match.group(1) == "新歌":
            res = []
            for title in my_ongeki_music:
                if my_ongeki_music[title]["new"]:
                    res.append(my_ongeki_music[title])
            if len(res) == 0:
                await osearch_music.finish("没有找到这样的歌")
            elif len(res) == 1:
                await osearch_music.finish(osong_txt(res[0]))
            else:
                s = "\n"
                for music in res:
                    s += f"{music['id']}. {music['title']}\n"
                await osearch_music.finish(MessageSegment.image(f"base64://{str(image_to_base64(text_to_image(s)), encoding='utf-8')}"))
        elif match.group(1) == "定数":
            ds = msg2.split(" ")
            if len(ds) == 1:
                # 格式化为保留一位小数的字符串
                try:
                    ds1 = float(ds[0])
                    ds1 = str(round(ds1, 1))
                except:
                    await osearch_music.finish("请输入正确的定数")
                s = "\n"
                for title in my_ongeki_music:
                    for i,ds in enumerate(my_ongeki_music[title]["ds"]):
                        if ds == ds1:
                            s += f"{my_ongeki_music[title]['id']}. [{diffs[i]}:{ds}] {my_ongeki_music[title]['title']}\n"
                if s == "\n":
                    await osearch_music.finish("没有找到这样的歌")
                else:
                    await osearch_music.finish(MessageSegment.image(f"base64://{str(image_to_base64(text_to_image(s)), encoding='utf-8')}"))
            elif len(ds) == 2:
                try:
                    ds1 = float(ds[0])
                    ds1 = str(round(ds1, 1))
                    ds2 = float(ds[1])
                    ds2 = str(round(ds2, 1))
                except:
                    await osearch_music.finish("请输入正确的定数")
                s = "\n"
                for title in my_ongeki_music:
                    for i,ds in enumerate(my_ongeki_music[title]["ds"]):
                        if float(ds1) <= float(ds) <= float(ds2):
                            s += f"{my_ongeki_music[title]['id']}. [{diffs[i]}:{ds}] {my_ongeki_music[title]['title']}\n"
                if s == "\n":
                    await osearch_music.finish("没有找到这样的歌")
                else:
                    await osearch_music.finish(MessageSegment.image(f"base64://{str(image_to_base64(text_to_image(s)), encoding='utf-8')}"))       
            else:
                await osearch_music.finish("定数查询格式错误")

wm_list = ['推分', '越级', '下埋', '夜勤', '练底力','练手法', '打mai', '干饭', '接弹幕', '收歌', '打中2']
jrog = on_command('今日音击', aliases={'今日ongeki','今日o'}, priority = DEFAULT_PRIORITY, block=True)
@jrog.handle()
async def _jrog(event: Event, message: Message = CommandArg()):
    qq = int(event.get_user_id())
    h = hash(qq)
    rp = h % 100
    wm_value = []
    for i in range(11):
        wm_value.append(h & 3)
        h >>= 2
    s = f"今日人品值：{rp}\n"
    for i in range(11):
        if wm_value[i] == 3:
            s += f'宜 {wm_list[i]}\n'
        elif wm_value[i] == 0:
            s += f'忌 {wm_list[i]}\n'
    s += "然哥提醒您：打几把中二快去学习\n"
    title = random.choice(list(my_ongeki_music.keys()))
    while my_ongeki_music[title]["title_sort"]=="":
        title = random.choice(list(my_ongeki_music.keys()))
    music = my_ongeki_music[title]
    await jrog.finish(MessageSegment.text(s) + osong_txt(music))

oid = on_command('oid', priority = DEFAULT_PRIORITY, block=True)
@oid.handle()
async def _(event: Event, message: Message = CommandArg()):
    msg = str(message).strip()
    try:
        id = int(msg)
        music = get_music_by_id(id)
        await oid.finish(osong_txt(music))
    except:
        return