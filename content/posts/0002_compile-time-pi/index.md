---
author: komori-n
draft: true
categories:
  - 技術解説
date: 2023-06-23T22:12:15+09:00
tags:
  - C++
keywords:
title: コンパイル時に円周率を100万桁計算する
relpermalink: blog/compile-time-pi
url: blog/compile-time-pi
description: TBD
---

{{< katex >}}

{{< github repo="komori-n/compile-time-pi" >}}

コンパイル時にCPUを酷使して円周率を計算する話。

## はじめに

C++20では、コンパイル時計算の制限がいくつか緩和された。例えば、
[constexpr関数内でのtry-catchブロック](https://cpprefjp.github.io/lang/cpp20/try-catch_blocks_in_constexpr_functions.html)
や
[可変サイズをもつコンテナの`constexpr`化](https://cpprefjp.github.io/lang/cpp20/more_constexpr_containers.html)
などが挙げられる。この緩和により、実用上ほとんどすべての計算をコンパイル時に実行可能になった。

本ページでは、このC++20 constexprを悪用して、コンパイル時に円周率100万桁計算する方法について概説する。

コンパイル時に円周率計算するためには、高速な乗算が可能な任意精度演算ライブラリが必要になる。
通常の円周率の計算では、[GNU Multi-Precision Library(GMP)](https://gmplib.org)
のような任意精度演算ライブラリを使用することで、円周率100万桁を1秒以内に求めることができる。
しかし、GMPを始めとした任意精度演算ライブラリは基本的にconstexpr計算に対応していない[^0]。
そのため、constexpr計算に対応した任意精度演算ライブラリを自作した。

[^0]:
    なぜ既存のライブラリがconstexpr計算に対応していないかというと、
    コンパイル時間がかかりすぎて実用性に乏しいからであると思われる

## 円周率の計算方式

コンピュータで円周率の計算を行う場合、Chudnovsky の公式[^1]

\\begin{align}
\\frac{1}{\\pi} = 12\\sum\_{n=0}^{\\infty} \\frac{(-1)^n (6n)! (A+Bn)}{(n!)^3 (3n)! C^{3n+3/2}}
\\end{align}

がよく用いられる。ただし、

\\begin{align}
A=13591409,\\quad B=545140134,\\quad C=640320
\\end{align}

である。Chudnovsky の公式は極めて収束が早く、実際に \\(n=0\\) で計算を打ち切っても、\\(3.141592653589734\\dots\\) と小数点以下13桁の精度がある。

[^1]: D. V. Chudnovsky and G. V. Chudnovsky, Approximations and complex multiplication according to Ramanujan, in Ramanujan Revisited, Academic Press Inc., Boston, (1988), p. 375-396 &amp; p. 468-472.

この式をそのまま計算すると、除算や平方根の演算が多くあるため、計算に時間がかかる。
しかし、F. Bellard氏の論文[^2]のような工夫をすることで、結果を高速に求められる。

[^2]: [Computation of 2700 billion decimal digits of Pi using a Desktop Computer](https://bellard.org/pi/pi2700e9/pipcrecord.pdf)

以下では、F. Bellard氏の論文のAlgorithm 1に沿って円周率の計算を行う。
このアルゴリズムの中身は[^2]に詳しく記載されているのでここでは深くは触れない。

このアルゴリズムでは、次のような任意精度演算を行う必要がある。

1. 乗算
2. 除算と平方根
3. 16進数→10進数変換

次節では、それぞれの演算に対するアルゴリズムについて簡潔に述べる。

## 多倍長整数演算

### 乗算

多倍長整数の乗算を愚直に実装すると、\\(O(n^2)\\)の計算量が必要になる。
この計算量を減らす方法として、Karatsuba法とFFT/NTTを用いる方法が知られている。

#### Karatsuba法

Karatsuba法では、整数\\(X:=x_1 B + x_2, Y:=y_1 B + y_2\\)（\\(0\\leq x_2, y_2 &lt; B, B=16^{\\ m}\\)）に対し

\\begin{align}
X Y &amp;= x_1 y_1 B^2 + \\left(x_1 y_2 + x_2 y_1\\right) B + x_2 y_2\\\\
&amp;= x_1 y_1 B^2 + \\left((x_1 + x_2)(y_1 + y_2) – x_1 y_1 – x_2 y_2\\right) B + x_2 y_2
\\end{align}

が成り立つことに注目する。また、\\(B\\)倍は乗算ではなくビットシフトで計算できることに注意する。
変形前（1行目）では4回の乗算が必要になるが、変形後の式（2行目）では、\\(x_1 y_1, x_2 y_2\\)
の計算結果を再利用することで乗算回数を3回に減らすことができる。同様の手法を分解後の乗算にも再帰的に適用することで、
全体の計算量を\\(O(n^{\\log_2 3})\\) に落とすことができる。

#### FFT/NTT

FFTを用いることで、任意精度整数の乗算を高速に行うことができる。

多倍長整数\\(X, Y\\)が
\\begin{align}
X &= \\sum*{i=0}^{N - 1} x*{i} B^{i}, \\\\
Y &= \\sum*{i=0}^{N - 1} y*{i} B^{i},
\\end{align}
のように小さな整数の列 \\((x\_{i})\_{i=0}^{N-1}, (y\_{i})\_{i=0}^{N-1}\\)
の表されるとする。ただし、\\(x*{i}, y*{i} \in \\{0, 1, \\dots, B - 1\\}\\)である。

この2つの整数列に対し、畳み込み演算
\\begin{align}
\\mathrm{IDFT}\[\\mathrm{DFT}\[(x_i)\] \\otimes \\mathrm{DFT}\[(y_i)\]\]
\\end{align}
を考える。ここで、\\(\\mathrm{DFT}\[\bullet\]\\) は離散フーリエ変換、
\\(\\mathrm{IDFT}\[\bullet\]\\) は逆離散フーリエ変換を表し、\\(\\otimes\\) は数列の項ごとに積を取る演算を表す。
この演算結果の第 \\(i\\) 項は、
\\begin{align}
z\_{i}
:=
\\sum\_{j=0}^{N - 1} x\_{j} y\_{i - j}
\\end{align}
となる。ただし、\\(x*{i} = 0, y*{i} = 0 \quad \(i \notin \\{0, 1, \dots, N - 1\\}\)\\) とする。
こうして得られた \\((z\_{i})\_{i=0}^{2N-1}\\) を \\(X\\) や \\(Y\\) と同様に多倍長整数とみなすと、
\\begin{align}
Z = \\sum\_{i=0}^{2N - 1} \\left(\\sum\_{j=0}^{N - 1} x\_{j} y\_{i - j} \\right)B^{i}
\\end{align}
となる。つまり、\\(Z\\) は \\(X \times Y\\) の計算結果になっている[^carry]。
畳み込み演算で現れるフーリエ変換、逆フーリエ変換はいずれも高速フーリエ変換（FFT）が適用でき、
高速に計算できる。

[^carry]:
    厳密なことを言うと、\\(z*{i} \geq B\\) となってしまう可能性があるが、
    下の桁から順に繰り上がり処理を行うことで、\\(0 \leq z*{i} < B (i = 0, 1, \dots, 2N - 1)\\) とできる。

{{< alert >}}
SSAの説明

- <https://円周率.jp/method/fft/>
- <https://tonjanee.home.xs4all.nl/SSAdescription.pdf>
  {{< /alert >}}

#### Karatsuba法とSSAの比較

後述する改造コンパイラを用いてKaratsuba法とSSA（[#コンパイル方法](#コンパイル方法)）

{{< alert >}}
数値実験をして結果を貼る
{{< /alert >}}

### 除算と平方根

多倍長整数の除算および平方根の計算には、いずれもNewton-Raphson法を用いる[^3]。

[^3]: 参考：[円周率.jp - Newton 法](https://xn--w6q13e505b.jp/method/newton.html)

整数の除算 \\(X / Y\\) を計算する場合、Newton-Raphson法を用いて \\(Y\\) の逆数 \\(Y^{-1}\\) を求め、
それを \\(X\\) に乗じるという手順を踏む。整数 \\(Y\\) の逆数（の近似値）は、
\\(1/Y\\) を根に持つ関数 \\(f(x) := 1/x – Y\\) に対しNewton-Raphson法を適用することで求められる。
\\(f\\) に対するNewton-Raphson法の反復式は

\\begin{align}
x\_{n+1} = x_n (2 – Y x_n)
\\end{align}

となる。この反復式を用いると、列 \\(\\{x_n\\}\\) は \\(1/Y\\) へ2次収束する。
このように、Newton-Raphson法を用いることで効率的に \\(Y\\) の逆数を求めることができる。

平方根についても逆数と同様に、Newton-Raphson法で求める。
ただし、\\(h(x) := x^2 – Y\\) のような関数を用いて平方根を求めようとすると、反復式の計算に除算が必要になってしまう。
そのため、\\(1/\\sqrt{Y}\\)を根に持つ関数 \\(g(x) := 1/x^2 – Y\\) に対しNewton-Raphson法を適用する。
\\(g\\) に対するNewton-Raphson法の反復式は

\\begin{align}
x\_{n+1} = \\frac{1}{2} x\_{n} (3 – Y x\_{n}^2)
\\end{align}

となる。このようにして得られた \\(1/\\sqrt{Y}\\) （の近似値）に対し、
\\(Y \\times (1 / \\sqrt{Y})\\) を計算することで \\(\\sqrt{Y}\\) を求めることができる。

### 16進数→10進数変換

円周率の計算を行う場合、大部分の計算は16進数で行われるが、最終的には10進数として出力する必要がある。
16進数で表された多倍長浮動小数を10進数への変換にも少し工夫が要る[^4]。

[^4]: 参考：[円周率.jp - 基底変換](https://xn--w6q13e505b.jp/method/base.html)

まず、0以上1未満の16進数で表された小数\\(x\\)を\\(n\\)桁の10進数の小数へ変換する方法を考える。
分割統治法を用いて、前半 \\(n/2\\) 桁と後半 \\(n/2\\) 桁に分けて考える。前半の \\(n/2\\) 桁は、
元の問題の半分のサイズの問題へ帰着させることができる。一方、後半の \\(n/2\\) 桁は、
\\(10^{n/2}\\) を乗じて \\(x \\times 10^{n/2}\\) とし、
この数の小数部分を \\(n/2\\) 桁の10進数へ変換する問題と言い換える事ができるので、
やはり半分のサイズの問題へ帰着できる。

{{< alert >}}
気の利いた図
{{< /alert >}}

このアルゴリズムを利用すれば整数を10進数へ変換することができる。16進数で表された整数を10進数表現に変換する場合、
元の整数を \\(10^{n}\\) で割ることで0以上1未満の小数になるため、上の問題に帰着させることができる。

## コンパイル方法

さて、コンパイル時に円周率のような大規模な計算を行う場合、コンパイラを改造する必要がある。
なぜなら、多くのコンパイラはconstexpr演算回数に制限を設けており、
円周率100万計算はその制限を優に上回ってしまうためである。

```text
// clang++のエラー例
src/komori/main.cpp:109:18: error: constexpr variable 'ans' must be initialized by a constant expression
  constexpr auto ans = GetPiString<100000>();
                 ^     ~~~~~~~~~~~~~~~~~~~~
/opt/homebrew/opt/llvm/bin/../include/c++/v1/__iterator/reverse_iterator.h:242:5: note: constexpr evaluation hit maximum step limit; possible infinite loop?
    return __x.base() != __y.base();
```

コンパイラは
[Clangでコンパイル時に評価されるコード量を増やす – Qiita](https://qiita.com/ushitora_anqou/items/6322c6839f39f6b03a4e)
を参考に改造を行った。

{{< alert >}}
patchを貼る
{{< /alert >}}

## 数値結果

作成した円周率計算プログラムに対し、コンパイル時計算と実行時計算でコンパイル時間の比較を行った。
加えて、参考としてGMPライブラリを用いた実行時計算の計算時間の計測も行った[^6]。
なお、（財布の都合上）計測回数は1回だけなので、計測結果はあくまで参考程度として受け取っていただきたい。

[^6]: [GMP Pi computation](https://gmplib.org/pi-with-gmp)

計算にはAWS EC2 r7g.2xlarge（Ubuntu 22.04）を用いた。
constexpr計算はコンパイル時間、実行時計算とGMPライブラリを用いた計算では実行時間をtimeコマンドを用いてそれぞれ計測した。
コンパイラはclang++（commit：200cc952a28a73687ba24d5334415df6332f2d5b）で、
前節で説明したconstexpr演算回数の制限を外すパッチを当てたものを使用した。

以下に計測結果を示す。

|      桁数 | constexpr計算 | 実行時計算 |    GMP |
| --------: | ------------: | ---------: | -----: |
|       100 |        1.475s |     0.002s | 0.002s |
|     1,000 |        4.075s |     0.002s | 0.002s |
|    10,000 |      157.750s |     0.018s | 0.003s |
|   100,000 |   12,787.984s |     1.049s | 0.032s |
| 1,000,000 |           TBD |    51.824s | 0.520s |

{{< chart >}}
type: 'line',
data: {
labels: [100, 1000, 10000, 100000, 1000000],
datasets: [{
label: "constexpr計算",
data: [
{x: 100, y: 1.475}, {x: 1000, y: 4.075}, {x: 10000, y: 157.750}, {x: 100000, y: 12787.984}
]
}, {
label: "実行時計算",
data: [
{x: 100, y: 0.002}, {x: 1000, y: 0.002}, {x: 10000, y: 0.018}, {x: 100000, y: 1.049}, {x: 1000000, y: 51.824}
]
}, {
label: "GMP",
data: [
{x: 100, y: 0.002}, {x: 1000, y: 0.002}, {x: 10000, y: 0.003}, {x: 100000, y: 0.32}, {x: 1000000, y: 0.520}
]
}],
},
options: {
scales: {
x: {
display: true,
type: 'logarithmic',
title: {
display: true,
text: "計算桁数",
}
},
y: {
display: true,
type: 'logarithmic',
title: {
display: true,
text: "計算時間[s]",
}
}
}
}
{{< /chart >}}

{{< alert >}}
結果の考察をなにか書く
{{< /alert >}}

{{< comment >}}
コンパイル時計算は、同じコードの実行時計算と比較して約4000★倍の時間がかかった。これは、実行時計算は `-O3` で最適化がきいているのに対し、コンパイル時計算ではほぼ最適化なしで計算が行われるためであると考えられる。また、GMPのリファレンスコードと比べると、コンパイル時計算は約100★万倍遅いという結果になった。

このように、コンパイル時計算では実行時と比較して多大な計算コストが必要になる。C++20で様々な制限が緩和されてほとんどあらゆることがコンパイル時に計算できるようになったが、円周率の計算のような大規模計算はコンパイル時ではなく実行時に行うべきだということがよく分かった。
{{< /comment >}}

## まとめ

本ページではC++20のコンパイル時計算を駆使してコンパイル時に円周率を10万桁求めた。
計算機科学の分野では古くから研究されている分野だが、想像よりも実装が複雑で、
コンパイル時の計算時間がかかることが実感できた。
