# 03 競合調査：日本の認知症予防・早期発見・家族介護者向け情報商品／サービス

調査日: 2026-10-09。対象期間は2023〜2026年の状況を優先。各項目は「Takeaway／Cited Findings／Inferences／Gaps」の順。URLは取得できたもののみ記載し、取得できなかった数値はGapsに回した。

---

## KQ1. note.com：認知症・介護関連コンテンツの実態（クリエイター層、有料化、価格、売れ行き）

### Takeaway
noteには「#介護」27万件超、「#認知症」11万件超の投稿があるが、人気フィードの大半は家族介護者の日記・エッセイで、医師による有料記事や認知症特化のメンバーシップは表面上ほぼ見当たらない。確認できた有料記事は300〜500円の単発記事（ケアマネ、一般ライター）で、購入数・スキ数などの販売実績データは取得できなかった（note API が403で遮断）。

### Cited Findings
- ハッシュタグ「#認知症」の投稿数は110,432件。人気フィード上位は「日記 2026.10.9 認知症、揺らぎの中」（てんす）、「親が認知症になった その11」（怪力熊男）、「【介護】認知症が進んでいる」など家族介護者の体験記が中心。人気表示中で有料だったのは1件のみ：ケアマネTAKU「認知症初期の記憶を、PLAUD NOTEで補えるか。ケアマネが考える3つの使い方と家族の手伝い方」¥500 — [note #認知症](https://note.com/hashtag/認知症)
- ハッシュタグ「#介護」の投稿数は273,620件。表示された約30件に有料表示・メンバーシップ案内はなし。発信者属性は「死生学を学ぶ主任ケアマネジャー」「社畜ケアマネ」「リハ人｜悩み続ける理学療法士」などの専門職と、「Maru｜88歳認知症の祖母とのゆっくりな暮らし」「お台場｜介護中年漂流記」「母と私、大丈夫かな？」などの家族介護者が混在。医師と明記された著者はなし。週刊形式の「週刊妖介護ラジオ 2026年10月5日号」という連載もある — [note #介護](https://note.com/hashtag/介護)
- ハッシュタグ「#認知症予防」は12,464件。表示20件中、有料は松井博「認知症予防に有効な意外な〇〇」¥300の1件のみ。著者は整体院、研修講師、薬剤師系（青島周一）、「とらぽん｜脳の健康窓口」など多様で、医師と明記された著者はなし — [note #認知症予防](https://note.com/hashtag/認知症予防)
- 認知症ケアを連載化している専門系アカウント例：「セオドア アカデミー」の『「家族も支援の対象者」という現実：認知症介護で31%が"ほぼ終日"介護に費やす家族の実態と5つの実践的支援策：認知症ケアシリーズ第6回』 — [note](https://note.com/seodoa_academy/n/nf6d2fa99fe11)；「みさき所長/信州ケアデザインLAB」の『第7章 認知症の親とどう向き合う？～家族が知っておきたい7つの接し方～』 — [note](https://note.com/asamacare_202602/n/na059a13d78be)；「認知症との向き合い方」アカウントの若年性認知症記事 — [note](https://note.com/hot_ferret8010/n/n00d3229403cc)
- 家族介護者の連載マガジン例：「認知症の母親の介護日記シリーズ」（kenjisugimoto_19） — [note](https://note.com/kenjisugimoto_19/m/m06dde6e5e1d4/hashtag/227503)
- 出版社・メディアが書籍の販促チャネルとしてnoteを使っている：かんき出版『認知症は決断が10割』紹介 — [note](https://note.com/kankipublishing/n/naed80373a723)；中央法規「けあサポ」の認知症関連書6点 — [note](https://note.com/caresapo_sapo/n/n58123b37d047)；新興医学出版社『認知症になりたくないけれど』（新見正則） — [note](https://note.com/shinkohigaku/n/nfed17bdb09ee)；家電批評編集部「認知症介護ガジェット」 — [note](https://note.com/kadenhihyo/n/nd1cea35cc7c6)
- 介護・医療系でメンバーシップを運営する例として「タクヤ先生のnote読み放題メンバーシップ」（中医学／漢方薬剤師。認知症特化ではない） — [note](https://note.com/takuyasensei/membership)；ケアマネ向けの有料解説記事例「CareFran（ケアフラン）」のケアプラン有料化解説 — [note](https://note.com/carefran/n/n5edd9c2e5ed5)

### Inferences
- noteにおける認知症領域は「家族の当事者語り（無料）」が圧倒的で、エビデンスに基づく体系的な家族向けガイドを有料提供している医師・専門職はほとんど見えない。有料化の主戦場はケアマネ・介護事業者向けの制度解説（B2B寄り）に偏っている。
- 単発の有料記事価格帯は300〜500円が中心と推測され、家族向けに「月額」で継続課金する設計は未開拓に近い。
- 出版社がnoteを販促に使っていることから、noteの読者層と書籍購買層（50〜60代の子世代）は重なっていると考えられる。

### Gaps
- noteの検索API（/api/v3/searches）はHTTP 403で取得できず、スキ数・購入者数・人気順ランキングは確認不能。
- 認知症特化の有料マガジン／メンバーシップの存在有無、価格、会員数は検索経由では特定できなかった（存在しないのではなく、発見できていない可能性あり）。
- 「健康／介護カテゴリの有料noteで何が売れるか」の定量データは公開されていない。

---

## KQ2. アプリ／デジタルサービス：認知症予防・脳トレ、早期発見、家族支援

### Takeaway
国内の予防・早期発見デジタルは「自治体・企業・健診経由のB2B2C」が主流で、個人課金で大きく成長している例は確認できなかった。利用者規模が公表されている最大級は「脳にいいアプリ」（25自治体超・20万人超）と、NTT Comの電話チェック（初週30万件）。血液検査は2万円台の自費、声・ゲーム型のセルフチェックは価格非公開（見積）で、家族介護者向けの相談・コミュニティは法人向け（介護離職防止）に収益化が寄っている。

### Cited Findings
**認知症予防・脳トレアプリ**
- 「脳にいいアプリ」（株式会社ベスプラ）：PR TIMESリリースで「全国25以上の自治体・20万人以上のユーザーに採用」 — [PR TIMES](https://prtimes.jp/main/html/rd/p/000000163.000007987.html)；埼玉県向け資料では「ユーザー15万人。継続率は80%以上！」 — [埼玉県資料](https://www.pref.saitama.lg.jp/documents/275741/2.pdf)；DXマガジンは「全国で20以上の自治体に導入」と報道 — [DXマガジン](https://dxmagazine.jp/news/2506ti19/)；八王子市の健康ポイント「てくポ」では60歳以上人口の約12人に1人にあたる16,000人超が日常利用、継続率約80% — [東京都UPGRADE資料](https://upgrade-tokyo.metro.tokyo.lg.jp/assets/pdf/winning14.pdf)；栃木県那珂川町が2025年1月から提供開始、65歳以上向けサポート講座全4回 — [xexeq](https://xexeq.jp/blogs/media/topics37060)
- 「脳トレ 紡」（KYOCERA Mirai Envision）：無料DL＋アプリ内課金、サブスク月額700円／年額7,000円、初回3週間は全機能無料 — [App Store](https://apps.apple.com/jp/app/%E3%81%97%E3%82%89%E3%81%9B%E3%81%82%E3%81%84-%E8%84%B3%E3%83%88%E3%83%AC-%E7%B4%A1/id1637034364)
- 「脳体力トレーナーCogEvo／脳活バランサー」（トータルブレインケア）：見当識・注意力・記憶力・計画力・空間認識力の5側面をチェック・訓練するクラウドサービス、25本超の論文・学会発表、神奈川県ME-BYO BRAND認定、日本旅行と資本業務提携し社員4,000人対象に試験導入 — [トラベルボイス](https://www.travelvoice.jp/20231013-154395)、[近畿経産局スタートアップ資料](https://www.kansai.meti.go.jp/3-3shinki/Startup/asset2025/files/startup-kansai-report/47tbcare.pdf)
- Lumosity／BrainHQの日本円価格：比較サイト（jisaku.com）に「Lumosity 1,480円〜、BrainHQ 2,000円〜」とあるが出典不明 — [jisaku.com](https://jisaku.com/posts/dementia-prevention-cognitive-pc)。BrainHQ公式は月額・年額の2プラン制とだけ記載 — [BrainHQ Support](https://support.brainhq.com/hc/en-us/articles/115002103266-Choosing-a-personal-subscription-plan)
- App Storeの「認知症予防」系個人アプリはレビュー数が少数（例：「認知症対策:記憶力の向上に特化した脳トレ」評価41件・平均3.6） — [App Store](https://apps.apple.com/jp/app/id6444015375)、[app-liv おすすめ6選](https://app-liv.jp/health/selfcares/3551/)

**早期発見・セルフチェック**
- エーザイ「のうKNOW」：Cogstate Brief Batteryを基にした4つのカードゲーム（記憶・注意・反応速度・視覚学習）、所要約15分、18〜99歳、非医療機器。価格は非公開（利用規模・頻度により見積、問合せから約5営業日）。導入先に東京海上日動、鹿島建設、複数自治体。2024年3月以降の更新情報はサイト上にない — [nouknow.jp](https://nouknow.jp/)
- エーザイ×ローソン×ウェルネスダイニングが愛媛県今治市のローソン店舗で「のうKNOW短縮版」を含む啓発・セルフチェックを2026年6月11日から順次開始 — [ベストカレンダー](https://bestcalendar.jp/press/134251)
- エーザイ×DeSCヘルスケア「Easiit」：2020年7月iOS配信開始、無料、「のうKNOW」とのデータ連携を予定 — [Impress Watch](https://www.watch.impress.co.jp/docs/news/1267863.html)；当時「5年で500万人の利用を目指す」 — [日刊薬業](https://nk.jiho.jp/article/153591)
- MCBI「MCIスクリーニング検査プラス」（島津製作所出資、筑波大発）：採血のみ、ApoA1・TTR・C3等の血中タンパク質でMCIリスク判定、結果まで3〜4週間、保険適用外。価格例：宇野病院 20,000円（税別） — [宇野病院](https://www.uno.or.jp/images/uno_images/kenshin/MCI.pdf)；放射線クリニック扇町 22,000円（税込・40歳以上） — [中山会](https://www.nakayamakai.com/kenshin/top/202402_mci.pdf)；MCIスクリーニング検査付き人間ドック 70,400円（新宿NSビルクリニック） — [MRSO](https://www.mrso.jp/mrs/SNSBC/Plans/detail/57646)。MCBIは2015年から延べ12万人以上に提供 — [薬事日報](https://www.yakuji.co.jp/?p=117818)
- 自費の「血液で悪玉アミロイドチェック」25,300円（税込）、PET/CTによる脳アミロイド蓄積度チェック275,000円（税込）という健診オプション例 — [TKGH R7オプション検査](https://www.tkgh.jp/cms/wp-content/uploads/2025/07/R7_オプション検査_認知症.pdf)；島津「アミロイドMS CL」は大分大学臼杵コホートでのPhase I段階（研究用途） — [大分大学資料](https://www.oita-u.ac.jp/000057246.pdf)
- 日本テクトシステムズ「ONSEI」：声で認知機能を判別。無料「ONSEI」（20秒）、健康記録・脳トレ付き「ONSEIプラス」、健診向け「ONSEI Pro」（約5分、タブレット音声回答） — [PR TIMES ONSEI Pro](https://prtimes.jp/main/html/rd/p/000000024.000045502.html)；グランドハイメディック倶楽部「ハイメディック横浜ベイコース」（2026年開設）に導入 — [PR TIMES](https://prtimes.jp/main/html/rd/p/000000028.000045502.html)；自治体向け資料で軽度AD判別率85%（論文）→93%（学会発表） — [防府市資料](https://www.city.hofu.yamaguchi.jp/uploaded/attachment/135019.pdf)；NTTコミュニケーションズと2022年に電話＋音声解析AIの認知機能チェックで連携 — [NTT Com](https://www.ntt.com/about-us/press-releases/news/article/2022/0302.html)
- NTT Com「脳の健康チェックフリーダイヤル」：2022年9月開始、日付と年齢を答えるだけで1分以内に結果、初週約30万件の着電。2023年9月21日に有償トライアル「脳の健康チェックplus」を発表（価格は非公開） — [Business Network](https://businessnetwork.jp/article/16475)
- NTTドコモは2023年にスマホ利用傾向から脳の健康状態をAIでチェックする「脳の健康チェックAI」を試作公開 — [ドコモR&D資料](https://www.docomo.ne.jp/binary/pdf/corporate/technology/rd/topics/2022/topics_230126_00.pdf)
- ミレニア「あたまの健康チェック®」：1対1の対話式・約10分、独自MPIスコア、「認知症か否かの評価を行うものではない」と明記。東京都港区の「あたまの元気度チェック」事業を令和8年度も継続受託 — [DIME（PR）](https://dime.jp/company_news/detail/?pr=2700528)；石川県白山市では無料・先着400名で提供 — [白山市チラシ](https://www.city.hakusan.lg.jp/_res/projects/default_project/_page_/001/008/337/r8_tirasi1.pdf)
- 神戸市「神戸モデル」（認知機能検診＋精密検査、自己負担ゼロ）：第1段階受診者 累計79,067人（令和6年6月末）、前年同期59,554人。第2段階実施医療機関61か所、うち9か所で2024年4月から新薬適応可否診断 — [神戸市 実施状況](https://www.city.kobe.lg.jp/documents/15725/03_kobemodelzissizyokyo.pdf)

**家族介護者向け支援・コミュニティ**
- 公益社団法人 認知症の人と家族の会：会員約9,000名（令和7年3月現在） — [青森県支部資料](https://www.pref.aomori.lg.jp/soshiki/kenko/koreihoken/files/ninchisyo_kazokunokai.pdf)；2024年版リーフレットでは9,400名 — [山梨県WAD2024](https://www.pref.yamanashi.jp/documents/101929/wad2024_leaflet.pdf)。専門職向けオンラインセミナーは有料（Zoom、返金不可）、家族支援講座は無料実績 — [家族の会](https://alzheimer.or.jp/wp-content/uploads/2024/12/20250320-1.pdf)
- 東京都は2025年9月1日から認知症介護経験者（ピア相談員）による電話相談窓口を開設 — [東京都報道発表](https://www.metro.tokyo.lg.jp/information/press/2025/08/2025082911)
- 「みんなの介護コミュニティ」アプリ（2022年リリース）：匿名相談、主対象は介護職だが家族介護者も対象 — [リセマム（PR TIMES）](https://resemom.jp/release/prtimes/20220301/79460.html)
- エクサウィザーズ「CareWiz」：2020年6月に無償提供開始、ユマニチュード動画・認定インストラクター電話相談・認知症関連サービス検索 — [エクサウィザーズ](https://exawizards.com/archives/10606)（2024年以降の提供状況は未確認）
- 法人向け「介護コンシェルジュ」（一社・日本顧問介護士協会「顧問介護士サービス」）：LINE・Zoom中心に365日・全国対応の相談窓口＋介護セミナー。静岡県中小企業団体中央会会員向け特別料金：従業員1〜10名 5,500円/月、11〜30名 7,700円/月、31〜100名 9,900円/月、101名以上 1名あたり110円/月、初月システム登録費11,000円（いずれも税込） — [静岡県中小企業団体中央会チラシ](https://www.siz-sba.or.jp/cms/files/siz-sba/MASTER/0010/BBidwsNO.pdf)
- インターネットインフィニティー「わかるかいごBiz」：企業向けに介護コンシェルジュ相談窓口・介護セミナー・情報サイトを提供 — [週刊アスキー](https://weekly.ascii.jp/elem/000/004/016/4016772/)
- LIFULL介護：月間300万UU（2023年1月時点）、掲載施設38,000件以上 — [Green 企業情報](https://www.green-japan.com/company/4418)
- 自治体LINE：鳥取県「脳とからだの健康LINE」友だち登録1,822人（2026年3月27日時点） — [鳥取県](https://www.pref.tottori.lg.jp/item/1422788.htm)
- 厚労省「介護事業所ナビ」アプリは令和6年3月末でサービス終了（ブラウザ版へ移行） — [介護サービス情報公表システム](https://www.kaigokensaku.mhlw.go.jp/sp_application)

### Inferences
- 国内の早期発見ツールはほぼ全て「非医療機器・診断ではない」と注記しており、結果を受け取った家族が「次に何をするか」を補う情報の空白が構造的に存在する。
- 価格が公開されているのは血液検査（2万円台）と一部脳トレアプリ（月700円）程度で、B2C価格の相場が形成されていない。
- 家族介護者向けの有料サービスは「企業福利厚生（介護離職防止）」経由で月数千円〜1人110円という単価で売られており、個人向け直販はほぼ無料（自治体・NPO）で占められている。

### Gaps
- Easiitの現在の提供状況（終了か継続か）と累計利用者数は確認できなかった。
- のうKNOW・CogEvo・あたまの健康チェックの個人向け価格、導入自治体数、累計受検者数は非公開。
- 「みまもりAI」「ブレインパフォーマンス」単体、Yahoo!介護、介護のほんねの2023年以降の状況は未確認（介護のほんねは2015年情報のみ）。
- App Store／Google Playの認知症・脳トレカテゴリのダウンロードランキングは有料ツール（Sensor Tower等）が必要で未取得。
- 家族向けLINE／チャットAI相談サービスの2025〜26年開始事例は見つからなかった。

---

## KQ3. 大手プレイヤー（製薬・保険・通信・教育・広告・自治体）

### Takeaway
大手は「保険の付帯サービス」「自治体への多因子介入プログラム提供」「啓発イベント」が中心で、家族向けの継続課金型情報サービスは見当たらない。SOMPOが研究（J-MINT PRIME Tamba）→サービス（コグー／Co-Good、2026年4月開始・6自治体）まで一気通貫で最も踏み込んでいる。

### Cited Findings
- SOMPO笑顔倶楽部：知る（認知症記事・コラム）、チェックする（あたまの元気度チェック、家族の会「早期発見のめやす」）、予防する（コグニサイズ、介護予防4種）、ケア（介護のプロに相談、医療機関検索、ケアパス、施設費用シミュレーター、成年後見）を提供。一部は会員限定（ログイン要）、会費・会員数の記載なし — [SOMPO笑顔倶楽部](https://www.sompo-egaoclub.com/)
- SOMPOウェルビーイング「コグー（Co-Good）」：2026年4月1日提供開始、現在6自治体で利用。神戸大学との「J-MINT PRIME Tamba」追跡で、介入群は18か月時点で対照群より認知スコア改善が41%大きく、介入開始後12か月の実医療費がKDBデータに基づく予測値より47%低かった（対照群実績との比較ではなく予測対実績、リリース自体も「示唆」と表現）。2026年7月10日AAIC/WW-FINGERSで発表 — [PR TIMES](https://prtimes.jp/main/html/rd/p/000000010.000175480.html)
- J-MINT本研究（MCIのある65〜85歳、531名、18か月継続率76.5%）は主要評価項目の認知複合スコアで介入群と対照群に有意差なし — [神経治療学（櫻井孝）](https://www.jstage.jst.go.jp/article/jsnt/42/4/42_489/_article/-char/ja)；丹波市の延長研究（J-MINT PRIME Tamba）は主要評価項目が改善 — [Alzheimer's & Dementia 2024](https://pmc.ncbi.nlm.nih.gov/articles/PMC11485327/)
- 2019年の厚労省向け資料でSOMPOは「MCIで保険金を支払うことで早期発見に貢献し、保険金を予防に使ってもらう」構想を提示 — [厚労省資料](https://www.mhlw.go.jp/content/12301000/000493244.pdf)
- 太陽生命：2019年7月時点で認知症保険の累計販売件数50万件突破 — [ニュースイッチ](https://newswitch.jp/p/18500)；「ひまわり認知症治療保険」は発売から1年4か月で契約23万件超 — [東洋経済](https://toyokeizai.net/articles/-/193038)
- オリコン「認知症保険」FP評価ランキング2025：1位 朝日生命「あんしん介護認知症保険」、2位 ネオファースト生命「認知症保険toスマイル」、3位 SOMPOひまわり生命「笑顔をまもる認知症保険」、4位 太陽生命「ひまわり認知症予防保険」 — [オリコン](https://life.oricon.co.jp/rankfp_dementia-insurance/2025/)
- 第一生命・SOMPOホールディングスは2019年にNeurotrackの2,100万ドルSeries Cに参加。第一生命は前年から顧客向けにNeurotrackの認知機能評価ツールを展開 — [THE BRIDGE](https://thebridge.jp/2019/06/cognitive-health-assessment-startup-neurotrack-raises-21m-series-c-pickupnews)、[MedCity News](https://medcitynews.com/2019/06/cognitive-health-assessment-startup-neurotrack-raises-21m-series-c/)
- エーザイ：のうKNOW（KQ2参照）、Easiit（KQ2参照）、ローソン連携（2026年6月、今治） — [ベストカレンダー](https://bestcalendar.jp/press/134251)
- ベネッセスタイルケア：2025年9月1日から9都道府県で「認知症タウンミーティング」（専門家講演＋体験型イベント）を計約70回開催 — [産経新聞社PR](https://san-tatsu.jp/pressrelease/449063/)
- NTT Com／ドコモ：電話型「脳の健康チェック」（初週30万件、2023年に有償版トライアル） — [Business Network](https://businessnetwork.jp/article/16475)；ドコモ「脳の健康チェックAI」試作 — [ドコモ](https://www.docomo.ne.jp/binary/pdf/corporate/technology/rd/topics/2022/topics_230126_00.pdf)
- 博報堂：2013年「認知症+designラボ」、2019年1月に認知症未来共創ハブ（慶應SFC）と協働し事業開発プログラム「認知症+DESIGN」提供開始 — [AdverTimes](https://www.advertimes.com/?p=101607)
- 電通：2023年8月にオールアバウトライフワークスと「テココロ」プロジェクト（ものづくりによる社会参加、認知症予防・共生を目標）。電通調査で「シニアが今一番関心を持っているのは脳の健康」 — [電通報](https://dentsu-ho.com/articles/8752)
- 神戸市：神戸モデル（KQ2参照）。認知症条例に基づく診断助成＋事故救済制度 — [神戸市 施策実施状況](https://www.city.kobe.lg.jp/documents/15725/03_kobemodelzissizyokyo.pdf)

### Inferences
- 保険会社は「保険金＋付帯サービス（チェックツール・相談）」でリーチは大きいが、契約者限定・ログイン制のため非契約者の家族には届かない。
- 多因子介入の社会実装（コグー）は自治体がバイヤーであり、個人が直接買える形にはなっていない。
- 広告代理店の取り組みはCSR・事業開発支援の性格が強く、家族向け情報商品としては展開されていない。

### Gaps
- SOMPO笑顔倶楽部の会員数・会費、太陽生命「ひまわり認知症予防保険」の最新保有契約件数、第一生命のNeurotrack提供継続有無は確認できなかった。
- セコム、Panasonic、学研、KDDIの2025年前後の認知症予防サービス発表は検索で特定できなかった。
- 博報堂・電通の2024〜25年の新規認知症プロジェクトは見つからなかった。

---

## KQ4. 書籍・メディア（ベストセラー、YouTube、LINE、Voicy、雑誌）

### Takeaway
書籍では『認知症世界の歩き方』シリーズ（累計25〜30万部、「令和で一番売れた認知症の本」と自称）、『マンガ ぼけ日和』（15万部、2027年映画化）、和田秀樹『80歳の壁』（2022年時点53.5万部）が目立ち、「当事者の視点」「明るいトーン」「高齢期の肯定」が売れ筋の文法。YouTubeでは「岡本一馬の認知症専門チャンネル」が12.7万人規模で最大級、認知症特化のVoicyや大規模LINE公式は確認できなかった。

### Cited Findings
- 『認知症世界の歩き方』（筧裕介、ライツ社、2021年9月）：2022年時点で16万部超 — [東洋経済](https://toyokeizai.net/articles/-/635079)；2026年1月時点で「シリーズ累計20万部」 — [我孫子市資料](https://www.city.abiko.chiba.jp/shisei/kouhou/houdouteikyou/R7houdou10-03.files/20260115nintisyousekai.pdf)；2026年9月の『実践編』コンパクト版リリースで「令和で一番売れた認知症の本、シリーズ累計30万部」 — [ORICON（PR）](https://www.oricon.co.jp/pressrelease/2972811/)、同時期の販売ページは「シリーズ累計25万部突破」 — [丸善ジュンク堂](https://www.maruzenjunkudo.co.jp/products/9784991297168)（数字が不一致）
- 矢部太郎『マンガ ぼけ日和』（原作：長谷川嘉哉『ボケ日和』かんき出版）：シリーズ累計15万部突破、大竹しのぶ・三浦友和W主演で2027年実写映画化、櫻井翔が認知症専門医役 — [財経新聞（PR）](https://zaikei.co.jp/releases/3542558/)、[秋田魁（ORICON配信）](https://www.sakigake.jp/news/article/20260728OR0021/)
- 和田秀樹『80歳の壁』：2022年年間ベストセラー時点で累計発行53万5,000部 — [PRESIDENT Online](https://president.jp/articles/-/57484)；和田氏の新刊『和田式 脳メンテ — 気になるあなたの新・認知症対策習慣』（白秋社）2026年7月発売 — [紀伊國屋書店](https://www.kinokuniya.co.jp/f/dsd-101001022012010-06-)
- 奥野修司『認知症は病気ではない』（文春新書、2024年10月） — [文藝春秋](https://books.bunshun.jp/ud/book/num/9784166614738)
- 講談社の認知症「とっさのフレーズ」本（介護施設運営者著）はAmazon「老年看護」カテゴリで2025年9月〜2026年4月の8か月連続ベストセラー獲得と出版社が表示 — [講談社](https://www.kodansha.co.jp/book/products/0000418513)
- かんき出版『認知症は決断が10割』（「感動話でも美談でもない」手引きとして訴求） — [note かんき出版](https://note.com/kankipublishing/n/naed80373a723)
- 子ども向け『10歳からのみらい読本 認知症の世界』（2025年9月25日発売、認知症月間企画） — [公募ガイド（PR TIMES）](https://koubo.jp/press-release/prtimes/c88370_r40)
- 雑誌：クロワッサン特別編集『新装版 介護の「困った」が消える本。』（マガジンハウス、2022年12月、92ページ、認知症を中心に施設選び等） — [ebookjapan](https://ebookjapan.yahoo.co.jp/books/739318/A003705488/)；介護専門誌『おはよう21』増刊（中央法規）に認知症ケア入門号 — [note けあサポ](https://note.com/caresapo_sapo/n/n58123b37d047)
- 認知症の人と家族の会が「推薦図書」リスト（2024-2025年用）を公開 — [家族の会](https://alzheimer.or.jp/wp-content/uploads/2023/07/f3c8f70591817b37653ea69c9c452c9e.pdf)
- YouTube「岡本一馬の認知症専門チャンネル」：登録者約12.7万人、動画1,000本以上（2025年6月14日時点）、ミッション「認知症で苦しむ人を0にする」 — [vidIQ](https://vidiq.com/youtube-stats/channel/UCSFMDMbIaOlts4hRyKXSNMQ)
- 認知症専門医・長谷川嘉哉（医療法人ブレイングループ理事長）の「ボケ日和 転ばぬ先の知恵」チャンネルが存在（登録者数は取得不能） — [ユーチュラ](https://yutura.net/channel/58360/video/V61G6jo4tS0/)
- 医師系チャンネル例：大場内科クリニック（帯状疱疹ワクチンと認知症予防など） — [ユーチュラ](https://yutura.net/channel/91928/video/_Bgd0kiC4z0/)；自治体系：名古屋市認知症相談支援センター — [名古屋市](https://www.city.nagoya.jp/shisei/kouhou/1010579/1035005/1035007/1010816.html)；板橋区「チャンネルいたばし」在宅医・伊藤直氏の67分講演 — [板橋区](https://www.city.itabashi.tokyo.jp/kusei/kouhou/tenji/tv/1027730/1027707/1039757.html)
- 鳥取県「脳とからだの健康LINE」友だち1,822人（2026年3月） — [鳥取県](https://www.pref.tottori.lg.jp/item/1422788.htm)；鹿児島市・江戸川区は市LINEで認知症・行方不明情報を配信 — [鹿児島市](https://www.city.kagoshima.lg.jp/kenkofukushi/chouju/tiikihoukatu/kenko/fukushi/choju/ninchi/nintisyookaerisupport.html)

### Inferences
- 売れている認知症本は「本人の内側から世界を見せる」「ユーモア」「決断・実践の手引き」のいずれかで、医学的網羅解説よりも家族の感情に寄り添う設計が商業的に強い。
- YouTubeは介護職・施設経営者系の発信者が医師より登録者を集めており、専門性より「毎日の対応ノウハウ」が需要の中心と推測される。
- LINE公式は自治体単位で数千人規模にとどまり、全国規模の認知症特化アカウントは空白。

### Gaps
- 2025年の日販・トーハン・Amazon年間ランキングにおける認知症本の順位は取得できなかった。
- 長谷川嘉哉氏ほか医師系YouTubeの登録者数、認知症特化Voicyチャンネルの有無、介護ポストセブン等メディアの認知症PVは未確認。
- 『ボケ日和』原作エッセイ単体の部数は不明（15万部はマンガ版）。

---

## KQ5. 公的・無料情報：何が既にあり、なぜ「情報が足りない」と感じられるか

### Takeaway
認知症サポーターは1,635万人（2025年6月末）、認知症カフェは約7,900か所、ケアパスは全市町村作成がKPIという厚い無料インフラがあるにもかかわらず、内閣府2025年調査で認知症基本法の成立を75%が知らず、未経験者の7割超が認知症カフェ・家族会を知らない。家族の最大の悩みは「先の見通しが立たない」（44.7%）で、「どこに相談すればよいか分からない」が初期段階のボトルネック。無料情報は「制度・窓口の羅列」で、個人の状況に合わせた意思決定支援になっていない。

### Cited Findings
- 認知症サポーター数：全国16,352,626人（2025年6月末） — [厚労省四国厚生支局資料](https://kouseikyoku.mhlw.go.jp/shikoku/chiiki_houkatsu/000247192.pdf)；約1,621万人（令和7年3月末） — [滋賀県](https://www.pref.shiga.lg.jp/ed00/4578.html)。共生社会の実現を推進するための認知症基本法は令和6年1月施行
- 認知症カフェ：令和3年度実績調査で47都道府県1,543市町村（88.6%）に7,904か所、設置主体は介護事業者と地域包括支援センターが多く、月1〜2回・2時間程度の開催が多い — [厚労省](https://www.mhlw.go.jp/content/12300000/001227277.pdf)
- 厚労省資料に市町村の「認知症ケアパス」作成率100%のKPI — [厚労省](https://www.mhlw.go.jp/content/11601000/000527246.pdf)；2025年3月に「都道府県・市町村向け 認知症施策推進計画策定の手引き」公表 — [厚労省](https://www.mhlw.go.jp/content/001476653.pdf)
- 内閣府「認知症に関する世論調査」（速報、2025年10月10日公表、18歳以上3,000人、回収率51.7%）：認知症基本法が「成立したことを知らない」75% — [WIC-NET掲載資料](https://www.wic-net.com/material/static/00022081/00022081.pdf)、[日刊薬業](https://nk.jiho.jp/article/202452)
- LIFULL介護調査（2025年8月、認知症介護未経験の20〜60代882人）：本人ミーティング・認知症カフェ・認知症家族会はいずれも70%超が「知らない」、列挙した全支援制度で過半数が「知らない」。親が認知症になった場合の不安1位は治療・介護費用34.9%、次いで親とのコミュニケーション29.5%、介護者の心身負担29.4%。約7割が親と認知症になった場合の話をしたことがない（話した人26.8%） — [LIFULL介護 tayorini](https://kaigo.homes.co.jp/tayorini/survey/2025-9/)
- ニッセイ基礎研究所「認知症介護家族の不安と負担感に関する調査」：困りごと1位「先の見通しが立たない」44.7%、2位「本人が望む方法がわからない」25.7%、3位「サービスを受けることを嫌がる」19.9%、4位「働き方を変えざるを得ない」18.4%、5位「介護費用の負担が大きい」17.5% — [ニッセイ基礎研](https://www.nli-research.co.jp/files/topics/63967_ext_18_0.pdf)
- 宇都宮市調査：認知症の人の変化に最初に気づくのは約8割が家族、介護者の約半数が「ストレスや精神的・肉体的な負担が大きい」 — [宇都宮市](https://www.city.utsunomiya.lg.jp/_res/projects/default_project/_page_/001/010/533/02ninntikoureisyasiryou1-1_220324.pdf)
- 岡山市調査：地域包括支援センター相談前・介護保険利用前の「初期段階」の本人・家族ニーズは把握が難しく、若年性認知症家族からは「どこに相談したらよいかわからず、窓口でも適切な相談につながらない」との声 — [岡山市](https://www.city.okayama.jp/kyoudou/cmsfiles/contents/0000042/42181/harusora_cyousa.pdf)
- 北翔大学研究：認知症初期に家族が直面する困難として「受診につなげる難しさ」、長期化すると「介護者の孤立」「世間体」 — [北翔大学リポジトリ](https://hokusho.repo.nii.ac.jp/record/3238/files/14_p109-113.pdf)
- 伊藤園調査（2020年11月）：認知症対策について「この先やりたいと思っているが、何をしてよいかわからない」52.0% — [伊藤園](https://www.itoen.co.jp/files/user/news/2020/201118matcha%20PJ03.pdf)
- 明治安田生命×島根県調査（2022年度）：認知症になった場合の不安は「家族に負担をかける」75.4%で最多 — [島根県](https://www.pref.shimane.lg.jp/medical/fukushi/kourei/kourei_sien/ninchishou/teigi.data/R4houdou.pdf)
- 内閣府2015年調査では成年後見制度を「内容も言葉も知らない」26.7% — [時事](https://sp.m.jiji.com/english/show/2683)
- 無料講座の例：板橋区の家族向け講座（定員30名） — [板橋区](https://www.city.itabashi.tokyo.jp/kenko/ninchisho/shien/1003776.html)；世田谷区の介護者向け心のケア講座（全4回・無料） — [世田谷区](https://www.city.setagaya.lg.jp/02087/18899.html)；江東区オンライン認知症サポーター養成講座（無料） — [江東区](https://www.city.koto.lg.jp/211500/ninsapo_online.html)

### Inferences
- 無料情報の供給量は十分だが、「認知症と診断される前・相談窓口に行く前」の家族（最も不安が高い層）に届く設計になっていない。ケアパスは診断後のサービス一覧であり、「親が受診を嫌がる」「まだ大丈夫と言われる」段階の行動指針がない。
- 認知度調査では制度名の認知を測っており、「自分の状況で何をすべきか」の自己効力感は測られていない。情報不足感の正体は「量」ではなく「個別化・順序付け・意思決定支援の欠如」と考えられる。

### Gaps
- 「親が受診を拒否した経験のある家族の割合」を示す全国調査は見つからなかった。
- 内閣府2025年調査の「認知症に対する不安」の具体数値、属性別クロス集計は確報待ち。
- 地域包括支援センターの全国設置数、認知症カフェの令和5年度以降の最新数は未取得。

---

## KQ6. 海外モデル（米英NPO、米デジタル認知ヘルス、介護者ベネフィット、FINGER系）

### Takeaway
米国Alzheimer's Associationは年商4.65億ドル、年間22.3万件のヘルプライン対応と1,900万回のウェブ利用で「無料・24時間・個別相談」を実現しており、日本にこの規模の中立的家族支援ハブは存在しない。デジタル認知評価（BrainCheck、Linus、Neurotrack、Isaac Health）は医療機関・保険者向けB2Bへ収斂し、介護者支援（Wellthy、Cariloop）は雇用主ベネフィットとして資金調達している。生活習慣介入はUS POINTERで「構造化群」の効果が示されたが自己学習群との差は小さい。

### Cited Findings
- Alzheimer's Association（米）FY2024（2023年7月〜2024年6月）：総収入4.65億ドル超、研究投資1.09億ドル。24/7ヘルプラインで223,000件超の電話・メール・チャットに修士レベルの臨床家が対応、alz.orgは約1,900万回のサービス提供、ケア・サポート提供は計1,000万回超、SNSフォロワー約150万人、無料オンラインコミュニティALZConnected運営、Walk to End Alzheimer'sで1億ドル調達 — [Annual Report 2024 (PDF)](https://alz.org/getmedia/dbc8fd3f-a1a8-4cfd-8c40-acb89fd65b23/annual-report-2024.pdf)
- Alzheimer's Society（英）：2024年3月期の総収入1億3,136万ポンド（寄付・遺贈9,829万ポンド、政府契約2,271万ポンド）、2025年3月期は1億4,383万ポンド — [Charity Commission](https://register-of-charities.charitycommission.gov.uk/en/constituency-search/-/charity-details/296645/financial-history)
- US POINTER（Alzheimer's Association主導、2年間RCT、JAMA掲載）：構造化介入群（2年で38回のピアチーム会合）は年0.243SD改善、自己学習群（6回＋教材）は0.213SD改善。差0.029SDはフィンランドFINGERの効果に匹敵と研究者は主張。4年間の追跡継続 — [UC Davis Health](https://health.ucdavis.edu/news/headlines/lifestyle-changes-boost-brain-health/2025/09)
- FINGER-NL（オランダ）：1,206名、24か月、8つの生活習慣領域、オンライン＋対面のハイブリッド — [Wageningen University](https://wur.nl/en/research-results/chair-groups/agrotechnology-and-food-sciences/human-nutrition-and-health/nutritional-biology/research/nutrition-and-ageing/finger-nl.htm)；LETHE（フィンランド・オーストリア・イタリア・スウェーデン）はデジタル支援型FINGER介入の実現可能性試験、60〜77歳のデジタルリテラシーのあるリスク保有者対象 — [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11580696/)
- Isaac Health（NY、2022年設立）：2025年8月に1,050万ドルのSeries A（Flare Capital Partners主導）、累計1,630万ドル。健康保険・医療システム向けにスクリーニング〜ケアマネジメントを提供 — [Fierce Healthcare](https://www.fiercehealthcare.com/health-tech/isaac-health-secures-105m-advance-technology-brain-health-and-dementia-care)
- BrainCheck（Austin）：2024年3月に1,500万ドル調達 — [MobiHealthNews](https://www.mobihealthnews.com/news/braincheck-locks-15-million-investment-cognitive-assessment-platform)；2025年に150以上の医療機関が新規採用 — [BrainCheck](https://braincheck.com/articles/news/150-practices-join-braincheck-in-2025-as-new-cognitive-care-workflows-scale-nationwide)；2026年2月に追加1,300万ドルのSeries A（Next Coast Ventures主導、UPMC Enterprises参加） — [Business Wire](https://www.businesswire.com/news/home/20260226481557/en/BrainCheck-Raises-$13-Million-to-Expand-AI-Enabled-Cognitive-Care-Platform)
- Linus Health（Boston）：AI強化デジタル認知評価。2024年7月にTogether Senior Healthを買収（3件目の買収） — [CB Insights](https://www.cbinsights.com/company/linus-health/financials)
- Neurotrack（Redwood City）：現在は「cognitive care enablement platform」としてMCI・認知症の検出〜ケアプランをB2B提供、価格非公開（デモ要求制）、「顧客は米国高齢者の約5%をケア」と自称、サイトは2026年も稼働 — [neurotrack.com](https://www.neurotrack.com/)；2023年にNAD（全米広告審査）でPosit Scienceからの申立てを受け「clinically proven」「アルツハイマーリスク低減」等の消費者向け主張を自主的に取り下げ — [BBB National Programs](https://bbbprograms.org/media/newsroom/decisions/neurotrack)
- Cariloop（Dallas）：2024年4月に2,000万ドルSeries C（ABS Capital主導）、雇用主提供の介護コーチ・ベネフィット — [Dallas Innovates](https://dallasinnovates.com/cariloop-raises-20m-series-c-to-boost-growth-and-expand-caregiver-support-solutions/)；最低加入規模100名 — [Shortlister](https://www.myshortlister.com/workplace-senior-support-companies/vendor-list)
- Wellthy：累計調達約7,700万ドル（直近2,550万ドル）、雇用主・健康保険向けケアコンシェルジュ — [Femtech Insider](https://femtechinsider.com/wellthy-investment/)；最低加入規模1,000名 — [Shortlister](https://www.myshortlister.com/workplace-senior-support-companies/vendor-list)
- Papa（Miami、「grandkids on demand」）：Series Aで1,000万ドル調達 — [Home Health Care News](https://homehealthcarenews.com/company/wellthy/)（Papa単体の最新状況は未確認）

### Inferences
- 米国で消費者直販（DTC）の脳トレ・認知チェックは広告規制（NAD）と科学的根拠の弱さで後退し、医療・保険者向けB2Bへ転換した。日本でDTC型を狙うなら「診断・予防効果を謳わない情報・意思決定支援」に設計を寄せる必要がある。
- 日本には家族向けの大規模・中立・24時間の相談ハブ（Alz Assocのヘルプライン22万件/年規模）に相当するものがなく、家族の会（会員9,000人）と自治体窓口に分散している。
- 介護者支援は「雇用主が払う」モデルが海外でも日本（介護コンシェルジュ月5,500円〜）でも共通しており、B2B2Eは現実的な入口。

### Gaps
- Linus Healthの2025年の資金調達は情報源が錯綜（Lindus Healthとの混同）し確認できず。
- Hero、Lingraphica、Carewell、Cognito Therapeutics、Papaの2025〜26年のトラクションと価格は未調査。
- Wellthy・Cariloopの雇用主向け単価（PEPM）は非公開。
- Alzheimer's Societyの具体的なデジタルサービス（Dementia Connect等）の利用者数は取得していない。

---

## KQ7. ギャップ：何が欠けているか

### Takeaway
日本市場で欠けているのは「診断前〜初期の家族」に向けた、エビデンスの強さを明示し、恐怖を煽らず、状況別に次の一手を示す日本語の意思決定支援コンテンツ。既存プレイヤーは「予防ツール（効果は非保証）」「診断後の制度案内」「当事者の体験記」に分かれ、その間を埋める商品がほぼ存在しない。

### Cited Findings
- 家族の最大の困りごとは「先の見通しが立たない」44.7%、「本人が望む方法がわからない」25.7%、「サービスを受けることを嫌がる」19.9% — [ニッセイ基礎研](https://www.nli-research.co.jp/files/topics/63967_ext_18_0.pdf)
- 認知症初期に家族が直面する最初の壁は「受診につなげる難しさ」 — [北翔大学](https://hokusho.repo.nii.ac.jp/record/3238/files/14_p109-113.pdf)；受診を嫌がる本人への伝え方（「認知症だから病院へ」ではなく「あなたが心配だから」）は書籍抜粋レベルの助言にとどまる — [技術評論社 書籍抜粋](https://gihyo.jp/assets/files/book/2025/978-4-297-15180-5/9784297151805-01.pdf)
- 未経験者の7割超が認知症カフェ・家族会・本人ミーティングを知らず、7割が親と話したことがない — [LIFULL介護](https://kaigo.homes.co.jp/tayorini/survey/2025-9/)
- 認知症基本法の成立を75%が知らない — [内閣府2025速報](https://www.wic-net.com/material/static/00022081/00022081.pdf)
- 国内セルフチェックツールは一様に「認知症の診断ではない」と注記（のうKNOW — [nouknow.jp](https://nouknow.jp/)、あたまの健康チェック — [DIME](https://dime.jp/company_news/detail/?pr=2700528)、MCIスクリーニング検査は「リスク把握と生活習慣改善のきっかけ」 — [宇野病院](https://www.uno.or.jp/images/uno_images/kenshin/MCI.pdf)）
- 多因子介入のエビデンスは研究間で結果が割れている（J-MINT本研究は有意差なし — [J-STAGE](https://www.jstage.jst.go.jp/article/jsnt/42/4/42_489/_article/-char/ja)；PRIME Tambaは改善 — [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC11485327/)；US POINTERは構造化群と自己学習群の差0.029SD — [UC Davis](https://health.ucdavis.edu/news/headlines/lifestyle-changes-boost-brain-health/2025/09)）が、一般向けにこの不確実性を翻訳した日本語コンテンツは確認できなかった
- 米国ではDTC脳トレの効果主張が広告審査で取り下げられている — [BBB National Programs](https://bbbprograms.org/media/newsroom/decisions/neurotrack)
- noteの人気コンテンツは体験記中心で、医師による有料の体系的ガイドは表面化していない — [note #認知症](https://note.com/hashtag/認知症)
- 売れている書籍は「当事者視点」「ユーモア」「決断の手引き」型 — [ORICON](https://www.oricon.co.jp/pressrelease/2972811/)、[財経新聞](https://zaikei.co.jp/releases/3542558/)、[かんき出版note](https://note.com/kankipublishing/n/naed80373a723)

### Inferences
- 具体的な空白領域：(1) 「気になる兆候→受診までの90日」のような、受診拒否・家族間調整・費用・窓口を順序立てた実務ガイド、(2) 予防法ごとの根拠の強さを格付けし「やらなくていいこと」も明示するエビデンス翻訳、(3) チェックツールの結果を受け取った後の行動フロー、(4) 子世代（40〜50代）向けの「親と話す」ための会話テンプレート、(5) 全国規模の中立的なLINE／チャットの一次相談導線。
- 収益化の現実的な入口は、個人向け単発コンテンツ（書籍・note 300〜500円〜1,500円）と、企業の介護離職防止予算（従業員1人110円〜月数千円）の二層。保険・自治体チャネルは大手が押さえており、後発は「中立性」と「診断前の家族」というポジションで差別化する余地がある。
- 書籍市場の成功例が示す通り、「不安を煽らない・明るい・当事者を尊重する」トーンは商業的にも有効で、エビデンス重視と両立させた商品は未開拓。

### Gaps
- 上記の空白を直接検証した市場調査（家族の支払意思額、望む形式）は見つからなかった。
- 「受診拒否」経験率、「情報源として何を使ったか」の2025年時点の全国データは未取得。
