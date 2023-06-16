---
author: komori-n
draft: true
categories:
  - プログラミング
date: "2021-11-30T22:57:06+09:00"
guid: https://komorinfo.com/blog/?p=1474
id: 1474
permalink: /bash-variable-of-variable/
tags:
  - Bash
title: Bashで変数の変数を参照する
url: bash-variable-of-variable/
---

1時間ぐらい悩んだのでメモ。

## A=${B}, B=${C}, …

以下のように変数が入れ子になっている状態を考える。

```
A='${B}'
B=334
```

変数 `A` だけが既知のとき、変数 `A` の指す先の変数 `B` に入っている値を読み出したい。この場合、`eval` を用いることですっきり書ける。

```
eval echo ${A}
# => echo ${B}
# => 334
```

`echo ${A}` は `echo \${B}` と解釈されるので、そのまま `eval` に渡せば `${B}` の指し先が分かるという仕組みだ。

同様に、変数が 3 つ以上連なっている場合も `eval` を連打することで展開することができる。

```
A='${B}'
B='${C}'
C=334
eval eval echo ${A}
# => 334
```

## A=B, B=C, …

少し似たようなケースで、以下のように変数が入れ子になっている場合を考える。

```
A=B
B=C
C=334
```

この場合、前節と同様に `eval` することで値を取り出せる。

```
eval eval echo \\\$\$${A}
# => eval echo \$$B
# => echo $C
# => 334
```

なお、変数のネストが1段階だけの場合、Indirect Expansionという機能を用いて次のように書くこともできる。

```
echo ${!B}
# => echo ${C}
# => echo 334
```
