# 06. 決済・規制・マネタイズ実務マップ：性／美容／お金 の3カテゴリ（日本・小規模事業者向け）

調査日: 2026-10-10。対象は「日本で小規模スタートアップ／個人事業主が実際に代金を回収し、商品を配布できるか」。法令は条文・ガイドライン名・年を付記。違法領域は「触らない境界」として記載。
注記: 本調査の途中でセッションのWeb検索枠が上限に達したため、後半はURL直接取得（WebFetch）のみで補完した。取得できなかった項目は各節の Gaps に明記。

---

## (a)-1 性・セクシャルウェルネス：カード決済の壁（Visa/Mastercard・PSP・手数料・2024年国内事件）

### Takeaway
Visa/Mastercardは成人向けを「高リスク（MCC 5967）」として加盟店登録・年齢/本人確認・コンテンツ監視を義務化しており、2022〜2025年に日本の主要プラットフォーム（DMM/FANZA、DLsite、ニコニコ、Fantia、とらのあな、U-NEXT等）が相次いでVisa/Mastercard停止を経験した。小規模事業者が成人向けで国際ブランド決済を直接取るのは現実的でなく、JCB・コンビニ・プリペイド・プラットフォーム経由（手数料12.5〜20%）が実務の主戦場になる。

### Cited Findings
**国際ブランドのルール**
- Mastercard AN 5196（2021年）: カード非提示の成人向け販売（サブスク、ストリーミング、画像）に適用。アクワイアラはMCC 5967または7841＋TCC "T" でタグ付けし、加盟店を事前登録、コンテンツ監視・ブロック・削除の管理体制を証明する必要がある — [adultbizlaw.com (2021)](https://adultbizlaw.com/2021/04/27/mastercards-new-rules-the-details-for-paysite-and-platform-owners-operators/)
- 同ルールで、出演者の年齢・本人確認（政府発行ID確認）、公開前のコンテンツ審査、違法・非同意コンテンツ苦情への7営業日以内対応、被写体の異議申立経路、アクワイアラへの月次コンプライアンス報告が求められる — [verifymy.io](https://verifymy.io/resources/regulation/card-brand-requirements)
- 児童搾取や非同意を想起させる検索語・マーケティングは禁止 — [Segpay](https://segpay.com/?p=10603)
- Visa Integrity Risk Program（VIRP）: 2023年5月1日にGlobal Brand Protection Programを置き換えて開始。Tier 1 = MCC 5967（成人向け）、7273（出会い・エスコート）、7995（ギャンブル）、5122/5912（薬局）。Tier 2 = 6051/6012（暗号資産）、4816（サイバーロッカー）、5816。Tier 3 = 6211（高リスク金融取引）、5966、5968（ネガティブオプション/サブスク）、5993 — [LegitScript VIRP解説](https://www.legitscript.com/regulatory-and-card-brand-compliance/visa-integrity-risk-program)
- VIRPで新たに指定されたMCCの加盟店は60日以内に登録、申請料USD 500（返金不可）＋年次更新USD 500（2023年時点） — [CommerceGate](https://www.commercegate.com/?p=3472)
- VIRPでは消費者・クリエイター双方の年齢確認義務と、現地の年齢確認法への準拠証明が求められる — [verifymy.io](https://verifymy.io/resources/regulation/card-brand-requirements)
- ACLU等は2023年にAN 5196を不公正慣行としてFTCに調査要請（結果は未確認） — [ACLU complaint PDF](https://assets.aclu.org/live/uploads/2023/08/Mastercard-Complaint-Final.pdf)

**2022〜2025年の国内停止年表**（利用者編集の年表。各社公式告知の二次整理）
- 2022-07-20 DMM Mastercard停止／2023-03-29 ニジエ Visa不可／2023-11-08 ニコニコ Mastercard停止／2024-02-21 8181Live Visa/MC停止（決済代行の決済ラインが段階的停止）／2024-03-08 ニコニコ Amex停止／2024-03-21 pixivリクエスト PayPal停止／2024-04-03 DLsite Visa・MC一時停止／2024-04-04 DLsite Amex停止／2024-04-12 ピンクパイナップル Visa・MC終了／2024-05-09 ニコニコプレミアム Visa停止／2024-05-21 Fantia Visa・MC一時停止／2024-06-14 FANZA同人 Visa一時停止／2024-06-21 U-NEXT(H-NEXT) Visa・MC停止／2024-08-09 とらのあな通販 Visa・MC停止／2024-08-15 DL.Getchu Visa再開（手数料値上げ・デポジット要求で資金繰り悪化）／2024-11-05 マンガ図書館Z サービス終了（決済停止が理由）／2024-11-11 U-NEXT成人向け Visa・MC再開／2024-12-11 ポケットドラマCD「オトナの女性向け」作品のカード決済終了／2025-01-16 ニコニコ春画 終了／2025-05 駿河屋 成人向け販売閉鎖（決済が理由） — [決済事業者による表現規制年表 (scrapbox)](https://scrapbox.io/motoso/%E6%B1%BA%E6%B8%88%E4%BA%8B%E6%A5%AD%E8%80%85%E3%81%AB%E3%82%88%E3%82%8B%E8%A1%A8%E7%8F%BE%E8%A6%8F%E5%88%B6%E5%B9%B4%E8%A1%A8)
- DLsite（Eisys）は2024年4月3日18時からVisa/Mastercard決済を一時停止。背景はカード会社からの成人向けコンテンツに関する要請。DLsiteは「ロリ」→「ひよこ」等のタグ言い換えで対応したが受け入れられず停止。翌4日Amexも停止し、国内ブランドJCBのみが利用可能に — [Automaton](https://automaton-media.com/en/news/dlsite-disables-visa-mastercard-payment-after-attempt-to-outsmart-credit-card-companies/)
- ニコニコプレミアムは2024年5月10日から一部Visaカードが停止、同月下旬に全Visa停止。Mastercard/Amexは既に一部停止済み。理由は記事中に明示なし。関連記事見出しによれば2025年2月21日にVisa決済再開 — [Impress Watch (2024-05-10)](https://www.watch.impress.co.jp/docs/news/1590378.html)
- FANZA同人は2024年6月14日にVisa停止、Mastercardは2022年7月29日に停止。viviONグループ（DLsite）は2026年1月から「viviON JCBカード」を発行（利用者編集百科のため要公式確認） — [pixiv百科事典 DLsite項](https://dic.pixiv.net/history/DLSite/8440623/source)
- DLsiteは独自決済代替・公式クレジットカードを導入（本文取得できず、見出しのみ確認） — [Automaton (独自決済)](https://automaton-media.com/en/news/japanese-game-and-comic-platform-dlsite-launches-its-own-payment-alternative-following-visa-and-mastercard-suspensions/), [Automaton (公式カード)](https://automaton-media.com/en/news/japanese-content-platform-dlsite-gets-its-own-official-credit-card-amidst-visa-and-mastercard-suspensions/)
- OnlyFansは2021年8月、銀行（BNY Mellon、JPMorgan Chase等）からの圧力で性的コンテンツ禁止を発表し6日後に撤回。クリエイター取り分80%、OnlyFans手数料20% — [Wikipedia: OnlyFans](https://en.wikipedia.org/wiki/OnlyFans)

**PSP（決済代行）のポリシーと手数料**
- Stripe日本の禁止業種: 「売春、エスコート、ペイパービュー、性的マッサージ、フェティッシュサービス、メールオーダーブライド、およびアダルトライブチャット機能を含むアダルトサービス」は禁止。「オンラインの出会い系およびマッチングサービス」は制限業種（追加審査） — [Stripe 禁止・制限業種 (日本)](https://stripe.com/jp/legal/restricted-businesses)
- PayPal日本のAUP、Squareの規約は本文取得に失敗（Gaps参照）
- テレコムクレジット: 比較サイト掲載で手数料3.0%〜＋売上処理料15円〜、他プランは要問合せ。アダルト適用料率は非公開 — [imitsu](https://saas.imitsu.jp/cate-payment/service/1813/price)
- ゼウス: 比較サイト掲載でクレジット（BtoC）手数料3.9%。アダルト可否は未確認 — [imitsu記事](https://saas.imitsu.jp/cate-payment/article/l-524)
- アダルト系は大手決済会社が取扱いを避け、中小決済会社が最大10%の手数料を得られる可能性があると報道 — [Forbes Japan](https://forbesjapan.com/articles/detail/98426)
- 一般的な決済代行手数料は決済手段により2〜10%（一般加盟店向け） — [pay-route](https://pay-route.co.jp/article/?p=7469)
- 国民生活センター/消費者委員会資料: 決済代行業者が海外法人で実態不明なケースが相談事例として報告 — [消費者委員会資料 (2014)](https://www.cao.go.jp/consumer/iinkai/2014/167/doc/140722_shiryou1.pdf)

**ファンプラットフォームの手数料（2026年7月時点）**
- Fantia: 2025年12月改定で非実写12.5%（旧10%）、実写17.5%（旧15%）。2025年7月から月額プラン以外の購入に購入者側8%手数料。振込ごとに330円 — [DAKKI調査プレスリリース (2026-07)](https://animeanime.jp/release/dreamnews/20260724/301284.html)
- CandFans: 20%（紹介経由15%）、最低振込額3,000円。myfans: 17.5%（招待コードで12.5%）、振込無料 — 同上（myfans支援会社の発表のため自社有利の可能性あり）
- FANZA同人: サークル還元率MAX99%キャンペーン、税込550円以下作品の卸値引上げ（2021年プレスリリース） — [value-press](https://www.value-press.com/pressrelease/283626)

### Inferences
- 小規模事業者が成人向けで独自にVisa/MC加盟店契約を取るには、VIRP/AN 5196の登録（US$500＋年次）＋本人確認・モデレーション体制＋月次報告が前提で、国内アクワイアラ側が受けない可能性が高い。実務上は (1) JCB＋コンビニ＋銀行振込＋プリペイド、(2) Fantia/CandFans/myfans等のプラットフォーム（12.5〜20%）、(3) DLsite/FANZA等の販売委託、の三択。
- 「決済停止」は違法性ではなくブランド規約（表現・タグ・ジャンル名）が引き金。DLsiteの事例が示す通り、言い換えで回避すると逆に全停止を招く。
- 手数料モデル: プラットフォーム経由なら粗利は売上の80〜87.5%、独自決済（アダルト対応PSP）で7〜10%程度の手数料＋保証金・デポジットが想定される（一次ソースで料率を確認できたわけではない）。

### Gaps
- テレコムクレジット／ゼウス／SBペイメントの「アダルト向け」正式料率・保証金・入金サイクルは公開情報で確認できず（要個別見積）。
- PayPal日本AUP・Square日本規約の成人向け条項は本文取得失敗（PayPalページは切り詰め、Squareは未取得）。
- Visa/Mastercardの現行ルール原文（2024〜2026年版）は未取得。AN 5196の文言は2021年の弁護士解説に依拠。
- Pixiv BOOTH・Skeb・Ci-enの個別停止日・復旧状況は一次情報を確認できず。
- チャージバック率の閾値（Visa VAMP等）と成人向けの実際のCB率は未取得。

---

## (a)-2 性・セクシャルウェルネス：配布経路（アプリストア・広告・SNS・AI companion）

### Takeaway
App Store/Google Playは「露骨に性的」なアプリを禁止し、UGC/クリエイターアプリにはモデレーションと年齢制限を要求。広告はMeta/Googleとも「快楽目的（セックストイ・増大）」は不可だが「健康目的（ED予防・避妊・潤滑剤・性教育）」は18+ターゲティングで可、という線引き。Xは2024年6月に同意に基づく成人向けコンテンツを正式許容、YouTubeは収益化外し。日本の媒体（LINEヤフー）は2026年9月からED/包茎広告の表現をさらに制限。

### Cited Findings
**アプリストア**
- Apple 1.1.4: 「Overtly sexual or pornographic material … This includes "hookup" apps and other apps that may include pornography or be used to facilitate prostitution」は不可。1.2: UGCアプリはフィルタ・通報・ブロック・連絡先の4要件、主にポルノ目的で使われるUGC/ランダムチャットは「予告なく削除」。1.2.1(a) クリエイターアプリは年齢制限機構が必要。3.1.1: デジタルコンテンツのアンロックはIAP必須。4.3(b): 出会い系は「意味のある差別化」がない新規申請は不受理 — [App Store Review Guidelines](https://developer.apple.com/app-store/review/guidelines/)
- Google Play: 「We don't allow apps that contain or promote sexual content or profanity, including pornography」。EDSA（教育・記録・科学・芸術）目的のヌードは例外。エスコート、シュガーダディ等の対価を伴う性的関係の斡旋は禁止。非同意のディープフェイク性的コンテンツ禁止 — [Google Play 性的コンテンツ](https://support.google.com/googleplay/android-developer/answer/9878810)
- Google Play AI生成コンテンツポリシー: 「Generative AI apps primarily intended to be sexually gratifying」および非同意ディープフェイク性的素材は禁止。テキスト型AIチャットボットアプリはポリシー対象 — [Google Play AI-Generated Content](https://support.google.com/googleplay/android-developer/answer/14094294)
- 2026年4月のTech Transparency Project報告で、App Storeに18本、Google Playに20本の「nudify」アプリが確認され、Appleは15本削除。同報告はnudifyアプリが累計4.83億DL・1.22億ドル超の収益とする（AppMagic推計）。カリフォルニア州市検事は1件US$25,000以上の民事制裁を警告 — [MediaNama (2026-04)](https://www.medianama.com/2026/04/223-apple-google-steer-users-nudify-apps-reports/), [The Star](https://www.thestar.com.my/tech/tech-news/2026/04/16/apple-google-offer-nudify-apps-despite-policies-against-them)

**広告ネットワーク**
- Meta（成人向け製品・生殖の健康）: 禁止＝「Sex toys, erotic products, non-surgical genital enhancement products」（快楽・増強目的）、ストリップクラブ等の成人向けサービス、「G-spot augmentation」等の快楽目的手術。許可（18+必須）＝「Prevention of erectile dysfunction」「Pain relief during sex」「Contraceptive products, including condoms」「Lube and pheromones」（健康目的）。18+不要＝性教育（情報・教育・記録目的）、生理トラッキングアプリ、女性衛生用品、ランジェリー — [Meta Health and Wellness / Adult Products](https://transparency.meta.com/policies/ad-standards/content-specific-restrictions/adult-products-or-services)
- Meta出会い系広告: 「Ads for dating services are only allowed with prior written permission」、18+必須、金銭を伴う出会い（メールオーダーブライド）・不倫斡旋・架空人物・「Sexually suggestive emphasis」禁止 — [Meta Dating Ads](https://transparency.meta.com/policies/ad-standards/restricted-goods-services/dating-ads/)
- 2022年Center for Intimacy Justice報告: ED・男性向け商材は通るのに女性向け健康広告が却下される不均衡。Metaは「執行ミスがあり覆した」とコメント — [Marketing Brew](https://www.marketingbrew.com/stories/2022/01/11/facebook-s-ad-blocking-for-health-products-and-services-could-have-a-gender-bias-research-suggests)
- Google Ads 性的コンテンツ: 「Sexual merchandise（sex toys, sexual enhancers）」「Sexual entertainment」は中程度制限＝年齢・地域法・SafeSearch設定に基づき配信。ヌードは強い制限。未成年ターゲティング禁止。日本固有の配信不可指定はなし — [Google Ads Sexual content](https://support.google.com/adspolicy/answer/6023699)
- LINEヤフー: 2026年9月7日から、LINEヤフー広告・LINE広告での医療機関によるED治療・包茎治療等の訴求について、性的印象を与える「症状」「治療内容」（包茎、ED、早漏、長くする、ED改善 等）はクリエイティブの1辺外縁から1/4以内に収める、「自信」「活力」「元気になる」「元に戻る」「取り戻す」「現役」「勃起」「勃起力」「精力アップ」「持続力」「夜のパワー」等は掲載不可、女性画像は在籍医療従事者（白衣等）以外不可。LINE広告は掲載制限により性的部位治療の訴求自体が掲載不可（2026年7月6日現在）。医療広告ガイドライン遵守が前提 — [LINEヤフー 広告審査判断基準変更 (2026-07-06, PDF)](https://www.lycbiz.com/sites/default/files/media/jp/terms-and-policies/pdf/ly/【広告主・代理店限定】医療機関における男性器特有の治療訴求に関する広告審査判断基準変更.pdf)

**SNS・動画プラットフォーム**
- X（2024年6月）: 同意のもと制作・配布された性的コンテンツを「正当な芸術表現」として許容。明確なラベル付け必須、未成年と希望しない成人には非表示、搾取・非同意・未成年性化は禁止 — [Al Jazeera (2024-06-04)](https://www.aljazeera.com/economy/2024/6/4/elon-musks-x-updates-policies-to-formally-allow-adult-content)
- 同時期報道: Xの広告ポリシーは「X prohibits the promotion of adult sexual content globally」（広告のみ。サブスクによるクリエイター収益は直接制限せず、との解釈） — [Social Media Today](https://www.socialmediatoday.com/news/x-updates-policies-to-allow-sexual-content-in-the-app/717845/)
- YouTube: 性的示唆コンテンツは「advertiser-friendly」外として収益化停止（削除ではない）。「digitally altered or generated to be sexually explicit」コンテンツの作成・配布の宣伝（AI OnlyFansアカウントの作り方等）は広告不適格と明示 — [Daily Wire](https://www.dailywire.com/news/youtube-demonetizes-ai-porn-tutorial-videos), [Search Engine Journal (2016)](https://www.searchenginejournal.com/youtube-disabling-monetization-non-advertiser-friendly-videos/172274/)
- Stripe日本: 「アダルトライブチャット」「ペイパービュー」は禁止業種（AI companionのNSFWチャットも同カテゴリと読める） — [Stripe 日本](https://stripe.com/jp/legal/restricted-businesses)

### Inferences
- 「AI彼女/companion」アプリはストア規約上、NSFWにした瞬間Google Playの「sexually gratifying」禁止、Appleの1.1.4に抵触。SFWのまま審査を通し、課金はIAP（手数料15〜30%）必須で、Web課金に逃がす場合はStripe等の規約（アダルトライブチャット禁止）が次の壁になる。日本では実質「JCB＋コンビニ＋アダルト対応PSP」かプラットフォーム経由。
- 広告で合法的に「性」を扱えるのは「医療・健康フレーム」（ED治療、避妊、潤滑剤、性教育）のみ。ただし日本ではED広告も医療広告ガイドライン＋媒体基準（LINEヤフー2026年9月）で表現が強く制限され、「モテる」「自信」系の訴求は不可。
- Xは唯一の「成人向けを許容する大手SNS」だが、広告は不可でサブスク課金に依存。日本での収益化はFantia/myfans等への導線としての利用が現実的。

### Gaps
- Appleの「AI girlfriend」アプリ削除（2024年報道）やAppleのAI生成コンテンツに関する2025年ガイドライン改定は本文確認できず（ガイドライン末尾12k文字は未読）。
- X Creator Subscriptions/Ads Revenue Sharingの成人向け適格性の一次ポリシー文は取得失敗（403）。
- note.comの成人向け・情報商材に関する規約条項は取得失敗（403）。
- TikTokの性的コンテンツ・広告ポリシーは未調査。
- Meta広告の「increase/増大」系・恋愛コンサル系広告の審査実態は未調査。

---

## (a)-3 性・恋愛：日本の法規制（風営法・出会い系サイト規制法・刑法175条・AV新法・医師法/薬機法・2025風営法改正）

### Takeaway
日本で性関連ビジネスを「合法に」やるには、(1) 映像送信型性風俗特殊営業の公安委員会届出（有料アダルト配信）、(2) 出会い系サイト規制法の届出＋年齢確認（異性紹介）、(3) 刑法175条のわいせつ基準（モザイク）、(4) AV出演被害防止・救済法（2022年）の契約・期間ルール、(5) ED等の医療領域は医師法20条・薬機法66/68条・医療広告GL、という5つの届出/境界がある。2025年風営法改正でホスト等の「色恋営業」「売掛回収目的の性風俗勧誘」「スカウトバック」が規制され、無許可営業罰則が法人3億円に引き上げられた。

### Cited Findings
**風営法（風俗営業等の規制及び業務の適正化等に関する法律）**
- 映像送信型性風俗特殊営業: 「専ら、性的好奇心をそそるため性的な行為を表す場合又は衣服を脱いだ人の姿態の映像を見せる営業で、電気通信設備を用いてその客に当該映像を伝達することにより営むもの」。営業開始前に営業所所在地を管轄する警察署経由で公安委員会に届出（様式第31号＋営業の方法 様式第32号、事務所使用権原書類、URL疎明書類、住民票／法人は定款・登記・役員住民票） — [香川県警](https://www.pref.kagawa.lg.jp/police/tetuzuki/eigyou/seifuuzoku.html), [愛知県警](https://www.pref.aichi.jp/police/shinsei/fuei/kyoka/hoan/shinsei.html), [島根県警 様式](https://www.pref.shimane.lg.jp/police/05_application_and_procedures/business_licensing/huuzokueigyou/yoshiki.html)
- 「専ら」営む者が対象で、アダルトバナー広告を載せるだけのサイトは該当しない。サーバーが国外でも国内で営業していれば対象。18歳未満への営業禁止、身分証やクレジットカード等による年齢証明が義務 — [INTERNET Watch (1999/2005)](https://internet.watch.impress.co.jp/www/article/1999/0315/fuueihou.htm), [INTERNET Watch (2005)](https://internet.watch.impress.co.jp/cda/news/2005/04/19/7334.html)
- 2025年改正風営法: 2025年6月28日施行（欠格事由拡大は2025年11月28日施行）。接待飲食営業（ホスト・キャバクラ）で恋愛感情等に乗じて困惑させる飲食・遊興の要求（色恋営業）を禁止（罰則なし・行政処分対象）。料金回収目的の威迫・困惑行為や性風俗勤務・AV出演の要求は6月以下の懲役又は100万円以下の罰金。性風俗営業者が紹介者に利益供与する「スカウトバック」禁止（広告費名目の迂回払いも対象、同罰則）。無許可営業は法人3億円以下の罰金、個人5年以下の懲役又は1000万円以下の罰金 — [ben54.jp](https://www.ben54.jp/news/2407)
- 警察庁は2025年6月4日に広告通達を出し、「年間売上〇億円突破」「指名数No.1」「神」「レジェンド」等の使用を禁止 — [DIME](https://dime.jp/genre/1989659/), [マネーポスト](https://www.moneypost.jp/1300932)

**出会い系サイト規制法（インターネット異性紹介事業を利用して児童を誘引する行為の規制等に関する法律、2003年制定・2008年改正）**
- 「インターネット異性紹介事業」4要件: (1)面識のない異性との交際希望者の求めに応じ交際情報を電子掲示板に掲載、(2)公衆が閲覧可能、(3)閲覧者がメール等で投稿者に連絡可能、(4)有償無償を問わず反復継続。事業者は公安委員会への届出（3条）、児童でないことの確認（11条）、禁止誘引書き込みの削除（12条）等の義務。罰則は31〜37条 — [警察庁 出会い系サイト規制法](https://www.npa.go.jp/policy_area/no_cp/deai/regulatory.html)
- 2008年改正で届出義務化、児童利用禁止の明示、年齢確認義務。2009年2月施行の改正規則で、運転免許証等の送付またはクレジットカード決済等による年齢確認が原則義務化（従来は自己申告可） — [INTERNET Watch (2008)](https://internet.watch.impress.co.jp/cda/news/2008/01/17/18146.html), [INTERNET Watch (2009)](https://internet.watch.impress.co.jp/cda/news/2009/03/27/22942.html)
- 国民生活センター「出会い系サイト」相談: 2023年度6,938件、2024年度4,402件、2025年度3,399件、2026年度283件（5/31時点）。典型は支援金・ポイント名目誘導、ポイント課金、プリペイド電子マネー支払い — [国民生活センター 出会い系サイト](https://www.kokusen.go.jp/soudan_topics/data/deaikei.html)

**刑法175条（わいせつ物頒布等）**
- 「わいせつな文書、図画、電磁的記録に係る記録媒体その他の物を頒布し、又は公然と陳列した者は、二年以下の拘禁刑若しくは二百五十万円以下の罰金若しくは科料に処し、又は拘禁刑及び罰金を併科する。」（2025年拘禁刑化後の条文） — [e-Gov 刑法 (明治40年法律第45号)](https://laws.e-gov.go.jp/api/2/law_data/140AC0000000045)

**AV出演被害防止・救済法（令和4年法律第78号、2022年6月23日施行）**
- 契約時に契約書等と説明書面等を交付し説明する義務。交付日から1か月間は撮影禁止。全撮影終了から4か月間は公表禁止。出演者は性別・年齢を問わず理由なく契約解除でき、公表から1年間（契約時期により経過措置: 2022/6/23〜2024/6/22締結は公表から2年、2024/6/23〜2025/6/22締結は公表から1年又は2026/12/22の遅い方）。契約がない公表・解除後は販売配信停止を請求可。撮影時の安全確保義務、嫌な行為の拒否権、公表前の映像確認権 — [内閣府男女共同参画局 AV出演被害防止・救済法](https://www.gender.go.jp/policy/no_violence/avjk/index.html)

**医療領域（ED・オンライン診療）**
- 薬機法66条（虚偽・誇大広告禁止）、68条（承認前医薬品の広告禁止）。未承認医薬品の広告は68条違反（東京都の解説） — [東京都保健医療局](https://www.hokeniryo.metro.tokyo.lg.jp/anzen/iyaku/koukokukisei/zenpan/kozinyunyu)
- 2018年、患者に一度も会わずED薬等を処方する「オンライン診療」が医師法20条（無診察治療禁止）違反の疑いで厚労省が問題視 — [日刊薬業](https://nk.jiho.jp/article/137020)
- 医療広告GL事例解説書は第6版（令和8年3月30日事務連絡）。厚労省は医療機関ネットパトロール通報フォームを運営 — [厚労省 医療広告規制](https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/kenkou_iryou/iryou/kokokukisei/index.html)
- 国民生活センター美容医療相談では「オンライン薄毛治療で電話のみ診療後、薬が定期配送に切り替わっていた」事例、包茎手術の即日契約・高額契約トラブル — [国民生活センター 美容医療サービス](https://www.kokusen.go.jp/soudan_topics/data/biyo.html)

**恋愛コンサル・情報商材周辺（消費者庁 注意喚起）**
- 2026-06-12 消費者庁注意喚起: 合同会社PLANETが2024年11月頃からマッチングアプリで知り合った相手に「営業の仕事」を紹介→コンサルティング契約→消費者金融での高額借入をさせ支払わせる。断定的判断の提供を確認し消費者安全法38条1項で公表 — [消費者庁 (2026-06-12)](https://www.caa.go.jp/notice/entry/046534/)
- 国民生活センター「情報商材」: 「副業、投資やギャンブル等で高額収入を得るためのノウハウ等と称して販売されている情報」。マッチングアプリの知人から投資講座教材を勧められる事例、購入後にサポート・コンサル契約へ誘導。相談件数 2023年6,256件、2024年4,163件、2025年2,623件 — [国民生活センター 情報商材](https://www.kokusen.go.jp/soudan_topics/data/infoproducts.html)
- 2024年の特商法行政処分で「恋愛」「モテる」系情報商材への処分は確認できず（通販分野の処分は美容商材中心） — [消費者庁 執行状況2024](https://www.caa.go.jp/notice/enforcement/2024/), [ネットショップ担当者フォーラム](https://netshop.impress.co.jp/node/13403)

### Inferences
- 「触らない境界」: 売春防止法（斡旋）、児童ポルノ、無修正配信（175条）、無届出の有料アダルト配信・異性紹介、ホストの売掛回収・スカウトバック、未承認ED薬の個人輸入代行広告、無診察処方。
- 合法ゾーンの届出コスト自体は低い（映像送信型は警察署への書類届出のみ）。重いのは決済と広告であって法律ではない。ただし出会い系規制法は「異性」紹介限定で、同性向け・友達マッチングは法の射程外だが、Visa Tier1（MCC 7273）とMetaの事前許可制は同じ。
- 恋愛コンサルは法規制が薄い代わりに、消費者庁が「マッチングアプリ×コンサル契約×消費者金融」の型を名指しで公表しており、特商法（通信販売の最終確認画面／電話勧誘）と消費者安全法38条の公表リスクが現実的。

### Gaps
- 警察庁の風営法Q&A原文は未取得（県警案内で代替）。出会い系サイト規制法31〜37条の罰則金額は未確認。
- 刑法175条の「モザイク基準」は法文に無く判例・実務慣行であり、一次資料未取得。
- 売春防止法、迷惑防止条例（ナンパ講習）に関する一次資料は未取得。
- 恋愛系（「モテる」情報商材・恋愛サロン）に対する消費者庁の特商法処分事例は2024〜2025年には見当たらず（検索枠の制約で2017〜2023年分は未調査）。
- 景表法の「増大サプリ」措置命令事例は未調査（検索枠切れ）。

---

## (a)-4 性・恋愛：小規模で成立しているマネタイズモデル

### Takeaway
小規模で合法に回るのは「プラットフォーム委託（FANZA/DLsite/Fantia）」「アフィリエイト（FANZA最大70%／新規サービス報酬最大5,240円）」「ファンサブスク（手数料12.5〜20%）」。出会い系・ED・サプリの広告出稿は規制で表現が縛られる一方、Meta/Googleの「健康フレーム」とX/サブスク導線は使える。

### Cited Findings
- DMMアフィリエイト: 直接報酬（同一商品）最大70%、カテゴリ報酬（同カテゴリ別商品）最大20%、新規サービス報酬（サービス初購入）最大5,240円（税抜4,764円）。翌月10日払い、振込手数料DMM負担。成人向け料率表は年齢ゲート内 — [DMMアフィリエイト](https://affiliate.dmm.com/)
- 解説記事ベース: FANZA動画35%〜最大70%（販売本数・キャンペーンで加算）、電子書籍約20〜30%、DMM GAMES約10%（記事間で数値不一致あり） — [mobinc (料率)](https://mobinc.jp/column/?p=1484), [mobinc (最大70%)](https://mobinc.jp/column/?p=1994)
- Fantia 12.5%/17.5%、myfans 17.5%/12.5%、CandFans 20%/15%（前節参照） — [DAKKI調査](https://animeanime.jp/release/dreamnews/20260724/301284.html)
- OnlyFans: クリエイター80%／手数料20% — [Wikipedia](https://en.wikipedia.org/wiki/OnlyFans)
- マッチングアプリ特化アフィリエイトサイトの売却事例: 月間売上約15万円・月間利益約9万円（2024年8月）等 — [batonz (案件 No.58685)](https://batonz.jp/sell_cases/58685), [batonz (No.74785)](https://batonz.jp/sell_cases/74785)
- 松井証券のアフィリエイト条件（参考: 金融系の提携審査の厳しさ）: 投資関連サイト・ブログとのみ提携、ギャンブル関連や公序良俗違反は不可、外務員登録のない者は投資勧誘・個別商品説明不可。ASPはAccesstrade/Janet/A8.net/TG/TCS — [松井証券](https://www.matsui.co.jp/utility/etc/affiliated.html)
- Meta広告でED予防製品は18+で可、Google広告でも遠隔医療は医療機関免許＋厚労省登録またはLegitScript認証＋Google認証で可（日本） — [Meta](https://transparency.meta.com/policies/ad-standards/content-specific-restrictions/adult-products-or-services), [Google Ads Healthcare (Japan)](https://support.google.com/adspolicy/answer/176031)
- 女性向け「オトナの女性向け」ドラマCDは2024年12月にカード決済終了（ポケットドラマCD）＝女性向け（TL/BL）も国際ブランドから同様の扱い — [年表](https://scrapbox.io/motoso/%E6%B1%BA%E6%B8%88%E4%BA%8B%E6%A5%AD%E8%80%85%E3%81%AB%E3%82%88%E3%82%8B%E8%A1%A8%E7%8F%BE%E8%A6%8F%E5%88%B6%E5%B9%B4%E8%A1%A8)

### Inferences
- 一人運営で最も粗利が高いのは「自作コンテンツ（音声・テキスト・イラスト）をDLsite/FANZA/Fantiaに委託」（取り分約80〜90%、決済・年齢確認・風営法届出をプラットフォームが吸収）。次点が「FANZA/DMMアフィリエイト」（70%報酬だが決済リスクはDMM側）。
- 「性×医療（ED/AGAオンライン診療の紹介）」は広告が通る数少ない経路だが、2026年9月以降LINEヤフーで表現が厳格化。SEO/比較記事型が主戦場。
- 恋愛コンサル×LINEファネルは法規制の空白ではなく、特商法（電話勧誘販売・通信販売）＋消費者安全法38条公表の直撃ゾーン。高額コンサル・借入誘導型は「触らない」。

### Gaps
- Pairs/タップル/with等のマッチングアプリCPA単価（ASP案件単価）は公開ソースなし（ASPログイン必要）。
- TENGAアフィリエイト制度、FANZAの成人向け料率表（年齢ゲート内）は未取得。
- 恋愛コンサルLINEファネルの単価・CVR等の実データは未取得。

---

## (b)-1 美容・外見：医療広告ガイドライン／薬機法／景表法／特商法／2025医療法改正

### Takeaway
美容は「法律上は参入自由だが、言えることが極端に少ない」領域。医療広告GL（医療法6条の5、省令1条の9）で体験談は全面禁止・ビフォーアフターは治療内容/費用/期間/リスク併記が条件、限定解除4要件。化粧品は薬機法の56効能以外を一切うたえず2021年8月から課徴金制度。景表法はステマ告示（2023年10月）で広告主責任、2024年6月に医療法人への初のステマ措置命令。特商法でエステ・一部美容医療は特定継続的役務（1か月超かつ5万円超）としてクーリングオフ・中途解約。2025年12月成立の医療法改正で美容医療機関に安全管理体制の報告義務（公布後2年以内施行）。

### Cited Findings
**医療広告ガイドライン（医療法6条の5、医療法施行規則1条の9、2018年改正）**
- 省令1条の9第1号: 「患者その他の者…の主観又は伝聞に基づく、治療等の内容又は効果に関する体験談の広告をしてはならないこと。」口コミサイトのコメント転載、スタッフの体験談、患者アンケートの加工転載も禁止。第2号: 「患者等を誤認させるおそれがある治療等の前又は後の写真等の広告をしてはならないこと。」写真掲載時は治療内容・費用・期間回数・リスク副作用を同じ場所に併記（リンク先不可）。バナー・SNSに写真だけも規制対象。限定解除4要件: (1)患者が自ら求めて入手する情報（Webサイト等）、(2)問い合わせ先明示、(3)自由診療の通常必要な治療内容・費用、(4)主なリスク・副作用。違反時: 報告命令・立入検査（医療法6条の8第1項）、中止命令・是正命令（同2項）、懲役・罰金（87条1号、89条2号）。規制対象は医療機関だけでなくマスコミ・アフィリエイター等掲載者の肩書を問わない — [モノリス法律事務所](https://monolith.law/corporate/medical-advertising-experiences)
- 2018年改正で体験談・誤認を与える術前術後表示が禁止事項に追加、客観的事実を証明できない内容も削除対象 — [厚労省 新旧対照表](https://www.mhlw.go.jp/file/05-Shingikai-10801000-Iseikyoku-Soumuka/0000186384.pdf)
- 加工・修正した術前術後写真は虚偽広告、著名人との関係強調は比較優良広告の事例 — [厚労省 事例解説書](https://www.mhlw.go.jp/content/001683116.pdf)
- 事例解説書 第6版（令和8年3月30日）、ガイドライン実施手順書モデル（令和6年8月23日）、ネットパトロール通報フォーム — [厚労省 医療広告規制](https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/kenkou_iryou/iryou/kokokukisei/index.html)
- 令和7年臨時国会で成立した医療法等改正法の一部が令和8年4月1日施行、オンライン診療の定義追加 — [厚労省 (001683595)](https://www.mhlw.go.jp/content/001683595.pdf)

**2025年医療法等改正（令和7年法律第87号、2025年12月5日成立・12月12日公布）**
- 「美容を目的として人の皮膚若しくは歯牙を清潔にし、若しくは美化し、身体を整え、又は体重を減ずるための医学的処置、手術及びその他の治療を行う病院又は診療所」（美容医療機関）に、医療安全指針・事故防止策・緊急時対応体制・医師情報等を都道府県知事（保健所設置市・特別区は市長・区長）に報告する義務を新設（改正医療法6条の12の2第1項）。知事は確認のため官公署に情報提供を求められ（3項）、未報告・虚偽報告には報告・是正を命令可（5項）、特に必要な事項は公表義務（4項）。施行期日は公布後2年以内の政令で定める日。あわせて健康保険法改正で保険医療機関の管理者は臨床研修2年＋病院での保険診療3年以上（合計5年）が要件（70条の2、令和8年4月1日施行）＝「直美」抑止 — [西村あさひ ニューズレター (2026-01-21)](https://www.nishimura.com/sites/default/files/newsletters/file/corporate_260121_ja.pdf)
- 事前評価書: 安全管理措置の実施状況・アフターフォロー体制等を年1回報告、知事等が公表 — [厚労省 規制の事前評価書](https://www.mhlw.go.jp/wp/seisaku/ria/2024/dl/ria2025_2_6.pdf)
- 医師法施行規則改正（令和8年厚生労働省令第62号）で診療録記載事項に美容医療の内容を追加 — [薬事日報](https://www.yakuji.co.jp/?p=132234)

**薬機法（化粧品）**
- 一般化粧品の広告で表示できる効能効果は56項目に限られ、事実であっても56項目以外は広告不可。薬用化粧品は承認範囲内で可。使用実感や愛用者コメントも広告とみなされ得る — [ECのミカタ](https://ecnomikata.com/column/30861/), [ownly](https://www.ownly.jp/sslab/sns-pmda)
- 2019年12月4日公布の改正薬機法で66条1項（虚偽・誇大広告）違反に課徴金制度、2021年8月1日施行。改正前は罰金上限200万円のみで利得を取り上げる仕組みがなかった — [西村あさひ (2020-06)](https://www.nishimura.com/sites/default/files/images/newsletter_200612_corporate.pdf), [コマースピック](https://www.commercepick.com/archives/45210)

**景表法**
- ステルスマーケティング告示: 2023年10月1日施行。事業者の表示であることを一般消費者が判別困難な表示が対象。義務を負うのは広告主（事業者）のみでインフルエンサー等第三者は対象外 — [消費者庁 ステマ規制](https://www.caa.go.jp/policies/policy/representation/fair_labeling/stealth_marketing/)
- 2024年6月6日、医療法人社団祐真会（マチノマ大森内科クリニック）に景表法5条3号（ステマ告示）違反で措置命令（7条1項） — [消費者庁 (2024-06-07)](https://www.caa.go.jp/notice/entry/038178/)
- 2024年8月8日、RIZAP株式会社（chocoZAP）に景表法5条1号（優良誤認）又は5条3号（ステマ）で措置命令 — [消費者庁 (2024-08-09)](https://www.caa.go.jp/notice/entry/038980/)
- アフィリエイト広告等に関する検討会: 2021年6月10日〜2022年1月28日の6回開催、報告書は2022年2月 — [消費者庁 検討会ページ](https://www.caa.go.jp/policies/policy/representation/meeting_materials/review_meeting_003/)

**特商法（特定継続的役務提供）**
- エステ・美容医療は期間1か月超かつ金額5万円超で特定継続的役務。契約書面受領から8日間クーリングオフ、期間後も中途解約可。美容医療で対象となるのは脱毛、にきび・しみ・そばかす・ほくろ・入れ墨等の除去、しわ・たるみの軽減、脂肪の減少、歯牙の漂白（2017年12月1日施行の改正）。中途解約の損害賠償上限: エステは施術前2万円／施術後は提供済対価＋2万円又は残額10%の低い方、美容医療は施術前2万円／施術後は提供済対価＋5万円又は残額20%の低い方。関連商品（化粧品・サプリ等）も対象だが消耗品は使用後は原則クーリングオフ不可 — [京都府消費生活安全センター](https://www.pref.kyoto.jp/shohise/15400050.html), [広島県](https://www.pref.hiroshima.lg.jp/site/syouhiseikatsucenter/keihatsu05-0110.html)
- 通信販売（特商法11条・12条の6）: 最終確認画面に分量・価格・支払時期・引渡時期・申込期間・解約条件等の表示義務、2回以上の購入が条件なら定期購入である旨と販売条件を明示、解除妨害の不実告知禁止（13条の2）、誤認による申込取消権（15条の4） — [特商法ガイド 通信販売](https://www.no-trouble.caa.go.jp/what/mailorder/)
- 2024年5月〜12月の通販分野処分4件はいずれも美容商材 — [ネットショップ担当者フォーラム](https://netshop.impress.co.jp/node/13403)
- 2025年の通販処分: 株式会社VIRTH（2025-06-27、6か月停止）、ASUNOBI株式会社（2025-09-10〜2026-03-09、美容クリーム等、6か月の広告・申込受付・契約締結停止＋役員禁止命令）、株式会社BIZM（2025-11-06〜2026-05-05、美容クリーム等、同6か月＋役員禁止命令） — [消費者庁 ASUNOBI](https://www.caa.go.jp/notice/entry/043486/), [消費者庁 BIZM](https://www.caa.go.jp/notice/entry/044086), [消費者庁 執行状況2025](https://www.caa.go.jp/notice/enforcement/2025/)
- 国民生活センター「美容医療サービス」相談: 2023年度6,281件、2024年度10,744件、2025年度7,944件、2026年度735件（5/31時点）。典型は即日施術・高額契約・リスク説明なし・オンライン薄毛治療の定期配送 — [国民生活センター](https://www.kokusen.go.jp/soudan_topics/data/biyo.html)
- 2024-10-24 消費者庁注意喚起: 株式会社ライフパートナーズ／株式会社NEOマーケティングが美容サロンの無料体験来訪者に「SNS投稿で月1万円稼げる」として高額加盟金を支払わせ不実告知（消費者安全法38条1項） — [消費者庁 (2024-10-24)](https://www.caa.go.jp/notice/entry/039720/)

### Inferences
- 美容の規制は「免許」ではなく「表現」に集中。個人メディアでも医療広告GLの射程（掲載者の肩書を問わない）に入るため、クリニック比較サイトは体験談・ビフォーアフターを扱うと同時に限定解除要件を満たす設計が必須。
- 化粧品D2Cは薬機法56効能＋2021年課徴金＋特商法定期購入規制の三重で、2024〜2025年の特商法処分はほぼ美容クリーム通販に集中している＝「美容通販の定期購入」は当局の最優先執行領域。
- 2025年医療法改正は美容クリニック側のコスト増と情報公開（アフターフォロー体制の公表）を生み、「公表情報を比較する」メディアには追い風。

### Gaps
- 医療広告GL Q&Aの最新更新日、2025〜2026年の美容医療関連GL改定の具体文言は未取得。
- 消費者庁No.1表示実態調査（2024年）報告書、祐真会・RIZAPの措置命令の具体表示内容（PDF）は未取得。
- アフィリエイト広告検討会報告書本文・管理措置指針改正（2022年6月29日）の本文は未取得（ページには報告書PDFリンクのみ）。

---

## (b)-2 美容・外見：広告プラットフォーム・アフィリエイト経済・集客コスト

### Takeaway
Meta/Googleは美容整形広告自体は18+で許容（Metaはビフォーアフターも一般美容で可、「容姿の劣等感」表現は禁止）。Googleは日本で遠隔医療・オンライン薬局に厚労省登録またはLegitScript認証＋Google認証を要求。アフィリエイト単価（AGA・脱毛・クリニック）の公開一次ソースは見つからず、入手できたのは証券口座500円（楽天証券）、金融系CPA 8,000〜20,000円、人材10,000〜25,000円といった断片のみ。

### Cited Findings
- Meta（美容施術）: 「must be targeted to people at least 18 years or older」。一般美容製品・施術・手術のビフォーアフター変化の描写は許可。「statements of inferiority about physical appearance」禁止。減量製品も18+、「脂肪をつまむクローズアップ」禁止。処方薬は別ポリシーで地域制限＋書面許可。非永続的コスメ（クリーム・メイク・ヘア）は18+不要 — [Meta Health and Wellness](https://transparency.meta.com/policies/ad-standards/restricted-goods-services/health-wellness/)
- Google Ads（日本）: オンライン薬局は薬局免許＋厚労省登録またはLegitScript認証、遠隔医療は医療機関免許＋厚労省登録またはLegitScript認証、いずれもGoogle認証が必要。処方薬名は広告文・LP・キーワードで使用不可（医療従事者限定サイト・実店舗薬局は例外）。OTCは免許番号のサイト掲載で可。「speculative and/or experimental medical treatments」は禁止 — [Google Ads Healthcare](https://support.google.com/adspolicy/answer/176031)
- 楽天証券アフィリエイト: 1件500円 — [楽天証券](https://www.rakuten-sec.co.jp/smartphone/service/affiliate.html)
- 業界別CPA（広告主側）: EC 5,000〜12,000円、金融 8,000〜20,000円（本文中「金融系では15,000円超」とも）、人材 10,000〜25,000円 — [mobinc CPAガイド (2025-12)](https://mobinc.jp/media/2025/12/28/cpa-meaning-calculation-guide/)
- 証券口座開設の広告運用事例: 目標CPA 12,000円→実績8,000円 — [StockSun](https://stock-sun.com/example/ad/shouken-kokyakutanka/)
- ゴリラクリニックはA8.net等複数ASPで提携広告を出稿（報酬額非公開） — [affsignal](https://affsignal.com/merchant/Gorilla)
- AGA治療費: 初月6,000〜38,000円、フィナステリド3,000〜6,000円/月、ミノキシジル内服6,000〜12,000円/月、メソセラピー2〜5万円/回、植毛500グラフト50〜60万円 — [銀座総合美容クリニック](https://www.gincli.jp/?p=733)
- トリビュー: 2024年10月に総額17億円調達、2025年4月時点で累計170万DL・累計GMV 250億円。利用者は無料で、クリニックに支払った施術費の一部がトリビューの収入。予約・施術で施術費5%分のポイント還元 — [創業手帳](https://sogyotecho.jp/?p=227928), [GMO プレスリリース](https://group.gmo/pdf/news/gmo_news_9473.pdf), [App Store](https://apps.apple.com/jp/app/%E3%83%88%E3%83%AA%E3%83%93%E3%83%A5%E3%83%BC-%E7%BE%8E%E5%AE%B9%E5%8C%BB%E7%99%82%E3%81%AE%E5%8F%A3%E3%82%B3%E3%83%9F%E4%BA%88%E7%B4%84%E3%82%A2%E3%83%97%E3%83%AA/id1291753353?l=en-US)
- キレイパス byGMO: 美容クリニックの体験チケットを事前決済で販売（GMOくまポン運営、2018年開始）、2025年に「キレイパスコネクト」とトリビューが予約連携 — [リセマム (2018)](https://resemom.jp/release/prtimes/20181115/49167.html), [GMO (9473)](https://group.gmo/pdf/news/gmo_news_9473.pdf)
- Stripe: 化粧品はグローバル制限カテゴリではない（タイ・インドネシアのみ）。「医薬品、医療機器、遠隔医療」は制限業種（追加審査） — [Stripe 日本](https://stripe.com/jp/legal/restricted-businesses)

### Inferences
- 美容は3カテゴリ中、決済・広告ともに最も通りやすい（Stripe/Meta/Googleいずれも「許可＋条件」）。粗利を決めるのは規制対応コスト（限定解除・薬機法チェック・特商法画面）と集客単価。
- 一次ソースでは確認できなかったが、クリニックの顧客獲得単価（CPA）が金融系並み（8,000〜20,000円以上）であることと、AGA月額3,000〜12,000円×継続という単価構造から、送客モデル（比較サイト・予約アプリ）が成立しているのは整合的。
- 2026年9月以降、LINEヤフー経由のED/包茎広告は実質的に「クリニック名＋施術名」しか言えなくなるため、男性美容クリニックの集客はSEO・比較メディア・予約アプリ依存が強まる。

### Gaps
- AGAクリニックCPA（1〜3万円とされる）、脱毛CPA、美容医療比較サイトの送客手数料率、トリビュー/キレイパスの正式手数料は公開一次ソースを確認できず（検索枠切れ・ASPログイン必要）。
- 「メイリー」は特定できず。
- Google広告の「美容整形」を日本で制限するポリシー条項（restricted）は本文に見当たらず（Healthcareページ日本節は薬局・遠隔医療・OTCのみ）。
- 美容クリニックの集客コストベンチマーク（業界レポート）は未取得。

---

## (c)-1 お金・金融不安：金商法／金融サービス提供法／貸金業法・弁護士法／保険募集／税理士法／特商法／消費者庁処分

### Takeaway
「個別銘柄・売買タイミングの有料助言」は投資助言・代理業の登録が必要で、不特定多数が随時購入できる書籍・雑誌・ソフトのみが例外。金融庁はSNS・マッチングアプリ経由の投資勧誘に注意喚起を更新（2025年4月）。Stripe日本は「投資・暗号資産・転売・ドロップシッピングで利益を得る方法のコンサル／情報／ツール」を日本固有の制限業種に指定している。副業・コンサル系は消費者庁が2025〜2026年に3社を消費者安全法38条で名指し公表（株式会社和、合同会社オアシスら、合同会社PLANET）。

### Cited Findings
**金商法（投資助言・代理業）**
- 監督指針: 投資助言業は「不特定多数の者を対象として、不特定多数の者が随時に購入可能な方法により、有価証券の価値等又は金融商品の価値等の分析に基づく投資判断…を提供する行為」には当たらない。店頭販売され誰でも自由に随時購入できる新聞・雑誌・書籍、店頭・DL販売の分析ソフトは登録不要。ただし投資助言業者に直接申し込まないと買えないレポート、使用中に継続的に投資データを供給するソフトは登録が必要になり得る — [行政書士法人シグマ 監督指針解説](https://www.shigyo.co.jp/kyoninka/toushijyogen/jyogen_kaitousinai.html)
- 弁護士見解（2020年頃）: 会員向け有料サロンやメルマガで銘柄推奨・ファンド推奨・投資タイミング助言を無登録で行うことは違法行為に該当 — [CoinPost](https://coinpost.jp/?p=154943)
- 財務局警告例: 株式会社LINQX（2022年6月、「話題株セレクト」でネット経由の投資顧問契約勧誘）、株式会社ダイバースリンク（2022年9月、「富士」）、株式会社産業と経済（令和8年3月13日） — [関東財務局 (LINQX)](https://lfb.mof.go.jp/kantou/rizai/pagekthp033000205.html), [関東財務局 (ダイバースリンク)](https://lfb.mof.go.jp/kantou/rizai/pagekthp033000391.html), [関東財務局 (産業と経済)](https://lfb.mof.go.jp/kantou/rizai/pagekthp033000210.html)
- 近畿財務局警告: 登録業者の名義を使った無登録者の投資助言。「登録業者であっても、金融庁・財務局が、その業者の信用力等を保証するものではありません」 — [近畿財務局](https://lfb.mof.go.jp/kinki/content/071/pagekinkihp027000164.html)
- 金融庁注意喚起（2023年1月6日公表、2025年4月17日更新）: SNS・マッチングアプリで知り合った者や著名人を騙る者からの暗号資産・FX投資勧誘、LINEグループ誘導、少額利益を見せてから高額入金要求、出金時の手数料・税金名目請求。取引前に「金融事業者一括検索」で登録確認を — [金融庁 SNS投資勧誘注意喚起](https://www.fsa.go.jp/ordinary/chuui/sns.html)
- 金融庁注意喚起一覧: 無登録業者名公表、「無登録業者との取引は高リスク」、「FX取引・暗号資産投資の勧誘」、バイナリーオプション、合同会社社員権勧誘、証券会社・日証協を騙る偽SNS広告 — [金融庁 注意喚起一覧](https://www.fsa.go.jp/ordinary/chuui/chuui.html)
- 国会議員ブログ: 課金制サイトは金融庁が中に入れず取締りが不十分との指摘（個人の見解） — [アゴラ (音喜多駿)](https://agora-web.jp/?p=243077)
- 松井証券アフィリエイト規約: 外務員登録のない者は投資勧誘・個別商品説明不可 — [松井証券](https://www.matsui.co.jp/utility/etc/affiliated.html)

**決済プラットフォームの金融・情報商材ポリシー**
- Stripe日本固有の制限業種: 「金融商品や暗号資産の取引や投資、再販ビジネスまたはドロップシッピングビジネスの運営によって利益を得る方法に関するガイダンス、情報、またはツールを提供するコンサルティングサービスまたはアドバイザリーサービス」。禁止業種に「無限連鎖講（ねずみ講またはマルチ商法）」「コミッションや勧誘に応じた販売を行うマルチ商法サービス」「一攫千金商法」（少ない労力で高収益を偽る投資オファー等）。「投資および仲介業務」「貸付」「送金」は制限業種 — [Stripe 日本](https://stripe.com/jp/legal/restricted-businesses)

**特商法・消費者庁**
- 2025-06-26 注意喚起: 株式会社和。2024年7月以降、SNSのアンケート型副業広告→「アフィリエイトで初心者でも簡単に稼げる」としてサポートプラン勧誘。「このプランなら、月50万が当たり前になる」「儲けが出なければ返金保証がある」。断定的判断の提供で消費者安全法38条1項公表 — [消費者庁 (2025-06-26)](https://www.caa.go.jp/notice/entry/042732/)
- 2025-12-19 注意喚起: 合同会社オアシスら。求人サイトの「データ入力・完全在宅・未経験OK」求人→面接で「WEBマーケティング」へ誘導→高額コンサル契約。断定的判断の提供 — [消費者庁 (2025-12-19)](https://www.caa.go.jp/notice/entry/044502/)
- 2026-06-12 注意喚起: 合同会社PLANET（マッチングアプリ→コンサル契約→消費者金融借入） — [消費者庁 (2026-06-12)](https://www.caa.go.jp/notice/entry/046534/)
- 2024-03 行政処分: 株式会社Historia（「ENTRE PLACE Academy」ビジネススクール、訪問販売、勧誘・申込受付・契約締結の一部停止） — [消費者庁 (036765)](https://www.caa.go.jp/notice/entry/036765/)
- 2024-09-05: 株式会社即決営業（電話勧誘販売、営業能力向上の商品・研修、3か月停止） — [消費者庁 (039195)](https://www.caa.go.jp/notice/entry/039195/)
- 2025-01-23: 株式会社ディプセル及び株式会社ウィリング（電話勧誘販売、滞留在庫アソートボックス販売＋フリマ販売サポート役務、3か月停止） — [消費者庁 (040837)](https://www.caa.go.jp/notice/entry/040837/)
- 2025-12-25: アドネス株式会社（電話勧誘販売、行政処分。内容未確認） — [消費者庁 執行状況2025](https://www.caa.go.jp/notice/enforcement/2025/)
- 国民生活センター「情報商材」相談: 2023年6,256件→2024年4,163件→2025年2,623件。マッチングアプリの知人からの投資講座教材、SNS広告→Web面談→サポート契約、在宅ワーク検索→競馬情報サイト→高額サポート、購入後のコンサル・セミナーへのアップセル、複数貸金業者からの借入 — [国民生活センター](https://www.kokusen.go.jp/soudan_topics/data/infoproducts.html)
- 特商法通信販売: 最終確認画面表示義務（12条の6）、定期購入条件の明示義務、解除妨害の不実告知禁止（13条の2）、誤認による取消権（15条の4） — [特商法ガイド](https://www.no-trouble.caa.go.jp/what/mailorder/)

### Inferences
- 「触らない境界」: 無登録での個別銘柄・タイミング助言（有料サロン・LINEグループ・メルマガ）、FX/暗号資産の勧誘代理、バイナリーオプション、自動売買シグナル販売（データ継続供給型ソフトは登録対象）、債務整理の紹介料受領・交渉代行（弁護士法72条）、保険募集（登録なし）、具体的税務相談（税理士法52条）、「月50万が当たり前」型の断定的判断。
- 登録不要で成立する「合法ゾーン」は (1) 書籍・雑誌・誰でも買える動画講座（一般的な金融リテラシー）、(2) 登録業者（証券・保険・貸金・弁護士事務所）へのアフィリエイト送客、(3) 金融サービス仲介業の登録。Stripe日本が「稼ぎ方コンサル」を制限業種にしているため、副業・投資ノウハウ販売はStripe審査で落ちる前提で設計する必要がある。
- 消費者庁の執行は特商法処分（事業者別）より「消費者安全法38条公表」（名指し）が副業・コンサル系の主戦術になっており、2024年11月〜2026年6月で副業/コンサル/マッチングアプリ型が3件。

### Gaps
- 金商法197条の2の罰則（5年以下の懲役/500万円以下の罰金）、投資助言・代理業の営業保証金500万円等の登録要件は一次ソース取得失敗（e-Gov API・解説ページの該当部分が未読）。
- 弁護士法72条・77条、税理士法2条・52条・59条の条文はe-Gov取得失敗（JSレンダリング）。条文番号は一般知識ベースで記載しており要確認。
- 金融サービス仲介業（2021年11月施行、2025年の法律名称変更）の公式ページは404で未取得。
- 保険業法の保険募集人登録、貸金業法に関する一次資料は未取得。
- 2024〜2025年に投資系オンラインサロン運営者の刑事摘発（逮捕）があったかは確認できず（検索結果は財務局警告のみ）。
- 消費者庁が2023年5月に公表した「業務提供誘引販売業者8事業者」処分の個別内容は未取得。
- note/Brain/Udemyの投資・副業コンテンツポリシーは取得失敗（note規約403）。

---

## (c)-2 お金：広告プラットフォーム認証とアフィリエイト経済

### Takeaway
Google Adsの金融サービス認証（規制当局登録の提出）の対象国リスト40か国に日本は含まれていない（2026年10月時点）。Metaは「一部の国では規制当局のライセンスが必要」とするのみで、日本の明示的な金融広告主認証は確認できず（報道では、Metaは2024〜2025年に日本政府の広告主本人確認義務化を恐れて「事後対応型」の集中取締りで回避した）。アフィリエイト単価は公開一次ソースが乏しく、確認できたのは楽天証券500円と業界CPAレンジのみ。

### Cited Findings
- Google Ads 金融サービス認証（規制当局と施行日）: 対象40か国＝オーストラリア、ブラジル、ドイツ、インド、シンガポール、韓国、台湾、タイ、英国、EU各国等。日本は未掲載 — [Google 金融サービス認証 対象地域](https://support.google.com/adspolicy/answer/15332527), [同 日本語版](https://support.google.com/adspolicy/answer/12390454?hl=ja)
- Google Ads 金融商品ポリシー: バイナリーオプション禁止、クレジット修復禁止、個人ローンは返済期間61日以上のみ、CFD/FXは認可業者＋Google承認が必要でシグナル提供LPは不承認、債務整理（debt management/settlement）は一部地域で認証制、暗号資産は地域別要件 — [Google Ads Financial products](https://support.google.com/adspolicy/answer/2464998)
- 2018年、Googleは規制された暗号資産交換業者に限り日本と米国で広告を許可（国ごとにGoogle認証） — [giga.law](https://giga.law/daily-news/2018/9/25/google-to-allow-ads-from-regulated-cryptocurrency-exchanges)
- Meta 金融・保険: 「Targeting some countries with a financial product or service ad requires a license from the relevant regulatory authorities」（国名の列挙なし）。ペイデイローン・バイナリーオプション・ICO・90日以下の短期ローン・CFD・ペニーオークション禁止。クレカ・ローン・保険広告は18+必須。広告主は事業・個人の本人確認を求められる場合あり — [Meta Financial products](https://transparency.meta.com/policies/ad-standards/restricted-goods-services/financial-services/)
- 内部文書報道（2026年1月）: Metaは日本が全広告主の本人確認を義務化すると恐れ、違反広告量を減らす集中取締りを実施し、本人確認制の導入ではなく「reactive only」の姿勢を採用。日本は恐れていた厳格な本人確認規則を導入しなかった。Metaは「advertiser verification is not a silver bullet」と反論 — [feedbagel (Reuters報道の転載)](https://feedbagel.com/post/meta-developed-strategy-to-avoid-advertiser-verification-requirements-amid-scam-), [MediaNama](https://www.medianama.com/2026/01/223-meta-playbook-delay-action-scam-ads-internal-documents/)
- Metaはオーストラリアで金融サービス広告主にAFSL番号等の検証を義務化（「Paid for by」表示） — [Financial Newswire (AU)](https://financialnewswire.com.au/investment/scam-crackdown-meta-to-ban-unverified-financial-services-ads/)
- 日本の偽投資広告の99%がLINEへ誘導する設計との報道、政府はプラットフォームに未知アカウント追加時の警告表示を要請 — [Asia News Network](https://asianews.network/99-of-alleged-fake-investment-ads-in-japan-designed-to-lure-victims-to-line/)
- Metaは2024年10月、顔認証で著名人なりすまし広告を検出するテストを開始（日本） — [Meta Japan ニュース](https://about.fb.com/ja/news/2024/)
- 楽天証券アフィリエイト 1件500円（掲載時点） — [楽天証券](https://www.rakuten-sec.co.jp/smartphone/service/affiliate.html)
- 業界別CPA: 金融 8,000〜20,000円、人材 10,000〜25,000円（登録・応募のハードルで高単価傾向）、EC 5,000〜12,000円 — [mobinc](https://mobinc.jp/media/2025/12/28/cpa-meaning-calculation-guide/)
- 証券口座開設の運用型広告CPA実績8,000円（目標12,000円） — [StockSun](https://stock-sun.com/example/ad/shouken-kokyakutanka/)
- 転職エージェントの企業側成功報酬は年収の30〜45%（アフィリエイト単価とは別） — [リクルート ダイレクトスカウト](https://directscout.recruit.co.jp/biz/guide/article/2982/)
- 司法書士の任意整理費用: 着手金2〜5万円＋報酬金2〜5万円＋減額報酬（依頼者負担。アフィリエイト単価ではない） — [imitsu](https://imitsu.jp/cost/judicial-scrivener/article/debt-consolidation)

### Inferences
- 日本では「金融広告の出稿に規制当局登録の提出が必須」という制度上の壁がGoogle/Metaに（2026年10月時点で）存在しないため、無登録のアフィリエイト・メディアでも証券・クレカ・保険の広告主案件に出稿・送客自体は可能。ただし広告主側（松井証券規約）が外務員登録のない者の勧誘・個別説明を禁じるため、「比較・一般情報」に表現を留める必要。
- 広告主CPAが8,000〜20,000円（金融）・10,000〜25,000円（人材）であることから、アフィリエイト報酬も同水準以下に設定される構造。依頼にあった「証券5,000〜15,000円、保険相談1〜2万円、転職2〜5万円、債務整理高額」というレンジはこの業界CPAと整合するが、公開一次ソースでの裏取りはできなかった。
- 「お金」カテゴリの最も安全な収益経路は「登録業者への送客アフィリエイト＋一般的な金融教育コンテンツ」。自社で助言・仲介・債務相談に踏み込むと即座に登録制（金商法・金サ法・弁護士法）に入る。

### Gaps
- 証券口座・クレカ・保険相談・転職・債務整理のASP別アフィリエイト単価（A8/afb/もしも）は公開一次ソースなし（ログイン必要・検索枠切れ）。
- Meta Business Help「金融サービスの広告主に影響を及ぼす可能性がある認証要件」ページ本文は取得できず（タイトルのみ）。日本の対象可否は未確認。
- Google Ads「債務整理」の日本での認証要否（answer/2464998の地域リスト）は未確認。
- note/Brain/Udemyの投資・副業コンテンツの可否・手数料は未取得。

---

## 三カテゴリ比較（参入障壁・決済可否・広告可否・法的リスク・粗利・プラットフォーム依存）

### Takeaway
性は「法律より決済」、美容は「免許より表現」、お金は「表現より登録」がボトルネック。小規模事業者にとって最も回収しやすいのは美容（決済・広告が通る）、最も粗利率が高いのは性（プラットフォーム委託で80〜90%）、最も単価が高いのはお金（送客CPA 8,000〜25,000円）だが登録制の壁が最も硬い。

### Cited Findings
（各セルの根拠は上記各節の出典を参照）

| 軸 | (a) 性・セクシャルウェルネス | (b) 美容・外見 | (c) お金・金融不安 |
|---|---|---|---|
| 参入障壁 | **法的には低**（映像送信型は警察署へ届出のみ、出会い系は公安委員会届出＋年齢確認）。**実務的には高**（Visa/MC加盟店登録VIRP Tier1、US$500＋年次、本人確認・モデレーション・月次報告） | **低**（免許不要。ただし医療広告GL・薬機法56効能・特商法特定継続的役務の表現／契約設計コスト） | **中〜高**（一般情報・書籍は登録不要。個別助言＝投資助言業登録、仲介＝金サ法登録、債務相談＝弁護士法72条、保険＝募集人登録、税務＝税理士法） |
| 決済可否 | **Visa/MC: 事実上不可**（2022〜2025年にDMM/DLsite/ニコニコ/Fantia/とらのあな停止）。Stripe: アダルトサービス禁止・出会い系は制限。**JCB・コンビニ・プリペイド・プラットフォーム経由（12.5〜20%）** | **可**（Stripeで化粧品は非制限、遠隔医療・医薬品は制限＝審査あり。通常3〜4%） | **条件付き可**（Stripe日本: 投資・暗号資産・転売で稼ぐ方法のコンサル／情報／ツールは制限業種、ねずみ講・一攫千金は禁止。通常の有料コンテンツ・送客は可） |
| 広告可否 | **ほぼ不可**（Meta: 快楽目的製品禁止、健康目的ED/避妊/潤滑剤は18+で可、出会い系は事前書面許可。Google: セックストイは中程度制限。X: 広告不可・投稿は可。LINEヤフー: 2026年9月からED/包茎広告の表現を厳格制限） | **可・条件付き**（Meta: 美容施術18+、ビフォーアフター可、劣等感表現禁止。Google: 遠隔医療は厚労省登録/LegitScript＋Google認証。医療広告GL: 体験談禁止・BA写真は併記条件・限定解除4要件） | **可・条件付き**（Google/Metaとも日本は金融認証対象国リストに未掲載〈2026-10〉。バイナリー・クレジット修復・ペイデイ禁止。クレカ・ローン・保険は18+） |
| 法的リスク | **高**（刑法175条: 2年以下の拘禁刑/250万円。AV新法: 1か月/4か月/1年ルール。2025風営法改正: 無許可営業 法人3億円、売掛回収目的の性風俗勧誘 6月以下/100万円。出会い系規制法の届出・年齢確認） | **中**（薬機法66条違反に課徴金〈2021年8月〉。景表法ステマ告示〈2023年10月〉、2024年に医療法人へ初の措置命令。特商法通販処分は2024〜2025年ほぼ美容クリーム通販で6か月停止＋役員禁止命令。2025年医療法改正で美容医療機関に報告義務） | **高**（無登録投資助言は金商法違反。消費者庁が2025〜2026年に副業・コンサル・マッチングアプリ型を3社名指し公表。国民生活センター情報商材相談は年2,600〜6,300件） |
| 粗利 | **高**（プラットフォーム委託で80〜87.5%、FANZAアフィリエイト最大70%。独自決済はアダルトPSP手数料〜10%＋保証金で粗利圧縮） | **中**（広告主CPA 8,000〜20,000円水準で送客。D2C化粧品は定期購入規制対応コスト。AGA等は月額3,000〜12,000円×継続のLTV） | **高単価**（金融CPA 8,000〜20,000円、人材10,000〜25,000円。ただし証券口座アフィリエイトは楽天証券で1件500円の例もあり案件差大） |
| プラットフォーム依存 | **極めて高**（DLsite/FANZA/Fantia/myfansなど決済と年齢確認を肩代わりするプラットフォームに事実上依存。JCB一社依存リスク） | **中**（トリビュー〈170万DL・GMV250億円〉、キレイパス等の予約アプリが台頭するが自社サイト＋SEO＋Meta/Google広告で独立運営可能） | **中〜高**（登録業者のアフィリエイト案件とASPに収益を依存。Stripe審査・Meta/Google広告ポリシーが「稼ぎ方」訴求を制限するため、独自課金は銀行振込・コンビニ・国内PSPに寄る） |

### Inferences
- 推奨ポジション（小規模・合法前提）: 性＝「自作コンテンツの委託販売＋FANZA/DMMアフィリエイト」または「性の健康（ED/避妊）の医療送客」、美容＝「限定解除を満たすクリニック比較／予約送客＋薬機法準拠D2C」、お金＝「登録不要の一般教育コンテンツ＋登録業者への送客」。三者とも「自前で決済を握る」ほど規制とブランドルールの直撃を受ける。
- 三カテゴリ共通の最新トレンド: (1) 消費者安全法38条による「名指し公表」が副業・美容サロン・マッチングアプリ型に広がる、(2) プラットフォーム規約（カードブランド・LINEヤフー・Google Play AI）が法律より先に表現を縛る、(3) 2025〜2026年の法改正（風営法・医療法・AV新法経過措置終了）で既存事業者のコンプライアンスコストが上がり、情報公開を扱うメディアには機会。

### Gaps
- 粗利欄の「アダルトPSP手数料7〜15%」は一次ソースで確認できず（Forbes報道の「最大10%」のみ）。
- 各カテゴリのチャージバック率・不承認率の実データは未取得。
- 本調査はWeb検索枠切れのため、依頼にあった以下は未着手: 国民生活センターの恋愛コンサル事例、景表法「増大」措置命令、迷惑防止条例、金融サービス仲介業一次資料、note/Brain/Udemy規約、TikTok広告、AI companionのWeb課金実例、Pairs/タップルCPA、AGA/脱毛/クレカ/保険/転職/債務整理のASP単価。
