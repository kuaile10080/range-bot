# Author: xyb, Diving_Fish

import os, aiohttp, random, heapq
from typing import Optional, Dict, List, Tuple
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from src.libraries.maimaidx_music import total_list, compute_ra
from src.libraries.image import get_music_cover, get_qq_logo
from src.libraries.static_lists_and_dicts import platename_to_file, pnconvert
from src.libraries.tool import is_fools_day

scoreRank = 'D C B BB BBB A AA AAA S S+ SS SS+ SSS SSS+'.split(' ')
combo = ' FC FC+ AP AP+'.split(' ')
diffs = 'Basic Advanced Expert Master Re:Master'.split(' ')

class ChartInfo(object):
    def __init__(self, idNum:str, diff:int, tp:str, achievement:float, ra:int, comboId:int, scoreId:int,
                 title:str, ds:float, lv:str):
        self.idNum = idNum
        self.diff = diff
        self.tp = tp
        self.achievement = achievement
        self.comboId = comboId
        self.scoreId = scoreId
        self.title = title
        self.ds = ds
        self.lv = lv
        self.ra = compute_ra(ds, achievement, b50=False)

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
        return cls(
            idNum=data["song_id"],
            title=data["title"],
            diff=data["level_index"],
            ra=compute_ra(float(data["ds"]), float(data["achievements"]), b50=False),
            ds=data["ds"],
            comboId=fi,
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

    def __init__(self, sdBest:BestList, dxBest:BestList, nickname:str, plate:str, qq:str):
        self.sdBest = sdBest
        self.dxBest = dxBest
        if nickname == None or nickname == "":
            self.nickname = "舞萌DX"
        else:
            self.nickname = self._stringQ2B(nickname)
        self.plate = ""
        for c in plate:
            if c in pnconvert:
                self.plate += pnconvert[c]
            else:
                self.plate += c
        self.qq = qq
        self.sdRating = 0
        self.dxRating = 0
        for sd in sdBest:
            sd.ra = compute_ra(float(sd.ds), float(sd.achievement), b50=False)
            self.sdRating += sd.ra
        for dx in dxBest:
            dx.ra = compute_ra(float(dx.ds), float(dx.achievement), b50=False)
            self.dxRating += dx.ra
        self.playerRating = self.sdRating + self.dxRating
        self.musicRating = self.playerRating
        self.rankRating = self.playerRating
        #self.musicRating = musicRating
        #self.rankRating = self.playerRating - self.musicRating
        self.pic_dir = 'src/static/mai/pic/'
        self.cover_dir = 'src/static/mai/cover/'
        self.plate_dir = 'src/static/mai/plate/'
        self.icon_dir = 'src/static/mai/icon/'
        self.temp_dir = 'src/static/mai/temp/'
        self.img = Image.open(self.pic_dir + 'UI_TTR_BG_Base_Plus.png').convert('RGBA')
        self.ROWS_IMG = [2]
        for i in range(6):
            self.ROWS_IMG.append(116 + 96 * i)
        self.COLOUMS_IMG = []
        for i in range(6):
            self.COLOUMS_IMG.append(2 + 172 * i)
        for i in range(4):
            self.COLOUMS_IMG.append(888 + 172 * i)
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
        num = '10'
        if self.playerRating < 1000:
            num = '01'
        elif self.playerRating < 2000:
            num = '02'
        elif self.playerRating < 3000:
            num = '03'
        elif self.playerRating < 4000:
            num = '04'
        elif self.playerRating < 5000:
            num = '05'
        elif self.playerRating < 6000:
            num = '06'
        elif self.playerRating < 7000:
            num = '07'
        elif self.playerRating < 8000:
            num = '08'
        elif self.playerRating < 8500:
            num = '09'
        return f'UI_CMN_DXRating_S_{num}.png'

    def _drawRating(self, ratingBaseImg:Image.Image):
        COLOUMS_RATING = [86, 100, 115, 130, 145]
        theRa = self.playerRating
        i = 4

        if is_fools_day():
            theRa += 10000

        while theRa:
            digit = theRa % 10
            theRa = theRa // 10
            digitImg = Image.open(self.pic_dir + f'UI_NUM_Drating_{digit}.png').convert('RGBA')
            digitImg = self._resizePic(digitImg, 0.6)
            ratingBaseImg.paste(digitImg, (COLOUMS_RATING[i] - 2, 9), mask=digitImg.split()[3])
            i = i - 1
        return ratingBaseImg

    def _drawBestList(self, img:Image.Image, sdBest:BestList, dxBest:BestList):
        itemW = 164
        itemH = 88
        Color = [(69, 193, 36), (255, 186, 1), (255, 90, 102), (134, 49, 200), (217, 197, 233)]
        levelTriagle = [(itemW, 0), (itemW - 27, 0), (itemW, 27)]
        rankPic = 'D C B BB BBB A AA AAA S Sp SS SSp SSS SSSp'.split(' ')
        comboPic = ' FC FCp AP APp'.split(' ')
        imgDraw = ImageDraw.Draw(img)
        titleFontName = 'src/static/adobe_simhei.otf'
        for num in range(0, len(sdBest)):
            i = num // 5
            j = num % 5
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
                title = self._changeColumnWidth(title, 14) + '...'
            tempDraw.text((8, 8), title, 'white', font)
            font = ImageFont.truetype(titleFontName, 14, encoding='utf-8')
            
            if is_fools_day():
                tempDraw.text((7, 28), f'{"%d" % int(chartInfo.achievement*10000)}%', 'red', font)
            else:
                tempDraw.text((7, 28), f'{"%.4f" % chartInfo.achievement}%', 'white', font)
                
            rankImg = Image.open(self.pic_dir + f'UI_GAM_Rank_{rankPic[chartInfo.scoreId]}.png').convert('RGBA')
            rankImg = self._resizePic(rankImg, 0.3)
            temp.paste(rankImg, (88, 28), rankImg.split()[3])
            if chartInfo.comboId:
                comboImg = Image.open(self.pic_dir + f'UI_MSS_MBase_Icon_{comboPic[chartInfo.comboId]}_S.png').convert('RGBA')
                comboImg = self._resizePic(comboImg, 0.45)
                temp.paste(comboImg, (119, 27), comboImg.split()[3])
            font = ImageFont.truetype('src/static/adobe_simhei.otf', 12, encoding='utf-8')
            tempDraw.text((8, 44), f'Base: {chartInfo.ds} -> {chartInfo.ra}', 'white', font)
            font = ImageFont.truetype('src/static/adobe_simhei.otf', 18, encoding='utf-8')
            tempDraw.text((8, 60), f'#{num + 1}', 'white', font)

            recBase = Image.new('RGBA', (itemW, itemH), 'black')
            recBase = recBase.point(lambda p: int(p * 0.8))
            img.paste(recBase, (self.COLOUMS_IMG[j] + 5, self.ROWS_IMG[i + 1] + 5))
            img.paste(temp, (self.COLOUMS_IMG[j] + 4, self.ROWS_IMG[i + 1] + 4))
        for num in range(len(sdBest), sdBest.size):
            i = num // 5
            j = num % 5
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
            font = ImageFont.truetype(titleFontName, 16, encoding='utf-8')
            title = chartInfo.title
            if self._coloumWidth(title) > 15:
                title = self._changeColumnWidth(title, 14) + '...'
            tempDraw.text((8, 8), title, 'white', font)
            font = ImageFont.truetype(titleFontName, 14, encoding='utf-8')

            if is_fools_day():
                tempDraw.text((7, 28), f'{"%d" % int(chartInfo.achievement*10000)}%', 'red', font)
            else:
                tempDraw.text((7, 28), f'{"%.4f" % chartInfo.achievement}%', 'white', font)

            rankImg = Image.open(self.pic_dir + f'UI_GAM_Rank_{rankPic[chartInfo.scoreId]}.png').convert('RGBA')
            rankImg = self._resizePic(rankImg, 0.3)
            temp.paste(rankImg, (88, 28), rankImg.split()[3])
            if chartInfo.comboId:
                comboImg = Image.open(self.pic_dir + f'UI_MSS_MBase_Icon_{comboPic[chartInfo.comboId]}_S.png').convert(
                    'RGBA')
                comboImg = self._resizePic(comboImg, 0.45)
                temp.paste(comboImg, (119, 27), comboImg.split()[3])
            font = ImageFont.truetype('src/static/adobe_simhei.otf', 12, encoding='utf-8')
            tempDraw.text((8, 44), f'Base: {chartInfo.ds} -> {chartInfo.ra}', 'white', font)
            font = ImageFont.truetype('src/static/adobe_simhei.otf', 18, encoding='utf-8')
            tempDraw.text((8, 60), f'#{num + 1}', 'white', font)

            recBase = Image.new('RGBA', (itemW, itemH), 'black')
            recBase = recBase.point(lambda p: int(p * 0.8))
            img.paste(recBase, (self.COLOUMS_IMG[j + 6] + 5, self.ROWS_IMG[i + 1] + 5))
            img.paste(temp, (self.COLOUMS_IMG[j + 6] + 4, self.ROWS_IMG[i + 1] + 4))
        for num in range(len(dxBest), dxBest.size):
            i = num // 3
            j = num % 3
            temp = Image.open(self.cover_dir + f'00000.png').convert('RGB')
            temp = self._resizePic(temp, itemW / temp.size[0])
            temp = temp.crop((0, (temp.size[1] - itemH) / 2, itemW, (temp.size[1] + itemH) / 2))
            temp = temp.filter(ImageFilter.GaussianBlur(1))
            img.paste(temp, (self.COLOUMS_IMG[j + 6] + 4, self.ROWS_IMG[i + 1] + 4))

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
        nameDxImg = Image.open(self.pic_dir + 'UI_CMN_Name_DX.png').convert('RGBA')
        nameDxImg = self._resizePic(nameDxImg, 0.9)
        namePlateImg.paste(nameDxImg, (200, 0), mask=nameDxImg.split()[3])
        self.img.paste(namePlateImg, (119, 47), mask=namePlateImg.split()[3])

        shougouImg = Image.open(self.pic_dir + 'UI_CMN_Shougou_Rainbow.png').convert('RGBA')
        shougouDraw = ImageDraw.Draw(shougouImg)
        font2 = ImageFont.truetype('src/static/adobe_simhei.otf', 14, encoding='utf-8')
        playCountInfo = f'{self.musicRating}'
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
        self.img.paste(dxImg, (890, 65), mask=dxImg.split()[3])
        sdImg = Image.open(self.pic_dir + 'UI_RSL_MBase_Parts_02.png').convert('RGBA')
        imgdraw = ImageDraw.Draw(sdImg)
        imgdraw.text((17,22), "b25:" + str(self.sdRating) , (0,0,0), font)
        self.img.paste(sdImg, (758, 65), mask=sdImg.split()[3])

        # self.img.show()

    def getDir(self):
        return self.img

async def generate(payload: Dict) -> Tuple[Optional[Image.Image], int]:
    async with aiohttp.request("POST", "https://www.diving-fish.com/api/maimaidxprober/query/player", json=payload) as resp:
        if resp.status == 400:
            return None, 400
        if resp.status == 403:
            return None, 403
        sd_best = BestList(25)
        dx_best = BestList(15)
        obj = await resp.json()
        dx: List[Dict] = obj["charts"]["dx"]
        sd: List[Dict] = obj["charts"]["sd"]
        # if len(dx) == 0 and len(sd) == 0:
        #     return None, 404
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
        pic = DrawBest(sd_best, dx_best, obj["nickname"], obj["plate"], qq).getDir()
        return pic, 0

async def generateap40(player_data,qq) -> Image.Image:
    sd_best = BestList(25)
    dx_best = BestList(15)
    for rec in player_data['records']:
        if rec['fc'] in ['ap','app']:
            if total_list.by_id(rec["song_id"]).cn_version == "舞萌DX2024":
                dx_best.push(ChartInfo.from_json(rec))
            else:
                sd_best.push(ChartInfo.from_json(rec))
    sd_best.sort()
    dx_best.sort()
    pic = DrawBest(sd_best, dx_best, player_data["nickname"], player_data["plate"], qq).getDir()
    return pic

async def generateb40_by_player_data(player_data,qq) -> Image.Image:
    sd_best = BestList(25)
    dx_best = BestList(15)
    for rec in player_data['records']:
        if total_list.by_id(rec["song_id"]).cn_version == "舞萌DX2024":
            dx_best.push(ChartInfo.from_json(rec))
        else:
            sd_best.push(ChartInfo.from_json(rec))
    sd_best.sort()
    dx_best.sort()
    pic = DrawBest(sd_best, dx_best, player_data["nickname"], player_data["plate"], qq).getDir()
    return pic