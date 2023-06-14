---
author: komori-n
draft: true
categories:
  - プログラミング
date: "2021-02-03T17:00:12+09:00"
guid: https://komorinfo.com/blog/?p=868
id: 868
image: https://komorinfo.com/wp-content/uploads/2021/01/1200px-Rust_programming_language_black_logo.svg_.png
og_img:
  - https://komorinfo.com/wp-content/uploads/2021/01/1200px-Rust_programming_language_black_logo.svg_.png
permalink: /rust-toggl-api-deserialize/
tags:
  - Rust
  - Toggl Track
title: RustでToggl Reports API v2を叩いてdeserializeする
url: rust-toggl-api-deserialize/
---

やってみたらものすごく簡単で感動したのでメモ。

## 環境

- rustc 1.49.0
- cargo 1.49.0

パッケージのバージョンは以下。

```
[dependencies]
reqwest = { version = "0.11" }
tokio = { version = "1.0", features = ["full"] }
serde = "1.0"
serde_json = "1.0"
serde_derive = "1.0"
anyhow = "1.0"
```

## 手順

### reportを取ってくる

[公式リファレンス](https://github.com/toggl/toggl_api_docs/blob/master/reports.md) のRESTful APIの仕様を参考に、[requwest](https://github.com/seanmonstar/reqwest)でGETを投げる<span class="easy-footnote-margin-adjust" id="easy-footnote-1-868"></span><span class="easy-footnote">[<sup>1</sup>](https://komorinfo.com/blog/rust-toggl-api-deserialize/#easy-footnote-bottom-1-868 "toggl Report APIの詳細な使い方については <a href="https://komorinfo.com/blog/toggl-report-to-line-notify/">togglの日報をLINEに送る</a> を参照。")</span>。エラー処理を簡単にするために、[anyhow](https://crates.io/crates/anyhow)を用いている。

```
use anyhow::Result;

const EMAIL: &'static str = "ikamat.kmr@gmail.com";
const SUMMARY_URL:&'static str = "https://api.track.toggl.com/reports/api/v2/summary";

async fn get_report(token: &str, workspace_id: &str) -> Result<String> {
    let client = reqwest::Client::new();
    let query = [
        ("user_agent", EMAIL),
        ("workspace_id", workspace_id),
    ];

    let req = client
        .get(SUMMARY_URL)
        .query(&query)
        .basic_auth(token, Some("api_token"));
    println!("{:?}", req);

    let res = req
        .send().await?
        .text().await?;

    Ok(res)
}
```

URLにqueryをくっつけて認証情報とともに投げるだけである。async構文とanyhowクレートのおかげで、非同期処理にも関わらず驚くほど短く書ける。

### jsonのパース

togglへ上記のようなリクエストを投げると、以下のようなjsonが返ってくる。

```
{
    "total_grand":7420000,
    "total_billable":null,
    "total_currencies":
    [
        {
            "currency":null,
            "amount":null
        }
    ],
    "data":
    [
        {
            "id":162834023,
            "title":
            {
                "project":"Personal",
                "client":null,
                "color":"0",
                "hex_color":"hoge"
            },
            "time":141000,
            "total_currencies":
            [
                {
                    "currency":null,
                    "amount":null
                }
            ],
            "items":
            [
                {
                    "title":
                    {
                        "time_entry":"todoist"
                    },
                    "time":141000,
                    "cur":null,
                    "sum":null,
                    "rate":null
                }
            ]
        }
    ]
}
```

jsonのパースには [serde](https://github.com/serde-rs/serde) クレートを用いる。特に、serdeの [derive](https://serde.rs/derive.html) モジュールを使うことで、ユーザー定義の構造体のserialization/deserializationが簡単に書ける。

```
#[derive(Deserialize, Debug)]
struct EntryTitle {
    #[serde(rename = "time_entry")]
    title: String,
}

#[derive(Deserialize, Debug)]
struct Entry {
    time: i64,
    #[serde(rename = "title")]
    entry_name: EntryTitle,
}

#[derive(Deserialize, Debug)]
struct ProjectTitle {
    #[serde(rename = "project")]
    title: String,
}

#[derive(Deserialize, Debug)]
struct Project {
    time: i64,
    #[serde(rename = "title")]
    proj_name: ProjectTitle,
    #[serde(rename = "items")]
    entries: Vec<Entry>,
}

#[derive(Deserialize, Debug)]
struct Track {
    #[serde(rename = "total_grand")]
    time: i64,
    #[serde(rename = "data")]
    projs: Vec<Project>,
}
```

基本的には、構造体の前に `#[derive(Deserialize)]` をつけるだけで構造体へのパースをしてくれるようになる。渡されるjsonと定義した構造体の間で名前が違う場合は、上記の例のように `[serde(rename = "hoge")]` とすることで違いを吸収することができる<span class="easy-footnote-margin-adjust" id="easy-footnote-2-868"></span><span class="easy-footnote">[<sup>2</sup>](https://komorinfo.com/blog/rust-toggl-api-deserialize/#easy-footnote-bottom-2-868 "Deserializeでは、渡されたjsonのkeyの数が構造体のメンバの数より多い場合、余剰なエントリーは無視される。余剰エントリーを無視ではなくエラーにしたい場合は <code>#[serde(deny_unknown_fields)]</code> をつける。")</span>。

このように構造体定義に少し細工をしておくだけで、jsonのパースが1行でできるようになる。

```
#[tokio::main]
async fn main() -> Result<()> {
    let toggl_token = env::var("TOGGL_TOKEN")?;
    let workspace_id = env::var("WORKSPACE_ID")?;
    let proj_data = get_report(&toggl_token, &workspace_id).await?;

    // 1行でjsonのパースができる
    let track: Track = serde_json::from_str(&proj_data)?;

    println!("{:?}", track);

    Ok(())
}
```

`serde_json::from_str()` で自動的に型推論をしてパースまで行ってくれる。恐ろしく簡単だ。

## コード全文

[toggl_report.rs](https://gist.github.com/komori-n/3dfcdfaf4faf83332b5e236ca4d86abf)
