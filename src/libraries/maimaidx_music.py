import json, random, nltk, math
from typing import Dict, List, Optional, Union, Tuple, Any
from src.libraries.tool import convert_cn2jp
from src.libraries.static_lists_and_dicts import SCORE_COEFFICIENT_TABLE, SCORE_COEFFICIENT_TABLE_LEGANCY
from copy import deepcopy

def get_cover_len4_id(mid) -> str:
    return mid
    mid = int(mid)
    if 10001 <= mid:
        mid -= 10000
    return f'{mid:04d}'

def compute_ra(ds:float, achievement:float, b50 = True)->int:
    if b50:
        score_table = SCORE_COEFFICIENT_TABLE
    else:
        score_table = SCORE_COEFFICIENT_TABLE_LEGANCY
    if achievement == 99.9999:
        return math.floor(score_table[-2][1]*ds*achievement/100)-1
    elif achievement == 100.4999:
        return math.floor(score_table[-1][1]*ds*achievement/100)-1
    else:
        for i in range(len(score_table)-1):
            if score_table[i][0] <= achievement < score_table[i+1][0]:
                return math.floor(score_table[i][1]*ds*achievement/100)
        return math.floor(score_table[-1][1]*ds*100.5/100)

def cross(checker: List[Any], elem: Optional[Union[Any, List[Any]]], diff):
    ret = False
    diff_ret = []
    if not elem or elem is Ellipsis:
        return True, diff
    if isinstance(elem, List):
        for _j in (range(len(checker)) if diff is Ellipsis else diff):
            if _j >= len(checker):
                continue
            __e = checker[_j]
            if __e in elem:
                diff_ret.append(_j)
                ret = True
    elif isinstance(elem, Tuple):
        for _j in (range(len(checker)) if diff is Ellipsis else diff):
            if _j >= len(checker):
                continue
            __e = checker[_j]
            if elem[0] <= __e <= elem[1]:
                diff_ret.append(_j)
                ret = True
    else:
        for _j in (range(len(checker)) if diff is Ellipsis else diff):
            if _j >= len(checker):
                continue
            __e = checker[_j]
            if elem == __e:
                return True, [_j]
    return ret, diff_ret


def in_or_equal(checker: Any, elem: Optional[Union[Any, List[Any]]]):
    if elem is Ellipsis:
        return True
    if isinstance(elem, List):
        return checker in elem
    elif isinstance(elem, Tuple):
        return elem[0] <= checker <= elem[1]
    else:
        return checker == elem

class Stats(Dict):
    count: Optional[int] = None
    avg: Optional[float] = None
    sss_count: Optional[int] = None
    difficulty: Optional[str] = None
    rank: Optional[int] = None
    total: Optional[int] = None
    def __getattribute__(self, item):
        if item == 'sss_count':
            return self['sssp_count']
        elif item == 'rank':
            return self['v'] + 1
        elif item == 'total':
            return self['t']
        elif item == 'difficulty':
            try:
                return self['tag']
            except:
                return "--"
        elif item in self:
            return self[item]
        return super().__getattribute__(item)

class Chart(Dict):
    tap: Optional[int] = None
    slide: Optional[int] = None
    hold: Optional[int] = None
    touch: Optional[int] = None
    brk: Optional[int] = None
    charter: Optional[str] = None

    def __getattribute__(self, item):
        if item == 'tap':
            return self['notes'][0]
        elif item == 'hold':
            return self['notes'][1]
        elif item == 'slide':
            return self['notes'][2]
        elif item == 'touch':
            return self['notes'][3] if len(self['notes']) == 5 else 0
        elif item == 'brk':
            return self['notes'][-1]
        elif item == 'charter':
            return self['charter']
        return super().__getattribute__(item)


class Music(Dict):
    id: Optional[str] = None
    title: Optional[str] = None
    ds: Optional[List[float]] = None
    level: Optional[List[str]] = None
    genre: Optional[str] = None
    type: Optional[str] = None
    bpm: Optional[float] = None
    version: Optional[str] = None
    is_new: Optional[bool] = None
    charts: Optional[Chart] = None
    stats: Optional[List[Stats]] = None
    release_date: Optional[str] = None
    artist: Optional[str] = None
    alias: Optional[List[str]] = None
    cn_version: Optional[str] = None

    diff: List[int] = []

    def __getattribute__(self, item):
        if item in {'genre', 'artist', 'release_date', 'bpm', 'version', 'is_new'}:
            if item == 'version':
                return self['basic_info']['from']
            return self['basic_info'][item]
        elif item in self:
            return self[item]
        return super().__getattribute__(item)



class MusicList(List[Music]):
    def by_id(self, music_id: any) -> Optional[Music]:
        for music in self:
            if int(music.id) == int(music_id):
                return music
        return None

    def by_title(self, music_title: str) -> Optional[Music]:
        for music in self:
            if music.title == music_title:
                return music
        return None

    def random(self):
        return random.choice(self)

    def filter(self,
            *,
            level: Optional[Union[str, List[str]]] = ...,
            ds: Optional[Union[float, List[float], Tuple[float, float]]] = ...,
            title_search: Optional[str] = ...,
            genre: Optional[Union[str, List[str]]] = ...,
            bpm: Optional[Union[float, List[float], Tuple[float, float]]] = ...,
            type: Optional[Union[str, List[str]]] = ...,
            diff: List[int] = ...,
            ):
        new_list = MusicList()
        for music in self:
            diff2 = diff
            music = deepcopy(music)
            ret, diff2 = cross(music.level, level, diff2)
            if not ret:
                continue
            ret, diff2 = cross(music.ds, ds, diff2)
            if not ret:
                continue
            if not in_or_equal(music.genre, genre):
                continue
            if not in_or_equal(music.type, type):
                continue
            if not in_or_equal(music.bpm, bpm):
                continue
            if title_search is not Ellipsis and title_search.lower() not in music.title.lower() and convert_cn2jp(title_search.lower()) not in music.title.lower():
                continue
            music.diff = diff2
            new_list.append(music)
        return new_list
    
    def filt_by_name(self,title_search:str):

        with open("src/static/all_alias_temp.json", "r", encoding="utf-8") as fp:
            alias_data = json.load(fp)

        title_search = title_search.lower()
        sdflag = False
        dxflag = False
        if title_search.startswith("标"):
            sdflag = True
        elif title_search.startswith("dx"):
            dxflag = True

        new_list = MusicList()
        title_temp_equal = MusicList()
        alias_temp_equal = MusicList()
        alias_temp_in = MusicList()
        ngram_temp1 = None
        ngram_temp2 = None
        ngrams_max1 = 0
        ngrams_max2 = 0
        for music in self:
            if sdflag and int(music.id) >= 10000:
                continue
            if dxflag and int(music.id) < 10000:
                continue
            alias_list = alias_data[music.id]["Alias"]
            if title_search == music.title.lower():
                title_temp_equal.append(music)
            else:
                if title_search in alias_list:
                    alias_temp_equal.append(music)
                else:
                    for alias in alias_list:
                        if title_search in alias.lower():
                            alias_temp_in.append(music)
                            break
                        ngram_similarity1 = calculate_ngram_similarity(title_search, alias.lower(), 1)
                        ngram_similarity2 = calculate_ngram_similarity(title_search, alias.lower(), 2)
                        if ngram_similarity1 > ngrams_max1:
                            ngrams_max1 = ngram_similarity1
                            ngram_temp1 = music
                        if ngram_similarity2 > ngrams_max2:
                            ngrams_max2 = ngram_similarity2
                            ngram_temp2 = music
        if len(title_temp_equal) != 0:
            return title_temp_equal
        elif len(alias_temp_equal) != 0:
            return alias_temp_equal
        elif len(alias_temp_in) != 0:
            return alias_temp_in
        elif ngram_temp2 is not None:
            new_list.append(ngram_temp2)
        elif ngram_temp1 is not None:
            new_list.append(ngram_temp1)
        return new_list

def calculate_ngram_similarity(text1_cn, text2, n):
    ngrams0 = set(nltk.ngrams(text1_cn, n))
    ngrams1 = set(nltk.ngrams(text2, n))
    intersection = len(ngrams0.intersection(ngrams1))
    union = len(ngrams0.union(ngrams1))
    if union == 0:
        return 0
    else:
        return intersection / union

def refresh_alias_temp():
    with open("src/static/all_alias.json", "r", encoding="utf-8") as aliasfile:
            alias_data = json.load(aliasfile)

    with open("src/static/alias_pre_process_add.json", "r", encoding="utf-8") as addfile, \
            open("src/static/alias_pre_process_remove.json", "r", encoding="utf-8") as removefile:
            alias_pre_process_add = json.load(addfile)
            alias_pre_process_remove = json.load(removefile)

    for key in alias_pre_process_add:
        for item in alias_pre_process_add[key]:
            if item not in alias_data[key]["Alias"]:
                alias_data[key]["Alias"].append(item)

    for key in alias_pre_process_remove:
        for item in alias_pre_process_remove[key]:
            if item in alias_data[key]["Alias"]:
                alias_data[key]["Alias"].remove(item)
    
    with open("src/static/all_alias_temp.json","w",encoding="utf-8") as fp:
        json.dump(alias_data,fp)
    return True


with open("src/static/version_list.json", "r", encoding="utf-8") as fp:
    version_list = json.load(fp)

version_replace = {
    "maimaDX": "舞萌DX",
    "Splash": "舞萌DX2021",
    "UNiVERSE": "舞萌DX2022",
    "FESTiVAL": "舞萌DX2023"
}

def get_cn_version(music: Music)->str:
    if music.id in version_list:
        if version_list[music.id] in version_replace:
            return version_replace[version_list[music.id]]
        else:
            return version_list[music.id]
    else:
        return "舞萌DX2023"
            

#OFFLINE
#obj_data = requests.get('https://www.diving-fish.com/api/maimaidxprober/music_data').json()
#obj_stats = requests.get('https://www.diving-fish.com/api/maimaidxprober/chart_stats').json()
def refresh_music_list():
    with open("src/static/music_data.json", "r", encoding="utf-8") as mdatafile, \
        open("src/static/chart_stats.json", "r", encoding="utf-8") as cstatsfile:
        obj_data = json.load(mdatafile)
        obj_stats = json.load(cstatsfile)
    obj_stats = obj_stats["charts"]
    _music_data = obj_data
    _total_list: MusicList = MusicList(obj_data)
            
    for __i in range(len(_total_list)):
        _total_list[__i] = Music(_total_list[__i])
        _total_list[__i]['cn_version'] = get_cn_version(_total_list[__i])
        _total_list[__i].cn_version = _total_list[__i]['cn_version']
        try:
            _total_list[__i]['stats'] = obj_stats[_total_list[__i].id]
        except:
            _total_list[__i]['stats'] = [{},{},{},{},{}]
        for __j in range(len(_total_list[__i].charts)):
            _total_list[__i].charts[__j] = Chart(_total_list[__i].charts[__j])
            _total_list[__i].stats[__j] = Stats(_total_list[__i].stats[__j])
    return _total_list, _music_data

# init alias

total_list, music_data = refresh_music_list()
music_data_byidstr = {}

with open("src/static/all_alias.json", "r", encoding="utf-8") as aliasfile:
        alias_data = json.load(aliasfile)

for music in music_data:
    music_data_byidstr[music['id']] = music
    if music['id'] not in alias_data:
        alias_data[music['id']] = {
            "Name": music['title'],
            "Alias": []
        }
with open("src/static/all_alias.json","w",encoding="utf-8") as fp:
    json.dump(alias_data,fp)


refresh_alias_temp()