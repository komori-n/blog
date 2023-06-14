---
author: komori-n
draft: true
categories:
  - プログラミング
date: "2021-05-31T23:04:05+09:00"
guid: https://komorinfo.com/blog/?p=1138
id: 1138
image: https://komorinfo.com/wp-content/uploads/2020/09/cpp.png
og_img:
  - https://komorinfo.com/wp-content/uploads/2020/09/cpp.png
permalink: /std-piecewise-construct/
tags:
  - C/C++
title: std::piecewise_constructの使い方（std::pair）
url: std-piecewise-construct/
---

c++の `std::pair` には `std::piecewise_construct` を渡して要素を直接構築するためのコンストラクタが存在する。このページではこの `std::piecewise_construct` の使い方について簡単にまとめる。

## 使い方

`std::piecewise_construct` は空の構造体 `std::piecewise_construct_t` 型の変数である。

```
namespace std {
  struct piecewise_construct_t {};
  constexpr piecewise_construct_t piecewise_construct {};
}
```

この変数自体は何の効果はない。`std::pair` のコンストラクタでタグとして使うのが基本的な使い方である。

```
namespace std {
  template <typename T1, typename T2>
  template <typename... Args1, typename... Args2>
  pair<T1, T2>::pair(piecewise_construct_t, tuple<Args1...> first_args, tuple<Args2...> second_args);

  // pair<T1, T2>(piecewise_construct, std::make_tuple(a1, a2, a3), std::make_tuple(b1))
  // => {.first = T1{a1, a2, a3}, .second = T2{b1}} のイメージ
}
```

第一要素を `first_args` から、第二要素を `second_args` からそれぞれ直接構築したpairをコンストラクトする<span class="easy-footnote-margin-adjust" id="easy-footnote-1-1138"></span><span class="easy-footnote">[<sup>1</sup>](https://komorinfo.com/blog/std-piecewise-construct/#easy-footnote-bottom-1-1138 "本筋には全く関係ないが、tupleを展開してコンストラクタを起動するには工夫が必要である。</p>

template &lt;typename... Args, size_t... Indices>
T ConstructImpl(std::tuple&lt;Args...> t, std::index_sequence&lt;Indices...>) {
return T(std::get&lt;Indices>(t)...);
}

template &lt;typename... Args>
T Construct(std::tuple&lt;Args...> t) {
return ConstructImpl(t, std::index_sequence_for&lt;Args...>());
}</pre>

<p>上記のコードのように、<code>std::index_sequence_for</code> で0, &#8230;, n-1のインデックスを作り、<code>std::get</code>で一つずつ取り出せばよい。")</span>。それぞれ事前に作っておいてmoveコンストラクタで渡せばいいと思われるかもしれないが、moveできないクラスやmoveのオーバーヘッドが大きいクラスをpairの要素にしたい場合に有用である<span class="easy-footnote-margin-adjust" id="easy-footnote-2-1138"></span><span class="easy-footnote">[<sup>2</sup>](https://komorinfo.com/blog/std-piecewise-construct/#easy-footnote-bottom-2-1138 "メンバ変数で std::array で巨大配列を持っているクラスが一例。moveは可能だが配列全体をコピーする必要がある。")</span>。

使用例：

```
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

```
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
