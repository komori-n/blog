---
author: komori-n
draft: true
categories:
  - tips
date: "2021-05-29T16:56:08+09:00"
tags:
  - C/C++
  - C++11
  - C++14
title: c++14でできてc++11ではできないことまとめ
relpermalink: blog/cpp14-features/
url: blog/cpp14-features/
description: c++14とc++11の差分まとめ。c++11とc++14を行ったり来たりしている時に確認すると便利。
---

c++14はc++11のマイナーバージョンアップで、c++11やc++17のような目玉となる機能拡張は少ない。そのため、「この書き方ってc++11でも動くんだっけ？」と気にする必要がある。また、開発プロジェクトで使用するコンパイルオプションが何の前触れもなくc++14からc++11に変わりそうになったとき、いつでも「この機能が使えなくなるとビルドが通らなくなる」とか「この機能がないと冗長な書き方になる」のようなことを言えるようにしておく必要がある。

そのため、個人的にc++14で追加された便利機能、ないと困る機能をまとめた。あくまで個人的に必要だと思う機能のリストなので、より正確な情報は [C++14 Overview, C++ FAQ](https://isocpp.org/wiki/faq/cpp14) などを参照。

以下のまとめは、個人的により必要だと思うものから順に並んでいる。

## constexprの制限緩和

c++14からconstexprが使える場面が大幅に増えた。

c++11時代のconstexpr関数には書ける内容に強い制限があった。C++14では、以下のような制限緩和が行われた。

> ・変数宣言を許可
> ・if文とswitch文を許可
> ・全てのループ文を許可(`for`文、範囲`for`文、`while`文、`do-while`文)
> ・変数の書き換えを許可
> ・戻り値型(リテラル型)として、`void`を許可
> ・`constexpr`非静的メンバ関数の、暗黙の`const`修飾を削除
>
> <https://cpprefjp.github.io/lang/cpp14/relaxing_constraints_on_constexpr.html>

この制限緩和により、メモリ確保を行わない関数やクラスのほとんど全てをconstexpr化できるようになった。個人的には、これだけでもc++14を使う理由になるほど画期的な変更だと思う。

なお、上で引用した制限緩和のうち、最後の項目はc++11と行き来する可能性のあるコードでは注意が必要である。

```cpp
struct Hoge{
  // c++11: 暗黙的に const 修飾される
  // c++14: const 修飾されない
  constexpr int func(int x);

  // c++11: エラー！明示的に const 修飾してはいけない
  // c++14: OK. c++11時代の上の宣言と同じ意味
  constexpr int func(int x) const;
};
```

c++11で動いていたコードがc++14で動かなくなるわけではないが、メンバ関数に対するconst修飾に破壊的変更が加えられている。

## lambda式の初期化キャプチャ

lambda式のキャプチャで、代入キャプチャ、参照キャプチャに加えて初期化キャプチャができるようになった。

```cpp
#include <memory>

int main() {
  std::unique_ptr<int> p = std::make_unique(334);

  // pをmove初期化してラムダ式に所有権を移す
  auto func = [p=std::move(p)]() {
    std::cout << *p << std::endl;
  };
  func();

  return 0;
}
```

特に、unique_ptrやfuture, promiseのようにコピーができない（moveしかできない）変数をキャプチャする時に重宝する。上記のコードは、c++11までの機能で表現すると、以下のコードとほぼ等価である[^1]。

[^1]: mutableをつけないlambda式は、キャプチャした変数をを書き換えることができない。`operator()` がconst修飾されているイメージである。

```cpp
#include <memory>

class TmpStruct {
public:
  TmpStruct(std::unique_ptr<int> p) : p_(p) {}
  void operator()() const {
    std::cout << *p_ << std::endl;
  }

private:
  std::unique_ptr<int> p_;
};

int main() {
  std::unique_ptr<int> p = std::make_unique(334);
  auto func = TmpStruct(std::move(p));
  func();

  return 0;
}
```

使える場面は限られていると思われるかもしれないが、unique_ptrやpromiseに関連するコールバックを書きたい場合、この機能がないと非常に冗長なコードになってしまう。そのため、個人的にないと困る機能だと考えている。

## 数値リテラルの桁区切り

c++14から `'` で数値リテラルの桁を区切れるようになった。

```cpp
constexpr unsigned long long kMask = 0xffff'ffff'ffff'ff00ULL;
```

このコードのように、64ビット変数でマスクを書くとき桁数を間違える事故を減らすことができる。地味ながら、ないと不便。

## std::make_uniqueの追加

`std::make_shared` はc++11で追加されたのに対し、 `std::make_unique` はc++14で遅れて追加された。そのため、c++11で `std::unique_ptr` の初期化を行う場合は以下のように書く必要がある。

```cpp
#include <memory>

int main() {
  auto p = std::unique_ptr<int>(new int);
}
```

生ポインタを渡しているので少し不安が残る。上記のコードほど単純であれば問題ないが、複雑なコードになるとバグが混入する可能性が高まるのでできれば生ポインタを扱うのは避けたい。

c++11環境でも以下のように簡単に自作はできる。

```cpp
template <T, typename Args...>
std::unique_ptr<T> make_unique(Args&& args...) {
  return std::unique_ptr<T> {new T(std::forward<Args>(args)...)};
}
```

ただ個人的には、make_uniqueは様々な箇所で使用するので、標準ライブラリから提供されたものを使いたいというお気持ちがある。make_uniqueを使うだけでも、c++11からc++14へ移行する理由としては十分だと思う。

## `<type_traits>`への \_t 版クラステンプレートの追加

&lt;type_traits&gt; の `XXX<T>::type` で結果を参照するクラステンプレートに対し、 `XXX_t<T>` というクラスが新たに追加された。一見すると文字数が4文字減るだけに見えるが、推論後の型を直接参照できるようになるので以下のように `typename` を省けるようになる。

```cpp
#include <type_traits>

// T が整数型のときのみ定義されてほしい
// c++11
template <typename T>
auto twice(T t) -> typename std::enable_if<std::is_integral<T>::value, T>::type {
    return 2 * t;
}

// c++14
template <typename T>
auto twice(T t) -> std::enable_if_t<std::is_integral<T>::value, T> {
    return 2 * t;
}
```

できることはほとんど変わらないかもしれないが、これがあれば可読性が少しだけ向上する。

## std::nullptr_tをテンプレートパラメータとして許可

c++14からは `std::nullptr_t` をテンプレートパラメータとして使用できるようになる。何に使うかピンとこないかもしれないが、SFINAEでクラスのメンバ関数を実体化抑制したい場合に有用である。

詳しくは以下の記事を参照。

{{< article link="blog/sfinae-template-class/" >}}

## 2進数リテラル

`0b` または `0B` で2進数リテラルを書けるようになった。

```cpp
int x = 0b101001110;
```

ただ、GCCやClangを始めとする主要なコンパイラでは古くからサポートされているので、多くの環境ではc++11以前から使えるはず。実際、手元の環境ではc++11でも2進数リテラルが問題なく使えた。

```sh
$ cat test.cpp
#include <iostream>

int main() {
  std::cout << 0b101001110 << std::endl;
}
$ g++ --version
g++ (Ubuntu 9.3.0-17ubuntu1~20.04) 9.3.0
Copyright (C) 2019 Free Software Foundation, Inc.
This is free software; see the source for copying conditions.  There is NO
warranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

$ g++ -std=c++11 test.cpp
$ ./a.out
334
$ clang++ --version
clang version 7.0.1-12 (tags/RELEASE_701/final)
Target: x86_64-pc-linux-gnu
Thread model: posix
InstalledDir: /usr/bin
$ clang++ -std=c++11 test.cpp
$ ./a.out
334
```
