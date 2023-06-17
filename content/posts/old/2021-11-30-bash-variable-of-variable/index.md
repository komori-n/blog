---
author: komori-n
categories:
  - 技術解説
date: "2021-11-30T22:57:06+09:00"
tags:
  - Bash
keywords:
  - 変数
  - 入れ子
title: Bashで変数の変数を参照する
relpermalink: blog/bash-variable-of-variable/
url: blog/bash-variable-of-variable/
description: Bashで入れ子になった変数の値を読み出す方法
---

1時間ぐらい悩んだのでメモ。

## A=${B}, B=${C}, …

以下のように変数が入れ子になっている状態を考える。

```bash
A='${B}'
B=334
```

変数 `A` だけが既知のとき、変数 `A` の指す先の変数 `B` に入っている値を読み出したい。この場合、`eval` を用いることですっきり書ける。

```bash
eval echo ${A}
# => echo ${B}
# => 334
```

`echo ${A}` は `echo \${B}` と解釈されるので、そのまま `eval` に渡せば `${B}` の指し先が分かるという仕組みだ。

同様に、変数が 3 つ以上連なっている場合も `eval` を連打することで展開することができる。

```bash
A='${B}'
B='${C}'
C=334
eval eval echo ${A}
# => 334
```

## A=B, B=C, …

少し似たようなケースで、以下のように変数が入れ子になっている場合を考える。

```bash
A=B
B=C
C=334
```

この場合、前節と同様に `eval` することで値を取り出せる。

```bash
eval eval echo \\\$\$${A}
# => eval echo \$$B
# => echo $C
# => 334
```

なお、変数のネストが1段階だけの場合、Indirect Expansionという機能を用いて次のように書くこともできる。

```bash
echo ${!B}
# => echo ${C}
# => echo 334
```
