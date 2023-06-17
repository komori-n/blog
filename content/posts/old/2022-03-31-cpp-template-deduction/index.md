---
author: komori-n
draft: true
categories:
  - tips
date: "2022-03-31T22:48:33+09:00"
tags:
  - C/C++
title: C++で型推論結果を手っ取り早く知りたいとき
relpermalink: blog/cpp-template-deduction/
url: blog/cpp-template-deduction/
description: C++のtemplateまわりのビルドエラーに立ち向かっているとき、templateの型推論結果をぱっと知る方法について説明する。
---

C++のtemplateまわりのビルドエラーに立ち向かっているとき、templateの型推論結果をぱっと知りたくなることがしばしばある。

```cpp
template <typename T, typename U = /* template 黒魔術（略） */>
void Hoge(T&& t) {
  // このあたりでバグっている場合を考える
  // 原因を探るために U がどう推論されているか知りたい
}
```

このような状況のとき、型推論の結果を手っ取り早く知る方法が大きく3つある。

## 実行時情報を見る

`<typeinfo>` や `<boost/type_index.hpp>` により、実行時に型情報を print させれば型を知ることができる。

```cpp
#include <typeinfo>
#include <iostream>
#include <type_traits>

template <typename T, typename U = std::conditional_t<std::is_integral_v<T>, int, double>>
void Hoge(T&& t) {
  std::cout << typeid(T).name() << std::endl;
}

int main() {
  Hoge(334);
}
```

実行結果

```sh
$ ./a.out
i
```

よい点

- 邪道な手段を用いずに実現できる

よくない点

- 出力される型がマングルされた文字列で出力されるため分かりづらい
- コンパイルできるコードでしか使えない
- 実行して該当パスを通す必要がある
- 型推論結果が標準出力に出る

## 型推論をわざと失敗させる

Effective Modern C++で紹介されている方法。実体のないtemplateクラスに型を入れて、わざとコンパイルエラーを発生させることにより型を特定する。

```cpp
#include <typeinfo>
#include <iostream>
#include <type_traits>

template <typename T>
class TypeOf;


template <typename T, typename U = std::conditional_t<std::is_integral_v<T>, int, double>>
void Hoge(T&& t) {
  TypeOf<U> x;  // error: implicit instantiation of undefined template 'TypeOf<int>'
}

int main() {
  Hoge(334);
}
```

よい点

- コンパイルが通らないコードでも使える（ことが多い）
- 関数ごとにどう推論されたかを追うことができる

よくない点

- 関数コールのネストが深いとき、エラーメッセージが非常に長くなる
- 必ずビルドエラーになる

## \[\[deprecated\]\]にする

個人的におすすめしたいお手軽手法。関数やクラスに `[[deprecated]]` をつけることで、ビルド時に warning を出させることができる。

```cpp
#include <typeinfo>
#include <iostream>
#include <type_traits>

template <typename T, typename U = std::conditional_t<std::is_integral_v<T>, int, double>>
[[deprecated]]
void Hoge(T&& t) {
  // test.cpp:12:9: warning: 'Hoge<int, int>' is deprecated [-Wdeprecated-declarations]
  //        Hoge(334);

}

int main() {
  Hoge(334);
}
```

\[\[deprecated\]\] 属性は C++14 で追加された機能で、機能が非推奨であることをユーザーに知らせるための機能である。多くのコンパイラでは非推奨メッセージに型推論結果も同時に表示してくれる。

よい点

- warningを出すだけなのでビルドエラーにならない
- 必要なタイプ数がかなり少ない

よくない点

- やや環境依存の方法である
- 推論をわざと失敗させる方法と比較して表示されるメッセージが短い
