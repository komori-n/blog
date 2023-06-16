---
author: komori-n
draft: true
categories:
  - Programming
date: "2023-05-31T22:31:35+09:00"
guid: https://komorinfo.com/blog/?p=2054
id: 2054
permalink: /en/copy-elision-in-cpp17-en/
tags:
  - C/C++
title: Copy Elision in C++17
url: copy-elision-in-cpp17-en/
---

Copy Elision is an optimization technique in C++ that allows compilers to avoid unnecessary copying of objects.

This blog post will explain the behavior of copy elision in C++17, including basic initialization, return value optimization (RVO), named return value optimization (NRVO), and practical examples.

## Basic Initialization (`T(T(T()))`)

Let’s consider the following statement:

```
// From [dcl.init]/17
T x = T(T(T()));
```

In C++17, the standard mandates that the variable `x` is directly initialized by a default constructor without copying or moving.<span class="easy-footnote-margin-adjust" id="easy-footnote-1-2054"></span><span class="easy-footnote">[<sup>1</sup>](https://komorinfo.com/blog/en/copy-elision-in-cpp17-en/#easy-footnote-bottom-1-2054 "</p>

<blockquote class="wp-block-quote"><p>If the initializer expression is a prvalue and the cv-unqualified version of the source type is the same class as the class of the destination, the initializer expression is used to initialize the destination object.</p><cite>[dcl.init]/17</cite></blockquote>

<p>")</span>. This applies even if `T` is a non-copyable/movable type.

```
// A non-copyable/movable type
class T {
public:
  T() = default;
  T(const T&) = delete;
  T(T&&) = delete;
  T& operator=(const T&) = delete;
  T& operator=(T&&) = delete;
};

int main() {
  T x = T(T(T()));  // OK in C++17
```

## Copy Elision

In C++17, objects are directly constructed in the following situations.

1. return statement
2. throw statement
3. exception declaration

The first one is called **Return Value Optimization(RVO)**, which is an optimization technique that mandates compilers directly construct the local variable by the return value. This can improve performance and reduce unnecessary copying/moving of objects. By using this feature, a function can return a non-copyable/movable type.

```
// A non-copyable/movable type
class T {
public:
  T() = default;
  T(const T&) = delete;
  T(T&&) = delete;
  T& operator=(const T&) = delete;
  T& operator=(T&&) = delete;
};

T func() { return T{}; }

int main() {
  T x = func();  // OK in C++17
}
```

## Named Return Value Optimization (NRVO) and Implicit Move

Consider the situation that a function returns or throws a local variable. As the lifetime of the variable is about to expire, move construction will be tried first even if it’s not moved.

```
T func() {
    T t;
    return t;  // move constructor/move assign will be used if possible
}

int main() {
    T x = func();
}
```

Even if not explicitly moved, move constructor or move assign operator will be used if possible.

Note that if a local variable is returned/thrown, **Named Return Value Optimization(NRVO)** may be applied by the compiler. NRVO is a technique that allows compilers to construct a returned local value storage instead of a function’s local storage. However, unlike RVO, NRVO may not always be applicable. Therefore, a function cannot return a non-copyable/movable local variable.

In short, when a function returns a local variable, NRVO is tried first, then a move constructor/assignment operator is tried, and finally, a copy constructor/assignment operator is used if neither is applicable.

## Practical Example

Consider the following program:

```
void func(std::string a) { /* ... */ }

int main() {
    std::string s = "Hello World";
    func(std::move(s));
}
```

The argument variable `a` is move-constructed. As described above, the move here can be skipped by a copy elision technique.

```
void func(std::string a) { /* ... */ }

int main() {
    func(std::string{"Hello World"});
}
```

In this code, the argument `a` is directly constructed by the argument `"Hello World"`. It works faster than the original code because no temporary object will be created.

If you want to avoid nests of parentheses, you can use a lambda expression.

```
void func(std::string a) { /* ... */ }

int main() {
    const auto s = [](){ return std::string{"Hello World"}; };
    func(s());
}
```

By using a lambda expression, the return statement is optimized by RVO, which allows compilers to construct the argument directly by the string literal `"Hello World"`. This avoids the need for a temporary object and improves performance.
