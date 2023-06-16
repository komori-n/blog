---
author: komori-n
draft: true
categories:
  - プログラミング
date: "2021-07-27T22:20:36+09:00"
guid: https://komorinfo.com/blog/?p=1347
id: 1347
image: https://komorinfo.com/wp-content/uploads/2021/07/lambda.png
og_img:
  - https://komorinfo.com/wp-content/uploads/2021/07/lambda.png
permalink: /rust-aws-lambda/
tags:
  - AWS Lambda
  - Rust
title: Rust で AWS Lambda を利用する手順まとめ
url: rust-aws-lambda/
---

何回やっても忘れてしまうので自分用にメモ。Rust で Lambda 関数を作る手順をまとめる。

## やりたいこと

AWS Lambda の処理を Rust で書きたい。

これを実現するためには、Lambda 向けのバイナリをクロスコンパイルしてアップロードする必要がある。

## 実装

Rustにおいては、Lambda でのリクエスト&amp;レスポンスの処理には [awslabs/aws-lambda-rust-runtime](https://github.com/awslabs/aws-lambda-rust-runtime) を用いる。

```
use lambda_runtime::{handler_fn, Context, Error};
use serde_json::{json, Value};

#[tokio::main]
async fn main() -> Result<(), Error> {
    let func = handler_fn(func);
    lambda_runtime::run(func).await?;
    Ok(())
}

async fn func(event: Value, _: Context) -> Result<Value, Error> {
    let first_name = event["firstName"].as_str().unwrap_or("world");

    Ok(json!({ "message": format!("Hello, {}!", first_name) }))
}
```

\# README.md のサンプルコードより引用

`lambda_runtime::run` で handler 関数を渡すことで、リクエストが来るたびにその handler をコールしてくれる。AWS Lambda の起動／終了周りの面倒な処理を意識することなく、関数のInputやOutputの処理にだけ集中することができる。

実装する上で常に気をつけることが1つある。それは、SSLライブラリの取り扱いである。`reqwest` 等の通信ライブラリはデフォルトでOpenSSLを使うように設定されているが、クロスビルド環境に OpenSSL が入っていなかったり Custom Container で Open SSL を使えるようにしたりするなど手間が増える。そこで、OpenSSL ではなく純Rust製SSLライブラリである `rustls` を用いるのがよい。

多くのライブラリでは、features を指定することで SSL ライブラリを切り替える事ができるようになっている。

```
reqwest = { version = "0.11", default-features = false, features = ["rustls-tls"]}
```

### ビルド

作成したコードを `x86_64-unknown-linux-musl` 向けにクロスコンパイルする。クロスコンパイル用のツールチェーンが入っていない場合、以下のコマンドによりインストールできる。

```
$ rustup target add x86_64-unknown-linux-musl
```

クロスコンパイルは以下のようにして行う。

```
$ cargo build --release --target x86_64-unknown-linux-musl
```

Lambda の Custom Container で動作させるためには、バイナリの名前を `bootstrap` に変更して zip で圧縮する。

```
$ cp ./target/x86_64-unknown-linux-musl/release/${PROJECT_NAME} ./bootstrap
$ zip lambda.zip bootstrap
```

この zip ファイルを GUI または CUI でアップロードすることで、Lambda 関数の作成、変更ができる。

### ローカルでのデバッグ方法

[`lambci/lambda` コンテナ](https://hub.docker.com/r/lambci/lambda/) を用いることで、本番の Lambda を模擬した環境をローカルに作れる。

上で作った `bootstrap` バイナリが置いてあるディレクトリに移動し、以下のコマンドを入力することでコンテナを立ち上げることができる。

```
$ docker run -it --rm -v $(pwd):/var/task:ro,delegated -e DOCKER_LAMBDA_USE_STDIN=1 -e AWS_LAMBDA_FUNCTION_MEMORY_SIZE=128 -e RUST_LOG=info lambci/lambda:provided
{}^D
START RequestId: 6a7581f0-b35d-11e7-a0d2-61405b686b7e Version: $LATEST
END RequestId: 6a7581f0-b35d-11e7-a0d2-61405b686b7e
REPORT RequestId: 6a7581f0-b35d-11e7-a0d2-61405b686b7e  Init Duration: 13150.71 ms      Duration: 8.14 ms       Billed Duration: 100 ms Memory Size: 128 MB     Max Memory Used: 18 MB

{"message":"Hello, world!"}
```

実行時間や大まかなメモリ使用量も出してくれる。Lambda に割り当てるメモリ量の下限を攻めたいときは、ローカルでの実測値を元に決めるのがよい。

## 関数の作成

### GUIで操作する場合

<figure class="wp-block-image size-large">![](https://komorinfo.com/wp-content/uploads/2021/07/image-2-1024x472.png)</figure>Lambdaの管理画面で「関数の作成」を押して、「一から作成」オプションを選択し、ランタイムを「Amazon Linux 2でユーザー独自のブートストラップを提供する」を選択して関数を作成する。

<figure class="wp-block-image size-large">![](https://komorinfo.com/wp-content/uploads/2021/07/image-3.png)</figure>次に、「コードソース」の右上隅の「アップロード元」の中の「.zip ファイル」を選択して前節で作成した zip ファイルをアップロードする。なお、バイナリサイズが 10MB を超える場合は直接のアップロードはできない。その場合は S3 を経由する必要がある。

### CUIで作成する場合

[AWS CLI](https://aws.amazon.com/jp/cli/) の `create-function` コマンドにより、上記の関数の作成とデプロイを簡単に行うことができる。

例えば以下は、Custom Runtimeを用いた「test」という名前のLambda関数を作成する例である。

```
$ aws lambda create-function \
  --function-name test \
  --runtime provided.al2 \
  --handler function.handler \
  --role arn:aws:iam::xxxxxxxxxxx:role/Lambda-only \
  --zip-file fileb://lambda.zip
```
