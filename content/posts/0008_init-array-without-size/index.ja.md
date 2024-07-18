---
author: komori-n
categories:
  - 技術解説
date: 2024-07-18T21:59:43+09:00
tags:
  - C++
keywords:
  - std::array
  - 配列
  - 要素数
  - 初期化
  - to_array
  - CATD
title: std::arrayで要素数を省略して初期化する
relpermalink: blog/init-array-without-size
url: blog/init-array-without-size
description: 本記事では、`std::array` で要素数を明示的に指定することなく初期化する方法について解説する。
---

`std::array` で要素数を明示的に指定することなく初期化する方法について解説する。

## 背景

以下のようなコードを考える。

```cpp
const std::array<int, 3> x = {3, 3, 4};
```

後で気が変わって最後の要素がいらなくなった場合、以下のような変更をしてしまう恐れがある。

```cpp
const std::array<int, 3> x = {3, 3};  // -> {3, 3, 0}
```

配列サイズが3なのに対し、与えられた初期化パラメータの長さが2であるため、
初期値を与えられなかった要素はすべて0で値初期化される。

C言語の配列では配列の要素数を省略して自動で推定させることができるが、
`std::array` ではできないため問題を回避するためには少し工夫をする必要がある。

```cpp
const int x[]           = {3, 3, 4};  // ok
const std::array<int> x = {3, 3, 4};  // error
```

## 推論補助(C++17)

まず、C++17以降であれば推論補助が使える。

```cpp
namespace std {
template <class T, class... U>
array(T, U...) -> array<T, 1 + sizeof...(U)>;
}
```

この機能を使い `std::array` のテンプレート引数を2つとも推論させることで、添字変え忘れ問題を回避できる。

```cpp
const std::array x = {3, 3, 4};  // -> std::array<int, 3> に推論される
const std::array y = {3, 3};     // -> std::array<int, 2> に推論される
```

ただし、可変長テンプレートパラメータ `U...` がすべて `T` と一致していなければこの推論補助は使えない。
この点はC言語配列の初期化とは異なるので注意する必要がある。

```cpp
const double x[]   = {3.0, 3.0f, 4};  // ok
const std::array x = {3.0, 3.0f, 4};  // error. 引数の型がすべて同じではない
```

## std::to_array(C++20) / to_array自作(C++14)

C++20以降であれば、関数テンプレート `std::to_array` を使って初期化をすることで要素数の記載を省ける。
`std::to_array` を使うメリットとして、明示的に型を指定できるのでパラメータの型が一貫していなくても
問題なく初期化を行うことができる。

```cpp
const std::array x = std::to_array({3, 3, 4});               // ok
const std::array y = std::to_array<double>({3.0, 3.0f, 4});  // ok
```

`std::to_array` のやっていることはC言語配列を `std::array` に変換しているだけなので、
簡単に自作することができる[^default-constructible]。

[^default-constructible]: `T` がデフォルト構築可能とは限らないので、
`for` 文で要素を1つずつ初期化する方法は取れない。そのため、
パラメータパック展開で全要素を一気に初期化するコードになっている

```cpp
namespace detail {
template <typename T, std::size_t N, std::size_t... I>
constexpr std::array<T, N> to_array_impl(const T (&list)[N], std::index_sequence<I...>) {
  return {list[I]...};
}

template <typename T, std::size_t N, std::size_t... I>
constexpr std::array<T, N> to_array_impl(T (&&list)[N], std::index_sequence<I...>) {
  return {std::move(list[I])...};
}
} // namespace detail

template <typename T, std::size_t N>
constexpr std::array<T, N> to_array(const T (&list)[N]) {
  return detail::to_array_impl(list, std::make_index_sequence<N>{});
}

template <typename T, std::size_t N>
constexpr std::array<T, N> to_array(T (&&list)[N]) {
  return detail::to_array_impl(std::move(list), std::make_index_sequence<N>{});
}
```
