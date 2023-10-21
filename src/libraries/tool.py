import time, json, aiohttp

def hash(qq: int):
    days = int(time.strftime("%d", time.localtime(time.time()))) + 31 * int(
        time.strftime("%m", time.localtime(time.time()+28800))) + 77
    return (days * qq) >> 8

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