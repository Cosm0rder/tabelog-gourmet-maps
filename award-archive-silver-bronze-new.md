# The Tabelog Award 過去年 SILVER／BRONZE 全件収集と突合結果

作成：2026-10-28
出典：食べログアワード公式アーカイブ（日本語版）https://award.tabelog.com/<年>/restaurants/<ランク>（2019〜2025年。2018年は旧形式 https://award.tabelog.com/2018/restaurants?main_prizes[]=<ランク> ）
原データ：award-archive-raw-<年>-<ランク>.md（2018〜2025年のSILVER/BRONZE全件。2025 SILVERは先行取得分 award-archive-raw-2025-silver.md）
突合先：保存リスト saved-list.md（1,433件）＋Award2026（award2026.md）＋ミシュラン東京2026／京都・大阪2026＋百名店2026／旧年版＋Destination/OAD＋ゴ・エ・ミヨ＋award-archive-new.md（増分6店含む）。正規化ユニーク名で計9,560件
突合方法：店名を正規化（NFKC・小文字化・スペース/中黒/記号除去・異体字統一）して完全一致＝既存。支店サフィックス除去・ジャンル接頭辞除去・包含・編集距離1〜2＝要確認。それ以外＝増分新規。カナのみ店名はローマ字化でも照合

## 照合表（年×ランク：公式発表数／アーカイブ表示／取得件数）

| 年 | GOLD（発表/アーカイブ/照合） | SILVER（発表/取得） | BRONZE（発表/取得） | 判定 |
|---|---|---|---|---|
| 2017 | 28 / 28 / 一致 | 89 / **取得不可** | 395 / **取得不可** | GOLDのみ照合可（下記注記） |
| 2018 | 33 / 33 / 一致 | 約120（PRは約数） / 124 | 約400（PRは約数） / 423 | アーカイブ公式表示（計580店）と一致 |
| 2019 | 30 / 30 / 一致 | 121 / 121 | 467 / 467 | 全ランク一致 |
| 2020 | 34 / 34 / 一致 | 102 / 102 | 488 / 488 | 全ランク一致 |
| 2021 | 32 / 32 / 一致 | 108 / 108 | 396 / 396 | 全ランク一致 |
| 2022 | 31 / 31 / 一致 | 107 / 107 | 384（PR計522） / **385**（アーカイブ計523） | **BRONZEに1件差異**（アーカイブ側が1店多い。PR発表の総数522と別転載・公式表示523の既知の食い違いと同一） |
| 2023 | 30 / 30 / 一致 | 100 / 100 | 340 / 340 | 全ランク一致 |
| 2024 | 35 / 35 / 件数一致（表記差異あり） | 101 / 101 | 320 / 320 | GOLDの店名表記に1件差異：復元リスト「鮨 なんば」 vs アーカイブ「鮨 なんば 日比谷」（同一店の拡張表記とみられる） |
| 2025 | 35 / 35 / 一致 | 151 / 151（先行取得ファイルの収録は150件、下記注記） | 467 / 467 | ほぼ一致 |

注記：
- 2017年は公式アーカイブに一覧ページが存在しない（2017年版サイトはトップページのカルーセル表示のみで、/2017/restaurants 配下は全て404。SILVER 89店・BRONZE 395店の全店リストは公式・PRとも公開されておらず取得不可）。GOLD 28店はトップページに全店表示され、復元リストと店数・店名とも一致を確認した
- 2025 SILVERの先行取得ファイル（award-archive-raw-2025-silver.md）は店名のみ・／区切り形式で、収録は150件だった（公式表示151件。1件は同名店の重複か転記漏れの可能性があり未検証）。突合には150件を含めた
- 取得総数：SILVER 913件＋BRONZE 3,286件＝延べ4,199件（2018〜2025年。公式表示ベースではSILVER 914件・計4,200件）。年・都道府県を跨いだ重複を除いたユニーク単位は1,330件

## 突合結果サマリー

| 分類 | 件数 |
|---|---|
| 既存（保存リストまたはいずれかのプールと完全一致） | 1,086 |
| 要確認（表記ゆれ・包含・近接の候補あり） | 139 |
| **増分新規（過去年SILVER/BRONZEでのみ受賞し、どこにも無い店）** | **105** |
| 合計（ユニーク単位） | 1,330 |

## 増分新規（105店）

形式：店名｜ジャンル｜都道府県｜受賞歴（今回収集したSILVER/BRONZEの範囲）

- くずし懐石 縁｜日本料理｜京都｜2018 BRONZE, 2019 BRONZE
- 京 上賀茂 御料理秋山｜日本料理｜京都｜2018 BRONZE, 2019 BRONZE, 2020 BRONZE, 2021 BRONZE, 2022 BRONZE
- 京趣味 菱岩｜その他｜京都｜2020 BRONZE
- 割烹 やました｜日本料理｜京都｜2019 BRONZE
- 味 ふくしま｜日本料理｜京都｜2018 BRONZE, 2019 BRONZE, 2020 BRONZE
- スポンテニアス｜フレンチ｜兵庫｜2018 BRONZE
- ミシェル・ブラス トーヤ ジャポン｜フレンチ｜北海道｜2018 BRONZE
- 焼肉ひび屋｜焼肉・すき焼き・しゃぶしゃぶ｜北海道｜2018 BRONZE, 2019 BRONZE
- トラットリア・アルベロ｜イタリアン｜千葉｜2018 BRONZE, 2019 BRONZE
- 蔓山｜中華料理｜千葉｜2022 BRONZE
- かしわや 闘鶏｜焼き鳥・鳥料理｜大阪｜2018 BRONZE, 2019 BRONZE, 2020 BRONZE, 2021 BRONZE, 2022 BRONZE
- グラン シャン｜フレンチ｜大阪｜2018 BRONZE, 2019 BRONZE, 2020 BRONZE
- 又三郎 本店｜焼肉・すき焼き・しゃぶしゃぶ｜大阪｜2018 BRONZE
- 懐石料理 桝田｜日本料理｜大阪｜2018 BRONZE, 2019 BRONZE
- 肥後橋 やま本｜日本料理｜大阪｜2018 BRONZE
- みょうが屋｜焼肉・すき焼き・しゃぶしゃぶ｜宮崎｜2020 BRONZE
- とおの屋 要｜創作料理｜岩手｜2023 BRONZE, 2024 BRONZE
- 要｜創作料理｜岩手｜2022 BRONZE
- とんかつあさくら｜とんかつ・揚げ物｜愛知｜2019 BRONZE, 2022 BRONZE
- エノテーカ ピンキオーリ 名古屋｜イタリアン｜愛知｜2020 BRONZE
- ビストロ ダイア｜フレンチ｜愛知｜2018 BRONZE, 2019 BRONZE, 2020 BRONZE, 2021 BRONZE
- レスト ケイ ヤマウチ｜フレンチ｜愛知｜2020 BRONZE
- 得仙｜日本料理｜愛知｜2019 BRONZE, 2020 BRONZE, 2021 BRONZE, 2022 BRONZE
- 明道町中国菜 一星｜中華料理｜愛知｜2020 BRONZE, 2021 BRONZE, 2022 BRONZE
- my farm to table おにや｜焼き鳥・鳥料理｜新潟｜2024 BRONZE, 2025 BRONZE
- ALLIE｜フレンチ｜東京｜2018 BRONZE, 2019 BRONZE, 2020 BRONZE
- FURUYA augastronome｜フレンチ｜東京｜2019 BRONZE, 2020 BRONZE
- Fukushima｜フレンチ｜東京｜2019 BRONZE
- GINZA JOTAKI｜中華料理｜東京｜2020 BRONZE, 2021 BRONZE, 2022 BRONZE ※保存側の「銀座 上瀧」（中華料理・東京）と同一店の可能性が高い（欧文表記違い）
- Le Bonze｜フレンチ｜東京｜2019 BRONZE
- Le Ciel｜フレンチ｜東京｜2019 BRONZE, 2020 BRONZE
- Libre｜フレンチ｜東京｜2020 BRONZE
- Lien Prive de Lien｜フレンチ｜東京｜2018 BRONZE
- Ryoco｜スイーツ｜東京｜2018 BRONZE
- TAKAZAWA｜イノベーティブ・フュージョン｜東京｜2018 BRONZE
- TIRPSE｜創作料理｜東京｜2018 BRONZE
- TRATTORIA GANZO｜イタリアン｜東京｜2018 BRONZE, 2019 BRONZE
- VIA BRIANZA｜イタリアン｜東京｜2021 BRONZE
- aca 1°｜スペイン料理｜東京｜2021 SILVER ※保存側の「アカ」（スペイン料理・東京）と同一店の可能性が高い（欧文表記違い）
- eclat｜フレンチ｜東京｜2019 BRONZE
- pâtisserie Paris S'éveille｜スイーツ｜東京｜2021 BRONZE
- stesso e Magari CHIC｜イタリアン｜東京｜2018 BRONZE, 2019 BRONZE
- Äta｜フレンチ｜東京｜2021 BRONZE
- うなぎ 赤坂 勢きね｜うなぎ｜東京｜2020 BRONZE
- しんせん 割烹 佐乃家｜日本料理｜東京｜2019 BRONZE, 2020 BRONZE
- つくしのこ｜居酒屋｜東京｜2018 BRONZE
- アッピア 本店｜イタリアン｜東京｜2018 BRONZE, 2019 BRONZE, 2020 BRONZE
- アヒルストア｜フレンチ｜東京｜2018 BRONZE, 2019 BRONZE
- アーティショー｜フレンチ｜東京｜2018 BRONZE, 2019 BRONZE
- イデミスギノ｜スイーツ｜東京｜2018 SILVER, 2019 BRONZE, 2020 BRONZE, 2021 BRONZE, 2022 BRONZE
- エルバ ダ ナカヒガシ｜イタリアン｜東京｜2018 BRONZE, 2019 BRONZE, 2020 BRONZE
- オルグイユ｜フレンチ｜東京｜2018 BRONZE, 2019 BRONZE, 2020 BRONZE
- サトブリDA｜焼肉・すき焼き・しゃぶしゃぶ｜東京｜2020 BRONZE, 2021 BRONZE, 2022 BRONZE, 2023 BRONZE, 2024 BRONZE
- サラマンジェ ド イザシ ワキサカ｜フレンチ｜東京｜2018 BRONZE, 2019 BRONZE, 2020 BRONZE
- シェ松尾・松濤レストラン｜フレンチ｜東京｜2018 BRONZE, 2019 BRONZE
- ダム・ジャンヌ｜フレンチ｜東京｜2018 BRONZE, 2019 BRONZE, 2020 BRONZE
- パッソ・ア・パッソ｜イタリアン｜東京｜2018 BRONZE, 2019 BRONZE
- ビオディナミコ｜イタリアン｜東京｜2018 BRONZE
- フェリチェリーナ｜イタリアン｜東京｜2018 BRONZE
- ホスタリア エル・カンピドイオ｜イタリアン｜東京｜2018 BRONZE, 2019 BRONZE
- ボナ フェスタ｜その他｜東京｜2018 BRONZE, 2019 BRONZE, 2020 BRONZE
- メンドコロ Kinari｜ラーメン｜東京｜2021 BRONZE
- ラ クレリエール｜フレンチ｜東京｜2018 BRONZE, 2019 BRONZE, 2020 BRONZE, 2021 BRONZE, 2022 BRONZE, 2023 BRONZE, 2024 BRONZE, 2025 BRONZE
- ラパルタメント ディ ナオキ｜イタリアン｜東京｜2018 BRONZE, 2019 BRONZE, 2020 BRONZE, 2021 BRONZE
- ラール・エ・ラ・マニエール｜フレンチ｜東京｜2019 BRONZE, 2020 BRONZE
- リストランテ エッフェ｜イタリアン｜東京｜2018 BRONZE
- リストランテ カッパス｜イタリアン｜東京｜2018 BRONZE, 2019 BRONZE
- ルメルシマン オカモト｜フレンチ｜東京｜2018 BRONZE, 2019 BRONZE, 2020 BRONZE
- ル・マノアール・ダスティン｜フレンチ｜東京｜2018 BRONZE, 2019 BRONZE, 2020 BRONZE
- レストラン クレッセント｜フレンチ｜東京｜2018 BRONZE, 2019 BRONZE, 2020 BRONZE
- レストラン サンパウ｜スペイン料理｜東京｜2018 BRONZE, 2019 BRONZE
- レストラン タテル ヨシノ 銀座｜フレンチ｜東京｜2018 BRONZE, 2019 BRONZE, 2020 BRONZE
- ヴォーロ・コズィ｜イタリアン｜東京｜2018 BRONZE
- 世良田｜焼き鳥・鳥料理｜東京｜2018 BRONZE
- 中勢以 内店｜ステーキ・鉄板焼き｜東京｜2018 BRONZE, 2019 BRONZE, 2020 BRONZE
- 中華 うずまき｜中華料理｜東京｜2018 BRONZE, 2019 BRONZE, 2020 BRONZE
- 中華たかせ｜中華料理｜東京｜2018 BRONZE, 2019 BRONZE, 2020 BRONZE, 2021 BRONZE
- 久遠の空｜創作料理｜東京｜2019 BRONZE, 2020 BRONZE
- 和食 こんどう｜日本料理｜東京｜2018 BRONZE, 2019 BRONZE, 2020 BRONZE
- 器楽亭｜日本料理｜東京｜2018 BRONZE, 2019 BRONZE, 2020 BRONZE
- 寿し処 寿々｜寿司｜東京｜2018 BRONZE, 2019 BRONZE, 2020 BRONZE
- 寿司 いずみ｜寿司｜東京｜2018 BRONZE, 2019 BRONZE, 2020 BRONZE
- 手打式超多加水麺 ののくら｜ラーメン｜東京｜2021 BRONZE, 2022 BRONZE
- 海鮮名菜 香宮｜中華料理｜東京｜2018 BRONZE, 2019 BRONZE, 2020 BRONZE, 2021 BRONZE
- 焼肉 いぶさな｜焼肉・すき焼き・しゃぶしゃぶ｜東京｜2021 BRONZE, 2022 BRONZE
- 神楽坂 鉄板焼 中むら｜ステーキ・鉄板焼き｜東京｜2019 BRONZE, 2020 BRONZE, 2021 BRONZE, 2022 BRONZE, 2023 BRONZE, 2024 BRONZE, 2025 BRONZE
- 第三春美鮨｜寿司｜東京｜2018 BRONZE, 2019 BRONZE, 2020 BRONZE
- 羊SUNRISE｜焼肉・すき焼き・しゃぶしゃぶ｜東京｜2020 BRONZE, 2021 BRONZE
- 翁｜日本料理｜東京｜2018 BRONZE, 2019 BRONZE
- 艪｜寿司｜東京｜2018 BRONZE
- 青華こばやし｜日本料理｜東京｜2020 BRONZE, 2021 BRONZE
- 飄香 麻布十番本店｜中華料理｜東京｜2018 BRONZE, 2019 BRONZE
- 滋味 康月｜日本料理｜滋賀｜2018 BRONZE, 2019 BRONZE, 2020 BRONZE
- 太平寿し｜寿司｜石川｜2018 SILVER, 2019 SILVER, 2020 BRONZE, 2021 BRONZE, 2022 BRONZE
- Variante｜イタリアン｜神奈川｜2018 BRONZE, 2019 BRONZE, 2020 BRONZE
- ソリス アグリトゥーリズモ｜イタリアン｜神奈川｜2019 BRONZE
- ミッシェル ナカジマ｜フレンチ｜神奈川｜2018 BRONZE, 2019 BRONZE
- ヴィノテカサクラ｜イタリアン｜神奈川｜2019 BRONZE
- 佛蘭西料理 名古屋｜フレンチ｜神奈川｜2018 BRONZE, 2019 BRONZE, 2020 BRONZE, 2021 BRONZE
- 嗣味｜日本料理｜福岡｜2022 BRONZE, 2023 BRONZE, 2024 BRONZE
- 御宿かわせみ｜その他｜福島｜2020 BRONZE, 2022 BRONZE, 2023 BRONZE, 2024 BRONZE
- 元祖 むらさき｜日本料理｜秋田｜2018 BRONZE, 2019 BRONZE
- 昔のきりたんぽや｜日本料理｜秋田｜2019 BRONZE, 2020 BRONZE
- 堂山｜日本料理｜長崎｜2025 BRONZE
- 座屋｜日本料理｜高知｜2019 BRONZE

## 要確認（139店）

形式：アーカイブ側店名｜ジャンル｜都道府県｜受賞歴 → 候補（突合先での表記｜出典｜判定理由）

- AU GAMIN DE TOKIO｜フレンチ｜東京｜2018 BRONZE → TOKi（保存リスト・包含）
- Amandier｜フレンチ｜東京｜2024 BRONZE, 2025 BRONZE → An Di（hyakumeiten-2026-new.md・包含）
- B｜フレンチ｜東京｜2019 BRONZE, 2020 BRONZE → bb9（保存リスト・編集距離2）
- CROWN｜フレンチ｜東京｜2018 BRONZE, 2019 BRONZE → Crony（保存リスト・編集距離2）
- Gris｜フレンチ｜東京｜2018 BRONZE → gii（hyakumeiten-2026-new.md・編集距離2）
- Hagiフランス料理店｜フレンチ｜福島｜2021 BRONZE, 2022 BRONZE → HAGI（award2026.md・包含）
- INUA｜イノベーティブ・フュージョン｜東京｜2019 BRONZE, 2020 BRONZE → INDU（hyakumeiten-2026-new.md・編集距離2）
- LOOP｜創作料理｜東京｜2022 BRONZE → LOOP TOKYO（hyakumeiten-older-new.md・包含）
- Lien｜フレンチ｜東京｜2019 BRONZE, 2020 BRONZE → Lito（award2026.md・編集距離2）
- MAVO｜フレンチ｜京都｜2018 BRONZE, 2019 BRONZE, 2020 BRONZE → MANO（hyakumeiten-2026-new.md・編集距離1）
- OGINO Red&Green Restaurant｜フレンチ｜東京｜2018 BRONZE → EST!（hyakumeiten-older-new.md・包含）
- OGINO organic Restaurant｜フレンチ｜東京｜2019 BRONZE → EST!（hyakumeiten-older-new.md・包含）
- THIERRY MARX｜フレンチ｜東京｜2018 BRONZE, 2019 BRONZE → MAR（hyakumeiten-older-new.md・包含）
- THIERRY MARX salon｜フレンチ｜東京｜2020 BRONZE → MAR（hyakumeiten-older-new.md・包含）
- TXOKO｜イタリアン｜東京｜2019 BRONZE → TOKi（保存リスト・編集距離2）
- USHIGORO S｜焼肉・すき焼き・しゃぶしゃぶ｜東京｜2018 SILVER → USHIGORO S. GINZA（保存リスト・包含）
- acca｜イタリアン｜岡山｜2021 BRONZE, 2022 BRONZE → Ata（hyakumeiten-older-new.md・編集距離2）
- broc 長谷川稔Lab｜フレンチ｜東京｜2021 BRONZE → 長谷川 稔（保存リスト・包含）
- あか吉｜寿司｜愛媛｜2024 BRONZE → あかぎ（hyakumeiten-2026-new.md・編集距離1）
- うな富士｜うなぎ｜愛知｜2019 BRONZE, 2020 BRONZE, 2021 BRONZE, 2022 BRONZE → 炭焼 うな富士 有楽町店（保存リスト・包含）
- う越貞｜魚介料理・海鮮料理｜大阪｜2020 BRONZE, 2021 BRONZE, 2022 BRONZE → うし松（hyakumeiten-2026-new.md・編集距離2）
- さえき｜寿司｜京都｜2020 BRONZE, 2021 BRONZE, 2022 BRONZE → 北新地 さえき（保存リスト・包含）
- さえ喜｜寿司｜大阪｜2018 SILVER → 鮨 さえ喜（保存リスト・包含）
- すし佐竹｜寿司｜東京｜2019 BRONZE, 2020 BRONZE → すし兆（hyakumeiten-older-new.md・編集距離2）
- すし善 本店｜寿司｜北海道｜2018 BRONZE → すし善（michelin-kyoto-osaka2026.md・接頭辞/接尾辞除去一致）
- すし家｜寿司｜東京｜2018 BRONZE, 2019 BRONZE → すし家 一柳（保存リスト・包含）
- たこつぼ｜日本料理｜広島｜2020 BRONZE, 2021 BRONZE → たつみ（hyakumeiten-older-new.md・編集距離2）
- ふぐ 牧野｜魚介料理・海鮮料理｜東京｜2018 BRONZE, 2019 BRONZE, 2020 BRONZE, 2021 BRONZE, 2022 BRONZE, 2023 BRONZE, 2025 BRONZE → 牧野（hyakumeiten-2026-new.md・接頭辞/接尾辞除去一致）
- ふぐ 福治｜魚介料理・海鮮料理｜東京｜2018 BRONZE, 2019 BRONZE, 2020 BRONZE, 2021 BRONZE, 2022 BRONZE → 福治（destination-oad.md・接頭辞/接尾辞除去一致）
- ほかけ｜寿司｜東京｜2019 BRONZE, 2020 BRONZE → ほうば（award-archive-new.md・編集距離2）
- まる富｜日本料理｜東京｜2018 BRONZE, 2019 BRONZE, 2020 BRONZE, 2021 BRONZE → 神楽坂 まる富（michelin-tokyo2026.md・包含）
- むろい｜日本料理｜京都｜2018 BRONZE, 2019 BRONZE → むさし（hyakumeiten-older-new.md・編集距離2）
- もり田｜寿司｜福岡｜2020 BRONZE → もめん（保存リスト・編集距離2）
- やきとり心香｜焼き鳥・鳥料理｜東京｜2018 BRONZE, 2019 BRONZE → やきとり 右羽。（hyakumeiten-older-new.md・編集距離2）
- らぁ麺 飯田商店｜｜｜2025 SILVER → 飯田商店（award2026.md・包含）
- らぁ麺 飯田商店｜ラーメン｜神奈川｜2020 BRONZE, 2021 BRONZE, 2022 BRONZE, 2023 BRONZE, 2024 BRONZE → 飯田商店（award2026.md・包含）
- らぁ麺屋 飯田商店｜ラーメン｜神奈川｜2018 BRONZE, 2019 BRONZE → 飯田商店（award2026.md・包含）
- アカーチェ｜イタリアン｜東京｜2018 BRONZE, 2019 BRONZE, 2020 BRONZE → アカ（保存リスト・包含）
- アルドアック｜スペイン料理｜東京｜2020 BRONZE → アドック（michelin-kyoto-osaka2026.md・編集距離2）
- ア・ニュ ルトゥルヴェ・ヴー｜フレンチ｜東京｜2018 BRONZE, 2019 BRONZE → アニュ（michelin-kyoto-osaka2026.md・包含）
- エッグ｜その他｜東京｜2018 BRONZE → 玉子物語 エッグストーリー（hyakumeiten-older-new.md・包含）
- エリタージュ｜フレンチ｜愛知｜2018 BRONZE, 2019 BRONZE, 2020 BRONZE → エリタージュ バイ ケイ コバヤシ（michelin-tokyo2026.md・包含）
- エル ブランシュ｜フレンチ｜東京｜2018 BRONZE → ラ・ピエール・ブランシュ 元町店（hyakumeiten-2026-new.md・包含）
- エール｜フレンチ｜東京｜2018 BRONZE, 2019 BRONZE, 2020 BRONZE → ラ・トゥーエル（保存リスト・包含）
- オルタナティブ｜フレンチ｜東京｜2020 BRONZE → オルタナティヴ（michelin-tokyo2026.md・編集距離1）
- カルパシ｜アジア・エスニック｜東京｜2021 BRONZE, 2022 BRONZE → カルーソー（hyakumeiten-older-new.md・編集距離2）
- カレーライス ディラン｜アジア・エスニック｜東京｜2020 BRONZE → ライース（michelin-kyoto-osaka2026.md・包含）
- カントニーズ 燕 ケン タカセ｜中華料理｜東京｜2018 BRONZE, 2019 BRONZE, 2020 BRONZE → カントニーズ 燕（hyakumeiten-2026-new.md・包含）
- キャラバン ステーキ専門店｜ステーキ・鉄板焼き｜佐賀｜2022 BRONZE → キャラバン（award2026.md・包含）
- グリグリ｜フレンチ｜東京｜2018 BRONZE, 2019 BRONZE, 2020 BRONZE → グリーチネ（hyakumeiten-older-new.md・編集距離2）
- サイフォン｜アジア・エスニック｜東京｜2018 BRONZE → サフラン（hyakumeiten-older-new.md・編集距離2）
- シャンペトル｜フレンチ｜東京｜2018 BRONZE → シャントレル（hyakumeiten-older-new.md・編集距離2）
- シュマン｜フレンチ｜東京｜2018 BRONZE, 2019 BRONZE, 2020 BRONZE → ボンシュマン（michelin-tokyo2026.md・包含）
- スゥリル｜フレンチ｜東京｜2018 BRONZE, 2019 BRONZE → スィークル（michelin-tokyo2026.md・編集距離2）
- センス｜中華料理｜東京｜2018 BRONZE, 2019 BRONZE, 2020 BRONZE → 広東料理 センス（保存リスト・包含）
- ヒロヤ｜創作料理｜東京｜2018 BRONZE → パティシエ・ヒロ ヤマモト（保存リスト・包含）
- ビンゴ｜イタリアン｜東京｜2018 BRONZE → ビアード（gaultmillau.md・編集距離2）
- ピエール・ガニェール｜フレンチ｜東京｜2018 BRONZE → ピエール（保存リスト・包含）
- マノワール・ディノ｜フレンチ｜東京｜2018 BRONZE, 2019 BRONZE, 2020 BRONZE → マノワ（michelin-tokyo2026.md・包含）
- ラ・ボッテガ・ゴローザ｜イタリアン｜神奈川｜2018 BRONZE, 2019 BRONZE → ボッテガ（michelin-tokyo2026.md・包含）
- リストランテ センソ｜イタリアン｜東京｜2018 BRONZE, 2019 BRONZE, 2020 BRONZE → リストランテ ペガソ（hyakumeiten-older-new.md・編集距離2）
- リストリア ラディーチェ｜イタリアン｜京都｜2019 BRONZE → ラディーチェ（michelin-kyoto-osaka2026.md・包含）
- ル・クープル｜フレンチ｜千葉｜2018 BRONZE → ルー・ド・メール（保存リスト・編集距離2）
- ル・ジャルダン・デ・サヴール｜フレンチ｜東京｜2018 BRONZE, 2019 BRONZE, 2020 BRONZE, 2021 BRONZE → ル・ジャルダン（hyakumeiten-older-new.md・包含）
- レストラン ひらまつ｜フレンチ｜東京｜2018 BRONZE, 2019 BRONZE → レストランひらまつ 広尾（hyakumeiten-older-new.md・包含）
- レストラン アルシミスト｜フレンチ｜東京｜2018 BRONZE → アルシミスト（michelin-tokyo2026.md・接頭辞/接尾辞除去一致）
- レストラン コバヤシ｜フレンチ｜東京｜2018 BRONZE, 2019 BRONZE, 2020 BRONZE → コバヤシ（gaultmillau.md・接頭辞/接尾辞除去一致）
- レストラン ビオス｜フレンチ｜静岡｜2018 BRONZE → レストラン エス（gaultmillau.md・編集距離2）
- レストラン フウ｜フレンチ｜東京｜2019 BRONZE → レストラン 5（hyakumeiten-older-new.md・編集距離2）
- レストラン ラッセ｜イタリアン｜東京｜2018 BRONZE → レストラン ラ・マーレ（hyakumeiten-older-new.md・編集距離2）
- レストラン リュウ｜フレンチ｜三重｜2022 BRONZE → レストラン リューズ（保存リスト・編集距離1）
- レヴォル｜フレンチ｜東京｜2019 BRONZE, 2020 BRONZE → レヴォ（award2026.md・包含）
- ヴァリノール｜フレンチ｜東京｜2018 BRONZE, 2019 BRONZE → ノル（michelin-tokyo2026.md・包含）
- 一献｜日本料理｜石川｜2018 BRONZE, 2019 BRONZE → 一献 うえ原（michelin-kyoto-osaka2026.md・包含）
- 中国菜 二位｜中華料理｜兵庫｜2021 BRONZE → 二位（保存リスト・包含）
- 中國菜 月泉｜中華料理｜大阪｜2021 BRONZE → 月泉（保存リスト・包含）
- 串揚げはやし｜とんかつ・揚げ物｜東京｜2018 BRONZE, 2019 BRONZE, 2020 BRONZE, 2021 BRONZE → はやし（hyakumeiten-older-new.md・包含）
- 京懐石 八泉｜日本料理｜愛知｜2018 BRONZE, 2019 BRONZE, 2020 SILVER, 2021 BRONZE, 2022 BRONZE, 2023 BRONZE → 懐石 八泉（award2026.md・包含）
- 割烹 互閃｜日本料理｜東京｜2019 BRONZE → 割烹 三友（hyakumeiten-2026-new.md・編集距離2）
- 割烹 樋山｜日本料理｜埼玉｜2021 BRONZE → 樋山（award2026.md・接頭辞/接尾辞除去一致）
- 割烹 牧野｜日本料理｜東京｜2018 BRONZE → 牧野（hyakumeiten-2026-new.md・接頭辞/接尾辞除去一致）
- 割烹 美加登家｜日本料理｜島根｜2018 SILVER, 2019 SILVER, 2020 BRONZE, 2021 SILVER, 2022 SILVER → 美加登家（award2026.md・接頭辞/接尾辞除去一致）
- 北新地 弧柳｜日本料理｜大阪｜2018 BRONZE, 2019 BRONZE → 弧柳（保存リスト・包含）
- 千翠｜日本料理｜福岡｜2020 BRONZE, 2021 BRONZE → 千亀（hyakumeiten-older-new.md・編集距離1）
- 千陽 本店｜日本料理｜青森｜2023 BRONZE → 千とせ 本店（hyakumeiten-older-new.md・編集距離2）
- 和 dining 清乃｜ラーメン｜和歌山｜2018 BRONZE, 2019 BRONZE, 2020 BRONZE → 和 dining 清乃 本店（hyakumeiten-older-new.md・包含）
- 寺沢｜日本料理｜岩手｜2019 BRONZE → 御料理 寺沢（award2026.md・包含）
- 寿司一｜寿司｜青森｜2018 BRONZE, 2019 BRONZE, 2020 BRONZE → 寿司 健（保存リスト・編集距離1）
- 岩さき｜日本料理｜京都｜2018 BRONZE, 2019 BRONZE, 2020 BRONZE, 2021 BRONZE → 御所 岩さき（michelin-kyoto-osaka2026.md・包含）
- 川蝉｜うなぎ｜栃木｜2018 BRONZE, 2019 BRONZE, 2020 BRONZE → 川口（destination-oad.md・編集距離1）
- 幸魚｜日本料理｜宮崎｜2023 BRONZE → 幸楽（hyakumeiten-older-new.md・編集距離1）
- 広尾 一会｜日本料理｜東京｜2018 BRONZE → 広尾 石阪（michelin-tokyo2026.md・編集距離2）
- 弘寿司｜寿司｜宮城｜2019 BRONZE, 2020 BRONZE → 弘前市（gaultmillau.md・編集距離2）
- 御料理 宮坂｜日本料理｜東京｜2018 SILVER, 2019 SILVER, 2020 SILVER, 2021 SILVER → 宮坂（award2026.md・包含）
- 懐石 大原｜日本料理｜東京｜2018 BRONZE → 懐石 八泉（award2026.md・編集距離2）
- 懐石 辻留｜日本料理｜東京｜2018 BRONZE, 2019 BRONZE, 2020 BRONZE → 懐石 八泉（award2026.md・編集距離2）
- 成蔵｜とんかつ・揚げ物｜東京｜2018 SILVER, 2019 SILVER → 成希（gaultmillau.md・編集距離1）
- 日本料理 とくを｜日本料理｜京都｜2018 BRONZE, 2019 BRONZE, 2020 BRONZE, 2021 BRONZE → とくを（michelin-kyoto-osaka2026.md・接頭辞/接尾辞除去一致）
- 日本料理 楽心｜日本料理｜大阪｜2022 BRONZE → 楽心（michelin-kyoto-osaka2026.md・接頭辞/接尾辞除去一致）
- 朗 長谷川稔Lab｜フレンチ｜東京｜2022 BRONZE → 長谷川 稔（保存リスト・包含）
- 東家｜日本料理｜東京｜2018 BRONZE, 2019 BRONZE → 東亭（hyakumeiten-older-new.md・編集距離1）
- 松弥｜日本料理｜大阪｜2020 BRONZE, 2021 BRONZE → 小松 弥助（award2026.md・包含）
- 柘榴 奈良きみや 別邸｜焼肉・肉料理｜大阪｜2022 BRONZE → きみや（hyakumeiten-2026-new.md・包含）
- 浪速割烹 喜川｜日本料理｜大阪｜2018 BRONZE, 2019 BRONZE → 浪速割烹 昇（michelin-kyoto-osaka2026.md・編集距離2）
- 淡 如雲｜日本料理｜愛知｜2021 BRONZE → 淡流（award2026.md・編集距離2）
- 焼き鳥 丈参｜焼き鳥・鳥料理｜東京｜2018 BRONZE → 焼き鳥 こと（award2026.md・編集距離2）
- 焼肉 銀座 コバウ｜焼肉・すき焼き・しゃぶしゃぶ｜東京｜2018 BRONZE, 2019 BRONZE, 2020 BRONZE → 焼肉 銀座コバウ 特別室（保存リスト・包含）
- 焼鳥 かさ原｜焼き鳥・鳥料理｜兵庫｜2019 BRONZE, 2020 BRONZE, 2021 SILVER, 2022 BRONZE → かさ原（award2026.md・接頭辞/接尾辞除去一致）
- 瓢亭 本店｜日本料理｜京都｜2018 SILVER, 2019 SILVER, 2020 BRONZE, 2021 BRONZE, 2022 BRONZE, 2023 BRONZE, 2024 BRONZE → 瓢亭（michelin-kyoto-osaka2026.md・接頭辞/接尾辞除去一致）
- 田ざわ｜天ぷら｜北海道｜2018 SILVER, 2019 BRONZE, 2021 BRONZE, 2022 BRONZE → 田久鮓（hyakumeiten-older-new.md・編集距離2）
- 田中旅館｜魚介料理・海鮮料理｜山口｜2021 BRONZE, 2022 BRONZE, 2023 BRONZE → 田中圭英（award2026.md・編集距離2）
- 石葉｜その他｜神奈川｜2020 BRONZE → 石の華（hyakumeiten-older-new.md・編集距離2）
- 祇園 呂色｜フレンチ｜京都｜2020 BRONZE, 2021 BRONZE, 2022 BRONZE → 祇園 きだ（michelin-kyoto-osaka2026.md・編集距離2）
- 粋・丸新｜日本料理｜福島｜2022 BRONZE → 丸新（award2026.md・包含）
- 臼杵ふぐ 山田屋 西麻布｜魚介料理・海鮮料理｜東京｜2018 BRONZE, 2019 BRONZE, 2020 BRONZE, 2021 BRONZE → 山田屋（award2026.md・包含）
- 蒼穹｜日本料理｜東京｜2019 BRONZE → 蒼（保存リスト・編集距離1）
- 西麻布 K+｜イタリアン｜東京｜2019 BRONZE → 西麻布 拓（michelin-tokyo2026.md・編集距離1）
- 赤坂 互閃｜日本料理｜東京｜2020 BRONZE → 赤坂味一（保存リスト・編集距離2）
- 重よし｜日本料理｜東京｜2020 BRONZE → 重亭（hyakumeiten-older-new.md・編集距離2）
- 鈴木｜うなぎ｜東京｜2018 BRONZE, 2019 BRONZE, 2020 BRONZE → 鮨 鈴木（保存リスト・包含）
- 銀座 奥田｜日本料理｜東京｜2018 BRONZE, 2019 BRONZE → 奥田（destination-oad.md・包含）
- 銀座 美会｜創作料理｜東京｜2022 BRONZE → 美会（保存リスト・包含）
- 雪月花 銀座｜焼肉・肉料理｜東京｜2025 BRONZE → 雪月花 彦根（hyakumeiten-2026-new.md・編集距離2）
- 雪村庵｜フレンチ｜茨城｜2024 BRONZE, 2025 BRONZE → 雪ぐに（hyakumeiten-older-new.md・編集距離2）
- 霞庭まつばら｜日本料理｜東京｜2018 BRONZE, 2019 BRONZE, 2020 BRONZE → まつばら（hyakumeiten-older-new.md・包含）
- 韓国料理 田無羅｜焼肉・すき焼き・しゃぶしゃぶ｜福岡｜2021 BRONZE → 田無羅（hyakumeiten-2026-new.md・包含）
- 馳走 とし藤｜日本料理｜滋賀｜2018 BRONZE, 2019 BRONZE, 2020 BRONZE → とし（destination-oad.md・包含）
- 馳走なかむら｜日本料理｜福岡｜2023 BRONZE, 2025 BRONZE → なかむら（award2026.md・包含）
- 高松｜日本料理｜京都｜2018 BRONZE, 2019 BRONZE, 2020 BRONZE, 2021 BRONZE → 高松市（gaultmillau.md・包含）
- 鮨 とかみ｜寿司｜東京｜2018 BRONZE, 2019 BRONZE, 2020 BRONZE, 2021 BRONZE, 2022 BRONZE, 2023 BRONZE → 鮨 さかい（award2026.md・編集距離2）
- 鮨 なかむら｜寿司｜東京｜2018 BRONZE, 2019 BRONZE, 2020 BRONZE → なかむら（award2026.md・接頭辞/接尾辞除去一致）
- 鮨 なんば 阿佐ヶ谷｜寿司｜東京｜2019 SILVER, 2020 BRONZE → 鮨 なんば（gaultmillau.md・包含）
- 鮨 安吉｜寿司｜福岡｜2018 BRONZE, 2019 BRONZE, 2020 BRONZE, 2021 BRONZE → 鮨 あお（award2026.md・編集距離2）
- 鮨 登喜和｜寿司｜新潟｜2022 BRONZE, 2023 BRONZE, 2024 BRONZE → 鮨 一喜（michelin-tokyo2026.md・編集距離2）
- 鮨し人｜寿司｜富山｜2022 BRONZE, 2023 BRONZE → 鮨 あお（award2026.md・編集距離2）
- 鮨人｜寿司｜富山｜2018 BRONZE, 2019 BRONZE, 2020 BRONZE, 2021 BRONZE → 鮨 功（hyakumeiten-older-new.md・編集距離1）
- 鳥かど｜焼き鳥・鳥料理｜東京｜2018 BRONZE → 鳥かご（hyakumeiten-older-new.md・編集距離1）
- 鳥田中｜焼き鳥・鳥料理｜東京｜2019 BRONZE, 2020 BRONZE, 2021 BRONZE, 2022 BRONZE, 2023 BRONZE → 鳥おか（hyakumeiten-older-new.md・編集距離2）
- 鶯谷園｜焼肉・すき焼き・しゃぶしゃぶ｜東京｜2018 BRONZE → 焼肉 鶯谷園（hyakumeiten-2026-new.md・包含）

## 取得できなかったもの

- 2017年 SILVER（89店）・BRONZE（395店）の全店リスト：公式アーカイブに一覧ページが無く（2017年版は単一ページのカルーセル形式）、PR・報道にも全店リストの掲載が無いため取得不可。GOLD 28店のみ照合済み
- 上記以外の2018〜2025年 SILVER／BRONZE は全ページ取得完了
