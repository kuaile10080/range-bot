from nonebot import on_command, on_regex, on_message
from nonebot.params import CommandArg
from nonebot.adapters import Event
from nonebot.adapters.onebot.v11 import Message, MessageSegment
from nonebot.matcher import Matcher
from nonebot.rule import to_me

from src.libraries.tool import offlineinit, convert_cn2jp
from src.libraries.maimaidx_music import total_list, music_data, refresh_music_list, refresh_alias_temp
from src.libraries.image import text_to_image, image_to_base64
from src.libraries.maimai_best_40 import generate
from src.libraries.maimai_best_50 import generate50, generateap50, generateb50_water_msg, generateb50_by_player_data
from src.libraries.maimai_plate_query import *
from src.libraries.secrets import *
from src.libraries.maimai_info import draw_new_info
from src.libraries.message_segment import song_MessageSegment2
from src.libraries.static_lists_and_dicts import pnconvert, platename_to_file, level_index_to_file, ptv, versionlist
from src.libraries.find_cover import find_cover_id

from PIL import Image, ImageDraw, ImageFont
import re,base64,random,os,json,requests,io

DEFAULT_PRIORITY = 10

cover_dir = 'src/static/mai/cover/'
long_dir_ = 'src/static/long/'
plate_path = "src/static/mai/plate/"

with open("src/static/musicGroup.json","r",encoding="utf-8") as f:
    musicGroup = json.load(f)

"""-----------(maibot删除功能：是什么歌)-----------"""
# music_aliases = defaultdict(list)
# f = open('src/static/aliases.csv', 'r', encoding='utf-8')
# tmp = f.readlines()
# f.close()
# for t in tmp:
#     arr = t.strip().split('\t')
#     for i in range(len(arr)):
#         if arr[i] != "":
#             music_aliases[arr[i].lower()].append(arr[0])

find_song = on_regex(r".+是什么歌$", priority = DEFAULT_PRIORITY, block = True)
@find_song.handle()
async def _(event: Event):
    regex = "(.+)是什么歌$"
    name = re.match(regex, str(event.get_message())).groups()[0].strip()
    if name.startswith("[CQ:"):
        return
    result_list = total_list.filt_by_name(name)
    if len(result_list) == 0:
        await find_song.finish("未找到此歌曲\n添加曲名别名请联系CDRange(50835696)")
    elif len(result_list) == 1:
        await find_song.finish(MessageSegment.text("您要找的是不是：\n") + song_MessageSegment2(result_list[0]))
    elif len(result_list) < 30:
        search_result = ""
        for music in sorted(result_list, key = lambda i: int(i['id'])):
            search_result += f"{music['id']}. {music['title']}\n"
        await find_song.finish(search_result.strip())
    else:
        await find_song.finish(f"结果过多（{len(result_list)} 条），请缩小查询范围。")

find_song_by_cover = on_message(priority = DEFAULT_PRIORITY, block = False)
@find_song_by_cover.handle()
async def _(event: Event, matcher: Matcher):
    msg = json.loads(event.json())["message"]
    if len(msg)!=2:
        return
    if msg[0]["type"] == "image" and msg[1]["type"] == "text":
        img_url = msg[0]["data"]["file"]
        text = msg[1]["data"]["text"]
    elif msg[1]["type"] == "image" and msg[0]["type"] == "text":
        img_url = msg[1]["data"]["file"]
        text = msg[0]["data"]["text"]
    else:
        return
    if text.strip() != "是什么歌":
        return
    matcher.stop_propagation()
    try:
        r = requests.get(img_url, stream=True)
        file_io = io.BytesIO(r.content)
        img = Image.open(file_io).convert("RGB")
    except:
        await find_song_by_cover.finish("图片获取失败")
    music_id = find_cover_id(img)
    cover_id = f'{int(music_id):05d}'
    music = total_list.by_id(music_id)
    if music == None:
        filenames = os.listdir(cover_dir)
        if cover_id + ".png" in filenames:
            img = Image.open(cover_dir + cover_id + ".png").convert('RGB').resize((190, 190))
            await find_song_by_cover.finish(MessageSegment.text("匹配到相似图片，但该歌曲未登录国服或已删除：\n") + MessageSegment.image(f"base64://{str(image_to_base64(img), encoding='utf-8')}"))
        else:
            await find_song_by_cover.finish("未知错误")
    else:
        await find_song_by_cover.finish(MessageSegment.text("您要找的是不是：\n") + song_MessageSegment2(music))




"""-----------谱师查歌&曲师查歌&新歌查歌&BPM查歌&版本查歌-----------"""
hardlist = ['Basic','Advance','Expert','Master','Re:Master']

charter_search = on_command('谱师查歌', priority = DEFAULT_PRIORITY, block = True)
@charter_search.handle()
async def _(event: Event, message: Message = CommandArg()):
    temp_dict = {
        2:"红",
        3:"紫",
        4:"白"
    }
    charter = str(message).strip()
    k=0
    s = s = "\n结果如下：\n"
    for i in range(0,len(music_data)):
        for j in range(2,len(music_data[i]['charts'])):
            if charter.lower() in music_data[i]['charts'][j]['charter'].lower() or convert_cn2jp(charter.lower()) in music_data[i]['charts'][j]['charter'].lower():
                k += 1
                s += f"No.{k:03d} {music_data[i]['charts'][j]['charter']} [{music_data[i]['id']}][{temp_dict[j]}]{music_data[i]['title']}\n"
    if k > 350 :
        await charter_search.finish(f"结果过多（{k} 条），请缩小搜索范围。")
    elif k == 0 :
        await charter_search.finish(f"没有找到结果，请检查搜索条件。")
    await charter_search.finish(MessageSegment.image(f"base64://{str(image_to_base64(text_to_image(s)), encoding='utf-8')}"))


artist_search = on_command('曲师查歌', priority = DEFAULT_PRIORITY, block = True)
@artist_search.handle()
async def _(event: Event, message: Message = CommandArg()):
    artist = str(message).strip()
    k=0
    s = "\n结果如下：\n"
    for i in range(0,len(music_data)):
        if artist.lower() in music_data[i]['basic_info']['artist'].lower() or convert_cn2jp(artist.lower()) in music_data[i]['basic_info']['artist'].lower():
            k += 1
            s += f"No.{k:02d} {music_data[i]['basic_info']['artist']} [{music_data[i]['id']}] {music_data[i]['title']}\n"
    if k > 99:
        await artist_search.finish(f"结果过多（{k} 条），请缩小搜索范围。")
    elif k == 0 :
        await artist_search.finish(f"没有找到结果，请检查搜索条件。")
    await artist_search.finish(MessageSegment.image(f"base64://{str(image_to_base64(text_to_image(s)), encoding='utf-8')}"))

new_search = on_command('新歌查歌', priority = DEFAULT_PRIORITY, block = True)
@new_search.handle()
async def _(event: Event, message: Message = CommandArg()):
    k=0
    s = "\n结果如下：\n"
    for i in range(0,len(music_data)):
        if (music_data[i]['basic_info']['is_new'] == True):
            k += 1
            s += f"No.{k:03d} [{music_data[i]['id']}] {music_data[i]['title']}\n"
    if k > 300:
        await new_search.finish(f"结果过多（{k} 条），请缩小搜索范围。")
    elif k == 0 :
        await new_search.finish(f"没有找到结果，请检查搜索条件。")
    await new_search.finish(MessageSegment.image(f"base64://{str(image_to_base64(text_to_image(s)), encoding='utf-8')}"))

bpm_search = on_command('bpm查歌' , aliases={"BPM查歌","Bpm查歌"}, priority = DEFAULT_PRIORITY, block = True)
@bpm_search.handle()
async def _(event: Event, message: Message = CommandArg()):
    argv = str(message).strip().split(" ")
    res = []
    if len(argv) == 2:
        for i in range(0,len(music_data)):
            if(float(argv[0]) <= music_data[i]['basic_info']['bpm'] <= float(argv[1])):
                res.append(music_data[i])
    elif len(argv) == 1:
        for i in range(0,len(music_data)):
            if(float(argv[0]) == music_data[i]['basic_info']['bpm']):
                res.append(music_data[i])
    else:
        await bpm_search.finish("命令格式为\nbpm查歌 <bpm>\nbpm查歌 <bpm下限> <bpm上限>")
    if len(res) > 99:
        await bpm_search.finish(f"结果过多（{len(res)} 条），请缩小搜索范围。")
    elif len(res) == 0 :
        await bpm_search.finish(f"没有找到结果，请检查搜索条件。")
    s = "\n结果如下：\n"
    res.sort(key = lambda x:float(x['basic_info']['bpm']))
    for i,music_dict in enumerate(res):
        s += f"No.{i+1:02d} BPM:{int(music_dict['basic_info']['bpm']):>3d} [{music_dict['id']}] {music_dict['title']}\n"
    await bpm_search.finish(MessageSegment.image(f"base64://{str(image_to_base64(text_to_image(s)), encoding='utf-8')}"))

update_music_data = on_command("更新歌曲列表", priority = DEFAULT_PRIORITY, block = True, rule = range_checker)
@update_music_data.handle()
async def _update_music_data(event: Event, message: Message = CommandArg()):
    status,strr = await offlineinit()
    if status == 1:
        global total_list, music_data
        total_list, music_data = refresh_music_list()
        await update_music_data.finish(strr)
    else:
        await update_music_data.finish(strr)


version_search = on_command('版本查歌', priority = DEFAULT_PRIORITY, block = True)
@version_search.handle()
async def _(event: Event, message: Message = CommandArg()):
    msg = str(message).strip()
    if msg == "":
        await version_search.finish("请在版本查歌后输入版本缩写，如“版本查歌 真超檄”")
    else:
        search_list = []
        for char in msg:
            if char == "真":
                search_list.append(ptv["真1"])
                search_list.append(ptv["真2"])
            elif char in ptv:
                search_list.append(ptv[char])
            else:
                await version_search.finish("版本缩写输入错误")
        res = []
        for music in total_list:
            if music.cn_version in search_list:
                res.append(music)
        if len(res) > 200:
            await version_search.finish(f"结果过多（{len(res)} 条），请缩小搜索范围。")
        else:
            res.sort(key = lambda x:int(x.id))
            s = "\n结果如下：\n"
            for i,music in enumerate(res):
                s += f"ID.{music.id:>5} {music.title} {music.type} {'/'.join(str(ds) for ds in music['ds'])}\n"    

    await version_search.finish(MessageSegment.image(f"base64://{str(image_to_base64(text_to_image(s)), encoding='utf-8')}"))





plate = on_regex(r'^([真超檄橙暁晓桃櫻樱紫菫堇白雪輝辉熊華华爽煌舞霸宙星祭祝])([極极将舞神者])(舞?)(?:进度|完成表|完成度)\s?(全?)$', priority = DEFAULT_PRIORITY, block = True)
@plate.handle()
async def _plate(event: Event):
    regex = r'^([真超檄橙暁晓桃櫻樱紫菫堇白雪輝辉熊華华爽煌舞霸宙星祭祝])([極极将舞神者])(舞?)(?:进度|完成表|完成度)\s?(全?)$'
    res = re.match(regex, str(event.get_message())).groups()
    if ((res[0]=="霸") ^ (res[1]=="者")) or ((res[1]=="舞") ^ (res[2]=="舞")):
        await plate.finish("¿")
    version = pnconvert[res[0]]
    if version == "霸":
        version = "舞"
    if version in "新的":
        ids = []
        for music in total_list:
            if music.cn_version == ptv["祭"]:
                ids.append(music.id)
    else:
        ids = musicGroup[version]
    if version == "舞":
        remids = musicGroup["舞ReMASTER"]
    else:
        remids = []
    
    status = {
        "MST_Re": {
            "V":0,
            "X":0,
            "-":len(remids)
        },
        "MST":{
            "V":0,
            "X":0,
            "-":len(ids)
        },
        "EXP":{
            "V":0,
            "X":0,
            "-":len(ids)
        },
        "ADV":{
            "V":0,
            "X":0,
            "-":len(ids)
        },
        "BSC":{
            "V":0,
            "X":0,
            "-":len(ids)
        }
    }

    qq = str(event.get_user_id())
    if not_exist_data(qq):
        await plate.send("每天第一次查询自动刷新成绩，可能需要较长时间。若需手动刷新请发送 刷新成绩")
    player_data,success = await read_full_data(qq)
    if success == 400:
        await plate.finish("未找到此玩家，请确登陆https://www.diving-fish.com/maimaidx/prober/ 录入分数，并正确填写用户名与QQ号。")
    
    record_selected = {}
    for rec in player_data['records']:
        if ((str(rec['song_id']) in ids) and (rec['level_index'] != 4)) or ((str(rec['song_id']) in remids) and (rec['level_index'] == 4)):
            tmp = {
                "id":rec['song_id'],
                "level_index": rec['level_index'],
                "ds": rec['ds']
                }
            status[level_index_to_file[rec['level_index']]]["-"] -= 1
            if res[1] in "極极":
                tmp["cover"] = rec['fc']
                if rec['fc'] != "":
                    tmp["finished"] = True
                    status[level_index_to_file[rec['level_index']]]["V"] += 1
                else:
                    tmp["finished"] = False
                    status[level_index_to_file[rec['level_index']]]["X"] += 1
 
            if res[1] == "将":
                tmp["cover"] = rec['rate']
                if rec['achievements'] >= 100:
                    tmp["finished"] = True
                    status[level_index_to_file[rec['level_index']]]["V"] += 1
                else:
                    tmp["finished"] = False
                    status[level_index_to_file[rec['level_index']]]["X"] += 1

            if res[1] == "神":
                tmp["cover"] = rec['fc']
                if rec['fc'][:2] == 'ap':
                    tmp["finished"] = True
                    status[level_index_to_file[rec['level_index']]]["V"] += 1
                else:
                    tmp["finished"] = False
                    status[level_index_to_file[rec['level_index']]]["X"] += 1

            if res[1] == "舞":
                tmp["cover"] = rec['fs']
                if rec['fs'][:3] == 'fsd':
                    tmp["finished"] = True
                    status[level_index_to_file[rec['level_index']]]["V"] += 1
                else:
                    tmp["finished"] = False
                    status[level_index_to_file[rec['level_index']]]["X"] += 1

            if res[1] == "者":
                tmp["cover"] = rec['rate']
                if rec['achievements'] >= 80:
                    tmp["finished"] = True
                    status[level_index_to_file[rec['level_index']]]["V"] += 1
                else:
                    tmp["finished"] = False
                    status[level_index_to_file[rec['level_index']]]["X"] += 1

            record_selected[f"{rec['song_id']}_{rec['level_index']}"] = tmp

    if version != "舞":
        status.pop("MST_Re")

    records = {}
    for id in ids:
        music = total_list.by_id(id)
        lev = music["level"][3]
        if lev not in records:
            records[lev] = []
        if f"{id}_3" in record_selected:
            records[lev].append(record_selected[f"{id}_3"])
        else:
            records[lev].append({
                "id":id,
                "level_index":3,
                "ds": music["ds"][3],
                "cover":"",
                "finished":False
            })
    for id in remids:
        music = total_list.by_id(id)
        lev = music["level"][4]
        if lev not in records:
            records[lev] = []
        if f"{id}_4" in record_selected:
            records[lev].append(record_selected[f"{id}_4"])
        else:
            records[lev].append({
                "id":id,
                "level_index":4,
                "ds": music["ds"][4],
                "cover":"",
                "finished":False
            })

    if version == "舞" and res[3] != "全":
        keys = list(records.keys())
        for key in keys:
            if key not in ["15","14+","14"]:
                records.pop(key)
    
    if res[1] in "極极":
        plate_file = "main_plate/" + platename_to_file[pnconvert[res[0]] + "极"]
    elif res[1] == "将":
        plate_file = "main_plate/" + platename_to_file[pnconvert[res[0]] + "将"]
    elif res[1] == "神":
        plate_file = "main_plate/" + platename_to_file[pnconvert[res[0]] + "神"]
    elif res[1] == "舞":
        plate_file = "main_plate/" + platename_to_file[pnconvert[res[0]] + "舞舞"]
    else:
        plate_file = "main_plate/" + platename_to_file["霸者"]

    dacheng = True
    for diff in status:
        if status[diff]["-"] != 0 or status[diff]["X"] != 0:
            dacheng = False
            break

    queren = True
    for lev in records:
        if lev in ["15","14+","14","13+"]:
            for rec in records[lev]:
                if not rec["finished"]:
                    queren = False
                    break
            if not queren:
                break

    info = {
        "qq": qq,
        "plate": plate_file,
        "status": status,
        "queren": queren,
        "dacheng": dacheng
    }
    img = await draw_final_rank_list(info = info,records = records)

    if img.size[1]>3000:
        b64 = image_to_base64(img,format="JPEG")
    else:
        b64 = image_to_base64(img,format="PNG")

    if version == "舞" and res[3] != "全":
        s = "舞系默认只展示14难度及以上。若需查看全部进度请在查询命令后加上“全”，如“舞将进度全”\n"
    elif version in "熊華":
        s = "请注意，国服熊代与華代成就需一同清谱舞萌DX版本获得\n"
    elif version in "爽煌":
        s = "请注意，国服爽代与煌代成就需一同清谱舞萌DX2021版本获得\n"
    elif version in "宙星":
        s = "请注意，国服宙代与星代成就需一同清谱舞萌DX2022版本获得\n"
    elif version in "祭祝":
        s = "请注意，国服祭代与祝代成就需一同清谱舞萌DX2023版本获得\n"
    elif version in "真" and res[1] == "将":
        s = "真代没有真将，但是我可以假装帮你查\n"
    else:
        s = ""

    s += "您的" + str(event.get_message()) + "为：" + "\n"
    await plate.finish(
        MessageSegment("at", {"qq": qq}) + \
        MessageSegment("text",{"text":s}) + \
        MessageSegment("image",{"file": f"base64://{str(b64, encoding='utf-8')}"}))


refresh_data = on_command("刷新成绩", priority = DEFAULT_PRIORITY, block = True)
@refresh_data.handle()
async def _refresh_data(event: Event, message: Message = CommandArg()):
    qq = str(event.get_user_id())
    data,success = await refresh_player_full_data(qq)
    if success == 0:
        await refresh_data.finish("刷新完成")
    else:
        await refresh_data.finish("未找到此玩家，请确登陆https://www.diving-fish.com/maimaidx/prober/ 录入分数，并正确填写用户名与QQ号。")



levelquery = on_regex(r"^([0-9]+)([＋\+]?)(?:进度|完成表|完成度|定数表)$",priority = DEFAULT_PRIORITY, block = True)
@levelquery.handle()
async def _levelquery(event: Event):
    regex = r"^([0-9]+)([＋\+]?)(?:进度|完成表|完成度|定数表)$"
    res = re.match(regex, str(event.get_message()))
    level = int(res.group(1))
    if (level >= 15) or (level <= 0):
        await levelquery.finish("蓝的盆")
    
    qq = str(event.get_user_id())
    if str(event.get_message()).endswith("定数表"):
        player_data = {
            'records':[]
        }
    else:
        if not_exist_data(qq):
            await levelquery.send("每天第一次查询自动刷新成绩，可能需要较长时间。若需手动刷新请发送 刷新成绩")
        player_data,success = await read_full_data(qq)
        if success == 400:
            await levelquery.finish("未找到此玩家，请确登陆https://www.diving-fish.com/maimaidx/prober/ 录入分数，并正确填写用户名与QQ号。")
    
    plus = res.group(2)
    records = {}
    if plus != "":
        for suffix in [".7",".8",".9"]:
            records[str(level)+suffix] = []
    else:
        for suffix in [".0",".1",".2",".3",".4",".5",".6"]:
            records[str(level)+suffix] = []
    
    record_selected = {}
    for rec in player_data['records']:
        if str(rec['ds']) in records:
            tmp = {
                "id":rec['song_id'],
                "level_index": rec['level_index'],
                "ds": rec['ds']
                }
            if rec['fc'][:2] == 'ap':
                tmp['cover'] = rec['fc']
            else:
                tmp['cover'] = rec['rate']
            if rec['achievements']>=100:
                tmp['finished'] = True
            else:
                tmp['finished'] = False
            record_selected[f"{rec['song_id']}_{rec['level_index']}"] = tmp
            
    for music in music_data:
        if int(music["id"]) >= 100000:
            continue
        for i,ds in enumerate(music['ds']):
            if str(ds) in records:
                if f"{music['id']}_{i}" in record_selected:
                    records[str(ds)].append(record_selected[f"{music['id']}_{i}"])
                else:
                    records[str(ds)].append({
                    "id": music['id'],
                    "level_index": i,
                    "ds": ds,
                    "cover": "",
                    "finished": False
                    })

    plate_file_path = "other_plate/" + random.choice(os.listdir(plate_path + "other_plate"))

    info = {
        "qq": qq,
        "plate": plate_file_path,
        "status":{},
        "queren": False,
        "dacheng": False
    }

    img = await draw_final_rank_list(info = info,records = records)
    
    if img.size[1]>3000:
        b64 = image_to_base64(img,format="JPEG")
    else:
        b64 = image_to_base64(img,format="PNG")

    await levelquery.finish(
        MessageSegment("at", {"qq": qq}) + \
        MessageSegment("text",{"text":"您的" + str(event.get_message()) + "为："}) + \
        MessageSegment("image",{"file": f"base64://{str(b64, encoding='utf-8')}"}))
    

singlequery = on_command("info",priority = DEFAULT_PRIORITY, block = True)
@singlequery.handle()
async def _singlequery(event: Event, message: Message = CommandArg()):
    o_msg = str(message).strip()
    msg = o_msg
    diff = {'绿':0,'黄':1,'红':2,'紫':3,'白':4}
    if msg[0] in diff:
        diff = diff[msg[0]]
        msg = msg[1:]
    else:
        diff = -1
    music1 = None
    music2 = None
    try:
        id = int(msg)
        music2 = total_list.by_id(str(id))
        if music2 == None:
            raise Exception
    except:
        if msg == "":
            await singlequery.finish("请输入正确的查询命令，格式：info+id或info+部分歌名。")
        else:
            res1 = total_list.filt_by_name(title_search=msg)
            res2 = total_list.filt_by_name(title_search=o_msg)
            if len(res1) == len(res2) == 0:
                await singlequery.finish("没有找到这样的乐曲。")

            if len(res1) == 1:
                music1 = res1[0]
            elif len(res1) > 1:
                for i in range(len(res1)):
                    if res1[i]['title'].lower().strip() == msg.lower().strip():
                        music1 = res1[i]
                        break
                if music1 == None:
                    music1 = random.choice(res1)

            if len(res2) == 1:
                music2 = res2[0]
                if music1 != None and (music1.id != music2.id):
                    music1 = music2
                    diff = -1
            elif len(res2) > 1:
                for i in range(len(res2)):
                    if res2[i]['title'].lower().strip() == o_msg.lower().strip():
                        music2 = res2[i]
                        break
                if music2 == None:
                    music2 = random.choice(res2)

    qq = str(event.get_user_id())
    if not_exist_data(qq):
        await singlequery.send("每天第一次查询自动刷新成绩，可能需要较长时间。若需手动刷新请发送 刷新成绩")
    player_data,success = await read_full_data(qq)
    if success == 400:
        await singlequery.finish("未找到此玩家，请确登陆https://www.diving-fish.com/maimaidx/prober/ 录入分数，并正确填写用户名与QQ号。")
    records1 = [{},{},{},{},{}]
    records2 = [{},{},{},{},{}]
    for rec in player_data['records']:
        if music1 != None and rec['song_id'] == int(music1.id):
            records1[rec['level_index']] = rec
        if music2 != None and rec['song_id'] == int(music2.id):
            records2[rec['level_index']] = rec
    if records1 == records2 == [{},{},{},{},{}]:
        if music1 == None:
            title = music2.title
        elif music2 == None:
            title = music1.title
        elif music1.title == music2.title:
            title = music1.title
        else:
            title = music1.title + "或" + music2.title
        await singlequery.finish(f"您查询的是{title}\n没有查到成绩。")
    else:
        imgs = []
        with open("src/static/mai/rgplct.json","r",encoding="utf-8") as f:
            rgplct = json.load(f)
        flag = False
        if qq in rgplct:
            flag = rgplct[qq]
        if diff == -1 or records1[diff] == {}:
            for rec in records2:
                if rec != {}:
                    img = await draw_new_info(rec,music2,plct=flag)
                    imgs.append(img)
        else:
            img = await draw_new_info(records1[diff],music1,plct=flag)
            imgs.append(img)

        width_sum = 5
        for img in imgs:
            width_sum += img.size[0]+5
        final_img = Image.new("RGB",(width_sum,imgs[0].size[1]+10),(255,255,255))
        width_pos = 5
        for img in imgs:
            final_img.paste(img,(width_pos,5),img)
            width_pos += img.size[0]+5
        font_title = ImageFont.truetype("src/static/SourceHanSansCN-Bold.otf", 20,encoding="utf-8")
        img_draw = ImageDraw.Draw(final_img)
        img_draw.text((width_sum-156,5),"Generated By",(0,0,0),font_title)
        img_draw.text((width_sum-156,27),"Range-Bot",(0,0,0),font_title)
        await singlequery.finish(MessageSegment.at(qq)+MessageSegment.image(f"base64://{str(image_to_base64(final_img), encoding='utf-8')}"))

def get_compare_value(record:dict):
    try:
        ds = float(total_list.by_id(record['song_id']).stats[record['level_index']]['fit_diff'])
    except:
        ds = record['ds']
    return ds + max(record['achievements']-100.8,0)


"""------------随机牛逼/随机丢人------------"""
random_niubi = on_command('随机牛逼', priority = DEFAULT_PRIORITY, block = True)
@random_niubi.handle()
async def _random_niubi(event: Event, message: Message = CommandArg()):
    msg = str(message).strip()
    # 判断msg是否为数字
    n = 1
    if msg.isdigit():
        n = int(msg)
        if n<=0 or n>10:
            n = 1

    qq = str(event.get_user_id())
    if not_exist_data(qq):
        await singlequery.send("每天第一次查询自动刷新成绩，可能需要较长时间。若需手动刷新请发送 刷新成绩")
    player_data,success = await read_full_data(qq)
    if success == 400:
        await singlequery.finish("未找到此玩家，请确登陆https://www.diving-fish.com/maimaidx/prober/ 录入分数，并正确填写用户名与QQ号。")

    records = []
    for rec in player_data['records']:
        if rec['achievements'] >= 100.8 and rec['level_index'] >= 3:
            # rec['compare_value'] = get_compare_value(rec)
            records.append(rec)
    # records.sort(key = lambda x:x['compare_value'],reverse = True)
    if len(records) == 0:
        await random_niubi.finish(MessageSegment.at(qq) + MessageSegment.text("您没有很牛逼的成绩，无法随机牛逼。"))
    # records = records[:min(n*10,len(records))]
    draw_list = random.sample(records,min(n,len(records)))
    imgs = []
    for rec in draw_list:
        music = total_list.by_id(rec['song_id'])
        img = await draw_new_info(rec,music)
        imgs.append(img)
    width_sum = 5
    for img in imgs:
        width_sum += img.size[0]+5
    final_img = Image.new("RGB",(width_sum,imgs[0].size[1]+10),(255,255,255))
    width_pos = 5
    for img in imgs:
        final_img.paste(img,(width_pos,5),img)
        width_pos += img.size[0]+5
    font_title = ImageFont.truetype("src/static/SourceHanSansCN-Bold.otf", 20,encoding="utf-8")
    img_draw = ImageDraw.Draw(final_img)
    img_draw.text((width_sum-156,5),"Generated By",(0,0,0),font_title)
    img_draw.text((width_sum-156,27),"Range-Bot",(0,0,0),font_title)
    await random_niubi.finish(MessageSegment.at(qq)+MessageSegment.image(f"base64://{str(image_to_base64(final_img), encoding='utf-8')}"))

random_caibi = on_command('随机菜逼', aliases={'随机丢人'}, priority = DEFAULT_PRIORITY, block = True)
@random_caibi.handle()
async def _random_caibi(event: Event, message: Message = CommandArg()):
    msg = str(message).strip()
    # 判断msg是否为数字
    n = 1
    if msg.isdigit():
        n = int(msg)
        if n<=0 or n>10:
            n = 1

    qq = str(event.get_user_id())
    if not_exist_data(qq):
        await singlequery.send("每天第一次查询自动刷新成绩，可能需要较长时间。若需手动刷新请发送 刷新成绩")
    player_data,success = await read_full_data(qq)
    if success == 400:
        await singlequery.finish("未找到此玩家，请确登陆https://www.diving-fish.com/maimaidx/prober/ 录入分数，并正确填写用户名与QQ号。")

    records = []
    for rec in player_data['records']:
        if rec['achievements'] <97 and rec['level_index'] >= 3:
            # rec['compare_value'] = get_compare_value(rec)
            records.append(rec)
    # records.sort(key = lambda x:x['compare_value'],reverse = True)
    if len(records) == 0:
        await random_caibi.finish(MessageSegment.at(qq) + MessageSegment.text("您没有很菜逼的成绩，无法随机菜逼。"))
    # records = records[:min(n*10,len(records))]
    draw_list = random.sample(records,min(n,len(records)))
    imgs = []
    for rec in draw_list:
        music = total_list.by_id(rec['song_id'])
        img = await draw_new_info(rec,music)
        imgs.append(img)
    width_sum = 5
    for img in imgs:
        width_sum += img.size[0]+5
    final_img = Image.new("RGB",(width_sum,imgs[0].size[1]+10),(255,255,255))
    width_pos = 5
    for img in imgs:
        final_img.paste(img,(width_pos,5),img)
        width_pos += img.size[0]+5
    font_title = ImageFont.truetype("src/static/SourceHanSansCN-Bold.otf", 20,encoding="utf-8")
    img_draw = ImageDraw.Draw(final_img)
    img_draw.text((width_sum-156,5),"Generated By",(0,0,0),font_title)
    img_draw.text((width_sum-156,27),"Range-Bot",(0,0,0),font_title)
    await random_caibi.finish(MessageSegment.at(qq)+MessageSegment.image(f"base64://{str(image_to_base64(final_img), encoding='utf-8')}"))






"""-----------------随n个x-----------------"""
rand_n = on_regex(r"^随[0-9]+[个|首][绿黄红紫白]?[0-9]+[＋\+]?", priority = DEFAULT_PRIORITY, block = True)
@rand_n.handle()
async def _rand_n(event: Event):
    pattern = r"^随([0-9]+)[个|首]([绿黄红紫白]?)([0-9]+)([＋\+]?)(.*)"
    temp_dict = {
        '绿': 0,
        '黄': 1,
        '红': 2,
        '紫': 3,
        '白': 4
    }
    re_temp_list = ['绿','黄','红','紫','白']
    msg = ""
    res = re.match(pattern, str(event.get_message()))
    n = int(res.group(1))
    diff = res.group(2)
    if diff != '':
        diff = temp_dict[diff]
    level = int(res.group(3))
    if res.group(4) != '':
        if level < 7:
            msg += "7以下没有+\n"
            plus = ''
        else:
            plus = '+'
    else:
        plus = ''
    if n==0 or n>30 or level==0 or level>15:
        dirlist = os.listdir(long_dir_)
        a = random.randint(0,len(dirlist)-1)
        with open(long_dir_ + dirlist[a],"rb")as fp:
            encoded = base64.b64encode(fp.read())
        url = "base64://" + encoded.decode('utf-8')
        await rand_n.finish(MessageSegment.image(url))
    else:
        l = []
        condition = res.group(5).strip()
        paichu_list = []
        if condition[:2] == "不要":
            for c in condition[2:]:
                if c in ptv:
                    paichu_list.append(ptv[c])
                elif c == '真':
                    paichu_list.append(ptv['真1'])
                    paichu_list.append(ptv['真2'])
                else:
                    paichu_list = []
                    break
        elif condition[:2] == "只要":
            paichu_list = versionlist.copy()
            for c in condition[2:]:
                if (c in ptv) and (ptv[c] in paichu_list):
                    paichu_list.remove(ptv[c])
                elif (c == '真') and (ptv['真1'] in paichu_list) and (ptv['真2'] in paichu_list):
                    paichu_list.remove(ptv['真1'])
                    paichu_list.remove(ptv['真2'])
                else:
                    paichu_list = []
                    break
        for music in music_data:
            for i,lv in enumerate(music["level"]):
                if (lv == str(level)+plus)and((diff=='')or(diff==i))and(music['cn_version'] not in paichu_list):
                    l.append(f"{re_temp_list[i]}【{music['id']}】{music['title']}")
        if len(l) == 0:
            dirlist = os.listdir(long_dir_)
            a = random.randint(0,len(dirlist)-1)
            with open(long_dir_ + dirlist[a],"rb")as fp:
                encoded = base64.b64encode(fp.read())
            url = "base64://" + encoded.decode('utf-8')
            await rand_n.finish(MessageSegment.image(url))
        elif len(l) < n:
            msg += "满足条件的谱面只有" + str(len(l)) + "个\n"
            for i in range(len(l)):
                msg += l[i] + "\n"
        else:
            for i in range(n):
                a = random.randint(0,len(l)-1)
                msg += l[a] + "\n"
                l.pop(a)
        await rand_n.finish(msg)

"""-----------------分数列表-----------------"""
fslb = on_regex(r"^([0-9]+)([＋\+]?)分数列?表([1-9]?)$", priority = DEFAULT_PRIORITY, block = True)
@fslb.handle()
async def _fslb(event: Event):
    pattern = r"^([0-9]+)([＋\+]?)分数列?表([1-9]?)$"
    res = re.match(pattern, str(event.get_message()))
    level = int(res.group(1))
    if (level > 15) | (level < 1) :
        return
    if res.group(2) == '':
        ds_l = level
        ds_h = level + 0.6
    else:
        ds_l = level + 0.7
        ds_h = level + 0.9
    qq = str(event.get_user_id())
    if not_exist_data(qq):
        await fslb.send("每天第一次查询自动刷新成绩，可能需要较长时间。若需手动刷新请发送 刷新成绩")
    player_data,success = await read_full_data(qq)
    if success == 400:
        await fslb.finish("未找到此玩家，请确登陆https://www.diving-fish.com/maimaidx/prober/ 录入分数，并正确填写用户名与QQ号。")
    querylist = []
    for song in player_data['records']:
        if song['ds'] >= ds_l and song['ds'] <= ds_h:
            querylist.append(song)
    if len(querylist) == 0:
        await fslb.finish("您还没有打过这个定数的谱面")
    querylist.sort(key = lambda x:x["achievements"],reverse=True)
    leveldict = ["绿","黄","红","紫","白"]
    s = f"""您的{res.group(1)}{res.group(2)}分数列表为:"""
    if res.group(3) == '':
        page = 1
    else:
        page = int(res.group(3))
    if (page-1)*100>len(querylist)-1:
        page = int(len(querylist)/100-0.01)+1
    maxpage = int(len(querylist)/100-0.01)+1
    querylist = querylist[(page-1)*100:page*100]

    for i,song in enumerate(querylist):
        addstr = ""
        if song['fc']:
            addstr += f"({song['fc']})"
        if song['fs']:
            addstr += f"({song['fs']})"
        s += f"""
{((page-1)*100 + i+1):>3}:【ID:{song['song_id']:>5}】{song['achievements']:>8.4f}% ({song['type']})({leveldict[song['level_index']]}) {song['title']}{addstr}"""
    s += f"""
第{page}页，共{maxpage}页"""
    await fslb.finish(MessageSegment.image(f"base64://{str(image_to_base64(text_to_image(s)), encoding='utf-8')}"))

"""-----------------别名增删查----------------"""
select_alias_vip = on_command("别名", priority = DEFAULT_PRIORITY, block = True, rule = maiqun_checker)
@select_alias_vip.handle()
async def _select_alias_vip(event: Event, message: Message = CommandArg()):
    msg = str(message).strip().split(" ")
    if len(msg) == 1 and msg[0] != "":
        id = msg[0]
        with open("src/static/all_alias_temp.json", "r", encoding='utf-8') as fp:
            alias_data = json.load(fp)
        if id not in alias_data:
            await select_alias_vip.finish("未找到该乐曲，请直接输入乐曲id。")
        else:
            s = f"{id}. {alias_data[id]['Name']}的别名有：\n"
            for i in range(len(alias_data[id]['Alias'])):
                if alias_data[id]['Alias'][i] != total_list.by_id(id)['title']:
                    s += f"{alias_data[id]['Alias'][i]}\n"
            await select_alias_vip.finish(s)
    elif len(msg) == 3:
        qq = str(event.get_user_id())
        id = msg[1]
        with open("src/static/all_alias_temp.json", "r", encoding='utf-8') as fp:
            alias_data = json.load(fp)
        if id not in alias_data:
            await select_alias_vip.finish("未找到该乐曲，请直接输入乐曲id。")
        else:
            if ("增" in msg[0]) or ("加" in msg[0]):
                if msg[2] in alias_data[id]["Alias"]:
                    await select_alias_vip.finish("该别名已存在。")
                else:
                    with open("src/static/alias_pre_process_add.json", "r", encoding='utf-8') as fp:
                        alias_pre_process_add = json.load(fp)
                    if id in alias_pre_process_add:
                        alias_pre_process_add[id].append(msg[2])
                    else:
                        alias_pre_process_add[id] = [msg[2]]
                    with open("src/static/alias_pre_process_add.json", "w", encoding='utf-8') as fp:
                        json.dump(alias_pre_process_add, fp, ensure_ascii=False, indent=4)
                    with open("src/static/alias_pre_process_remove.json", "r", encoding='utf-8') as fp:
                        alias_pre_process_remove = json.load(fp)
                    if id in alias_pre_process_remove:
                        if msg[2] in alias_pre_process_remove[id]:
                            alias_pre_process_remove[id].remove(msg[2])
                    with open("src/static/alias_pre_process_remove.json", "w", encoding='utf-8') as fp:
                        json.dump(alias_pre_process_remove, fp, ensure_ascii=False, indent=4)
                    with open("src/static/alias_log.csv", "a", encoding='utf-8') as fp:
                        fp.write(f"{qq},{','.join(msg)}\n")
                    if refresh_alias_temp():
                        await select_alias_vip.finish(f"添加成功。\n已为 {id}.{alias_data[id]['Name']} 添加别名：\n{msg[2]}")
            elif ("删" in msg[0]) or ("减" in msg[0]):
                if msg[2] not in alias_data[id]["Alias"]:
                    await select_alias_vip.finish("该别名不存在。")
                else:
                    with open("src/static/alias_pre_process_remove.json", "r", encoding='utf-8') as fp:
                        alias_pre_process_remove = json.load(fp)
                    if id in alias_pre_process_remove:
                        alias_pre_process_remove[id].append(msg[2])
                    else:
                        alias_pre_process_remove[id] = [msg[2]]
                    with open("src/static/alias_pre_process_remove.json", "w", encoding='utf-8') as fp:
                        json.dump(alias_pre_process_remove, fp, ensure_ascii=False, indent=4)
                    with open("src/static/alias_pre_process_add.json", "r", encoding='utf-8') as fp:
                        alias_pre_process_add = json.load(fp)
                    if id in alias_pre_process_add:
                        if msg[2] in alias_pre_process_add[id]:
                            alias_pre_process_add[id].remove(msg[2])
                    with open("src/static/alias_pre_process_add.json", "w", encoding='utf-8') as fp:
                        json.dump(alias_pre_process_add, fp, ensure_ascii=False, indent=4)
                    with open("src/static/alias_log.csv", "a", encoding='utf-8') as fp:
                        fp.write(f"{qq},{','.join(msg)}\n")
                    if refresh_alias_temp():
                        await select_alias_vip.finish("删除成功")
            else:
                await select_alias_vip.finish('输入格式错误。\n查别名请输入“别名 id”\n增加别名请输入“别名 增 id 别名”\n删除别名请输入“别名 删 id 别名”')

    else:
        await select_alias_vip.finish('输入格式错误。\n查别名请输入“别名 id”\n增加别名请输入“别名 增 id 别名”\n删除别名请输入“别名 删 id 别名”\n')

"""-----------------有什么别名----------------"""
select_alias = on_regex(r"^([0-9]+)有什么别名$", priority = DEFAULT_PRIORITY, block = True)
@select_alias.handle()
async def _select_alias(event: Event):
    msg = str(event.get_message()).strip()
    pattern = r"^([0-9]+)有什么别名$"
    res = re.match(pattern, msg)
    id = str(int(res.group(1)))
    with open("src/static/all_alias_temp.json", "r", encoding='utf-8') as fp:
        alias_data = json.load(fp)
    if id not in alias_data:
        await select_alias.finish("未找到该乐曲，输入乐曲id。")
    else:
        s = f"{id}. {alias_data[id]['Name']}的别名有：\n"
        for i in range(1, len(alias_data[id]['Alias'])):
            s += f"{alias_data[id]['Alias'][i]}\n"
        await select_alias.finish(s)


"""-----------------apb50----------------"""
apb50 = on_command("apb50", priority = DEFAULT_PRIORITY, block = True)
@apb50.handle()
async def _apb50(event: Event, message: Message = CommandArg()):
    username = str(message).strip()
    if username == "":
        qq = str(event.get_user_id())
        if not_exist_data(qq):
            await apb50.send("每天第一次查询自动刷新成绩，可能需要较长时间。若需手动刷新请发送 刷新成绩")
        player_data,success = await read_full_data(qq)
        if success == 400:
            await apb50.finish("未找到此玩家，请确登陆https://www.diving-fish.com/maimaidx/prober/ 录入分数，并正确填写用户名与QQ号。")
    else:
        qq = '0'
        player_data,success = await get_full_data_by_username(username)
        if success == 400:
            await apb50.finish("未找到此玩家")
        elif success == 403:
            await apb50.finish("该用户禁止了其他人获取数据。")
    img = await generateap50(player_data,qq)
    await apb50.finish(MessageSegment.image(f"base64://{str(image_to_base64(img), encoding='utf-8')}"))



"""-----------------b50水分检测----------------"""
b50_water = on_command('b50水分检测', priority = DEFAULT_PRIORITY - 1, block = True)
@b50_water.handle()
async def _b50_water(event: Event, message: Message = CommandArg()):
    s = str(message).strip()
    if s != "":
        return
    
    qq = str(event.get_user_id())
    if not_exist_data(qq):
        await b50_water.send("每天第一次查询自动刷新成绩，可能需要较长时间。若需手动刷新请发送 刷新成绩")
    player_data,success = await read_full_data(qq)
    if success == 400:
        await b50_water.finish("未找到此玩家，请确登陆https://www.diving-fish.com/maimaidx/prober/ 录入分数，并正确填写用户名与QQ号。")
    msg = "\n"
    msg += "本功能根据拟合定数进行计算，仅供娱乐，不具有任何参考价值，请勿上纲上线！\n下图为您b50的含水图\n"
    img,msg2 = await generateb50_water_msg(player_data,qq)
    await b50_water.finish(MessageSegment.at(qq) + MessageSegment.text(msg) + MessageSegment.image(f"base64://{str(image_to_base64(img), encoding='utf-8')}") + MessageSegment.text(msg2))
    
"""-----------------b50娱乐版----------------"""
b50_yuleban = on_command('b50娱乐版', priority = DEFAULT_PRIORITY - 1, block = True)
@b50_yuleban.handle()
async def _b50_yuleban(event: Event, message: Message = CommandArg()):
    s = str(message).strip()
    qq = str(event.get_user_id())
    if s != "":
        if type(re.match("group_(.+)_(.+)",event.get_session_id())) != re.Match:
            return
        else:
            groupid = str(re.match("group_(.+)_(.+)",event.get_session_id()).groups()[0])
        if groupid not in MAIN_GROUPS:
            return
        else:
            try:
                qq = int(s)
                player_data,success = await read_full_data(qq)
            except:
                player_data,success = await read_full_data(qq='0',username=s)
    else:
        if not_exist_data(qq):
            await b50_yuleban.send("每天第一次查询自动刷新成绩，可能需要较长时间。若需手动刷新请发送 刷新成绩")
        player_data,success = await read_full_data(qq)
    if success == 400:
        await b50_yuleban.finish("未找到此玩家，请确登陆https://www.diving-fish.com/maimaidx/prober/ 录入分数，并正确填写用户名与QQ号。")
    elif success == 403:
        await b50_yuleban.finish("该用户禁止了其他人获取数据。")
    for song in player_data['records']:
        fitds = 0
        try:
            fitds = round(total_list.by_id(song['song_id']).stats[song['level_index']]['fit_diff'],2)
        except:
            pass
        if fitds != 0:
            song['ds'] = fitds
    msg = "\n"
    msg += "本功能根据拟合定数进行计算，仅供娱乐，不具有任何参考价值，请勿上纲上线！\n下图为您b50的娱乐版\n（部分定数的小数保留一位的歌曲为没有足够的数据生成拟合定数的歌曲）\n"
    if s != "":
        img = await generateb50_by_player_data(player_data,qq='0',yule=True)
    else:
        img = await generateb50_by_player_data(player_data,qq=qq,yule=True)
    await b50_yuleban.finish(MessageSegment.at(qq) + MessageSegment.text(msg) + MessageSegment.image(f"base64://{str(image_to_base64(img), encoding='utf-8')}"))