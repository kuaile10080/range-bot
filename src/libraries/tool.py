import datetime, hashlib, json, aiohttp, pickle

def hash(qq) -> int:
    s = datetime.datetime.now().strftime("%y%m%d")+str(qq)
    return int(hashlib.sha256(s.encode()).hexdigest(),16)
# def hash(qq: int):
#     days = int(time.strftime("%d", time.localtime(time.time()))) + 31 * int(
#         time.strftime("%m", time.localtime(time.time()+28800))) + 77
#     return (days * qq) >> 8

async def offlineinit():
    s = ""
    k=1
    async with aiohttp.request('GET', 'https://www.diving-fish.com/api/maimaidxprober/music_data') as resp:
        if resp.status == 200:
            s += "music_data.json下载成功\n"
            with open("src/static/music_data.json", "w", encoding= "utf-8") as f:
                j = await resp.json()
                json.dump(j, f, ensure_ascii=False)
        else:
            s += "music_data.json下载失败\n"
            k=0
    async with aiohttp.request('GET', 'https://www.diving-fish.com/api/maimaidxprober/chart_stats') as resp:
        if resp.status == 200:
            s += "chart_stats.json下载成功\n"
            with open("src/static/chart_stats.json", "w", encoding= "utf-8") as f:
                j = await resp.json()
                json.dump(j, f, ensure_ascii=False)
        else:
            s += "chart_stats.json下载失败\n"
            k=0
    async with aiohttp.request('GET', 'https://api.yuzuchan.moe/maimaidx/maimaidxalias') as resp:
        if resp.status == 200:
            s += "all_alias.json下载成功\n"
            with open("src/static/all_alias.json", "w", encoding= "utf-8") as f:
                j = await resp.json()
                json.dump(j, f, ensure_ascii=False)
        else:
            s += "all_alias.json下载失败\n"
            k=0
    async with aiohttp.request('GET', 'https://www.diving-fish.com/api/chunithmprober/music_data') as resp:
        if resp.status == 200:
            s += "chunithm_music_data.json下载成功\n"
            with open("src/static/chunithm/chuni_music_g.json", "w", encoding= "utf-8") as f:
                j = await resp.json()
                json.dump(j, f, ensure_ascii=False)
        else:
            s += "chunithm_music_data.json下载失败\n"
            k=0
    #"https://chunithm.sega.jp/storage/json/music.json"
    async with aiohttp.request('GET', 'https://chunithm.sega.jp/storage/json/music.json') as resp:
        if resp.status == 200:
            s += "chunithm_music.json下载成功\n"
            with open("src/static/chunithm/chuni_music.json", "w", encoding= "utf-8") as f:
                j = await resp.json()
                json.dump(j, f, ensure_ascii=False)
        else:
            s += "chunithm_music.json下载失败\n"
            k=0
    return k,s

with open("src/static/kanjic2j_xcj.dat","rb")as fp:
    kanjic2j = pickle.load(fp)

def convert_cn2jp(text:str) -> str:
    for char in text:
        if char in kanjic2j:
            text = text.replace(char, kanjic2j[char][0])
    return text

def get_nickname_from_event(event_str: str) -> str:
    event_json = json.loads(event_str)
    return event_json["sender"]["nickname"]