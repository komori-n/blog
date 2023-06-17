---
author: komori-n
draft: true
categories:
  - tips
date: "2022-11-10T22:01:00+09:00"
tags:
  - Bazel
title: Bazelで管理されていないライブラリをBazelで使う
relpermalink: blog/use-non-bazel-project-in-bazel/
url: blog/use-non-bazel-project-in-bazel/
description: Bazelで管理されていないライブラリをBazelから使う方法について扱う
---

Bazel で管理されていないライブラリを Bazel から使う方法について扱う[^1]。

[^1]: Q. なんで [Bazelの公式ドキュメント](https://bazel.build/docs/external) を読めばわかる内容をまとめたんですか？ → A. 世の中には独創性あふれるコードを書く方がたくさんいるのです

Bazelでプロジェクトを構築する際に、Bazel で管理されていないライブラリをリンクしたくなることがある。

```py
cc_binary(
  name = "hello-world",
  srcs = ["main.cpp"],
  deps = [
    # ★外部ライブラリをリンクしたい
  ],
)
```

ローカルに存在するファイルを Bazel で使いたいときは、`new_local_repository` を用いる[^2]。

[^2]: Gitリポジトリなどで管理されたファイルを取り込みたいときは、`git_repository` の `build_file` や `build_file_content` を用いれば良い（[ドキュメント](https://bazel.build/rules/lib/repo/git#git_repository-build_file_content)

`new_local_reppository` はWORKSPACE内で使える関数で、ローカルに存在するディレクトリにBUILDファイルを仮想的に追加できる。BUILDファイルは、`build_file` で指定するか、`build_file_content` でBUILDファイルの内容を直接書くことで指定する。例えば、ローカルにインストールされた OpenSSL を例に取ると、`build_file` を使う場合は

```py
# WORKSPACE.bazel
new_local_repository(
  name = "openssl",
  path = "/opt/homebrew/Cellar/openssl@3/3.0.5",
  build_file = "openssl.BUILD",
)
```

```py
# openssl.BUILD
cc_library(
  name = "lib",
  hdrs = glob(["include/**/*.h"]),
  srcs = glob(["lib/*.dylib"]),
  strip_include_prefix = "include",
  visibility = ["//visibility:public"],
)
```

`build_file_content` を使う場合は

```py
# WORKSPACE.bazel
new_local_repository(
  name = "openssl",
  path = "/opt/homebrew/Cellar/openssl@3/3.0.5",
  build_file_content = """
cc_library(
  name = "lib",
  hdrs = glob(["include/**/*.h"]),
  srcs = glob(["lib/*.dylib"]),
  strip_include_prefix = "include",
  visibility = ["//visibility:public"],
)""",
)
```

とそれぞれ書ける。なお、後者の方法の場合、インデントに注意しないと正しい BUILD ファイルだと認識されないので注意すること。
