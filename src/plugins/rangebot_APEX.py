import time,requests
from PIL import Image,ImageDraw,ImageFont

from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message, Event, MessageSegment
from src.libraries.secrets import APEX_API_key

from src.libraries.image import *

DEFAULT_PRIORITY = 40

path = 'src/static/apex/'
map_aliases = {"Kings Canyon": "猪王峡谷","World's Edge": "世界尽头","Olympus": "奥林匹斯","Storm Point": "风暴点","Broken Moon":"破碎月球"}

"""-----------APEX地图轮换-----------"""   
Map_rotation = on_command('APEX地图轮换',aliases={"apex地图轮换","Apex地图轮换"}, priority = DEFAULT_PRIORITY, block = True)
@Map_rotation.handle()
async def _(event: Event, message: Message = CommandArg()):
    resp = requests.get(r"https://api.mozambiquehe.re/maprotation?auth=" + APEX_API_key)
    if resp.status_code in [400,403,404,405,410,429,500]:
        await Map_rotation.finish(Message([
        {
            "type": "text",
            "data": {
                "text": "请求失败，code：" + str(resp.status_code)
            }
        }
        ]))
    temp = resp.json()
    map1, map2 = temp['current']['map'], temp['next']['map']
    img1 = Image.open(path + '/maps/' + map1 + '.jpg')
    img2 = Image.open(path + '/maps/' + map2 + '.jpg')
    font = ImageFont.truetype(path[:-5] + 'Tahoma.ttf', 30, encoding='utf-8')

    imgdraw = ImageDraw.Draw(img1)
    imgdraw.text((22,22), "当前地图" , (0,0,0), font)
    imgdraw.text((20,20), "当前地图" , (255,255,255), font)
    remainingTimer = '剩余时间：' + temp['current']['remainingTimer']
    w, h = imgdraw.textsize(remainingTimer, font = font)
    imgdraw.text((img1.size[0] - w - 18,22), remainingTimer , (0,0,0), font)
    imgdraw.text((img1.size[0] - w - 20,20), remainingTimer , (255,255,255), font)
    imgdraw.text((22,img1.size[1] - h - 18), map_aliases[temp['current']['map']] , (0,0,0), font)
    imgdraw.text((20,img1.size[1] - h - 20), map_aliases[temp['current']['map']] , (255,255,255), font)


    imgdraw = ImageDraw.Draw(img2)
    imgdraw.text((22,22), "下一张地图" , (0,0,0), font)
    imgdraw.text((20,20), "下一张地图" , (255,255,255), font)
    start, end = time.localtime(temp['next']['start']), time.localtime(temp['next']['end'])
    startTimers = '开始时间：' + time.strftime("%H:%M:%S", start)
    endTimers = '结束时间：' + time.strftime("%H:%M:%S", end)
    w, h = imgdraw.textsize(startTimers, font = font)
    imgdraw.text((22,img2.size[1] - h - 18), map_aliases[temp['next']['map']] , (0,0,0), font)
    imgdraw.text((20,img2.size[1] - h - 20), map_aliases[temp['next']['map']] , (255,255,255), font)
    imgdraw.text((img2.size[0] - w - 18,22), startTimers , (0,0,0), font)
    imgdraw.text((img2.size[0] - w - 20,20), startTimers , (255,255,255), font)
    imgdraw.text((img2.size[0] - w - 18,42 + h), endTimers , (0,0,0), font)
    imgdraw.text((img2.size[0] - w - 20,40 + h), endTimers , (255,255,255), font)

    w, h = img1.size[0], img1.size[1] + img2.size[1]
    img = Image.new("RGB",(w,h))
    img.paste(img1)
    img.paste(img2,(0,img1.size[1]))
    await Map_rotation.finish(MessageSegment.image(f"base64://{str(image_to_base64(img), encoding='utf-8')}"))