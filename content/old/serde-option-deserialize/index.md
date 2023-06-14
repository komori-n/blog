---
author: komori-n
draft: true
categories:
  - プログラミング
date: "2021-02-28T17:11:22+09:00"
guid: https://komorinfo.com/blog/?p=1037
id: 1037
image: https://komorinfo.com/wp-content/uploads/2021/01/1200px-Rust_programming_language_black_logo.svg_.png
og_img:
  - https://komorinfo.com/wp-content/uploads/2021/01/1200px-Rust_programming_language_black_logo.svg_.png
permalink: /serde-option-deserialize/
tags:
  - Rust
title: serdeのDeserializeでnullと値なしを区別する
url: serde-option-deserialize/
---

## 環境

```
# rustc 1.49.0
serde = "1.0"
serde_derive = "1.0"
serde_json = "1.0"
```

## モチベ

次のような、Option型をメンバに取る構造体のデシリアライズについて考える。

```
use serde_derive::Deserialize;

#[derive(Debug, Deserialize)]
struct Hoge {
    val: Option<u64>,
}
```

この定義に対し、

1. 値が正しく格納されたjson
2. 値がnullであるjson
3. 値が入っていないjson

の3つを与えると、後者2つはいずれもNoneにデシリアイズされる。

```
let json_1 = r#"{ "val": 334 }"#;
let ans_1: Hoge = serde_json::from_str(json_1).unwrap();
assert_eq!(ans_1.val, Some(334));

let json_2 = r#"{ "val": null }"#;
let ans_2: Hoge = serde_json::from_str(json_2).unwrap();
assert_eq!(ans_2.val, None);

let json_3 = r#"{}"#;
let ans_3: Hoge = serde_json::from_str(json_3).unwrap();
assert_eq!(ans_2.val, None);
```

つまり、Option型を含む構造体のデフォルトのデシリアライザでは、null値と値なしは区別できない。

nullと値なしではデータの意味が変わってしまうようなjsonの場合、この挙動は都合が悪い。そのため、値なしの場合はデシリアライズを失敗させたい。

## やり方

シンプルにカスタムデシリアライザを定義するだけで実現できる。

```
use serde::{Deserialize, Deserializer};
use serde_derive::Deserialize;

#[derive(Debug, Deserialize)]
struct Hoge {
    #[serde(deserialize_with="deserialize_option")]
    val: Option<u64>,
}

// deny if entry is not exist
// (null is acceptable)
fn deserialize_option<'de, D, T>(deserializer: D) -> Result<Option<T>, D::Error>
    where D: Deserializer<'de>,
          T: Deserialize<'de>
{
    Deserialize::deserialize(deserializer)
}
```

\#\[serde(deserialize_with=…)\]でカスタムデシリアライザを指定する。直感的にはやや気持ち悪いが、これにより値のあるなしにかかわらずdeserialize_optionが呼ばれ、値なしの場合はパースに失敗するようになる。

```
let json_1 = r#"{ "val": 334 }"#;
let ans_1: Hoge = serde_json::from_str(json_1).unwrap();
assert_eq!(ans_1.val, Some(334));

let json_2 = r#"{ "val": null }"#;
let ans_2: Hoge = serde_json::from_str(json_2).unwrap();
assert_eq!(ans_2.val, None);

let json_3 = r#"{}"#;
let ans_3: Result<Hoge, _> = serde_json::from_str(json_3);
assert!(ans_3.is_err());
```

コード：<https://gist.github.com/komori-n/87064b81d14f773737571da43c1dd0ec>
