---
author: komori-n
draft: true
categories:
  - プログラミング
date: "2020-09-09T20:56:53+09:00"
guid: https://komorinfo.com/blog/?p=499
id: 499
image: https://komorinfo.com/wp-content/uploads/2020/09/cpp.png
og_img:
  - https://komorinfo.com/blog/wp-content/uploads/2020/09/cpp.png
permalink: /cpp-cast/
tags:
  - C/C++
title: static_cast, dynamic_cast, reinterpret_castで結果が変わる例
url: cpp-cast/
---

`static_cast`, `dynamic_cast`, `reinterpret_cast`の計算結果がすべて違う値になる例がぱっと思いつかなかったのでメモ。

以下のコードは、3つのキャストの計算結果が異なる例である。

```
#include <iostream>
#include <cstdlib>

class A1 {virtual void f(){};};
class A2 {virtual void g(){};};
class B : public A1, public A2 {};

#define DEBUG_PRINT(val)  std::cout << #val << "\t:" << (val) << std::endl

int main(int argc, char* argv[]) {
  A2* a2 = new A2;

  DEBUG_PRINT(a2);
  DEBUG_PRINT(static_cast<B*>(a2));
  DEBUG_PRINT(dynamic_cast<B*>(a2));
  DEBUG_PRINT(reinterpret_cast<B*>(a2));

  delete a2;
  return EXIT_SUCCESS;
}
```

コンパイルして実行すると、以下のように成る。

```
$ g++ cast_test.cpp
$ ./a.out
a2      :0x55eb8db7ae70
static_cast<B*>(a2)     :0x55eb8db7ae68
dynamic_cast<B*>(a2)    :0
reinterpret_cast<B*>(a2)        :0x55eb8db7ae70
```

`static_cast`, `dynamic_cast`, `reinterpret_cast`の計算結果がそれぞれ異なっている。

`static_cast`では、元のアドレス値から8を引た値になった。`A2`と`B`の継承関係から”8″という値が静的に決められている。実行時は変数の中身を見ないでキャストするので、`B`のインスタンスでない`a2`に対しても構わず引き算を実行している。

`dynamic_cast`では、実行時に`a2`の継承関係を調べて結果を決める。`a2`は`B`のインスタンスではないので、動的キャストに失敗して`nullptr`が返る。

`reinterpret_cast`は、計算前後でアドレス値が変化しない。<span class="easy-footnote-margin-adjust" id="easy-footnote-1-499"></span><span class="easy-footnote">[<sup>1</sup>](https://komorinfo.com/blog/cpp-cast/#easy-footnote-bottom-1-499 "厳密に言うと、<code>reinterpret_cast</code>前後でアドレス値が変わるかどうかは処理系依存である。ISO/IEC 14882:2011（C++11）では、<code>reintepret_cast</code>で別の型に変換して、再度<code>reinterpret_cast</code>で元の型に戻しても値が変わらないことだけが記載されている。")</span>`reinterpret_cast`の危険性がよく分かる。
