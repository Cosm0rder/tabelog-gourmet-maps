# -*- coding: utf-8 -*-
"""新規店プール統合: 全プールの「新規/増分」節を統合・デデュープ・百名店36ジャンル分類・チャンク化。
出力: new-pool-unified.tsv / chunks/new/*.txt / new-pool-summary.md / new-pool-unresolved.md
正規化は match_archive.py と同一方式(NFKC・異体字変換・記号除去)。
"""
import re, unicodedata, json, os
from pathlib import Path
from collections import defaultdict, Counter

BASE = Path.home() / "workspace/tabelog-to-google-maps"

# ---------------- normalize (match_archive.py と同一) ----------------
VARIANTS = str.maketrans({
    "髙": "高", "﨑": "崎", "𠮷": "吉", "㐂": "喜", "澤": "沢", "櫻": "桜", "龍": "竜", "廣": "広",
    "榮": "栄", "齋": "斎", "邊": "辺", "國": "国", "會": "会", "圓": "円", "龜": "亀",
    "嶋": "島", "舘": "館", "壽": "寿", "萬": "万", "與": "与", "來": "来", "條": "条",
    "應": "応", "營": "営", "關": "関", "縣": "県", "區": "区", "麵": "麺",
    "鹽": "塩", "螢": "蛍", "蟲": "虫", "絲": "糸", "戀": "恋", "獨": "独", "獻": "献", "顯": "顕",
    "佛": "仏", "瀧": "滝", "遙": "遥", "頰": "頬", "惠": "恵", "渚": "緒", "靑": "青", "淸": "清",
    "郞": "郎", "亰": "京", "凜": "凛", "濱": "浜", "邉": "辺", "塚": "塚",
})
REMOVE_CHARS = set(" ・･·‐-―ー.,、。，．・:：;；/／\\|｜()（）[]［］【】「」『』\"'’‘“”!?！？~〜～*＊&＆+＋=＝_＿<>＜＞#＃@＠%％¥￥$＄")

def normalize(name):
    s = unicodedata.normalize("NFKC", name)
    s = s.translate(VARIANTS)
    s = s.lower()
    s = "".join(ch for ch in s if ch not in REMOVE_CHARS and not ch.isspace())
    return s

def aliases(name):
    """match_archive.add_ref と同じ別名生成: 本体・括弧内・括弧除去・/分割"""
    out = set()
    n = normalize(name)
    if n:
        out.add(n)
    m = re.match(r"^(.*?)（(.+?)）(.*)$", name)
    if m:
        inner = normalize(m.group(2))
        if inner:
            out.add(inner)
        stripped = normalize(m.group(1) + m.group(3))
        if stripped:
            out.add(stripped)
    if "／" in name:
        for part in name.split("／"):
            pn = normalize(part)
            if pn:
                out.add(pn)
    return out

# ---------------- 都道府県・市区町村の正規化 ----------------
PREFS = ["北海道", "青森県", "岩手県", "宮城県", "秋田県", "山形県", "福島県", "茨城県", "栃木県", "群馬県",
         "埼玉県", "千葉県", "東京都", "神奈川県", "新潟県", "富山県", "石川県", "福井県", "山梨県", "長野県",
         "岐阜県", "静岡県", "愛知県", "三重県", "滋賀県", "京都府", "大阪府", "兵庫県", "奈良県", "和歌山県",
         "鳥取県", "島根県", "岡山県", "広島県", "山口県", "徳島県", "香川県", "愛媛県", "高知県", "福岡県",
         "佐賀県", "長崎県", "熊本県", "大分県", "宮崎県", "鹿児島県", "沖縄県"]
TOKYO_WARDS = ["千代田区", "中央区", "港区", "新宿区", "文京区", "台東区", "墨田区", "江東区", "品川区", "目黒区",
               "大田区", "世田谷区", "渋谷区", "中野区", "杉並区", "豊島区", "北区", "荒川区", "板橋区", "練馬区",
               "足立区", "葛飾区", "江戸川区"]

def short_to_pref(s):
    s = s.strip()
    if s in PREFS:
        return s
    if s == "東京":
        return "東京都"
    if s == "大阪":
        return "大阪府"
    if s == "京都":
        return "京都府"
    if s == "北海道":
        return "北海道"
    if s + "県" in PREFS:
        return s + "県"
    return ""

def extract_pref(area):
    if not area:
        return ""
    for p in PREFS:
        if p in area:
            return p
    if "京都市" in area:
        return "京都府"
    if "大阪市" in area:
        return "大阪府"
    for w in TOKYO_WARDS:
        if w in area:
            return "東京都"
    return short_to_pref(area)

def extract_city(area, pref):
    """市区町村キーを返す。取れない/広域表記なら ''"""
    if not area:
        return ""
    m = re.search(r"(京都市[^\s、・/]+区|大阪市[^\s、・/]+区)", area)
    if m:
        return m.group(1)
    if pref == "東京都":
        for w in TOKYO_WARDS:
            if w in area:
                return w
    if "・" not in area:
        m = re.search(r"([^\s、/都道府県]+[市区町村])", area.replace(pref, "", 1))
        if m:
            return m.group(1)
    return ""

# ---------------- ジャンル分類(regroup.py の RULES) ----------------
RULES = [
    ('とんかつ', ['とんかつ']),
    ('すき焼き・しゃぶしゃぶ', ['すき焼き', 'しゃぶしゃぶ']),
    ('うなぎ', ['うなぎ', '鰻']),
    ('天ぷら', ['天ぷら', '天麩羅']),
    ('そば', ['そば', '蕎麦']),
    ('うどん', ['うどん']),
    ('寿司', ['寿司', '鮨', 'すし']),
    ('焼き鳥', ['焼き鳥', '焼鳥']),
    ('鳥料理', ['鳥料理', '鶏料理', '水炊き']),
    ('焼肉', ['焼肉', 'ホルモン']),
    ('ステーキ・鉄板焼き', ['ステーキ', '鉄板焼']),
    ('餃子', ['餃子']),
    ('ラーメン', ['ラーメン', 'らーめん', 'らぁめん', 'つけ麺', '中華そば', '麺']),
    ('カレー', ['カレー']),
    ('ピザ', ['ピザ', 'ピッツァ']),
    ('ハンバーガー', ['ハンバーガー', 'バーガー']),
    ('お好み焼き', ['お好み焼き', 'もんじゃ', '鉄板焼き お好み']),
    ('フレンチ', ['フレンチ', 'フランス料理', 'ビストロ']),
    ('イタリアン', ['イタリアン', 'イタリア料理', 'トラットリア', 'パスタ']),
    ('スペイン料理', ['スペイン']),
    ('洋食', ['洋食', 'グリル', 'ハンバーグ']),
    ('創作料理・イノベーティブ', ['イノベーティブ', '創作料理', 'フュージョン', 'モダンフレンチ', 'イノベーティブ・フュージョン']),
    ('中国料理', ['中華', '中国料理', '四川', '飲茶', '点心', '台湾料理', '上海料理', '広東', '北京料理', '薬膳']),
    ('アジア・エスニック', ['韓国', 'タイ料理', 'ベトナム', 'インド料理', 'エスニック', 'ネパール', 'スリランカ', 'インドネシア', 'マレーシア', 'シンガポール', 'フィリピン', '中東', 'トルコ', 'メキシコ', 'ブラジル', 'ペルー', 'モンゴル', 'ウイグル', 'バリ']),
    ('アイス・ジェラート', ['アイス', 'ジェラート', 'ソフトクリーム']),
    ('和菓子・甘味処', ['和菓子', '甘味処', 'たい焼き', 'どら焼き', '大福', '団子', 'かき氷', 'あんみつ', '羊羹', '最中', 'せんべい', '和スイーツ']),
    ('スイーツ', ['スイーツ', 'ケーキ', '洋菓子', 'パティスリー', 'デザート', 'チョコ', 'クレープ', 'パフェ', 'ドーナツ', 'マカロン', 'タルト', 'プリン', 'バームクーヘン', 'カステラ', 'ベーグル', 'シュークリーム']),
    ('パン', ['パン', 'ベーカリー', 'サンドイッチ']),
    ('喫茶店', ['喫茶店']),
    ('カフェ', ['カフェ', 'コーヒー', 'ロースタリー']),
    ('バー', ['バー', 'ワインバー', '日本酒バー', '焼酎バー', 'ダイニングバー', 'パブ', 'ワイン']),
    ('立ち飲み', ['立ち飲み', '立飲み', '立ち食い', '立食い']),
    ('居酒屋', ['居酒屋', '海鮮居酒屋', '炉端焼き', '串揚げ', '串カツ', 'もつ焼き', 'やきとん', 'おでん', '釜飯']),
    ('食堂', ['食堂', '定食', '丼', '海鮮丼', '親子丼', '天丼', 'うな丼', 'カツ丼', '飯処', 'めし']),
    ('日本料理', ['日本料理', '懐石', '会席', '割烹', '京料理', '郷土料理', '海鮮', '魚介', '鍋', 'ふぐ', 'あんこう', 'すっぽん', '鯨', '精進料理', '豆腐料理', '湯葉', 'おばんざい', '茶懐石', '鮎', '川魚', 'ジビエ']),
    ('その他', []),
]
SUPP_GENRE = {
    '現代風料理': '創作料理・イノベーティブ',
    'クリエイティブ': '創作料理・イノベーティブ',
    '沖縄料理': '日本料理',
    'イノベーティブ・フュージョン': '創作料理・イノベーティブ',
}

def classify_genre_text(genre_raw):
    if not genre_raw:
        return None
    g = genre_raw.strip()
    if g.startswith('すき焼'):
        return 'すき焼き・しゃぶしゃぶ'
    if g in SUPP_GENRE:
        return SUPP_GENRE[g]
    tokens = [t.strip() for t in re.split(r'[、・/]', g) if t.strip()]
    first = tokens[0] if tokens else ''
    if first in SUPP_GENRE:
        return SUPP_GENRE[first]
    for cat, kws in RULES:
        for kw in kws:
            if kw and kw in first:
                return cat
    for cat, kws in RULES:
        for kw in kws:
            if kw and kw in g:
                return cat
    for t in tokens:
        if t in SUPP_GENRE:
            return SUPP_GENRE[t]
    return None

def classify_name(name):
    base = re.sub(r'（[^）]*）', '', name)
    base = re.sub(r'\([^)]*\)', '', base)
    for cat, kws in RULES:
        for kw in kws:
            if kw and kw in base:
                return cat
    return None

GENRE_ORDER = ['日本料理', '寿司', 'とんかつ', 'そば', 'うどん', '天ぷら', 'うなぎ', 'すき焼き・しゃぶしゃぶ',
               '焼肉', 'ステーキ・鉄板焼き', '焼き鳥', '鳥料理', 'ラーメン', 'カレー', '中国料理', '餃子',
               'アジア・エスニック', 'フレンチ', 'イタリアン', 'スペイン料理', 'ピザ', '洋食',
               '創作料理・イノベーティブ', 'ハンバーガー', 'お好み焼き', '居酒屋', '立ち飲み', 'バー', '食堂',
               'スイーツ', '和菓子・甘味処', 'アイス・ジェラート', 'パン', 'カフェ', '喫茶店', 'その他']
HYAKU_GENRES = set(GENRE_ORDER)


EN_CITY = {
    'Tokyo': ('東京都', ''), 'Kyoto': ('京都府', '京都市'), 'Osaka': ('大阪府', '大阪市'),
    'Fukuoka': ('福岡県', '福岡市'), 'Sapporo': ('北海道', '札幌市'), 'Shizuoka': ('静岡県', '静岡市'),
    'Kitakyushu': ('福岡県', '北九州市'), 'Tatebayashi': ('群馬県', '館林市'), 'Gifu': ('岐阜県', '岐阜市'),
    'Kobe': ('兵庫県', '神戸市'), 'Nagahama': ('滋賀県', '長浜市'), 'Kanazawa': ('石川県', '金沢市'),
    'Nagoya': ('愛知県', '名古屋市'), 'Karuizawa': ('長野県', '軽井沢町'), 'Kaga': ('石川県', '加賀市'),
    'Niigata': ('新潟県', '新潟市'), 'Ishikawa': ('石川県', ''), 'Sakai': ('大阪府', '堺市'),
    'Hiroshima': ('広島県', '広島市'), 'Imari': ('佐賀県', '伊万里市'), 'Iida': ('長野県', '飯田市'),
    'Iizuna': ('長野県', '飯綱町'), 'Mie': ('三重県', ''), 'Komatsu': ('石川県', '小松市'),
    'Fukui': ('福井県', '福井市'), 'Ashiya': ('兵庫県', '芦屋市'), 'Saga': ('佐賀県', '佐賀市'),
    'Wakayama': ('和歌山県', '和歌山市'), 'Kamakura': ('神奈川県', '鎌倉市'), 'Tottori': ('鳥取県', '鳥取市'),
    'Fujisawa': ('神奈川県', '藤沢市'), 'Kanagawa': ('神奈川県', ''), 'Yokohama': ('神奈川県', '横浜市'),
    'Higashiomi': ('滋賀県', '東近江市'), 'Chiba': ('千葉県', '千葉市'), 'Hakodate': ('北海道', '函館市'),
    'Nanao': ('石川県', '七尾市'), 'Nara': ('奈良県', '奈良市'), 'Matsusaka': ('三重県', '松阪市'),
    'Otsu': ('滋賀県', '大津市'), 'Sendai': ('宮城県', '仙台市'), 'Okayama': ('岡山県', '岡山市'),
}
OSAKA_FU_CITIES = {'吹田市', '箕面市', '豊中市', '東大阪市', '堺市', '枚方市', '八尾市', '寝屋川市', '茨木市',
                   '高槻市', '岸和田市', '池田市', '守口市', '門真市', '摂津市', '富田林市', '松原市', '大東市',
                   '和泉市', '柏原市', '羽曳野市', '藤井寺市', '泉南市', '阪南市', '泉佐野市', '交野市', '四條畷市'}
KYOTO_FU_CITIES = {'宇治市', '亀岡市', '城陽市', '向日市', '長岡京市', '八幡市', '京田辺市', '木津川市', '南丹市', '福知山市', '舞鶴市', '綾部市', '宮津市', '京丹後市'}

# ---------------- レコード収集 ----------------
records = []
unresolved_raw = []

def add(name, area_raw, pref, city, genre_text, genre_fixed, source, flags=None):
    records.append({
        'name': name.strip(), 'area_raw': area_raw.strip() if area_raw else '',
        'pref': pref or '', 'city': city or '',
        'genre_text': genre_text.strip() if genre_text else '',
        'genre_fixed': genre_fixed or '', 'source': source,
        'flags': list(flags or []),
    })

def read(fn):
    return (BASE / fn).read_text(encoding='utf-8').splitlines()

def section_lines(lines, start_pred, end_pred):
    out, on = [], False
    for ln in lines:
        if not on and start_pred(ln):
            on = True
            continue
        if on and end_pred(ln):
            break
        if on:
            out.append(ln)
    return out

# --- award2026.md 新規 ---
for ln in section_lines(read('award2026.md'),
                        lambda l: l.startswith('## 新規'), lambda l: l.startswith('## 付記')):
    if ln.startswith('- '):
        p = ln[2:].split('｜')
        if len(p) == 4:
            add(p[0], p[2], short_to_pref(p[2]), '', p[1], '', 'Award2026')

# --- michelin-tokyo2026.md 新規 ---
for ln in section_lines(read('michelin-tokyo2026.md'),
                        lambda l: l.startswith('## 新規'), lambda l: l.startswith('## 付記')):
    if ln.startswith('- '):
        p = ln[2:].split('｜')
        if len(p) == 3:
            add(p[0], p[1], '東京都', p[1], p[2], '', 'ミシュラン東京2026')

# --- michelin-kyoto-osaka2026.md 新規 ---
for ln in section_lines(read('michelin-kyoto-osaka2026.md'),
                        lambda l: l.startswith('## 新規'), lambda l: l.startswith('## 付記')):
    if ln.startswith('- '):
        body = re.sub(r'\s*【[^】]*】\s*$', '', ln[2:])
        p = body.split('｜')
        if len(p) == 3:
            pref = extract_pref(p[1])
            if not pref and p[1].strip() in OSAKA_FU_CITIES:
                pref = '大阪府'
            if not pref and p[1].strip() in KYOTO_FU_CITIES:
                pref = '京都府'
            city = extract_city(p[1], pref) or (p[1].strip() if pref and p[1].strip().endswith(('市', '区', '町', '村')) else '')
            add(p[0], p[1], pref, city, p[2], '', 'ミシュラン京阪2026')

# --- michelin-archive-new.md 増分 ---
cur_sec = ''
for ln in section_lines(read('michelin-archive-new.md'),
                        lambda l: l.startswith('## 増分新規'), lambda l: l.startswith('## 要確認')):
    m = re.match(r'^### (東京|京都|大阪)', ln)
    if m:
        cur_sec = {'東京': '東京都', '京都': '京都府', '大阪': '大阪府'}[m.group(1)]
    if ln.startswith('- '):
        body = re.sub(r'\s*【新規】\s*$', '', ln[2:])
        p = body.split('｜')
        if len(p) >= 3:
            pref = extract_pref(p[1]) or cur_sec
            add(p[0], p[1], pref, extract_city(p[1], pref), p[2], '', 'ミシュラン過去年')

# --- michelin-archive2-new.md 増分 ---
cur_sec = ''
for ln in read('michelin-archive2-new.md'):
    m = re.match(r'^## 増分新規（(東京|京都|大阪)', ln)
    if m:
        cur_sec = {'東京': '東京都', '京都': '京都府', '大阪': '大阪府'}[m.group(1)]
    if ln.startswith('## 要確認'):
        cur_sec = ''
    if cur_sec and ln.startswith('- '):
        p = ln[2:].split('｜')
        if len(p) >= 3:
            add(p[0], p[1], cur_sec, extract_city(p[1], cur_sec), p[2], '', 'ミシュラン過去年2')

# --- 百名店系 ---
def parse_hyakumeiten(fn, source, archive_style=False):
    genre = ''
    mode = None
    for ln in read(fn):
        if archive_style:
            if re.match(r'^#{2,4}\s+増分新規', ln):
                mode = 'new'
                continue
            if re.match(r'^#{2,4}\s+要確認', ln):
                mode = 'unres'
                continue
            if re.match(r'^## 未完', ln):
                mode = None
                continue
            m = re.match(r'^#{3,4}\s+(.+?)（\d+店）', ln)
            if m and m.group(1).strip() in HYAKU_GENRES:
                genre = m.group(1).strip()
        else:
            m = re.match(r'^## (.+?) 百名店', ln)
            if m:
                genre = m.group(1).strip()
            if ln.startswith('### 新規'):
                mode = 'new'
                continue
            if ln.startswith('### 要確認'):
                mode = 'unres'
                continue
            if ln.startswith('## '):
                mode = None
        if mode == 'new' and ln.startswith('- '):
            p = ln[2:].split('｜')
            if len(p) >= 2:
                area = re.sub(r'（選出:.*$', '', p[1]).strip()
                add(p[0], area, short_to_pref(area) or extract_pref(area), '', '', genre, source)
        elif mode == 'unres' and ln.startswith('- '):
            unresolved_raw.append({'raw': ln[2:].strip(), 'source': source})

parse_hyakumeiten('hyakumeiten-2026-new.md', '百名店2026')
parse_hyakumeiten('hyakumeiten-older-new.md', '百名店旧年')
parse_hyakumeiten('hyakumeiten-archive-new.md', '百名店アーカイブ', archive_style=True)

# --- ゴ・エ・ミヨ 新規 ---
cur_pref = ''
for ln in section_lines(read('gaultmillau.md'),
                        lambda l: l.startswith('## 新規'), lambda l: l.startswith('## 付録')):
    m = re.match(r'^### (.+)$', ln)
    if m and m.group(1).strip() in PREFS:
        cur_pref = m.group(1).strip()
    if ln.startswith('- '):
        p = ln[2:].split('｜')
        if len(p) >= 3:
            name = p[0].strip()
            city = ''
            mm = re.match(r'^(.*)（([^（）]+[市区町村])）$', name)
            if mm:
                name, city = mm.group(1).strip(), mm.group(2).strip()
            genre = re.sub(r'［[^］]*］\s*$', '', p[2]).strip()
            add(name, (cur_pref + city) if city else cur_pref, cur_pref, city, genre, '', 'ゴ・エ・ミヨ2026')

# --- Destination Restaurants / OAD 新規 ---
for ln in section_lines(read('destination-oad.md'),
                        lambda l: l.startswith('## 新規'), lambda l: l.startswith('## 出典')):
    if ln.startswith('- '):
        p = ln[2:].split('｜')
        if len(p) >= 3:
            pref_raw = p[2].strip()
            pref = short_to_pref(pref_raw) or extract_pref(pref_raw)
            city = ''
            if pref_raw in EN_CITY:
                pref, city = EN_CITY[pref_raw]
            add(p[0], pref_raw, pref, city, '', '', 'DR/OAD')

# --- Award 過去年 GOLD ---
for ln in section_lines(read('award-archive-new.md'),
                        lambda l: l.startswith('## 増分新規'), lambda l: l.startswith('## 要確認')):
    if ln.startswith('- '):
        p = ln[2:].split('｜')
        if len(p) >= 3:
            add(p[0], p[2], short_to_pref(p[2]), '', p[1], '', 'Award過去年')

# --- Award 過去年 SILVER/BRONZE ---
for ln in section_lines(read('award-archive-silver-bronze-new.md'),
                        lambda l: l.startswith('## 増分新規'), lambda l: l.startswith('## 要確認')):
    if ln.startswith('- '):
        p = ln[2:].split('｜')
        if len(p) >= 3:
            add(p[0], p[2], short_to_pref(p[2]), '', p[1], '', 'Award過去年SB')

# --- TRY 新規 ---
for ln in section_lines(read('try-ramen.md'),
                        lambda l: l.startswith('## 新規'), lambda l: l.startswith('## 付記')):
    if ln.startswith('- '):
        p = ln[2:].split('｜')
        if len(p) >= 2:
            area = p[1].strip()
            fl = []
            pref = extract_pref(area)
            if area == 'エリア未確認':
                pref = ''
                fl.append('エリア未確認')
            add(p[0], area, pref, extract_city(area, pref), '', 'ラーメン', 'TRY', fl)

# --- ラ・リスト/50Best 新規 ---
for ln in section_lines(read('laliste-50best.md'),
                        lambda l: l.startswith('## 新規'), lambda l: l.startswith('## La Liste 未取得')):
    if ln.startswith('- '):
        p = ln[2:].split('｜')
        if len(p) >= 3:
            city_raw = p[2].strip()
            add(p[0], city_raw, short_to_pref(city_raw), '', '', '', 'ラリスト/50Best')

print('parsed records:', len(records))
print(Counter(r['source'] for r in records))
print('hyakumeiten unresolved bullets so far:', len(unresolved_raw))
json.dump(records, open('/tmp/newpool_records.json', 'w'), ensure_ascii=False)
json.dump(unresolved_raw, open('/tmp/newpool_unresolved_raw.json', 'w'), ensure_ascii=False)

# ============================================================
# Part 2: 要確認の集約(百名店系以外)
# ============================================================
def add_unres(name, area, genre, source, note):
    unresolved_raw.append({'name': name.strip(), 'area': area.strip(), 'genre': genre.strip(),
                           'source': source, 'note': note.strip()})

# award2026 要確認
for ln in section_lines(read('award2026.md'),
                        lambda l: l.startswith('## 要確認'), lambda l: l.startswith('## 新規')):
    if ln.startswith('- '):
        body = ln[2:]
        main, _, note = body.partition(' ― ')
        p = main.split('｜')
        if len(p) >= 3:
            add_unres(p[0], p[2], p[1], 'Award2026', note)

# ミシュラン表形式の要確認
def parse_michelin_table(fn, source, area_idx, genre_idx):
    for ln in section_lines(read(fn),
                            lambda l: l.startswith('## 要確認'), lambda l: l.startswith('## 全掲載') or l.startswith('## 出典')):
        if ln.startswith('|') and '---' not in ln and '店名' not in ln:
            cells = [c.strip() for c in ln.strip().strip('|').split('|')]
            if len(cells) > area_idx:
                genre = cells[genre_idx] if genre_idx is not None else ''
                skip = {0, area_idx} | ({genre_idx} if genre_idx is not None else set())
                note = ' / '.join(c for i, c in enumerate(cells) if i not in skip)
                add_unres(cells[0], cells[area_idx], genre, source, note)

parse_michelin_table('michelin-tokyo2026.md', 'ミシュラン東京2026', 2, 3)
parse_michelin_table('michelin-kyoto-osaka2026.md', 'ミシュラン京阪2026', 2, 3)
parse_michelin_table('michelin-archive-new.md', 'ミシュラン過去年', 1, None)
parse_michelin_table('michelin-archive2-new.md', 'ミシュラン過去年2', 1, None)

# ゴ・エ・ミヨ 要確認
for ln in section_lines(read('gaultmillau.md'),
                        lambda l: l.startswith('## 要確認'), lambda l: l.startswith('## 新規')):
    if ln.startswith('- '):
        body = ln[2:]
        m = re.match(r'^(.*?)（([^（）]+)）｜(.+)$', body)
        if m:
            genre = m.group(3).split('｜')[-1] if '｜' in m.group(3) else ''
            note = m.group(3)
            add_unres(m.group(1), m.group(2).replace('・', ''), genre, 'ゴ・エ・ミヨ2026', note)
        else:
            add_unres(body.split('｜')[0], '', '', 'ゴ・エ・ミヨ2026', body)

# DR/OAD 要確認
for ln in section_lines(read('destination-oad.md'),
                        lambda l: l.startswith('## 要確認'), lambda l: l.startswith('## 新規')):
    if ln.startswith('- '):
        body = ln[2:]
        m = re.match(r'^(.*?)(?:（([^（）]*)）)?\s*→\s*(.+)$', body)
        if m:
            area = ''
            if m.group(2):
                mm = re.search(r'・([A-Za-z]+|[^・]+県|[^・]+府|東京都|北海道)$', m.group(2))
                area = m.group(2)
            add_unres(m.group(1), area, '', 'DR/OAD', m.group(3))

# Award過去年 要確認
for ln in section_lines(read('award-archive-new.md'),
                        lambda l: l.startswith('## 要確認'), lambda l: l.startswith('## 既存')):
    if ln.startswith('- '):
        body = ln[2:]
        main, _, note = body.partition(' ― ')
        p = main.split('｜')
        if len(p) >= 3:
            add_unres(p[0], p[2], p[1], 'Award過去年', note)

# Award過去年SB 要確認
for ln in section_lines(read('award-archive-silver-bronze-new.md'),
                        lambda l: l.startswith('## 要確認'), lambda l: l.startswith('## 取得')):
    if ln.startswith('- '):
        body = ln[2:]
        main, _, note = body.partition(' → ')
        p = main.split('｜')
        if len(p) >= 3:
            add_unres(p[0], p[2], p[1], 'Award過去年SB', note)

# ラリスト 要確認
for ln in section_lines(read('laliste-50best.md'),
                        lambda l: l.startswith('## 要確認'), lambda l: l.startswith('## 新規')):
    if ln.startswith('- '):
        p = ln[2:].split('｜')
        if len(p) >= 3:
            note = '｜'.join(p[3:])
            add_unres(p[0], p[2], '', 'ラリスト/50Best', note)

# 百名店系の要確認バレットを構造化
hyaku_unres = []
for u in unresolved_raw:
    if 'name' in u:
        continue
    raw = u['raw']
    m = re.match(r'^(.*?)｜([^｜]+?)(?:（選出:[^）]*）)?\s*(?:→\s*(.+))?$', raw)
    if m:
        hyaku_unres.append({'name': m.group(1).strip(), 'area': m.group(2).strip(), 'genre': '',
                            'source': u['source'], 'note': (m.group(3) or '').strip()})
    else:
        hyaku_unres.append({'name': raw.split('｜')[0].strip(), 'area': '', 'genre': '',
                            'source': u['source'], 'note': raw})
unresolved_all = [u for u in unresolved_raw if 'name' in u] + hyaku_unres
print('unresolved total entries:', len(unresolved_all))
print(Counter(u['source'] for u in unresolved_all))
json.dump(unresolved_all, open('/tmp/newpool_unresolved.json', 'w'), ensure_ascii=False)

# ============================================================
# Part 3: デデュープ(union-find 的グリーディ割当)・分類・出力
# ============================================================
SRC_PRIORITY = ['百名店2026', '百名店旧年', '百名店アーカイブ', 'Award2026', 'Award過去年', 'Award過去年SB',
                'ミシュラン東京2026', 'ミシュラン京阪2026', 'ミシュラン過去年', 'ミシュラン過去年2',
                'ゴ・エ・ミヨ2026', 'DR/OAD', 'TRY', 'ラリスト/50Best']
SRC_RANK = {s: i for i, s in enumerate(SRC_PRIORITY)}

def has_cjk(s):
    return any('぀' <= c <= '鿿' for c in s)

# グループ: {records:[], pref, city}
groups = []
alias_index = defaultdict(list)  # (alias, pref) -> [group_id]

def cities_compatible(a, b):
    if not a or not b:
        return True
    if a == b:
        return True
    return a.startswith(b) or b.startswith(a)  # 京都市 vs 京都市中京区 など親子関係

def city_compatible(g, rec):
    return cities_compatible(g['city'], rec['city'])

def find_group(rec):
    cands = []
    for a in aliases(rec['name']):
        for gid in alias_index.get((a, rec['pref']), []):
            if gid not in cands:
                cands.append(gid)
    for gid in cands:
        if city_compatible(groups[gid], rec):
            return gid
    return None

order = sorted(range(len(records)), key=lambda i: (SRC_RANK[records[i]['source']], i))
for i in order:
    rec = records[i]
    gid = find_group(rec) if rec['pref'] else None
    if gid is None:
        gid = len(groups)
        groups.append({'records': [], 'pref': rec['pref'], 'city': rec['city']})
    g = groups[gid]
    g['records'].append(rec)
    if rec['city'] and (not g['city'] or (rec['city'].startswith(g['city']) and len(rec['city']) > len(g['city']))):
        g['city'] = rec['city']
    if not g['pref'] and rec['pref']:
        g['pref'] = rec['pref']
    for a in aliases(rec['name']):
        if rec['pref']:
            alias_index[(a, rec['pref'])].append(gid)
        alias_index[(a, '')].append(gid) if False else None

# ---- Pass 2: ジャンル接頭辞除去名・ローマ字名での追加マージ ----
GENRE_PREFIXES = ["てんぷら", "天ぷら", "天麩羅", "鮨", "寿司", "寿し", "鮓", "すし", "日本料理", "レストラン", "焼肉", "焼き鳥", "焼鳥", "そば", "蕎麦", "うなぎ", "鰻", "ラーメン", "らーめん", "中華料理", "中国料理", "フレンチ", "イタリアン", "割烹", "料亭", "懐石", "会席", "京料理", "ふぐ", "河豚", "和食", "洋食", "ステーキハウス", "鉄板焼", "寿司処", "鮨処", "すし処", "寿し処", "鮓処", "山菜料理", "炭火焼肉", "郷土料理"]

def core_names(name):
    n = normalize(name)
    out = {n}
    for pre in GENRE_PREFIXES:
        pn = normalize(pre)
        if n.startswith(pn) and len(n) > len(pn) + 1:
            out.add(n[len(pn):])
    return out

KANA_ROMAJI = {
    "あ": "a", "い": "i", "う": "u", "え": "e", "お": "o", "か": "ka", "き": "ki", "く": "ku", "け": "ke", "こ": "ko",
    "さ": "sa", "し": "shi", "す": "su", "せ": "se", "そ": "so", "た": "ta", "ち": "chi", "つ": "tsu", "て": "te", "と": "to",
    "な": "na", "に": "ni", "ぬ": "nu", "ね": "ne", "の": "no", "は": "ha", "ひ": "hi", "ふ": "fu", "へ": "he", "ほ": "ho",
    "ま": "ma", "み": "mi", "む": "mu", "め": "me", "も": "mo", "や": "ya", "ゆ": "yu", "よ": "yo",
    "ら": "ra", "り": "ri", "る": "ru", "れ": "re", "ろ": "ro", "わ": "wa", "を": "wo", "ん": "n",
    "が": "ga", "ぎ": "gi", "ぐ": "gu", "げ": "ge", "ご": "go", "ざ": "za", "じ": "ji", "ず": "zu", "ぜ": "ze", "ぞ": "zo",
    "だ": "da", "ぢ": "ji", "づ": "zu", "で": "de", "ど": "do", "ば": "ba", "び": "bi", "ぶ": "bu", "べ": "be", "ぼ": "bo",
    "ぱ": "pa", "ぴ": "pi", "ぷ": "pu", "ぺ": "pe", "ぽ": "po",
    "きゃ": "kya", "きゅ": "kyu", "きょ": "kyo", "しゃ": "sha", "しゅ": "shu", "しょ": "sho",
    "ちゃ": "cha", "ちゅ": "chu", "ちょ": "cho", "にゃ": "nya", "にゅ": "nyu", "にょ": "nyo",
    "ひゃ": "hya", "ひゅ": "hyu", "ひょ": "hyo", "みゃ": "mya", "みゅ": "myu", "みょ": "myo",
    "りゃ": "rya", "りゅ": "ryu", "りょ": "ryo", "ぎゃ": "gya", "ぎゅ": "gyu", "ぎょ": "gyo",
    "じゃ": "ja", "じゅ": "ju", "じょ": "jo",
    "ー": "", "ぁ": "a", "ぃ": "i", "ぅ": "u", "ぇ": "e", "ぉ": "o", "っ": "", "ゃ": "ya", "ゅ": "yu", "ょ": "yo",
}

def romanize(s):
    s = "".join(chr(ord(c) - 0x60) if "ァ" <= c <= "ヶ" else c for c in s)
    out, i = [], 0
    while i < len(s):
        if i + 1 < len(s) and s[i:i + 2] in KANA_ROMAJI:
            out.append(KANA_ROMAJI[s[i:i + 2]]); i += 2
        elif s[i] in KANA_ROMAJI:
            out.append(KANA_ROMAJI[s[i]]); i += 1
        else:
            return ""
    return "".join(out)

def is_kana_only(raw):
    s = unicodedata.normalize("NFKC", raw)
    return bool(s) and all(("ぁ" <= c <= "ゖ" or "ァ" <= c <= "ヶ" or c in "ー・ 　") for c in s)

def group_keys(g, mode):
    keys = set()
    for r in g['records']:
        if mode == 'core':
            keys |= core_names(r['name'])
            for a in aliases(r['name']):
                keys |= core_names(a)
        elif mode == 'romaji':
            raw = re.sub(r'[\s　]', '', unicodedata.normalize('NFKC', r['name']))
            if is_kana_only(raw):
                rm = romanize(raw)
                if rm:
                    keys.add(rm)
            else:
                n = normalize(r['name'])
                if n and n.isascii():
                    keys.add(n)
    return keys

def merge_pass(mode):
    merged = 0
    idx = defaultdict(set)
    for gid, g in enumerate(groups):
        if not g['records'] or not g['pref']:
            continue
        for k in group_keys(g, mode):
            idx[(k, g['pref'])].add(gid)
    for (k, pref), gids in idx.items():
        gids = [x for x in gids if groups[x]['records']]
        if len(gids) < 2:
            continue
        base = gids[0]
        for other in gids[1:]:
            if not groups[other]['records']:
                continue
            if cities_compatible(groups[base]['city'], groups[other]['city']):
                groups[base]['records'].extend(groups[other]['records'])
                if len(groups[other]['city']) > len(groups[base]['city']):
                    groups[base]['city'] = groups[other]['city']
                groups[other]['records'] = []
                merged += 1
    return merged

m1 = merge_pass('core')
m2 = merge_pass('romaji')
groups = [g for g in groups if g['records']]
print('pass2 merges: core', m1, '/ romaji', m2, '-> groups:', len(groups))

# 都道府県不明レコード(pref='')を既存グループへ寄せる(完全名一致・候補が1つだけのとき)
attached = 0
for g in list(groups):
    if g['pref']:
        continue
    names = {normalize(r['name']) for r in g['records']}
    cand = set()
    for n in names:
        for (a, p), gids in alias_index.items():
            if a == n and p:
                cand.update(gids)
    cand = {c for c in cand if groups[c]['pref']}
    if len(cand) == 1:
        tgt = groups[list(cand)[0]]
        if city_compatible(tgt, g['records'][0]):
            tgt['records'].extend(g['records'])
            g['records'] = []
            attached += 1
groups = [g for g in groups if g['records']]
print('groups after dedupe:', len(groups), '(pref-less attached:', attached, ')')

# ---- グループ → 統合エントリ ----
def pick_display_name(g):
    recs = sorted(g['records'], key=lambda r: (SRC_RANK[r['source']],))
    for r in recs:
        if has_cjk(r['name']):
            return r['name']
    return recs[0]['name']

def area_display(g):
    if g['city']:
        if g['city'].startswith(('京都市', '大阪市')):
            return g['pref'] + g['city'] if not g['city'].startswith(g['pref']) else g['city']
        if g['pref'] and g['city'] != g['pref']:
            return g['pref'] + g['city']
        return g['city']
    broad = [r['area_raw'] for r in g['records'] if '・' in r['area_raw'] and r['source'] == 'ミシュラン過去年2']
    if broad:
        return (g['pref'] + ' ' if g['pref'] else '') + broad[0]
    if g['pref']:
        return g['pref']
    raws = [r['area_raw'] for r in g['records'] if r['area_raw']]
    return raws[0] if raws else 'エリア未確認'

entries = []
for g in groups:
    name = pick_display_name(g)
    srcs = sorted({r['source'] for r in g['records']}, key=lambda s: SRC_RANK[s])
    flags = set()
    for r in g['records']:
        flags.update(r['flags'])
    # ジャンル決定
    fixed = {}
    for r in g['records']:
        if r['genre_fixed']:
            fixed.setdefault(r['genre_fixed'], []).append(r['source'])
    mapped = {}
    for r in g['records']:
        mg = classify_genre_text(r['genre_text'])
        if mg:
            mapped.setdefault(mg, []).append(r['source'])
    genre = None
    genre_how = ''
    if fixed:
        genre = sorted(fixed.keys(), key=lambda k: min(SRC_RANK[s] for s in fixed[k]))[0]
        genre_how = 'fixed'
        others = {k for k in mapped if k != genre}
        if len(fixed) > 1:
            flags.add('ジャンル相違(ソース間): ' + ' / '.join(sorted(fixed.keys())))
        elif others:
            flags.add('ジャンル相違(百名店区分 vs 他ソース): ' + ' / '.join(sorted(others)))
    elif mapped:
        genre = sorted(mapped.keys(), key=lambda k: min(SRC_RANK[s] for s in mapped[k]))[0]
        genre_how = 'text'
        if len(mapped) > 1:
            flags.add('ジャンル相違(ソース間): ' + ' / '.join(sorted(mapped.keys())))
    else:
        ng = classify_name(name)
        if ng:
            genre = ng
            genre_how = 'name'
            flags.add('ジャンル推定(店名から)')
        else:
            genre = '要分類'
            genre_how = 'none'
            flags.add('要分類')
    if normalize(name) == 'ramenfeel' or any(normalize(r['name']) == 'ramenfeel' for r in g['records']):
        flags.add('閉店確認済み(2026年2月末・TRY公式注記)')
    if not has_cjk(name) and srcs == ['DR/OAD']:
        flags.add('日本語店名未確定(欧文表記のみ)')
    entries.append({
        'name': name, 'area': area_display(g), 'pref': g['pref'], 'city': g['city'],
        'genre': genre, 'genre_how': genre_how, 'sources': srcs,
        'flags': sorted(flags), 'n_records': len(g['records']),
    })

# 同名・同都道府県・別エリアのグループにフラグ
by_name_pref = defaultdict(list)
for e in entries:
    by_name_pref[(normalize(e['name']), e['pref'])].append(e)
for k, es in by_name_pref.items():
    cities = {e['city'] for e in es if e['city']}
    if len(es) > 1 and len(cities) > 1:
        for e in es:
            e['flags'] = sorted(set(e['flags']) | {'同名・同都道府県内に別エリアの店舗あり'})

print('unified entries:', len(entries))
print('genre counts:', Counter(e['genre'] for e in entries).most_common())
json.dump(entries, open('/tmp/newpool_entries.json', 'w'), ensure_ascii=False)

# ============================================================
# Part 4: 成果物出力
# ============================================================
import os, math
GENRE_ORDER = GENRE_ORDER + ['要分類']  # Part1定義の36ジャンルに要分類を追加
PREF_ORDER = {p: i for i, p in enumerate(PREFS)}

def entry_sort_key(e):
    return (GENRE_ORDER.index(e['genre']), PREF_ORDER.get(e['pref'], 99), e['name'])

entries_sorted = sorted(entries, key=entry_sort_key)

# --- TSV ---
with open('new-pool-unified.tsv', 'w', encoding='utf-8') as f:
    f.write('店名\tエリア/最寄り\t百名店ジャンル\t出典ソース\t備考フラグ\n')
    for e in entries_sorted:
        f.write('\t'.join([e['name'], e['area'], e['genre'], '、'.join(e['sources']), '、'.join(e['flags'])]) + '\n')

# --- chunks ---
os.makedirs('chunks/new', exist_ok=True)
for old_f in os.listdir('chunks/new'):
    os.remove(os.path.join('chunks/new', old_f))
chunk_files = {}
for genre in GENRE_ORDER:
    es = [e for e in entries_sorted if e['genre'] == genre]
    files = []
    for i in range(0, len(es), 50):
        part = es[i:i + 50]
        fn = f'chunks/new/{genre}-{i // 50 + 1}.txt'
        with open(fn, 'w', encoding='utf-8') as f:
            for e in part:
                f.write(f"{e['name']}（エリア：{e['area']}）\n")
        files.append(fn)
    chunk_files[genre] = files
total_chunk_files = sum(len(v) for v in chunk_files.values())

# --- unresolved 集約 ---
unres_map = {}
for u in unresolved_all:
    key = (normalize(u['name']), u['area'])
    if key not in unres_map:
        unres_map[key] = {'name': u['name'], 'area': u['area'], 'genre': u['genre'], 'sources': [], 'notes': []}
    m = unres_map[key]
    if u['source'] not in m['sources']:
        m['sources'].append(u['source'])
    if u['genre'] and not m['genre']:
        m['genre'] = u['genre']
    if u['note'] and u['note'] not in m['notes']:
        m['notes'].append(u['note'])
unres_list = sorted(unres_map.values(), key=lambda u: (SRC_RANK.get(u['sources'][0], 99), u['name']))
with open('new-pool-unresolved.md', 'w', encoding='utf-8') as f:
    f.write('# 新規プール 要確認集約（追加チャンクには含めない）\n\n')
    f.write(f'各プールファイルの「要確認」節から集約。 raw {len(unresolved_all)}件 → 店名+エリアで名寄せ後 {len(unres_list)}件。\n')
    f.write('いずれも「保存済み店の表記ゆれ候補」であり、新規追加の前に保存リスト側との照合が必要。\n\n')
    cur_src = None
    for u in unres_list:
        s0 = u['sources'][0]
        if s0 != cur_src:
            cur_src = s0
            f.write(f"\n## 主ソース: {s0}\n\n")
        parts = [u['name'], u['area'] or 'エリア不明']
        if u['genre']:
            parts.append(u['genre'])
        line = '｜'.join(parts)
        extra = []
        if len(u['sources']) > 1:
            extra.append('他ソース: ' + '、'.join(u['sources'][1:]))
        extra += u['notes']
        if extra:
            line += ' ― ' + ' ／ '.join(extra)
        f.write(f'- {line}\n')

# --- summary ---
src_input = Counter(r['source'] for r in records)
src_in_entries = Counter()
src_single = Counter()
for e in entries:
    for s in e['sources']:
        src_in_entries[s] += 1
    if len(e['sources']) == 1:
        src_single[e['sources'][0]] += 1
dist = Counter(len(e['sources']) for e in entries)
genre_counts = Counter(e['genre'] for e in entries)
n_inferred = sum(1 for e in entries if any('ジャンル推定' in f for f in e['flags']))
n_diff = sum(1 for e in entries if any('ジャンル相違' in f for f in e['flags']))
n_yobun = sum(1 for e in entries if any('欧文表記' in f for f in e['flags']))
n_area_unknown = sum(1 for e in entries if 'エリア未確認' in e['flags'])
n_same_name = sum(1 for e in entries if any('同名・同都道府県内' in f for f in e['flags']))

with open('new-pool-summary.md', 'w', encoding='utf-8') as f:
    f.write('# 新規プール統合サマリ（2026-10-29）\n\n')
    f.write('## 概要\n\n')
    f.write(f'- 入力レコード（全14プールの新規／増分節）: {len(records):,}件\n')
    f.write(f'- 統合後ユニーク店舗: **{len(entries):,}店**（重複 {len(records) - len(entries):,}件を名寄せ）\n')
    f.write(f'- 追加チャンク: chunks/new/ に {total_chunk_files}ファイル（1ファイル50店まで）\n')
    f.write(f'- 要分類: {genre_counts.get("要分類", 0)}店（「その他」へは逃がさず専用チャンクに分離）\n')
    f.write(f'- 要確認（別ファイル集約・チャンク外）: raw {len(unresolved_all)}件 → {len(unres_list)}件\n\n')
    f.write('注: hyakumeiten-archive-new.md は収集側の全量再突合で確定版に更新済み（増分新規 2,872→**3,271店**、要確認 480→557件。同ファイルの突合集計が正）。本統合はこの確定版を入力としている。\n\n')
    f.write('## ジャンル別件数\n\n| ジャンル | 店数 | チャンク数 |\n|---|---:|---:|\n')
    for genre in GENRE_ORDER:
        f.write(f'| {genre} | {genre_counts.get(genre, 0)} | {len(chunk_files[genre])} |\n')
    f.write(f'| **合計** | **{len(entries)}** | **{total_chunk_files}** |\n\n')
    f.write('## ソース別\n\n| ソース | 入力レコード | 含む統合店 | そのソースのみの店 |\n|---|---:|---:|---:|\n')
    for s in SRC_PRIORITY:
        f.write(f'| {s} | {src_input.get(s, 0)} | {src_in_entries.get(s, 0)} | {src_single.get(s, 0)} |\n')
    f.write('\n## 重複の状況\n\n')
    for k in sorted(dist.keys()):
        f.write(f'- 出典{k}ソースの店: {dist[k]}店\n')
    f.write(f'- 複数ソースに跨る店: {sum(v for k, v in dist.items() if k >= 2)}店\n\n')
    f.write('## フラグ内訳\n\n')
    f.write(f'- 要分類: {genre_counts.get("要分類", 0)}店（大半はジャンル欄の無い DR/OAD 由来）\n')
    f.write(f'- ジャンル推定（店名から）: {n_inferred}店\n')
    f.write(f'- ジャンル相違（ソース間で区分が異なる）: {n_diff}店\n')
    f.write(f'- エリア未確認: {n_area_unknown}店（TRY由来）\n')
    f.write(f'- 日本語店名未確定（欧文表記のみ・DR/OAD単独）: {n_yobun}店\n')
    f.write(f'- 同名・同都道府県内に別エリアの店舗あり: {n_same_name}店\n')
    f.write('- 閉店確認済み: 1店（Ramen FeeL、東京都。2026年2月末閉店・TRY公式注記。除外交ぜず含めている）\n\n')
    f.write('## デデュープ方式と留保\n\n')
    f.write('- 名寄せキー: 正規化店名（NFKC・表記ゆれ統一・記号除去、既存 match-archive.py と同一方式）のエイリアス（括弧内・括弧除去・／分割）＋都道府県。一致しても市区町村が食い違う場合は別店として分離（支店・別立地の温存）。市区町村は親子関係（京都市 vs 京都市中京区）を同一とみなす。\n')
    f.write('- 追加マージ: ジャンル接頭辞（「日本料理」「鮨」等）を除いた店名での一致、カナ店名のローマ字化での一致も統合した。\n')
    f.write('- 留保: ローマ字⇔カナの混交表記（例: TACUBO 白金台 と タクボ 白金台）は同一店でも統合しきれていないものが残る可能性がある。追加作業時にマップ側で重複に気付いたら片方を外せばよい。\n')
    f.write('- ジャンル決定の優先順位: 百名店の版ジャンル（固定）＞ 各ソースのジャンル表記を regroup.py の RULES で写像 ＞ 店名からの推定（フラグ付き）。固定ジャンルと他ソース写像が食い違う場合は百名店区分を採り、相違フラグを付けた。\n')
    f.write('- エリア/最寄り列: 駅情報はプールに無いため、都道府県＋市区町村（判明分）を格納。チャンクでは全店「（エリア：〜）」形式で、マップ追加時に店名＋エリアで検索する想定。\n')

print('WROTE: tsv / chunks', total_chunk_files, '/ unresolved unique', len(unres_list))
