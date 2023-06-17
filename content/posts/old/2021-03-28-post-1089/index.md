---
author: komori-n
categories:
  - 技術解説
date: "2021-03-28T22:30:18+09:00"
tags:
  - C++
keywords:
  - C++11
  - 生文字列リテラル
  - Raw String Literals
  - 使い方
  - json
  - エスケープ
title: 生文字列リテラル（Raw String Literals）の使い方メモ
relpermalink: blog/post-1089/
url: blog/post-1089/
description: C++11で追加された生文字列リテラル（Raw String Literals）の使い方について
---

C++11には「生文字列リテラル（Raw String Literals）」というあまり知られていない機能がある。

例えば、JSOM文字列をコード中で使いたい場合、C++11以前の世界では以下のように書く。

```cpp
constexpr const char* kJsonData = "{\"data\": \"Hello World\"}";
```

文字 `"` を文字列リテラル中で使いたい場合、 `\"` とエスケープを行う必要がある。短い文字列の場合は気合で書くだけではあるが、長いJSON文字列を作ろうとするとかなりしんどい。

生文字列リテラルは、 `R"(<contents>)"` で表される文字列リテラルで、 `<contents>` の中では `"` や `\` などの文字をエスケープなしで用いることができる[^1]。

[^1]: Pythonなら `R"""<contents>"""`、Rustなら `r#"<contents>"#` に対応する機能である

```cpp
constexpr const char* kJsonData = R"({"data": "Hello World"})";
```

`"` だけでなく、改行文字等の特殊文字も書いた通りに解釈してくれる。

```cpp
constexpr const char* kJsonData = R"({
    "data": "Hello World"
})";  // "{\n    \"data\": \"Hello World\"\n}" と同じ
```

`<contents>` の中には `)"` というパターンを含めることはできないが、その場合は終端部分に追加文字列を設定することもできる。

```cpp
constexpr const char* kTestData = R"TEST("("+")")TEST";  // 結果： "("+")"
```

知らないからと言って困る機能ではないので意外と使っている人は少ないが、取り入れるだけでコードの可読性が上がるので頭の片隅で覚えておきたい機能である。
