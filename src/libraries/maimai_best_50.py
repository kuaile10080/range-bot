# Author: xyb, Diving_Fish

import os, aiohttp, random, heapq
from typing import Optional, Dict, List, Tuple
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from src.libraries.maimaidx_music import total_list, compute_ra
from src.libraries.image import get_music_cover, get_qq_logo
from src.libraries.static_lists_and_dicts import platename_to_file

scoreRank = 'D C B BB BBB A AA AAA S S+ SS SS+ SSS SSS+'.split(' ')
combo = ' FC FC+ AP AP+'.split(' ')
diffs = 'Basic Advanced Expert Master Re:Master'.split(' ')



class ChartInfo(object):
    def __init__(self, idNum:str, diff:int, tp:str, achievement:float, ra:int, comboId:int, fsId:int, scoreId:int,
                 title:str, ds:float, lv:str):
        self.idNum = idNum
        self.diff = diff
        self.tp = tp
        self.achievement = achievement
        self.ra = compute_ra(ds,achievement)
        self.comboId = comboId
        self.fsId = fsId
        self.scoreId = scoreId
        self.title = title
        self.ds = ds
        self.lv = lv

    def __str__(self):
        return '%-50s' % f'{self.title} [{self.tp}]' + f'{self.ds}\t{diffs[self.diff]}\t{self.ra}'

    def __eq__(self, other):
        return self.ra == other.ra

    def __lt__(self, other):
        return self.ra < other.ra

    @classmethod
    def from_json(cls, data):
        rate = ['d', 'c', 'b', 'bb', 'bbb', 'a', 'aa', 'aaa', 's', 'sp', 'ss', 'ssp', 'sss', 'sssp']
        ri = rate.index(data["rate"])
        fc = ['', 'fc', 'fcp', 'ap', 'app']
        fi = fc.index(data["fc"])
        fs = ['', 'fs', 'fsp', 'fsd', 'fsdp']
        fsi = fs.index(data["fs"])
        return cls(
            idNum=total_list.by_title(data["title"]).id,
            title=data["title"],
            diff=data["level_index"],
            ra=data["ra"],
            ds=data["ds"],
            comboId=fi,
            fsId=fsi,
            scoreId=ri,
            lv=data["level"],
            achievement=data["achievements"],
            tp=data["type"]
        )



class BestList(object):

    def __init__(self, size:int):
        self.data = []
        self.size = size

    def push(self, elem:ChartInfo):
        if len(self.data) >= self.size and elem < self.data[0]:
            return
        heapq.heappush(self.data, elem)
        while len(self.data) > self.size:
            heapq.heappop(self.data)

    def pop(self):
        heapq.heappop(self.data)

    def sort(self):
        self.data.sort(reverse=True)

    def __str__(self):
        return '[\n\t' + ', \n\t'.join([str(ci) for ci in self.data]) + '\n]'

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        return self.data[index]


class DrawBest(object):

    def __init__(self, sdBest:BestList, dxBest:BestList, nickname:str, plate:str, qq:str, additional_rating:int):
        self.sdBest = sdBest
        self.dxBest = dxBest
        self.nickname = self._stringQ2B(nickname)
        self.plate = plate
        self.qq = qq
        self.adr = additional_rating
        self.sdRating = 0
        self.dxRating = 0
        for sd in sdBest:
            self.sdRating += compute_ra(sd.ds, sd.achievement)
        for dx in dxBest:
            self.dxRating += compute_ra(dx.ds, dx.achievement)
        self.playerRating = self.sdRating + self.dxRating
        self.pic_dir = 'src/static/mai/pic/'
        self.cover_dir = 'src/static/mai/cover/'
        self.plate_dir = 'src/static/mai/plate/'
        self.icon_dir = 'src/static/mai/icon/'
        self.rank_dir = 'src/static/mai/rank/'
        self.temp_dir = 'src/static/mai/temp/'
        self.img = Image.open(self.pic_dir + 'UI_TTR_BG_Base_Plus.png').convert('RGBA')
        self.ROWS_IMG = [2]
        for i in range(6):
            self.ROWS_IMG.append(116 + 96 * i)
        self.COLOUMS_IMG = []
        for i in range(8):
            self.COLOUMS_IMG.append(2 + 138 * i)
        for i in range(4):
            self.COLOUMS_IMG.append(988 + 138 * i)
        self.draw()

    def _Q2B(self, uchar):
        """单个字符 全角转半角"""
        inside_code = ord(uchar)
        if inside_code == 0x3000:
            inside_code = 0x0020
        else:
            inside_code -= 0xfee0
        if inside_code < 0x0020 or inside_code > 0x7e: #转完之后不是半角字符返回原来的字符
            return uchar
        return chr(inside_code)

    def _stringQ2B(self, ustring):
        """把字符串全角转半角"""
        return "".join([self._Q2B(uchar) for uchar in ustring])

    def _getCharWidth(self, o) -> int:
        widths = [
            (126, 1), (159, 0), (687, 1), (710, 0), (711, 1), (727, 0), (733, 1), (879, 0), (1154, 1), (1161, 0),
            (4347, 1), (4447, 2), (7467, 1), (7521, 0), (8369, 1), (8426, 0), (9000, 1), (9002, 2), (11021, 1),
            (12350, 2), (12351, 1), (12438, 2), (12442, 0), (19893, 2), (19967, 1), (55203, 2), (63743, 1),
            (64106, 2), (65039, 1), (65059, 0), (65131, 2), (65279, 1), (65376, 2), (65500, 1), (65510, 2),
            (120831, 1), (262141, 2), (1114109, 1),
        ]
        if o == 0xe or o == 0xf:
            return 0
        for num, wid in widths:
            if o <= num:
                return wid
        return 1

    def _coloumWidth(self, s:str):
        res = 0
        for ch in s:
            res += self._getCharWidth(ord(ch))
        return res

    def _changeColumnWidth(self, s:str, len:int) -> str:
        res = 0
        sList = []
        for ch in s:
            res += self._getCharWidth(ord(ch))
            if res <= len:
                sList.append(ch)
        return ''.join(sList)

    def _resizePic(self, img:Image.Image, time:float):
        return img.resize((int(img.size[0] * time), int(img.size[1] * time)))

    def _findRaPic(self) -> str:
        num = '01'
        if self.playerRating > 14999:
            num = '11'
        elif self.playerRating > 14499:
            num = '10'
        elif self.playerRating > 13999:
            num = '09'
        elif self.playerRating > 12999:
            num = '08'
        elif self.playerRating > 11999:
            num = '07'
        elif self.playerRating > 9999:
            num = '06'
        elif self.playerRating > 6999:
            num = '05'
        elif self.playerRating > 3999:
            num = '04'
        elif self.playerRating > 1999:
            num = '03'
        elif self.playerRating > 999:
            num = '02'
        return f'UI_CMN_DXRating_S_{num}_2023.png'

    def _drawRating(self, ratingBaseImg:Image.Image):
        COLOUMS_RATING = [86, 100, 115, 130, 145]
        COLOUMS_RATING = [86-5, 100-6, 115-7, 130-8, 145-9]
        theRa = self.playerRating
        i = 4
        while theRa:
            digit = theRa % 10
            theRa = theRa // 10
            digitImg = Image.open(self.pic_dir + f'UI_NUM_Drating_{digit}.png').convert('RGBA')
            digitImg = self._resizePic(digitImg, 0.6)
            ratingBaseImg.paste(digitImg, (COLOUMS_RATING[i] - 2, 9), mask=digitImg.split()[3])
            i = i - 1
        return ratingBaseImg

    def _drawBestList(self, img:Image.Image, sdBest:BestList, dxBest:BestList):
        itemW = 131
        itemH = 88
        Color = [(69, 193, 36), (255, 186, 1), (255, 90, 102), (134, 49, 200), (217, 197, 233)]
        levelTriagle = [(itemW, 0), (itemW - 27, 0), (itemW, 27)]
        rankPic = 'D C B BB BBB A AA AAA S Sp SS SSp SSS SSSp'.split(' ')
        comboPic = ' FC FCp AP APp'.split(' ')
        fsPic = ' FS FSp FSD FSDp'.split(' ')
        imgDraw = ImageDraw.Draw(img)
        titleFontName = 'src/static/adobe_simhei.otf'
        for num in range(0, len(sdBest)):
            i = num // 7
            j = num % 7
            chartInfo = sdBest[num]
            temp = get_music_cover(chartInfo.idNum)
            temp = self._resizePic(temp, itemW / temp.size[0])
            temp = temp.crop((0, (temp.size[1] - itemH) / 2, itemW, (temp.size[1] + itemH) / 2))
            temp = temp.filter(ImageFilter.GaussianBlur(3))
            temp = temp.point(lambda p: int(p * 0.72))

            tempDraw = ImageDraw.Draw(temp)
            tempDraw.polygon(levelTriagle, Color[chartInfo.diff])
            font = ImageFont.truetype(titleFontName, 16, encoding='utf-8')
            title = chartInfo.title
            if self._coloumWidth(title) > 15:
                title = self._changeColumnWidth(title, 12) + '...'
            tempDraw.text((8, 8), title, 'white', font)
            font = ImageFont.truetype(titleFontName, 12, encoding='utf-8')

            tempDraw.text((7, 28), f'{"%.4f" % chartInfo.achievement}%', 'white', font)
            rankImg = Image.open(self.pic_dir + f'UI_GAM_Rank_{rankPic[chartInfo.scoreId]}.png').convert('RGBA')
            rankImg = self._resizePic(rankImg, 0.5)
            temp.paste(rankImg, (50, 61), rankImg.split()[3])
            if chartInfo.comboId:
                comboImg = Image.open(self.pic_dir + f'UI_MSS_MBase_Icon_{comboPic[chartInfo.comboId]}_S.png').convert('RGBA')
                comboImg = self._resizePic(comboImg, 0.6)
                temp.paste(comboImg, (72, 22), comboImg.split()[3])
            if chartInfo.fsId:
                fsImg = Image.open(self.pic_dir + f'UI_MSS_MBase_Icon_{fsPic[chartInfo.fsId]}_S.png').convert('RGBA')
                fsImg = self._resizePic(fsImg, 0.6)
                temp.paste(fsImg, (100, 22), fsImg.split()[3])
            font = ImageFont.truetype('src/static/adobe_simhei.otf', 12, encoding='utf-8')
            tempDraw.text((8, 44), f'Base: {chartInfo.ds} -> {compute_ra(chartInfo.ds, chartInfo.achievement)}', 'white', font)
            font = ImageFont.truetype('src/static/adobe_simhei.otf', 18, encoding='utf-8')
            tempDraw.text((8, 60), f'#{num + 1}', 'white', font)

            recBase = Image.new('RGBA', (itemW, itemH), 'black')
            recBase = recBase.point(lambda p: int(p * 0.8))
            img.paste(recBase, (self.COLOUMS_IMG[j] + 5, self.ROWS_IMG[i + 1] + 5))
            img.paste(temp, (self.COLOUMS_IMG[j] + 4, self.ROWS_IMG[i + 1] + 4))
        for num in range(len(sdBest), sdBest.size):
            i = num // 7
            j = num % 7
            temp = Image.open(self.cover_dir + f'00000.png').convert('RGB')
            temp = self._resizePic(temp, itemW / temp.size[0])
            temp = temp.crop((0, (temp.size[1] - itemH) / 2, itemW, (temp.size[1] + itemH) / 2))
            temp = temp.filter(ImageFilter.GaussianBlur(1))
            img.paste(temp, (self.COLOUMS_IMG[j] + 4, self.ROWS_IMG[i + 1] + 4))
        for num in range(0, len(dxBest)):
            i = num // 3
            j = num % 3
            chartInfo = dxBest[num]
            temp = get_music_cover(chartInfo.idNum)
            temp = self._resizePic(temp, itemW / temp.size[0])
            temp = temp.crop((0, (temp.size[1] - itemH) / 2, itemW, (temp.size[1] + itemH) / 2))
            temp = temp.filter(ImageFilter.GaussianBlur(3))
            temp = temp.point(lambda p: int(p * 0.72))

            tempDraw = ImageDraw.Draw(temp)
            tempDraw.polygon(levelTriagle, Color[chartInfo.diff])
            font = ImageFont.truetype(titleFontName, 14, encoding='utf-8')
            title = chartInfo.title
            if self._coloumWidth(title) > 13:
                title = self._changeColumnWidth(title, 12) + '...'
            tempDraw.text((8, 8), title, 'white', font)
            font = ImageFont.truetype(titleFontName, 12, encoding='utf-8')

            tempDraw.text((7, 28), f'{"%.4f" % chartInfo.achievement}%', 'white', font)
            rankImg = Image.open(self.pic_dir + f'UI_GAM_Rank_{rankPic[chartInfo.scoreId]}.png').convert('RGBA')
            rankImg = self._resizePic(rankImg, 0.5)
            temp.paste(rankImg, (50, 61), rankImg.split()[3])
            if chartInfo.comboId:
                comboImg = Image.open(self.pic_dir + f'UI_MSS_MBase_Icon_{comboPic[chartInfo.comboId]}_S.png').convert('RGBA')
                comboImg = self._resizePic(comboImg, 0.6)
                temp.paste(comboImg, (72, 22), comboImg.split()[3])
            if chartInfo.fsId:
                fsImg = Image.open(self.pic_dir + f'UI_MSS_MBase_Icon_{fsPic[chartInfo.fsId]}_S.png').convert('RGBA')
                fsImg = self._resizePic(fsImg, 0.6)
                temp.paste(fsImg, (100, 22), fsImg.split()[3])
            font = ImageFont.truetype('src/static/adobe_simhei.otf', 12, encoding='utf-8')
            tempDraw.text((8, 44), f'Base: {chartInfo.ds} -> {chartInfo.ra}', 'white', font)
            font = ImageFont.truetype('src/static/adobe_simhei.otf', 18, encoding='utf-8')
            tempDraw.text((8, 60), f'#{num + 1}', 'white', font)

            recBase = Image.new('RGBA', (itemW, itemH), 'black')
            recBase = recBase.point(lambda p: int(p * 0.8))
            img.paste(recBase, (self.COLOUMS_IMG[j + 8] + 5, self.ROWS_IMG[i + 1] + 5))
            img.paste(temp, (self.COLOUMS_IMG[j + 8] + 4, self.ROWS_IMG[i + 1] + 4))
        for num in range(len(dxBest), dxBest.size):
            i = num // 3
            j = num % 3
            temp = Image.open(self.cover_dir + f'00000.png').convert('RGB')
            temp = self._resizePic(temp, itemW / temp.size[0])
            temp = temp.crop((0, (temp.size[1] - itemH) / 2, itemW, (temp.size[1] + itemH) / 2))
            temp = temp.filter(ImageFilter.GaussianBlur(1))
            img.paste(temp, (self.COLOUMS_IMG[j + 8] + 4, self.ROWS_IMG[i + 1] + 4))

    def draw(self):
        if self.plate in platename_to_file:
            PlateImg = Image.open(self.plate_dir + 'main_plate/' + platename_to_file[self.plate]).convert('RGBA')
        else:
            try:
                PlateImg = Image.open(self.plate_dir + 'private_plate/' + self.qq + '.png').convert('RGBA')
            except:
                plates = os.listdir(self.plate_dir + 'other_plate/')
                PlateImg = Image.open(self.plate_dir + 'other_plate/' + random.choice(plates)).convert('RGBA')
        self.img.paste(PlateImg, (5, 3), mask=PlateImg.split()[3])
        
        if self.qq != '0':
            iconLogo = get_qq_logo(self.qq)
        else:
            iconLogo = get_qq_logo(self.qq,mode=0)

        iconLogo = iconLogo.resize((98,98))
        self.img.paste(iconLogo, (14, 12), mask=iconLogo.split()[3])

        ratingBaseImg = Image.open(self.pic_dir + self._findRaPic()).convert('RGBA')
        ratingBaseImg = self._drawRating(ratingBaseImg)
        ratingBaseImg = self._resizePic(ratingBaseImg, 0.95)
        self.img.paste(ratingBaseImg, (119, 10), mask=ratingBaseImg.split()[3])

        namePlateImg = Image.open(self.pic_dir + 'UI_TST_PlateMask.png').convert('RGBA')
        namePlateImg = namePlateImg.resize((253, 32))
        namePlateDraw = ImageDraw.Draw(namePlateImg)
        font1 = ImageFont.truetype('src/static/msyh.ttc', 22, encoding='unic')
        namePlateDraw.text((8, 0), ' '.join(list(self.nickname)), 'black', font1)
        #nameDxImg = Image.open(self.pic_dir + 'UI_CMN_Name_DX.png').convert('RGBA')
        #nameDxImg = self._resizePic(nameDxImg, 0.9)
        #namePlateImg.paste(nameDxImg, (200, 0), mask=nameDxImg.split()[3])
        if self.adr != -1:
            try:
                if self.adr > 10:
                    self.adr += 1
                nameDxImg = Image.open(self.rank_dir + f'UI_DNM_DaniPlate_{self.adr:02d}.png').convert('RGBA')
            except:
                nameDxImg = Image.open(self.rank_dir + 'UI_DNM_DaniPlate_00.png').convert('RGBA')
            nameDxImg = self._resizePic(nameDxImg, 0.2)
            namePlateImg.paste(nameDxImg, (200-30, 0+1), mask=nameDxImg.split()[3])
        self.img.paste(namePlateImg, (119, 47), mask=namePlateImg.split()[3])

        shougouImg = Image.open(self.pic_dir + 'UI_CMN_Shougou_Rainbow.png').convert('RGBA')
        shougouDraw = ImageDraw.Draw(shougouImg)
        font2 = ImageFont.truetype('src/static/adobe_simhei.otf', 14, encoding='utf-8')
        playCountInfo = f'B35: {self.sdRating} + B15: {self.dxRating} = {self.playerRating}'
        shougouImgW, shougouImgH = shougouImg.size
        playCountInfoW, playCountInfoH = shougouDraw.textsize(playCountInfo, font2)
        textPos = ((shougouImgW - playCountInfoW - font2.getoffset(playCountInfo)[0]) / 2, 5)
        shougouDraw.text((textPos[0] - 1, textPos[1]), playCountInfo, 'black', font2)
        shougouDraw.text((textPos[0] + 1, textPos[1]), playCountInfo, 'black', font2)
        shougouDraw.text((textPos[0], textPos[1] - 1), playCountInfo, 'black', font2)
        shougouDraw.text((textPos[0], textPos[1] + 1), playCountInfo, 'black', font2)
        shougouDraw.text((textPos[0] - 1, textPos[1] - 1), playCountInfo, 'black', font2)
        shougouDraw.text((textPos[0] + 1, textPos[1] - 1), playCountInfo, 'black', font2)
        shougouDraw.text((textPos[0] - 1, textPos[1] + 1), playCountInfo, 'black', font2)
        shougouDraw.text((textPos[0] + 1, textPos[1] + 1), playCountInfo, 'black', font2)
        shougouDraw.text(textPos, playCountInfo, 'white', font2)
        shougouImg = self._resizePic(shougouImg, 0.88)
        self.img.paste(shougouImg, (119, 88), mask=shougouImg.split()[3])

        self._drawBestList(self.img, self.sdBest, self.dxBest)

        font3 = ImageFont.truetype('src/static/adobe_simhei.otf', 12, encoding='utf-8')
        authorBoardImg = Image.open(self.pic_dir + 'UI_CMN_MiniDialog_01.png').convert('RGBA')
        authorBoardImg = self._resizePic(authorBoardImg, 0.35)
        authorBoardDraw = ImageDraw.Draw(authorBoardImg)
        authorBoardDraw.text((35, 18), '        Credit to\nXybBot & Chiyuki\n   Generated By\n           Range', 'black', font3)
        self.img.paste(authorBoardImg, (1224, 19), mask=authorBoardImg.split()[3])

        font = ImageFont.truetype('src/static/adobe_simhei.otf', 17, encoding='utf-8')
        dxImg = Image.open(self.pic_dir + 'UI_RSL_MBase_Parts_01.png').convert('RGBA')
        imgdraw = ImageDraw.Draw(dxImg)
        imgdraw.text((17,22), "b15:" + str(self.dxRating) , (0,0,0), font)
        self.img.paste(dxImg, (988, 65), mask=dxImg.split()[3])
        sdImg = Image.open(self.pic_dir + 'UI_RSL_MBase_Parts_02.png').convert('RGBA')
        imgdraw = ImageDraw.Draw(sdImg)
        imgdraw.text((11,22), "b35:" + str(self.sdRating) , (0,0,0), font)
        self.img.paste(sdImg, (865, 65), mask=sdImg.split()[3])

        # self.img.show()

    def getDir(self):
        return self.img


# def computeRa(ds: float, achievement: float) -> int:
#     baseRa = 22.4 
#     if achievement < 50:
#         baseRa = 7.0
#     elif achievement < 60:
#         baseRa = 8.0 
#     elif achievement < 70:
#         baseRa = 9.6 
#     elif achievement < 75:
#         baseRa = 11.2 
#     elif achievement < 80:
#         baseRa = 12.0 
#     elif achievement < 90:
#         baseRa = 13.6 
#     elif achievement < 94:
#         baseRa = 15.2 
#     elif achievement < 97:
#         baseRa = 16.8 
#     elif achievement < 98:
#         baseRa = 20.0 
#     elif achievement < 99:
#         baseRa = 20.3
#     elif achievement < 99.5:
#         baseRa = 20.8 
#     elif achievement < 100:
#         baseRa = 21.1 
#     elif achievement < 100.5:
#         baseRa = 21.6 

#     return math.floor(ds * (min(100.5, achievement) / 100) * baseRa)


async def generate50(payload: Dict) -> Tuple[Optional[Image.Image], int]:
    async with aiohttp.request("POST", "https://www.diving-fish.com/api/maimaidxprober/query/player", json=payload) as resp:
        if resp.status == 400:
            return None, 400
        if resp.status == 403:
            return None, 403
        sd_best = BestList(35)
        dx_best = BestList(15)
        obj = await resp.json()
        dx: List[Dict] = obj["charts"]["dx"]
        sd: List[Dict] = obj["charts"]["sd"]
        for c in sd:
            sd_best.push(ChartInfo.from_json(c))
        for c in dx:
            dx_best.push(ChartInfo.from_json(c))
        sd_best.sort()
        dx_best.sort()
        if 'qq' in payload :
            qq = payload['qq']
        else :
            qq = '0'
        pic = DrawBest(sd_best, dx_best, obj["nickname"], obj["plate"], qq, obj["additional_rating"]).getDir()
        return pic, 0

async def generateap50(player_data,qq) -> Image.Image:
    sd_best = BestList(35)
    dx_best = BestList(15)
    for rec in player_data['records']:
        if rec['fc'] in ['ap','app']:
            if total_list.by_id(rec["song_id"]).cn_version == "舞萌DX2023":
                dx_best.push(ChartInfo.from_json(rec))
            else:
                sd_best.push(ChartInfo.from_json(rec))
    sd_best.sort()
    dx_best.sort()
    pic = DrawBest(sd_best, dx_best, player_data["nickname"], player_data["plate"], qq, player_data["additional_rating"]).getDir()
    return pic

async def generateb50_by_player_data(player_data,qq) -> Image.Image:
    sd_best = BestList(35)
    dx_best = BestList(15)
    for rec in player_data['records']:
        if total_list.by_id(rec["song_id"]).cn_version == "舞萌DX2023":
            dx_best.push(ChartInfo.from_json(rec))
        else:
            sd_best.push(ChartInfo.from_json(rec))
    sd_best.sort()
    dx_best.sort()
    pic = DrawBest(sd_best, dx_best, player_data["nickname"], player_data["plate"], qq, player_data["additional_rating"]).getDir()
    return pic