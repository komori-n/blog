---
author: komori-n
categories:
  - 技術解説
date: 2024-03-16T10:54:00+09:00
tags:
  - C++
keywords:
  - STL
  - operator[]
  - at
  - アセンブリ
  - 比較
title: STLコンテナの`opeator[]()`と`at()`のアセンブリ出力比較
relpermalink: blog/operator-vs-at
url: blog/operator-vs-at
description: 本記事では、C++ STL コンテナの`operator[]()`と`at()`を比較し、アセンブリ出力を眺めることで`at()`を使用するコストを理解する。
---

本記事では、C++ STL コンテナの`operator[]()`と`at()`を比較し、
アセンブリ出力を眺めることで`at()`を使用するコストを理解する。

## 背景

本記事では、STL コンテナの`operator[]()`と`at()`のパフォーマンスの比較を行う。
アセンブリ出力を見て、`at()`を用いる drawback を正確に理解することが目的である。

なお、本記事では STL コンテナのアクセス効率のみを比較する。
最近のコンパイラはとても賢いので、実際に使われ方に応じてより全く異なるコンパイル結果になる可能性がある。
そのため、本記事の内容はあくまで一事例として捉えてほしい。

本記事では、以下の STL コンテナに対して比較を行う[^array]。

- `std::vector`
- `std::deque`
- `std::array`

[^array]: `std::array`は厳密には container ではない

### インターフェースの比較

`operator[]()`と`at()`はいずれも、STL シーケンシャルコンテナの`i`番目の要素を取ってくるメンバ関数である。
この 2 つの関数の違いは、`opeator[]()`は`i`がコンテナの範囲内かチェックしないのに対し、
`at()`はチェックすることである。前者で`i`の範囲外アクセスをした場合の挙動は未規定だが、
後者は`std::out_of_range`例外を送出すると規定されている。

`at()`は範囲内チェックをしなければならないため、`operator[]()`よりも少し遅いことが知られている。
本記事では、この速度差を定量的に体感することが目標である。

## アセンブリ出力の比較

以下の条件でアセンブリ出力の比較を行った。

- x86-64
  - コンパイラ： clang-17.0.1
  - オプション： `-Ofast`
- armv8
  - コンパイラ： clang-17.0.1
  - オプション： `-Ofast`

以下のコードに対し、コンパイルを行った。

```cpp
#include <vector>

int OperatorAccess(const std::vector<int>& vec, std::size_t i) {
    return vec[i];
}

int AtAccess(const std::vector<int>& vec, std::size_t i) {
    return vec.at(i);
}
```

### x86-64

x86-64 環境では、アセンブリ出力は以下のようになった。

```asm
OperatorAccess(std::vector<int, std::allocator<int> > const&, unsigned long): # @OperatorAccess(std::vector<int, std::allocator<int> > const&, unsigned long)
        mov     rax, qword ptr [rdi]
        mov     eax, dword ptr [rax + 4*rsi]
        ret

AtAccess(std::vector<int, std::allocator<int>> const&, unsigned long):        # @AtAccess(std::vector<int, std::allocator<int>> const&, unsigned long)
        mov     rax, qword ptr [rdi]
        mov     rdx, qword ptr [rdi + 8]
        sub     rdx, rax
        sar     rdx, 2
        cmp     rdx, rsi
        jbe     .LBB1_2
        mov     eax, dword ptr [rax + 4*rsi]
        ret
.LBB1_2:
        push    rax
        lea     rdi, [rip + .L.str]
        xor     eax, eax
        call    std::__throw_out_of_range_fmt(char const*, ...)@PLT
.L.str:
        .asciz  "vector::_M_range_check: __n (which is %zu) >= this->size() (which is %zu)"
```

<https://godbolt.org/z/rcdT5reKb>

`opeator[]()`の命令数が 2 であるのに対し、`at()`の（`i`が範囲内の場合の）命令数は 7 だった。
つまり、`i`が範囲内かどうかチェックするために 5 命令が追加された。

### armv8

```asm
OperatorAccess(std::vector<int, std::allocator<int>> const&, unsigned long): // @OperatorAccess(std::vector<int, std::allocator<int>> const&, unsigned long)
        ldr     x8, [x0]
        ldr     w0, [x8, x1, lsl #2]
        ret

AtAccess(std::vector<int, std::allocator<int>> const&, unsigned long):        // @AtAccess(std::vector<int, std::allocator<int>> const&, unsigned long)
        ldp     x8, x9, [x0]
        sub     x9, x9, x8
        asr     x2, x9, #2
        cmp     x2, x1
        b.ls    .LBB1_2
        ldr     w0, [x8, x1, lsl #2]
        ret
.LBB1_2:
        stp     x29, x30, [sp, #-16]!           // 16-byte Folded Spill
        mov     x29, sp
        adrp    x0, .L.str
        add     x0, x0, :lo12:.L.str
        bl      std::__throw_out_of_range_fmt(char const*, ...)
.L.str:
        .asciz  "vector::_M_range_check: __n (which is %zu) >= this->size() (which is %zu)"
```

<https://godbolt.org/z/6jKa5KPxY>

`opeator[]()`の命令数が 2 であるのに対し、`at()`の（`i`が範囲内の場合の）命令数は 6 だった。
つまり、`i`が範囲内かどうかチェックするために 4 命令が追加された。

## まとめ

本ページでは STL シーケンシャルコンテナに対し`operator[]()`と`at()`のアセンブリ出力を比較した。
その結果、`at()`を使用することによるオーバーヘッドは高々 5 CPU 命令であることが分かった。
よって、多くの実アプリケーションでは`at()`により実行時間が有意に遅くなることはないと言える。

よって、以下の条件をすべて満たしている場合に限り、`at()`ではなく`operator[]()`を使用することを検討した方が良い。

- 範囲外アクセスをしない自信がある
  - for 文でイテレーションしているときや、アクセス直前に if 文でチェックしているとき
- コンテナアクセスが計算の大部分を占める
  - 例）行列演算、配列のフィルタリング
- ベンチマークを占める比較したとき、有意に実行速度に差がある

また、`at()`の代わりに`operator[]()`を使用する場合、範囲外アクセスのデバッグが困難になることを覚悟しなければならない。
`at()`を使用した場合は範囲外アクセスした時点で例外となるため発生箇所の特定は容易だが、
`operator[]()`で範囲外アクセスした場合の挙動は未規定なので、全く関係ないコードでバグが露見することがしばしばある。

そのため、保守性の観点では、本当に必要な場合以外は常に`at()`を使用するべきである。

なお、本記事を書いたモチベーションは、最近、範囲外アクセスによる Segmentation Fault の解析に半日溶かして虚無になったためである。
