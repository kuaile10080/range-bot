from nonebot import on_command, on_regex
from nonebot.params import CommandArg
from nonebot.adapters import Event
from nonebot.adapters.onebot.v11 import Message, MessageSegment

from src.libraries.ongeki_music import *
from src.libraries.image import *
from src.libraries.tool import hash

import re, random
DEFAULT_PRIORITY = 10

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
                for id in ongeki_music:
                    for i,chart in enumerate(ongeki_music[id]["charts"]):
                        if chart["ds"] == ds1:
                            s += f"{id}. [{diffs[i]}:{ds1}] {ongeki_music[id]['title']}\n"
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
                count = 0
                for id in ongeki_music:
                    for i,chart in enumerate(ongeki_music[id]["charts"]):
                        if float(ds1) <= float(chart["ds"]) <= float(ds2):
                            count += 1
                            s += f"{id}. [{diffs[i]}:{chart['ds']}] {ongeki_music[id]['title']}\n"
                if s == "\n":
                    await osearch_music.finish("没有找到这样的歌")
                elif count>200:
                    await osearch_music.finish("结果过多，请输入更精确的定数范围")
                else:
                    await osearch_music.finish(MessageSegment.image(f"base64://{str(image_to_base64(text_to_image(s)), encoding='utf-8')}"))       
            else:
                await osearch_music.finish("定数查询格式错误")

wm_list = ['拼机', '推分', '越级', '下埋', '夜勤', '练底力', '练手法', '干饭', '接弹幕', '收歌', '打舞萌', '打中二']
jrog = on_command('今日音击', aliases={'今日ongeki','今日o'}, priority = DEFAULT_PRIORITY, block=True)
@jrog.handle()
async def _jrog(event: Event, message: Message = CommandArg()):
    qq = int(event.get_user_id())
    h = hash(qq)
    rp = h % 100
    wm_value = []
    for i in range(len(wm_list)):
        wm_value.append(h & 3)
        h >>= 2
    s = f"今日人品值：{rp}\n"
    for i in range(len(wm_list)):
        if wm_value[i] == 3:
            s += f'宜 {wm_list[i]}\n'
        elif wm_value[i] == 0:
            s += f'忌 {wm_list[i]}\n'
    s += "然哥提醒您：打几把音击快去学习\n"
    idlist = list(ongeki_music.keys())
    music = ongeki_music[idlist[h % len(idlist)]]
    await jrog.finish(MessageSegment.text(s) + osong_txt(music))

oid = on_command('oid', priority = DEFAULT_PRIORITY, block=True)
@oid.handle()
async def _(event: Event, message: Message = CommandArg()):
    msg = str(message).strip()
    try:
        id = int(msg)
        music = get_music_by_id(id)
        if music:
            await oid.finish(osong_txt(music))
        else:
            await oid.finish("没有找到这首歌")
    except:
        return