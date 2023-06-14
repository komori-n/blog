---
author: komori-n
draft: true
categories:
  - Programming
date: "2022-08-23T22:01:00+09:00"
guid: https://komorinfo.com/blog/?p=1786
id: 1786
permalink: /en/cpp-swallow-idiom-en/
tags:
  - C/C++
title: Throw away pack expansion results in C++
url: cpp-swallow-idiom-en/
---

This article describes how to throw away template parameter pack expansions in C++.

## Motivation

In template metaprogramming (TMP) in C++, you may want to discard pack expansion results after evaluating them. However, pack expansions are allowed in limited contexts. For example, the following code will not compile due to a syntax error:

```
/// Assign 0 to all of `arr[Indices...]`
template <int... Indices>
constexpr void Clear(Array& arr) noexcept {
  arr[Indices] = 0...;
  // ↑ error!
  // You cannot expand parameter pack here.
}
```

Therefore, one needs a particular idiom to throw away expanded values in such a situation.

The following text describes how to discard evaluation results of pack expansions before C++17 and after C++17.

## After C++17

It is easier in C++17 than in C++14. One can throw away pack expansions by fold expressions using `operator,()`. Fold expressions are a new syntax introduced in C++17, which can recursively apply binary operators to parameter packs. Typically, arithmetic or logical operators like `+` and `&&` are widely used, but `operator,()` is also applicable.

```
template <int... Indices>
constexpr void Clear(Array& arr) noexcept {
     ((arr[Indices] = 0), ...);
}
```

Compilers interpret the above example as `(arr[I0] = 0), ((arr[I1] = 0), ((arr[I2] = 0), ((...`. The expression executes all expressions from the starting one and does a pack expansion while throwing away results.

As described above, it is straightforward to discard pack expansion results in C++17.

## Before C++17

Before C++17, one can throw away pack expansion results only in the following situations:

- Function arguments `f(args...)`
- Initializer lists `{args...}`

I recommend the latter because in the former, the order of evaluation passed to a function is unspecified. Example:

```
/// （not recommended） A function that ignores all arguments
template <typename... Args>
constexpr void ConsumeValues(Args&&...) noexcept {}

template <int... Indices>
constexpr void Clear(Array& arr) noexcept {
     ConsumeValues((arr[Indices] = 0)...);
     // ↑ It is ok, but I don't recommend this code
     // Because the order of argument evaluation is unspecified.
}
```

Therefore, the following code is better to throw away values before C++17. This idiom is sometimes called **swallow idiom**.

````
/// An empty struct that is construcrible by any value
struct Anything {
  template <typename T>
  constexpr Anything(T&&) noexcept {}
};

/// A empty function that takes an initializer list of `Anything`
/// As `Anything` is constructible by any type, you can discard values by
/// ```
/// ConsumeValues({/* 式1 */, /* 式2 */, ...});
/// ```
constexpr void ConsumeValues(std::initializer_list<Anything>) noexcept {}
````

First, define a struct `Anything` that is constructible by any value. The type is implicitly convertible from any instance, so `std::initializer_list<Anything>` acts as a trash box for any expression.

```
ConsumeValues({33, 4, "hoge", 44.5});
/// All values is converted `Anything`, and removed away
```

Using this trash box, you can discard the expansion results of parameter packs.

```
template <int... Indices>
constexpr void Clear(Array& arr) noexcept {
     ConsumeValues({(arr[Indices] = 0)...});
}
```

Because arguments of initializer lists are evaluated from beginning to end, the swallow idiom is guaranteed to evaluate expansions from beginning to end.

```
template <int... Indices>
constexpr void Func(Array& arr) noexcept {
     ConsumeValues({(Something(arr[Indices]),0)...});
}
```
