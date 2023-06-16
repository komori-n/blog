---
author: komori-n
draft: true
categories:
  - Math
date: "2022-10-29T21:02:00+09:00"
guid: https://komorinfo.com/blog/?p=1843
id: 1843
permalink: /en/compute-xor-of-consecutive-integers-en/
tags:
  - Algorithm
title: Compute Exclusive OR(xor) of Consecutive Integers
url: compute-xor-of-consecutive-integers-en/
---

This page shows how to calculate xor of nonnegative consecutive integers in constant time.

Consider the following function \\(f:\\mathbb{N}\_{0}\\rightarrow\\mathbb{N}\_{0}\\):

\\begin{align}
f(n) = 1 \\oplus 2 \\oplus \\dots \\oplus n
\\end{align}

where \\(\\oplus\\) is bitwise exclusive OR(xor) operator. One can compute the result of the function without applying xor \\(n – 1\\) times.

<div class="wp-block-vk-blocks-border-box vk_borderBox vk_borderBox-background-transparent is-style-vk_borderBox-style-solid-kado-tit-tab"><div class="vk_borderBox_title_container">#### Theorem

</div><div class="vk_borderBox_body">\\begin{align}
2m \\oplus (2m + 1) = 1 \\ \\ \\forall m \\in \\mathbb{N}\_{0}
\\end{align}

</div></div>By this fact,

\\begin{align}
4m \\oplus (4m+1) \\oplus (4m+2) \\oplus (4m+3) = 0
\\end{align}

follows for all \\(m \\in \\mathbb{N}\_{0}\\). In other words, \\(f\\) is equal to \\(0\\) for every 4 elements. Thus, one can calculate \\(f\\) in \\(O(1)\\) by

\\begin{align}
f(n) = \\begin{cases}
n, &amp; n \\equiv 0 \\pmod 4 \\\\
1, &amp; n \\equiv 1 \\pmod 4 \\\\
n + 1, &amp; n \\equiv 2 \\pmod 4 \\\\
0\. &amp; n \\equiv 3 \\pmod 4
\\end{cases}
\\end{align}

In addition, xor of the consecutive integers

\\begin{align}
g(n, m) := n \\oplus (n+1) \\oplus \\dots \\oplus m\\ \\ (0 &lt; n &lt; m)
\\end{align}

can be calculated in \\(O(1)\\) by

\\begin{align}
g(n, m) = f(n-1) \\oplus f(m).
\\end{align}
