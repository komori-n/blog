---
author: komori-n
draft: true
categories:
  - tips
date: "2021-07-30T22:42:17+09:00"
tags:
  - C/C++
title: 3要素以上のstd::min, std::maxを取る
relpermalink: blog/cpp-3-element-max/
url: blog/cpp-3-element-max/
description: std::min、std::maxはinitializer listを受け取ることができるので、3要素以上の比較にも使える。
---

c++03の知識で止まっていたので懺悔のメモ。

`std::min`, `std::max`, `std::minmax` で3要素以上にわたる演算をしたい場合は、`std::initializer_list<T>` 型を引数に取るオーバーロードを用いればよい。

```cpp
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
