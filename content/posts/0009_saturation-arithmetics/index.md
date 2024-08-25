---
author: komori-n
date: 2024-08-25T11:24:25+09:00
categories:
  - 技術解説
tags:
  - C++
keywords:
  - 飽和演算
  - Saturation Arithmetics
  - ビルトイン関数
title: C++における飽和演算（Saturation Arithmetics）の実装
relpermalink: blog/saturation-arithmetics-cpp/
url: blog/saturation-arithmetics-cpp/
description: C++において、オーバーフローを検知するビルトイン関数が使える環境および使えない環境での飽和演算（Saturation Arithmetics）の実装方法について解説する。
---

C++において、オーバーフローを検知するビルトイン関数が使える環境および使えない環境での
飽和演算（Saturation Arithmetics）の実装方法について解説する。

なお、C++26 以降であれば、本ページで解説する `add_sat()` や `sub_sat()` などの関数は
標準ライブラリで提供されるため、自前で実装する必要はない。

本ページのコードはGitHubで公開しているので、興味のある方はリンクから参照してほしい。
なお、簡潔のために本ページの例示コードでは `constexpr` や SFINAE などの枝葉のコードは省略している。

{{< github repo="komori-n/saturation_arithmetic" >}}

## 飽和加算（`add_sat()`）

### ビルトイン関数が使えるとき

GCCのビルトイン関数 `__builtin_add_overflow()` が使える場合、
飽和加算は次のように実装できる[^builtin]。

[^builtin]: ビルトイン関数が使えるかどうかは `__has_builtin()` マクロで確認できる。詳しくは <https://clang.llvm.org/docs/LanguageExtensions.html#langext-feature-check> を参照

```cpp
template <typename T>
T add_sat(T x, T y) {
  T result{};
  if (__builtin_add_overflow(x, y, &result)) {
    return y >= 0 ? std::numeric_limits<T>::max() : std::numeric_limits<T>::min();
  }
  return result;
}
```

`__builtin_add_overflow(x, y, &result)` は GCC 5 以降で使えるビルトイン関数で、次のような処理を行う。

- `x + y` がオーバーフローしない場合、`result` に `x + y` の結果を格納し、`false` を返す
- `x + y` がオーバーフローする場合、`true` を返す

上記のコードでは、`__builtin_add_overflow()` でオーバーフローを検出し、
オーバーフローが発生した場合は `y` の符号に応じて `std::numeric_limits<T>::max()` または `std::numeric_limits<T>::min()` を返している。

### ビルトイン関数が使えないとき

`__builtin_add_overflow()` が使えない場合は、（符号付き整数のオーバーフローによる）
未定義動作を避けるために、次のように実装する。

```cpp
template <typename T>
T add_sat(T x, T y) {
  constexpr T kMax = std::numeric_limits<T>::max();
  constexpr T kMin = std::numeric_limits<T>::min();

  if (y > 0 && x > kMax - y) {
    return kMax;
  } else if (y < 0 && x < kMin - y) {
    return kMin;
  } else {
    return x + y;
  }
}
```

`y > 0` のときは最大値、`y < 0` のときは最小値を超えていないかチェックし、
オーバーフローが発生する場合は飽和値を返す。

## 飽和減算（`sub_sat()`）

飽和加算のときと同様に、`__builtin_sub_overflow()` が使える場合と使えない場合で実装方法が異なる。
それぞれ次のように実装できる。

### ビルトイン関数が使えるとき

```cpp
template <typename T>
T sub_sat(T x, T y) {
  T result{};
  if (__builtin_sub_overflow(x, y, &result)) {
    return y >= 0 ? std::numeric_limits<T>::min() : std::numeric_limits<T>::max();
  }
  return result;
}
```

### ビルトイン関数が使えないとき

```cpp
template <typename T>
T sub_sat(T x, T y) {
  constexpr T kMax = std::numeric_limits<T>::max();
  constexpr T kMin = std::numeric_limits<T>::min();

  if (y > 0 && x < kMin + y) {
    return kMin;
  } else if (y < 0 && x > kMax + y) {
    return kMax;
  } else {
    return x - y;
  }
}
```

## 飽和乗算（`mul_sat()`）

### ビルトイン関数が使えるとき

`__builtin_mul_overflow()` が使える場合は、飽和加算や飽和減算と同様に次のように実装できる。

```cpp
template <typename T>
T mul_sat(T x, T y) {
  T result{};
  if (__builtin_mul_overflow(x, y, &result)) {
    return y >= 0 ? std::numeric_limits<T>::max() : std::numeric_limits<T>::min();
  }
  return result;
}
```

### ビルトイン関数が使えないとき

`__builtin_mul_overflow()` が使えない場合は、条件分岐が少しだけ複雑になる。
コード例は次のとおりである。

```cpp
template <typename T>
T mul_sat(T x, T y) {
  constexpr T kMax = std::numeric_limits<T>::max();
  constexpr T kMin = std::numeric_limits<T>::min();

  if (x > 0 && y > 0) {
    // プラス方向のオーバーフローをチェック
    if (x > kMax / y) {
      return kMax;
    }
  } else if (x < 0 && y < 0) {
    // プラス方向のオーバーフローをチェック
    if (x < kMax / y) {
      return kMax;
    }
  } else if (x > 0 && y < 0) {
    // マイナス方向のオーバーフローをチェック
    if (y < kMin / x) {
      return kMin;
    }
  } else if (x < 0 && y > 0) {
    // マイナス方向のオーバーフローをチェック
    // うっかり `y > kMin / x` でオーバーフロー判定を行うと、x == -1 のときに未定義動作が発生する
    if (x < kMin / y) {
      return kMin;
    }
  }

  return x * y;
}
```

## 飽和除算（`div_sat()`）

飽和除算は基本的には普通の除算と同じだが、
`std::numeric_limits<T>::min() / -1` の場合にのみオーバーフローが発生するため別処理が必要である[^div]。

[^div]: 飽和除算のオーバーフローを判定するビルトイン関数は存在しない

```cpp
template <typename T>
T div_sat(T x, T y) {
  if constexpr (std::is_signed<T>::value) {
    if (x == std::numeric_limits<T>::min() && y == static_cast<T>(-1)) {
      return std::numeric_limits<T>::max();
    }
  }

  return x / y;
}
```

## 飽和キャスト（`saturate_cast<R>()`）

飽和キャスト`static_cast<R, T>(T x)` は、`x` を `R` 型にキャストするが、
`x` が `R` 型に収まらない場合には飽和値を返す。
これも未定義動作を避けるためには少し頭の体操が必要である。

```cpp
template <typename R, typename T>
R saturate_cast(T x) {
  using ST = std::make_signed_t<T>;
  using SR = std::make_signed_t<R>;
  using UT = std::make_unsigned_t<T>;
  using UR = std::make_unsigned_t<R>;

  if (x < 0) {
    if (std::is_unsigned<R>::value) {
      return 0;  // x が負かつ R が符号なしの場合は 0 に飽和
    } else if (static_cast<SR>(std::numeric_limits<R>::min()) > static_cast<ST>(x)) {
      // x が R の最小値より小さい場合は R の最小値に飽和
      // コンパイラの警告を抑制するために、符号付き型（ST, SR）で比較する
      return std::numeric_limits<R>::min();
    }
  } else if (static_cast<UR>(std::numeric_limits<R>::max()) < static_cast<UT>(x)) {
    // x が非負かつ R の最大値より大きい場合は R の最大値に飽和
    // コンパイラの警告を抑制するために、符号なし型（UT, UR）で比較する
    return std::numeric_limits<R>::max();
  }

  // キャストが安全な場合はそのままキャスト
  return static_cast<R>(x);
}
```
