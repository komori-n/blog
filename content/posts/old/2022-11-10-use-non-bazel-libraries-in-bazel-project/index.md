---
author: komori-n
draft: true
categories:
  - Programming
date: "2022-11-10T22:02:00+09:00"
guid: https://komorinfo.com/blog/?p=1878
id: 1878
permalink: /en/use-non-bazel-libraries-in-bazel-project/
tags:
  - Bazel
title: Use non-Bazel Libraries in Bazel Project
url: use-non-bazel-libraries-in-bazel-project/
---

One may want to use external libraries that Bazel does not manage when using Bazel.<span class="easy-footnote-margin-adjust" id="easy-footnote-1-1878"></span><span class="easy-footnote">[<sup>1</sup>](https://komorinfo.com/blog/en/use-non-bazel-libraries-in-bazel-project/#easy-footnote-bottom-1-1878 "Q. As one can know from <a rel="noreferrer noopener" href="https://bazel.build/docs/external" target="_blank">the official document</a>, why is this page needed? → A. Some people have unusual creativity.")</span>

```
cc_binary(
  name = "hello-world",
  srcs = ["main.cpp"],
  deps = [
    # external libraries that are not managed by bazel
  ],
)
```

To use local files in Bazel, one can use `new_local_repository`. <span class="easy-footnote-margin-adjust" id="easy-footnote-2-1878"></span><span class="easy-footnote">[<sup>2</sup>](https://komorinfo.com/blog/en/use-non-bazel-libraries-in-bazel-project/#easy-footnote-bottom-2-1878 "To use remote files managed by Git <code>build_file</code> or <code>build_file_content</code> in <code>git_repository</code> can be used the same way as this page. (<a rel="noreferrer noopener" href="https://bazel.build/rules/lib/repo/git#git_repository-build_file_content" target="_blank">ref</a>)")</span>

`new_local_repository` is a function that can be used in WORKSPACE files, which adds a BUILD file virtually and make a local directory Bazel project. One can specify the BUILD file by the option `build_file` or`build_file_content`. For example, if one wants to use OpenSSL in its local storage, a sample code with `build_file` is the following:

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

A sample code with `build_file_content` is the following:

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

In the latter case, one needs to set proper indents, or it will not be recognized as a correct BUILD file.
