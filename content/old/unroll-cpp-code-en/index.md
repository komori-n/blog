---
author: komori-n
draft: true
categories:
  - Programming
date: "2022-12-19T19:39:47+09:00"
guid: https://komorinfo.com/blog/?p=1903
id: 1903
permalink: /en/unroll-cpp-code-en/
tags:
  - C/C++
title: Unroll for-loops in C++
url: unroll-cpp-code-en/
---

## Overview

Loop unrolling is a widely used technique in C++. By reducing conditional branches and pipeline stalls, although it increases the size of binaries, most compilers generate a faster binary for unrolled code.

In C++, there are three kinds of ways of loop unrolling methods:

- By Hand: Unroll loops by macro functions
- Unroller: Expand code by meta functions and lambda expressions
- Pragma: Ask compilers to expand

Each of them has pros/cons and should be used according to the situation. In the remainder of this page, each will be discussed individually.

## Unrolling by Hand

It may be the first method that comes to mind, but the simplest way of unrolling is to use a macro function that repeats the argument.

```
#include <iostream>

// Repeat the expression `p` four times.
#KOMORI_UNROLL_4(p) \
  do { \
    p; \
    p; \
    p; \
    p; \
  } while(false)

int main() {
  // Repeat `std::cout << "Hello World" << std::endl;` four times
  KOMORI_UNROLL_4(std::cout << "Hello World" << std::endl);

  // Output：
  // Hello World
  // Hello World
  // Hello World
  // Hello World
}
```

In the above example, the macro function `KOMORI_UNROLL_4(p)` simply repeats the expression `p` four times. One can easily realize loop unrolling by this simple macro function.

With a little modification, it is possible to unroll (virtually) any length of loops by the following code. <span class="easy-footnote-margin-adjust" id="easy-footnote-1-1903"></span><span class="easy-footnote">[<sup>1</sup>](https://komorinfo.com/blog/en/unroll-cpp-code-en/#easy-footnote-bottom-1-1903 "If one wants to unroll a multi-level loop, one can use <a href="https://www.boost.org/doc/libs/1_80_0/libs/preprocessor/doc/index.html">Boost.Preprocessor</a>.")</span>

```
#include <iostream>

// `expr` を `num` 回分アンロールする
// Unroll the expression `expr` `num`-times.
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
// ...

int main() {
  // Repeat `std::cout << "Hello World" << std::endl;` four times
  KOMORI_UNROLL(4, std::cout << "Hello World" << std::endl);

  // Output：
  // Hello World
  // Hello World
  // Hello World
  // Hello World
}
```

The disadvantage of code cloning is reduced readability and maintenanceability. One must pass an expression to be unrolled to the macro function, which results in higher code complexity.

In addition to this, as macro functions are expanded in the preprocessing phase, one cannot use compile-time (constexpr) constants. In other words, loop counts must be integer literals or macro constants.

On the other hand, the good point of code cloning is that it will likely be unrolled for any loop. It repeats the same expression at the code level, so there is no ambiguity during unrolling.

## Unroller (template class)

The second method is the unroller idiom. _Unroller_ is a meta function that expands a passed argument N times, which is often shown as a template function example. One can implement an unroller class by “constexpr if”.

```
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
  // Repeat `std::cout << "Hello World" << std::endl;` four times
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

The invocation `Unroller<N>::Execute()` will be expanded as `Unroller<N>::Execute()` -&gt; `Unroller<N-1>::Execute()` -&gt; … -&gt; `Unroller<0>::Execute()`, and each `Execute()` calls the given function object. This expansion is executed at compile time, so the expression will almost surely be unrolled.

However, `Unroller` has a critical drawback: _the lack of early returning_. Expressions to be expanded are packed into a lambda expression, which makes it difficult to exit in the middle of the loop. Therefore, if a loop has an exit condition, one cannot unroll it by unrollers.

## Pragma unroll

The third method is to ask compilers to unroll loops.

Recent compilers sometimes unroll loops automatically and have special unrolling directives. For example, unrolling directives for GCC is `#pragma GCC unroll n`, and that for clang is `#pragma unroll n`. One can unroll loops by adding these directives before `for`.

```
int main() {
  // Repeat `std::cout << "Hello World" << std::endl;` four times
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

One can unroll loops and, at the same time, keep code clean by unrolling based on compiler features.

However, unrolling by compiler features can lead to low code portability. The argument for pragma directives (or pragma operators) depends on compiler implementations, and some compilers don’t have loop unrolling directives. Moreover, compilers sometimes ignore unrolling directives, so one should confirm that the machine code generated by the compiler is unrolled as intended.

## Conclusion

<figure class="wp-block-table is-style-vk-table-border-top-bottom">| Method | Pros | Cons |
|---|---|---|
| By hand | easy to understand. | Readability is very low.   It cannot use constexpr constants for loop counts. |
| Unroller | Almost surely unrolled. | It cannot be used with early returns. |
| Pragma | Almost no change is required. | Its behavior depends on compilers.   It is sometimes not unrolled. |

</figure>On this page, I introduced three major unrolling methods in C++. Each has pros/cons, so one must select the best method according to the balance between readability and efficiency.
