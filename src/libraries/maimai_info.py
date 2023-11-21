from PIL import Image, ImageDraw, ImageFont
from src.libraries.maimaidx_music import Music
from src.libraries.image import get_music_cover
from src.libraries.maimaidx_music import compute_ra

assets_path = "src/static/mai/newinfo/"
cover_path = "src/static/mai/cover/"

async def draw_new_info(record:dict,music:Music)->Image.Image:

    diff_replace = {
        "Basic": "BSC",
        "Advanced": "ADV",
        "Expert": "EXP",
        "Master": "MST",
        "Re:MASTER": "MST_Re",
    }

    info_to_file_dict = {
        "sssp": "SSSp",
        "sss": "SSS",
        "ssp": "SSp",
        "ss": "SS",
        "sp": "Sp",
        "s": "S",
        "aaa": "AAA",
        "aa": "AA",
        "a": "A",
        "bbb": "BBB",
        "bb": "BB",
        "b": "B",
        "c": "C",
        "d": "D",
        "fc": "FC",
        "fcp": "FCp",
        "ap": "AP",
        "app": "APp",
        "fs": "FS",
        "fsp": "FSp",
        "fsd": "FSD",
        "fsdp": "FSDp"
    }

    diff = diff_replace[record["level_label"]]

    chartmode = "Deluxe" if record["type"]=="DX" else "Standard"

    music_id = record["song_id"]

    if record["level"][-1] == "+":
        lv = int(record["level"][:-1])
        plus = True
    else:
        lv = int(record["level"])
        plus = False

    music_title = record["title"]

    artist = music.artist

    dxscore = record["dxScore"]

    dxscore_max = sum(music['charts'][record['level_index']]['notes'])*3
    
    if record['dxScore']/dxscore_max >= 0.97:
        stars = 5
    elif record['dxScore']/dxscore_max >= 0.95:
        stars = 4
    elif record['dxScore']/dxscore_max >= 0.93:
        stars = 3
    elif record['dxScore']/dxscore_max >= 0.90:
        stars = 2
    elif record['dxScore']/dxscore_max >= 0.85:
        stars = 1
    else:
        stars = 0

    achievement = record["achievements"]

    rank = info_to_file_dict[record["rate"]]

    fc = "Blank" if record["fc"]=='' else info_to_file_dict[record["fc"]]

    fs = "Blank" if record["fs"]=='' else info_to_file_dict[record["fs"]]

    notes_designer = music.charts[record['level_index']].charter

    bpm = int(music.bpm)


    img= Image.new('RGBA', (394, 678), color = (0, 0, 0,0))
    img_draw = ImageDraw.Draw(img)
 
    # 主边框
    temp_img = Image.open(assets_path + f"UI_TST_MBase_{diff}.png").convert("RGBA")
    img.paste(temp_img,(0,62),temp_img)

    # 边框头
    temp_img = Image.open(assets_path + f"UI_TST_MBase_{diff}_Tab.png").convert("RGBA")
    img.paste(temp_img,(0,0),temp_img)

    # DX/SD
    temp_img = Image.open(assets_path + f"UI_TST_Infoicon_{chartmode}Mode.png").convert("RGBA")
    img.paste(temp_img,(6,6),temp_img)

    # 封面
    temp_img = get_music_cover(music_id)
    temp_img = temp_img.resize((316,316),resample=Image.Resampling.BILINEAR)
    img.paste(temp_img,(40,94))

    # LV
    temp_img = Image.open(assets_path + f"UI_TST_MBase_LV_{diff}.png").convert("RGBA")
    img.paste(temp_img,(217,363),temp_img)

    # 等级
    temp_img = Image.open(assets_path + f"UI_CMN_MusicLevel_{diff}_14.png").convert("RGBA")
    img.paste(temp_img,(262,402),temp_img)
    if lv >= 10:
        temp_img = Image.open(assets_path + f"UI_CMN_MusicLevel_{diff}_1.png").convert("RGBA")
        img.paste(temp_img,(293,402),temp_img)
    temp_img = Image.open(assets_path + f"UI_CMN_MusicLevel_{diff}_{lv%10}.png").convert("RGBA")
    img.paste(temp_img,(321,402),temp_img)
    if plus:
        temp_img = Image.open(assets_path + f"UI_CMN_MusicLevel_{diff}_10.png").convert("RGBA")
        img.paste(temp_img,(348,402),temp_img)

    # 曲名
    font_title = ImageFont.truetype("src/static/SourceHanSansCN-Bold.otf", 20,encoding="utf-8")
    text_length = font_title.getbbox(music_title)[2]
    if text_length>382:
        font_title = ImageFont.truetype("src/static/SourceHanSansCN-Bold.otf", int(20*382/text_length),encoding="utf-8")
        text_length = font_title.getbbox(music_title)[2]
    img_draw.text(((394-text_length)/2, 482), music_title, font=font_title, fill=(255, 255, 255, 255))
    
    # 艺术家
    font_artist = ImageFont.truetype("src/static/Tahoma.ttf", 16,encoding="utf-8")
    text_length = font_artist.getbbox(artist)[2]
    if text_length>382:
        font_artist = ImageFont.truetype("src/static/Tahoma.ttf", int(16*382/text_length),encoding="utf-8")
        text_length = font_artist.getbbox(artist)[2]
    img_draw.text(((394-text_length)/2, 531), artist, font=font_artist, fill=(255, 255, 255, 255))

    # 信息背景
    temp_img = Image.open(assets_path + f"BG_{stars}_stars.png").convert("RGBA")
    img.paste(temp_img,(4,563),temp_img)

    # 分数
    font_score = ImageFont.truetype("src/static/MFZhiShang_Noncommercial-Regular.otf", 20,encoding="utf-8")
    score_text = f"{achievement:>8.4f}".replace(" ","   ")
    score_text += " %"
    temp_img = Image.new('RGBA', (font_score.getbbox(score_text)[2], font_score.getbbox(score_text)[3]), color = (0, 0, 0,0))
    temp_img_draw = ImageDraw.Draw(temp_img)
    temp_img_draw.text((0, 0), score_text, font=font_score, fill=(227, 178, 24))
    temp_img = temp_img.resize((int(temp_img.size[0]*1.13),temp_img.size[1]),resample=Image.Resampling.BILINEAR)
    img.paste(temp_img,(18,571),temp_img)

    # 评价
    temp_img = Image.open(assets_path + f"UI_MSS_Rank_{rank}.png").convert("RGBA")
    img.paste(temp_img,(183,570),temp_img)
    temp_img = Image.open(assets_path + f"UI_MSS_MBase_Icon_{fc}.png").convert("RGBA")
    img.paste(temp_img,(255,570),temp_img)
    temp_img = Image.open(assets_path + f"UI_MSS_MBase_Icon_{fs}.png").convert("RGBA")
    img.paste(temp_img,(321,570),temp_img)

    # DX分
    font_dxscore = ImageFont.truetype("src/static/Tahoma.ttf", 20,encoding="utf-8")
    img_draw.text((140, 598), f"{dxscore:>4d}a/a{dxscore_max:>4d}".replace(" ","  ").replace("a"," "), font=font_dxscore, fill=(255, 255, 255, 255))

    # 谱师
    font_notes_designer = ImageFont.truetype("src/static/Tahoma.ttf", 16,encoding="utf-8")
    text_length = font_notes_designer.getbbox(notes_designer)[2]
    if text_length>260:
        notes_designer = notes_designer[:int(260/text_length*len(notes_designer))]
    img_draw.text((12, 645), notes_designer, font=font_notes_designer, fill=(34,81,146))

    # BPM
    font_bpm = ImageFont.truetype("src/static/MFZhiShang_Noncommercial-Regular.otf", 16,encoding="utf-8")
    img_draw.text((290, 647), f"BPM  {bpm:03d}", font=font_bpm, fill=(0,0,0))

    # img.save("test.png")

    return img


num_img = Image.open(f"{assets_path}UI_DNM_LifeNum_02.png").convert("RGBA")
numbox = [
    (0,0,60,72),
    (60,0,120,72),
    (120,0,180,72),
    (180,0,240,72),
    (0,72,60,144),
    (60,72,120,144),
    (120,72,180,144),
    (180,72,240,144),
    (0,144,60,216),
    (60,144,120,216)
]
#裁剪每个数字
for i in range(10):
    numbox[i] = num_img.crop(numbox[i]).resize((30,36))

def draw_Lv(lv:str,diff)->Image.Image:
    img = Image.new('RGBA', (119, 57), color = (0, 0, 0,0))
    if lv[-1]=='+':
        lv = lv[:-1]
        plus = True
    else:
        plus = False
    lv = int(lv)
    # 等级
    temp_img = Image.open(assets_path + f"UI_CMN_MusicLevel_{diff}_14.png").convert("RGBA")
    img.paste(temp_img,(-4,0),temp_img)
    if lv >= 10:
        temp_img = Image.open(assets_path + f"UI_CMN_MusicLevel_{diff}_1.png").convert("RGBA")
        img.paste(temp_img,(27,0),temp_img)
    temp_img = Image.open(assets_path + f"UI_CMN_MusicLevel_{diff}_{lv%10}.png").convert("RGBA")
    img.paste(temp_img,(55,0),temp_img)
    if plus:
        temp_img = Image.open(assets_path + f"UI_CMN_MusicLevel_{diff}_10.png").convert("RGBA")
        img.paste(temp_img,(82,0),temp_img)

    return img

diff_list = ["BSC", "ADV", "EXP", "MST", "MST_Re"]

version_icon_path = {
    "maimai": "UI_CMN_TabTitle_MaimaiTitle_Ver100.png",
    "maimaiPLUS": "UI_CMN_TabTitle_MaimaiTitle_Ver110.png",
    "GreeN": "UI_CMN_TabTitle_MaimaiTitle_Ver120.png",
    "GreeNPLUS": "UI_CMN_TabTitle_MaimaiTitle_Ver130.png",
    "ORANGE": "UI_CMN_TabTitle_MaimaiTitle_Ver140.png",
    "ORANGEPLUS": "UI_CMN_TabTitle_MaimaiTitle_Ver150.png",
    "PiNK": "UI_CMN_TabTitle_MaimaiTitle_Ver160.png",
    "PiNKPLUS": "UI_CMN_TabTitle_MaimaiTitle_Ver170.png",
    "MURASAKi": "UI_CMN_TabTitle_MaimaiTitle_Ver180.png",
    "MURASAKiPLUS": "UI_CMN_TabTitle_MaimaiTitle_Ver185.png",
    "MiLK": "UI_CMN_TabTitle_MaimaiTitle_Ver190.png",
    "MiLKPLUS": "UI_CMN_TabTitle_MaimaiTitle_Ver195.png",
    "FiNALE": "UI_CMN_TabTitle_MaimaiTitle_Ver199.png",
    "舞萌DX": "UI_CMN_TabTitle_MaimaiTitle_Ver200.png",
    "舞萌DX 2021": "UI_CMN_TabTitle_MaimaiTitle_Ver214.png",
    "舞萌DX 2022": "UI_CMN_TabTitle_MaimaiTitle_Ver220.png",
    "舞萌DX 2023": "UI_CMN_TabTitle_MaimaiTitle_Ver230.png"
}

genre_icon_path = {
    "舞萌": "UI_CMN_TabTitle_Original.png",
    "流行&动漫": "UI_CMN_TabTitle_PopsAnime.png",
    "其他游戏": "UI_CMN_TabTitle_Variety.png",
    "niconico & VOCALOID": "UI_CMN_TabTitle_Niconico.png",
    "东方Project": "UI_CMN_TabTitle_Toho.png",
    "音击&中二节奏": "UI_CMN_TabTitle_Chugeki.png"
}

def draw_music_info(music:dict)->Image.Image:
    
    if len(music['ds'])==5:
        jump = 143
        chats_sum = 5
    else:
        jump = 191
        chats_sum = 4

    # 打开背景
    bg = Image.open(f"{assets_path}BG_{chats_sum}.png").convert("RGBA")
    #bg = Image.open(f"{assets_path}BG_SD_5_template.png")
    img_draw = ImageDraw.Draw(bg)
    
    # 版本 流派
    version_icon = Image.open(f"{assets_path}version_icon/{version_icon_path[music['cn_version']]}").convert("RGBA").resize((207,100))
    bg.paste(version_icon,(145,80),version_icon)
    genre_icon = Image.open(f"{assets_path}genre_icon/{genre_icon_path[music['basic_info']['genre']]}").convert("RGBA").resize((207,100))
    bg.paste(genre_icon,(352,80),genre_icon)

    # 标准/DX
    chartmode = "Deluxe" if music["type"]=="DX" else "Standard"
    type_img = Image.open(f"{assets_path}UI_TST_Infoicon_{chartmode}Mode.png").convert("RGBA")
    bg.paste(type_img,(160,195),type_img)

    # ID
    for i in range(len(music["id"])):
        j = len(music["id"])-i-1
        num = int(music["id"][j])
        bg.paste(numbox[num],(518-i*29,202),numbox[num])

    # 封面
    cover_img = get_music_cover(music['id']).convert("RGBA")
    cover_img = cover_img.resize((316,316))
    bg.paste(cover_img,(194,283),cover_img)

    # 等级
    lv_img = draw_Lv(music["level"][3],"MST")
    bg.paste(lv_img,(420,610),lv_img)

    # 曲名
    font_title = ImageFont.truetype("src/static/SourceHanSansCN-Bold.otf", 20,encoding="utf-8")
    text_length = font_title.getbbox(music["title"])[2]
    if text_length>382:
        font_title = ImageFont.truetype("src/static/SourceHanSansCN-Bold.otf", int(20*382/text_length),encoding="utf-8")
        text_length = font_title.getbbox(music["title"])[2]
    img_draw.text((154+(394-text_length)/2, 688), music["title"], font=font_title, fill=(255, 255, 255))
    
    # 艺术家
    font_artist = ImageFont.truetype("src/static/Tahoma.ttf", 16,encoding="utf-8")
    text_length = font_artist.getbbox(music["basic_info"]["artist"])[2]
    if text_length>382:
        font_artist = ImageFont.truetype("src/static/Tahoma.ttf", int(16*382/text_length),encoding="utf-8")
        text_length = font_artist.getbbox(music["basic_info"]["artist"])[2]
    img_draw.text((154+(394-text_length)/2, 688+49), music["basic_info"]["artist"], font=font_artist, fill=(255, 255, 255))

    # BPM
    font_bpm = ImageFont.truetype("src/static/MFZhiShang_Noncommercial-Regular.otf", 16,encoding="utf-8")
    img_draw.text((454, 775), f"BPM  {music['basic_info']['bpm']:03d}", font=font_bpm, fill=(255,255,255))

    # 每谱面信息
    for i in range(chats_sum):
        #等级
        lv_img = draw_Lv(music["level"][i],diff_list[i]).resize((84,40))
        bg.paste(lv_img,(917,97+i*jump),lv_img)


        font_info = ImageFont.truetype("src/static/SourceHanSansCN-Bold.otf", 16,encoding="utf-8")
        # 定数
        ds_text = f"定数 {music['ds'][i]:>2.1f}         SSS+ {compute_ra(100.5,music['ds'][i]):>3d}         SSS {compute_ra(100,music['ds'][i]):>3d}"
        width = font_info.getbbox(ds_text)[2]
        img_draw.text((628 + int((348-width)/2), 137+i*jump), ds_text, font=font_info, fill=(255, 255, 255, 255))
        # maxcombo
        combo = sum(music["charts"][i]["notes"])
        img_draw.text((708, 165+i*jump), f"{combo}", font=font_info, fill=(255, 255, 255))
        width = font_info.getbbox(f"{combo*3}")[2]
        img_draw.text((801 + int((180-width)/2), 181+i*jump), f"{combo*3}", font=font_info, fill=(0, 0, 0))
        # 谱师
        charter = music["charts"][i]["charter"]
        img_draw.text((626, 204+i*jump), f"{charter}", font=font_info, fill=(0, 0, 0))
        img_draw.text((625, 203+i*jump), f"{charter}", font=font_info, fill=(255, 255, 255))
        # NOTES
        notes = music["charts"][i]["notes"]
        tap = notes[0]
        hold = notes[1]
        slide = notes[2]
        breaks = notes[-1]
        if music["type"]=="DX":
            touch = notes[3]
        else:
            touch = "-"
        img_draw.text((1129, 108+i*jump), f"{tap}\n{hold}\n{slide}\n{touch}\n{breaks}", font=font_info, fill=(0, 0, 0))
        # statistic
        if music["stats"][i] == {}:
            text_list = ["--","--","--","--","--","--","--","--"]
        else:
            dist = music["stats"][i]["dist"]
            sssp = (dist[-1]) /sum(dist)
            sss = (dist[-1] + dist[-2]) /sum(dist)
            ss = (dist[-1] + dist[-2] + dist[-3] + dist[-4]) /sum(dist)
            s = (dist[-1] + dist[-2] + dist[-3] + dist[-4] + dist[-5] + dist[-6]) /sum(dist)
            fc_dist = music["stats"][i]["fc_dist"]
            app = (fc_dist[-1]) /sum(fc_dist)
            ap = (fc_dist[-1] + fc_dist[-2]) /sum(fc_dist)
            fcp = (fc_dist[-1] + fc_dist[-2] + fc_dist[-3]) /sum(fc_dist)
            fc = (fc_dist[-1] + fc_dist[-2] + fc_dist[-3] + fc_dist[-4]) /sum(fc_dist)

            text_list = [f"{sssp:06.2%}",f"{sss:06.2%}",f"{ss:06.2%}",f"{s:06.2%}",f"{app:06.2%}",f"{ap:06.2%}",f"{fcp:06.2%}",f"{fc:06.2%}"]

        img_draw.text((1313, 110+i*jump), text_list[0], font=font_info, fill=(0, 0, 0))
        img_draw.text((1313, 144+i*jump), text_list[2], font=font_info, fill=(0, 0, 0))
        img_draw.text((1313, 177+i*jump), text_list[4], font=font_info, fill=(0, 0, 0))
        img_draw.text((1313, 203+i*jump), text_list[6], font=font_info, fill=(0, 0, 0))
        img_draw.text((1440, 110+i*jump), text_list[1], font=font_info, fill=(0, 0, 0))
        img_draw.text((1440, 144+i*jump), text_list[3], font=font_info, fill=(0, 0, 0))
        img_draw.text((1440, 177+i*jump), text_list[5], font=font_info, fill=(0, 0, 0))
        img_draw.text((1440, 203+i*jump), text_list[7], font=font_info, fill=(0, 0, 0))
    
    return bg