from nonebot import on_command, on_regex, on_keyword, on_message
from nonebot.params import CommandArg, EventMessage
from nonebot.adapters import Event
from nonebot.adapters.onebot.v11 import Message, MessageSegment

from src.libraries.image import *
from src.libraries.secrets import *

from playwright.async_api import async_playwright
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

#舟材料
zcl_url = "https://ytl.viktorlab.cn/"

cailiao = on_command('舟材料', aliases={'zcl'}, priority=DEFAULT_PRIORITY, block=True)
@cailiao.handle()
async def _(message: Message = CommandArg()):
    if str(message).strip() != "":
        return
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(zcl_url)
        await page.set_viewport_size({"width": 1200, "height": 1080})

        # 等待直到id为"stage_3"的元素出现 
        stage_3_element = await page.wait_for_selector("#stage_3")

        # 当条件满足时，对id为"stage_3"的整个DOM进行截图
        img_bytes = await stage_3_element.screenshot()

        await browser.close()
        
    await cailiao.finish(MessageSegment.image(f"base64://{str(base64.b64encode(img_bytes), encoding='utf-8')}"))