---
author: komori-n
categories:
  - Techniques
date: 2024-07-18T21:59:48+09:00
tags:
  - C++
keywords:
  - array
  - size
  - initialize
  - to_array
  - CATD
title: Initialize `std::array` without Length
relpermalink: blog/init-array-without-size
url: blog/init-array-without-size
description: In this article, we will describe how to initialize `std::array` without specifying its size
---

In this article, we will describe how to initialize `std::array` without specifying its size.

## 背景

Consider the following code.

```cpp
const std::array<int, 3> x = {3, 3, 4};
```

If the last element is no longer needed, one may modify the code to:

```cpp
const std::array<int, 3> x = {3, 3};  // -> {3, 3, 0}
```

Since the size of `x` is 3 but the length of the argument is 2,
all non-specified elements will be initialized with 0.
In contrast to C-array,`std::array` doesn't have a feature to detect the length of an array,
so one may need to do something non-trivial.

```cpp
const int x[]           = {3, 3, 4};  // ok
const std::array<int> x = {3, 3, 4};  // error
```

## Template Argument Deduction(C++17)

In C++17 and later, one can incorporate class template argument deduction (CTAD).

```cpp
namespace std {
template <class T, class... U>
array(T, U...) -> array<T, 1 + sizeof...(U)>;
}
```

By using the feature, one can omit specifying the size of an array.

```cpp
const std::array x = {3, 3, 4};  // -> deduced to std::array<int, 3>
const std::array y = {3, 3};     // -> deduced to std::array<int, 2>
```

Note that, unlike C-array, the feature cannot be applied if one of the variable-length template `U...` doesn't match `T`.

```cpp
const double x[]   = {3.0, 3.0f, 4};  // ok
const std::array x = {3.0, 3.0f, 4};  // error. The argument type is inconsistent
```

## std::to_array(C++20) / Create to_array(C++14)

In C++20 and later, one can use the function template `std::to_array` to omit size.
Unlike CTAD, `std::to_array` can explicitly specify the type of the array, so
it can be used even if the types of arguments are not the same.

```cpp
const std::array x = std::to_array({3, 3, 4});               // ok
const std::array y = std::to_array<double>({3.0, 3.0f, 4});  // ok
```

As `std::to_array` just transforms a C-array into `std::array`,
one can easily create it in C++14 or C++17.

```cpp
namespace detail {
template <typename T, std::size_t N, std::size_t... I>
constexpr std::array<T, N> to_array_impl(const T (&list)[N], std::index_sequence<I...>) {
  return {list[I]...};
}

template <typename T, std::size_t N, std::size_t... I>
constexpr std::array<T, N> to_array_impl(T (&&list)[N], std::index_sequence<I...>) {
  return {std::move(list[I])...};
}
} // namespace detail

template <typename T, std::size_t N>
constexpr std::array<T, N> to_array(const T (&list)[N]) {
  return detail::to_array_impl(list, std::make_index_sequence<N>{});
}

template <typename T, std::size_t N>
constexpr std::array<T, N> to_array(T (&&list)[N]) {
  return detail::to_array_impl(std::move(list), std::make_index_sequence<N>{});
}
```
