---
author: komori-n
categories:
  - 技術解説
date: "2022-08-23T22:01:00+09:00"
tags:
  - C++
keywords:
  - swallow
  - 捨てる
  - パック展開
  - C++17
  - anything
title: C++で行儀よくパック展開結果を捨てる
relpermalink: blog/cpp-swallow-idiom/
url: blog/cpp-swallow-idiom/
description: C++でパラメータパックのパック展開結果をお行儀よく捨てる方法のまとめ。
---

C++でパラメータパックのパック展開結果をお行儀よく捨てる方法のまとめ。

## モチベーション

C++のテンプレートメタプログラミング（TMP）を書いていると、パラメータパックに関する式をパック展開しながら評価したくなることがしばしばある。しかし、C++ではパック展開が可能な箇所は限られており、特定の文脈でなければパック展開が許されていない。例えば、以下のようなパック展開は文法違反となりコンパイルが通らない。

```cpp
/// `arr[Indices...]` すべてに 0 を代入する関数
template <int... Indices>
constexpr void Clear(Array& arr) noexcept {
  arr[Indices] = 0...;
  // ↑ error!
  // パラメータパックを何もないところで展開することはできない。
}
```

そのため、パック展開結果を虚空に送るイディオムが必要になる。

以下ではC++17以降とC++14以前に分けてパック展開の評価結果の捨て方を紹介する。C++17以降の方が簡潔にかけるため、まずは前者を説明し、その後にC++14以前向けの方法を紹介する。

### C++17以降

C++17以降の場合は話は単純で、`operator,`の畳み込みで簡単に値を捨てることができる。畳み込み式（Fold Expression）はC++17で導入された文法で、パラメータパックを展開しながら二項演算を再帰的に適用できる。典型的には `+` や `&&` などの演算子と組み合わせて用いられることが多いが、`operator,` に対しても畳み込み式を使うことができる。

```cpp
template <int... Indices>
constexpr void Clear(Array& arr) noexcept {
     ((arr[Indices] = 0), ...);
}
```

上記のコードは `(arr[I0] = 0), ((arr[I1] = 0), ((arr[I2] = 0), ((...` と展開される。このコードはパラメータパックの先頭から順に式を実行し、値を捨てながらパック展開を行うことができる。

このように、C++17以降の環境ではこの後で紹介する黒魔術をすることなくパック展開の結果を捨てることができるのである。

### C++14以前

C++14以前の環境では、パック展開結果を捨てる方法は大きく分けて次の2つしかない。

- 関数の引数 `f(args...)`
- 初期化子リスト `{args...}`

このうち、前者の関数引数に渡す方法はあまりおすすめできない。なぜなら、C++14以前の環境では、関数引数に渡された式の評価順が未規定であるためである。パラメータパックがどのような順番で展開されるかはコンパイラ実装者の気分次第なのである。

```cpp
/// （非推奨） 引数をすべて無視する
template <typename... Args>
constexpr void ConsumeValues(Args&&...) noexcept {}

template <int... Indices>
constexpr void Clear(Array& arr) noexcept {
     ConsumeValues((arr[Indices] = 0)...);
     // ↑ このコード自体は問題ないが、あまりおすすめしない
     // 引数の評価順序が規定されていないため。
}
```

そのため、C++14環境で値を行儀よく捨てるには以下のようなコードがよい。このイディオムは **swallow イディオム**と呼ばれる[^1]。

[^1]: `Anything` ではなく `int` などのプリミティブ型と `operator,` の組み合わせでも swallow イディオムは実現可能だが、コードが読みづらくなるのであまりおすすめしない。

````cpp
/// 任意の値でコンストラクトできる空構造体
struct Anything {
  template <typename T>
  constexpr Anything(T&&) noexcept {}
};

/// `Anything` の初期化子リストを引数に取る空関数
/// `Anything` は任意の型からコンストラクト可能なので、
/// ```
/// ConsumeValues({/* 式1 */, /* 式2 */, ...});
/// ```
/// の要領で値を虚無に捨てることができる。
constexpr void ConsumeValues(std::initializer_list<Anything>) noexcept {}
````

まず、任意の値でコンストラクトできる構造体 `Anything` を定義する。この型は任意の値から暗黙的に型変換できる。よって、`std::initializer_list<Anything>` は任意の値を引数に取ることができる「ゴミ箱」として機能する。

```cpp
ConsumeValues({33, 4, "hoge", 44.5});
/// それぞれの値が Anything に暗黙変換された後、虚空に捨てられる
```

このゴミ箱を用いれば、パラメータパック展開の評価結果を行儀よく捨てることができる。

```cpp
template <int... Indices>
constexpr void Clear(Array& arr) noexcept {
     ConsumeValues({(arr[Indices] = 0)...});
}
```

初期化子リストは先頭から順に評価されるので、このパック展開も同様に先頭から順に評価されることが保証される。

なお、評価結果が `void` になる式は `Anything` に変換できないので、以下のようにカンマ演算子で無理やり評価結果を 0 にすることで値を捨てることができる。

```cpp
template <int... Indices>
constexpr void Func(Array& arr) noexcept {
     ConsumeValues({(Something(arr[Indices]),0)...});
}
```

## まとめ

C++において、行儀よく値を捨てる方法は、それぞれ以下である。

- C++17以降：`operator,` と畳み込み式
- C++14以前：swallowイディオム or C++17以降に乗り換える
