---
author: komori-n
draft: true
categories:
  - プログラミング
date: "2020-07-10T19:21:00+09:00"
guid: https://komorinfo.com/blog/?p=85
id: 85
image: https://komorinfo.com/wp-content/uploads/2020/07/cocoro-pyonpyon2.png
og_img:
  - https://komorinfo.com/blog/wp-content/uploads/2020/07/cocoro-pyonpyon2.png
permalink: /macro-strip-brackets/
tags:
  - C/C++
title: マクロ定数からカッコを剥ぎ取る
url: macro-strip-brackets/
---

意外とぱっと思いつかなかったので、忘れないようにメモ。

## 問題設定

次のように、カッコで値が囲まれたマクロ定数から値を取り出すマクロ関数`STRIP_PRN()`を作りたい。

```
#define A (1)

STRIP_PRN(A)  // => 1
```

展開したカッコつきの定数をマクロ関数の引数と解釈させると、中身を取り出すことができる。

```
#define STRIP_PRN(x) IDENTITY x
#define IDENTITY(x) x
```

これを応用すると、次のように型名が指定されたマクロ定数からも値を取り出すことができる。

```
#define B ((uint8_t)2)

#define DELETE_BLOCK(x) DELETE_ARG x
#define DELETE_ARG(x)

DELETE_BLOCK(STRIP_PRN(B))  // => 2
```

## コード

[GitHub – cocoro-pyonpyon2.c](https://gist.github.com/komori-n/6e75072a31f267473cb700248b715827)

```
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
