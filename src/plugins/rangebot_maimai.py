from nonebot import on_command, on_regex
from nonebot.params import CommandArg
from nonebot.adapters import Event
from nonebot.adapters.onebot.v11 import Message, MessageSegment

from src.libraries.tool import offlineinit, convert_cn2jp
from src.libraries.maimaidx_music import *
from src.libraries.image import *
from src.libraries.maimai_best_40 import generate
from src.libraries.maimai_best_50 import generate50
from src.libraries.maimai_plate_query import *
from src.libraries.secrets import range_checker,dajiang_checker, maiqun_checker
from src.libraries.maimai_info import draw_new_info
from src.libraries.message_segment import *

from PIL import Image, ImageDraw, ImageFont
import re,base64,random

cover_dir = 'src/static/mai/cover/'
long_dir_ = 'src/static/long/'

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

find_song = on_regex(r".+是什么歌", rule = dajiang_checker, priority = 10, block = True)

@find_song.handle()
async def _(event: Event):
    regex = "(.+)是什么歌"
    name = re.match(regex, str(event.get_message())).groups()[0].strip()
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


"""-----------谱师查歌&曲师查歌&新歌查歌&BPM查歌&版本查歌-----------"""
hardlist = ['Basic','Advance','Expert','Master','Re:Master']

charter_search = on_command('谱师查歌', priority = 10, block = True)
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


artist_search = on_command('曲师查歌', priority = 10, block = True)
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

new_search = on_command('新歌查歌', priority = 10, block = True)
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

bpm_search = on_command('bpm查歌' , aliases={"BPM查歌","Bpm查歌"}, priority = 10, block = True)
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


"""-----------不知道两个oncommand能不能分配给一个handle所以先放在这里--------"""
range_best_40_pic = on_command('range b40', priority = 10, block = True)
@range_best_40_pic.handle()
async def _(event: Event, message: Message = CommandArg()):
    username = str(message).strip()
    if username == "":
        payload = {'qq': str(event.get_user_id())}
    else:
        payload = {'username': username}
    img, success = await generate(payload)
    if success == 400:
        await range_best_40_pic.finish("未找到此玩家，请确登陆https://www.diving-fish.com/maimaidx/prober/录入分数，并正确填写用户名与QQ号。")
    elif success == 403:
        await range_best_40_pic.finish("该用户禁止了其他人获取数据。")
    else:
        await range_best_40_pic.finish(MessageSegment.image(f"base64://{str(image_to_base64(img), encoding='utf-8')}"))


range_best_50_pic = on_command('range b50', priority = 10, block = True)
@range_best_50_pic.handle()
async def _(event: Event, message: Message = CommandArg()):
    username = str(message).strip()
    if username == "":
        payload = {'qq': str(event.get_user_id()),'b50':True}
    else:
        payload = {'username': username,'b50':True}
    img, success = await generate50(payload)
    if success == 400:
        await range_best_50_pic.finish("未找到此玩家，请确登陆https://www.diving-fish.com/maimaidx/prober/录入分数，并正确填写用户名与QQ号。")
    elif success == 403:
        await range_best_50_pic.finish("该用户禁止了其他人获取数据。")
    else:
        await range_best_50_pic.finish(MessageSegment.image(f"base64://{str(image_to_base64(img), encoding='utf-8')}"))

update_music_data = on_command("更新歌曲列表", priority = 5, block = True, rule = range_checker)
@update_music_data.handle()
async def _update_music_data(event: Event, message: Message = CommandArg()):
    status,strr = await offlineinit()
    if status == 1:
        global total_list, music_data, alias_data
        total_list, music_data, alias_data = refresh_music_list()
        await update_music_data.finish(strr)
    else:
        await update_music_data.finish(strr)
    


ptv = {
        '真1': 'maimai',
        '真2': 'maimai PLUS',
        '超': 'maimai GreeN',
        '檄': 'maimai GreeN PLUS',
        '橙': 'maimai ORANGE',
        '暁': 'maimai ORANGE PLUS',
        '晓': 'maimai ORANGE PLUS',
        '桃': 'maimai PiNK',
        '櫻': 'maimai PiNK PLUS',
        '樱': 'maimai PiNK PLUS',
        '紫': 'maimai MURASAKi',
        '菫': 'maimai MURASAKi PLUS',
        '堇': 'maimai MURASAKi PLUS',
        '白': 'maimai MiLK',
        '雪': 'MiLK PLUS',
        '輝': 'maimai FiNALE',
        '辉': 'maimai FiNALE',
        '熊': 'maimai でらっくす',
        '華': 'maimai でらっくす PLUS',
        '华': 'maimai でらっくす PLUS',
        '爽': 'maimai でらっくす Splash',
        '煌': 'maimai でらっくす Splash PLUS',
        '宙': 'maimai でらっくす UNiVERSE',
        '星': 'maimai でらっくす UNiVERSE PLUS',
        '祭': 'maimai でらっくす FESTiVAL',
        '祝': 'maimai でらっくす FESTiVAL PLUS',
}

versionlist = ['maimai','maimai PLUS','maimai GreeN','maimai GreeN PLUS','maimai ORANGE','maimai ORANGE PLUS','maimai PiNK','maimai PiNK PLUS','maimai MURASAKi','maimai MURASAKi PLUS','maimai MiLK','MiLK PLUS','maimai FiNALE','maimai でらっくす','maimai でらっくす PLUS','maimai でらっくす Splash','maimai でらっくす Splash PLUS','maimai でらっくす UNiVERSE','maimai でらっくす UNiVERSE PLUS','maimai でらっくす FESTiVAL','maimai でらっくす FESTiVAL PLUS']

version_search = on_command('版本查歌', priority = 10, block = True)
@version_search.handle()
async def _(event: Event, message: Message = CommandArg()):
    input = str(message).strip()
    input2 = ''
    if input in ptv:
        input = ptv[input]
    elif input in versionlist:
        pass
    elif input == '真':
        input = 'maimai'
        input2 = 'maimai PLUS'
    else:
        await version_search.finish("未找到该版本，请检查输入")
    k=0
    s = """ 结果如下

 """
    for i in range(0,len(music_data)):
        if (input == music_data[i]['basic_info']['from']) or (input2 == music_data[i]['basic_info']['from']):
            k += 1
            s += ('No.' + str(k) + ' ' + '[' + music_data[i]['id'] + ']' + '. ' + music_data[i]['title'] + "【紫谱定数：" + str(music_data[i]['ds'][3]) + "】")
            s += """
 """
    await version_search.finish(MessageSegment.image(f"base64://{str(image_to_base64(text_to_image(s)), encoding='utf-8')}"))

pnconvert = {
    '真': '真',
    '超': '超',
    '檄': '檄',
    '橙': '橙',
    '暁': '暁',
    '晓': '暁',
    '桃': '桃',
    '櫻': '櫻',
    '樱': '櫻',
    '紫': '紫',
    '菫': '堇',
    '堇': '堇',
    '白': '白',
    '雪': '雪',
    '輝': '輝',
    '辉': '輝',
    '熊': '熊',
    '華': '華',
    '华': '華',
    '爽': '爽',
    '煌': '煌',
    '舞': '舞',
    '霸': '霸',
    '覇': '霸',
    '極': '極',
    '极': '極',
    '将': '将',
    '舞': '舞',
    '舞舞': '舞舞',
    '神': '神',
    '者': '者',
    '宙': '宙',
    '星': '星',
    '祭': '祭',
    '祝': '祝',
}       


plate = on_regex(r'^([真超檄橙暁晓桃櫻樱紫菫堇白雪輝辉熊華华爽煌舞霸宙星祭祝])([極极将舞神者]舞?)(?:进度|完成表|完成度)\s?(.+)?', priority = 10, block = True)
@plate.handle()
async def _plate(event: Event):
    regex = "([真超檄橙暁晓桃櫻樱紫菫堇白雪輝辉熊華华爽煌舞霸宙星祭祝])([極极将舞神者]舞?)(?:进度|完成表|完成度)\s?(.+)?"
    res = re.match(regex, str(event.get_message()).lower())
    platename = list(res.groups()[:2])
    platename[0] = pnconvert[platename[0]]
    platename[1] = pnconvert[platename[1]]
    #diffs = 'Basic Advanced Expert Master Re:Master'.split(' ')
    #combo_rank = 'fc fcp ap app'.split(' ')
    #sync_rank = 'fs fsp fsd fsdp'.split(' ')
    flag = 1    
    qq = str(event.get_user_id())
    payload = {'qq': qq}
    if f'{platename[0]}{platename[1]}' == '真将':
        await plate.send(f"真代没有真将，但是我可以帮你查")
    elif (platename[0] == '霸') ^ (platename[1] == '者'):
        await plate.finish("¿")
    elif  f'{platename[0]}{platename[1]}' == '舞神':
        await plate.send(f"你也要参加合成大舞神？")
    if platename[0] in ['舞', '霸']:
        payload['version'] = [ptv['真1'], ptv['真2'], ptv['超'], ptv['檄'], ptv['橙'], ptv['暁'], ptv['桃'], ptv['櫻'], ptv['紫'], ptv['菫'], ptv['白'], ptv['雪'], ptv['輝']]
        if res.groups()[2] != "全":
            flag = 0
            await plate.send("舞系查询默认只展示14难度及以上。若需查看全部进度请在查询命令后加上“全”，如“舞将进度全”")
        else:
            flag = 2
    elif platename[0] in ['真']:
        payload['version'] = [ptv['真1'], ptv['真2']]
    elif platename[0] in ['熊','華']:
        await plate.send("请注意，国服熊代与華代成就需一同清谱获得")
        payload['version'] = [ptv['熊'], ptv['華']]
    elif platename[0] in ['爽','煌']:
        await plate.send("请注意，国服爽代与煌代成就需一同清谱获得")
        payload['version'] = [ptv['爽'], ptv['煌']]
    else:
        payload['version'] = [ptv[platename[0]]]
    player_data, success = await get_player_plate(payload)
    if success == 400:
        await plate.finish("未找到此玩家，请确登陆https://www.diving-fish.com/maimaidx/prober/ 录入分数，并正确填写用户名与QQ号。")
    elif success == 403:
        await plate.finish("该用户禁止了其他人获取数据。")
    else:
        song_played = {}
        for song in player_data['verlist']:
            song_played[str(song["id"])+'l'+str(song["level_index"])] = {
                "achievements": song["achievements"],
                "fc": song["fc"],
                "fs": song["fs"],
                "level": song["level"]
            }         
        searchlist = []
        diffcount = {
            "15":0,
            "14+":0,
            "14":0,
            "13+":0,
            "13":0,
            "12+":0,
            "12":0,
            "11+":0,
            "11":0,
            "10+":0,
            "10":0,
            "9+":0,
            "9":0,
            "8+":0
            }
        if platename[0] in ['舞', '霸']:
            if flag:
                for song in music_data:
                    if song["basic_info"]["from"] in payload['version']:
                        chartinfo = [song["id"],song["level"][3],3]
                        searchlist.append(chartinfo)
                        diffcount[song["level"][3]]+=1
                        if len(song["level"]) == 5:
                            chartinfo = [song["id"],song["level"][4],4]
                            searchlist.append(chartinfo)
                            diffcount[song["level"][4]]+=1
            else:
                for song in music_data:
                    if song["basic_info"]["from"] in payload['version']:
                        chartinfo = [song["id"],song["level"][3],3]
                        if song["level"][3] in ["15","14+","14"]:
                            searchlist.append(chartinfo)
                            diffcount[song["level"][3]]+=1
                        if len(song["level"]) == 5:
                            chartinfo = [song["id"],song["level"][4],4]
                            if song["level"][4] in ["15","14+","14"]:
                                searchlist.append(chartinfo)
                                diffcount[song["level"][4]]+=1
        else:
            for song in music_data:
                if song["basic_info"]["from"] in payload['version']:
                    chartinfo = [song["id"],song["level"][3],3]
                    searchlist.append(chartinfo)
                    diffcount[song["level"][3]]+=1
        searchlist.sort(key = lambda x:x[1],reverse=True)
        platename = platename[0] + platename[1]
        print(platename)
        img = await querydraw(song_played,searchlist,diffcount,platename,qq,flag)
        await plate.finish(
            MessageSegment("at", {"qq": qq}) + \
            MessageSegment("text",{"text":"您的" + str(event.get_message()) + "为："}) + \
            MessageSegment("image",{"file": f"base64://{str(image_to_base64(img), encoding='utf-8')}"}))


refresh_data = on_command("刷新成绩", priority = 10, block = True)
@refresh_data.handle()
async def _refresh_data(event: Event, message: Message = CommandArg()):
    qq = str(event.get_user_id())
    data,success = await refresh_player_full_data(qq)
    if success == 0:
        await refresh_data.finish("刷新完成")
    else:
        await refresh_data.finish("未找到此玩家，请确登陆https://www.diving-fish.com/maimaidx/prober/ 录入分数，并正确填写用户名与QQ号。")



levelquery = on_regex(r"^([0-9]+)([＋\+]?)进度$",priority = 10, block = True)
@levelquery.handle()
async def _levelquery(event: Event):
    regex = r"^([0-9]+)([＋\+]?)进度$"
    res = re.match(regex, str(event.get_message()))
    level = res.group(1)
    if (int(level) > 15) | (int(level) < 1) :
        return
        await levelquery.finish("别搞了，我最近忙得很没空改bot，有问题跟我说一下就行，别像有人一天天在群里测来测去的测你*呢，想测不会自己开个去玩吗，再测ban了")
    plus = res.group(2)
    if plus != "":
        plus = "+"
    if level + plus == "15+":
        return
        await levelquery.finish("别搞了，我最近忙得很没空改bot，有问题跟我说一下就行，别像有人一天天在群里测来测去的测你*呢，想测不会自己开个去玩吗，再测ban了")
    qq = str(event.get_user_id())
    if not_exist_data(qq):
        await levelquery.send("每天第一次查询自动刷新成绩，可能需要较长时间。若需手动刷新成绩请发送“刷新成绩”")
    player_data,success = await read_full_data(qq)
    if success == 400:
        await levelquery.finish("未找到此玩家，请确登陆https://www.diving-fish.com/maimaidx/prober/ 录入分数，并正确填写用户名与QQ号。")
    song_played = {}
    for song in player_data['records']:
        song_played[str(song["song_id"])+'l'+str(song["level_index"])] = {
            "achievements": song["achievements"],
            "fc": song["fc"],
            "fs": song["fs"],
            "ds": song["ds"]
        }
    searchlist = []
    diffcount = {}
    if int(level) >=7:
        if plus == "":
            pythonsb = [".6",".5",".4",".3",".2",".1",".0"]
            for sb in pythonsb:
                diffcount[level+sb] = 0
        else:
            plus =="+"
            pythonsb = [".9",".8",".7"]
            for sb in pythonsb:
                diffcount[level+sb] = 0
    else:
        if plus != "":
            await levelquery.send("7以下没有+")
        pythonsb = [".9",".8",".7",".6",".5",".4",".3",".2",".1",".0"]
        for sb in pythonsb:
            diffcount[level+sb] = 0
    for song in music_data:
        for i in range(len(song["ds"])):
            if song["level"][i] == level+plus:
                chartinfo = [song["id"],song["ds"][i],i]
                searchlist.append(chartinfo)
                diffcount[str(song["ds"][i])]+=1
    searchlist.sort(key = lambda x:x[1],reverse=True)
    img = await querydraw(song_played,searchlist,diffcount,"霸者",qq)#level+plus)
    await levelquery.finish(
        MessageSegment("at", {"qq": qq}) + \
        #MessageSegment("text",{"text":"您的" + str(event.get_message()) + "为："}) + \
        MessageSegment("image",{"file": f"base64://{str(image_to_base64(img), encoding='utf-8')}"}))



singlequery = on_command("info",priority = 10, block = True)
@singlequery.handle()
async def _singlequery(event: Event, message: Message = CommandArg()):
    msg = str(message).strip()
    music = None
    try:
        id = int(msg)
        music = total_list.by_id(str(id))
        if music == None:
            raise Exception
    except:
        if msg == "":
            await singlequery.finish("请输入正确的查询命令，格式：info+id或info+部分歌名。")
        else:
            name = msg
            res = total_list.filt_by_name(title_search=name)
            if len(res) == 0:
                await singlequery.finish("没有找到这样的乐曲。")
            elif len(res) == 1:
                music = res[0]
            else:
                for i in range(len(res)):
                    if res[i]['title'].lower().strip() == name.lower().strip():
                        music = res[i]
                        break
                if music == None:
                    music = random.choice(res)
    id = int(music.id)
    
    qq = str(event.get_user_id())
    if not_exist_data(qq):
        await singlequery.send("每天第一次查询自动刷新成绩，可能需要较长时间。若需手动刷新成绩请发送“刷新成绩”")
    player_data,success = await read_full_data(qq)
    if success == 400:
        await singlequery.finish("未找到此玩家，请确登陆https://www.diving-fish.com/maimaidx/prober/ 录入分数，并正确填写用户名与QQ号。")
    records = [{},{},{},{},{}]
    for rec in player_data['records']:
        if rec['song_id'] == id:
            records[4-rec['level_index']] = rec
    if records == [{},{},{},{},{}]:
        await singlequery.finish(f"您查询的是{music.title}\n您还没有打过这首歌")
    else:
        imgs = []
        for rec in records:
            if rec == {}:
                continue
            else:
                img = await draw_new_info(rec,music)
                imgs.append(img)
        width_sum = 5
        imgs.reverse()
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



"""-----------old info-----------"""
    # img = Image.open("src/static/platequery/bginfo.png").convert('RGBA')
    # cover = get_music_cover(id)
    # cover = cover.resize((200,200))
    # img.paste(cover,(60,90))
    # if musictype == "DX":
    #     icon = Image.open("src/static/platequery/DX.png").convert('RGBA')
    # else:
    #     icon = Image.open("src/static/platequery/SD.png").convert('RGBA')
    # img.paste(icon,(50,50),mask=icon.split()[3])
    # draw = ImageDraw.Draw(img)
    # font = ImageFont.truetype("src/static/msyh.ttc", 37, encoding='utf-8')
    # y = 40
    # info_to_file_dict = {
    #     "sssp": "SSSp",
    #     "sss": "SSS",
    #     "ssp": "SSp",
    #     "ss": "SS",
    #     "sp": "Sp",
    #     "s": "S",
    #     "aaa": "AAA",
    #     "aa": "AA",
    #     "a": "A",
    #     "bbb": "BBB",
    #     "bb": "BB",
    #     "b": "B",
    #     "c": "C",
    #     "d": "D",
    #     "fc": "FC",
    #     "fcp": "FCp",
    #     "ap": "AP",
    #     "app": "APp",
    #     "fs": "FS",
    #     "fsp": "FSp",
    #     "fsd": "FSD",
    #     "fsdp": "FSDp"
    # }
    # for rec in records:
    #     if rec != {}:
    #         #draw dxstars
    #         x = 330
    #         dx_max = sum(music['charts'][rec['level_index']]['notes'])*3
    #         if rec['dxScore']/dx_max > 0.99:
    #             stars = 6
    #         elif rec['dxScore']/dx_max > 0.97:
    #             stars = 5
    #         elif rec['dxScore']/dx_max > 0.95:
    #             stars = 4
    #         elif rec['dxScore']/dx_max > 0.93:
    #             stars = 3
    #         elif rec['dxScore']/dx_max > 0.90:
    #             stars = 2
    #         elif rec['dxScore']/dx_max > 0.85:
    #             stars = 1
    #         else:
    #             stars = 0
    #         for i in range(stars):
    #             star = Image.open(f"src/static/platequery/stars_{stars}.png").convert('RGBA')
    #             img.paste(star,(x+40*i,y+16),mask=star.split()[3])
    #         #draw achievement
    #         x = 335
    #         offset=22
    #         if rec['achievements']<10:
    #             x=x+offset*2
    #         elif rec['achievements']<100:
    #             x=x+offset
    #         achi = "%.4f" % rec['achievements'] + "%"
    #         y=y+4
    #         draw.text((x-1,y+4),achi,(0,0,0),font)
    #         draw.text((x-1,y+6),achi,(0,0,0),font)
    #         draw.text((x+1,y+4),achi,(0,0,0),font)
    #         draw.text((x+1,y+6),achi,(0,0,0),font)
    #         draw.text((x,y+5),achi,(255,255,255),font)
    #         #draw others
    #         y=y-4
    #         x=345

    #         rate = Image.open("src/static/mai/pic/UI_GAM_Rank_" + info_to_file_dict[rec["rate"]] + ".png").convert('RGBA')
    #         img.paste(rate,(x+185,y+12),mask=rate.split()[3])
    #         if rec["fs"] != "":
    #             fs = Image.open("src/static/mai/pic/UI_MSS_MBase_Icon_" + info_to_file_dict[rec["fs"]] + ".png").convert('RGBA')
    #             img.paste(fs,(x+283,y+12),mask=fs.split()[3])
    #         if rec["fc"] != "":
    #             fc = Image.open("src/static/mai/pic/UI_MSS_MBase_Icon_" + info_to_file_dict[rec["fc"]] + ".png").convert('RGBA')
    #             img.paste(fc,(x+328,y+12),mask=fc.split()[3])
    #     y = y + 60
    # font = ImageFont.truetype("src/static/msyh.ttc", 20, encoding='utf-8')
    # w ,h = draw.textsize(musictitle, font = font)
    # draw.text((160-w/2,310),musictitle,(0,0,0),font)
    # await singlequery.finish(MessageSegment.at(qq)+MessageSegment.image(f"base64://{str(image_to_base64(img), encoding='utf-8')}"))


    

with open("src/static/music_data_bkp.json", encoding="utf-8")as fp:
    music_data_bkp = json.load(fp)

"""-----------------随n个x-----------------"""
rand_n = on_regex(r"^随[0-9]+[个|首][绿黄红紫白]?[0-9]+[＋\+]?", rule = dajiang_checker, priority = 10, block = True)
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
        for music in music_data_bkp:
            for i,lv in enumerate(music["level"]):
                if (lv == str(level)+plus)and((diff=='')or(diff==i))and(music["basic_info"]["from"] not in paichu_list):
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
fslb = on_regex(r"^([0-9]+)([＋\+]?)分数列?表([1-9]?)$", priority = 10, block = True)
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
        await fslb.send("每天第一次查询自动刷新成绩，可能需要较长时间。若需手动刷新成绩请发送“刷新成绩”")
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
select_alias = on_command("别名", priority = 10, block = True, rule = maiqun_checker)
@select_alias.handle()
async def _select_alias(event: Event, message: Message = CommandArg()):
    msg = str(message).strip().split(" ")
    if len(msg) == 1 and msg[0] != "":
        id = msg[0]
        with open("src/static/all_alias_temp.json","r",encoding='utf-8')as fp:
            alias_data = json.load(fp)
        if id not in alias_data:
            await select_alias.finish("未找到该乐曲，请直接输入乐曲id。")
        else:
            s = f"{id}.{alias_data[id]['Name']}的别名有：\n"
            for i in range(1,len(alias_data[id]['Alias'])):
                s += f"{alias_data[id]['Alias'][i]}\n"
            await select_alias.finish(s)
    elif len(msg) == 3:
        qq = str(event.get_user_id())
        id = msg[1]
        with open("src/static/all_alias_temp.json","r",encoding='utf-8')as fp:
            alias_data = json.load(fp)
        if id not in alias_data:
            await select_alias.finish("未找到该乐曲，请直接输入乐曲id。")
        else:
            if ("增" in msg[0]) or ("加" in msg[0]):
                if msg[2] in alias_data[id]["Alias"]:
                    await select_alias.finish("该别名已存在。")
                else:
                    with open("src/static/alias_pre_process_add.json","r",encoding='utf-8')as fp:
                        alias_pre_process_add = json.load(fp)
                    if id in alias_pre_process_add:
                        alias_pre_process_add[id].append(msg[2])
                    else:
                        alias_pre_process_add[id] = [msg[2]]
                    with open("src/static/alias_pre_process_add.json","w",encoding='utf-8')as fp:
                        json.dump(alias_pre_process_add,fp,ensure_ascii=False,indent=4)
                    with open("src/static/alias_log.csv","a",encoding='utf-8')as fp:
                        fp.write(f"{qq},{','.join(msg)}\n")
                    if refresh_alias_temp():
                        await select_alias.finish(f"添加成功。\n已为 {id}.{alias_data[id]['Name']} 添加别名：\n{msg[2]}")
            elif ("删" in msg[0]) or ("减" in msg[0]):
                if msg[2] not in alias_data[id]["Alias"]:
                    await select_alias.finish("该别名不存在。")
                else:
                    with open("src/static/alias_pre_process_remove.json","r",encoding='utf-8')as fp:
                        alias_pre_process_remove = json.load(fp)
                    if id in alias_pre_process_remove:
                        alias_pre_process_remove[id].append(msg[2])
                    else:
                        alias_pre_process_remove[id] = [msg[2]]
                    with open("src/static/alias_pre_process_remove.json","w",encoding='utf-8')as fp:
                        json.dump(alias_pre_process_remove,fp,ensure_ascii=False,indent=4)
                    with open("src/static/alias_log.csv","a",encoding='utf-8')as fp:
                        fp.write(f"{qq},{','.join(msg)}\n")
                    if refresh_alias_temp():
                        await select_alias.finish("删除成功")
            else:
                await select_alias.finish('输入格式错误。\n查别名请输入“别名 id”\n增加别名请输入“别名 增 id 别名”\n删除别名请输入“别名 删 id 别名”')

    else:
        await select_alias.finish('输入格式错误。\n查别名请输入“别名 id”\n增加别名请输入“别名 增 id 别名”\n删除别名请输入“别名 删 id 别名”\n')

    