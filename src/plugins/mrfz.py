from nonebot import on_command, on_regex, on_keyword, on_message
from nonebot.params import CommandArg, EventMessage
from nonebot.adapters import Event
from nonebot.adapters.onebot.v11 import Message, MessageSegment, exception
from nonebot.matcher import Matcher

from src.libraries.image import *
import os,glob,random,base64

mrfz_dir = 'src/static/mrfz/'
lihui = on_command('zlh', aliases={'舟立绘'}, priority=40, block=True)


@lihui.handle()
async def _(event: Event, message: Message = CommandArg()):
    argv = str(message).strip().split(" ")
    if len(argv) > 0 and len(argv) < 3:
        fpath_list = glob.glob(mrfz_dir + f"立绘_{argv[0]}_*.png")
        if len(fpath_list) == 0:
            fpath_list = glob.glob(mrfz_dir + f"立绘_*{argv[0]}*_*.png")
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