import requests,re,json
from io import BytesIO
from PIL import Image,ImageDraw,ImageFont

from nonebot import on_command
from nonebot.params import CommandArg, EventMessage
from nonebot.adapters import Event
from nonebot.adapters.onebot.v11 import Message, MessageSegment
from src.libraries.image import *


path = 'src/static/lol/'
# icon_url = r"https://game.gtimg.cn/images/lol/act/img/champion/" # + HeroList[i]['alias'] + '.png'

    
zhoumian = on_command('周免', aliases={"lol周免","LOL周免","Lol周免","101周免"}, priority = 20, block = True)
@zhoumian.handle()
async def _(event: Event, message: Message = CommandArg()):
    BullBoard = requests.get("https://lol.qq.com/act/AutoCMS/publish/LOLAct/ZMSubject_Board_Site/ZMSubject_Board_Site.js")
    text_re = re.match("(.+)return(.+)}\);(.+)", BullBoard.text)
    hero_all = json.loads(text_re.groups()[1][:-1])
    heroGet = requests.get("https://game.gtimg.cn/images/lol/act/img/js/heroList/hero_list.js")
    HeroList = json.loads(heroGet.text)['hero']
    k = 0
    for i in hero_all.keys():
        if int(i) > k:
            k = int(i)
    freeHero = json.loads('[' + hero_all[str(k)]['freeHero'] + ']')
    freeHeroListId = []
    for i in range(0,len(freeHero)):
        for j in range(0,len(HeroList)):
            if int(HeroList[j]['heroId']) == freeHero[i]:
                freeHeroListId.append(j)
                break
    Hero_BG = Image.open(path + '/Hero_BG.png').convert('RGBA')
    tempDraw = ImageDraw.Draw(Hero_BG)
    font = ImageFont.truetype(path[:-4] + 'Tahoma.ttf', 20, encoding='utf-8')
    for i in range(0,2):
        for j in range(0,10):
            try:
                icon = Image.open(path + 'icon/' + HeroList[freeHeroListId[i*10+j]]['alias'] + '.png').convert('RGBA')
            except:
                try:
                    iconget = requests.get("https://game.gtimg.cn/images/lol/act/img/champion/"+ HeroList[freeHeroListId[i*10+j]]['alias'] + ".png")
                    temp =  BytesIO(iconget.content)
                    icon = Image.open(temp)
                except:
                    icon = Image.open(path + 'icon/' + 'none_icon.png').convert('RGBA')
                    print(freeHeroListId[i*10+j])
                    print(HeroList[freeHeroListId[i*10+j]]['alias'])
            Hero_BG.paste(icon, (10+140*j, 20+180*i))
            name = HeroList[freeHeroListId[i*10+j]]['name']
            w ,h = tempDraw.textsize(name, font = font)
            tempDraw.text((10+140*j+(120-w)/2, 20+180*i+120), name , (202,196,181), font)
            title = HeroList[freeHeroListId[i*10+j]]['title']
            w ,h = tempDraw.textsize(title, font = font)
            tempDraw.text((10+140*j+(120-w)/2, 20+180*i+150), title , (202,196,181), font)
    Hero_Mask = Image.open(path + '/Hero_Mask.png').convert('RGBA')
    Hero_BG.paste(Hero_Mask, (0,0),mask=Hero_Mask.split()[3])
    await zhoumian.finish(MessageSegment.image(f"base64://{str(image_to_base64(Hero_BG), encoding='utf-8')}"))

ldzhoumian = on_command('大乱斗周免', aliases={"大乱斗免费英雄","乱斗周免"}, priority = 20, block = True)
@ldzhoumian.handle()
async def _(event: Event, message: Message = CommandArg()):
    BullBoard = requests.get("https://lol.qq.com/act/AutoCMS/publish/LOLAct/ZMSubject_Board_Site/ZMSubject_Board_Site.js")
    text_re = re.match("(.+)return(.+)}\);(.+)", BullBoard.text)
    hero_all = json.loads(text_re.groups()[1][:-1])
    heroGet = requests.get("https://game.gtimg.cn/images/lol/act/img/js/heroList/hero_list.js")
    HeroList = json.loads(heroGet.text)['hero']
    k = 0
    for i in hero_all.keys():
        if int(i) > k:
            k = int(i)
    fightHero = json.loads('[' + hero_all[str(k)]['fightHero'] + ']')
    fightHeroId = []
    for i in range(0,len(fightHero)):
        for j in range(0,len(HeroList)):
            if int(HeroList[j]['heroId']) == fightHero[i]:
                fightHeroId.append(j)
                break
    ARAM_BG = Image.open(path + '/ARAM_BG.png').convert('RGBA')
    tempDraw = ImageDraw.Draw(ARAM_BG)
    font = ImageFont.truetype(path[:-4] + 'Tahoma.ttf', 20, encoding='utf-8')
    for i in range(0,5):
        for j in range(0,10):
            try:
                icon = Image.open(path + 'icon/' + HeroList[fightHeroId[i*10+j]]['alias'] + '.png').convert('RGBA')
            except:
                icon = Image.open(path + 'icon/' + 'none_icon.png').convert('RGBA')
                print(fightHeroId[i*10+j])
                print(HeroList[fightHeroId[i*10+j]]['alias'])
            ARAM_BG.paste(icon, (10+140*j, 20+180*i))
            name = HeroList[fightHeroId[i*10+j]]['name']
            w ,h = tempDraw.textsize(name, font = font)
            tempDraw.text((10+140*j+(120-w)/2, 20+180*i+120), name , (202,196,181), font)
            title = HeroList[fightHeroId[i*10+j]]['title']
            w ,h = tempDraw.textsize(title, font = font)
            tempDraw.text((10+140*j+(120-w)/2, 20+180*i+150), title , (202,196,181), font)
    i = 5
    for j in range(0,2):
        try:
            icon = Image.open(path + 'icon/' + HeroList[fightHeroId[i*10+j]]['alias'] + '.png').convert('RGBA')
        except:
            icon = Image.open(path + 'icon/' + 'none_icon.png').convert('RGBA')
            print(fightHeroId[i*10+j])
            print(HeroList[fightHeroId[i*10+j]]['alias'])
        ARAM_BG.paste(icon, (10+140*j, 20+180*i))
        name = HeroList[fightHeroId[i*10+j]]['name']
        w ,h = tempDraw.textsize(name, font = font)
        tempDraw.text((10+140*j+(120-w)/2, 20+180*i+120), name , (202,196,181), font)
        title = HeroList[fightHeroId[i*10+j]]['title']
        w ,h = tempDraw.textsize(title, font = font)
        tempDraw.text((10+140*j+(120-w)/2, 20+180*i+150), title , (202,196,181), font)

    ARAM_Mask = Image.open(path + '/ARAM_Mask.png').convert('RGBA')
    ARAM_BG.paste(ARAM_Mask, (0,0),mask=ARAM_Mask.split()[3])
    await ldzhoumian.finish(MessageSegment.image(f"base64://{str(image_to_base64(ARAM_BG), encoding='utf-8')}"))