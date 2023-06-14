---
author: komori-n
draft: true
categories:
  - プログラミング
date: "2021-03-28T22:30:18+09:00"
guid: https://komorinfo.com/blog/?p=1089
id: 1089
image: https://komorinfo.com/wp-content/uploads/2020/09/cpp.png
og_img:
  - https://komorinfo.com/wp-content/uploads/2020/09/cpp.png
permalink: /post-1089/
tags:
  - C/C++
title: 生文字列リテラル（Raw String Literals）の使い方メモ
url: post-1089/
---

C++11には「生文字列リテラル（Raw String Literals）」というあまり知られていない機能がある。

例えば、JSOM文字列をコード中で使いたい場合、C++11以前の世界では以下のように書く。

```
constexpr const char* kJsonData = "{\"data\": \"Hello World\"}";
```

文字 `"` を文字列リテラル中で使いたい場合、 `\"` とエスケープを行う必要がある。短い文字列の場合は気合で書くだけではあるが、長いJSON文字列を作ろうとするとかなりしんどい。

生文字列リテラルは、 `R"(<contents>)"` で表される文字列リテラルで、 `<contents>` の中では `"` や `\` などの文字をエスケープなしで用いることができる<span class="easy-footnote-margin-adjust" id="easy-footnote-1-1089"></span><span class="easy-footnote">[<sup>1</sup>](https://komorinfo.com/blog/post-1089/#easy-footnote-bottom-1-1089 "Pythonなら <code>R"""&lt;contents>"""</code>、Rustなら <code>r#"&lt;contents>"#</code> に対応する機能である")</span>。

```
constexpr const char* kJsonData = R"({"data": "Hello World"})";
```

`"` だけでなく、改行文字等の特殊文字も書いた通りに解釈してくれる。

```
constexpr const char* kJsonData = R"({
    "data": "Hello World"
})";  // "{\n    \"data\": \"Hello World\"\n}" と同じ
```

`<contents>` の中には `)"` というパターンを含めることはできないが、その場合は終端部分に追加文字列を設定することもできる。

```
constexpr const char* kTestData = R"TEST("("+")")TEST";  // 結果： "("+")"
```

知らないからと言って困る機能ではないので意外と使っている人は少ないが、取り入れるだけでコードの可読性が上がるので頭の片隅で覚えておきたい機能だ<span class="easy-footnote-margin-adjust" id="easy-footnote-2-1089"></span><span class="easy-footnote">[<sup>2</sup>](https://komorinfo.com/blog/post-1089/#easy-footnote-bottom-2-1089 "ちなみに僕はclang-tidyくんのwarningで初めて知った")</span>。
