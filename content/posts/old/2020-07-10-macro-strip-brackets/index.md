---
author: komori-n
categories:
  - 技術解説
date: "2020-07-10T19:21:00+09:00"
tags:
  - C言語
keywords:
  - Cプリプロセッサマクロ
relpermalink: blog/macro-strip-brackets/
url: blog/macro-strip-brackets/
title: マクロ定数からカッコを剥ぎ取る
description: C言語のプリプロセッサマクロを駆使して、括弧付きの文字列から括弧を外す方法について説明する。
---

意外とぱっと思いつかなかったので、忘れないようにメモ。

## 問題設定

次のように、カッコで値が囲まれたマクロ定数から値を取り出すマクロ関数`STRIP_PRN()`を作りたい。

```c
#define A (1)

STRIP_PRN(A)  // => 1
```

展開したカッコつきの定数をマクロ関数の引数と解釈させると、中身を取り出すことができる。

```c
#define STRIP_PRN(x) IDENTITY x
#define IDENTITY(x) x
```

これを応用すると、次のように型名が指定されたマクロ定数からも値を取り出すことができる。

```c
#define B ((uint8_t)2)

#define DELETE_BLOCK(x) DELETE_ARG x
#define DELETE_ARG(x)

DELETE_BLOCK(STRIP_PRN(B))  // => 2
```

## コード

{{< gist komori-n 6e75072a31f267473cb700248b715827 >}}

```sh
$ gcc -E cocoro-pyonpyon2.c
# 1 "cocoro-pyonpyon2.c"
# 1 "<built-in>"
# 1 "<command-line>"
# 31 "<command-line>"
# 1 "/usr/include/stdc-predef.h" 1 3 4
# 32 "<command-line>" 2
# 1 "cocoro-pyonpyon2.c"
# 9 "cocoro-pyonpyon2.c"
1
2
```
