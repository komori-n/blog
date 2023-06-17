---
author: komori-n
categories:
  - やってみた
date: "2021-03-14T17:14:23+09:00"
tags:
  - C++
  - GoogleTest
keywords:
  - GoogleMock
  - Git
  - cmake
  - 単体テスト
  - モック
  - 導入
title: GoogleTest/GoogleMockをsubmoduleで管理する
relpermalink: blog/add-gtest-and-gmock-into-your-project/
url: blog/add-gtest-and-gmock-into-your-project/
description: GoogleTest/GoogleMockをgit submoduleでお手軽に導入する
---

GoogleTest/GoogleMockの導入を、何回やっても覚えられないので自分用にメモする。

## 環境

- Windows 10 Education 20H2
- Ubuntu 20.04 (with WSL2)
- [GoogleTest](https://github.com/google/googletest) v1.10.0
- cmake 3.16.3

## GoogleTestの導入方法

GoogleTest/GoogleMockを既存のプロジェクトに導入する方法は大きく分けて2つある。1つはローカルでビルドしたライブラリをインストールする方法で、もう1つは利用したいプロジェクトのsubmoduleに追加してcmakeでいい感じにリンクする方法がである。前者は個人で開発する場合に、環境構築を `make install` でサクッと行えるという利点がある。一方後者は、多人数で開発するときに開発者の間で環境をそろえやすいという利点がある。

本ページでは後者の、リポジトリのsubmoduleに追加する方法についてメモする。

ディレクトリ構造は以下のようにする。

- `src` : ソース（.cpp）
- `include` : ヘッダ（.hpp）
- `test` : テスト用ソース（XXX_test.cpp）
- `third-party` : 外部依存ライブラリ

### submoduleの追加

GoogleTestとGoogleMockはどちらも [google/googletest: Googletest – Google Testing and Mocking Framework](https://github.com/google/googletest) リポジトリで管理されている。これを、適当な位置（以下の例では third-party の下）にsubmoduleとして追加する。

```sh
mkdir third-party
cd third-party
git submodule add https://github.com/google/googletest.git
```

### CMakeLists.txtの作成

プロジェクトのソースとテスト用ソースからテスト用バイナリを生成するルールを記述する。

```cmake
cmake_minimum_required(VERSION 3.0)
project(google-test-test CXX)

set(PROGRAM google-test-test)

# Google Testの不要なキャッシュ変数をオフにしておく
option(BUILD_GMOCK "Builds the googlemock subprojects" OFF)
option(INSTALL_GTEST "Enables installation of googletest" OFF)

# 親プロジェクトのコンパイラ・リンカ設定を上書きするのを防ぐ（Windowsのみ）
set(gtest_force_shared_crt ON CACHE BOOL "" FORCE)

# Google Testをこのプロジェクトに組み込む
add_subdirectory(third-party/googletest)

file(GLOB TEST_SOURCES
  test/*.cpp)

file(GLOB SOURCES
  src/*.cpp)

list(REMOVE_ITEM SOURCES src/main.cpp)

add_executable(${PROGRAM}
  ${SOURCES}
  ${TEST_SOURCES}
)

target_link_libraries(${PROGRAM}
  PRIVATE
    # Google Testをリンクする
    gmock
    gtest
    gmock_main
)

target_include_directories(${PROGRAM}
  PUBLIC
    include
    third-party/googletest/googletest/include
    third-party/googletest/googlemock/include
)

enable_testing()
add_test(NAME GoogleTestTest COMMAND ${PROGRAM})
```

参考：[Google Testの使い方 – Qiita](https://qiita.com/shohirose/items/30e39949d8bf990b0462)

`main()` 関数は（ “gmock_main” の内に含まれている）GoogleTest用のものを用いるので、”src/main.cpp”をビルド対象から除外する必要がある。

GoogleMockが必要ない（GoogleTestのみ使いたい）場合、依存ライブラリとインクルードパスからgmockを削除し、依存ライブラリの”gmock_main” を “gtest_main” へと書き換えればよい。

## 使用例（動作確認）

2つの整数を足す `add(a, b)` という関数に対し、単体検査を書いてみる。

```cpp
// include/hoge.hpp
#pragma once

int add(int a, int b);
```

```cpp
// src/hoge.cpp

#include "hoge.hpp"

int add(int a, int b) {
    return a + b;
}
```

```cpp
// test/hoge_test.cpp

#include "gtest/gtest.hpp"
#include "hoge.hpp"

TEST(HogeTest, Add) {
    EXPECT_EQ(37, add(33, 4));
}
```

以下のコマンドにより、ビルドとテストを行える。

```sh
$ mkdir build
$ cd build
$ cmake ..
$ make -j
$ ./google-test-test
Running main() from ../third-party/googletest/googletest/src/gtest_main.cc
[==========] Running 1 test from 1 test suite.
[----------] Global test environment set-up.
[----------] 1 test from HogeTest
[ RUN      ] HogeTest.Add
[       OK ] HogeTest.Add (0 ms)
[----------] 1 test from HogeTest (0 ms total)

[----------] Global test environment tear-down
[==========] 1 test from 1 test suite ran. (0 ms total)
[  PASSED  ] 1 test.
```

導入はとても簡単なので、任意のC++プロジェクトに導入したほうがいい。
