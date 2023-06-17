---
author: komori-n
categories:
  - Techniques
date: "2022-04-30T15:45:55+09:00"
tags:
  - C++
  - SFINAE
keywords:
  - C++17
  - Constraints
  - enable_if
  - nullptr
keywords:
title: "`Constraints` improves readability of SFINAE code"
relpermalink: en/blog/sfinae-constraints/
url: blog/sfinae-constraints/
description: This page introduces the `Constraints` pattern, which can reduce the complexity of SFINAE implementation.
---

This page introduces the `Constraints` pattern, which can reduce the complexity of SFINAE implementation.

In C++17, in order to switch function declaration according to input types, typical C++ programmers write codes like the following.[^1]

[^1]: See [Entry is not found - Secret Garden(Instrumental)](https://secret-garden.hatenablog.com/entry/2016/12/22/032008%22)(Japanese) and [std::enable_ifを使ってオーバーロードする時、enablerを使う？ - Qiita](https://qiita.com/kazatsuyu/items/203584ef4cb8b9e52462)(Japanese) to understand why C++ programmers often use `std::enable_if` and `std::nullptr_t`

```cpp
template <typename T,
          std::enable_if_t</* SFINAE condition */, std::nullptr_t> = nullptr>
void func(T&& t) {
    /* ... */
}
```

Those who don’t familiar with SFINAE might feel the above code is hard to read. It may be because the code uses `std::nullptr_t` and `nullptr`, which don’t seem to relate to the type `T`. In addition, more SFINAE conditions make the length of template parameters of `std::enable_if_t`, which leads to a reduction in readability.

In such a situation, the meta function `Constraints` could improve readability.

```cpp
namespace detail {
template <typename... Args>
struct ConstraintsImpl {
  using Type = std::nullptr_t;
};
}  // namespace detail

template <typename... Args>
using Constraints = typename detail::ConstraintsImpl<Args...>::Type;


// usage
template <typename T,
          Constraints<std::enable_if_t</* SFINAE condition 1 */>,
                      std::enable_if_t</* SFINAE condition 2 */>,
                      /* SFINAE conditions... */> = nullptr>
void func(T&& t) {
    /* ... */
}
```

`Constraints` just always returns `std::nullptr_t`. This idiom hides `std::nullptr_t`, which could improve readability.

```cpp
// example
template <typename T,
          Constraints<std::enable_if_t<std::is_default_constructible_v<T>>,
                      std::enable_if_t<std::is_nothrow_assignable_v<T>>> = nullptr>
void func(T&& t) noexcept {
    std::cout << "T is default constructible and nothrow assignable" << std::endl;
}
```

It may be true that the appearance is not very different from the original code. However, I found that it makes SFINAE codes more readable than I expected, so I am willing to use this idiom instead of `enabler` or `ALWAYS_TRUE` idiom.
