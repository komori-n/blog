---
author: komori-n
draft: true
categories:
  - プログラミング
date: "2021-09-30T22:19:23+09:00"
guid: https://komorinfo.com/blog/?p=1378
id: 1378
image: https://komorinfo.com/wp-content/uploads/2021/09/image-8.png
og_img:
  - https://komorinfo.com/wp-content/uploads/2021/09/image-7.png
permalink: /cold-clear-search-algorithm/
tags:
  - Rust
  - Tetris
title: テトリスAI『Cold Clear』の思考部を眺める
url: cold-clear-search-algorithm/
---

テトリスAIのCold Clearの探索方法が気になったので一通り読んでまとめた。

以下の内容は2021-09-30時点の最新版（7b4abc931948d69f6f0b4eb7d401167c1cdedb03）に基づいて記載している。

## 概要

**Cold Clear**はRustで開発されているオープンソースのテトリスAIである。テトリスAIの強豪ソフトの一つとして広く知られており、安定して高い火力を送る技術に定評がある。

Cold Clearのソースコードは以下のリポジトリから取得することができる。

<figure class="wp-block-image">[![MinusKelvin/cold-clear - GitHub](https://gh-card.dev/repos/MinusKelvin/cold-clear.svg)](https://github.com/MinusKelvin/cold-clear)</figure>また、youtubeで「Cold Clear」で検索することで、Cold Clearの超人的なプレイ動画が見られる。

<figure class="wp-block-embed is-type-video is-provider-youtube wp-block-embed-youtube wp-embed-aspect-16-9 wp-has-aspect-ratio"><div class="wp-block-embed__wrapper"><iframe allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen="" frameborder="0" height="281" loading="lazy" src="https://www.youtube.com/embed/AejufICCQQc?feature=oembed" title="宇宙最強AI対決！ColdClearパフェ型VS ColdClear火力型【ぷよぷよテトリス】【puyopuyotetris】" width="500"></iframe></div></figure>本ページは、Cold Clearの探索部をざっくりと理解することが目的である。

### ディレクトリ構成

Cold Clearのコードはコンポーネントごとに細かくパッケージ化されていて、初見ではどこに何が書かれているのか分かりづらい。Cold Clearリポジトリのディレクトリ構造は以下のようになっている。

- battle｜AI同士の対戦
- bot｜**Cold Clear探索部**
- c-api｜Cold ClearのC言語ライブラリ
- cc-client｜GUI
- compare｜評価関数の比較テスト
- libtetris｜テトリス関連の基本的な型、ルール
- opening-book｜開幕テンプレ
- optimizer｜パラメータチューニング（遺伝的アルゴリズム）
- tbp｜tetris-bot-protocol

また、リポジトリは分かれているが、Perfect Clear（全消し）の探索にはpcfが用いられている。

<figure class="wp-block-image">[![MinusKelvin/pcf - GitHub](https://gh-card.dev/repos/MinusKelvin/pcf.svg)](https://github.com/MinusKelvin/pcf)</figure>本ページでは、上記のうち `bot` ディレクトリ以下の実装に絞って解説する。

## 3行まとめ

- 人間の直感を元にした評価関数
- 特殊なノード選択をするMonte-Carlo Tree Search
- Perfect Clearに特化した探索モード

## テトリスの基礎知識

Cold Clearの実装を眺め始める前に、テトリスの基礎知識について重要な部分だけかいつまんで説明する。日頃からテトリスに慣れ親しんでいる方には特に目新しい情報はないので、次章まで読み飛ばしても問題ない<span class="easy-footnote-margin-adjust" id="easy-footnote-1-1378"></span><span class="easy-footnote">[<sup>1</sup>](https://komorinfo.com/blog/cold-clear-search-algorithm/#easy-footnote-bottom-1-1378 "ちなみに僕はテトリス歴1週間で平積みすらままならないレベルである")</span>。

### Tetris Guideline

近年開発されているテトリスは「Tetris Guideline」と呼ばれる基準に従い開発が行われている。Tetris Guidelineは、ハードやソフトによるルールの差異を軽減するために制定されており、テトリミノの色や形を始めとして、画面配置やミノのドロップ時間、テトリミノの奇怪な回転法則<span class="easy-footnote-margin-adjust" id="easy-footnote-2-1378"></span><span class="easy-footnote">[<sup>2</sup>](https://komorinfo.com/blog/cold-clear-search-algorithm/#easy-footnote-bottom-2-1378 "Super Rotation System(SRS)。AIやクライアントを自作する際はSRS準拠の挙動を再現するのに苦労することが多い")</span>に至るまでテトリスを開発する上で守るべきルールが細かく定義されている。自作のテトリスAIやクライアントを作る際は、このガイドラインを守ることで移植性や互換性を高めることができる。

Tetris Guidelineは一般には公開されていないので最新版を確認することはできないが、2009年版は [tetris guideline docs 2009.zip](https://www.dropbox.com/s/g55gwls0h2muqzn/tetris%20guideline%20docs%202009.zip?dl=0) よりダウンロードできる。

<div class="wp-block-image"><figure class="aligncenter size-large is-resized">![](https://komorinfo.com/wp-content/uploads/2021/09/image-3.png)<figcaption>2009 Tetris Design Duideline.pdf (p.6)</figcaption></figure></div>### Bag System

<figure class="wp-block-image size-large">![](https://komorinfo.com/wp-content/uploads/2021/09/image.png)</figure>テトリスにはO, I, T, L, J, S, Zの7種のミノが存在する。これらはすべて独立にランダムに落ちてくるわけではなく、**bag system**と呼ばれる法則に従って抽選される。

7種のミノを1つずつ集めたものを1セット（bag）として、bagの中からランダムにミノを取り出すことを繰り返す。bagが空になったらまた1セットをbagの中に入れて、同様の手順を繰り返していく。7手ごとに状態がループする構造を取ることから、「7種1巡の法則」と呼ばれることもある。

必ず7手で1巡するので、完全ランダムだった昔のテトリスと比べてランダム性が小さくなっている。Cold Clearでは、この法則性を前提にミノの先読みと探索の投機実行を行っている<span class="easy-footnote-margin-adjust" id="easy-footnote-3-1378"></span><span class="easy-footnote">[<sup>3</sup>](https://komorinfo.com/blog/cold-clear-search-algorithm/#easy-footnote-bottom-3-1378 "テトリスプレイヤーの間では、この強い法則性を活かして序盤に決まった形に組む「開幕テンプレ」という戦術が常識になっている")</span>。

<figure class="wp-block-image size-large">![](https://komorinfo.com/wp-content/uploads/2021/09/image-1-1024x123.png)</figure>7手ごとの境界の間では特にミノの調整は行われないので、運が悪いと上図のように同じミノが連続して降ってくることもある。

### 火力

テトリスでは、特定の消し方をすることで相手にラインを送ることができる。以下に一例として『ぷよぷよテトリス』で採用されている火力（対テトリス）の一覧を示す。ここでは話を簡単にするため、Back-to-Backについては省いて考えることにする。

<figure class="wp-block-table">| 消し方 | 相手に送れる段数 |
|---|---|
| Single | 0 |
| Double | 1 |
| Triple | 2 |
| Tetris | 4 |
| T-Spin Mini | 0 |
| T-Spin Single | 2 |
| T-Spin Double | 4 |
| T-Spin Triple | 6 |
| (Perfect Clear) | 10 |

<figcaption>相手に送れるライン数（ぷよぷよテトリスの対テトリス）<span class="easy-footnote-margin-adjust" id="easy-footnote-4-1378"></span><span class="easy-footnote">[<sup>4</sup>](https://komorinfo.com/blog/cold-clear-search-algorithm/#easy-footnote-bottom-4-1378 "Perfect Clearは消し方に関係なく固定で10ライン。RENボーナスも無視される")</span></figcaption></figure>上記の表を見ると分かる通り、TetrisとT-Spin Doubleが同じ火力に設定されている。同じ火力にもかかわらず、Tetrisに必要なブロック数は40ブロック（9ミノ+Iミノ）なのに対し、T-Spin Doubleは21ブロック（4ミノ+屋根+Tミノ）である。そのため、火力アップのためにはT-Spinを狙って打つ戦術が必要になる。また、Perfect Clearの火力も10ラインと強力で、1回の攻撃だけで相手の盤面の半分を埋める事ができる。

連続してライン消去を行うと、上の表の火力に加えてRENと呼ばれる火力ボーナスが得られる。

<figure class="wp-block-table">| REN | 火力ボーナス |
|---|---|
| 0－ 1 | 0 |
| 2 － 3 | +1 |
| 4 － 5 | +2 |
| 6 － 7 | +3 |
| 8 － 10 | +4 |
| 11 － | +5 |

<figcaption>RENの火力ボーナス（ぷよぷよテトリスの対テトリス）</figcaption></figure>ボーナス自体は微々たるものだが、10RENで計24ライン、15RENで計49ラインと高火力な攻撃を相手に送りつけることができる。

このように、現代テトリスはひたすら平積みをしてTetris（4列消し）し続けるゲームではなく、状況に応じてT-spinやRENを組んだり、Perfect Clearを狙ったりして火力効率をできるだけ高めるゲームなのである。そのため、**いかにT-SpinやPerfect Clearを連打する手順を見つけられるか**が探索において重要となる。

## 評価器（Evaluator）

\# bot/src/evaluation/\*.rs <span class="easy-footnote-margin-adjust" id="easy-footnote-5-1378"></span><span class="easy-footnote">[<sup>5</sup>](https://komorinfo.com/blog/cold-clear-search-algorithm/#easy-footnote-bottom-5-1378 "Cold Clearには <code>standard::Standard</code> と <code>changed::Stanrdard</code> の2つの評価器が定義されているが、現在のコードでは名前以外は完全に同一なので注意")</span>

Cold Clearにおける評価器 `Evaluator` は盤面（Board）や次のミノの置き方 （FallingPiece）の「よさ」を数値化する役割を担う。数値化することにより、異なる盤面の「よさ」の比較が可能となり、最適な配置方法を選ぶ基準にできる。

評価器は次のようなトレイトにより表現される。

```
pub trait Evaluator: Send + Sync {
    // ...
    fn evaluate(
        &self,
        lock: &LockResult,
        board: &Board,
        move_time: u32,
        placed: Piece,
    ) -> (Self::Value, Self::Reward);
    // ...
}
```

Cold Clearの評価器は、**報酬**（Reward）と**評価値**（Evaluation）のの2つの値を出力する。似た単語で紛らわしいが、「報酬」は**ミノを置くことそのものに対する評価**、「評価値」は**ミノを置いた後の地形やネクストをもとに計算される評価**である<span class="easy-footnote-margin-adjust" id="easy-footnote-6-1378"></span><span class="easy-footnote">[<sup>6</sup>](https://komorinfo.com/blog/cold-clear-search-algorithm/#easy-footnote-bottom-6-1378 "2つの値がある理由は、別経路による盤面の合流をうまく扱うためである。経路に依存する値と依存しない値に分けて持つことで、別経路で求めた評価値を流用できる")</span> <span class="easy-footnote-margin-adjust" id="easy-footnote-7-1378"></span><span class="easy-footnote">[<sup>7</sup>](https://komorinfo.com/blog/cold-clear-search-algorithm/#easy-footnote-bottom-7-1378 "厳密には、パラメータから計算される値に加え、生の火力（相手に何ライン送れるか）も報酬と評価値の構造体の中に入っている。通常時は使用しないが、相手から攻撃が来ていて今すぐ相殺しないと負けの盤面では、「形のよさ」ではなく火力を優先して手を選ぶ")</span>。

<figure class="wp-block-image size-large">![](https://komorinfo.com/wp-content/uploads/2021/09/image-4-1024x762.png)<figcaption>報酬と評価値（初期値）の計算イメージ。</figcaption></figure>報酬は、ラインの消し方（Tetris消しやT-spinなど）や火力ボーナス、ミノ移動にかかる時間から計算される。消し方から計算される指標のため、**探索中に報酬の値が変化することはない**。

一方、評価値は盤面のポテンシャルを表す指標のため、**子局面の評価に応じて探索中に増減する**値である。評価値の初期値は盤面のブロックの高さ、穴の位置と深さ、ネクストのTミノの数など幅広い指標を足し合わせて計算する。Cold Clearでは特にT-Spin関連の地形のパターンマッチに気合が入っており、おそらくここが強さの肝になっていると考えられる。

Cold Clearの評価器は人の目で厳選した特徴量で構成されている。30以上の特徴を確認し、それぞれの加点・減点を足し合わせることで評価を数値化している。加点・減点のパラメータは遺伝的アルゴリズムにより学習している<span class="easy-footnote-margin-adjust" id="easy-footnote-8-1378"></span><span class="easy-footnote">[<sup>8</sup>](https://komorinfo.com/blog/cold-clear-search-algorithm/#easy-footnote-bottom-8-1378 "特徴量は人の手で選んでいるがパラメータは遺伝的アルゴリズムで求めているので、「Cold ClearはルールベースのAI」と言うのは厳密には誤りだと思う")</span>。

```
// bot/src/evaluation/standard.rs よりT-Spin finの判定（抜粋）
//
// '#' ｜ブロックが存在するセル
// '_' ｜ブロックが存在しないセル
// '?' ｜どちらでも良い
detect_shape! {
    fin_left
    heights [h1 h2 _ _]
    require (|_, _| h1 <= h2+1)
    start_y(h2 + 2)
    success (3, h2-1, T, West)
    [? ? # # ?]
    [? ? _ _ ?]
    [? ? _ _ #]
    [? ? _ _ ?]
    [? ? # _ #]
}
```

探索中の評価値の更新方法については次節の「探索」にて述べる。

## 探索

\# bot/src/dag.rs, bot/src/modes/\*.rs

Cold Clearでは、現局面を根とする探索木を作り、末端ノードの展開を繰り返すことで探索を進めていく。具体的には、大きく分けて次のような手順で進められる。

1. 展開するleaf nodeの選択
2. 評価値を逆伝播

以下では、それぞれの手順についてもう少し掘り下げる。なお、Cold Clearのコードはマルチスレッド対応の影響で非常に分かりづらいため、本質を損なわない程度に記号やアルゴリズムを簡略化して説明する。

### 展開するleaf nodeの選択

<div class="wp-block-image"><figure class="aligncenter size-large is-resized">![](https://komorinfo.com/wp-content/uploads/2021/09/image-5.png)<figcaption>leaf nodeを見つけるまで木を下る</figcaption></figure></div>木の根（現在の局面）からスタートして一定のルールに従いながら確率的に木を下っていく。まだ子の展開をしていないノード（leaf node）にたどり着くまでこの手順を繰り返し、見つけたらleaf nodeを返すというアルゴリズムになっている。

木を下る手順が、ネクスト既知の場合と未知の場合で少し異なるので、分けて説明する。

#### ネクスト既知の場合

<div class="wp-block-image"><figure class="aligncenter size-large">![](https://komorinfo.com/wp-content/uploads/2021/09/image-7.png)<figcaption>子局面選択のイメージ</figcaption></figure></div>ホールドまたはネクストの1ミノの置き方をすべて列挙し、置き方それぞれに対する評価値を計算する。ここで、ミノの置き方に対する評価値 \\(E\_i^+\\) は、ドロップ自体の報酬 \\(R\_i\\) と子局面の評価値 \\(E\_i\\) の和 \\(E\_i + R\_i\\)で計算する。

この評価値から重み付けを計算し、重みに従い次の手を確率的に選択する。具体的には、ある盤面で \\(n\\) 通りの置き方があり、評価値が降順で \\(E_1^+, E_2^+, \\dots, E_n^+\\) であるとき、\\(i\\) 番目の手が選ばれる確率は\\\[P(i) \\propto \\frac{\\left(E_i^+ – \\displaystyle{\\min_j E_j^+}\\right)^2+10}{(i-1)^2+1}\\tag{1}\\\] である<span class="easy-footnote-margin-adjust" id="easy-footnote-9-1378"></span><span class="easy-footnote">[<sup>9</sup>](https://komorinfo.com/blog/cold-clear-search-algorithm/#easy-footnote-bottom-9-1378 "“(\\propto)”は比例を表す。すなわち、右辺の値が大きいものほど相対的に選ばれる確率が高い")</span>。分母に順位の2乗の項（ \\(i^2\\) ）があるため、評価値が高い置き方ほど選ばれる確率が高い。

このように、leaf nodeを見つけるまでchild nodeを選ぶことを繰り返す。

#### ネクスト未知の場合

<figure class="wp-block-image size-large">![](https://komorinfo.com/wp-content/uploads/2021/09/image-8.png)</figure>ネクストが不明の場合、bag systemに基づき次に落ちてくる可能性があるミノをすべて列挙する。この中から等確率で次のミノを選択し、「ネクスト既知」の探索方法に帰着させる。

### 評価値を逆伝播

<div class="wp-block-image"><figure class="aligncenter size-large">![](https://komorinfo.com/wp-content/uploads/2021/09/image-6.png)<figcaption>leaf nodeに子を追加して評価値を逆伝播させて更新する</figcaption></figure></div>前節の手法により未展開のleaf nodeが一つ選ばれているものとする。

まず、leaf nodeに対し可能なミノの置き方をすべて列挙し、木にchild nodeを追加する。leaf nodeがネクスト不明のノードである場合は、bag systemに基づきあり得るネクストすべてに対しこの操作を行う。

新たなleaf nodeを追加したら、中間ノードの評価値を「報酬+子局面の評価値（の期待値）」の最大値により更新する。式で表現すると、

\\begin{align}
E \\leftarrow \\begin{cases}
\\displaystyle{\\max\_{i} \\left(R_i + E_i\\right)} &amp; \\text{Mino is known} \\\\
\\displaystyle{\\mathbb{E}\_{\\mathrm{bag}}\\left\[\\max\_{i} \\left(R_i + E_i\\right)\\right\]} &amp; \\text{Mino is unknown}
\\end{cases}
\\end{align}

となる。ただし、\\(\\mathbb{E}\_{\\mathrm{bag}}\\) はbagのミノに関する期待値である。

この更新は木の葉から根の方向で行われる。たくさん火力を送れて消去後の地形がきれいな経路ほど評価値が高くなるようになっている。

以上のように、leaf nodeの展開と逆伝播を繰り返して読み進めることがCold Clearの探索部の大まかな流れである。

### PcLooper

「テトリスの基礎知識」で述べた通り、テトリスでは開幕Perfect Clearが取れるかどうかによって火力に大きな差が生じる。Cold Clearでは、盤面が空の時に限り、ネクスト10個+ホールドの計11ミノ以内でPerfect Clearが可能かどうかを探索する専用のルーチンを持っている<span class="easy-footnote-margin-adjust" id="easy-footnote-10-1378"></span><span class="easy-footnote">[<sup>10</sup>](https://komorinfo.com/blog/cold-clear-search-algorithm/#easy-footnote-bottom-10-1378 "対人戦では、PcLooperを有効化していると開幕から理不尽パフェ連打が飛んでくるので、この機能はしばしば無効化される")</span>。

探索構造体は `PcLooper` と呼ばれ、その内部では `pcf` パッケージを用いる。`PcLooper` は文字通りPerfect Clearを連打することが目的の探索部で、Perfect Clearが見つからなかったら通常の探索方法に戻る。`pcf`はPerfect Clearに特化したパッケージで、Cold Clear本体と比較して盤面の表現方法が簡略化されているため高速にPerfect Clearの探索を行うことができる<span class="easy-footnote-margin-adjust" id="easy-footnote-11-1378"></span><span class="easy-footnote">[<sup>11</sup>](https://komorinfo.com/blog/cold-clear-search-algorithm/#easy-footnote-bottom-11-1378 "Zetrisのパフェ探索（<a href="https://github.com/knewjade/sfinder-cpp">knewjade/sfinder-cpp: Tetris: Implement my solution-finder in C++</a>）の方が技術的に高度なことをしており、より高速にPerfect Clearを求められると思われる。詳しい技術解説は <a href="https://gist.github.com/knewjade/0a44ae8178526746477e5830bd38107c">パフェ全列挙アルゴリズム：プログラミング.md</a> を参照")</span>。

```
// bot/src/modes/mod.rs（一部コメント追加）
// Normalモード（火力型）からPcLoopモード（パフェ型）へ切り替えるべきかどうか判定する
fn can_pc_loop(board: &Board, hold_enabled: bool) -> bool {
    // 1. 盤面が空
    if board.get_row(0) != <u16 as Row>::EMPTY {
        return false;
    }
    let pieces = board.next_queue().count();
    if hold_enabled {
        // 2-a. （ホールドありの時）ネクストがホールド含めて11ミノ見えている
        let pieces = pieces + board.hold_piece.is_some() as usize;
        pieces >= 11
    } else {
        // 2-b. （ホールドなしの時）ネクストが10ミノ見えている
        pieces >= 10
    }
}
```

## まとめ

テトリスAIの『Cold Clear』の探索部の実装をざっくりと追った。特徴的なポイントは以下の3点であった。

- 人間の直感を元にした評価関数
- 特殊なノード選択をするMonte-Carlo Tree Search
- Perfect Clearに特化した探索モード
