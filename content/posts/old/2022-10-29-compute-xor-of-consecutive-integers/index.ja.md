---
author: komori-n
draft: true
categories:
  - 数学
date: "2022-10-29T21:01:00+09:00"
tags:
  - アルゴリズム
title: 連続整数列の排他的論理和（xor）
relpermalink: blog/compute-xor-of-consecutive-integers/
url: blog/compute-xor-of-consecutive-integers/
description: 連続する非負整数の排他的論理和（xor）を高速に計算する方法について。
---

{{< katex >}}

連続する非負整数の排他的論理和（xor）を高速に計算する方法について。

次の関数 \\(f: \\mathbb{N}\_0 \\rightarrow \\mathbb{N}\_0 \\) を考える。

\\begin{align}
f(n) = 1 \\oplus 2 \\oplus \\dots \\oplus n
\\end{align}

ただし、 \\(\\oplus\\) はビットごとの排他的論理和（xor）である。素直に計算するなら \\(O(n)\\) の計算量が必要だが、実はこの関数は排他的論理和を一回も取らずに結果を得ることができる。

## 性質

任意の非負整数 \\(m\\) に対し、

\\begin{align}
2m \\oplus (2m+1) = 1.
\\end{align}

---

この性質から、任意の非負整数 \\(m\\) に対し、

\\begin{align}
4m \\oplus (4m+1) \\oplus (4m+2) \\oplus (4m+3) = 0
\\end{align}

が成り立つ。すなわち、\\(f\\) は4要素ごとにゼロになることがわかる。よって、\\(f\\) は、

\\begin{align}
f(n) = \\begin{cases}
n &amp; n \\equiv 0\\ (\\text{mod }4) \\\\
1 &amp; n \\equiv 1\\ (\\text{mod }4) \\\\
n + 1 &amp; n \\equiv 2\\ (\\text{mod }4) \\\\
0 &amp; n \\equiv 3\\ (\\text{mod }4)
\\end{cases}
\\end{align}

と \\(O(1)\\) で計算できる。

これを用いれば、任意の連続自然数の和
\\begin{align}
g(n, m) := n \\oplus (n+1) \\oplus \\dots \\oplus m\\ \\ (0 &lt; n &lt; m)
\\end{align}

は

\\begin{align}
g(n, m) = f(n-1) \\oplus f(m)
\\end{align}

と \\(O(1)\\) と計算できる。
