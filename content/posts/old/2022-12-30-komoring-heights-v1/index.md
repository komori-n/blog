---
author: komori-n
draft: true
categories:
  - プログラミング
  - ポエム
  - 将棋
date: "2022-12-30T14:06:25+09:00"
guid: https://komorinfo.com/blog/?p=1914
id: 1914
og_img:
  - https://komorinfo.com/wp-content/uploads/2022/12/image-1.png
permalink: /komoring-heights-v1/
tags:
  - C/C++
  - df-pn algorithm
  - 詰将棋
title: 安定性が向上した詰将棋エンジン『KomoringHeights v1.0.0』を公開した
url: komoring-heights-v1/
---

[KomoringHeights v1.0.0](https://github.com/komori-n/KomoringHeights/releases/tag/kh-v1.0.0) に対する詳しめのリリースノート。

## 利用者向け

### 解答手順構成の安定性向上

<div class="wp-block-image"><figure class="aligncenter size-large">![](https://komorinfo.com/wp-content/uploads/2022/12/image-3-1024x505.jpg)</figure></div>v0.5.0 の探索部は、大きく分けて**Main Search**と**Post Search**の2つに分かれていた。**Main Search**は、与えられた局面が詰みかどうかを調べる本探索である。一方、Post Searchは**Main Search**で見つけた詰み局面のグラフ構造を再探索して双方最善を尽くしたときの詰み手順を構成する探索である。

探索部が2つに分かれていた理由は、Main Searchだけでは自然な詰み手順が構成できないからだった。Main Searchでは[df-pnアルゴリズム](https://komorinfo.com/blog/df-pn-basics/)と呼ばれる詰将棋と相性が良い探索を用いていた。df-pnアルゴリズムは詰みの判定自体は高速なのだが、見つけた手が必ずしも最善手と一致するとは限らない。最善手ではない手をベースに詰み手順を構成すると、人間から見て不自然な手順になってしまう。

そのため、Main Searchの後のPost Searchで経路の再探索を行い、手順の再構成を行っていた。Post SearchはMain Searchと比べてあまり時間がかからず、Main Searchの補助的な位置づけだった。

<div class="wp-block-image"><figure class="aligncenter size-full">![](https://komorinfo.com/wp-content/uploads/2022/12/image-1.png)<figcaption>Post Searchのイメージ。
詰み（水色）／不詰（灰色）が分かっているとき、最適な手順を探す。</figcaption></figure></div>しかし、Post Searchにより手順を再構成する方法は、稀に手順の構成に失敗するケースがあった。探索失敗の原因はいくつかあり、Post Searchの千日手回避のフローで無限ループに陥ってしまったり、Garbage Collectionにより必要な探索結果が置換表から消されてしまったりなどである。このように、Post Searchを用いる手順は見た目ほど簡単ではなく、詰み手順の構成にはより高度なアルゴリズムが必要だと分かってきた。

そのため、v1.0.0ではMain Search自体を拡張して詰み手順の改良を行うようにした。Main Searchの探索において、「与えられた局面が詰むかどうか」を調べる代わりに、「与えられた局面が**M手以下で**詰むかどうか」を調べる。これにより、「**ちょうどM手**で詰むかどうか」を「M手以下で詰む」かつ「M-2手以下では詰まない」により判定できるようになった<span class="easy-footnote-margin-adjust" id="easy-footnote-1-1914"></span><span class="easy-footnote">[<sup>1</sup>](https://komorinfo.com/blog/komoring-heights-v1/#easy-footnote-bottom-1-1914 "細かい話をすると、「<strong>M手以下で詰み</strong>」には<a href="https://komorinfo.com/blog/proof-piece-and-disproof-piece/">持ち駒の優等性</a>と同様に半順序関係があり、その優等関係を探索に活用できる。具体的には、</p>

<ul><li>「M手以下で詰み」なら「M+2手以下で詰み」</li><li>「M手以下で詰まない」なら「M-2手以下では詰まない」</li></ul>

<p>が成り立つ。</p>

<p>ただし、この優等関係を真面目に実装すると置換表のメモリを一瞬で食いつぶしてしまう。というのも、1つの局面に対し</p>

<ul><li>「M手で詰み」に対するpn/dn</li><li>「M-2手で詰み」に対するpn/dn</li><li>…</li></ul>

<p>の要領でほぼ同じ内容のエントリが大量にできてしまうためだ。そのため、実際の実装では適度にごまかしを入れながらこの優等関係を活用している")</span>。

### 無駄合検知の削除

v0.5.0では無駄合を出力手順から消す機能があったが、v1.0.0では削除された。無駄合探索はPost Search内で行っていた機能で、詰将棋の一般的なルールに則り無駄な合駒を手順から消す機能だった。

v0.5.0の無駄合の判定は、さまざまな問題を抱えていた。まず、一般的な詰将棋のルールに沿っておらず、利用者の混乱を招いていた。特に、駒がたくさん余る実戦形の詰将棋では、人間的には不自然な手順を返していた。それに加え、無駄合探索の実現のために、コード的にはだいぶ険しい実装をしていた。このように、v0.5.0の無駄合探索は手間がかかる割に恩恵の少ない機能だった。

それゆえ、v1.0.0では無駄合機能を削除した。合駒が無駄合かどうかは全く考慮されず、無駄合を含めた最短手順を返す挙動に変わった。

なお、この機能削除は今後の無駄合探索の再実装を否定するものではない。今後、正しい詰将棋のルールに沿った無駄合の検出機能を実装を予定している。

## 開発者向け

実は、探索方法の変更に伴い、コードをほぼ全て書き直している。それに伴い、Doxygenコメントと単体テストの整備を行った。

### Doxygenコメント整備

<figure class="wp-block-image size-large">[![](https://komorinfo.com/wp-content/uploads/2022/12/image-1024x539.jpg)](https://komori-n.github.io/komoring-heights-docs/)</figure>全体リファクタリングのついでに、すべての公開インターフェースに最低限のDoxygenコメントを追加した。最新版に対するドキュメントは [komoring-heights-docs](https://komori-n.github.io/komoring-heights-docs/) にて公開している。この公開ドキュメントは本体リポジトリのCIで自動生成している。またローカル環境でも、`source/engine/user_engine/tests` で `make docs` を実行することで同様のドキュメントを生成できる。

### 単体テスト整備

<figure class="wp-block-image size-large">![](https://komorinfo.com/wp-content/uploads/2022/12/image-1024x310.png)</figure>探索部以外のほぼ全てのコンポーネントに対し、単体テストを追加した。単体テストの追加に伴い、クラスの分割粒度やファイル分割粒度についても見直しを行った。現在、Line Coverageが96%程度、Branch Coerageが91%程度のテストが書かれている。

## 今後の展望

まず、盤面の初期評価については大きな改善の余地があると考える。KomoringHeightsの盤面の初期評価は `initial_estimation.hpp` に集約されている。このファイルには謎のマジックナンバーがいくつか定義されている。実は、この数値を少しいじるだけで詰将棋エンジンの挙動が大きく変わってしまう。このようにとても重要なパラメータであるのだが、あまり真面目に検討ができていない。今後は機械学習により最適値を設定したい。

また、df-pnアルゴリズム以外のアルゴリズムについても試してみたいと考えている。というのも、df-pnアルゴリズムは裸玉局面を極端に苦手としているためである。df-pnは分岐の少ない局面を優先して探索するアルゴリズムである。手数にとらわれず分岐の少ない経路を深く細く読むことができるため、長手数の詰将棋と相性が良い。一方で、裸玉のように王手の選択肢が多い局面の探索には向かない。なぜなら、兄妹局面が無数に存在しており、分岐数だけでは局面の優劣をうまく測れないためである。そのため、裸玉局面に強いアルゴリズムが作れないか試してみたい。

なお、次回のリリース時期については見通しが立っていない。いろいろ余裕ができたら開発を再開したい。
