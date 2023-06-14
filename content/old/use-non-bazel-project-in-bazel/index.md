---
author: komori-n
draft: true
categories:
  - プログラミング
date: "2022-11-10T22:01:00+09:00"
guid: https://komorinfo.com/blog/?p=1865
id: 1865
permalink: /use-non-bazel-project-in-bazel/
tags:
  - Bazel
title: Bazelで管理されていないライブラリをBazelで使う
url: use-non-bazel-project-in-bazel/
---

Bazel で管理されていないライブラリを Bazel から使う方法について扱う<span class="easy-footnote-margin-adjust" id="easy-footnote-1-1865"></span><span class="easy-footnote">[<sup>1</sup>](https://komorinfo.com/blog/use-non-bazel-project-in-bazel/#easy-footnote-bottom-1-1865 "Q. なんで <a rel="noreferrer noopener" href="https://bazel.build/docs/external" target="_blank">Bazelの公式ドキュメント</a> を読めばわかる内容をまとめたんですか？ → A. 世の中には独創性あふれるコードを書く方がたくさんいるのです")</span>。

Bazelでプロジェクトを構築する際に、Bazel で管理されていないライブラリをリンクしたくなることがある。

```
cc_binary(
  name = "hello-world",
  srcs = ["main.cpp"],
  deps = [
    # ★外部ライブラリをリンクしたい
  ],
)
```

ローカルに存在するファイルを Bazel で使いたいときは、`new_local_repository` を用いる<span class="easy-footnote-margin-adjust" id="easy-footnote-2-1865"></span><span class="easy-footnote">[<sup>2</sup>](https://komorinfo.com/blog/use-non-bazel-project-in-bazel/#easy-footnote-bottom-2-1865 "Gitリポジトリなどで管理されたファイルを取り込みたいときは、<code>git_repository</code> の <code>build_file</code> や <code>build_file_content</code> を用いれば良い（<a rel="noreferrer noopener" href="https://bazel.build/rules/lib/repo/git#git_repository-build_file_content" target="_blank">ドキュメント</a>）")</span>。

`new_local_reppository` はWORKSPACE内で使える関数で、ローカルに存在するディレクトリにBUILDファイルを仮想的に追加できる。BUILDファイルは、`build_file` で指定するか、`build_file_content` でBUILDファイルの内容を直接書くことで指定する。例えば、ローカルにインストールされた OpenSSL を例に取ると、`build\_file` を使う場合は

```
# WORKSPACE.bazel
new_local_repository(
  name = "openssl",
  path = "/opt/homebrew/Cellar/openssl@3/3.0.5",
  build_file = "openssl.BUILD",
)
```

```
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

```
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
