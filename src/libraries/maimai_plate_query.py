from PIL import Image
import math,wget,os,aiohttp,json,time

from src.libraries.maimaidx_music import get_cover_len5_id
from src.libraries.secrets import DF_Dev_Token
from src.libraries.image import get_music_cover

cover_dir = 'src/static/mai/cover/'
icon_dir = 'src/static/mai/icon/'
temp_dir = 'src/static/mai/temp/'

async def get_player_plate(payload: dict):
    async with aiohttp.request("POST", "https://www.diving-fish.com/api/maimaidxprober/query/plate", json=payload) as resp:
        if resp.status == 400:
            return None, 400
        elif resp.status == 403:
            return None, 403
        plate_data = await resp.json()
        return plate_data, 0
        
async def refresh_player_full_data(qq: str):
    payload = {'qq': qq } 
    async with aiohttp.request("POST", "https://www.diving-fish.com/api/maimaidxprober/query/player", json=payload) as resp:
        if resp.status == 400:
            return None, 400
        query_player = await resp.json()
        username = query_player["username"]
        async with aiohttp.request("GET","https://www.diving-fish.com/api/maimaidxprober/dev/player/records",params={"username":username},headers={"developer-token":DF_Dev_Token}) as resp:
            if resp.status == 400:
                return None, 400
            full_data = await resp.json()      
            file = open( temp_dir + qq + time.strftime("_%y%m%d") + ".json", "w", encoding= "utf-8")
            json.dump(full_data,file)
            file.close()
            return full_data, 0

async def read_full_data(qq:str):
    try:
        file = open( temp_dir + qq + time.strftime("_%y%m%d") + ".json", "r", encoding= "utf-8")
        data = json.load(file)
        file.close()
        return data,1
    except:
        data,success = await refresh_player_full_data(qq)
        return data,success

def not_exist_data(qq:str):
    if os.path.exists(temp_dir + qq + time.strftime("_%y%m%d") + ".json"):
        return 0
    else:
        return 1

async def querydraw(song_played:dict,searchlist:list,diffcount:dict,platename:str,qq:str,flag = 1) -> Image:
    iconsize = 140
    iconsizepro = 180
    k=0
    s=0
    for diff in diffcount:
        k+=math.ceil(diffcount[diff]/9)
        if(diffcount[diff]!=0):
            s+=1
    width,height = 2000,100+232+100+k*iconsizepro+40*s+80
    img = Image.new("RGB",(width,height))
    #imgdraw = ImageDraw.Draw(img)
    bg = Image.open("src/static/platequery/bg.png").convert('RGB')
    for i in range(math.ceil(height/2000)):
        img.paste(bg,(0,2000*i))
    hoffset = 100
    try:
        plate = Image.open("src/static/mai/plate/"+ platename + ".png").convert('RGBA')
        plate = plate.resize((1440,232))
        img.paste(plate,(280,hoffset),mask=plate.split()[3])
    except:
        pass
    hoffset += 232+100
    k=0
    fcfs_name_dict = {
        "fc": "FC",
        "fcp": "FCp",
        "ap": "AP",
        "app": "APp",
        "fs": "FS",
        "fsp": "FSp",
        "fsd": "FSD",
        "fsdp": "FSDp",
        "none": "none"        
    }
    for diff in diffcount:
        if(diffcount[diff]!=0):
            dificon = Image.open("src/static/platequery/"+ diff + ".png").convert('RGBA')
            img.paste(dificon,(50,hoffset),mask=dificon.split()[3])
            woffset = 320
            for i in range(diffcount[diff]):
                musicid = searchlist[k][0]
                frame = Image.open("src/static/platequery/"+ str(searchlist[k][2]) + ".png").convert('RGBA')
                finish = Image.open("src/static/platequery/finish.png").convert('RGBA')
                icon = get_music_cover(musicid)
                icon = icon.resize((130,130))
                frame.paste(icon,(5,5))
                if (str(musicid) + 'l' + str(searchlist[k][2])) in song_played:
                    minfo = song_played[(str(musicid) + 'l' + str(searchlist[k][2]))]
                    if minfo['fc'] == "":
                        minfo['fc'] = "none"
                    if minfo['fs'] == "":
                        minfo['fs'] = "none"
                else:
                    minfo = {
                    "achievements": 0,
                    "fc": "none",
                    "fs": "none",
                    "level": searchlist[k][1]
                    }
                covertime = 1.2
                if platename[1] == '者':
                    if minfo['fc'][:2] == 'ap':
                        covertime = 1.7
                        cover = minfo['fc']
                        frame.paste(finish,(5,5),mask=finish.split()[3])
                        cover = Image.open("src/static/mai/pic/UI_MSS_MBase_Icon_"+ cover + ".png").convert('RGBA')
                    else:
                        if minfo['achievements'] >= 100:
                            if minfo['achievements'] >= 100.5:
                                cover = 'SSSp'
                                frame.paste(finish,(5,5),mask=finish.split()[3])
                            else:
                                cover = 'SSS'
                                frame.paste(finish,(5,5),mask=finish.split()[3])
                        elif minfo['achievements'] >= 99:
                            if minfo['achievements'] >= 99.5:
                                cover = 'SSp'
                                frame.paste(finish,(5,5),mask=finish.split()[3])
                            else:
                                cover = 'SS'
                                frame.paste(finish,(5,5),mask=finish.split()[3])
                        elif minfo['achievements'] >=97:
                            if minfo['achievements'] >= 98:
                                cover = 'Sp'
                                frame.paste(finish,(5,5),mask=finish.split()[3])
                            else:
                                cover = 'S'
                                frame.paste(finish,(5,5),mask=finish.split()[3])
                        elif minfo['achievements'] >=94:
                            cover = 'AAA'
                            frame.paste(finish,(5,5),mask=finish.split()[3])
                        elif minfo['achievements'] >=90:
                            cover = 'AA'
                            frame.paste(finish,(5,5),mask=finish.split()[3])
                        elif minfo['achievements'] >=80:
                            cover = 'A'
                            frame.paste(finish,(5,5),mask=finish.split()[3])
                        elif minfo['achievements'] >=75:
                            cover = 'BBB'
                        elif minfo['achievements'] >=70:
                            cover = 'BB'
                        elif minfo['achievements'] >=60:
                            cover = 'B'
                        elif minfo['achievements'] >=50:
                            cover = 'C'
                        elif minfo['achievements'] >0:
                            cover = 'D'
                        else:
                            cover = 'none'
                        cover = Image.open("src/static/mai/pic/UI_GAM_Rank_"+ cover + ".png").convert('RGBA')
                elif platename[1] == '極':
                    covertime = 1.7
                    cover = fcfs_name_dict[minfo['fc']]
                    if cover != 'none':
                        frame.paste(finish,(5,5),mask=finish.split()[3])
                    cover = Image.open("src/static/mai/pic/UI_MSS_MBase_Icon_"+ cover + ".png").convert('RGBA')
                elif platename[1] == '神':
                    covertime = 1.7
                    cover = fcfs_name_dict[minfo['fc']]
                    if cover[:2] == 'ap':
                        frame.paste(finish,(5,5),mask=finish.split()[3])
                    cover = Image.open("src/static/mai/pic/UI_MSS_MBase_Icon_"+ cover + ".png").convert('RGBA')
                elif platename[1] == '舞':
                    covertime = 1.7
                    cover = fcfs_name_dict[minfo['fc']]
                    if cover[:3] == 'fsd':
                        frame.paste(finish,(5,5),mask=finish.split()[3])
                    cover = Image.open("src/static/mai/pic/UI_MSS_MBase_Icon_"+ cover + ".png").convert('RGBA')
                else: #if platename[1] == '将':
                    if minfo['fc'][:2] == 'ap':
                        covertime = 1.7
                        cover = fcfs_name_dict[minfo['fc']]
                        frame.paste(finish,(5,5),mask=finish.split()[3])
                        cover = Image.open("src/static/mai/pic/UI_MSS_MBase_Icon_"+ cover + ".png").convert('RGBA')
                    else:
                        if minfo['achievements'] >= 100:
                            if minfo['achievements'] >= 100.5:
                                cover = 'SSSp'
                                frame.paste(finish,(5,5),mask=finish.split()[3])
                            else:
                                cover = 'SSS'
                                frame.paste(finish,(5,5),mask=finish.split()[3])
                        elif minfo['achievements'] >= 99:
                            if minfo['achievements'] >= 99.5:
                                cover = 'SSp'
                            else:
                                cover = 'SS'
                        elif minfo['achievements'] >=97:
                            if minfo['achievements'] >= 98:
                                cover = 'Sp'
                            else:
                                cover = 'S'
                        elif minfo['achievements'] >=94:
                            cover = 'AAA'
                        elif minfo['achievements'] >=90:
                            cover = 'AA'
                        elif minfo['achievements'] >=80:
                            cover = 'A'
                        elif minfo['achievements'] >=75:
                            cover = 'BBB'
                        elif minfo['achievements'] >=70:
                            cover = 'BB'
                        elif minfo['achievements'] >=60:
                            cover = 'B'
                        elif minfo['achievements'] >=50:
                            cover = 'C'
                        elif minfo['achievements'] >0:
                            cover = 'D'
                        else:
                            cover = 'none'
                        cover = Image.open("src/static/mai/pic/UI_GAM_Rank_"+ cover + ".png").convert('RGBA')
                cover = cover.resize((int(cover.size[0]*covertime),int(cover.size[1]*covertime)))
                coverpos = (int((iconsize-cover.size[0])/2),int((iconsize-cover.size[1])/2))
                frame.paste(cover,coverpos,mask=cover.split()[3])
                img.paste(frame,(woffset + i%9*iconsizepro, hoffset + int(i/9)*iconsizepro))
                k+=1
            hoffset += math.ceil(diffcount[diff]/9)*iconsizepro+40

    if qq != '':
        if os.path.exists(icon_dir + qq + '.png'):
            logo = Image.open(icon_dir + qq + '.png').convert('RGBA')
        else:
            try:
                ProfImg = wget.download('https://q.qlogo.cn/g?b=qq&nk=' + qq + '&s=640' , temp_dir + qq)
                logo = Image.open(ProfImg).convert('RGBA')
            except:
                try:
                    logo = Image.open(temp_dir + qq).convert('RGBA')
                except:
                    logo = Image.open(icon_dir + 'default.png').convert('RGBA')       
    else:
        logo = Image.open(icon_dir + 'default.png').convert('RGBA')
    # if qq == '':
    #     logo = Image.open(icon_dir + 'default.png').convert('RGBA')
    # else:
    #     try:
    #         logo = Image.open(icon_dir + qq + '.png').convert('RGBA')
    #     except:
    #         if os.path.exists(temp_dir + qq):
    #             os.remove(temp_dir + qq)
    #         ProfImg = wget.download('https://q.qlogo.cn/g?b=qq&nk=' + qq + '&s=640' , temp_dir + qq)
    #         logo = Image.open(ProfImg).convert('RGBA')
    iconmask = Image.open(icon_dir + 'iconmask.png').convert('RGBA')
    logo = logo.resize((200,200))
    temp = Image.new("RGBA",(200,200))
    temp.paste(logo, (0,0), mask=iconmask.split()[3])
    img.paste(temp, (296, 115), mask=temp.split()[3])
    if flag == 2:
        img = img.resize((int(img.size[0]*0.5),int(img.size[1]*0.5)))
    else:
        pass
#        img = img.resize((int(img.size[0]*0.75),int(img.size[1]*0.75)))
    return img
