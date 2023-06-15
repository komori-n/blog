---
author: komori-n
draft: true
categories:
  - Programming
canonical: https://komorinfo.com/blog/en/sfinae-constraints-2/
date: "2022-07-11T18:30:47+09:00"
guid: https://komorinfo.com/blog/?p=1724
id: 1724
permalink: /en/sfinae-constraints-en/
tags:
  - C/C++
title: "`Constraints` improves readability of SFINAE code"
url: sfinae-constraints-en/
---

This page introduces the `Constraints` pattern, which can reduce the complexity of SFINAE implementation.

In C++17, in order to switch function declaration according to input types, typical C++ programmers write codes like the following<span class="easy-footnote-margin-adjust" id="easy-footnote-1-1724"></span><span class="easy-footnote">[<sup>1</sup>](https://komorinfo.com/blog/en/sfinae-constraints-en/#easy-footnote-bottom-1-1724 "See <a href="https://secret-garden.hatenablog.com/entry/2016/12/22/032008">【C++ Advent Calendar 2016 22日目】C++ で enable_if を使うコードのベストプラクティス &#8211; Secret Garden(Instrumental)</a> (Japanese) and <a href="https://qiita.com/kazatsuyu/items/203584ef4cb8b9e52462">std::enable_ifを使ってオーバーロードする時、enablerを使う？ &#8211; Qiita</a> (Japanese) to understand why C++ programmers often use <code>std::enable_if</code> and <code>std::nullptr_t</code>")</span>.

```
template <typename T,
          std::enable_if_t</* SFINAE condition */, std::nullptr_t> = nullptr>
void func(T&& t) {
    /* ... */
}
```

Those who don’t familiar with SFINAE might feel the above code is hard to read. It may be because the code uses `std::nullptr_t` and `nullptr`, which don’t seem to relate to the type `T`. In addition, more SFINAE conditions make the length of template parameters of `std::enable_if_t`, which leads to a reduction in readability.

In such a situation, the meta function `Constraints` could improve readability.

```
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

```
// example
template <typename T,
          Constraints<std::enable_if_t<std::is_default_constructible_v<T>>,
                      std::enable_if_t<std::is_nothrow_assignable_v<T>>> = nullptr>
void func(T&& t) noexcept {
    std::cout << "T is default constructible and nothrow assignable" << std::endl;
}
```

It may be true that the appearance is not very different from the original code. However, I found that it makes SFINAE codes more readable than I expected, so I am willing to use this idiom instead of `enabler` or `ALWAYS_TRUE` idiom.
