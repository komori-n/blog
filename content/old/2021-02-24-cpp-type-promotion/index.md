---
author: komori-n
draft: true
categories:
  - プログラミング
date: "2021-02-24T14:10:13+09:00"
guid: https://komorinfo.com/blog/?p=1019
id: 1019
image: https://komorinfo.com/wp-content/uploads/2020/09/cpp.png
og_img:
  - https://komorinfo.com/wp-content/uploads/2020/09/cpp.png
permalink: /cpp-type-promotion/
tags:
  - C/C++
title: C++の整数演算における型の昇格
url: cpp-type-promotion/
---

懺悔のメモ。

## 問題のコード

以下のコードを考える。

```
#include <iostream>
#include <cstdlib>

int main(void) {
  std::int32_t x = -10;
  std::uint32_t y = 5;

  auto z = x + y;  // ★
  if (z < 1) {
    std::cout << "z < 1" << std::endl;
  } else {
    std::cout << "z >= 1" << std::endl;
  }

  return 0;
}
```

このコードは `-Wall -Wextra` を付けてビルドすると特にwarningなくビルドできる。しかし、実行してみると予想とは異なる実行結果が得られる。

```
$ g++ -Wall -Wextra test.cpp
$ ./a.out
z >= 1
```

z=-10+5なので、”z &lt; 1″と表示されてほしい。

これは、上記コードの★の部分で暗黙の型変換（Implicit conversions）が行われるためである。

## 型の昇格

詳細な規則は <https://en.cppreference.com/w/c/language/conversion> の「Usual arithmetic conversions」を参照。直感的に表現すると、異なる整数型の2項演算はよりサイズの大きな整数にそろえて型変換が行われるという内容である。一般的な32bit処理系の場合、以下に示す順にサイズが大きくなる<span class="easy-footnote-margin-adjust" id="easy-footnote-1-1019"></span><span class="easy-footnote">[<sup>1</sup>](https://komorinfo.com/blog/cpp-type-promotion/#easy-footnote-bottom-1-1019 "int32_t=int, int64_t=longを仮定して説明している。一般の処理系に対するimplicit conversionの説明は上記ページや規格書を参照")</span>。

- int
- unsigned int
- long
- unsigned long
- …

冒頭のコードの場合だと、int32_tとuint32_tの加算のため、内部的には以下のコードと等価である。

```
uint32_t z = static_cast<uint32_t>(x) + y;  // ★'
```

よって、zの値は4294967291となる<span class="easy-footnote-margin-adjust" id="easy-footnote-2-1019"></span><span class="easy-footnote">[<sup>2</sup>](https://komorinfo.com/blog/cpp-type-promotion/#easy-footnote-bottom-2-1019 "正確には、c++17以前では結果は処理系依存である。c++20以降は <a rel="noreferrer noopener" href="https://cpprefjp.github.io/lang/cpp20/signed_integers_are_twos_complement.html" target="_blank">符号付き整数型が2の補数表現であることを規定</a> しているので、結果は必ず4294967291となる")</span>。

なお、対象の整数型のrankがintよりも小さい場合、一律intに引き上げられてから上記のルールが適用されるので、（一般的な32bit処理系では）以下のコードは正しく動作する。

```
#include <iostream>
#include <cstdlib>

int main(void) {
  std::int16_t x = -10;
  std::uint16_t y = 5;

  auto z = x + y;  // int32_tで計算される
  if (z < 1) {
    std::cout << "z < 1" << std::endl;  // こちらが実行される
  } else {
    std::cout << "z >= 1" << std::endl;
  }

  return 0;
}
```

ビルド時にwarningが出ないので、はまらないよう注意していきたい。
