---
author: komori-n
categories:
  - 技術解説
date: "2022-12-19T19:39:37+09:00"
tags:
  - C言語
  - C++
keywords:
  - ループアンロール
  - マクロ
  - Unroller
  - Pragma
title: C++でループをアンロールする
relpermalink: blog/unroll-cpp-code/
url: blog/unroll-cpp-code/
description: C++で行儀よくループアンロールする方法のまとめ。
---

C++で行儀よくループアンロールする方法のまとめ。

## 概要

C++で重いループを高速化するときに、ループアンローリングしたくなることがしばしばある。ループアンロールによりバイナリサイズは肥大化してしまうが、条件分岐の削減やパイプラインストールの抑制によりそこそこの高速化が期待できる場合が多い。

C++で行儀よくループアンロールする方法は大きく分けて3つある。

- Hand Unrolling: ループの中身を（マクロ関数などを用いて）展開する
- Unroller: メタ関数とラムダ式を用いてコードを展開する
- Pragma: コンパイラに指示してアンロールしてもらう

これらはそれぞれメリット／デメリットがあるため状況に応じて使い分ける必要がある。それぞれ順に説明していく。

## Hand Unrolling

まず思いつくのは、コードクローンの要領でループ内の処理をマクロで連打する方法である。

```cpp
#include <iostream>

// 式 p を 4 回連打するマクロ関数
#KOMORI_UNROLL_4(p) \
  do { \
    p; \
    p; \
    p; \
    p; \
  } while(false)

int main() {
  // `std::cout << "Hello World" << std::endl;` を 4 回実行してほしい
  KOMORI_UNROLL_4(std::cout << "Hello World" << std::endl);

  // 出力：
  // Hello World
  // Hello World
  // Hello World
  // Hello World
}
```

上のコード例において、マクロ関数 `KOMORI_UNROLL_4(p)` は式 `p` を 4 回唱えるだけの単純なマクロである。このマクロ関数を用いれば簡単にループアンロールを実現できる。

また、少し工夫をすることで、（だいたい）任意の回数のアンロールを実現することもできる[^1]。

[^1]: 多重ループをアンロールしたい場合は [Boost.Preprocessor](https://www.boost.org/doc/libs/1_80_0/libs/preprocessor/doc/index.html) を使用すればよい。なお、Boost.Preprocessorの実装詳細は [BOOST_PP_REPEATの仕組み](https://zenn.dev/hikarin/articles/5329647ec2a542653f68) が詳しい。

```cpp
#include <iostream>

// `expr` を `num` 回分アンロールする
#define KOMORI_UNROLL(num, expr) \
  do { \
    KOMORI_CAT(KOMORI_REPEAT_IMPL_, num)(expr;) \
  } while(false)

#define KOMORI_CAT(A, B) KOMORI_CAT_IMPL(A, B)
#define KOMORI_CAT_IMPL(A, B) A##B

#define KOMORI_REPEAT_IMPL_1(expr) expr
#define KOMORI_REPEAT_IMPL_2(expr) KOMORI_REPEAT_IMPL_1(expr) expr
#define KOMORI_REPEAT_IMPL_3(expr) KOMORI_REPEAT_IMPL_2(expr) expr
#define KOMORI_REPEAT_IMPL_4(expr) KOMORI_REPEAT_IMPL_3(expr) expr
#define KOMORI_REPEAT_IMPL_5(expr) KOMORI_REPEAT_IMPL_4(expr) expr
#define KOMORI_REPEAT_IMPL_6(expr) KOMORI_REPEAT_IMPL_5(expr) expr
#define KOMORI_REPEAT_IMPL_7(expr) KOMORI_REPEAT_IMPL_6(expr) expr
#define KOMORI_REPEAT_IMPL_8(expr) KOMORI_REPEAT_IMPL_7(expr) expr
// ...（好きな数定義する）

int main() {
  // `std::cout << "Hello World" << std::endl;` を 4 回実行してほしい
  KOMORI_UNROLL(4, std::cout << "Hello World" << std::endl);

  // 出力：
  // Hello World
  // Hello World
  // Hello World
  // Hello World
}
```

コードクローンによりアンロールするデメリットは、コードの可読性や保守性が下がることである。アンロール対象のコードをマクロ関数に渡す必要があるので、どうしても元のコードより読みづらくなってしまう。

また、マクロ関数はプリプロセス時に展開される必要があるため、constexpr定数のようなコンパイル時定数が使えない。つまり、ループ回数は直接数値リテラルを書くかマクロ定数にするしかない。

一方で、コードクローンによるアンロールを行うメリットは、分かりやすくアンロールされることである。やりたい処理をコピペにより連打している状態なので、疑いなく確実にアンロールできる。そのため、可読性や保守性をすべて犠牲にしてどうしても高速化したい場合に適している方法である。

## Unroller (template class)

2つめの方法は Unroller とよばれるイディオムを使用する方法である。Unroller は N 回与えられた関数を唱えるメタ関数で、テンプレートの例としてしばしば紹介される。実装方法はいくつか考えられるが、c++17 では constexpr if 文を用いて簡単に実装できる。

```cpp
template <std::size_t N>
struct Unroller {
  template <typename T>
  static void Execute(T&& t) {
    if constexpr (N > 0) {
      Unroller<N-1>::Execute(t);
      t(N);
    }
  }
};

int main() {
  // `std::cout << "Hello World" << std::endl;` を 4 回実行してほしい
  Unroller<4>::Execute([](std::size_t i) {
    std::cout << "Hello World" << std::endl;
  });

  // 出力：
  // Hello World
  // Hello World
  // Hello World
  // Hello World
}
```

コンパイル時に `Unroller<N>` -&gt; `Unroller<N-1>` -&gt; … -&gt; `Unroller<0>` と展開されて、それぞれのメタ関数で関数コールが行われる。構造体の展開はコンパイル時に行われるので、ほぼ間違いなくアンロールさせることができる。

ただし、`Unroller` を使う上で注意しなければならないのが、early returnができない点である。Unrollerは実行したい内容をLambda式で包む必要があるので、ループの途中で抜け出すことが難しい。そのため、ループの中断条件がある場合はUnrollerを使うことはできない。

## Pragma unroll

3つめの方法はコンパイラにすべて任せる方法である。

最近のコンパイラは、プログラムの高速化のために自動でループのアンロールを行うことがある。また、コード中の Pragma ディレクティブ（`#pragma`）や Pragma 演算子（`_Pragma()`）を通じてアンロールの指示を与えられるコンパイラも多い[^2]。例えば、GCCでは `#pragma GCC unroll n` （`Pragma("GCC unroll n")`）、clangでは `#pragma unroll n` （`Pragma("unroll n")`）によりアンロールの指示を与えられる。

[^2]: [Pragma演算子](https://cpprefjp.github.io/lang/cpp11/pragma_operator.html)はC++11で追加された記法で、従来の Pragma ディレクティブで難しかったプリプロセッサ処理が可能になっている。

```cpp
int main() {
  // `std::cout << "Hello World" << std::endl;` を 4 回実行してほしい
#pragma unroll 4
  for (std::size_t i = 0; i < 4; ++i) {
    std::cout << "Hello World" << std::endl;
  }

  // 出力：
  // Hello World
  // Hello World
  // Hello World
  // Hello World
}
```

コンパイラにアンロールを任せることによって、コードをきれいに保つことができる。マクロやテンプレートのような回りくどいコードを書く必要がなく、可読性を保ったままアンロールを行うことができる。

ただし、コンパイラによるアンロールはコンパイラに依存している部分が大きい。コンパイラによって Pragma の中身を変える必要があるし、アンロールに対応していないコンパイラも存在する。また、ループ内容が複雑な場合、アンロール指示を与えても無視されてしまうこともある。そのため、必ずコンパイル結果を逆アセンブルして意図通り展開されているか確認する必要がある。

## まとめ

| 手法           | メリット                       | デメリット                                                                              |
| -------------- | ------------------------------ | --------------------------------------------------------------------------------------- |
| Hand Unrolling | 確実にアンロールされる         | 可読性・保守性が低い ループ回数をマクロ定数にする必要がある （constexpr定数が使えない） |
| Unroller       | （ほぼ）確実にアンロールされる | early returnできない                                                                    |
| Pragma         | コードがきれいに保てる         | 挙動がコンパイラに依存する しばしばアンロールされないことがある                         |

このページではC++で行儀よくループをアンロールする方法について3つ紹介した。それぞれにメリットとデメリットがあるため、一概のどの方法が良いとは言えない。そのため、可読性と効率性のバランスやプロジェクトの状況を踏まえて最適な方法を選ぶ必要がある。
