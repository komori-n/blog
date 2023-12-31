---
author: komori-n
categories:
  - 技術解説
date: "2021-04-21T21:16:32+09:00"
tags:
  - C++
keywords:
  - C++03
  - C++11
  - C++17
  - C++20
  - explicit
  - 型変換
  - コンストラクタ
title: c++のexplicit指定子の使い方まとめ
relpermalink: blog/cpp-explicit-specifier/
url: blog/cpp-explicit-specifier/
description: c++におけるexplicit指定しの使い方についての簡単なまとめ。
---

c++のexplicit指定子（explicit specifier）の使い方をググってもいい感じの情報にはたどり着けなかったのでメモ。

## c++03まで

クラスのコンストラクタの宣言で `explicit` をつけると、次の2つの制限が適用される。

1. コピー初期化ができない
2. 暗黙の型変換ができない

それぞれコードで示すと以下のようになる。

```cpp
class Test {
public:
    explicit Test(int) {}
};

void hoge(Test test) {}

ina main() {
    // <コピー初期化>
    Test test1(0);         // OK
    Test test2 = 0;        // NG: intでコピー初期化はできない
    Test test3 = Test(0);  // OK
    // </コピー初期化>

    // <暗黙の型変換>
    hoge(Test(0));  // OK
    hoge(0);        // NG: intからTestへ暗黙の型変換はできない
    // </暗黙の型変換>
}
```

コンストラクタにexplicitがついていなければ問題ないが、explicitがついていることにより一部のケースがコンパイルできないようになる。

たったこれだけの機能だが、プログラマが気づきづらいミスを未然に防ぐことができる。`explicit` をつけることは「違う型の値を同一視しない」と言い換えられる。これのせいでコードの記述量が増えてしまう場合もあるが、知らないうちに型が変わっているという心配をしなくて済むようになる。

```cpp
//... 上のコードと同様のクラス定義

Test operator+(Test lhs, Test rhs);

int main() {
    Test x(10);
    Test z = x + 10;  // Test(int)がexplicitでない場合、
                      // Test z = x + Test(10);
                      // と解釈されてコンパイルが通ってしまう
}

Test fuga(void) {
    return 0;  // Test(int)がexplicitでない場合はOK
               // Test(int)がexplicitである場合はNG
}
```

有名なCoding Styleのひとつである [Google Coding Style](<http://Google C++ Style Guide>) では、引数が1変数のコンストラクタ（コピーコンストラクタ、ムーブコンストラクタ以外）には必ず `excplit` を付与するルールになっている。

## c++11

c++11では、explicit関連で2つの大きな変更があった。型変換演算子（ `operator <型>()` ）や2個以上引数を取るコンストラクタにもexplicitをつけられるようになった。

### 型変換演算子

型変換演算子は、以下のように直感に反する変換が行われることが多々あった。

```cpp
class Test {
public:
    operator bool() const;
};

int main() {
    Test test;
    std::cout << test + 5 << std::endl;
    // (int)((bool)test) + 5 と解釈されてコンパイルが通ってしまう
}
```

explicit指定子を用いることで、このような型変換演算子の暗黙の型変換を抑制することができる。

```cpp
class Test {
public:
    explicit operator bool() const;
};

int main() {
    Test test;
    std::cout << test + 5 << std::endl;
    // NG: Test + int はできない
}
```

c++11以降で型変換演算子を定義する場合、よっぽど特別な理由がない限りは必ず `explicit` を付与すべきである。上述の [Google Coding Style](http://google%20c++%20style%20guide/) でも、型変換演算子を独自定義する場合は必ず `explicit` 指定するルールが記載されている。

### 2個以上引数を取るコンストラクタ

c++11以降では一様初期化が可能になったことに伴い、2個以上引数を取るようなコンストラクタにもexplicitがつけられるようになった[^1]。

[^1]: 説明の都合上省略したが、引数が0個のコンストラクタへもexplicitを付与することができる。実際、c++11ではstd::pairのデフォルトコンストラクタにexplicitがついている。

```cpp
class Test {
public:
    explicit Test(int, int) {}
};

void hoge(Test test) {}

ina main() {
    // <コピー初期化>
    Test test1{0, 0};         // OK
    Test test2 = {0, 0};      // NG: {int, int}でコピー初期化はできない
    Test test3 = Test{0, 0};  // OK
    // </コピー初期化>

    // <暗黙の型変換>
    hoge(Test{0, 0});  // OK
    hoge({0, 0});      // NG: {int, int}からTestへ暗黙の型変換はできない
    // </暗黙の型変換>
}
```

機能としては1変数の場合と同様で、コピー初期化や暗黙の型変換を封じる効果がある。

2個以上の引数を取るコンストラクタについて `explicit` を付与するかどうかは個人の感覚に依るところが大きいと思う。実際、[Google Coding Style](http://google%20c++%20style%20guide/) では特に規定がされていない。判断基準は「`return {a, b}` と書けたほうがよいか？」ということだけである。

```cpp
Test hoge() {
    return {33, 4};  // このように書きたいなら Test(int, int) にexplictをつけない
                     // 常に Test{33, 4} と書かせたいなら explicitをつける
}
```

個人的には、使う側の記法だけの問題と捉えているので、`explicit` をつけないようにしている。一般には、 引数で渡された値をそのまま持つクラスには `explicit` をつけないが、それ以外には `explicit` をつける人が多いと思う。

## c++17

c++11時点の標準ライブラリでは `std::tuple` のコンストラクタには `explicit` がついている一方で、`std::pair` には `explicit` がついていかった。それにより、以下に示すようにコードの挙動が一貫していなかった。

```cpp
std::pair<int, int> hoge(void) {
    return {334, 264};  // OK: pair(int&&, int&&) は explicit ではない
}

std::tuple<int, int> fuga(void) {
    return {334, 264};  // NG: tuple(int&&, int&&) は explicit
}
```

c++17では標準ライブラリに変更が加えられた。`std::tupl`e と `std::pair` の各要素を渡すコンストラクタは、引数の型がそれぞれ暗黙の型変換可能な場合に限り `explicit` を付与するように仕様が改定された。つまり、上記のコード例はc++17以降ではいずれでもOKとなる。

## c++20

c++17の標準ライブラリの仕様改定において、条件付きで `explicit` を付与する仕様が追加された。これは、c++17時点では SFINAE により実装されていた。c++20以降は条件付きで `explicit` を付与する言語機能が追加され、より簡潔にコンストラクタを宣言できるようになった。具体的には、`noexcept` と同様に `explicit(<cond>)` （ `<cond>` は `bool` の定数式）と書けるようになり、 `<cond>` が `true` の場合のときに限り `explicit` と解釈される。

```cpp
template <typename T>
class Test {
public:
    template <typename U>
    explicit(std::is_same_v<T, U>) Test(U&& u);  // TとUが同じ型の場合のみ explicit
};
```

## まとめ

- c++11以前：1変数を引数に取るコンストラクタは（コピーコンストラクタ以外は）`explicit` を付与する
  - これにより、コピー初期化と暗黙の型変換を抑制して気づきづらいミスを減らせる
- c++11：↑ に加えて `operator T` にも `explicit` を付与する。それ以外（0変数、2変数以上）のコンストラクタにはつけてもつけなくても良い
- c++17：`std::pair` と `std::tuple` がどちらもいい感じに `explicit` を付与するようになった
- c++20: `explicit(<cond>)` と書けるようになった
