from PIL import Image, ImageDraw, ImageFont
from src.libraries.maimaidx_music import Music
from src.libraries.image import get_music_cover

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

    img.save("test.png")

    return img