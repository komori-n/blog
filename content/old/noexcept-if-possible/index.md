---
add-keywords:
  - move constructor, noexcept
author: komori-n
draft: true
categories:
  - プログラミング
date: "2021-04-14T21:34:37+09:00"
guid: https://komorinfo.com/blog/?p=1106
id: 1106
image: https://komorinfo.com/wp-content/uploads/2020/09/cpp.png
og_img:
  - https://komorinfo.com/wp-content/uploads/2020/09/cpp.png
permalink: /noexcept-if-possible/
tags:
  - C/C++
title: 他関数に応じてnoexceptにしたりしなかったりする
url: noexcept-if-possible/
---

noexcept例外仕様とnoexcept演算子の話。

C++で関数を定義するとき、参照している関数がnoexceptなら定義する関数もnoexceptにしたいことがある。

```
int hoge(Piyo p) noexcept /*<- fuga(p)次第*/ {
    return fuga(p);
}
```

このような場合、以下のように書く。

```
int hoge(Piyo p) noexcept(noexcept(fuga(p))) {
    return fuga(p);
}
```

例外仕様に `noexcept(noexcept(fuga(x)))` と書く。初見だと多大な違和感を抱くかもしれないが、2箇所の `noexcept` はそれぞれ意味が異なる。外側の `noexcept` は例外仕様指定子（カッコの中がtrueならnoexceptになる）として、内側の `noexcept` は演算子（カッコの中の式が例外を投げないなら true になる）としてそれぞれ用いている。

ちなみに、これがムーブコンストラクタや代入演算子であれば、type_traitsを用いることで少しだけ見やすい形で書き直せる。

```
Hoge::Hoge(Fuga&& fuga) noexcept(std::is_nothrow_move_constructible<Fuga>::value)  // Fugaがnoexceptでmove構築可能ならこのメソッドもnoexcept
    : fuga_(std::move(fuga)) {}
```

moveコンストラクタはついつい何も考えずnoexceptをつけてしまいがちなので頭の片隅に留めておきたい。
