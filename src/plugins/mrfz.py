from nonebot import on_command, on_regex, on_keyword, on_message
from nonebot.params import CommandArg, EventMessage
from nonebot.adapters import Event
from nonebot.adapters.onebot.v11 import Message, MessageSegment

from src.libraries.image import *
from src.libraries.secrets import *

from PIL import Image
from io import BytesIO
import glob, random, base64, requests, os, time

DEFAULT_PRIORITY = 40

mrfz_dir = 'src/static/mrfz/'

lihui = on_command('zlh', aliases={'舟立绘'}, priority=DEFAULT_PRIORITY, block=True)
@lihui.handle()
async def _(message: Message = CommandArg()):
    argv = str(message).strip().split(" ")
    if len(argv) > 0 and len(argv) < 3:
        fpath_list = glob.glob(mrfz_dir + f"lihui/立绘_{argv[0]}_*.png")
        if len(fpath_list) == 0:
            fpath_list = glob.glob(mrfz_dir + f"lihui/立绘_*{argv[0]}*_*.png")
            if len(fpath_list) == 0:
                await lihui.finish("没有找到这样的干员，目前只支持干员精确中文名查询")
        try:
            if argv[1] in ["1", "2"]:
                fpath = random.choice(
                    [f for f in fpath_list if f"_{argv[1]}.png" in f])
            elif argv[1] in ["皮肤", "皮", "skin"]:
                fpath = random.choice(
                    [f for f in fpath_list if "skin" in f])
        except:
            fpath = random.choice(fpath_list)
        with open(fpath, 'rb') as fp:
            encoded = base64.b64encode(fp.read())
        url = "base64://" + encoded.decode('utf-8')
        await lihui.finish(MessageSegment.image(url))

cailiao = on_command('舟材料', aliases={'zcl'}, priority=DEFAULT_PRIORITY, block=True)
@cailiao.handle()
async def _(message: Message = CommandArg()):
    if str(message).strip() != "":
        return
    
    try:
        if os.path.getmtime(mrfz_dir + '材料.png') < time.time() - 86400:
            os.remove(mrfz_dir + '材料.png')
    except:
        pass

    if os.path.exists(mrfz_dir + '材料.png'):
        await cailiao.finish(MessageSegment.image(f"base64://{str(image_to_base64(Image.open(mrfz_dir + '材料.png')), encoding='utf-8')}"))

    else:
        html_to_img_url = f"http://{TENCENT_CLOUD_IP}:{HTML_TO_IMAGE_PORT}/screenshot"
        key = HTML_TO_IMAGE_KEY
        params = {
            'url': 'http://yituliu.site',
            'key': key, 
            'w': '1000', 
            'h': '1321'
            }
        res = requests.get(html_to_img_url, params=params)
        if res.status_code != 200:
            await cailiao.finish("渲染失败")
        else:
            img = Image.open(BytesIO(res.content))
            img = img.crop((0,134,1000,885))
            img.save(mrfz_dir + '材料.png')
            await cailiao.finish(MessageSegment.image(f"base64://{str(image_to_base64(img), encoding='utf-8')}"))

shuaxincailiao = on_command('刷新舟材料', priority=40, block=True, rule=range_checker)
@shuaxincailiao.handle()
async def _():
    html_to_img_url = f"http://{TENCENT_CLOUD_IP}:{HTML_TO_IMAGE_PORT}/screenshot"
    key = HTML_TO_IMAGE_KEY
    params = {
        'url': 'http://yituliu.site',
        'key': key, 
        'w': '1000', 
        'h': '1321'
        }
    res = requests.get(html_to_img_url, params=params)
    if res.status_code != 200:
        await cailiao.finish("渲染失败")
    else:
        img = Image.open(BytesIO(res.content))
        img = img.crop((0,134,1000,885))
        img.save(mrfz_dir + '材料.png')
        await cailiao.finish(MessageSegment.image(f"base64://{str(image_to_base64(img), encoding='utf-8')}"))