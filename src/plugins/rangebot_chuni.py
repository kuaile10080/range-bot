from nonebot import on_command, on_regex
from nonebot.params import CommandArg
from nonebot.adapters import Event
from nonebot.adapters.onebot.v11 import Message, MessageSegment
from nonebot.exception import FinishedException

from src.libraries.image import *
from src.libraries.chuni_music import *
from src.libraries.tool import hash
from src.libraries.image import *

import re

chuni_music_jp = get_chuni_json()

chuni_b40 = on_command('cb30', priority=10, block=True)
@chuni_b40.handle()
async def _(event: Event, message: Message = CommandArg()):
    username = str(message).strip()
    if username == "":
        payload = {'qq': str(event.get_user_id())}
    else:
        payload = {'username': username}
    img, success = await generate_chuni40(payload)
    if success == 400:
        await chuni_b40.finish("未找到此玩家，请确登陆https://www.diving-fish.com/maimaidx/prober/录入分数，并正确填写用户名与QQ号。")
    elif success == 403:
        await chuni_b40.finish("该用户禁止了其他人获取数据。")
    else:
        await chuni_b40.finish(MessageSegment.image(f"base64://{str(image_to_base64(img), encoding='utf-8')}"))

cover_dir = 'src/static/chunithm/cover/'

def song_txt(music: Music):
    return MessageSegment.text(f"{music.id}. {music.title}\n") + \
        MessageSegment.image(f"base64://{str(image_to_base64(get_chuni_cover(music.id)), encoding='utf-8')}") + \
        MessageSegment.text(f"\n定数:{'/'.join(str(ds) for ds in music['ds'])}\n") + \
        MessageSegment.text(f"艺术家: {music['basic_info']['artist']}\n") + \
        MessageSegment.text(f"分类: {music['basic_info']['genre']}\n") + \
        MessageSegment.text(f"BPM: {music['basic_info']['bpm']}\n") + \
        MessageSegment.text(f"版本: {music['basic_info']['from']}\n")

def song_txt_r(music: dict):
    lev_list = []
    lev_keys = ["lev_bas", "lev_adv", "lev_exp", "lev_mas", "lev_ult"]
    for key in lev_keys:
        if music[key] != "":
            lev_list.append(music[key])
        else:
            lev_list.append("-")
    return MessageSegment.text(f"{music['id']}. {music['title']}\n") + \
        MessageSegment.image(f"base64://{str(image_to_base64(get_chuni_cover(music['id'])), encoding='utf-8')}") + \
        MessageSegment.text(f"\n等级:{'/'.join(lev_list)}\n") + \
        MessageSegment.text(f"艺术家: {music['artist']}\n") + \
        MessageSegment.text(f"分类: {music['catname']}\n") + \
        MessageSegment.text(f"注音: {music['reading']}\n")

def inner_level_q(ds1, ds2=None):
    result_set = []
    diff_label = ['Bas', 'Adv', 'Exp', 'Mst', 'ReM']
    if ds2 is not None:
        music_data = total_list.filter(ds=(ds1, ds2))
    else:
        music_data = total_list.filter(ds=ds1)
    for music in sorted(music_data, key=lambda i: int(i['id'])):
        for i in music.diff:
            result_set.append(
                (music['id'], music['title'], music['ds'][i], diff_label[i], music['level'][i]))
    return result_set


inner_level = on_command('cinner_level ', aliases={'c定数查歌 '}, priority=10, block=True)
@inner_level.handle()
async def _(event: Event, message: Message = CommandArg()):
    argv = str(message).strip().split(" ")
    if len(argv) > 2 or len(argv) == 0:
        await inner_level.finish("命令格式为\nc定数查歌 <定数>\nc定数查歌 <定数下限> <定数上限>")
    if len(argv) == 1:
        result_set = inner_level_q(float(argv[0]))
    else:
        result_set = inner_level_q(float(argv[0]), float(argv[1]))
    if len(result_set) > 300:
        await inner_level.finish(f"结果过多（{len(result_set)} 条），请缩小搜索范围。")
    s = """ 结果如下：

 """
    for elem in result_set:
        s += f"""{elem[0]}. {elem[1]} {elem[3]} {elem[4]}({elem[2]})
 """
    await inner_level.finish(MessageSegment.image(f"base64://{str(image_to_base64(text_to_image(s)), encoding='utf-8')}"))


spec_rand = on_regex(r"^c随个(?:dx|sd|标准)?[绿黄红紫白]?[0-9]+\+?", priority=10, block=True)
@spec_rand.handle()
async def _(event: Event):
    # level_labels = ['绿', '黄', '红', '紫', '白']
    regex = "c随个((?:dx|sd|标准))?([绿黄红紫白]?)([0-9]+\+?)"
    res = re.match(regex, str(event.get_message()).lower())
    level = res.groups()[2]
    if res.groups()[1] == "":
        music_data = total_list.filter(level=level)
    else:
        music_data = total_list.filter(
            level=level, diff=['绿黄红紫白'.index(res.groups()[1])])
    if len(music_data) == 0:
        rand_result = "没有这样的乐曲哦。"
    else:
        rand_result = song_txt(music_data.random())
    await spec_rand.finish(rand_result)


mr = on_regex(r".*中二.*什么", priority=10, block=True)
@mr.handle()
async def _():
    await mr.finish(song_txt(total_list.random()))


search_music = on_regex(r"^c查歌.+",priority=10, block=True)
@search_music.handle()
async def _(event: Event):
    regex = "c查歌(.+)"
    name = re.match(regex, str(event.get_message())).groups()[0].strip()
    if name == "":
        return
    res = total_list.filter(title_search=name)
    if len(res) == 0:
        await search_music.finish("没有找到这样的乐曲。")
    elif len(res) == 1:
        await search_music.finish(song_txt(res[0]))
    elif len(res) < 30:
        search_result = ""
        for music in sorted(res, key=lambda i: int(i['id'])):
            search_result += f"{music['id']}. {music['title']}\n"
        await search_music.finish(search_result.strip())
    else:
        await search_music.finish(f"结果过多（{len(res)} 条），请缩小查询范围。")

crsearch_music = on_regex(r"^cr查歌.+",priority=10, block=True)
@crsearch_music.handle()
async def _(event: Event):
    regex = "cr查歌(.+)"
    name = re.match(regex, str(event.get_message())).groups()[0].strip()
    if name == "":
        return
    res = []
    for music in chuni_music_jp:
        if name.lower() in music['title'].lower():
            res.append(music)
    if len(res) == 0:
        await crsearch_music.finish("没有找到这样的乐曲。")
    elif len(res) == 1:
        await crsearch_music.finish(song_txt_r(res[0]))
    elif len(res) < 50:
        search_result = ""
        for music in sorted(res, key=lambda i: int(i['id'])):
            search_result += f"{music['id']}. {music['title']}\n"
        await crsearch_music.finish(search_result.strip())
    else:
        await crsearch_music.finish(f"结果过多（{len(res)} 条），请缩小查询范围。")

crid = on_regex(r"^crid ?([0-9]+)", priority=10, block=True)
@crid.handle()
async def _(event: Event):
    regex = "crid ?([0-9]+)"
    id = re.match(regex, str(event.get_message())).groups()[0].strip()
    for music in chuni_music_jp:
        if music['id'] == id:
            await crid.finish(song_txt_r(music))
    await crid.finish("没有找到这样的乐曲。")



query_chart = on_regex(r"^c([绿黄红紫白]?)id ?([0-9]+)", priority=10, block=True)
@query_chart.handle()
async def _(event: Event):
    regex = "c([绿黄红紫白]?)id ?([0-9]+)"
    groups = re.match(regex, str(event.get_message())).groups()
    level_labels = ['绿', '黄', '红', '紫', '白']
    if groups[0] != "":
            level_index = level_labels.index(groups[0])
            level_name = ['Basic', 'Advanced',
                          'Expert', 'Master', 'Re: MASTER']
            name = groups[1].strip()
            music = total_list.by_id(name)

            if music is None:
                await query_chart.finish("没有找到这样的乐曲。")
            if len(chart = music['charts']) < level_index:
                await query_chart.finish("没有这个难度。")

            chart = music['charts'][level_index]
            ds = music['ds'][level_index]
            level = music['level'][level_index]
            img = get_chuni_cover(music.id)
            msg = f"{level_name[level_index]} {level}({ds})\n谱师: {chart['charter']}\nCombo: {chart['combo']}"
            await query_chart.finish(MessageSegment.text(f"{music['id']}. {music['title']}\n") +
                                     MessageSegment.image(f"base64://{str(image_to_base64(img), encoding='utf-8')}") +
                                     MessageSegment.text(msg))
    else:
        name = groups[1].strip()
        music = total_list.by_id(name)
        await query_chart.finish(song_txt(music))


wm_list = ['推分', '越级', '下埋', '夜勤', '练底力','练手法', '打SUN', '干饭', '抓大J', '收歌', '扭头去打mai']
jrzhe = on_command('今日中二', aliases={'今日chuni'}, priority=10, block=True)


@jrzhe.handle()
async def _(event: Event, message: Message = CommandArg()):
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
    music = total_list[h % len(total_list)]
    await jrzhe.finish(MessageSegment.text(s) + song_txt(music))


"""-----------谱师查歌&曲师查歌&新歌查歌&BPM查歌&版本查歌-----------"""
hardlist = ['Basic', 'Advance', 'Expert', 'Master', 'Re:Master']

ccharter_search = on_command('c谱师查歌', priority=10, block=True)
@ccharter_search.handle()
async def _(event: Event, message: Message = CommandArg()):
    charter = str(message).strip()
    k = 0
    s = """ 结果如下

 """
    for i in range(0, len(music_data)):
        for j in range(3, len(music_data[i]['charts'])):
            if charter.lower() in music_data[i]['charts'][j]['charter'].lower():
                k += 1
                s += ('No.' + str(k) + ' ' + music_data[i]['charts'][j]['charter'] + ' ' + '[' + str(music_data[i]['id']) + ']' + '. ' + hardlist[j] + ' ' + music_data[i]['title'])
                s += """
 """
    if k > 350:
        await ccharter_search.finish(f"结果过多（{k} 条），请缩小搜索范围。")
    elif k == 0:
        await ccharter_search.finish(f"没有找到结果，请检查搜索条件。")
    await ccharter_search.finish(MessageSegment.image(f"base64://{str(image_to_base64(text_to_image(s)), encoding='utf-8')}"))


cartist_search = on_command('c曲师查歌', priority=10, block=True)
@cartist_search.handle()
async def _(event: Event, message: Message = CommandArg()):
    artist = str(message).strip()
    k = 0
    s = """ 结果如下

 """
    for i in range(0, len(music_data)):
        if artist.lower() in music_data[i]['basic_info']['artist'].lower():
            k += 1
            s += ('No.' + str(k) + ' ' + music_data[i]['basic_info']['artist'] +
                  ' ' + '[' + str(music_data[i]['id']) + ']' + '. ' + music_data[i]['title'])
            s += """
 """
    if k > 300:
        await cartist_search.finish(f"结果过多（{k} 条），请缩小搜索范围。")
    elif k == 0:
        await cartist_search.finish(f"没有找到结果，请检查搜索条件。")
    await cartist_search.finish(MessageSegment.image(f"base64://{str(image_to_base64(text_to_image(s)), encoding='utf-8')}"))


cversion_search = on_command('c版本查歌', priority=10, block=True)
@cversion_search.handle()
async def _(event: Event, message: Message = CommandArg()):
    artist = str(message).strip()
    k = 0
    s = """ 结果如下

 """
    for i in range(0, len(music_data)):
        if artist.lower() in music_data[i]['basic_info']['from'].lower():
            k += 1
            s += ('No.' + str(k) + ' ' + music_data[i]['basic_info']['from'] +
                  ' ' + '[' + str(music_data[i]['id']) + ']' + '. ' + music_data[i]['title'])
            s += """
 """
    if k > 300:
        await cversion_search.finish(f"结果过多（{k} 条），请缩小搜索范围。")
    elif k == 0:
        await cversion_search.finish(f"没有找到结果，请检查搜索条件。")
    await cversion_search.finish(MessageSegment.image(f"base64://{str(image_to_base64(text_to_image(s)), encoding='utf-8')}"))


cbpm_search = on_command('cbpm查歌', aliases={"cBPM查歌", "cBpm查歌"}, priority=10, block=True)
@cbpm_search.handle()
async def _(event: Event, message: Message = CommandArg()):
    argv = str(message).strip().split(" ")
    if len(argv) == 2:
        k = 0
        s = """ 结果如下

 """
        for i in range(0, len(music_data)):
            if (float(argv[0]) <= music_data[i]['basic_info']['bpm'] <= float(argv[1])):
                k += 1
                s += ('No.' + str(k) + ' BPM:' + str(music_data[i]['basic_info']['bpm']) +
                      ' ' + '[' + str(music_data[i]['id']) + ']' + '. ' + music_data[i]['title'])
                s += """
 """
    elif len(argv) == 1:
        k = 0
        s = """ 结果如下
 """
        for i in range(0, len(music_data)):
            if (float(argv[0]) == music_data[i]['basic_info']['bpm']):
                k += 1
                s += ('No.' + str(k) + ' BPM:' + str(music_data[i]['basic_info']['bpm']) +
                      ' ' + '[' + str(music_data[i]['id']) + ']' + '. ' + music_data[i]['title'])
                s += """
 """
    else:
        await cbpm_search.finish("命令格式为\nbpm查歌 <bpm>\nbpm查歌 <bpm下限> <bpm上限>")
    if k > 300:
        await cbpm_search.finish(f"结果过多（{k} 条），请缩小搜索范围。")
    elif k == 0:
        await cbpm_search.finish(f"没有找到结果，请检查搜索条件。")
    await cbpm_search.finish(MessageSegment.image(f"base64://{str(image_to_base64(text_to_image(s)), encoding='utf-8')}"))
