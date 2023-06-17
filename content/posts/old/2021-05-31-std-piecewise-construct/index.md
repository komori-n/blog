---
author: komori-n
categories:
  - 技術解説
date: "2021-05-31T23:04:05+09:00"
tags:
  - C++
keywords:
  - pair
  - piecewise_construct
  - map
  - 直接構築
title: std::piecewise_constructの使い方（std::pair）
relpermalink: blog/std-piecewise-construct/
url: blog/std-piecewise-construct/
---

c++の `std::pair` には `std::piecewise_construct` を渡して要素を直接構築するためのコンストラクタが存在する。このページではこの `std::piecewise_construct` の使い方について簡単にまとめる。

## 使い方

`std::piecewise_construct` は空の構造体 `std::piecewise_construct_t` 型の変数である。

```cpp
namespace std {
  struct piecewise_construct_t {};
  constexpr piecewise_construct_t piecewise_construct {};
}
```

この変数自体は何の効果はない。`std::pair` のコンストラクタでタグとして使うのが基本的な使い方である。

```cpp
namespace std {
  template <typename T1, typename T2>
  template <typename... Args1, typename... Args2>
  pair<T1, T2>::pair(piecewise_construct_t, tuple<Args1...> first_args, tuple<Args2...> second_args);

  // pair<T1, T2>(piecewise_construct, std::make_tuple(a1, a2, a3), std::make_tuple(b1))
  // => {.first = T1{a1, a2, a3}, .second = T2{b1}} のイメージ
}
```

第一要素を `first_args` から、第二要素を `second_args` からそれぞれ直接構築したpairをコンストラクトする。

使用例：

```cpp
#include <iostream>
#include <utility>
#include <tuple>
#include <string>
#include <vector>

int main() {
    std::pair<std::string, std::vector<int>> p {
        std::piecewise_construct,
        std::make_tuple("AAA"),
        std::make_tuple(4, 0)
    };

    std::cout << p.first << " " << p.second.size() << std::endl;
    // => AAA 4
}
```

実用上、pairへ要素を直接構築したくなることがあるのかと疑問に思われるかもしれない。しかし、piecewise_constructは `std::map`（ `std::unordered_map` や `std::multimap` なども同様）への要素挿入時に便利に使えるのである。

```cpp
#include <iostream>
#include <utility>
#include <tuple>
#include <string>
#include <vector>
#include <map>

int main() {
    std::map<std::string, std::vector<int>> m;

    m.emplace(
        std::piecewise_construct,
        std::make_tuple("AAA"),
        std::make_tuple(4, 0)
    );

    for (auto&& p : m) {
        std::cout << p.first << " " << p.second.size() << std::endl;
    }
    // => AAA 4
}
```

`map::emplace` は木の要素を直接構築する関数である。受け取った引数を内部では `std::pair<Key, Value>` へ横流しするので、`std::piecewise_construct` を活用してmapの要素を直接構築できるのである。

なお、`std::piecewise_construct` は `std::pair` 限定の機能で `std::tuple` では使えない。map要素を直接構築するために導入された機能なので、tupleには不要だと考えられて導入が見送られたのだろう。
