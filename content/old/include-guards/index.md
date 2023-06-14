---
author: komori-n
draft: true
categories:
  - プログラミング
  - ポエム
date: "2021-08-31T22:13:11+09:00"
guid: https://komorinfo.com/blog/?p=1367
id: 1367
image: https://komorinfo.com/wp-content/uploads/2020/09/cpp.png
og_img:
  - https://komorinfo.com/wp-content/uploads/2020/09/cpp.png
permalink: /include-guards/
tags:
  - C/C++
title: C++のインクルードガードの命名
url: include-guards/
---

`_` から始まる変数や `__` を含む変数をマクロ定数に用いてはいけないが、世の中にはこのルールを逸脱しているコードが数多く存在するので注意が必要である。

## 予約語

c++ではいくつか識別子として使ってはいけない名前（予約語）が存在する。例えば、`struct` や `int` など言語機能にかかわる単語は変数名やクラス名として用いることができない事になっている。コード中でこれらの識別子が使われた場合、コンパイルに失敗するので大きな問題になる前に気づくことができる。

一方、C++では以下の識別子はコンパイラのために予め予約されているので、ユーザーが勝手に使うのは規約違反である<span class="easy-footnote-margin-adjust" id="easy-footnote-1-1367"></span><span class="easy-footnote">[<sup>1</sup>](https://komorinfo.com/blog/include-guards/#easy-footnote-bottom-1-1367 "逆に、コンパイラを実装する側はこれらを含む識別子を意図的に用いることで、ユーザーのソースコードとのコンフリクトを防ぐことができる。実際、<a href="https://github.com/gcc-mirror/gcc/tree/master/libstdc%2B%2B-v3">libstdc++</a> の実装を見ると、このような識別子が至るところで用いられていることが確認できる。")</span>。言語機能にかかわる単語とは違い、名前が衝突しない限りコンパイラからwarningが発せられることはないので、普段から意識していないと気づくことができない。

- 2つ以上連続したアンダースコア `__` を含む識別子
  - 例）`A__B`, `__x`
- 「アンダースコア `_` + 大文字」から始まる識別子
  - 例）`_ABC`
- （global namespace限定）「アンダースコア `_` + 小文字」から始まる識別子
  - 例）`_abc`

3番目のルールだけ少しややこしいが、global namespace以外（namespace内やローカル変数など）ではユーザー側が好きに使うことができる<span class="easy-footnote-margin-adjust" id="easy-footnote-2-1367"></span><span class="easy-footnote">[<sup>2</sup>](https://komorinfo.com/blog/include-guards/#easy-footnote-bottom-2-1367 "ユーザー定義リテラル（<code>1ms</code> のように書く記法）は1文字目を <code>_</code> にしなければならないので、必ずいずれかのnamespaceに入れて <code>_</code> + 小文字 から始まる変数名にしなければならない")</span>。

よって、以下のようなインクルードガードを書くのはC++のコードとしては正しくない。

```
#ifndef _INCLUDE_GUARD_HOGE_H__  // 予約語なのでダメ(!)
#define _INCLUDE_GUARD_HOGE_H__

// implementations...

#endif // _INCLUDE_GUARD_HOGE_H__
```

正しくは、インクルードガードには `INCLUDE_GUARD_HOGE_H_` のようにルールを守った変数名をつける。さらに言えば、プロジェクト全体で変数名が被らないようにするために、”fuga/piyo/hoge.h” なら `FUGA_PIYO_HOGE_H_` のようにファイルの階層に合わせた命名にしたほうが良い。
