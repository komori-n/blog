---
author: komori-n
draft: true
categories:
  - プログラミング
date: "2022-06-15T21:06:29+09:00"
guid: https://komorinfo.com/blog/?p=1658
id: 1658
image: https://komorinfo.com/wp-content/uploads/2022/02/cropped-25806739-1-1.png
og_img:
  - https://komorinfo.com/wp-content/uploads/2022/02/cropped-25806739-1-1.png
permalink: /template-technique-for-type-list/
tags:
  - C/C++
title: 型リストに対する展開回数を抑えたC++テンプレート
url: template-technique-for-type-list/
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

```
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

```
$ g++ -std=c++14 test.cpp
test.cpp:10:56: fatal error: recursive template instantiation exceeded maximum depth of 1024
constexpr bool kIsAnyOf<T, FirstType, OtherTypes...> = kIsAnyOf<T, OtherTypes...>;
```

これは、`kIsAnyOf<Hoge<0>, Hoge<1>, ..., Hoge<10000>>`, `kIsAnyOf<Hoge<0>, Hoge<2>, ..., Hoge<10000>>`, … が再帰的に実体化されてしまうことが原因である。

本ページでは、このような線形再帰を用いずに冒頭で挙げた4つのメタ関数を実現する方法について説明する。

## 型がリストに含まれるか（kIsAnyOf）

<div class="wp-block-vk-blocks-border-box vk_borderBox vk_borderBox-background-transparent is-style-vk_borderBox-style-solid-kado-tit-onborder"><div class="vk_borderBox_title_container">#### `template <T, Ts...> IsAnyOf`

</div><div class="vk_borderBox_body">- `T` が `Ts...` に含まれている → true
- `T` が `Ts...` に含まれていない → false

</div></div>まずは最も簡単な問題から。`kIsAnyOf` を再帰なしで実現する方法はいくつか考えられる。ここでは、次の `kFind` に拡張しやすい constexpr 関数を使う方法を紹介する<span class="easy-footnote-margin-adjust" id="easy-footnote-1-1658"></span><span class="easy-footnote">[<sup>1</sup>](https://komorinfo.com/blog/template-technique-for-type-list/#easy-footnote-bottom-1-1658 "以下は最近知ったおしゃれなコード。<code>&lt;..., false&gt;</code> と <code>&lt;false, ...&gt;</code> を比較することで <code>...</code> がすべて <code>false</code> かどうかを判定できる。</p>

template &lt;bool... Bs>
struct BoolList {};

template &lt;class T, class... Ts>
constexpr bool kIsAnyOf = !std::is_same&lt;
BoolList&lt;std::is_same&lt;T, Ts>::value..., false>,
BoolList&lt;false, std::is_same&lt;T, Ts>::value...>
\>::value;</pre>

<p>")</span>。

```
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

<div class="wp-block-vk-blocks-border-box vk_borderBox vk_borderBox-background-transparent is-style-vk_borderBox-style-solid-kado-tit-onborder"><div class="vk_borderBox_title_container">#### `template <T, Ts...> kFind`

</div><div class="vk_borderBox_body">- `T` が `Ts...` に含まれている → その index を返す
- `T` が `Ts...` に含まれていない → `sizeof...(Ts)` を返す

</div></div>`kIsAnyOf` では true/false を返していたが、`kFind` では見つけた index を返す。このメタ関数は `kIsAnyOf` と同様に constexpr 関数で実現できる。

```
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

<div class="wp-block-vk-blocks-border-box vk_borderBox vk_borderBox-background-transparent is-style-vk_borderBox-style-solid-kado-tit-onborder"><div class="vk_borderBox_title_container">#### `template <P, Ts...> kFindIf`

</div><div class="vk_borderBox_body">- `P<T>::value` は `bool` 値
- `Ts...` に `P<T> == true` となる型が含まれている → その index を返す
- `Ts...` に `P<T> == true` となる型が含まれていない → `sizeof...(Ts)` を返す

</div></div>`kFindIf` を使う典型的な応用として、型リストの中からあるテンプレート型 `Hoge<Args...>` （`Args...` は任意）が含まれているかどうかの判定に使える。具体的には、条件式 `P` を以下のように定義すればよい。

```
template <class Ts>
struct Hoge {};

template <class T>
struct IsHoge : std::bool_constant<false> {};

template <class... Args>
struct IsHoge<Hoge<Args...>> : std::bool_constant<true> {};
```

このメタ関数も容易に実現できる。初めて見たときは少し戸惑うかもしれないが、template template の文法をしっかり理解していれば難しいことはないはずだ。

```
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

<div class="wp-block-vk-blocks-border-box vk_borderBox vk_borderBox-background-transparent is-style-vk_borderBox-style-solid-kado-tit-onborder"><div class="vk_borderBox_title_container">#### `template <I, Ts...> NthType`

</div><div class="vk_borderBox_body">- `I` は `std::size_t`
- `Ts...` の `I` 番目の型を返す

</div></div>先程までとは逆に、型リストの I 番目の型を取ってくる問題である。

STL に詳しい方は `std::tuple_element` を使えばよいと考えるかもしれない。しかし、STL の実装によっては `std::tuple_element` が線形再帰により実現されているため、大量の型を処理したい場合は不向きである<span class="easy-footnote-margin-adjust" id="easy-footnote-2-1658"></span><span class="easy-footnote">[<sup>2</sup>](https://komorinfo.com/blog/template-technique-for-type-list/#easy-footnote-bottom-2-1658 "libstdc++の <code>tuple_element</code> は<a rel="noreferrer noopener" href="https://github.com/gcc-mirror/gcc/commit/09aab7e699dcbd79fd64959cf259567bdca94022#diff-c83fa13992f340f6a862cc4955e8c2b97522219ebd2f1c4366c0758e5374c7db" target="_blank">少し前のコミット</a> で再帰を使わない実装に変わった。また、clang には <code>\_\_type_pack_element</code> という組み込み関数が搭載されており、clang&amp;libc++ 環境なら <code>std::tuple_element</code> を使って問題ない")</span> <span class="easy-footnote-margin-adjust" id="easy-footnote-3-1658"></span><span class="easy-footnote">[<sup>3</sup>](https://komorinfo.com/blog/template-technique-for-type-list/#easy-footnote-bottom-3-1658 "実は libstdc++ の <code>std::get</code> は 再帰を使わない実装になっているので、<code>decltype(std::get<Index>(...))</code> でも効率的に型を求めることができる（ライブラリ依存の実装なのであまりおすすめしない）")</span>。

`std::tuple` に頼らず、かつ線形再帰を使わずに実現しようと思うとかなり難しい。このためには、関数テンプレートの型の自動推論とパラメータパックを用いた多重継承を駆使する必要がある。コード例がこちら。

```
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

これらの補助型を用いることで、`Get<Index>(GetImpl{})` すれば適切な `Get()` の定義が選ばれ、型 `T` が得られるというメカニズムだ<span class="easy-footnote-margin-adjust" id="easy-footnote-4-1658"></span><span class="easy-footnote">[<sup>4</sup>](https://komorinfo.com/blog/template-technique-for-type-list/#easy-footnote-bottom-4-1658 "厳密に言うと、<code>std::index_sequence_for<Ts...></code> が O(log(n)) アルゴリズムかどうかは実装依存である。ただ、仮に線形時間だったとしても、紹介したコードの方が <code>std::tuple_element</code> と比べて定数倍高速化できる")</span> 。パラメータパックを展開しながら多重継承する手法を初めて見た方にはかなり分かりづらいコードかもしれない。

## まとめ

型リストに対し、線形再帰を用いないメタ関数の実現方法を 4 例紹介した。大きく分けて、constexpr 関数で素直に実装する方法と、テンプレートパラメータパックを用いた多重継承で型を推論させる方法の 2 通りがあった。C++14 環境では、基本的にはいずれかのパターンに帰着することを意識していれば大抵のテンプレートは省メモリで書けると思われる。

なお、C++17環境であればこれらに加えて畳み込み式（`(args + ...)`のような式）が使えるので書き方の幅がより広がると考えられる。
