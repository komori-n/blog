---
author: komori-n
draft: true
categories:
  - プログラミング
  - 将棋
date: "2021-12-30T16:56:08+09:00"
guid: https://komorinfo.com/blog/?p=1476
id: 1476
image: https://komorinfo.com/wp-content/uploads/2021/12/image-6.png
og_img:
  - https://komorinfo.com/wp-content/uploads/2021/12/image-6.png
permalink: /mate-solver-pv-search/
tags:
  - df-pn algorithm
  - 詰将棋
title: 詰将棋ソルバーにおける最善応手列（PV）の探索
url: mate-solver-pv-search/
---

**<span class="has-inline-color has-red-color">2022/1/26追記</span>**

以下に書いてある情報は嘘解法なのでKomoringHeights最新版では採用していない。詳しくはKomoringHeights最新版のソースを参照。

懺悔の意味を込めて記事自体はそのままにしている。

---

過去3回ぐらいバグり散らかしていたので忘れずにメモ。

## 概要

df-pnアルゴリズムをベースとする詰将棋ソルバーは、局面の詰み／不詰を高速に判定することができる。しかし、探索時は探索深さをあまり意識せずに探索を行うため、双方が最善を尽くした時の詰み手順（最善応手列；PV）を得るには追加の探索が必要になる。

詰将棋に対する詰み手順については、日本将棋連盟の公式サイトにてルールが記載されている。

> 1\. 攻め方（先手）が玉方（後手）の玉を詰ますのが目的。
> 2\. 攻め方は必ず王手をかける（玉方は必ず王手をはずす）。
> 3\. 玉方は盤上と攻め方の持駒以外すべての駒（ただし玉は除く）を合駒として使用できる。
> 4\. 玉方は最善を尽くし、最も長く手数がかかるように逃げる。
> 5\. 玉方は無駄な合駒をしない。
> 6\. その他は指し将棋のルール通り。二歩、打ち歩詰め、行き所のない駒、連続王手の千日手はいけない。<span class="easy-footnote-margin-adjust" id="easy-footnote-1-1476"></span><span class="easy-footnote">[<sup>1</sup>](https://komorinfo.com/blog/mate-solver-pv-search/#easy-footnote-bottom-1-1476 "『最後の審判』のように、打ち歩詰めと連続王手の千日手が両方同時に発生した場合、その局面が詰みかどうかは定義されていない")</span>
>
> <cite>[詰将棋・次の一手｜日本将棋連盟](https://www.shogi.or.jp/tsume_shogi/)</cite>

このうち、5. の「玉方は無駄な合駒をしない」はルールが曖昧で大変難しい問題なので、本ページでは扱わない<span class="easy-footnote-margin-adjust" id="easy-footnote-2-1476"></span><span class="easy-footnote">[<sup>2</sup>](https://komorinfo.com/blog/mate-solver-pv-search/#easy-footnote-bottom-2-1476 "詰将棋の中には、無駄合かどうか人によって意見が分かれる局面が存在する。例えば <a href="http://kazemidori.fool.jp/?p=8466">詰将棋のルール論争(7)　無駄合 | つみき書店</a> や <a href="http://exlight.net/shogi/log/20131120/index.html">詰将棋における無駄合いNGの妥当性</a> を参照。")</span>。有効合・無駄合を区別せず、できる限り手数が伸びるような手を選ぶことを考える。

また、攻め方はできるだけ詰み手数が短くなるように手を選ぶことにする。

df-pnアルゴリズムにより探索を行う場合、置換表サイズを減らすために、最善手や詰み手数を置換表に登録しない場合がしばしば存在する。その場合、df-pn探索終了後に改めて最善応手列（PV）の復元を行う必要がある<span class="easy-footnote-margin-adjust" id="easy-footnote-3-1476"></span><span class="easy-footnote">[<sup>3</sup>](https://komorinfo.com/blog/mate-solver-pv-search/#easy-footnote-bottom-3-1476 "df-pnアルゴリズムの性質から、探索中に保存した詰み手順が最適な詰み手順になるとは限らない。N手詰の局面でN手よりも短い詰み手順を返してしまう可能性があるので要注意")</span>。本ページでは、最善応手列の探索方法について考える。

以下では、局面としてすべてdf-pn探索により詰みだと判明している局面だけを考える。

## 詰み手数

まず、以下の局面グラフを考える。

<div class="wp-block-image"><figure class="aligncenter size-full">![](https://komorinfo.com/wp-content/uploads/2021/12/image.png)<figcaption>局面グラフの例。雲マークはグラフの省略を表す。</figcaption></figure></div>Aを始点として、攻め方はできるだけ最短手数で詰むように、受け方はできるだけ手数が長くなるような手を選択すると、詰み手数は以下のようになる。

<figure class="wp-block-table is-style-vk-table-border-top-bottom">| 局面 | 子局面 | 詰み手数 |
|---|---|---|
| A | B(18)、C(5) | 5 |
| B | D(17) | 18 |
| C | (3) | 4 |
| D | E(∞)、F(16) | 17 |
| E | A(loop) | ∞ |
| F | (15) | 16 |

<figcaption>Aを始点とした各ノードの小局面と詰み手数。 カッコ内は詰み手数。 「詰み手数=∞」は不詰を表す。</figcaption></figure>よって、Aは5手詰となる。

これだけなら簡単だが、探索結果を再利用しようとすると途端に難しくなる。例えば、Dを始点として詰み手数を考え直すと、以下のようになる。

<figure class="wp-block-table is-style-vk-table-border-top-bottom">| 局面 | 子局面 | 詰み手数 |
|---|---|---|
| A | B(18)、C(5) | 5 |
| B | **D(loop)** | **∞** |
| C | (3) | 4 |
| D | **E(6)**、F(16) | **7** |
| E | **A(5)** | **6** |
| F | (15) | 16 |

<figcaption>Dを始点とした各ノードの小局面と詰み手数。カッコ内は詰み手数。「詰み手数=∞」は不詰を表す。</figcaption></figure>Aを始点としたときと比較して、B、D、Eの詰み手数が変化している。これは、探索局面のループが原因である。探索中に同じ局面に戻ってきた場合、その手順は不詰だと判定してしまうため、始点のとり方によって各局面の詰み手数が変わってしまうのである。

このように、**詰み手数は探索経路に依存する**概念のため、単純に「局面→詰み手数」の置換表を用いて探索すると痛い目を見ることになる<span class="easy-footnote-margin-adjust" id="easy-footnote-4-1476"></span><span class="easy-footnote">[<sup>4</sup>](https://komorinfo.com/blog/mate-solver-pv-search/#easy-footnote-bottom-4-1476 "3敗")</span>。しかし、置換表なしで詰み手順を求める場合、ループを多数含むような長手数の詰将棋では探索時間が指数関数的に増加してしまう。そのため、詰み手数が探索経路に依存したものかどうかを考慮して置換表を用いる必要がある<span class="easy-footnote-margin-adjust" id="easy-footnote-5-1476"></span><span class="easy-footnote">[<sup>5</sup>](https://komorinfo.com/blog/mate-solver-pv-search/#easy-footnote-bottom-5-1476 "df-pnアルゴリズムでも同様のループ問題が発生する。df-pnアルゴリズムにおけるループの回避方法は <a href="https://komorinfo.com/blog/and-or-tree-ghi-problem/">詰将棋ソルバーにおけるGHI問題対策 | コウモリのちょーおんぱ</a> を参照。")</span>。

## 置換表

詰み手数が探索経路により影響を受けるのはループが発生している時だけである。逆に言うと、ループがない場合は詰み手数は探索経路に依存しないため、「局面→詰み手数」の置換表により過去の別経路の探索結果を安全に再利用することができる。

先ほどの例の場合、Aを始点とした探索では、A、C、Fは経路非依存の詰み手数が得られるのに対し、B、D、Eは「Aに戻ると不詰」という情報を使っているので経路依存の詰み手数となっている<span class="easy-footnote-margin-adjust" id="easy-footnote-6-1476"></span><span class="easy-footnote">[<sup>6</sup>](https://komorinfo.com/blog/mate-solver-pv-search/#easy-footnote-bottom-6-1476 "少しややこしいが、ループの始点Aは経路非依存の結果が得られる")</span>。

<div class="wp-block-image"><figure class="aligncenter size-full">![](https://komorinfo.com/wp-content/uploads/2021/12/image-5.png)<figcaption>Aを始点とした探索を行う場合、E、D、Bの詰み手数は経路依存。</figcaption></figure></div>より一般的な書き方をすると、以下のようになる。

- 深さXの探索中に深さD（D&lt;X）の局面へのループを発見した場合、深さ D+1、D+2、…、X の探索結果は置換表に書かない
  - 逆に言うと、深さ 0、1、…、D と深さ X+1、X+2 の探索結果は置換表に書いてもよい
