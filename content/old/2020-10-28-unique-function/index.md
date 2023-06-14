---
author: komori-n
draft: true
categories:
  - プログラミング
date: "2020-10-28T20:28:24+09:00"
guid: https://komorinfo.com/blog/?p=579
id: 579
image: https://komorinfo.com/wp-content/uploads/2020/09/cpp.png
og_img:
  - https://komorinfo.com/wp-content/uploads/2020/09/cpp.png
permalink: /unique-function/
tags:
  - C/C++
title: move-onlyな関数を扱えるstd::functionのようなものを実装する
url: unique-function/
---

## モチベーション

`std::function`は関数ポインタ、ラムダ式、関数オブジェクトなど多彩なファンクターを格納することができる。コールバックを引数で指定させたいときなど、「関数っぽいもの」を統一的に扱う場面で広く使われる。

しかし、`std::function`に渡すファンクターはcopy assignableでなければならなず、move-onlyなラムダ式や関数オブジェクトは渡すことができない。

move-onlyなラムダ式を使いたくなる場面なんてあるのかと思われるかもしれないが、`unique_ptr`などのmove-onlyなオブジェクトをラムダ式に渡したくなることがしばしばある。

```
std::unique_ptr<int> ptr = std::make_unique<int>(334);
std::function<void()> fn = [ptr = std::move(ptr)](void) {
  /* ... */
};  // error! move-onlyなラムダ式はstd::functionに格納できない
```

`unique_ptr`の代わりに`shared_ptr`を使えば`std::function`に渡せるようになるが、パフォーマンスのことを考えるとできれば`unique_ptr`のまま渡したい。

そこで、move-onlyなファンクターを扱える`std::function`の代替クラス`unique_function`を実装した。このようなクラスは、c++標準化委員会で現在も議論されている内容で、`std::unique_function`や`std::any_invoker`という名前でproposalが出されている（P0228、P0288）<span class="easy-footnote-margin-adjust" id="easy-footnote-1-579"></span><span class="easy-footnote">[<sup>1</sup>](https://komorinfo.com/blog/unique-function/#easy-footnote-bottom-1-579 "個人的には、<code>std::unique_function</code>が<code>std::function</code>のmove-only版であることは分かりやすいが、<code>std::any_invoker</code>は何をするクラスなのか分かりにくいと思う")</span>。

完成イメージはこんな感じ。

```
std::unique_ptr<int> ptr = std::make_unique<int>(334);
komori::unique_function<void()> fn = [ptr = std::move(ptr)](void) {
  /* ... */
};  // ok
do_something(std::move(fn));  // moveすればファンクターを渡せる
```

## unique_functionの実装

できるだけコードが短くなるよう意識してコードを書いた。その結果、100行未満に収めることができた。

以下が`unique_function`の実装全文である。

```
#pragma once

#include <utility>
#include <functional>

namespace komori {
  namespace detail {
    template <typename F, typename Res, typename... ArgTypes>
    struct invoke_helper {
      static Res invoke(void* storage, ArgTypes&&... args) {
        return
          std::invoke(*static_cast<F*>(storage), std::forward<ArgTypes>(args)...);
      }

      static void deleter(void* storage) {
        delete static_cast<F*>(storage);
      }
    };
  }


  template <typename T>
  class unique_function;

  template <typename Res, typename... ArgTypes>
  class unique_function<Res(ArgTypes...)> {
    using invoker_t = Res(*)(void*, ArgTypes&&...);
    using deleter_t = void(*)(void*);

    template <typename F>
    using helper = detail::invoke_helper<F, Res, ArgTypes...>;
  public:
    unique_function(void) : storage_(nullptr), invoker_(nullptr), deleter_(nullptr) {}

    unique_function(nullptr_t) : storage_(nullptr), invoker_(nullptr), deleter_(nullptr) {}
    template <typename F, typename DF=std::decay_t<F>>
    unique_function(F&& f)
    : storage_(new DF(std::forward<F>(f))),
      invoker_(&helper<DF>::invoke),
      deleter_(&helper<DF>::deleter) {}

    unique_function(unique_function&& f) : storage_(f.storage_), invoker_(f.invoker_), deleter_(f.deleter_) {
      f.storage_ = nullptr;
      f.invoker_ = nullptr;
      f.deleter_ = nullptr;
    }
    template <typename F>
    unique_function& operator=(F&& f) {
      unique_function(std::forward<F>(f)).swap(*this);
      return *this;
    }

    unique_function(const unique_function&) = delete;
    unique_function& operator=(const unique_function&) = delete;
    ~unique_function(void) {
      if (storage_) {
        deleter_(storage_);
        storage_ = nullptr;
      }
    }

    explicit operator bool(void) const {
      return storage_;
    }

    void swap(unique_function& f) {
      std::swap(storage_, f.storage_);
      std::swap(invoker_, f.invoker_);
      std::swap(deleter_, f.deleter_);
    }

    Res operator()(ArgTypes&&... args) {
      return invoker_(storage_, std::forward<ArgTypes>(args)...);
    }

  private:
    void* storage_;
    invoker_t invoker_;
    deleter_t deleter_;
  };
}
```

やっていることは非常に単純。ファンクターがセットされた際、`new`により動的にメモリ確保して`void* storage_`に格納する。また、`invoke_`（関数呼び出し）、`deleter_`（メモリ解放）という2つの関数ポインタを初期化する<span class="easy-footnote-margin-adjust" id="easy-footnote-2-579"></span><span class="easy-footnote">[<sup>2</sup>](https://komorinfo.com/blog/unique-function/#easy-footnote-bottom-2-579 "実装のミソはここ。<code>unique_function<Res(ArgTypes...)></code>は格納している型に関するtemplate parameterは持っていないが、ファンクターを渡された時に、その呼出方法とメモリ開放方法を覚えておくことで、ファンクターの型を忘れてしまっても良い構造になっている。頭いい。")</span> <span class="easy-footnote-margin-adjust" id="easy-footnote-3-579"></span><span class="easy-footnote">[<sup>3</sup>](https://komorinfo.com/blog/unique-function/#easy-footnote-bottom-3-579 "<code>unique_function</code>の中では動的に確保した<code>void*</code>でファンクターを管理しているので、<code>delete</code>する際は適切にメモリ解放するdeleterが必要になる。")</span>。

コードを短くするためにいくつか実装をサボった部分がある。

- small object optimization(SOO):[ libstdc++のstd::functionの実装を眺める](https://komorinfo.com/blog/libstd-function-impl/) で見たように、`std::function`の実装では小さなメモリに収まるファンクタは動的メモリ確保を行わず、静的領域に変数を格納されることが多い。一方、上記の実装では、ファンクターのサイズに関係なく動的にメモリを確保している<span class="easy-footnote-margin-adjust" id="easy-footnote-4-579"></span><span class="easy-footnote">[<sup>4</sup>](https://komorinfo.com/blog/unique-function/#easy-footnote-bottom-4-579 "これに対応しようとすると、型のサイズに応じて<code>invoke_helper</code>を分岐させたり、invoker, deleterに加えてmover（moveの時にポインタ付け替えで済ますか<code>std::move</code>をするか）を実装する必要があり、かなり大変。")</span>
- std::invoke: 関数の呼び出し部分でc++17で追加されたstd::invokeを使用している。c++11, 14しか使えない環境の場合、std::invokeに相当する機能を実装する必要がある（そんなに難しくない）
- const、noexceptなどのquelifier

コードは短いが色々調べながらの実装だったのでとても勉強になった。

本ページの実装は以下でも参照できる。
<https://gist.github.com/komori-n/dcc1af3f79481ff085a4835e6bcf8084>
