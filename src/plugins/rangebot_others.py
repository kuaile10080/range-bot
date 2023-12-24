from nonebot import on_command, on_regex, on_keyword, on_message
from nonebot.params import CommandArg
from nonebot.adapters import Event
from nonebot.adapters.onebot.v11 import Message, MessageSegment, exception
from nonebot.matcher import Matcher

from src.libraries.image import *
from src.libraries.secrets import *

from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt
import os,re,random,json,time,math,pymysql,wget,base64,io,requests
import numpy as np

db = pymysql.connect(   host = SQL_HOST, 
                        port = SQL_PORT,
                        user = 'root', 
                        password = SQL_PASSWORD, 
                        database = 'bot')

static_dir = "src/static/"

def readjson(path:str):
    try:
        file = open(path,"r")
        jsontemp = json.load(file)
        file.close()
        return jsontemp
    except:
        jsontemp = {"num": 0, "time": 0, "source": "-1"}
        return jsontemp
def writejson(path:str, jsontemp):
    file = open(path,"w")
    json.dump(jsontemp,file)
    file.close()
    return

capoo_dir_ = 'src/static/capoo/'
long_dir_ = 'src/static/long/'

"""-----------随机龙图-----------"""
longtu = on_command('随机龙图', aliases={"来个龙图","来张龙图","来点龙图"}, priority = 30, block = True)
@longtu.handle()
async def _longtu(event: Event, message: Message = CommandArg()):
    if random.random() < 0.02:
        long_dir = capoo_dir_
    else:
        long_dir = long_dir_
    dirlist = os.listdir(long_dir)
    a = random.randint(0,len(dirlist)-1)
    with open(long_dir + dirlist[a],"rb")as fp:
        encoded = base64.b64encode(fp.read())
    url = "base64://" + encoded.decode('utf-8')
    await longtu.finish(MessageSegment.image(url))

"""-----------随机cappo-----------"""
capoo = on_command('/capoo', priority = 30, block = True)
@capoo.handle()
async def _capoo(event: Event, message: Message = CommandArg()):
    if random.random() < 0.02:
        capoo_dir = long_dir_
    else:
        capoo_dir = capoo_dir_
    dirlist = os.listdir(capoo_dir)
    a = random.randint(0,len(dirlist)-1)
    with open(capoo_dir + dirlist[a],"rb")as fp:
        encoded = base64.b64encode(fp.read())
    url = "base64://" + encoded.decode('utf-8')
    await capoo.finish(MessageSegment.image(url))
    


"""-----------机厅几（开发中qy|bl|hsh|yt|rs|wy|lw|zc|wxh）-----------"""
jt_sh = ['qy','bl','hsh']
jt_zb = ['yt','rs','wy','zc','wxh']
jt_jn = ['lw']
group_sh = ['751302572','775613195','780012208','742829700','646232811','698699856','606964743']
group_sh.extend(MAIN_GROUPS)
group_zb = ['419134739','610587231',TEST_GROUP]
group_jn = ['784593881',TEST_GROUP]

#jtregex = r"(?i)^(qy|bl|hsh|yt|rs|wy|wxh)(j|-?[0-9]+|\+?[0-9]+)$"
jtregex = r"(?i)^(qy|bl|hsh|yt|rs|wy|lw|zc|wxh)(j|几|[0-9]+)$"
jtmax = {"qy":40,"bl":40,"hsh":20,"yt":50,"rs":30,"wy":30,"lw":30,"zc":30,"wxh":30}
jtj = on_regex(jtregex, priority = 21, block = True)
@jtj.handle()
async def _jtj(event: Event):
    msg = re.match(jtregex,str(event.get_message()).strip().lower()).groups()
    if (str(re.match("group_(.+)_(.+)",event.get_session_id()).groups()[0]) in group_sh) and (msg[0] in jt_sh) \
        or (str(re.match("group_(.+)_(.+)",event.get_session_id()).groups()[0]) in group_zb) and (msg[0] in jt_zb)\
            or (str(re.match("group_(.+)_(.+)",event.get_session_id()).groups()[0]) in group_jn) and (msg[0] in jt_jn):
        if (8 < int(time.strftime("%H")) < 23):
            user = str(event.get_user_id())
            if msg[1] in ["j","几"]:
                #发送时间和人数
                jtjson = readjson(static_dir + "jt/" + msg[0] + ".json")
                if time.strftime('%j',time.localtime(time.time())) != time.strftime('%j',time.localtime(jtjson['time'])):
                    await jtj.finish("没说就是0")
                else:
                    m = int((time.time() - jtjson['time'])/60)
                    num = jtjson['num']
                    if 'source' in jtjson.keys():
                        source = '信息提供者: ' + jtjson['source']
                    else:
                        source = ''
                    await jtj.finish(f"{m}分钟前{msg[0]}{num}  {source}")
            else:
                num = int(msg[1])
                if (num > jtmax[msg[0]]) | (num < 0):
                    try:
                        db.ping()
                        cursor = db.cursor()
                        SQL = f"INSERT INTO sblist VALUES ({user},now());"
                        cursor.execute(SQL)
                        db.commit()
                        cursor.close()
                    except:
                        pass
                    #await jtj.finish("你测你码呢")
                else:
                    jtjson = {'num': 0, 'time': 0, 'source': "0"}
                    jtjson['num'] = num
                    jtjson['time'] = time.time()
                    jtjson['source'] = user
                    writejson(static_dir + "jt/" + msg[0] + ".json", jtjson)
                    try:
                        db.ping()
                        cursor = db.cursor()
                        SQL = f"INSERT INTO {msg[0]} (time,num,operator,operate_parameter) VALUES (now(),{num},{user},{num});"
                        cursor.execute(SQL)
                        db.commit()
                        cursor.close()
                    except:
                        pass
                    await jtj.finish("收到收到，" + msg[0] + str(num))
        else:
            await jtj.finish("看看几点了")

jtaddre = r"(?i)^(qy|bl|hsh|yt|rs|wy|lw|zc|wxh)([\+＋\-－])(\d+)$"
jtadd = on_regex(jtaddre, priority = 22, block = True)
@jtadd.handle()
async def _jtadd(event: Event):
    msg = re.match(jtaddre,str(event.get_message()).strip().lower()).groups()
    if (str(re.match("group_(.+)_(.+)",event.get_session_id()).groups()[0]) in group_sh) and (msg[0] in jt_sh) \
        or (str(re.match("group_(.+)_(.+)",event.get_session_id()).groups()[0]) in group_zb) and (msg[0] in jt_zb)\
            or (str(re.match("group_(.+)_(.+)",event.get_session_id()).groups()[0]) in group_jn) and (msg[0] in jt_jn):
        if (8 < int(time.strftime("%H")) < 23):
            user = str(event.get_user_id())
            jtjson = readjson(static_dir + "jt/" + msg[0] + ".json")
            if time.strftime('%j',time.localtime(time.time())) != time.strftime('%j',time.localtime(jtjson['time'])):
                await jtadd.finish("没有人报过今天的人数，请上报确切人数")
            num = jtjson['num']
            if msg[1] in "+＋":
                num = num + int(msg[2])
                oper = "PLUS"
            else:
                num = num - int(msg[2])
                oper = "MINUS"
            if (0 <= num <= jtmax[msg[0]]):
                jtjson['num'] = num
                jtjson['time'] = time.time()
                jtjson['source'] = user
                writejson(static_dir + "jt/" + msg[0] + ".json", jtjson)
                try:
                    db.ping()
                    cursor = db.cursor()
                    SQL = f"INSERT INTO {msg[0]} (time,num,operator,operate,operate_parameter) VALUES (now(),{num},{user},'{oper}',{int(msg[2])});"
                    cursor.execute(SQL)
                    db.commit()
                    cursor.close()
                except:
                    pass
                await jtadd.finish("收到收到，" + msg[0] + msg[1] + msg[2] + ",目前" + msg[0] + str(num))
            else:
                await jtadd.finish("上报有误，请重新上报或上报确切人数")
        else:
            await jtadd.finish("看看几点了")



"""-----------帮你做决定（抄的）-----------"""    
rghaishi = on_regex(r"^range.*还是.*", priority = 31, block = True)
@rghaishi.handle()
async def _(event: Event):
    haishilist = str(event.get_message())[5:].strip().split("还是")
    for s in haishilist:
        if len(set(haishilist)) != len(haishilist) or (s.strip() == ""):
            await rghaishi.finish("蓝的盆")
        await rghaishi.finish(haishilist[random.randint(0,len(haishilist)-1)].strip())


SETU_TIMING = 30
"""-----------随机色图(开发中)-----------"""
setu_dir = 'src/static/setu/'
sjst = on_keyword(['色图','涩图','瑟图'], rule = setu_checker, priority = 10000, block = True) #取消priority = 10 
@sjst.handle()
async def sjst_handle(event: Event):
    timelist = readjson(static_dir + "seturecord.json")
    if re.match("group_(.+)_(.+)",event.get_session_id()):
        groupid = str(re.match("group_(.+)_(.+)",event.get_session_id()).groups()[0])
    else:
        groupid = TEST_GROUP
    try:
        a = (timelist[groupid])
    except:
        a = 0
    rest = time.time() - a
    if (rest > SETU_TIMING) | (groupid == TEST_GROUP) | (str(event.get_user_id()) == RANGE):
        timelist[groupid] = time.time()
        writejson(static_dir + "seturecord.json",timelist)
        dirlist = os.listdir(setu_dir)
        dirlist.sort(key = lambda x:int(x[:-4]))
        #sorted_dirlist = sorted(dirlist , key = lambda file: os.path.getctime(os.path.join( setu_dir , file)))
        a = int(math.sin(random.uniform(0,1.1))/math.sin(1.1)*len(dirlist))
        setupath = setu_dir + str(a) + '.jpg'
        with open(setupath,"rb")as fp:
            encoded = base64.b64encode(fp.read())
        url = "base64://" + encoded.decode('utf-8')
        try:
            await sjst.finish(MessageSegment.image(url))
        except exception.ActionFailed:
            banlist = readjson(static_dir + "setubanrecord.json")
            banlist.append(a)
            writejson(static_dir + "setubanrecord.json", banlist)
            await sjst.finish("图可能没发出来，大概率被处男审核截胡了")
    else:
        #CD还剩rest秒
        await sjst.finish("本群CD还剩" + str( SETU_TIMING - int(rest)) + "秒，请稍后再试")


fuducount = {}
fudumessage = {}
"""-----------复读-----------"""
fudu = on_message(priority = 20001, block = True)  
@fudu.handle()
async def fudu_handle(event: Event):
    global fuducount, fudumessage
    if type(re.match("group_(.+)_(.+)",event.get_session_id())) == re.Match:
        if '当前版本不支持该消息类型' in str(event.get_message()):
            return
        group = str(re.match("group_(.+)_(.+)",event.get_session_id()).groups()[0])
        if len(str(event.get_message())) > 50:
            fuducount[group] = -1
            fudumessage[group] = ''
            return
        if (group in fuducount.keys()) & (group in fudumessage.keys()):
            if fudumessage[group] == str(event.get_message()):
                fuducount[group] +=1
                if fuducount[group] > 2:
                    fuducount[group] = -1000
                    await fudu.finish(Message(str(event.get_message())))
                else:
                    return
            else:
                fuducount[group] = 1
                fudumessage[group] = str(event.get_message())
                return
        else:
            fuducount[group] = 1
            fudumessage[group] = str(event.get_message())
            return
    return

"""-----------dayday-----------"""
daydaykeywords = ['自卑','焦虑','急','[CQ:face,id=107]']
dayday = on_message(priority = 20000, block = False, rule = dayday_checker)
@dayday.handle()
async def dayday_handle(event: Event, matcher: Matcher):
    s = str(event.get_message())
    for word in daydaykeywords:
        if word in s:
            msg = "你" + word + "你ma呢"
            matcher.stop_propagation()
            await dayday.finish(msg)
    return

"""-----------gre-----------"""
with open("src/static/gre/GRE_3.json",encoding='utf-8')as fp:
    gre_dict = fp.read().split('\n')[:-1]
    gre_dict = [json.loads(item) for item in gre_dict]
gre_temp = {}
gre_status = 0
ans_pattern = ""
gre_event = on_message(priority = 19999, block = False, rule = gre_checker)
@gre_event.handle()
async def gre_handle(event: Event,matcher: Matcher):
    global gre_temp, gre_status, gre_dict, ans_pattern
    s = str(event.get_message()).lower().strip()
    if gre_status != 0:
        if s in ["重置","reset"]:
            gre_status = 0
            matcher.stop_propagation()
            await gre_event.finish("已重置")
        elif s == "答案":
            with open("src/static/gre/review.json","r",encoding='utf-8')as fp:
                review = json.load(fp)
            review.append(gre_temp)
            with open("src/static/gre/review.json","w",encoding='utf-8')as fp:
                json.dump(review,fp)
            qq = str(event.get_user_id())
            with open("src/static/gre/rank.json","r",encoding='utf-8')as fp:
                rank = json.load(fp)
            if qq in rank.keys():
                # if rank[qq]["point"]>2:
                rank[qq]["point"] -= 3
                with open("src/static/gre/rank.json","w",encoding='utf-8')as fp:
                    json.dump(rank,fp)
                gre_status = 0
                matcher.stop_propagation()
                await gre_event.finish(gre_temp["content"]["word"]["wordHead"])
                # else:
                #     matcher.stop_propagation()
                #     await gre_event.finish(f"积分为{rank[qq]['point']}，积分不足")
            else:
                rank[qq] = {
                    "right": 0,
                    "trys": 0,
                    "point": 0
                }
                with open("src/static/gre/rank.json","w",encoding='utf-8')as fp:
                    json.dump(rank,fp)
                matcher.stop_propagation()
                await gre_event.finish(f"积分为0，积分不足")
        else:
            if re.match(ans_pattern,s):
                matcher.stop_propagation()
                qq = str(event.get_user_id())
                with open("src/static/gre/rank.json","r",encoding='utf-8')as fp:
                    rank = json.load(fp)
                if qq not in rank.keys():
                    rank[qq] = {
                        "right": 0,
                        "trys": 0,
                        "point": 0
                    }
                if s == gre_temp["content"]["word"]["wordHead"]:
                    gre_status = 0
                    rank[qq]["right"] += 1
                    rank[qq]["trys"] += 1
                    rank[qq]["point"] += 1
                    with open("src/static/gre/rank.json","w",encoding='utf-8')as fp:
                        json.dump(rank,fp)
                    await gre_event.finish(MessageSegment.at(qq) + "答对了")
                else:
                    gre_status += 1
                    rank[qq]["trys"] += 1
                    with open("src/static/gre/rank.json","w",encoding='utf-8')as fp:
                        json.dump(rank,fp)
                    if gre_status == 5:
                        with open("src/static/gre/review.json","r",encoding='utf-8')as fp:
                            review = json.load(fp)
                        review.append(gre_temp)
                        with open("src/static/gre/review.json","w",encoding='utf-8')as fp:
                            json.dump(review,fp)
                        msg = "提示：\n"
                        for key in gre_temp["content"]["word"]["content"]:
                            if key == 'usphone':
                                msg += "美：[" + gre_temp["content"]["word"]["content"][key] + "]\n"
                            elif key =='ukphone':
                                msg += "英：[" + gre_temp["content"]["word"]["content"][key] + "]\n"
                        if msg != "提示：\n":
                            await gre_event.finish(msg)
                    if gre_status > 10:
                        gre_status = 0
                        await gre_event.finish("答错10次，已重置，正确答案是" + gre_temp["content"]["word"]["wordHead"])
                    else:
                        await gre_event.finish(MessageSegment.at(qq) + "答错了，再想想")
    elif (gre_status == 0) and (s in ["gre","gre review"]):
        if s != "gre":
            with open("src/static/gre/review.json","r",encoding='utf-8')as fp:
                review = json.load(fp)
            if len(review) == 0:
                await gre_event.finish("复习完了")
            else:
                word = random.choice(review)
                review.remove(word)
                with open("src/static/gre/review.json","w",encoding='utf-8')as fp:
                    json.dump(review,fp)
        else:
            word = random.choice(gre_dict)
            while((word == gre_temp) or ("syno" not in word["content"]["word"]["content"])):
                word = random.choice(gre_dict)
        gre_temp = word
        word = gre_temp["content"]["word"]
        gre_status = 1
        wordHead = word["wordHead"]
        replace_list = random.sample([i for i in range(1,len(wordHead))], len(wordHead)//2)
        wordHead = list(wordHead)
        for i in replace_list:
            wordHead[i] = '_'
        wordHead = ''.join(wordHead)
        ans_pattern = wordHead.replace("_","[a-z\-]*")
        synos = word["content"]["syno"]["synos"]
        msg = f"{wordHead}\n"
        pt = r"（[^()]*）"
        for item in synos:
            tran = re.sub(pt, "", item['tran'])
            msg += f"{item['pos']} {tran}\n"
        matcher.stop_propagation()
        await gre_event.finish(msg)

"""-----------gre rank-----------"""
gre_rank = on_regex(r"^gre rank$", priority = 19998, block = True, rule = gre_checker)
@gre_rank.handle()
async def gre_rank_handle(event: Event):
    with open("src/static/gre/rank.json","r",encoding='utf-8')as fp:
        rank = json.load(fp)
    rank = sorted(rank.items(), key=lambda x: int(x[1]["right"])/int(x[1]["trys"]), reverse=True)
    labels = [item[0] for item in rank]
    rights = [item[1]["right"] for item in rank]
    trys = [item[1]["trys"] for item in rank]
    points = [item[1]["point"] for item in rank]
    x = np.arange(len(labels)) 
    width = 0.1 
    fig, ax = plt.subplots()

    fig, ax = plt.subplots()
    # rects1 = ax.bar(x - width*2, points, width, label='points')
    rects2 = ax.bar(x - width+0.01, rights, width, label='rights')
    rects3 = ax.bar(x + 0.02, trys, width, label='trys')

    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()

    def autolabel(rects):
        """在*rects*中的每个柱状条上方附加一个文本标签，显示其高度"""
        for rect in rects:
            height = rect.get_height()
            ax.annotate('{}'.format(height),
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom')
    # autolabel(rects1)
    autolabel(rects2)
    autolabel(rects3)
    fig.tight_layout()
    plt.xticks([])
    w, h = fig.get_size_inches()
    for i,qq in enumerate(labels):
        icon = get_qq_logo(qq)
        fig.figimage(icon.resize((int(3*width*fig.dpi),int(3*width*fig.dpi))), 65 + (w*fig.dpi-65)/(len(labels)-1)*i*0.87, 0, zorder=3)

    plt.savefig("src/static/gre/rank.png")
    plt.close()
    await gre_rank.finish(MessageSegment.text("积分系统暂时下线") + MessageSegment.image("file:///" + os.path.realpath("src/static/gre/rank.png")))



"""-----------daimao-----------"""
daimao_font = ImageFont.truetype("src/static/PingFangBold.ttf", 16, encoding="utf-8")
daimao_edit = on_command("daimao", priority = 10, block = True)
@daimao_edit.handle()
async def _daimao_edit(event: Event, message: Message = CommandArg()):
    msg = str(message).strip().split(" ")
    if len(msg) not in [1,2]:
        return
    elif len(msg) == 1:
        str1 = msg[0]
        str2 = ""
    elif len(msg) == 2:
        str1 = msg[0]
        str2 = msg[1]

    daimao = Image.open("src/static/gifedit/daimao.gif")
    #获取daimao中的所有帧
    #x = daimao.n_frames
    frames = []
    for i in range(23):
        daimao.seek(len(frames)) 
        frames.append(daimao.copy())

 
    draw = ImageDraw.Draw(frames[0])
    text_width1, text_height = draw.textsize(str1, daimao_font)
    x1 = max((frames[0].width - text_width1) // 2,0)
    text_width2, text_height = draw.textsize(str2, daimao_font)
    x2 = max((frames[0].width - text_width2) // 2,0)
    del draw

    if str2 == "":
        for frame in frames[6:]:
            draw = ImageDraw.Draw(frame)
            draw.text((x1, 100), str1, font=daimao_font, fill=(255,255,255))
            del draw
    else:
        for frame in frames[6:13]:
            draw = ImageDraw.Draw(frame)
            draw.text((x1, 100), str1, font=daimao_font, fill=(255,255,255))
            del draw
        for frame in frames[15:]:
            draw = ImageDraw.Draw(frame)
            draw.text((x2, 100), str2, font=daimao_font, fill=(255,255,255))
            del draw

    frames[0].save("src/static/gifedit/daimaotemp.gif", save_all=True, append_images=frames[1:], duration=130, loop=0)
    with open("src/static/gifedit/daimaotemp.gif","rb")as fp:
        encoded = base64.b64encode(fp.read())
    url = "base64://" + encoded.decode('utf-8')
    await daimao_edit.finish(MessageSegment.image(url))

MIRROR_TIMING = 30
mirror_img = on_command("mirror", priority = 10, block = True, rule=ex_fdu_checker)
@mirror_img.handle()
async def _mirror_img(event: Event, message: Message = CommandArg()):

    msg_json = json.loads(event.json())["message"]
    if len(msg_json) != 2:
        return
    elif msg_json[0]["type"] != "text" or msg_json[1]["type"] != "image":
        return
    else:
        if msg_json[0]["data"]["text"][6] == "l":
            part = 0
        elif msg_json[0]["data"]["text"][6] == "r":
            part = 1
        elif msg_json[0]["data"]["text"][6] == "t":
            part = 2
        else:
            await mirror_img.finish(Message("请确保格式为mirror l/r/t + 图片"))

    if type(re.match("group_(.+)_(.+)",event.get_session_id())) == re.Match:
        groupid = str(re.match("group_(.+)_(.+)",event.get_session_id()).groups()[0])
        if groupid not in MAIN_GROUPS:
            timelist = readjson(static_dir + "mirrorrecord.json")
            try:
                a = (timelist[groupid])
            except:
                a = 0
            rest = time.time() - a
            if (rest < MIRROR_TIMING) & (groupid != TEST_GROUP) & (str(event.get_user_id()) != RANGE):
                await mirror_img.finish("本群CD还剩" + str( MIRROR_TIMING - int(rest)) + "秒，请稍后再试") 
            else:
                timelist[groupid] = time.time()
                writejson(static_dir + "mirrorrecord.json",timelist)

    img_url = msg_json[1]["data"]["file"]
    r = requests.get(img_url, stream=True)
    file_io = io.BytesIO(r.content)
    img = Image.open(file_io)

    if img.format == "GIF":
        n = img.n_frames
    else:
        n = 1

    frames = []
    outframes = []
    for i in range(n):
        img.seek(i)
        frames.append(img.copy())

    if len(frames) == 0:
        await mirror_img.finish(Message("图片解析错误"))
    width, height = img.size

    if part == 2:
        for frame in frames:
            outframes.append(frame.transpose(Image.FLIP_LEFT_RIGHT))
    elif part == 0:
        for frame in frames:
            left_half = frame.crop((0, 0, width // 2, height))
            mirrored_img = left_half.transpose(Image.FLIP_LEFT_RIGHT)
            full_image = Image.new("RGBA", (width//2*2, height))
            full_image.paste(left_half, (0, 0))
            full_image.paste(mirrored_img, (width//2, 0))
            outframes.append(full_image)
            del left_half, mirrored_img, full_image
    elif part == 1:
        for frame in frames:
            right_half = frame.crop((width // 2, 0, width, height))
            mirrored_img = right_half.transpose(Image.FLIP_LEFT_RIGHT)
            full_image = Image.new("RGBA", (width//2*2, height))
            full_image.paste(mirrored_img, (0, 0))
            full_image.paste(right_half, (width//2, 0))
            outframes.append(full_image)
            del right_half, mirrored_img, full_image
    

    output = io.BytesIO()
    if img.format == "GIF":
        outframes[0].save(output,format="GIF", save_all=True, append_images=outframes[1:], duration=img.info['duration'], loop=img.info['loop'], disposal=2)
    else :
        outframes[0].save(output,format="PNG")
    encoded = base64.b64encode(output.getvalue())
    url = "base64://" + encoded.decode('utf-8')
    await mirror_img.finish(MessageSegment.image(url))



