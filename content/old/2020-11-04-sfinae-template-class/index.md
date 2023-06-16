---
author: komori-n
draft: true
categories:
  - tips
date: "2020-11-04T20:28:02+09:00"
tags:
  - C/C++
  - SFINAE
title: SFINAEでtemplate classのメンバ関数の実体化を制御する
relpermalink: blog/sfinae-template-class/
url: blog/sfinae-template-class/
description: C++のSFINAEの代表的な使い方の一つである。メンバ関数実体化抑制の使い方について説明する。
---

## 問題設定

SFINAE[^1]を用いて、template classのメンバ関数を実体化したりしなかったりしたい。例えば、typenameが`void`の時は実体化する関数を抑制したり、typenameに応じて関数を呼び分けてほしい場合が考えられる。

[^1]: SFINAE(Substitution Failure Is Not An Error)は、C++の黒魔術の一つ。template実体化時にうまく代入できなかった場合、コンパイルエラーとはならず単に無視してくれる機能である。

普通のSFINAEの感覚だと以下のように書いてみたくなるが、これだとコンパイルエラーになる。

```cpp
template <typename T>
struct Hoge {
  // void用の関数
  auto func(void)
  -> std::enable_if_t<std::is_same<T, void>::value, void> {
    std::cout << "void" << std::endl;
  }

  // 非void用の関数
  auto func(void)
  -> std::enable_if_t<!std::is_same<T, void>::value, void> {
    std::cout << "not void" << std::endl;
  }
};
```

SFINAEはtemplateのsubstitution failureを無視してくれる機能なので、template classであっても非templateメンバ関数の実体化に失敗すると普通にエラーになる。

SFINAEはtemplateに関する機能なので、メンバ関数をtemplateメンバ関数化して回避しなければならない。回避の仕方は大きく分けて3通り。後に紹介する方法ほどおすすめの方法である。

本ページのサンプルコードは以下の場所にある。
[member-sfinae-1.cpp](https://gist.github.com/komori-n/086c8d369fbfde0f06e947696c6d11ca)

## 方法1｜Dummyのtemplateを使う

よく目にするのはこの形式である。`U`という変数（デフォルト値は`T`）を導入してsubstitution failureの形にする。

```cpp
template <typename T>
struct Hoge {
  template <typename U=T>
  auto func(void)
  -> std::enable_if_t<std::is_same<U, void>::value, void> {
    std::cout << "void" << std::endl;
  }

  template <typename U=T>
  auto func(void)
  -> std::enable_if_t<!std::is_same<U, void>::value, void> {
    std::cout << "not void" << std::endl;
  }
};
```

`std::is_same<U, void>::value`は`U`によって値が変わる。したがって、メンバ関数`func`の戻り値も`U`の値が決まるまで分からないので、SFINAEの対象になる。

この方法のメリットは可読性が高いこと。SFINAE特有の読みにくさはあるが、ぱっと見て分かりやすいコードになる。

一方で、この方法のデメリットは、利用者が誤用する余地が残ることである。

```cpp
int main(int argc, char* argv[]) {
  Hoge<int> hoge;
  hoge.func<void>();  // void用の関数が呼ばれてしまう

  return 0;
}
```

`U`のデフォルト値が`T`だが、呼び出し側はこのtemplate parameterを自由に設定することもできる。そのため、上記のように設計者が意図しない関数が呼ばれる可能性がある。

## 方法2｜dummyのbool変数を持たせる

SFINAEで実体化抑制させるだけなら、template変数はtypenameでなくてもよい。例えば、必ず`true`になるbool変数を用いる方法が考えられる。

```cpp
template <typename T>
struct Hoge {
  template <bool AlwaysTrue = true>
  auto func(void)
  -> std::enable_if_t<std::is_same<U, void>::value && AlwaysTrue, void> {
    std::cout << "void" << std::endl;
  }

  template <bool AlwaysTrue = true>
  auto func(void)
  -> std::enable_if_t<!std::is_same<U, void>::value && AlwaysTrue, void> {
    std::cout << "not void" << std::endl;
  }
};

```

`std::is_same::value && AlwaysTrue`は`AlwaysTrue`の値が決まるまで戻り値の型が決まらないので、SFINAEによる実体化抑制ができる。

方法1と比較すると、bool変数を用いる方法は誤用される心配はない。もし`AlwaysTrue`に`false`がセットされた場合、実体化に失敗して呼び出せなくなるためである。

```cpp
int main(int argc, char* argv[]) {
  Hoge<int> hoge;
  hoge.func<false>();  // Error! 呼び出し候補の関数がない

  return 0;
}
```

ただし、実体化できないとはいえ、template関数に`false`を代入できるように見えるのは少し気持ち悪い。もう少しスマートに解決したい。

## 方法3｜template parameterにnullptr_tを用いる

c++14から、template parameterに`std::nullptr_t`が使えるようになった[^2]。`std::nullptr_t`は`nullptr`の一値しか取れない型だが、template parameterとして立派に機能する。

[^2]: 参考：<https://cpprefjp.github.io/lang/cpp14/nontype_template_parameters_of_type_nullptr_t.html>

```cpp
template <typename T>
struct Hoge {
  template <std::nullptr_t Dummy = nullptr>
  auto func(void)
  -> std::enable_if_t<std::is_same<T, void>::value && Dummy == nullptr, void> {
    std::cout << "void" << std::endl;
  }

  template <std::nullptr_t Dummy = nullptr>
  auto func(void)
  -> std::enable_if_t<!std::is_same<T, void>::value && Dummy == nullptr, void> {
    std::cout << "not void" << std::endl;
  }
};
```

理屈はbool変数を用いる方法と同様。`std::nullptr_t`は一値しかとらないとはいえ、`std::is_same<T, void>::value && Dummy == nullptr`は`Dummy`の値が決まるまで分からないので、SFINAEにより実体化抑制に使える。

`std::nullptr_t`を用いることでtemplate parameterの自由度を下げることができ、利用者に余計な心配をさせなくて済む。
