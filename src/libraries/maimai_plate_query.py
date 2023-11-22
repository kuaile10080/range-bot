from PIL import Image, ImageDraw, ImageFont
import os,aiohttp,json,time

from src.libraries.secrets import DF_Dev_Token
from src.libraries.image import get_music_cover, get_qq_logo
from src.libraries.static_lists_and_dicts import info_to_file_dict

cover_dir = 'src/static/mai/cover/'
temp_dir = 'src/static/mai/temp/'
assets_path = "src/static/mai/platequery/"
plate_path = "src/static/mai/plate/"
        
async def refresh_player_full_data(qq: str):
    async with aiohttp.request("GET","https://www.diving-fish.com/api/maimaidxprober/dev/player/records",params={"qq":qq},headers={"developer-token":DF_Dev_Token}) as resp:
        if resp.status == 400:
            return None, 400
        full_data = await resp.json()      
        file = open( temp_dir + qq + time.strftime("_%y%m%d") + ".json", "w", encoding= "utf-8")
        json.dump(full_data,file)
        file.close()
        return full_data, 0

async def get_full_data_by_username(username: str):
    async with aiohttp.request("GET","https://www.diving-fish.com/api/maimaidxprober/dev/player/records",params={"username":username},headers={"developer-token":DF_Dev_Token}) as resp:
        if resp.status == 400:
            return None, 400
        full_data = await resp.json()
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

def draw_one_music(record:dict)->Image.Image:
    # base_size = (140,140)
    base = Image.open(f"{assets_path}{record['level_index']}{'dx' if int(record['id'])>=10000 else ''}.png").convert("RGBA")
    cover = get_music_cover(record['id'])
    cover = cover.convert('RGBA').resize((130,130))
    if record['finished']:
        f = Image.open(f"{assets_path}finish.png").convert("RGBA")
        cover.alpha_composite(f)
    elif record['cover']!="":
        f = Image.open(f"{assets_path}unfinish.png").convert("RGBA")
        cover.alpha_composite(f)
        
    base.paste(cover,(5,5),cover)
    if record['cover'] in info_to_file_dict.keys():
        cover = Image.open(f"{assets_path}UI_{info_to_file_dict[record['cover']]}.png").convert("RGBA")
        base.paste(cover,(int((base.size[0]-cover.size[0])/2),int((base.size[1]-cover.size[1])/2)),cover)

    return base



def draw_rank_list(records:dict)->Image.Image:
    keys = list(records.keys())
    keys.sort(reverse=True)
    none_keys = []
    for key in keys:
        if records[key]==[]:
            none_keys.append(key)
    for key in none_keys:
        keys.remove(key)

    lines = sum([1 + int((len(records[key])-0.1)/10) for key in keys])
    img = Image.new('RGBA', (1952, lines*160), color = (0, 0, 0,0))
    line = 0
    row = 0
    for key in keys:
        head = Image.open(f"{assets_path}{key}.png").convert("RGBA")
        img.paste(head,(30,line*160+15),head)
        for record in records[key]:
            if row == 10:
                row = 0
                line += 1
            song_img = draw_one_music(record)
            img.paste(song_img,(row*160+340,line*160+15),song_img)
            row += 1
        row = 0
        line += 1
    return img


def draw_status(status:dict)->Image.Image:
    img = Image.new('RGBA', (152*len(status)+150*len(status)-150, 156), color = (0, 0, 0,0))
    font_info = ImageFont.truetype("src/static/SourceHanSansCN-Bold.otf", 34,encoding="utf-8")
    for i,key in enumerate(status):
        temp = Image.open(f"{assets_path}UI_RSL_MusicJacket_Base_{key}.png").convert("RGBA")
        temp_draw = ImageDraw.Draw(temp)
        temp_draw.text((82, 3), f"{status[key]['V']}\n{status[key]['X']}\n{status[key]['-']}", font=font_info, fill=(255, 255, 255))
        temp_draw.text((81, 2), f"{status[key]['V']}\n{status[key]['X']}\n{status[key]['-']}", font=font_info, fill=(0, 0, 0))
        img.paste(temp,(i*152+i*150,0),temp)
    return img
        

async def draw_final_rank_list(info:dict,records:dict)->Image.Image:
    a = time.time()
    # get rank list
    rank_list = draw_rank_list(records)

    print(time.time()-a)

    status_img = None
    finished_img = None
    # get status
    if info["status"]=={}:
        statusoffset = 0
    else:
        statusoffset = 120
        status_img = draw_status(info["status"])
        if info["dacheng"]:
            finished_img = Image.open(f"{assets_path}已达成.png").convert("RGBA")
        elif info["queren"]:
            finished_img = Image.open(f"{assets_path}已确认.png").convert("RGBA")

    print(time.time()-a)

    # create new image
    img = Image.new('RGBA', (rank_list.size[0], rank_list.size[1] + 800 + statusoffset), color = (255, 255, 255, 255))

    # draw bg
    rankbg = Image.open(f"{assets_path}rankbg.png").convert("RGBA")
    bg_times = int((img.size[1]-400)/rankbg.size[1]) + 1
    for i in range(bg_times):
        img.paste(rankbg,(0,400+i*rankbg.size[1]),rankbg)

    top = Image.open(f"{assets_path}top.png").convert("RGBA")
    img.alpha_composite(top)
    
    bott = Image.open(f"{assets_path}bott.png").convert("RGBA")
    temp = img.crop((0,img.size[1]-bott.size[1],img.size[0],img.size[1]))
    temp.alpha_composite(bott)
    img.paste(temp,(0,img.size[1]-bott.size[1]),temp)

    print(time.time()-a)
    # draw status
    if status_img:
        img.paste(status_img,(int((img.size[0]-status_img.size[0])/2),430),status_img)

    if finished_img:
        # draw plate and qq
        plate_shadow = Image.open(f"{assets_path}plate_shadow.png").convert("RGBA")
        img.paste(plate_shadow,(256-100,150),plate_shadow)
        plate = Image.open(f"{plate_path}{info['plate']}").convert("RGBA").resize((1440,232))
        img.paste(plate,(256-100,150),plate)
        qqlogo = get_qq_logo(info['qq']).resize((200,200))
        img.paste(qqlogo,(256+16-100,150+15),qqlogo)
        img.paste(finished_img,(1600,120),finished_img)
    else:
        # draw plate and qq
        plate_shadow = Image.open(f"{assets_path}plate_shadow.png").convert("RGBA")
        img.paste(plate_shadow,(256,150),plate_shadow)
        plate = Image.open(f"{plate_path}{info['plate']}").convert("RGBA").resize((1440,232))
        img.paste(plate,(256,150),plate)
        qqlogo = get_qq_logo(info['qq']).resize((200,200))
        img.paste(qqlogo,(256+16,150+15),qqlogo)

    # draw rank list
    img.paste(rank_list,(0,500 + statusoffset),rank_list)
    img = img.convert("RGB")

    print(time.time()-a)
    return img