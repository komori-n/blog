---
author: komori-n
categories:
  - Techniques
date: "2023-05-31T22:31:35+09:00"
tags:
  - C++
keywords:
  - C++17
  - copy elision
  - return value optimization
  - RVO
title: Copy Elision in C++17
relpermalink: en/blog/copy-elision-in-cpp17-en/
url: blog/copy-elision-in-cpp17-en/
description: Copy Elision is an optimization technique in C++ that allows compilers to avoid unnecessary copying of objects. This blog post will explain the behavior of copy elision in C++17, including basic initialization, return value optimization (RVO), named return value optimization (NRVO), and practical examples.
---

Copy Elision is an optimization technique in C++ that allows compilers to avoid unnecessary copying of objects.

This blog post will explain the behavior of copy elision in C++17, including basic initialization, return value optimization (RVO), named return value optimization (NRVO), and practical examples.

## Basic Initialization (`T(T(T()))`)

Let’s consider the following statement:

```cpp
// From [dcl.init]/17
T x = T(T(T()));
```

In C++17, the standard mandates that the variable `x` is directly initialized by a default constructor without copying or moving. [^1]
This applies even if `T` is a non-copyable/movable type.

[^1]:
    > If the initializer expression is a prvalue and the cv-unqualified version of the source type is the same class as the class of the destination, the initializer expression is used to initialize the destination object. (\[dcl.init\]/17)

```cpp
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

```cpp
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

```cpp
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

```cpp
void func(std::string a) { /* ... */ }

int main() {
    std::string s = "Hello World";
    func(std::move(s));
}
```

The argument variable `a` is move-constructed. As described above, the move here can be skipped by a copy elision technique.

```cpp
void func(std::string a) { /* ... */ }

int main() {
    func(std::string{"Hello World"});
}
```

In this code, the argument `a` is directly constructed by the argument `"Hello World"`. It works faster than the original code because no temporary object will be created.

If you want to avoid nests of parentheses, you can use a lambda expression.

```cpp
void func(std::string a) { /* ... */ }

int main() {
    const auto s = [](){ return std::string{"Hello World"}; };
    func(s());
}
```

By using a lambda expression, the return statement is optimized by RVO, which allows compilers to construct the argument directly by the string literal `"Hello World"`. This avoids the need for a temporary object and improves performance.
