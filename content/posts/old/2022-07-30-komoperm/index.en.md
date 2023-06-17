---
author: komori-n
categories:
  - Techniques
date: "2022-07-30T20:07:00+09:00"
tags:
  - C++
keywords:
  - permutation
  - duplication
  - library
  - publication
  - compile-time
title: Handle permutations with duplicates at compile time
relpermalink: en/blog/komoperm/
url: blog/komoperm/
description: I created a simple library that handles permutation sequences with duplicates at compile time in C++14.
---

I created a simple library that handles permutation sequences with duplicates at compile time in C++14.

## Overview

I published an open-source library called komoperm, which handles permutation sequences with repetition.

{{< github repo="komori-n/komoperm" >}}

It can calculate an index of a sequence of integers or enumerations or generate a sequence corresponding to the given index.

```cpp
#include "komoperm/komoperm.hpp"

enum Hoge {
    A, B, C,
};

int main() {
    constexpr komoperm::Permutations<Hoge, A, A, A, B, B, C> p;

    static_assert(p.Size() == 60,
        "The number os possible permutations is 60");

    static_assert(p.Index({B, A, B, C, A, A}) < 60,
        "{B, A, B, C, A, A} is a permutation of {A, A, A, B, B, C}");

    static_assert(p.Index(p.Get(10)) == 10,
        "Get() generates the 10th permutation");
}
```

A set of permutation sequences `komoperm::Permutations` have two template parameters: typename `T` and sequence values `Vals...`. The values `Vals...` don’t have to be sorted. Moreover, the same values don’t need to be in consecutive positions.

The komoperm calculates all expressions at compile time and works fast even at runtime, thanks to template calculation. The memory consumption at compile time is relatively small because they don’t use template recursions.

It uses only C++14 features In the following section, I would like to show how to realize these features.

## Implementation

The most challenging point in komoperm is not the generation of sequences but the creation of a helpful type `PermutationImpl`.

```cpp
Input:
Permutations<T, Vals...>

Output:
PermutationsImpl<
  T,
  N, // sizeof...(Vals)
  M, // The number of the most frequent value in Vals...
  ItemCount<
    Val,  // A value
    N2,   // How many remaining symbols are to be placed
    C    　// How many `Val` is to be placed
  >,
  ItemCount<
    // ...
  >
  ...
>
```

A type `PermutationImpl` contains each `Val` and its counts `C` as template parameters. By using this type, we can quickly realize permutation operations. In the above code example, values except for `Val`, `N2`And `C` are easily obtained by `Vals...`. Therefore, we focus on how we could make a type that has `<Val, N2, C>...` template parameters.

In komoperm:

1. Get unique values in `Vals...`
2. Sort `Vals...`
3. Count the number of `Val` for each `Val`
4. Expand result of 3.

Note that komoperm doesn’t use template recursion, so it doesn’t need massive memory at compile time.

1., 2., and 3. are not so difficult. [This code](https://github.com/komori-n/komoperm/blob/main/src/komoperm.hpp#L240-L308) and [this code](https://github.com/komori-n/komoperm/blob/main/src/komoperm.hpp#L494-L547) realize these features without recursions.

The toughest part is No.4. From 1-3, we have the following three arrays.

- An array that contains unique `Val`s
- The number of `Val`s in i, i+1,i+2,…
- The number of `Vals`

For example, consider a sequence `A, A, A, B, B, C`. The above sequences are as follows.

- `{A, B, C}`
- `{6, 3, 1}`
- `{3, 2, 1}`

Now, we would like to create a new type whose template parameters are ordered like `<A, 6, 3>, <B, 3, 2>, <C, 1, 1>`. One may think that is not easy, but we can realize it by index substitutions and template parameter pack expansions.

```cpp
template <typename T, T... Vals, std::size_t... Indices>
struct MakePermutationsImpl<ValueSet<T, Vals...>,
                            std::index_sequence<Indices...>> {
 private:
  static constexpr auto Impl() noexcept {
    constexpr auto kValue = MakeItemCountsImplCalc<T, Vals...>();
    using type = PermutationsImpl<
        T, sizeof...(Vals), std::max({kValue.counts[Indices]...}),
        ItemCount<T, kValue.values[Indices], kValue.remains[Indices],
                  kValue.counts[Indices]>...>;
    return type{};
  }

 public:
  using type = decltype(Impl());
};
```

The point is L1 and 9-10. The parameter pack expansion `ItemCount<values[Indices], remain[Indices], counts[Indices]>...` generates the desired type sequence using an index parameter pack `Indices...`, t.

## Conclusion

In this article, I showed basic techniques for permutation sequence with repetition. I’ll be happy if you find the difficulty of c++ templates.
