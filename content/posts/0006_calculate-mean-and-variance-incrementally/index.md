---
author: komori-n
categories:
  - 技術解説
date: 2023-12-13T21:03:35+09:00
tags:
  - 数学
keywords:
  - 丸め誤差
  - 平均
  - 分散
title: 丸め誤差を抑えて平均と分散を計算する
relpermalink: blog/calculate-mean-and-variance-incrementally
url: blog/calculate-mean-and-variance-incrementally
description: 丸め誤差を最小限に抑えながら平均や分散を計算する方法について解説する。
---

{{< katex >}}

丸め誤差を最小限に抑えながら平均や分散を計算する方法について解説する。

## 背景

以下では、標本 $(x_i)_{i=1}^{n}$ の$i=1,2,\dots,m$に対する平均$\mu_m$
および分散$\sigma_m^2$を逐次的（incremental）に求める手法を考える[^1]。
定義より、$\mu_m$の更新式は

\\begin{align}
\mu_m &= \frac{(m - 1)\mu_{m-1} + x_m}{m}
\\end{align}

となる。しかし、このまま計算機上で実装すると、
分子の加算において情報落ち誤差が生じる可能性がある。
特に、$m\gg 1$のとき、分子の第1項は第2項と比べて絶対値が約$m$倍となり、
第2項の加算に大きな誤差が乗るためである。
よって、計算機上で計算する場合は、計算順序を工夫して丸め誤差が混入しづらくする必要がある。

[^1]: 分散ではなく不偏分散を計算したい場合も、本ページと同様の変形を行うことで丸め誤差を減らして計算を行える。

分散$\sigma_m^2$の計算においても同様に、
更新式を工夫しなければ桁落ち誤差が発生しやすいため注意しなければならない。
以下では、丸め誤差が混入しづらい平均および分散の計算式を示し、
実際の計算機上で実装して数値的に優れていることを確かめる。

## 平均

式(1)を少し変形すると、

\\begin{align}
\mu_m &= \mu_{m-1} + \frac{x_m - \mu_{m-1}}{m}
\\end{align}

を得る。式(1)ではなく式(2)を使うことで、丸め誤差を抑えられることが知られている。
直感的には、式(1)の分子では$m\gg 1$のとき情報落ち誤差により加算が停止してしまうのに対し、
式(2)では$\mu_m$の差分を考慮することで情報落ち誤差が結果へ影響しにくくなっている。

## 分散

分散の定義より、

\\begin{align}
m\sigma.m^2 &= \sum_{i=1}^{m} (x_i - \mu_m)^2 \notag \\\\
&= \sum_{i=1}^m x_i^2 - m\mu_m^2 \notag
\\end{align}

が成り立つ。これを利用して式変形を行うと、

\\begin{align}
m\sigma_m^2 - (m-1)\sigma_{m-1}^2
&= x_m^2 - m\mu_{m}^2 + (m-1) \mu_{m-1}^2 \notag \\\\
&= x_m^2 - \mu_m (x_n + (m-1)\mu_{m-1}) + \mu_{m-1} (m\mu_m - x_n) \notag \\\\
&= x_m^2 - (\mu_{m-1} + \mu_m) x_m + \mu_{m-1} \mu_{m} \notag \\\\
&= (x_m - \mu_{m-1}) (x_m - \mu_{m})
\\end{align}

を得る。この式は式(1)の平均値の計算に似ていることに注目すると、
式(1)→式(2)の変形と同様の変形を行うことができ、

\\begin{align}
\sigma_m^2 = \sigma_{m-1}^2 + \frac{
(x_m - \mu_{m-1}) (x_m - \mu_{m}) - \sigma\_{m-1}^2
}{m}
\\end{align}

を得る。この式を用いて$\sigma_m^2$を逐次更新していくことで、
分散の計算を小さな差分計算に落とし込むことができ、
計算中に発生する丸め誤差を抑えることができる。

## 数値実験

数列$(x_i)_{i=1}^{100,000,000}$に対し、通常の方法および上記の方法を用いて平均および分散を計算した。
ここで、

\\begin{align}
x_i = \begin{cases}
1 & \text{if }i\text{ is odd}, \\\\
2 & \text{if }i\text{ is even},
\end{cases}
\\end{align}

である。なお、$(x_i)_{i=1}^{n}$の正確な平均は$1.5$、分散は$0.25$である。

### 平均

まず、次のようなプログラムを用いて平均値を計算した。

```cpp
#include <iostream>

namespace {
constexpr std::size_t kCount = 100'000'000;

float GetX(std::size_t i) {
  return i % 2 == 0 ? 1.0f : 2.0f;
}

float MeanNaive() {
  float sum = 0.0f;
  for (std::size_t i = 0; i < kCount; ++i) {
    const auto x = GetX(i);
    sum += GetX(i);
  }

  return sum / kCount;
}

float MeanIterative() {
  float mean = 0.0f;
  for (std::size_t i = 0; i < kCount; ++i) {
    const auto x = GetX(i);
    mean += (x - mean) / (i + 1);
  }

  return mean;
}
}  // namespace

int main() {
  std::cout << "naive: " << MeanNaive() << std::endl;
  std::cout << "iterative: " << MeanIterative() << std::endl;
}
```

`MeanNaive()`が定義どおり「総和÷要素数」により平均を計算する関数、
`MeanIterative()`が式(2)により逐次的に平均を計算する関数である。
上記のプログラムを実行すると、次の出力が得られた。

```text
naive: 0.335544
iterative: 1.5
```

`MeanNaive()`は丸め誤差の影響により正しい平均値が求められなかったのに対し、
`MeanIterative()`では正しい平均値を計算できた。

### 分散

次に、以下のプログラムにより分散の計算を行った。

```cpp
#include <iostream>

namespace {
constexpr std::size_t kCount = 100'000'000;

float GetX(std::size_t i) {
  return i % 2 == 0 ? 1.0f : 2.0f;
}

float VarianceNaive() {
  float sum = 0.0f;
  for (std::size_t i = 0; i < kCount; ++i) {
    const auto x = GetX(i);
    sum += x;
  }

  float square_sum = 0.0f;
  for (std::size_t i = 0; i < kCount; ++i) {
    const auto x = GetX(i);
    square_sum += (x - sum) * (x - sum);
  }

  return square_sum / kCount;
}

float VarianceIterative() {
  float mean = 0.0f;
  float variance = 0.0f;
  for (std::size_t i = 0; i < kCount; ++i) {
    const auto x = GetX(i);
    const auto new_mean = mean + (x - mean) / (i + 1);
    variance += ((x - mean) * (x - new_mean) - variance) / (i + 1);
    mean = new_mean;
  }

  return variance;
}
}  // namespace

int main() {
  std::cout << "naive: " << VarianceNaive() << std::endl;
  std::cout << "iterative: " << VarianceIterative() << std::endl;
}
```

上記のプログラムを実行すると、次の出力が得られた。

```text
naive: 1.88895e+14
iterative: 0.25
```

`VarianceNaive()`は丸め誤差の影響により正しい分散が求められなかったのに対し、
`VarianceIterative()`では正しい分散を計算できた。
