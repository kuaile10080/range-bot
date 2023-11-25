from nonebot import on_command, on_regex
from nonebot.params import CommandArg
from nonebot.adapters import Event
from nonebot.adapters.onebot.v11 import Message, MessageSegment
from nonebot.exception import FinishedException

from src.libraries.tool import hash
from src.libraries.maimaidx_music import *
from src.libraries.image import *
from src.libraries.maimai_best_40 import generate
from src.libraries.maimai_best_50 import generate50
from src.libraries.message_segment import *

from PIL import Image
import re

cover_dir = 'src/static/mai/cover/'

def inner_level_q(ds1, ds2=None):
    result_set = []
    diff_label = ['Bas', 'Adv', 'Exp', 'Mst', 'ReM']
    if ds2 is not None:
        music_data = total_list.filter(ds=(ds1, ds2))
    else:
        music_data = total_list.filter(ds=ds1)
    for music in sorted(music_data, key = lambda i: int(i['id'])):
        for i in music.diff:
            result_set.append((music['id'], music['title'], music['ds'][i], diff_label[i], music['level'][i]))
    return result_set


inner_level = on_command('inner_level ', aliases={'定数查歌 '}, priority = 10, block = True)

@inner_level.handle()
async def _(event: Event, message: Message = CommandArg()):
    argv = str(message).strip().split(" ")
    if len(argv) > 2 or len(argv) == 0:
        await inner_level.finish("命令格式为\n定数查歌 <定数>\n定数查歌 <定数下限> <定数上限>")
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


spec_rand = on_regex(r"^随个(?:dx|sd|标准)?[绿黄红紫白]?[0-9]+\+?", priority = 10, block = True)
@spec_rand.handle()
async def _(event: Event):
    #level_labels = ['绿', '黄', '红', '紫', '白']
    regex = "随个((?:dx|sd|标准))?([绿黄红紫白]?)([0-9]+\+?)"
    res = re.match(regex, str(event.get_message()).lower())
    if res.groups()[0] == "dx":
        tp = ["DX"]
    elif res.groups()[0] == "sd" or res.groups()[0] == "标准":
        tp = ["SD"]
    else:
        tp = ["SD", "DX"]
    level = res.groups()[2]
    if res.groups()[1] == "":
        music_data = total_list.filter(level=level, type=tp)
    else:
        music_data = total_list.filter(level=level, diff=['绿黄红紫白'.index(res.groups()[1])], type=tp)
    if len(music_data) == 0:
        rand_result = MessageSegment.text("没有这样的乐曲哦。\n")
    else:
        rand_result = song_MessageSegment2(music_data.random())
    await spec_rand.finish(rand_result)


mr = on_regex(r".*maimai.*什么", priority = 100, block = True)
@mr.handle()
async def _():
    await mr.finish(song_MessageSegment2(total_list.random()))


search_music = on_regex(r"^查歌.+", priority = 10, block = True)
@search_music.handle()
async def _(event: Event):
    regex = "^查歌(.+)"
    name = re.match(regex, str(event.get_message())).groups()[0].strip()
    if name == "":
        return
    res = total_list.filter(title_search=name)
    if len(res) == 0:
        ress = total_list.filt_by_name(name)
        if len(ress) == 0:
            await search_music.finish("没有找到这样的乐曲")
        elif len(ress) == 1:
            await search_music.finish(MessageSegment.text("您要找的是不是：\n") + song_MessageSegment2(ress[0]))
        elif len(ress) < 30:
            search_result = ""
            for music in sorted(ress, key = lambda i: int(i['id'])):
                search_result += f"{music['id']}. {music['title']}\n"
            await search_music.finish(search_result.strip())
        else:
            await search_music.finish(f"结果过多（{len(ress)} 条），请缩小查询范围。")
    elif len(res) == 1:
        await search_music.finish(song_MessageSegment2(res[0]))
    elif len(res) < 50:
        search_result = ""
        for music in sorted(res, key = lambda i: int(i['id'])):
            search_result += f"{music['id']}. {music['title']}\n"
        await search_music.finish(search_result.strip())
    else:
        await search_music.finish(f"结果过多（{len(res)} 条），请缩小查询范围。")


query_chart = on_regex(r"^([绿黄红紫白老]?) ?id ?([0-9]+)" , priority = 10, block = True)
@query_chart.handle()
async def _(event: Event):
    regex = "^([绿黄红紫白老]?) ?id ?([0-9]+)"
    groups = re.match(regex, str(event.get_message())).groups()
    level_labels = ['绿', '黄', '红', '紫', '白']
    if groups[0] == "":
        name = groups[1].strip()
        music = total_list.by_id(name)
        if music is None:
            await query_chart.finish("未找到该谱面")
        else:
            await query_chart.finish(song_MessageSegment2(music))
    elif groups[0] == "老":
        name = groups[1].strip()
        music = total_list.by_id(name)
        if music is None:
            await query_chart.finish("未找到该谱面")
        else:
            await query_chart.finish(song_MessageSegment(music))
    else:
        try:
            level_index = level_labels.index(groups[0])
            level_name = ['Basic', 'Advanced', 'Expert', 'Master', 'Re: MASTER']
            name = groups[1].strip()
            music = total_list.by_id(name)
            chart = music['charts'][level_index]
#             info = f'''
# 曲师: {music['basic_info']['artist']}
# 版本: {music['basic_info']['genre']}
# 流派: {music['basic_info']['from']}
# BPM: {music['basic_info']['bpm']}'''
            ds = music['ds'][level_index]
            level = music['level'][level_index]
#-------平均完成率与拟合定数-----------------
            try:
                avg = f"{music['stats'][level_index]['avg']:.4f}%"
                fit_diff = f"{music['stats'][level_index]['fit_diff']:.2f}"
                if (fit_diff == ""):
                    avg = "游玩数据过少"
                    fit_diff = "游玩数据过少"
            except:
                avg = "游玩数据过少"
                fit_diff = "游玩数据过少"            
            diffcalc = f'''
平均达成率：{avg}
拟合定数：{fit_diff}
'''
            if len(chart['notes']) == 4:
                msg = f'''{level_name[level_index]} {level}({ds})
TAP: {chart['notes'][0]}
HOLD: {chart['notes'][1]}
SLIDE: {chart['notes'][2]}
BREAK: {chart['notes'][3]}
谱师: {chart['charter']}'''
            else:
                msg = f'''{level_name[level_index]} {level}({ds})
TAP: {chart['notes'][0]}
HOLD: {chart['notes'][1]}
SLIDE: {chart['notes'][2]}
TOUCH: {chart['notes'][3]}
BREAK: {chart['notes'][4]}
谱师: {chart['charter']}'''
            await query_chart.finish(   MessageSegment.text(f"{music['id']}. {music['title']}\n") + \
                                        MessageSegment.image(f"base64://{str(image_to_base64(get_music_cover(music.id)), encoding='utf-8')}") + \
                                        MessageSegment.text(msg + diffcalc))
        except FinishedException:
            pass
        except Exception:
            await query_chart.finish("未找到该谱面")



wm_list = ['拼机', '推分', '越级', '下埋', '夜勤', '练底力', '练手法', '打旧框', '干饭', '抓绝赞', '收歌']

jrwm = on_command('今日舞萌', aliases={'今日mai'}, priority = 10, block = True)
@jrwm.handle()
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
    s += "然哥提醒您：打几把舞萌快去学习\n新机需要共同维护，谁拆机，我拆谁\n"
    music = total_list[h % len(total_list)]
    await jrwm.finish(MessageSegment.text(s) + song_MessageSegment(music))


query_score = on_command('分数线', priority = 10, block = True)
@query_score.handle()
async def _(event: Event, message: Message = CommandArg()):
    r = "([绿黄红紫白])(id)?([0-9]+)"
    argv = str(message).strip().split(" ")
    if len(argv) == 1 and argv[0] == '帮助':
        s = '''此功能为查找某首歌分数线设计。
命令格式：分数线 <难度+歌曲id> <分数线>
	@@ -264,12 +232,11 @@ async def _(bot: Bot, event: Event, state: T_State):
SLIDE\t3/7.5/15
TOUCH\t1/2.5/5
BREAK\t5/12.5/25(外加200落)'''
        await query_score.finish(MessageSegment.image(f"base64://{str(image_to_base64(text_to_image(s)), encoding='utf-8')}"))
    elif len(argv) == 2:
        try:
            grp = re.match(r, argv[0]).groups()
            level_labels = ['绿', '黄', '红', '紫', '白']
            level_labels2 = ['Basic', 'Advanced', 'Expert', 'Master', 'Re:MASTER']
            level_index = level_labels.index(grp[0])
            chart_id = grp[2]
            line = float(argv[1])
            music = total_list.by_id(chart_id)
            chart: Dict[Any] = music['charts'][level_index]
            tap = int(chart['notes'][0])
            slide = int(chart['notes'][2])
            hold = int(chart['notes'][1])
            touch = int(chart['notes'][3]) if len(chart['notes']) == 5 else 0
            brk = int(chart['notes'][-1])
            total_score = 500 * tap + slide * 1500 + hold * 1000 + touch * 500 + brk * 2500
            break_bonus = 0.01 / brk
            break_50_reduce = total_score * break_bonus / 4
            reduce = 101 - line
            if reduce <= 0 or reduce >= 101:
                raise ValueError
            await query_chart.finish(f'''{music['title']} {level_labels2[level_index]}
分数线 {line}% 允许的最多 TAP GREAT 数量为 {(total_score * reduce / 10000):.2f}(每个-{10000 / total_score:.4f}%),
BREAK 50落(一共{brk}个)等价于 {(break_50_reduce / 100):.3f} 个 TAP GREAT(-{break_50_reduce / total_score * 100:.4f}%)''')
        except FinishedException:
            pass
        except Exception:
            await query_chart.finish("格式错误，输入“分数线 帮助”以查看帮助信息")


best_40_pic = on_command('b40', priority = 10, block = True)


@best_40_pic.handle()
async def _(event: Event, message: Message = CommandArg()):
    username = str(message).strip()
    if username == "":
        payload = {'qq': str(event.get_user_id())}
    else:
        payload = {'username': username}
    img, success = await generate(payload)
    if success == 400:
        await best_40_pic.finish("未找到此玩家，请确登陆https://www.diving-fish.com/maimaidx/prober/录入分数，并正确填写用户名与QQ号。")
    elif success == 403:
        await best_40_pic.finish("该用户禁止了其他人获取数据。")
    else:
        await best_40_pic.finish(MessageSegment.text("旧版b40已停止维护，对结果不负责")+MessageSegment.image(f"base64://{str(image_to_base64(img), encoding='utf-8')}"))

best_50_pic = on_command('b50', priority = 10, block = True)


@best_50_pic.handle()
async def _(event: Event, message: Message = CommandArg()):
    username = str(message).strip()
    if username == "":
        payload = {'qq': str(event.get_user_id()),'b50':True}
    else:
        payload = {'username': username,'b50':True}
    img, success = await generate50(payload)
    if success == 400:
        await best_50_pic.finish("未找到此玩家，请确登陆https://www.diving-fish.com/maimaidx/prober/录入分数，并正确填写用户名与QQ号。")
    elif success == 403:
        await best_50_pic.finish("该用户禁止了其他人获取数据。")
    else:
        await best_50_pic.finish(MessageSegment.image(f"base64://{str(image_to_base64(img), encoding='utf-8')}"))