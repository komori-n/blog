---
author: komori-n
categories:
  - 技術解説
date: "2022-06-15T21:06:29+09:00"
tags:
  - C++
keywords:
  - template
  - C++14
  - メモリ
  - 展開回数
title: 型リストに対する展開回数を抑えたC++テンプレート
relpermalink: blog/template-technique-for-type-list/
url: blog/template-technique-for-type-list/
description: 本記事は、型リストに対する基本的なテンプレートに絞って再帰深度を抑えるテクニックを説明する。
---

## モチベーション

\# 本ページの内容は C++14 を想定して書かれている。C++11 では一部使えない記法が含まれているため注意。

C++でtemplate meta programming（TMP）をするとき、展開深さ上限に達したり、メモリ不足によりエラーになったりすることがしばしばある。このような問題はあまり頻繁に遭遇することはないが、いざ遭遇すると普通の C++ とは異なる感覚が要求されるため頭を悩ませることが多い。

本記事は、型リストに対する基本的なテンプレートに絞って再帰深度を抑えるテクニックを説明する。具体的には、以下の4つのメタ関数を扱う。

- 型がリストに含まれるか（kIsAnyOf）
- 型が何番目にあるか（kFind）
- 条件を満たす型が何番目にあるか（kFindIf）
- N番目の型は何か（NthType）

型リストから型やインデックスを取り出す関数たちである。これらは型リストに対するとても基本的な機能であるが、TMP 初心者にとっては少し頭を悩ませるかもしれない。

いずれの問題についても、以下のような愚直な線形再帰コードを書けば簡単に実現できる。

```cpp
// IsAnyOf<T, Ts...>
//   T ∈ Ts...  -> true
//   otherwise  -> false
template <class T, class... Ts>
constexpr bool kIsAnyOf = false;

template <class T, class... OtherTypes>
constexpr bool kIsAnyOf<T, T, OtherTypes...> = true;

template <class T, class FirstType, class... OtherTypes>
constexpr bool kIsAnyOf<T, FirstType, OtherTypes...> = kIsAnyOf<T, OtherTypes...>;
```

しかし、このような再帰的に template 引数を展開するコードは、引数の型が多くなるとコンパイラの再帰深さ上限に達したり、メモリ不足によるコンパイルエラーになってしまうことがある。例えば、`kIsAnyOf<Hoge<0>, Hoge<1>, ..., Hoge<10000>>` を与えると再帰深さが 10000 に達するため、手元の環境ではコンパイルエラーになってしまった。

```sh
$ g++ -std=c++14 test.cpp
test.cpp:10:56: fatal error: recursive template instantiation exceeded maximum depth of 1024
constexpr bool kIsAnyOf<T, FirstType, OtherTypes...> = kIsAnyOf<T, OtherTypes...>;
```

これは、`kIsAnyOf<Hoge<0>, Hoge<1>, ..., Hoge<10000>>`, `kIsAnyOf<Hoge<0>, Hoge<2>, ..., Hoge<10000>>`, … が再帰的に実体化されてしまうことが原因である。

本ページでは、このような線形再帰を用いずに冒頭で挙げた4つのメタ関数を実現する方法について説明する。

## 型がリストに含まれるか（kIsAnyOf）

### `template <T, Ts...> IsAnyOf`

- `T` が `Ts...` に含まれている → true
- `T` が `Ts...` に含まれていない → false

まずは最も簡単な問題から。`kIsAnyOf` を再帰なしで実現する方法はいくつか考えられる。ここでは、次の `kFind` に拡張しやすい constexpr 関数を使う方法を紹介する。

```cpp
template <class T, class... Ts>
constexpr bool IsAnyOf() {
  const bool bs[] = { std::is_same<T, Ts>::value... };
  for (const auto b : bs) {
    if (b) {
      return true;
    }
  }
  return false;
}

template <class T, class... Ts>
constexpr bool kIsAnyOf = IsAnyOf<T, Ts...>();
```

`Ts...` 全体に `is_same<T, *>` をかけて愚直に for 文で調べるだけである。C++14 で constexpr 関数の要件が緩和されたおかげで、TMP 特有のテクニックを駆使しなくても容易に書けるようになった。言われて見れば簡単だが、TMP 入門記事を読んだばかりの人はついつい格好をつけて冒頭の例のようなコードを書きがちなので注意が必要である。

## 型が何番目にあるか（kFind）

### `template <T, Ts...> kFind`

- `T` が `Ts...` に含まれている → その index を返す
- `T` が `Ts...` に含まれていない → `sizeof...(Ts)` を返す

`kIsAnyOf` では true/false を返していたが、`kFind` では見つけた index を返す。このメタ関数は `kIsAnyOf` と同様に constexpr 関数で実現できる。

```cpp
template <class T, class... Ts>
constexpr std::size_t Find() {
  const bool bs[] = { std::is_same<T, Ts>::value... };
  std::size_t i = 0;
  for (const auto b : bs) {
    if (b) {
      return i;
    }
    ++i;
  }
  return sizeof...(Ts);
}

template <class T, class... Ts>
constexpr std::size_t kFind = Find<T, Ts...>();
```

## 条件を満たす型が何番目にあるか（kFindIf）

### `template <P, Ts...> kFindIf`

- `P<T>::value` は `bool` 値
- `Ts...` に `P<T> == true` となる型が含まれている → その index を返す
- `Ts...` に `P<T> == true` となる型が含まれていない → `sizeof...(Ts)` を返す

`kFindIf` を使う典型的な応用として、型リストの中からあるテンプレート型 `Hoge<Args...>` （`Args...` は任意）が含まれているかどうかの判定に使える。具体的には、条件式 `P` を以下のように定義すればよい。

```cpp
template <class Ts>
struct Hoge {};

template <class T>
struct IsHoge : std::bool_constant<false> {};

template <class... Args>
struct IsHoge<Hoge<Args...>> : std::bool_constant<true> {};
```

このメタ関数も容易に実現できる。初めて見たときは少し戸惑うかもしれないが、template template の文法をしっかり理解していれば難しいことはないはずだ。

```cpp
template <template <class T> class P, class... Ts>
constexpr bool FindIf() {
  const bool bs[] = { P<Ts>::value... };
  std::size_t i = 0;
  for (const auto b : bs) {
    if (b) {
      return i;
    }
    ++i;
  }
  return sizeof...(Ts);
}

template <template <class T> class P, class... Ts>
constexpr bool kFindIf = FindIf<P, Ts...>();
```

`std::is_same` が `P` に置き換わっただけである。本質的には `kIsOneOf`、`kFind`、`kFindIf` のアルゴリズムは同じであるため、`FindIf` で実装を共通化することも可能である。

## N番目の型は何か（NthType）

### `template <I, Ts...> NthType`

- `I` は `std::size_t`
- `Ts...` の `I` 番目の型を返す

先程までとは逆に、型リストの I 番目の型を取ってくる問題である。

STL に詳しい方は `std::tuple_element` を使えばよいと考えるかもしれない。しかし、STL の実装によっては `std::tuple_element` が線形再帰により実現されているため、大量の型を処理したい場合は不向きである[^1]。

[^1]: libstdc++の `tuple_element` は<https://github.com/gcc-mirror/gcc/commit/09aab7e699dcbd79fd64959cf259567bdca94022#diff-c83fa13992f340f6a862cc4955e8c2b97522219ebd2f1c4366c0758e5374c7db>で再帰を使わない実装に変わった。また、clang には `__type_pack_element` という組み込み関数が搭載されており、clang&amp;libc++ 環境なら `std::tuple_element` を使って問題ない

`std::tuple` に頼らず、かつ線形再帰を使わずに実現しようと思うとかなり難しい。このためには、関数テンプレートの型の自動推論とパラメータパックを用いた多重継承を駆使する必要がある。コード例がこちら。

```cpp
template <class T, std::size_t Index>
struct IndexTag {};

template <class... Ts>
struct GetImpl;

template <std::size_t... Indices, class... Ts>
struct GetImpl<std::index_sequence<Indices...>, Ts...> : IndexTag<Ts, Indices>... {};

template <std::size_t Index, class T>
constexpr T Get(IndexTag<T, Index>);

template <std::size_t N, class... Ts>
using NthType = decltype(Get<N>(std::declval<GetImpl<std::index_sequence_for<Ts...>, Ts...>>()));
```

コード行数は短いが、かなり高度なテクニックが用いられている。それぞれ簡潔に役割を説明する。

1. `IndexTag<T, Index>`: `Index` と `T` の対応を記憶するためのタグ
2. `GetImpl<std::index_sequence<...>, Ts...>`: `Ts...` の型をそれぞれ `T[0]`, `T[1]`, … とおくと、 `IndexTag<Ts[0], 0>`, `IndexTag<Ts[1], 1>`, …, を多重継承した型
3. `T Get<Index, T>(IndexTag<T, Index>)`: `IndexTag` から `T` だけ取ってくる空関数。コンパイル時にのみ使用し、実際に呼ばれることはない

これらの補助型を用いることで、`Get<Index>(GetImpl{})` すれば適切な `Get()` の定義が選ばれ、型 `T` が得られるというメカニズムだ[^2]。パラメータパックを展開しながら多重継承する手法を初めて見た方にはかなり分かりづらいコードかもしれない。

[^2]: 厳密に言うと、`std::index_sequence_for<Ts...>` が O(log(n)) アルゴリズムかどうかは実装依存である。ただ、仮に線形時間だったとしても、紹介したコードの方が `std::tuple_element` と比べて定数倍高速化できる

## まとめ

型リストに対し、線形再帰を用いないメタ関数の実現方法を 4 例紹介した。大きく分けて、constexpr 関数で素直に実装する方法と、テンプレートパラメータパックを用いた多重継承で型を推論させる方法の 2 通りがあった。C++14 環境では、基本的にはいずれかのパターンに帰着することを意識していれば大抵のテンプレートは省メモリで書けると思われる。

なお、C++17環境であればこれらに加えて畳み込み式（`(args + ...)`のような式）が使えるので書き方の幅がより広がると考えられる。
