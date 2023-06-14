---
author: komori-n
draft: true
categories:
  - プログラミング
date: "2021-07-30T22:42:17+09:00"
guid: https://komorinfo.com/blog/?p=1360
id: 1360
image: https://komorinfo.com/wp-content/uploads/2020/09/cpp.png
og_img:
  - https://komorinfo.com/wp-content/uploads/2020/09/cpp.png
permalink: /cpp-3-element-max/
tags:
  - C/C++
title: 3要素以上のstd::min, std::maxを取る
url: cpp-3-element-max/
---

c++03の知識で止まっていたので懺悔のメモ。

`std::min`, `std::max`, `std::minmax` で3要素以上にわたる演算をしたい場合は、`std::initializer_list<T>` 型を引数に取るオーバーロードを用いればよい<span class="easy-footnote-margin-adjust" id="easy-footnote-1-1360"></span><span class="easy-footnote">[<sup>1</sup>](https://komorinfo.com/blog/cpp-3-element-max/#easy-footnote-bottom-1-1360 "この機能を知るまでは <code>std::max(std::max(3, 3), 4)</code> したり可変長引数のmaxを自作したりしていた")</span>。

```
#include <algorithm>
#include <iostream>

int main() {
  std::cout << std::max({3, 3, 4}) << std::endl;
  // => 4

  int x = 2;
  int y = 6;
  int z = 4;
  std::cout << std::min({x, y, z}) << std::endl;
  // => 2
}
```

参考：[max – cpprefjp C++日本語リファレンス](https://cpprefjp.github.io/reference/algorithm/max.html)
