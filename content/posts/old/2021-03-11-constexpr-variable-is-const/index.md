---
author: komori-n
draft: true
categories:
  - tips
date: "2021-03-11T18:21:04+09:00"
tags:
  - C/C++
  - constexpr
title: constexpr宣言された変数は暗黙的にconstになる
permalink: blog/constexpr-variable-is-const/
url: blog/constexpr-variable-is-const/
description: constexpr宣言された変数は暗黙的にconstexprとなるが、constの付く位置に注意。
---

constexprはc++11で導入されたキーワードで、変数や関数が定数式（Constant Expressions）であることを宣言することができる。

constexpr変数はコンパイル時に値が定まるので、template parameterや配列宣言時のサイズ指定に使用できる。

```cpp
constexpr size_t N = 10;
std::array<int, N> hoge;
int fuga[N];
```

一言でいうと、`const` は値や戻り値が書き換え不可であることを宣言するのに対し、 `constexpr` は値や戻り値がROM化可能であることを宣言する。

constexprが付与された変数は、暗黙的にconstも付与される。

```cpp
// 以下の2つは等価
constexpr int N = 334;
constexpr const int N = 334;
```

しかし、ポインタ型に対しconstexprをつける時は注意が必要である。

```cpp
int x = 0;
// 以下の2つは等価
constexpr int* p = &x;
constexpr int* const p = &x;

// 以下は上の2式とは等価でない
constexpr const int* p = &x;
```

constexprは対象の変数がROM化可能（すなわち書き換え不可）であることを宣言するので、constが付与されるのは `*` の後になる。言い換えると、上記の例の場合、`p` 自体を実行時に変えることはできないが、 `*p` を通じて `x` の値を書き換えることはできるのである。

```cpp
int x = 0;
int main(void) {
    int y = 10;
    constexpr int* p = &x;

    // OK: pの指す先の値を変えることができる
    *p = 20;

    // NG: p自体を変えることはできない
    // p = &y;

    // 参照でも同じ。
    constexpr int& r = x;

    // OK: rの指す先の値を変えることができる
    r = 30;

    return 0;
}
```

まとめると、以下のようになる。

- `constexpr` 宣言された変数は自動的に `const` 宣言されたことになる
- ただし、ポインタや参照が絡む場合、指す先の値を書き換えることはできる

## 参考

- [c++ – constexpr const vs constexpr variables? – Stack Overflow](https://stackoverflow.com/questions/28845058/constexpr-const-vs-constexpr-variables)
- [c++ – Difference between `constexpr` and `const` – Stack Overflow](https://stackoverflow.com/questions/14116003/difference-between-constexpr-and-const)
