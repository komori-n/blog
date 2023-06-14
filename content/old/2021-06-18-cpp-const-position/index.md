---
author: komori-n
draft: true
categories:
  - プログラミング
date: "2021-06-18T23:03:15+09:00"
guid: https://komorinfo.com/blog/?p=1153
id: 1153
image: https://komorinfo.com/wp-content/uploads/2020/09/cpp.png
og_img:
  - https://komorinfo.com/wp-content/uploads/2020/09/cpp.png
permalink: /cpp-const-position/
tags:
  - C/C++
title: C/C++でconstの位置に迷うときの考え方
url: cpp-const-position/
---

C/C++で、ポインタや参照が絡んだ時に `const` をどこにつければいいか一瞬迷うことがある。そのため、 `const` の考え方について自分用にメモする。

## constの考え方

覚えておくべきルールは以下の2つだけである。

1. 冒頭の`const`は直後の型名と入れ替えても同じ意味
   - `const int`と`int const`は同じ型
   - `const int*`と`int const*`は同じ型だが`int* const`とは違う型
2. `const`、`volatile`、`*`、`&`、`&&`は直前の型を修飾して別の型にする記号
   - `volatile int* const&` は `(((volatile int)*) const)&` のイメージ。日本語で書き下すなら、（（書き換え不可能な（（volatileなint）を指すポインタ））への参照）となる。

`const`をつける位置に迷ったら、まず1の考え方に従い`<型名> const` の順に入れ替える。通常のコーディングでは`const`を手前に置く方が主流だが、`const`の位置に迷った時は1.のルールで脳内変換した方が考えやすい。

### 例題

例題：`T=const char*` のとき、`const T&` を現す型は何か？

### 解答

それぞれに1.を適用すると以下のようになる。

- `T=const char*` -&gt; `T=char const*`
- `const T&` -&gt; `T const&`

`T=char const*` を `const T&` に代入すれば、求める型は `char const* const&`（`=const char* const&`）だと分かる。「`const`は直前の型を修飾する」という大原則を忘れなければ、`const`を付ける位置に迷うことは少なくなるはずだ<span class="easy-footnote-margin-adjust" id="easy-footnote-1-1153"></span><span class="easy-footnote">[<sup>1</sup>](https://komorinfo.com/blog/cpp-const-position/#easy-footnote-bottom-1-1153 "この例題で15分溶かした自称C++プログラマーがいるらしい")</span>。

## constexprの考え方

さて、`const`の考え方は上に述べた通りだが、`constexpr`はルールが異なるので注意が必要である。`constexpr`は、宣言する変数がROM化可能（コンパイル時に計算可能）であることを修飾するキーワードである。すなわち、**`constexpr`は型ではなく変数にかかるイメージ**である。

例えば、`const char* x` は「`const char`を指すポインタ変数 `x`」を表すのに対し、`constexpr char* x`は「`char`を指すポインタ変数`x`はROM化可能」を表す。

コードで差分を示すと以下のようになる。

```
int g = 334;

// OK: グローバル変数 g への書き換え不可能なポインタ
const int* a = &g;
// OK: グローバル変数 g へのポインタ（グローバル変数のアドレスはROM化可能）
constexpr int* b = &g;

int main() {
  const int l = 264;
  // OK: a の書き換えは禁止されていない
  a = &l;
  // NG: b の書き換えは禁止
  // b = &l;

  // NG: a は const int を指すので書き換え不可
  // *a = l;
  // OK: b の中身は書き換え可能
  *b = l;
}
```

とてもややこしいので注意が必要だ<span class="easy-footnote-margin-adjust" id="easy-footnote-2-1153"></span><span class="easy-footnote">[<sup>2</sup>](https://komorinfo.com/blog/cpp-const-position/#easy-footnote-bottom-2-1153 "<code>constexpr</code>でも<code>const</code>の1.のルールは使える。すなわち、<code>constexpr int x</code> は <code>int constexpr x</code> と書くこともできる")</span>。

`constexpr` と `const` の関係については以下の記事も参照。

<figure class="wp-block-embed is-type-wp-embed is-provider-コウモリのちょーおんぱ wp-block-embed-コウモリのちょーおんぱ"><div class="wp-block-embed__wrapper">> [constexpr宣言された変数は暗黙的にconstになる](https://komorinfo.com/blog/constexpr-variable-is-const/)

<iframe class="wp-embedded-content" data-secret="K7zfNflHTj" frameborder="0" height="282" marginheight="0" marginwidth="0" sandbox="allow-scripts" scrolling="no" security="restricted" src="https://komorinfo.com/blog/constexpr-variable-is-const/embed/#?secret=K7zfNflHTj" style="position: absolute; clip: rect(1px, 1px, 1px, 1px);" title="“constexpr宣言された変数は暗黙的にconstになる” — コウモリのちょーおんぱ" width="500"></iframe></div></figure>
