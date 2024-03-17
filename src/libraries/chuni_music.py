import requests,json,os,wget,aiohttp
from typing import Optional, Dict, Tuple
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from src.libraries.maimaidx_music import MusicList,Music,Chart
from src.libraries.image import get_qq_logo

chuni_path = "src/static/chunithm/"

with open(chuni_path + "chuni_music.json","r",encoding="utf-8") as fp:
    chuni_music = json.load(fp)

def get_chuni_json() -> dict:
    try:
        with open(chuni_path + "chuni_music.json","r",encoding='utf-8')as fp:
            chuni_music = json.load(fp)
    except:
        url = "https://chunithm.sega.jp/storage/json/music.json"
        resp = requests.get(url)
        chuni_music = resp.json()
        with open(chuni_path + "chuni_music.json","w",encoding='utf-8')as fp:
            json.dump(chuni_music, fp)
    return chuni_music

def get_chuni_cover(jid:str) -> Image.Image:
    if os.path.exists(chuni_path + f"cover/{jid}.jpg"):
        return Image.open(chuni_path + f"cover/{jid}.jpg").convert("RGB")
    else:
        try:
            for music in chuni_music:
                if music["id"] == jid:
                    image_url = music["image"]
                    break
            url = "https://new.chunithm-net.com/chuni-mobile/html/mobile/img/" + image_url
            path = chuni_path + f"cover/{jid}.jpg"
            wget.download(url, path)
            return Image.open(chuni_path + f"cover/{jid}.jpg").convert("RGB")
        except:
            return Image.open(chuni_path + "cover/0.jpg").convert("RGB")

def get_chuni_cover_by_title(title:str) -> Image.Image:
    flag = False
    for music in chuni_music:
        if music["title"] == title:
            image_url = music["image"]
            jid = music["id"]
            flag = True
            break
    if flag:
        if os.path.exists(chuni_path + f"cover/{jid}.jpg"):
            return Image.open(chuni_path + f"cover/{jid}.jpg").convert("RGB")
        else:
            try:
                url = "https://new.chunithm-net.com/chuni-mobile/html/mobile/img/" + image_url
                path = chuni_path + f"cover/{jid}.jpg"
                wget.download(url, path)
                return Image.open(chuni_path + f"cover/{jid}.jpg").convert("RGB")
            except:
                return Image.open(chuni_path + "cover/0.jpg").convert("RGB")
    else:
        return Image.open(chuni_path + "cover/0.jpg").convert("RGB")

def get_chuni_music_list():
    try:
        mdatafile = open(chuni_path + "chuni_music_g.json", encoding="utf-8")
        obj_data = json.load(mdatafile)
        mdatafile.close()
    except:
        obj_data = requests.get('https://www.diving-fish.com/api/chunithmprober/music_data').json()
    _music_data = obj_data
    _total_list: MusicList = MusicList(obj_data)
    for __i in range(len(_total_list)):
        _total_list[__i] = Music(_total_list[__i])
        for __j in range(len(_total_list[__i].charts)):
            _total_list[__i].charts[__j] = Chart(_total_list[__i].charts[__j])
    return _total_list, _music_data

total_list, music_data = get_chuni_music_list()


#开抄————————————————————————————————————————————————————————————————————————————
chuni_ra_list = [(1009000,215,100,0),
                 (1007500,200,100,1),
                 (1005000,150,50,1),
                 (1000000,100,100,1),
                 (990000,60,250,1),
                 (975000,0,250,1),
                 (925000,-300,100,0.6),
                 (900000,-500,125,1)]

def cal_chuni_ra_int100(score:int,ds:float)->int:
    ds = round(ds*100)
    if score <= 500000:
        res = 0
    elif score <= 800000:
        res = (score-500000)/800000*(ds-500)/2
    elif score <= 900000:
        res = (score-800000)/100000*(ds-500)/2 + (ds-500)/2
    else:
        for i in range(len(chuni_ra_list)):
            if score >= chuni_ra_list[i][0]:
                res = ds + chuni_ra_list[i][1] + (score - chuni_ra_list[i][0])//chuni_ra_list[i][2]*chuni_ra_list[i][3]
                break
    res = int(res)
    return max(0,res)


class DrawChuni(object):
    def __init__(self, b30:list, r10:list, nickname:str, qq:str) -> None:
        self.b30 = b30
        self.r10 = r10
        self.qq = qq
        self.b30ra_int100 = 0
        self.r10ra_int100 = 0
        self.playerRating_int100 = 0
        for song in b30:
            self.b30ra_int100 += cal_chuni_ra_int100(song["score"],song["ds"])
        for song in r10:
            self.r10ra_int100 += cal_chuni_ra_int100(song["score"],song["ds"])
        self.playerRating_int100 = self.b30ra_int100 + self.r10ra_int100
        self.playerRating = self.playerRating_int100//40/100
        if nickname == None or nickname == "":
            self.nickname = "chunithm"
        else:
            self.nickname = self._stringQ2B(nickname)
        self.pic_dir = chuni_path + 'pic/'
        self.icon_dir = chuni_path + 'icon/'
        self.temp_dir = chuni_path + 'temp/'
        self.cover_dir = chuni_path + 'cover/'
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
    
    def _get_rank_by_score(self, score:int) -> str:
        if score >= 1009000:
            return "SSSp"
        elif score >= 1007500:
            return "SSS"
        elif score >= 1005000:
            return "SSp"
        elif score >= 1000000:
            return "SS"
        elif score >= 990000:
            return "Sp"
        elif score >= 975000:
            return "S"
        elif score >= 950000:
            return "AAA"
        elif score >= 925000:
            return "AA"
        elif score >= 900000:
            return "A"
        elif score >= 800000:
            return "BBB"
        elif score >= 700000:
            return "BB"
        elif score >= 600000:
            return "B"
        elif score >= 500000:
            return "C"
        else:
            return "D"

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
        num = '8'
        if self.playerRating < 4.00:
            num = '0'
        elif self.playerRating < 7.00:
            num = '1'
        elif self.playerRating < 10.00:
            num = '2'
        elif self.playerRating < 12.00:
            num = '3'
        elif self.playerRating < 13.25:
            num = '4'
        elif self.playerRating < 14.50:
            num = '5'
        elif self.playerRating < 15.25:
            num = '6'
        elif self.playerRating < 16.00:
            num = '7'
        return f'Rating_{num}.png'

    def _drawBestList(self, img:Image.Image, b30:list, r10:list):
        itemW = 164
        itemH = 88
        Color = [(69, 193, 36), (255, 186, 1), (255, 90, 102), (134, 49, 200), (0, 0, 0)]
        levelTriagle = [(itemW, 0), (itemW - 27, 0), (itemW, 27)]
        imgDraw = ImageDraw.Draw(img)
        comboPic = {"fullcombo":"FC",
                    "fullchain":"FS",
                    "fullchain2":"FSD",
                    "alljustice":"AP"}
        titleFontName = 'src/static/adobe_simhei.otf'
        for num in range(0, len(b30)):
            i = num // 6
            j = num % 6
            chartInfo = b30[num]
            chartInfo["ra"] = cal_chuni_ra_int100(chartInfo["score"],chartInfo["ds"])/100
            temp = get_chuni_cover_by_title(chartInfo["title"])
            temp = self._resizePic(temp, itemW / temp.size[0])
            temp = temp.crop((0, (temp.size[1] - itemH) / 2, itemW, (temp.size[1] + itemH) / 2))
            temp = temp.filter(ImageFilter.GaussianBlur(3))
            temp = temp.point(lambda p: int(p * 0.72))

            tempDraw = ImageDraw.Draw(temp)
            tempDraw.polygon(levelTriagle, Color[chartInfo["level_index"]])
            font = ImageFont.truetype(titleFontName, 16, encoding='utf-8')
            title = chartInfo["title"]
            if self._coloumWidth(title) > 15:
                title = self._changeColumnWidth(title, 14) + '...'
            tempDraw.text((8, 8), title, 'white', font)
            font = ImageFont.truetype(titleFontName, 14, encoding='utf-8')

            tempDraw.text((7, 28), f'{"%d" % chartInfo["score"]}', 'white', font)
            rankImg = Image.open(self.pic_dir + f'UI_GAM_Rank_{self._get_rank_by_score(chartInfo["score"])}.png').convert('RGBA')
            rankImg = self._resizePic(rankImg, 0.3)
            temp.paste(rankImg, (88, 28), rankImg.split()[3])
            if chartInfo["fc"] in comboPic:
                comboImg = Image.open(self.pic_dir + f'UI_MSS_MBase_Icon_{comboPic[chartInfo["fc"]]}_S.png').convert('RGBA')
                comboImg = self._resizePic(comboImg, 0.45)
                temp.paste(comboImg, (119, 27), comboImg.split()[3])
            font = ImageFont.truetype('src/static/adobe_simhei.otf', 12, encoding='utf-8')
            tempDraw.text((8, 44), f'Base: {chartInfo["ds"]} -> {chartInfo["ra"]}', 'white', font)
            font = ImageFont.truetype('src/static/adobe_simhei.otf', 18, encoding='utf-8')
            tempDraw.text((8, 60), f'#{num + 1}', 'white', font)

            recBase = Image.new('RGBA', (itemW, itemH), 'black')
            recBase = recBase.point(lambda p: int(p * 0.8))
            img.paste(recBase, (self.COLOUMS_IMG[j] + 5, self.ROWS_IMG[i + 1] + 5))
            img.paste(temp, (self.COLOUMS_IMG[j] + 4, self.ROWS_IMG[i + 1] + 4))
        for num in range(len(b30), 30):
            i = num // 6
            j = num % 6
            temp = Image.open(self.cover_dir + f'0.jpg').convert('RGB')
            temp = self._resizePic(temp, itemW / temp.size[0])
            temp = temp.crop((0, (temp.size[1] - itemH) / 2, itemW, (temp.size[1] + itemH) / 2))
            temp = temp.filter(ImageFilter.GaussianBlur(1))
            img.paste(temp, (self.COLOUMS_IMG[j] + 4, self.ROWS_IMG[i + 1] + 4))
        for num in range(0, len(r10)):
            i = num // 2
            j = num % 2
            chartInfo = r10[num]
            chartInfo["ra"] = cal_chuni_ra_int100(chartInfo["score"],chartInfo["ds"])/100
            temp = get_chuni_cover_by_title(chartInfo["title"])
            temp = self._resizePic(temp, itemW / temp.size[0])
            temp = temp.crop((0, (temp.size[1] - itemH) / 2, itemW, (temp.size[1] + itemH) / 2))
            temp = temp.filter(ImageFilter.GaussianBlur(3))
            temp = temp.point(lambda p: int(p * 0.72))

            tempDraw = ImageDraw.Draw(temp)
            tempDraw.polygon(levelTriagle, Color[chartInfo["level_index"]])
            font = ImageFont.truetype(titleFontName, 16, encoding='utf-8')
            title = chartInfo["title"]
            if self._coloumWidth(title) > 15:
                title = self._changeColumnWidth(title, 14) + '...'
            tempDraw.text((8, 8), title, 'white', font)
            font = ImageFont.truetype(titleFontName, 14, encoding='utf-8')

            tempDraw.text((7, 28), f'{"%d" % chartInfo["score"]}', 'white', font)
            rankImg = Image.open(self.pic_dir + f'UI_GAM_Rank_{self._get_rank_by_score(chartInfo["score"])}.png').convert('RGBA')
            rankImg = self._resizePic(rankImg, 0.3)
            temp.paste(rankImg, (88, 28), rankImg.split()[3])
            if chartInfo["fc"]:
                comboImg = Image.open(self.pic_dir + f'UI_MSS_MBase_Icon_{comboPic[chartInfo["fc"]]}_S.png').convert('RGBA')
                comboImg = self._resizePic(comboImg, 0.45)
                temp.paste(comboImg, (119, 27), comboImg.split()[3])
            font = ImageFont.truetype('src/static/adobe_simhei.otf', 12, encoding='utf-8')
            tempDraw.text((8, 44), f'Base: {chartInfo["ds"]} -> {chartInfo["ra"]}', 'white', font)
            font = ImageFont.truetype('src/static/adobe_simhei.otf', 18, encoding='utf-8')
            tempDraw.text((8, 60), f'#{num + 1}', 'white', font)

            recBase = Image.new('RGBA', (itemW, itemH), 'black')
            recBase = recBase.point(lambda p: int(p * 0.8))
            img.paste(recBase, (self.COLOUMS_IMG[j + 7] + 5, self.ROWS_IMG[i + 1] + 5))
            img.paste(temp, (self.COLOUMS_IMG[j + 7] + 4, self.ROWS_IMG[i + 1] + 4))
        for num in range(len(r10), 10):
            i = num // 2
            j = num % 2
            temp = Image.open(self.cover_dir + f'0.jpg').convert('RGB')
            temp = self._resizePic(temp, itemW / temp.size[0])
            temp = temp.crop((0, (temp.size[1] - itemH) / 2, itemW, (temp.size[1] + itemH) / 2))
            temp = temp.filter(ImageFilter.GaussianBlur(1))
            img.paste(temp, (self.COLOUMS_IMG[j + 7] + 4, self.ROWS_IMG[i + 1] + 4))

    def draw(self):
        PlateImg = Image.open(chuni_path + "chuni_plate.png").convert('RGBA')
        PlateImg = PlateImg.resize((720,116))
        self.img.paste(PlateImg, (5, 3), mask=PlateImg.split()[3])
        
        if self.qq != '0':
            iconLogo = get_qq_logo(self.qq)
        else:
            iconLogo = get_qq_logo(self.qq,mode=0)

        iconLogo = iconLogo.resize((98,98))
        self.img.paste(iconLogo, (14, 12), mask=iconLogo.split()[3])

        ratingBaseImg = Image.open(self.pic_dir + self._findRaPic()).convert('RGBA')
        ratingBaseDraw = ImageDraw.Draw(ratingBaseImg)
        font1 = ImageFont.truetype('src/static/msyh.ttc', 22, encoding='unic')
        ratingBaseDraw.text((60, 3), f"{self.playerRating}", 'black', font1)
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
        #playCountInfo = f'底分: {self.musicRating} + 段位分: {self.rankRating}'
        playCountInfo = ""
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

        self._drawBestList(self.img, self.b30, self.r10)

        font3 = ImageFont.truetype('src/static/adobe_simhei.otf', 12, encoding='utf-8')
        authorBoardImg = Image.open(self.pic_dir + 'UI_CMN_MiniDialog_01.png').convert('RGBA')
        authorBoardImg = self._resizePic(authorBoardImg, 0.35)
        authorBoardDraw = ImageDraw.Draw(authorBoardImg)
        authorBoardDraw.text((35, 18), '        Credit to\nXybBot & Chiyuki\n   Generated By\n           Range', 'black', font3)
        self.img.paste(authorBoardImg, (1224, 19), mask=authorBoardImg.split()[3])

        font = ImageFont.truetype('src/static/adobe_simhei.otf', 17, encoding='utf-8')
        dxImg = Image.open(self.pic_dir + 'UI_RSL_MBase_Parts_01.png').convert('RGBA')
        imgdraw = ImageDraw.Draw(dxImg)
        imgdraw.text((14,22), f"r10:{self.r10ra_int100//10/100}", (0,0,0), font)
        self.img.paste(dxImg, (self.COLOUMS_IMG[7] , 65), mask=dxImg.split()[3])
        sdImg = Image.open(self.pic_dir + 'UI_RSL_MBase_Parts_02.png').convert('RGBA')
        imgdraw = ImageDraw.Draw(sdImg)
        imgdraw.text((14,22), f"b30:{self.b30ra_int100//30/100}" , (0,0,0), font)
        self.img.paste(sdImg, (self.COLOUMS_IMG[7] - 124, 65), mask=sdImg.split()[3])

        # self.img.show()

    def getDir(self):
        return self.img


async def generate_chuni40(payload: Dict) -> Tuple[Optional[Image.Image], int]:
    async with aiohttp.request("POST", "https://www.diving-fish.com/api/chunithmprober/query/player", json=payload) as resp:
        if resp.status == 400:
            return None, 400
        if resp.status == 403:
            return None, 403
        obj = await resp.json()
        b30 = obj["records"]["b30"]
        r10 = obj["records"]["r10"]
        if 'qq' in payload :
            qq = payload['qq']
        else :
            qq = '0'
        pic = DrawChuni(b30,r10,obj["nickname"],qq).getDir()
        return pic, 0

async def draw_ajb30(obj: Dict, qq: str) -> Image.Image:
    b30 = []
    for rec in obj["records"]["best"]:
        if rec["fc"] == "alljustice":
            b30.append(rec)
    b30.sort(key=lambda x:x['ra'],reverse=True)
    if len(b30) > 30:
        b30 = b30[:30]
    r10 = []
    for rec in obj["records"]["r10"]:
        if rec["fc"] == "alljustice":
            r10.append(rec)
    r10.sort(key=lambda x:x['ra'],reverse=True)
    if len(r10) > 10:
        r10 = r10[:10]
    pic = DrawChuni(b30,r10,obj["nickname"],qq).getDir()
    return pic