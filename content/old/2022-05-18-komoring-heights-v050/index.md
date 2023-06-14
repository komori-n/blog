---
author: komori-n
draft: true
categories:
  - プログラミング
  - 将棋
date: "2022-05-18T20:16:26+09:00"
guid: https://komorinfo.com/blog/?p=1613
id: 1613
image: https://komorinfo.com/wp-content/uploads/2022/02/cropped-25806739-1-1.png
og_img:
  - https://komorinfo.com/wp-content/uploads/2022/02/cropped-25806739-1-1.png
permalink: /komoring-heights-v050/
tags:
  - C/C++
  - df-pn algorithm
  - 詰将棋
title: 難解作品が解ける詰め将棋エンジン KomoringHeights v0.5.0 を公開した
url: komoring-heights-v050/
---

[KomorintHeights v0.5.0](https://github.com/komori-n/KomoringHeights/releases/tag/kh-v0.5.0) で使われている技術について解説する。

## 主な変更点

詰将棋エンジンの実力を測る有名な指標に一つとして

<meta charset="utf-8"></meta>[コンピュータ向け超難解詰将棋作品集](http://toybox.tea-nifty.com/memo/2005/05/post_3535.html) が知られている。これは、既存の詰将棋のうち特にコンピュータ詰将棋エンジンにとって解きづらい問題だけを集めた問題集で、KomoringHeights v0.4.0 では全13問中5問ほどしか解くことができなかった。v0.5.0 では難解詰将棋対策を一通り実装したため、全13題が解けるようになった。 せっかくなので、最新版 v0.5.0 における解答時間を測定した。測定環境は以下のとおりである。

- Engine｜KomoringHeights v0.5.0
- CPU｜Amazon EC2 r5.xlarge <span class="easy-footnote-margin-adjust" id="easy-footnote-1-1613"></span><span class="easy-footnote">[<sup>1</sup>](https://komorinfo.com/blog/komoring-heights-v050/#easy-footnote-bottom-1-1613 "時間測定を繰り返したせいで財布がやや散華した")</span>
- Compiler｜clang 11.1.0
- USI_Hash｜29000 \[MB\]

計測結果は以下のようになった。

<figure class="wp-block-table">| 問題 | 作為手数 | 解答時間（s） | 探索局面数 | 出力手数 |
|---|---|---|---|---|
| 驚愕の曠野 | 59 | 43270 | 29991173951 | 63 |
| 木星の旅 | 411 | 4038 | 2198487548 | 411 |
| メタ新世界 | 941 | 199796 | 70662557472 | 965 |
| Fairway | 611 | 459 | 220854295 | 629 |
| 乱 | 451 | 407 | 237235214 | 451 |
| メガロポリス | 515 | 6413 | 3419107074 | 517 |
| 裸玉(38) | 35 | 3295 | 2020189021 | 45 |
| 谷口均29手 | 29 | 2201 | 1568746903 | 45 |
| 田島289手 | 289 | 5313 | 3052945562 | 303 |
| 明日香 | 703 | 8313 | 4603885643 | 735 |
| 新桃花源 | 1205 | 460 | 272600747 | 1213 |
| チップイン | 111 | 224 | 150875151 | 125 |
| 赤兎馬 | 525 | 1256 | 735483679 | 535 |
| （参考）墨酔17番 | 51 | 3499 | 2528353366 | 71 |

</figure>表が示す通り、超難解作品集をすべて解けた。特に、『<meta charset="utf-8"></meta>驚愕の曠野』、『メタ新世界』以外の作品はすべて3時間以内に詰みを示せた<span class="easy-footnote-margin-adjust" id="easy-footnote-2-1613"></span><span class="easy-footnote">[<sup>2</sup>](https://komorinfo.com/blog/komoring-heights-v050/#easy-footnote-bottom-2-1613 "『メタ新世界』だけやけに時間がかかっているので、まだ改善の余地がありそう")</span> <span class="easy-footnote-margin-adjust" id="easy-footnote-3-1613"></span><span class="easy-footnote">[<sup>3</sup>](https://komorinfo.com/blog/komoring-heights-v050/#easy-footnote-bottom-3-1613 "特に印象に残ってる問題について感想を述べたい。</p>

<ul><li>新桃花源｜二重カウントによる証明数のオーバーフローが多発した。ミクロコスモスよりも難しいが、難解詰将棋の中では簡単なほう。</li><li>明日香｜1筋の連続合駒が意外と読みづらい。合駒の遅延展開を導入するきっかけになった。</li><li>メガロポリス｜PostSearchの不具合を踏みまくった。左半分の玉方の応手が指数関数的に増加するため、対策を入れないとPostSearchの探索が一生終わらない。</li><li>驚愕の曠野｜そもそも最初の4手がなくても難しい。最初の4手の紛れがかなり多く、紛れもなく超難問。</li><li>メタ新世界｜最も苦戦した問題。仕組み的にはメガロポリスに似ているが、こちらの方が数段難しく感じた。この問題でもPostSearchのバグをたくさん踏んで頭を抱えた。</li></ul>

<p>")</span>。

以下では v0.5.0 で新たに導入した技術についてざっと解説する。

## 技術解説

### 合流検出（SNDA）

v0.3.0のころからずっと先延ばしにしていた、局面の合流検出（SNDA）を実装した。

v0.4.1 では、一部の詰将棋でpn/dnがオーバーフローする事象が発生していた。pn/dnは64bit変数なので現実的な時間内でオーバーフローすることはあまりないのだが、手順中に複数回合流が発生する詰将棋ではpn/dnが二重、四重、八重、…と指数関数的に重複カウントされてしまい、あっという間にオーバーフローしてしまうことがあった。特に、『メガロポリス』や『<meta charset="utf-8"></meta>新桃花源』のような、玉方手番でどの手を選んでも手順があまり変わらないタイプの詰将棋でこのような問題が頻発していた。

そこで、合流を検出して局面の過小評価を防ぐ仕組みを導入した。v0.4.1 で解けなかった問題が v0.5.0 で解けるようになったのは、この機能の存在が大きい。合流検出および二重カウントの防止方法については以下の記事の「先行研究」を参照。

<figure class="wp-block-embed is-type-wp-embed is-provider-コウモリのちょーおんぱ wp-block-embed-コウモリのちょーおんぱ"><div class="wp-block-embed__wrapper">> [詰将棋探索における簡易的な二重カウント対策](https://komorinfo.com/blog/proof-number-double-count/)

<iframe class="wp-embedded-content" data-secret="4AzrHJR4Fa" frameborder="0" height="282" marginheight="0" marginwidth="0" sandbox="allow-scripts" scrolling="no" security="restricted" src="https://komorinfo.com/blog/proof-number-double-count/embed/#?secret=4AzrHJR4Fa" style="position: absolute; clip: rect(1px, 1px, 1px, 1px);" title="“詰将棋探索における簡易的な二重カウント対策” — コウモリのちょーおんぱ" width="500"></iframe></div></figure>合流検出の実装はかなり複雑だ。詰将棋探索では探索中の局面を置換表（メモリ）に保存する必要があるのだが、合流検出のためにはこれを増やす必要がある。具体的には、v0.4.1 では 1 局面あたりの置換表エントリサイズは 32 byte であったのに対し、v0.5.0 では親局面のポインタ（12 byte）と合流フラグ（8 byte）を追加で持たせているため、サイズが 56 byte（1.5倍）に膨れ上がっている<span class="easy-footnote-margin-adjust" id="easy-footnote-4-1613"></span><span class="easy-footnote">[<sup>4</sup>](https://komorinfo.com/blog/komoring-heights-v050/#easy-footnote-bottom-4-1613 "単純計算すると32 + 12 + 8 = 52 だが、8 byte 単位にするために 56 byte に切り上げている")</span>。

さらに、合流検出のアルゴリズム自体もそれほど単純ではない。合流の可能性がある局面を見つけるたびに、再帰的に局面をさかのぼって合流検出のフラグを立てに行く必要がある。1回の計算量は大したことがないが、長時間探索する場合は無視できない計算量になりうる。

これらの理由から、合流検出を実装したことでNPS（単位時間あたりの探索局面数）がかなり低下する……はずだった。しかし、置換表のデータ構造や処理の入れ替えなどの細かい改善を積み重ねたことで、v0.4.1 と比べてNPSはほとんど変わらない水準になっている。

### 合駒の遅延展開

合駒局面の展開を遅らせるようになった。

v0.5.0 では 歩→桂→香→銀→角→飛→金 の順に合駒を調べるよう修正した。歩合で詰むなら桂合、桂合で詰むなら香合、… という要領で読みを進めるため、何を合駒しても詰まない局面における探索局面数が大幅に削減された<span class="easy-footnote-margin-adjust" id="easy-footnote-5-1613"></span><span class="easy-footnote">[<sup>5</sup>](https://komorinfo.com/blog/komoring-heights-v050/#easy-footnote-bottom-5-1613 "探索順がこの順なのは、やねうら王の <code>PieceType</code> がこのような定義順になっているため")</span>。

例えばこの局面を考える。

<div class="wp-block-image"><figure class="aligncenter">![](http://sfenreader.appspot.com/sfen?sfen=9%2F7kp%2FR8%2F6P2%2F9%2F9%2F9%2Fb8%2F9%20b%20rb4g4s4n4l16p%201)<figcaption>角がよく利いていて詰まない</figcaption></figure></div>王手はしばらく続けられるものの、明らかに不詰の局面である。▲３三歩成／▲３三飛成いずれに対しても、△１一玉と引けば角がよく利いていて明確に詰まない。しかし、v0.4.1 では不詰を示すためには 22394998 局面もの探索を必要とする。これは、合駒が絡む手順において、詰むかどうか分からないような合駒を延々と読み進めるためである<span class="easy-footnote-margin-adjust" id="easy-footnote-6-1613"></span><span class="easy-footnote">[<sup>6</sup>](https://komorinfo.com/blog/komoring-heights-v050/#easy-footnote-bottom-6-1613 "この局面ではどう王手されても歩合で不詰。一般の不詰局面でも歩合だけ確かめれば不詰が示せることが多い")</span>。一方、v0.5.0 では 3587 局面の探索で不詰を読み切ることができるようになった。

### 余詰探索（PostSearch）

v0.5.0 では余詰探索が少しだけ賢くなり、解答する詰手順が少しだけきれいになった。

KomoringHeights における詰将棋探索は大きく分けて**本探索**と**余詰探索**（PostSearch）に分かれている。本探索は、与えられた局面が詰みかどうかを調べる探索で、df-pnアルゴリズムを用いる。ただ、df-pnアルゴリズムは詰みを示すことはできても最善手順を返すのは苦手であるため、本探索終了後に追加探索を行っている。

v0.5.0 ではこの余詰探索に以下の機能が追加された。

- 無駄合検出
- 探索結果の再利用
- αβ枝刈り
- 前向き枝刈り

v0.5.0における余詰探索の改善効果を最も実感できる詰将棋は『将棋図巧第99番』である。

<meta charset="utf-8"></meta>『将棋図巧第99番』は最古の煙詰（盤上の駒がすべて消える詰将棋）として有名な117手詰作品である。しかし、v0.4.1 では趣向をガン無視して<meta charset="utf-8"></meta>駒余り9枚の123手詰の手順を返していた。

<div class="wp-block-image"><figure class="aligncenter">![](http://sfenreader.appspot.com/sfen?sfen=9%2F7P1%2F4B2Gk%2F9%2F6N1%2BP%2F9%2F9%2F9%2F9%20w%20N8P2rb3g4s2n4l8p%201)<figcaption>『将棋図巧第99番』詰め上がり図（KomoringHeights v0.4.1）</figcaption></figure></div>一方、v0.5.0 では作為通りの117手詰の煙詰手順を返すようになった。特に67手目の歩合強要のための龍寄りが正しく読めるようになった。ぜひ手元で確かめてみてほしい。

なお、v0.5.0 に実装された余詰探索機能はあくまで**悪くない詰手順**を返すためのものである。任意の詰将棋で正解手順を返すほどの精度はないため過信は禁物である<span class="easy-footnote-margin-adjust" id="easy-footnote-7-1613"></span><span class="easy-footnote">[<sup>7</sup>](https://komorinfo.com/blog/komoring-heights-v050/#easy-footnote-bottom-7-1613 "例えばこの局面。</p>

<div class="wp-block-image">
<figure class="aligncenter"><img src="http://sfenreader.appspot.com/sfen?sfen=9%2F9%2F6Bnl%2F8k%2FR6p1%2F9%2F9%2F9%2F9%20b%20rb4g4s3n3l17p%201" alt=""/></figure></div>

<p>詰将棋的には ▲９四飛 までの1手詰だが、KomoringHeightsは ▲<meta charset="utf-8" />９四飛△２四金▲同角成 までの3手詰と解答する。「王手していた駒で合駒をすぐに取り返せば詰む」以外の状況は有効合と判断するためである。</p>

<p>また、N手詰に対しN手未満の手順を解答してしまうケースも存在している")</span>。

## 今後の展望（v1.0.0へ向けて）

v0.5.0 でコンピュータ向け難解詰将棋がすべて解けるようになった。次回の更新で詰将棋エンジンに必要な機能の実装が完了し、v1.0.0 として公開する見込みである。

v1.0.0 の公開に向けて残る課題は次の2つである。

- PostSearch が安定しない
- Garbage Collection の挙動が怪しい

PostSearch の不安定さについては、KomoringHeights を使い込んでいたり、ソースコードを眺めたりしたことがある方はご存知かもしれない。v1.0.0 ではちゃんと USI_Hash で確保した領域を使い、余詰探索を行えるようにしたい。そしてできれば、コンピュータ向け難解詰将棋すべてに対し作為手順を返せるようなエンジンを目指したい。

次に、Garbage Collection（GC）の挙動については、まだ全容がつかめていないが、どうも探索に致命的に悪影響を及ぼすバグが潜んでいるようである。ちょっと GC の条件を変えるだけで探索局面数が1.5倍に増えたり、解答手順が大きく変わったりと制御しきれていない部分が多い印象である。また、過去の論文では2時間程度で解けていた『メタ新世界』に1.5日かかっているためかなり改善の余地があると考えている。今後、GC の方式を工夫することで難解詰将棋に対する探索時間が大幅に削減できる……かもしれない。
