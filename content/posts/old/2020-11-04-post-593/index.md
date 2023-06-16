---
author: komori-n
draft: true
categories:
  - tips
date: "2020-11-04T20:59:50+09:00"
tags:
  - C/C++
  - SFINAE
title: 一度きりしか呼べないファンクターを管理したい
relpermalink: blog/post-593/
url: blog/post-593/
description: C++14環境にて、一度きりしか呼べないstd::functionライクなクラスを自作する。
---

[move-onlyな関数を扱えるstd::functionのようなものを実装する](/blog/unique-function/)の派生。

一度しか呼べないことが保証された`std::function`のようなものが欲しい。ファンクターをコールできるのは一度きりで、呼んだ後は必ずデストラクトされるようにしたい。ついでに、`std::function`では保持できないmove-onlyなファンクターも保持したい。

本ページのサンプルコードは以下の場所にある。
[onetime_function.hpp](https://gist.github.com/komori-n/5a5240441d95764ea12928f7a3a171e7)

以前に作った（このページ冒頭の記事）`komori::unique_function`との主な差分箇所を抜粋する。

```cpp
    template <std::nullptr_t Dummy = nullptr>
    auto operator()(ArgTypes&&... args)
    -> std::enable_if_t<!std::is_same<Res, void>::value && Dummy == nullptr, Res> {
      if (storage_) {
        auto&& res = invoker_(storage_, std::forward<ArgTypes>(args)...);
        onetime_function().swap(*this);
        return std::forward<Res>(res);
      } else {
        throw std::runtime_error("storage is null");
      }
    }

    template <std::nullptr_t Dummy = nullptr>
    auto operator()(ArgTypes&&... args)
    -> std::enable_if_t<std::is_same<Res, void>::value && Dummy == nullptr, Res> {
      if (storage_) {
        invoker_(storage_, std::forward<ArgTypes>(args)...);
        onetime_function().swap(*this);
      } else {
        throw std::runtime_error("storage is null");
      }
    }
```

戻り値（`Res`）が`void`かどうかによって実装を切り替えている[^1]。戻り値が`void`以外の場合、invokeの戻り値を中継して呼び出し元に返却する必要があるが、`void`の場合は必要ない。C++ではvoid型の変数を宣言することは許されないので、SFINAEを用いて実装を切り替えている。

[^1]: member関数のSFINAEによる実体化抑制は[SFINAEでtemplate classのメンバ関数の実体化を制御する](/blog/sfinae-template-class)を参照。

やっていることは単純で、関数呼び出し直後にnullファンクターとswapするだけである。入れ替え先のnullファンクターはswap直後にデストラクトされるので、storageで抱えているファンクターを2度以上呼び出すことはできない。

storageがnullの場合の処理はやや迷ったが、ここではruntime errorを上げるようにしている。

（2021/02/15追記）以下でコードを公開。

{{< github repo="komori-n/unique-function" >}}
