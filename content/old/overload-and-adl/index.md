---
author: komori-n
draft: true
categories:
  - プログラミング
date: "2020-12-26T17:04:16+09:00"
guid: https://komorinfo.com/blog/?p=697
id: 697
image: https://komorinfo.com/wp-content/uploads/2020/09/cpp.png
og_img:
  - https://komorinfo.com/wp-content/uploads/2020/09/cpp.png
permalink: /overload-and-adl/
tags:
  - C/C++
title: 演算子オーバーロードとADLとtemplate関数の名前解決
url: overload-and-adl/
---

ADLが絡むと想定とは違う関数が呼ばれることがあるよというお話。これを読めば、演算子オーバーロードを型定義と同じ名前空間に置くべき理由が理解できるようになる。

## 問題

いきなりだが脳内コンパイラチェックである。

次のような `operator<<`がオーバーロードされたプログラムを考える。

```
#include <iostream>

namespace ns {
  // forward declaration
  struct A;
}

ns::A& operator<<(ns::A& a, const char*) {
  std::cout << "::operator<<(A&,const char*)" << std::endl;
  return a;
}

namespace ns {
  struct A {
    A& operator<<(bool) {
      std::cout << "ns::A::operator<<(bool)" << std::endl;
      return *this;
    }
  };

  template <typename T>
  A& operator<<(A&& a, T&& t) {
    std::cout << "ns::operator<<(A&&,T&&)" << std::endl;
    return a << std::forward<T>(t);
  }

  A& operator<<(A& a, const void*) {
    std::cout << "ns::operator<<(A&,const void*)" << std::endl;
    return a;
  }
}


int main(int argc, char* argv[]) {
  ns::A() << "Hoge" << 264 << "Fuga";

  return 0;
}
```

構造体 `ns::A`に対し、`operator<<`が4種類オーバーロードされている。

- `::ns::operator<<(A&, const char*)`
- `ns::A::operator<<(bool)`
- `template <typename T> ns::operator<<(A&&, T&&)`
- `ns::operator<<(A&, const void*)`

この時、上記のプログラムはc++14環境でコンパイルできるだろうか。コンパイルできる場合、実行結果はどのようになるだろうか<span class="easy-footnote-margin-adjust" id="easy-footnote-1-697"></span><span class="easy-footnote">[<sup>1</sup>](https://komorinfo.com/blog/overload-and-adl/#easy-footnote-bottom-1-697 "僕の脳内コンパイラは1個目のoperatorが正しく解決できなかった")</span>。

## 問題の解答

上記のプログラムのコンパイル可能で、実行結果は以下のようになる。

```
$ ./a.out
ns::operator<<(A&&,T&&)
ns::operator<<(A&,const void*)
ns::A::operator<<(bool)
::operator<<(A&,const char*)
```

1つ目のoperatorでは`operator<<(A&&, T&&)`と`operator<<(A&,const void*)`が呼び出されるのに対し、3つ目のoperatorでは`operator<<(A&,const char*)`が呼び出されているのが直感に反する。この挙動を理解するためには、オーバーロードされた関数の名前解決方法をちゃんと理解する必要がある。

## ADL

[ADL（実引数依存の名前探索）](https://en.cppreference.com/w/cpp/language/adl)とは、特定の状況下では名前空間を省略して関数を呼び出せる機能のことである。例えば、以下のプログラムを考える。

```
#include <iostream>

namespace ns {
  struct X {};
  void func(X x) {}
}

int main(void) {
  // 引数がnamespace nsなので、ns::funcが呼び出し候補に追加される
  func(ns::X());

  return 0;
}
```

このプログラムは問題なくコンパイルできる。ADLとは、簡単に言うと引数の型が含まれる名前空間の関数も呼び出し候補に加えてくれる機能である。`func(ns::X())`と書くと、引数の型が名前空間`ns`に入っているので、`ns::func`も呼び出し候補に自動的に加わる。

普段、`std::cout << "Hello World"`を`using std::operator<<`することなく使用可能なのもADLのおかげである。

## Two-phase name lookup

[Two-phase name lookup](https://en.cppreference.com/w/cpp/language/two-phase_lookup)とは、template関数内の名前解決の方法のことである。template関数の名前解決は、templateに依存する部分／しない部分の2段階に分けて行われる。

例えば、以下のプログラムを考える。

```
void g(int) {}

template <typename T>
void func(T& t) {
    g(1);
    g(t);
}

struct X{};
void g(X) {}

int main(void) {
    func(X());

    return 0;
}
```

上記のプログラムの`g(1)`はtemplate parameterに依存しない部分なので、実体化より前に名前解決が行われる。もし上記のプログラムで`g(int)`の宣言が`func()`より後方にあった場合、コンパイルエラーとなる。

一方、`g(t)`はtemplate parameterに依存するので、名前解決は関数の実体化まで先送りされる。template parameterの`T=X`は基本型ではないので、`g(t)`の名前解決にはADLが使用される<span class="easy-footnote-margin-adjust" id="easy-footnote-2-697"></span><span class="easy-footnote">[<sup>2</sup>](https://komorinfo.com/blog/overload-and-adl/#easy-footnote-bottom-2-697 "<code>T</code>が基本型の場合はADLは使用されず普通の名前探索になる。詳しくは<a rel="noreferrer noopener" href="https://en.cppreference.com/w/cpp/language/dependent_name" target="_blank">https://en.cppreference.com/w/cpp/language/dependent_name</a>のbinding rulesを参照。")</span>。そのため、定義がtemplate関数よりも後方に位置する関数でも、コンパイラは`g(X)`の宣言を見つけて呼び出し候補に加えられる<span class="easy-footnote-margin-adjust" id="easy-footnote-3-697"></span><span class="easy-footnote">[<sup>3</sup>](https://komorinfo.com/blog/overload-and-adl/#easy-footnote-bottom-3-697 "引数の型が基本型ではない場合、associated namespace/class以外は探索を行わないので注意が必要である。詳しくは<a rel="noreferrer noopener" href="https://stackoverflow.com/questions/27178483/lookup-of-dependent-names-in-c-template-instantiation" target="_blank">https://stackoverflow.com/questions/27178483/lookup-of-dependent-names-in-c-template-instantiation</a>を参照")</span>。

## 冒頭の問題の解説

上記の概念を踏まえ、冒頭のプログラムの`operator<<`の呼び出し関数選択方法について説明する。

```
// コードの再掲
ns::A() << "Hoge" << 264 << "Fuga";
```

### 1つ目のoperator

`A`は名前空間`ns`に含まれるので、1つ目の`operator<<`の呼び出しはADLによる探索が行われる。呼び出し候補となる`operator<<`の一覧は次の通りである。

- `::ns::operator<<(A&, const char*)`
- `ns::A::operator<<(bool)`
- `ns::operator<<(A&&, const char(&)[5])`（template）
- `ns::operator<<(A&, const void*)`

いま考えている呼び出し`ns::A() << "Hoge"`に一番「近い」のは3番目の関数である<span class="easy-footnote-margin-adjust" id="easy-footnote-4-697"></span><span class="easy-footnote">[<sup>4</sup>](https://komorinfo.com/blog/overload-and-adl/#easy-footnote-bottom-4-697 "関数同士の「近さ」の測り方は<a rel="noreferrer noopener" href="https://en.cppreference.com/w/cpp/language/overload_resolution" target="_blank">https://en.cppreference.com/w/cpp/language/overload_resolution</a>を参照。とても簡単に言うと、引数の型と呼び出し先の型の間の型変換が少ない方の関数が「近い」と判断される。この例の場合、3番目の関数は引数の型変換が必要ないので最も「近い」関数である。")</span>。呼び出されるtemplate関数の定義は以下のようになっている。

```
template <typename T>
A& operator<<(A&& a, T&& t) {
  std::cout << "ns::operator<<(A&&,T&&)" << std::endl;
  return a << std::forward<T>(t);  // ★
}
```

この関数では、`A`をlvalueにしたバージョンのoperator&lt;&lt;を再度呼び出す（★）。`A`は基本型ではないので、この`operator<<`の呼び出し候補はADLにより探索される。そのため、★の呼び出し候補の関数は次の3択になる。

- `ns::A::operator<<(bool)`
- `template <typename T> ns::operator<<(A&&, T&&)`
- `ns::operator<<(A&, const void*)`

一番ふさわしそうな`::operator<<(A&, const char*)`はADLで見つからないため探索候補には含まれない。

上のリストの中で`a << std::forward<const char(&)[5]>(t)`の呼び出しに最もふさわしいのは3番目の関数なのでこの関数が呼ばれる。

以上をまとめると、`ns::A() << "Hoge"`の出力結果は以下のようになる。

```
ns::operator<<(A&&,T&&)
ns::operator<<(A&,const void*)
```

### 2つ目のoperator

1つ目の`operator<<`の戻り値は`A&`なので、2つ目のoperatorの呼び出し候補は以下の4つとなる。

- `::ns::operator<<(A&, const char*)`
- `ns::A::operator<<(bool)`
- `ns::operator<<(A&&, int&&)`（template）
- `ns::operator<<(A&, const void*)`

このうち、1番目、4番目は`int`からポインタへ変換できないので呼び出せない。また、3番目もlvalue referenceからrvalue referenceへの変換ができないので呼び出せない。そのため、2番目の定義が呼ばれる。

```
ns::A::operator<<(bool)
```

### 3つ目のoperator

2つ目の`operator<<`の戻り値は`A&`なので、3つ目のoperatorの呼び出し候補は以下の4つとなる。

- `::ns::operator<<(A&, const char*)`
- `ns::A::operator<<(bool)`
- `ns::operator<<(A&&, const char(&)[5])`（template）
- `ns::operator<<(A&, const void*)`

このうち、3番目は`A`がlvalue referenceであることから呼び出せない。残った3つのうち、文字列`"Fuga"`の型（`const char(&)[5]`）に最も「近い」1番目の定義が呼ばれる。

```
ns::operator<<(A&,const char*)
```

## まとめ

演算子の宣言位置によっては、意図しない定義が選択される例を見てきた。特に、ADLとtemplate関数が絡むと直感を外れることが多くなる。

そのため、operatorを定義する場合は型と同じ名前空間に宣言すべきなのである。
