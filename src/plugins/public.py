from nonebot import on_command
from nonebot.typing import T_State
from nonebot.adapters.onebot.v11 import Event, Bot, MessageSegment
from src.libraries.image import *


# @event_preprocessor
# async def preprocessor(bot, event, state):
#     if hasattr(event, 'message_type') and event.message_type == "private" and event.sub_type != "friend":
#         raise IgnoredException("not reply group temp message")

    

help = on_command('help', priority = 5, block = True)

@help.handle()
async def _(bot: Bot, event: Event, state: T_State):
    help_str = '''diving-fish功能：
b40 b50 —》 查分
今日舞萌/今日mai —》 查看今天的舞萌运势
XXXmaimaiXXX什么 —》 随机一首歌
随个[dx/标准][绿黄红紫白]<等级> —》 随机一首指定条件的乐曲
查歌<乐曲标题的一部分> —》 查询符合条件的乐曲
[绿黄红紫白]id<歌曲编号> —》 查询乐曲信息或谱面信息
<歌曲别名>是什么歌 —》 查询乐曲别名对应的乐曲
定数查歌 <定数> —》 查询定数对应的乐曲
定数查歌 <定数下限> <定数上限> —》 查询定数范围对应的乐曲
分数线 <难度+歌曲id> <分数线> —》 详情请输入“分数线 帮助”查看

其他maimai功能：
谱师查歌 <谱师名字的一部分> -》 按谱师名字查歌
曲师查歌 <曲师名字的一部分> -》 按曲师名字查歌
新歌查歌 -》 按新歌列表查歌
bpm查歌 <bpm> 或 bpm查歌 <bpm上限> <bpm下限> -》 按bpm查歌
版本查歌 <版本> -》 按版本查歌
<等级/版本>进度 -》 查询完成度
info<歌曲id/歌曲名称> -》 查询该歌曲成绩

chuni功能：
cb30 -》 查分
今日中二/今日chuni —》 查看今天的舞萌运势
XXX中二XXX什么 —》 随机一首歌
c随个[绿黄红紫白]<等级> —》 随机一首指定条件的乐曲
c查歌<乐曲标题的一部分> —》 查询符合条件的乐曲
cr查歌<乐曲标题的一部分> —》 查询符合条件的乐曲（日服列表）
c[绿黄红紫白]id<歌曲编号> —》 查询乐曲信息或谱面信息
crid<歌曲编号> —》 查询乐曲信息（日服列表，无不同难度谱面信息）
c定数查歌 <定数> -》 查询定数对应的乐曲
c定数查歌 <定数下限> <定数上限> -》 查询定数范围对应的乐曲
c谱师查歌 <谱师名字的一部分> -》 按谱师名字查歌
c曲师查歌 <曲师名字的一部分> -》 按曲师名字查歌
cbpm查歌 <bpm> 或 cbpm查歌 <bpm上限> <bpm下限> -》 按bpm查歌
c版本查歌 <版本> -》 按版本查歌

Range功能：
来个龙图/来张龙图 —》 随机龙图
range XXX还是XXX —》 帮你做选择
lol周免 -》 查询lol周免
大乱斗周免-》 查询lol大乱斗周免
apex地图轮换 -》 查询apex地图轮换（制造轮换等其它信息开发中）
zlh/舟立绘 <干员名> -》 查询明日方舟干员立绘
zlh/舟立绘 <干员名> <皮肤> -》 查询明日方舟干员皮肤立绘
zlh/舟立绘 <干员名> <1/2> -》 查询明日方舟干员普通/精2立绘

备注：
自定义头像，牌子，联系CDRange，不可自定义清谱牌子
别名表搞不动了不搞了
DX以后的查牌子不准，暂时没空写
中二的master以上难度也叫白，懒得改了。
单曲成绩和查牌子查等级完成度采用缓存机制，每天第一次查询刷新缓存，之后查询使用缓存。
如果发现成绩不同步请发送 刷新成绩 
b40/b50无需刷新，同步水鱼'''
    await help.finish(MessageSegment.image(f"base64://{str(image_to_base64(text_to_image(help_str)), encoding='utf-8')}"))