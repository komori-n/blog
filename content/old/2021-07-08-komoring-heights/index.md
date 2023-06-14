---
author: komori-n
draft: true
categories:
  - プログラミング
  - ポエム
  - 将棋
date: "2021-07-08T22:56:14+09:00"
guid: https://komorinfo.com/blog/?p=1290
id: 1290
image: https://komorinfo.com/wp-content/uploads/2021/04/cropped-icon.png
og_img:
  - https://komorinfo.com/wp-content/uploads/2021/04/cropped-icon.png
permalink: /komoring-heights/
tags:
  - C/C++
  - df-pn algorithm
  - 詰将棋
title: オープンソースの詰将棋エンジン「KomoringHeights」を作った
url: komoring-heights/
---

詰将棋エンジン「KomoringHeights」を公開した。

<figure class="wp-block-image">[![komori-n/KomoringHeights - GitHub](https://gh-card.dev/repos/komori-n/KomoringHeights.svg)](https://github.com/komori-n/KomoringHeights)</figure>やねうら王ベースのオープンソースの詰将棋エンジンで、df-pnアルゴリズムにより長手数の詰将棋でも短時間で詰みを見つけられる。手元の環境だと、現在最長手数の詰将棋であるミクロコスモス（1525手詰）の詰みを10分程度で読み切ることができる。

<figure class="wp-block-image size-large">![](https://komorinfo.com/wp-content/uploads/2021/07/komoringheights-1024x724.jpg)</figure>## ソフトの概要

df-pnアルゴリズムをベースにして、n手詰めルーチンや証明駒／反証駒による探索ノード数の削減を行うことで、現実的な時間内で長手数の詰将棋を解くことができる。指し手生成などの基本的なデータ構造はやねうら王のコードをほぼそのまま使用している。

新たに書いたコード量は1500行弱と短いが、詰将棋探索の基本的な探索手法がすべて凝縮されている。今後、自力で詰将棋エンジンを作ろうとしている人の参考になれば嬉しい<span class="easy-footnote-margin-adjust" id="easy-footnote-1-1290"></span><span class="easy-footnote">[<sup>1</sup>](https://komorinfo.com/blog/komoring-heights/#easy-footnote-bottom-1-1290 "1500行の割にはコーディングやデバッグ作業にかなり手こずった。感覚的には6000行ぐらい書いた気分である")</span>。

細かい技術解説は最近の詰将棋技術の解説記事を参照。

<figure class="wp-block-embed is-type-wp-embed is-provider-コウモリのちょーおんぱ wp-block-embed-コウモリのちょーおんぱ"><div class="wp-block-embed__wrapper">> [詰将棋に対するdf-pnアルゴリズムの解説](https://komorinfo.com/blog/df-pn-basics/)

<iframe class="wp-embedded-content" data-secret="jDeVkyMdLA" frameborder="0" height="282" marginheight="0" marginwidth="0" sandbox="allow-scripts" scrolling="no" security="restricted" src="https://komorinfo.com/blog/df-pn-basics/embed/#?secret=jDeVkyMdLA" style="position: absolute; clip: rect(1px, 1px, 1px, 1px);" title="“詰将棋に対するdf-pnアルゴリズムの解説” — コウモリのちょーおんぱ" width="500"></iframe></div></figure><figure class="wp-block-embed is-type-wp-embed is-provider-コウモリのちょーおんぱ wp-block-embed-コウモリのちょーおんぱ"><div class="wp-block-embed__wrapper">> [詰将棋探索における証明駒／反証駒の活用方法](https://komorinfo.com/blog/proof-piece-and-disproof-piece/)

<iframe class="wp-embedded-content" data-secret="gsHTu7Q1hV" frameborder="0" height="282" marginheight="0" marginwidth="0" sandbox="allow-scripts" scrolling="no" security="restricted" src="https://komorinfo.com/blog/proof-piece-and-disproof-piece/embed/#?secret=gsHTu7Q1hV" style="position: absolute; clip: rect(1px, 1px, 1px, 1px);" title="“詰将棋探索における証明駒／反証駒の活用方法” — コウモリのちょーおんぱ" width="500"></iframe></div></figure>実装にあたってtanuki-詰め<span class="easy-footnote-margin-adjust" id="easy-footnote-2-1290"></span><span class="easy-footnote">[<sup>2</sup>](https://komorinfo.com/blog/komoring-heights/#easy-footnote-bottom-2-1290 "<a href="https://github.com/yaneurao/YaneuraOu/blob/master/source/engine/tanuki-mate-engine/tanuki-mate-search.cpp">YaneuraOu/tanuki-mate-search.cpp at master · yaneurao/YaneuraOu</a>")</span>やdlshogiのdf-pnエンジン<span class="easy-footnote-margin-adjust" id="easy-footnote-3-1290"></span><span class="easy-footnote">[<sup>3</sup>](https://komorinfo.com/blog/komoring-heights/#easy-footnote-bottom-3-1290 "<a href="https://github.com/TadaoYamaoka/DeepLearningShogi">TadaoYamaoka/DeepLearningShogi</a>")</span>、やねうら王の詰将棋エンジン<span class="easy-footnote-margin-adjust" id="easy-footnote-4-1290"></span><span class="easy-footnote">[<sup>4</sup>](https://komorinfo.com/blog/komoring-heights/#easy-footnote-bottom-4-1290 "<a href="https://github.com/yaneurao/YaneuraOu/blob/master/source/engine/yaneuraou-mate-engine/yaneuraou-mate-search.cpp">YaneuraOu/yaneuraou-mate-search.cpp at master · yaneurao/YaneuraOu</a>")</span>を大いに参考にしている<span class="easy-footnote-margin-adjust" id="easy-footnote-5-1290"></span><span class="easy-footnote">[<sup>5</sup>](https://komorinfo.com/blog/komoring-heights/#easy-footnote-bottom-5-1290 "やねうら王の詰将棋探索を眺めているときにバグを見つけ、人生初めて将棋ソフトのPull Requestを出した。（<a href="https://github.com/yaneurao/YaneuraOu/pull/176">&#8211; df-pnのsecond_pn,second_dnの計算が正しくない問題を修正 by komori-n · Pull Request #176 · yaneurao/YaneuraOu</a>）将棋ソフトへのcontributionがプログラミングを始めたときからの一つの目標だったので、個人的にはこれは非常に嬉しかった。")</span>。

また、作成したエンジンの動作チェックにはやねうらお氏作成の詰将棋500万問を使用している<span class="easy-footnote-margin-adjust" id="easy-footnote-6-1290"></span><span class="easy-footnote">[<sup>6</sup>](https://komorinfo.com/blog/komoring-heights/#easy-footnote-bottom-6-1290 "<a href="https://yaneuraou.yaneu.com/2020/12/25/christmas-present/">やねうら王公式からクリスマスプレゼントに詰将棋500万問を謹呈 | やねうら王 公式サイト</a>")</span> <span class="easy-footnote-margin-adjust" id="easy-footnote-7-1290"></span><span class="easy-footnote">[<sup>7</sup>](https://komorinfo.com/blog/komoring-heights/#easy-footnote-bottom-7-1290 "11手詰100万問問題集のおかげでバグを19個見つけることができた")</span>。

### よくありそうなQA

Q. なんでこれを作ったんですか？
A. 現実的な時間、メモリサイズでミクロコスモスが解けるソフトを自分の手で作ってみたいと思ったから。オープンソースの詰将棋エンジンを探してみたが、既存のエンジンはほとんどが実戦特化型で、超長手数の詰将棋には向かない実装になっていた。長手数の詰将棋エンジンの理論自体は20年以上前からほとんど変わっていないので、自分でも作ってみたいと思い実装した<span class="easy-footnote-margin-adjust" id="easy-footnote-8-1290"></span><span class="easy-footnote">[<sup>8</sup>](https://komorinfo.com/blog/komoring-heights/#easy-footnote-bottom-8-1290 "はじめはローカル環境でサクッと作って個人的に楽しんで終わりにしようと考えていたが、実装してみたら異常に大変だったので公開することにした")</span> <span class="easy-footnote-margin-adjust" id="easy-footnote-9-1290"></span><span class="easy-footnote">[<sup>9</sup>](https://komorinfo.com/blog/komoring-heights/#easy-footnote-bottom-9-1290 "なお、<a href="https://gps.tanaka.ecc.u-tokyo.ac.jp/gpsshogi/">GPSshogi</a> はdf-pnアルゴリズムを完璧に（証明駒やヒューリスティックな枝刈りを含んだ状態で）実装されているらしいが、現代はやねうら王全盛期のためやねうら王ベースでの実装にこだわった")</span>。

---

Q. 脊尾詰<span class="easy-footnote-margin-adjust" id="easy-footnote-10-1290"></span><span class="easy-footnote">[<sup>10</sup>](https://komorinfo.com/blog/komoring-heights/#easy-footnote-bottom-10-1290 "<a href="http://panashogi.web.fc2.com/seotsume.html">脊尾詰ダウンロード</a>")</span>の3倍ぐらい遅いのはどうしてですか？
A. これは僕の技術力不足が原因である。

探索速度についてはKomoringHeightsはやねうら王ベースのため、指し手生成速度は現在のコンピュータ将棋の中でも最速に近いはずである。しかし、詰将棋探索部の実装方法の工夫が不足しているためか、npsが想定ほど出ていない。現在のKomoringHeights実装では、実行時間の45%が置換表のLookUpに充てられているようだ。

KomoringHeightsはあくまで長手数の詰将棋が解ける実装の一例を提供することが目的なので、本将棋AIのような1%単位の高速化にはあまりこだわっていない。そのため、脊尾詰よりも高速に探索できるようにするモチベーションは今のところはない<span class="easy-footnote-margin-adjust" id="easy-footnote-11-1290"></span><span class="easy-footnote">[<sup>11</sup>](https://komorinfo.com/blog/komoring-heights/#easy-footnote-bottom-11-1290 "実は、アルゴリズム面で1つ大きな妥協している点がある。それは、末端局面のpn/dnを1/1固定にしている点だ。局面の詰みやすさをヒューリスティックに求めてpn/dnの初期値を変えるアルゴリズム（df-pn+, やねうら詰め方式）を採用することで探索局面数の削減が見込める。しかし、これを採用するとデバッグがしづらくなったり、パラメータの少しの調整で探索時間が大きく変動したりしてとても疲れるので採用を取りやめた。解図速度は間違いなく向上するので、気が向いたら実装してみようと思う。")</span>。

---

Q. 脊尾詰は256MBでミクロコスモスを解けるのに、KomoringHeightsは1GB以上必要なのはなぜですか？
A. 効率的なGarbage Collection（GC）を実装していないことが原因である。なぜ実装していないかというと、なくても長手数詰将棋を解けてしまうためである。

---

Q. 詰み手順に無駄合が含まれていて美しくないのはなんとかならないですか？
Q. 余詰検索機能はないんですか？
A. 無駄合や余詰の検知は判定がかなり複雑なので、KomoringHeightsでは一切考慮していない。そのため、これらの用途で詰将棋エンジンを使いたい場合は脊尾詰を使うのがおすすめである。

---

Q. スレッド数を2以上にしても探索が並列化されないようですが、今後並列化を実装する予定はありますか？
A. 並列化の予定は今のところはない。

並列化をするためにはかなりの大改造が必要になるが、今の実装で解けない問題が解けるようになる改造ではない（n並列化ならシングルスレッドでもn倍の時間をかければ解ける）のであまり気が進まないというのが現状である。

---

Q. なんで「KomoringHeights」って名前なんですか？
A. 気づいたときにはこの名前になっていた。響きだけで決めているので深い理由はない。
