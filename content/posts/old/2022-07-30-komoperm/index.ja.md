---
author: komori-n
draft: true
categories:
  - tips
date: "2022-07-30T20:06:00+09:00"
tags:
  - C/C++
title: コンパイル時に重複のある順列を扱う
relpermalink: blog//komoperm/
url: blog/komoperm/
description: C++のコンパイル時評価を活かし、重複のある順列を計算するための簡単なライブラリを作った。
---

C++のコンパイル時評価を活かし、重複のある順列を計算するための簡単なライブラリを作った。

## 概要

コンパイル時計算に対応した重複のある順列に関する演算を行うライブラリを公開した。

{{< github repo="komori-n/komoperm" >}}

以下のコード例のように、整数型または列挙型の重複順列からそのインデックスを求めたり、逆にインデックスに対応する重複順列を生成することができる。

```cpp
#include "komoperm/komoperm.hpp"

enum Hoge {
    A, B, C,
};

int main() {
    constexpr komoperm::Permutations<Hoge, A, A, A, B, B, C> p;

    static_assert(p.Size() == 60,
        "The number os possible permutations is 60");

    static_assert(p.Index({B, A, B, C, A, A}) < 60,
        "{B, A, B, C, A, A} is a permutation of {A, A, A, B, B, C}");

    static_assert(p.Index(p.Get(10)) == 10,
        "Get() generates the 10th permutation");
}
```

重複順列の集合 `komoperm::Permutations` は型名 `T` と値の列 `Vals...` により定義される。値の列 `Vals...` はソートされている必要はなく、さらに同じ値が連続に並ぶよう並べ替える必要もない。

komopermの特徴として、すべての計算を**コンパイル時**に行うことができる。また、コンパイル時型計算に恩恵により、実行時も高速に動作する。templateの再帰を用いずに実装しているため、コンパイル時のメモリ消費量が比較的小さい。

komopermはC++14の機能だけで実現されている。以下では、C++14 constexpr 対応をするにあたり工夫した点を簡潔に述べたい。なお前提知識として、以前投稿した以下の記事の内容に目を通しておくことを推奨する。

- [SFINAEの制約式を少しだけ読みやすくするConstraints | コウモリのちょーおんぱ](https://komorinfo.com/blog/sfinae-constraints/)
- [型リストに対する展開回数を抑えたC++テンプレート | コウモリのちょーおんぱ](https://komorinfo.com/blog/template-technique-for-type-list/)

## 実装方針

komopermのうち実装が少し難しい点は、順列の生成自体ではなく、入力から以下のような補助型 `PermutationImpl` を作ることである[^1]。

[^1]: 順列の生成自体は簡単だと述べたが、高速化のために [このコード](https://github.com/komori-n/komoperm/blob/main/src/komoperm.hpp#L469-L486) のような少し頭のおかしなことをしている

```cpp
Input:
Permutations<T, Vals...>

Output:
PermutationsImpl<
  T,
  N, // sizeof...(Vals)
  M, // Vals... のうち最も出現頻度の高いものの個数
  ItemCount<
    Val,  // T型の値
    N2,   // Valを含め残り何個並べるか
    C    　// Valを何個並べるか
  >,
  ItemCount<
    // ...
  >
  ...
>
```

`Vals...` をチェックして、それぞれの値 `Val` に対し登場する回数 `C` と残りのシンボル数をカウントし、テンプレート引数に並べた型を作っている。このような型が作れれば、(N choose C1) x (N-C1 choose C2) x (N-C1-C2 choose C3) x … の要領で重複ありの順列に関する計算を容易に行うことができる。

上記の型変換において、`Val`, `N2`, `C` 以外の値は容易に計算可能である。よって、問題になるのはどのようにして入力 `Vals...` から `(Val, N2, C)` を並べた型を作るかということである。

komopermで大まかに以下の手順によりこれを実現している。

1. `Vals...` のうち相違な値が何個あるかを数える
2. `Vals...` をソートする
3. それぞれの `Val` の出現回数、およびそれ以降のシンボル数をカウントする
4. 3. を展開して型を作る

特に、komopermではコード中に template の再帰が1回も登場しない。そのため、メモリ消費量を抑えて高速にコンパイルを行うことができる[^2]。

[^2]: Q. 最初から `Permutations<Item<A, 3>, Item<B, 2>, Item<C, 1>>` のようなインターフェースにしておけば、こんなめんどくさいことをしなくて済むのでは？ → A. それはそう

### 1. `Vals...` のうち相違な値が何個あるかを数える

`Vals...` に含まれる値の種類数をカウントする。この値は、3. においてカウント結果を格納する配列を定義するために用いる。

これは、[型リストに対する展開回数を抑えたC++テンプレート](https://komorinfo.com/blog/template-technique-for-type-list/)の `kFindIf` と同じ要領で容易に実現できる。

### 2. `Vals...` をソートする

この手順は必須ではないが、次の手順の計算量を O(N^2) から O(N) に削減するためにソートを行う。

C++14では `std::sort` は `constexpr` していされていないので、自前で実装する必要がある。komopermではマージソートによりこれを実現した。これも容易に実現できる。

### 3. それぞれの `Val` の出現回数、およびそれ以降のシンボル数をカウントする

`Vals...` を事前にソートしておくことで、各要素の出現回数カウントを O(N) で行える。コードに直すと、大まかに以下のようなコードになる。

```cpp
template <typename T, std::size_t N>
struct ItemArray {
  T values[N];
  std::size_t remains[N];
  std::size_t counts[N];
};

template <typename T, T... Vals>
inline constexpr auto MakeItemCountsImplCalc() noexcept {
  ItemArray<T, UniqueCount<T, Vals...>()> ret{};
  T vals[sizeof...(Vals)]{Vals...};
  bool visited[sizeof...(Vals)]{};

  std::size_t remains = sizeof...(Vals);
  std::size_t max_idx = 0;
  for (std::size_t i = 0; i < sizeof...(Vals); ++i) {
    if (!visited[i]) {
      visited[i] = true;
      ret.values[max_idx] = vals[i];
      std::size_t count = 1;
      for (std::size_t j = i + 1; j < sizeof...(Vals); ++j) {
        if (vals[i] == vals[j]) {
          count++;
          visited[j] = true;
        }
      }
      ret.remains[max_idx] = remains;
      ret.counts[max_idx] = count;

      remains -= count;
      max_idx++;
    }
  }

  assert(max_idx == (UniqueCount<T, Vals...>()));
  assert(remains == 0);

  return ret;
}
```

### 4. 3. を展開して型を作る

これまでの計算により、長さが (`Vals...` のうち相違な値の個数) の以下の3つの配列が得られた。

- 相違な `Val` を並べた配列
- `i+1` 番目以降の値の配置個数
- `i` 番目の `Val` の出現回数

```cpp
constexpr auto value = MakeItemCountsImplCalc<Hoge, A, A, A, B, B, C>();
// == {
//   {A, B, C},
//   {6, 3, 1},
//   {3, 2, 1}
// }
```

ただし、この値を順に並べたような型を定義するためには少し頭の体操が必要である。具体的には、`{A, B, C}`, `{6, 3, 1}`, `{3, 2, 1}` という3つの配列から `(A, 6, 3)`, `(B, 3, 2)`, `(C, 2, 1)` という順で値を取り出してこの順でtemplateパラメータに並べたい。これは、`std::index_sequence` を用いて丁寧にゴリ押すことで実現できる。

```cpp
template <typename T, T... Vals, std::size_t... Indices>
struct MakePermutationsImpl<ValueSet<T, Vals...>,
                            std::index_sequence<Indices...>> {
 private:
  static constexpr auto Impl() noexcept {
    constexpr auto kValue = MakeItemCountsImplCalc<T, Vals...>();
    using type = PermutationsImpl<
        T, sizeof...(Vals), std::max({kValue.counts[Indices]...}),
        ItemCount<T, kValue.values[Indices], kValue.remains[Indices],
                  kValue.counts[Indices]>...>;
    return type{};
  }

 public:
  using type = decltype(Impl());
};
```

`Indices=0..X` を補助的に使い、`ItemCount<values[Indices], remain[Indices], counts[Indices]>...` という `Indices...` に対するパラメータパック展開に帰着することで強引に `ItemCount<>` を並べた型を作ることができる。

## まとめ

コンパイル時に重複を含む順列を扱うためのテクニックについて紹介した。c++テンプレートの頭痛ポイントが伝われば幸いである。
