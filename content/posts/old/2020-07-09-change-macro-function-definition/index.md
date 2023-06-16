---
author: komori-n
draft: true
categories:
  - tips
date: "2020-07-09T21:19:49+09:00"
tags:
  - C/C++
  - C Preprocessor Macro
relpermalink: blog/change-macro-function-definition/
url: blog/change-macro-function-definition/
title: 値に応じて中身が変わるマクロ関数
description: 値に応じて展開結果が代わるようなC言語マクロの書き方について。
---

書こうと思ったら意外と苦戦したのでメモ。

## 問題設定

マクロの設定値に応じて展開結果が変わるようなマクロ関数を作りたい。

具体的には、以下のようなマクロを考える。

```c
#define A 0
#define B 1

#define CFG_1_MODE A
#define CFG_2_MODE B
#define CFG_3_MODE A
```

A, Bの2つのモードがあり、configすべき項目がいくつか（この例では3つ）ある状況を考える。

このとき、以下のように展開されるマクロ関数`EXPAND(i)`をうまく書きたい。

```c
EXPAND(1)  // => IMPL_A(1)
EXPAND(2) // => IMPL_B(2)
EXPAND(3) // => IMPL_A(3)
```

`IMPL_A, IMPL_B`に対し3項演算子は使えないものとする。（中身は単純な式ではないと仮定）

マクロ関数でなくても良いなら、以下のように`#if~#endif`を連打すれば簡単に実現できる。

```c
#if CFG_1_MODE == A
IMPL_A(1)
#elif CFG_1_MODE == B
IMPL_B(1)
#endif
...
```

これをマクロ関数にするとなると意外と難しくなる。`#define`中では`#if`は使えないので、次のように工夫する必要がある。

```c
#define EXPAND(i) IMPL_TMP(CFG_##i##_MODE)(i)
#define IMPL_TMP(mode) IMPL_CAT(mode)
#define IMPL_CAT(mode) IMPL_##mode
#IMPL_0 IMPL_A
#IMPL_1 IMPL_B
```

`CFG_##i##_MODE`の値をIMPL\_の後にくっつけて、分岐を実現する。

```c
$ gcc -E cocoro-pyonpyon.c
# 1 "cocoro-pyonpyon.c"
# 1 "<built-in>"
# 1 "<command-line>"
# 31 "<command-line>"
# 1 "/usr/include/stdc-predef.h" 1 3 4
# 32 "<command-line>" 2
# 1 "cocoro-pyonpyon.c"
# 14 "cocoro-pyonpyon.c"
IMPL_A(1)
IMPL_B(2)
IMPL_A(3)
```

ちゃんと動いた。

これ、`IMPL_0`や`IMPL_1`の部分がややダサいけどなんとかならないかな。値域が狭ければ`BOOST_PP_EQUAL`でなんとかなりそうだけど、一般の値を扱うとなると難しそう。僕には思いつかなかった。

## コード

{{< gist komori-n 9e4d290618982cba573a546c14215d41 >}}
