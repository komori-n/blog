---
author: komori-n
draft: true
categories:
  - Programming
date: "2022-11-10T22:02:00+09:00"
tags:
  - Bazel
title: Use non-Bazel Libraries in Bazel Project
permalink: /en/blog/use-non-bazel-libraries-in-bazel-project/
url: blog/use-non-bazel-libraries-in-bazel-project/
description: This page will explain how to use external libraries in Bazel
---

One may want to use external libraries that Bazel does not manage when using Bazel.

```py
cc_binary(
  name = "hello-world",
  srcs = ["main.cpp"],
  deps = [
    # external libraries that are not managed by bazel
  ],
)
```

To use local files in Bazel, one can use `new_local_repository`. [^1]

[^1]: To use remote files managed by Git `build_file` or `build_file_content` in `git_repository` can be used the same way as this page. ([ref](https://bazel.build/rules/lib/repo/git#git_repository-build_file_content)

`new_local_repository` is a function that can be used in WORKSPACE files, which adds a BUILD file virtually and make a local directory Bazel project. One can specify the BUILD file by the option `build_file` or`build_file_content`. For example, if one wants to use OpenSSL in its local storage, a sample code with `build_file` is the following:

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

A sample code with `build_file_content` is the following:

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

In the latter case, one needs to set proper indents, or it will not be recognized as a correct BUILD file.
