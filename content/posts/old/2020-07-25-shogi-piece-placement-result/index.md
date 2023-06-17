---
author: komori-n
categories:
  - やってみた
series:
  - 利かずの駒並べ
series_order: 2
date: "2020-07-25T17:11:23+09:00"
tags:
  - C++
  - パズル
  - 将棋
keywords:
  - 利かずの駒並べ
  - 局面図
title: 利かずの駒並べ｜実践編
relpermalink: blog/shogi-piece-placement-result/
url: blog/shogi-piece-placement-result/
description: 将棋パズル「利かずの駒並べ」に対し、計算機上で総当り探索により発見した解について説明する。
---

「利かずの駒並べ｜理論編」で解説したプログラムを用いて、双方向駒並べの探索を行った。

{{< github repo="komori-n/shogi-piece-placement" >}}

## 概要

**駒追加**は40枚の駒に何枚まで駒を足せるか、**駒成**は何枚まで成駒に交換できるかを表す。

以前から広く知られていた配置法[^1]は以下である。

[^1]: <https://mozuyama.hatenadiary.org/entry/20050710/P20050710KIKI>

- 歩4枚追加
- 桂5枚追加
- 歩3枚成
- 角1枚成
- 飛1枚成

それに対し、今回のプログラムで得られた駒配置は以下の通りである。いずれも限界まで駒追加または駒成をした結果である。結果図を眺めたらまだ駒を置けそうだったので、追加で桂馬も置けるだけ置いた。

| 駒種 | 駒追加  | 駒成      |
| ---- | ------- | --------- |
| 歩   | +歩4    | 歩成8+桂1 |
| 桂   | +桂6    | 桂成4+桂1 |
| 銀   | +銀3桂1 | 銀成4+桂4 |
| 金   | +金2桂3 | –         |
| 玉   | +玉2桂2 | –         |
| 飛   | –       | 飛成1+桂2 |
| 角   | +角2    | 角成2+桂3 |

得られた駒配置のまとめ。すべて上限値。

歩成が予想外にたくさん成らせることができて驚いた。と金の左右には駒が置けないので、歩成は4枚程度が限界だと予想していたからだ。

逆に、飛成が1枚までしかできないのも面白い。直感的には歩成8より飛成2の方が簡単そうに見えるからだ。実際のところ、飛車の斜め4マスに金が置ける事がわりと重要だったのだろう。

## 双方向駒並べ 結果

プログラムで得られた図から、以下の点を手で修正している。
（簡略化した駒を元に戻すプログラムを書くのが面倒だったので）

- 歩 → 香
- 金 → と、成桂、成銀

### 駒追加

#### +歩4

![40枚+歩4枚](http://sfenreader.appspot.com/sfen?sfen=K1S1BPBPP%2F2N1p1p1p%2F1R7%2Fg1g1PPP1G%2F4NnnP1%2FK1G1ppppP%2F3R5%2FS1P1PPPPP%2Fs1s1pllll%20b%20-%201)

#### +桂6

![40枚+桂6枚](http://sfenreader.appspot.com/sfen?sfen=SP1G1K1sP%2F2R6%2FSP1g1PPPP%2FN4NNnn%2FBP1G1pppp%2F4R4%2FBP1g1PPPP%2FN4nNnn%2FsP1K1llll%20b%20-%201)

#### +銀3桂1

![40枚+銀3桂1](http://sfenreader.appspot.com/sfen?sfen=K1S1G1LLL%2F2B2Pnnn%2FK1p1Ppppp%2F3R5%2FS1g1P1PPP%2FB3nP1pn%2Fp1G1ppP1p%2F1R7%2Fg1l1SSsss%20b%20-%201)

#### +金2桂3

![40枚+金2桂3](http://sfenreader.appspot.com/sfen?sfen=K1S1G1LLL%2F2N2PNnn%2FG1p1Ppppp%2F1R7%2FP1g1PPPPP%2FB3NNnp1%2Fs1G1ppp1g%2F3R5%2FK1g1PBSsl%20b%20-%201)

#### +玉2桂2

![40枚+玉2桂2](http://sfenreader.appspot.com/sfen?sfen=G1PBSsP1K%2F1R7%2Fg1PPP1G1K%2F2np1P3%2FK1p1PpP1P%2F7R1%2FS1PPPPP1g%2FB1NNNnn2%2Fs1pllll1K%20b%20-%201)

#### +飛

飛車は1枚も足せない。

#### +角2

![40枚+角2](http://sfenreader.appspot.com/sfen?sfen=K1BLB1LLL%2F2N1p1ppp%2F1R7%2Fg1PPS1G1G%2F2n1N2P1%2FK1sPp1P1g%2F5R3%2FS1n1P1PPP%2Fs1BPB1ppp%20b%20-%201)

### 成り駒に置き換え

#### 歩成8+桂1

![40枚（歩成8）+桂1](http://sfenreader.appspot.com/sfen?sfen=G1G1SBSBs%2F1R7%2Fg1g1%2BP1%2BP1%2BP%2F5P1P1%2FK1%2BP1PsP1%2Bp%2F3R5%2FK1%2Bp1PPPPP%2F4nNNNn%2F%2Bp1%2Bp1pllll%20b%20-%201)

#### 桂成4+桂1

![40枚（桂成4）+桂1](http://sfenreader.appspot.com/sfen?sfen=G1G1G1g1%2Bn%2F1R7%2F%2Bn1P1%2BN1SsP%2F3R5%2FS1%2Bn1PPPPP%2FB3ppppp%2FN1K6%2FB3PPPPP%2Fs1K1pllll%20b%20-%201)

#### 銀成4+桂4

![40枚（銀成4）+桂4](http://sfenreader.appspot.com/sfen?sfen=%2BS1%2BS1LBLLL%2F1R7%2FN1%2Bs1PPP1%2BS%2FB3NNnP1%2FN1G1ppppP%2F3R5%2FK1g1PPPPP%2F5pnnn%2FK1g1g1ppp%20b%20-%201)

#### 飛成1+桂2

![40枚（飛成1）+桂2](http://sfenreader.appspot.com/sfen?sfen=K1G1PPP1P%2F3Ppp2s%2F1%2BR7%2F3G1PS1P%2FK1g1g1p1p%2F7R1%2FS1NPPPP1P%2FB1NNnnn1B%2Fs1pplll1l%20b%20-%201)

#### 角成2+桂3

![40枚（角成2+桂3）](http://sfenreader.appspot.com/sfen?sfen=G1G1g1SsL%2F1R7%2F2g1PPPPP%2F%2BB3ppppp%2F3R5%2F%2BB3PPPPP%2F2K1pNNNN%2FS4pnnn%2Fs1K1P1lll%20b%20-%201)
