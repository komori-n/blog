---
author: komori-n
categories:
  - 技術解説
date: "2023-05-31T22:30:32+09:00"
tags:
  - C++
keywords:
  - C++17
  - Copy Elision
  - Return Value Optimization
  - RVO
title: C++17におけるコピー省略（Copy Elision）
relpermalink: blog/copy-elision-in-cpp17/
url: blog/copy-elision-in-cpp17/
description: Copy Elisionは、C++11で追加された最適化機能の一つであり、特定の条件下で値のコピーやムーブを省略してパフォーマンスを向上させることができる。本ページでは、特にC++17以降でのCopy Elisionの動作について説明する。
---

**Copy Elision**は、C++11で追加された最適化機能の一つであり、特定の条件下で値のコピーやムーブを省略してパフォーマンスを向上させることができる。

本ページでは、特にC++17以降でのCopy Elisionの動作について説明する。

## 基礎

### 基本の直接初期化 `T(T(T()))`

まず、以下の式について考える。

```cpp
// [dcl.init]/17 より引用
T x = T(T(T()));
```

C++17では、この式の `x` はデフォルトコンストラクタにより直接初期化される。この式では、オブジェクトのコピーやムーブは一切発生しない。この挙動はC++標準規格で厳密に定義されており[^1]、たとえ `T` がコピー／ムーブ不可能な型であっても、問題なくコンストラクトすることができる[^2]。

[^1]:
    > If the initializer expression is a prvalue and the cv-unqualified version of the source type is the same class as the class of the destination, the initializer expression is used to initialize the destination object. (\[dcl.init\]/17)

[^2]: <https://godbolt.org/z/8eb9c86Kn>

```cpp
// コピー構築やムーブ構築ができない型
class T {
public:
  T() = default;
  T(const T&) = delete;
  T(T&&) = delete;
  T& operator=(const T&) = delete;
  T& operator=(T&&) = delete;
};

int main() {
  T x = T(T(T()));  // C++14ではエラー、C++17ではOK
}
```

これの応用として、`explicit` なコンストラクタを持つコピー／ムーブ不可能な型を引数で受け取ることができる[^3]。

[^3]: <https://godbolt.org/z/vhqT8Trfo>. なお、`T()` が `explicit` でないなら `func({})` とすることでC++14環境でもコンパイルを通すことができる

```cpp
class T {
public:
  explicit T() = default;
  T(const T&) = delete;
  T(T&&) = delete;
  T& operator=(const T&) = delete;
  T& operator=(T&&) = delete;
};

void func(T t) {}

int main() {
  func(T{});  // C++14ではエラー、C++17ではOK
}
```

### Copy Elision（コピー／ムーブの省略）

さらに、C++17では特定の状況下でコピー／ムーブを行うことなく、オブジェクトの直接構築ができる。

- 関数の `return` 文
- `throw`
- exception-declaration（catchの変数宣言）

特に、1つ目の場合は**Return Value Optimization（RVO）**と呼ばれる。関数の戻り値としてprvalue[^4]を指定すると、戻り先の変数を直接構築することができる。C++14以前はコンパイラに許可された挙動の一つで、必ずしも最適化されるわけではなかった。一方、C++17以降は仕様として必ず直接構築されることになっている。この機能を利用することで、コピー／ムーブできない型を関数の戻り値として返すことができる[^5]。

[^4]: 純粋（pure）な右辺値（rvalue）。詳しくは [Value categories - cppreference.com](https://en.cppreference.com/w/cpp/language/value_category) を参照。
[^5]: <https://godbolt.org/z/KW3rG66nT>

```cpp
// コピーやムーブができない型
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
  T x = func();  // C++14ではエラー、C++17ではOK
}
```

### ムーブ優先とNRVO

return時やthrow時にローカル変数（引数含む）を返す場合を考える。そのローカル変数はreturnの呼び出し時点で寿命が尽きるため、たとえ明示的に `std::move()` していなくても、ムーブコンストラクタが優先して呼ばれる。

```cpp
T func() {
    T t;
    return t;  // ムーブは不要（必要なら呼び出し元でムーブコンストラクタが呼ばれる）
}

int main() {
    T x = func();
}
```

上記のような、`return <ローカル変数>` という式の場合、たとえ明示的にムーブしなくても、ムーブ構築やムーブ代入が可能の場合はコピー構築やコピー代入よりも優先して呼ばれる。

なお、上記のようにローカル変数を返す場合、常にムーブしないほうが良い。というのも、**Named Return Value Optimization（NRVO）**と呼ばれる最適化が働く可能性があるためである。NRVOとは、ローカル変数を戻り値として返すときに、RVOと同様に戻り先の領域へ直接初期化する機能である。

ただし、NRVOはRVOとは異なり必ずしも行われることが保証されていない。そのため、RVOの例のようなコピー／ムーブ不可能な変数を返すことはできない。

つまり、関数内のローカル変数を戻り値として返すときは、可能なら戻り先の領域に直接構築（NRVO）、できない場合はムーブ構築、それもできない場合はコピー構築という優先順位になっている。

## 応用

関数の引数が値渡しのとき、以下のようにローカル変数をムーブして渡していないだろうか。

```cpp
void func(std::string a) { /* ... */ }

int main() {
    std::string s = "Hello World";
    func(std::move(s));
}
```

`std::move()` しているので十分高速に動作するが、まだ高速化の余地がある。というのも、このコードでは一時オブジェクト `s` のムーブやデストラクトのコストが発生してしまうためである[^6]。

[^6]: また、このコードは保守性についても改善の余地がある。変数 `s` は本質的には定数なので `const` をつけたいが、そうすると `std::move()` できなくなってしまう

よって、ここは以下のように書いたほうが速度面で優れる。

```cpp
void func(std::string a) { /* ... */ }

int main() {
    func(std::string{"Hello World"});
}
```

上で説明した通り、変数 `a` は直接コンストラクタが呼ばれて構築される。ムーブコンストラクタの呼び出しや一時オブジェクトのデストラクトが必要ないので、先のコードよりも高速に動作する。または、変数をローカル変数に保存したいのなら以下のような書き方もできる。

```cpp
void func(std::string a) { /* ... */ }

int main() {
    const auto s = [](){ return std::string{"Hello World"}; };
    func(s());
}
```

RVOの効果で `s()` は `a` に直接構築されるので、一時オブジェクトの構築は行われない。

## まとめ

- C++17では特定の条件下でオブジェクトの直接構築ができる
- ローカル変数を戻り値として返すときは NRVO が効く可能性があるので `std::move()` してはいけない
