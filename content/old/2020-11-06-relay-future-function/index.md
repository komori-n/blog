---
author: komori-n
draft: true
categories:
  - プログラミング
date: "2020-11-06T20:43:22+09:00"
guid: https://komorinfo.com/blog/?p=574
id: 574
image: https://komorinfo.com/wp-content/uploads/2020/09/cpp.png
og_img:
  - https://komorinfo.com/wp-content/uploads/2020/09/cpp.png
permalink: /relay-future-function/
tags:
  - C/C++
title: std::functionやunique_functionを用いて、std::futureを中継する
url: relay-future-function/
---

## 問題設定

`std::future<X>`（`X`は構造体）を返す関数`func_a(int a)`を考える。背後にいるworker threadに要求を投げて、その戻り値を非同期に受け取ような関数を想定している。

```
struct X;
std::future<X> func_a(int a);
```

`func_a`はスレッドセーフである必要はないが、戻り値の`future`に値がセットされるまでの間にまた呼ばれる可能性はある。

以下では、この`func_a`の実装について考える。

さて、`func_a`のworker threadに計算をお願いする部分を別の関数`func_b`として切り出したい。関数`func_b`は、futureパターン等を用いて要求をworker threadに渡し、コンテキストをすぐに返す関数とする。ここで、切り出した関数の内部の処理は構造体`X`に依存させず、`X`と等価な情報を持つ構造体`Y`を用いるとする<span class="easy-footnote-margin-adjust" id="easy-footnote-1-574"></span><span class="easy-footnote">[<sup>1</sup>](https://komorinfo.com/blog/relay-future-function/#easy-footnote-bottom-1-574 "<code>X</code>は外部との互換性のために使う構造体で、将来構造が変更される可能性がある状況を想定している。")</span>。加えて、`func_b`をtemplate関数にしてヘッダーに置くことも禁止とする<span class="easy-footnote-margin-adjust" id="easy-footnote-2-574"></span><span class="easy-footnote">[<sup>2</sup>](https://komorinfo.com/blog/relay-future-function/#easy-footnote-bottom-2-574 "関数の実装が複雑で、ヘッダーにおくべきでない状況を想定している。")</span>。この制限に従えば、関数`func_b`の引数や戻り値はある程度柔軟に決めてもよい。

```
struct Y;

// func_bは自由に引数や戻り値を変えてもよい。
// ただし、Xに依存してはならない。
// また、func_bをtemplate関数にしてもいけない。

// 以下のいずれも形式でもOK
std::future<Y> func_b(int a);                               // 計算結果が出たらfutureに値が入る
void func_b(int a, std::promise<Y> y);                      // 計算結果が出たらpromiseに値をセットする
void func_b(int a, std::function<void(const Y&)> functor);  // 計算結果を与えられたfunctorに渡す

// 以下のいずれの形式もNG
Y func_b(int a);                                            // 非同期に実行できない
std::future<X> func_b(int a);                               // Xに依存している
template <typename F>
void func_b(int a, F functor);                              // templateを使っている
```

仮に`X=Y`の場合、以下のようにすれば簡単に実現できる。

```
void func_b(int a, std::promise<X> promise);

std::future<X> func_a(int a) {
  std::promise<X> promise;
  std::future<X> future = promise.get_future();

  // promiseをfunc_bへ、futureを呼び出し元に返すことで、計算結果を呼び出し元に返せる
  func_b(a, std::move(promise));
  return future;
}
```

これが`X!=Y`のときは途端に難しくなる。上記のような`func_b`にpromiseを渡す方式の場合、返ってきた`future<Y>`を`promise<X>`に変換して格納し直す必要があるためである。

```
void func_b(int a, std::promise<Y> promise);
X convert_y_to_x(const Y& y);

std::function<X> func_a(int a) {
  std::promise<X> promise_x;
  std::promise<Y> promise_y;
  std::function<X> future_x = promise_x.get_future();
  std::function<Y> future_y = promise_y.get_future();

  func_b(a, std::move(promise_y));

  // future_yに値が入ったらpromise_xに値をセットする処理???

  return future_x;
}
```

futureを中継するだけのthreadを起動しておけば実現は可能だが、それだけのためにthreadを起動するのはオーバーヘッドが大きすぎる。

```
void relay_future(std::promise<X> promise_x, std::future<Y> future_y) {
  auto y = future_y.get();  // blocking wait
  promise_x.set_value(std::move(y));
}

std::function<X> func_a(int a) {
  // ...

  // ちょっとダサい
  threads_.push_back(std::thread(relay_future, std::move(promise_x), std::move(future_y)));
  return future_x;
}
```

上記のような、futureを返す関数で型変換を伴う処理はどのように書くのがいいのか、というのが問題設定である。

## std::functionに無理やり持たせる

`func_b`の引数を自由に変えられるので、`std::function`でコールバック関数を渡せば簡単に解決すると思われるかもしれない。

```
void func_b(int a, std::function<void(const Y&)> callback);
X convert_y_to_x(const Y& y);

std::function<X> func_a(int a) {
  // ...
  std::promise<X> promise_x;
  std::future<X> future_x = promise_x.get_future();
  func_b(a, [promise_x=std::move(promise_x)](const Y& y) {
    auto x = convert_y_to_x(y);
    promise_x.set_value(std::move(x));
  });
  return future_x;
}
```

「コールすると`y`から`x`に変換して`promise_x`にセットする関数」を引数に渡す方法である。一見するとこれで行けるように見えるが、これではうまく行かない。

```
$ g++ main.cpp
In file included from /usr/include/c++/9/future:48,
                 from func_a.hpp:3,
                 from main.cpp:3:
/usr/include/c++/9/bits/std_function.h: In instantiation of ‘static void std::_Function_base::_Base_manager<_Functor>::_M_clone(std::_Any_data&, const std::_Any_data&, std::false_type) [with _Functor = func_a(int)::<lambda(const Y&)>; std::false_type = std::integral_constant<bool, false>]’:
/usr/include/c++/9/bits/std_function.h:211:16:   required from ‘static bool std::_Function_base::_Base_manager<_Functor>::_M_manager(std::_Any_data&, const std::_Any_data&, std::_Manager_operation) [with _Functor = func_a(int)::<lambda(const Y&)>]’
/usr/include/c++/9/bits/std_function.h:677:19:   required from ‘std::function<_Res(_ArgTypes ...)>::function(_Functor) [with _Functor = func_a(int)::<lambda(const Y&)>; <template-parameter-2-2> = void; <template-parameter-2-3> = void; _Res = void; _ArgTypes = {const Y&}]’
func_a.hpp:22:4:   required from here
/usr/include/c++/9/bits/std_function.h:176:6: error: use of deleted function ‘func_a(int)::<lambda(const Y&)>::<lambda>(const func_a(int)::<lambda(const Y&)>&)’
  176 |      new _Functor(*__source._M_access<const _Functor*>());
      |      ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
In file included from main.cpp:3:
func_a.hpp:19:40: note: ‘func_a(int)::<lambda(const Y&)>::<lambda>(const func_a(int)::<lambda(const Y&)>&)’ is implicitly deleted because the default definition would be ill-formed:
   19 |   func_b(a, [promise=std::move(promise)](const Y& y) mutable {
      |                                        ^
func_a.hpp:19:40: error: use of deleted function ‘std::promise<_Res>::promise(const std::promise<_Res>&) [with _Res = X]’
In file included from func_a.hpp:3,
                 from main.cpp:3:
/usr/include/c++/9/future:1077:7: note: declared here
 1077 |       promise(const promise&) = delete;
      |       ^~~~~~~
 mnt  g  Programming  future_relay 
```

`std::function`にはcopyableなファンクタしか格納できないので、move-onlyな変数をキャプチャしたラムダ式を保持できない。

以下のように、中継専用の関数オブジェクトを使えばゴリ押すことも可能だが、他の箇所で関数オブジェクトを流用できないしいかにもダサい。そもそも、`func_b`が`FutureRelay`に依存しているということは、間接的に`Y`にも依存しているので、問題設定にやや違反してしまっている。

```
class FutureRelay {
public:
  FutureRelay(std::promise<X> promise) : promise_(std::move(promise)) {}
  FutureRelay(FutureRelay&& rhs) : promise_(std::move(rhs.promise_)) {}
  FutureRelay(void) = delete;
  FutureRelay(const FutureRelay&) = delete;
  FutureRelay& operator=(const FutureRelay&) = delete;

  void operator()(const Y& y) {
    auto x = convert_y_to_x(y);
    promise_.set_value(std::move(x));
  }
private:
  std::promise<X> promise_;
};

void func_b(int a, FutureRelay&& relay);
X convert_y_to_x(const Y& y);

std::function<X> func_a(int a) {
  // ...
  std::promise<X> promise_x;
  std::future<X> future_x = promise_x.get_future();
  func_b(a, FutureRelay(std::move(promise_x)));
  return future_x;
}
```

基本的には`std::function`はcopyableなファンクター専用だが、move-onlyなオブジェクトを含むようなファンクターを格納する方法も存在する。

1. `std::shared_ptr`でmove-onlyなオブジェクトを包む
2. copyableなwrapperで包む

これらの方法の詳細については、[\[C++\]std::functionに与える関数はcopy-constructibleでなければならない。 – 賢朽脳瘏](https://kenkyu-note.hatenablog.com/entry/2019/10/06/194822) を参照。また、2については [c++ – Passing a non-copyable closure object to std::function parameter – Stack Overflow](https://stackoverflow.com/questions/20843271/passing-a-non-copyable-closure-object-to-stdfunction-parameter) の回答も詳しい。

ただし、これらの方法はいずれも欠点がある。

まず、1の方法はshared_ptrの参照カウンタの分だけ余計なオーバーヘッドがかかる。shared_ptrは、オブジェクトの領域に加えて参照カウンタを動的にメモリ確保する必要がある。また、参照カウンタ自体の更新コストも余計にかかる。お手軽に試せる方法ではあるが、オーバーヘッドが無視できない。

一方、2の方法は反則に近い方法である。この方法は、作成した`std::function`をmove-onlyでしか使わないという前提で、dummyのcopy constructorを定義する方法である。もし万が一、渡した関数オブジェクトのcopy constructorが呼ばれてしまった場合、例外をthrowする。

これは、`func_b`の実装者に`std::function`をmove-onlyで使うことを暗に強制することになる。また、そのコードが正しく動作するかは実行時に例外が投げられるまで分からない。<span class="easy-footnote-margin-adjust" id="easy-footnote-3-574"></span><span class="easy-footnote">[<sup>3</sup>](https://komorinfo.com/blog/relay-future-function/#easy-footnote-bottom-3-574 "<code>constexpr</code>を駆使してもう一段wrapperを噛ませばコンパイル時にcopy constructorが呼ばれるかどうか検出できる感じはある。ただ、本来の<code>std::function</code>にはない使用制限を<code>func_b</code>に課すことになるので、設計としてよくないことに変わりはないと思う。")</span>

## ObjectPool等に預ける

`std::promise`の所有権をラムダ式に渡さず、他の誰かが持つ。所有権の持ち方は何でもいいが、複数のリクエストが同時に呼ばれる可能性があるので、ObjectPoolを使うのがいいと思う。こうすることで、ラムダ式がcopy assignableになるので`std::function`で扱えるようになる。

ObjectPoolの実装は何でもよいが、一例を示す。

```
#pragma once

#include <queue>

template <typename T>
class ObjectPool {
public:
  template <typename... ArgTypes>
  T* create(ArgTypes&&... args) {
    if (!queue_.empty()) {
      auto ptr = queue_.front();
      queue_.pop();
      new (ptr) T(std::forward<ArgTypes>(args)...);
      return ptr;
    } else {
      return new T(std::forward<ArgTypes>(args)...);
    }
  }

  void destroy(T* ptr) {
    ptr->~T();
    queue_.push(ptr);
  }

private:
  std::queue<T*> queue_;
};
```

ObjectPoolを用いると、以下のような感じでpromiseへの値の受け渡しが行える。

```
void func_b(int a, std::function<void(const Y&)> functor);
X convert_y_to_x(const Y& y);

std::function<X> func_a(int a) {
  // ...
  std::promise<X> promise_x;
  std::future<X> future_x = promise_x.get_future();
  auto* promise_x_ptr = pool_.create(std::move(promise_x));

  func_b(a, [&pool, promise_x_ptr](const Y& y) mutable {
    auto x = convert_y_to_x(y);
    promise_x_ptr->set_value(std::move(x));
    pool_.destroy(promise_x_ptr);
  });
  return future_x;
}
```

ただ、この方法にもいくつか欠点がある。

まず、メモリリークが発生しやすい。promiseの生存期間は`pool.create`から`pool.destroy`の間の区間で、非常に分かりづらい。コールバック関数が呼ばれないかもしれないし、コールバックの実装を間違えてメモリ開放を怠るリスクもある。

また、変換すべき型が増えると、その分だけpoolの個数を増やす必要がある。今回は、func_a-&gt;func_bでX&lt;-Yの場合のみを考えているが、他にも同様の関数を作りたくなった場合、戻り値のfutureの型の数だけpoolを保持しなければならない。

## unique_function(any_invokable)を用いる

上で見てきたようにね「`std::function`がcopyableであること」と「`std::promise`がmove-onlyであること」がぶつかっているので実装が難しくなっているのであった。そのため、`std::function`の代わりにunique_function（any_invokableと呼ばれることもある）を用いることで、この問題をシンプルに解決できる<span class="easy-footnote-margin-adjust" id="easy-footnote-4-574"></span><span class="easy-footnote">[<sup>4</sup>](https://komorinfo.com/blog/relay-future-function/#easy-footnote-bottom-4-574 "一応、copyableな<code>std::promise</code>を作って解決することもできるが、<code>std::promsie</code>は実装がそこそこ難しいのと、パフォーマンスがあまりよろしくなさそうなので見送った。")</span>。

unique_functionについては [move-onlyな関数を扱えるstd::functionのようなものを実装する](https://komorinfo.com/blog/unique-function/) を参照。一言でいうと、`std::function`のmove-only版である。

unique_functionを用いれば、promiseの受け渡しが簡単に行える。また、promiseの所有権が明確で、メモリリークの可能性も小さい。<span class="easy-footnote-margin-adjust" id="easy-footnote-5-574"></span><span class="easy-footnote">[<sup>5</sup>](https://komorinfo.com/blog/relay-future-function/#easy-footnote-bottom-5-574 "加えて、<code>komori::unique_function</code>の実装は短いので、気軽に使いやすいと思う。")</span>

```
void func_b(int a, komori::unique_function<void(const Y&)> functor);
X convert_y_to_x(const Y& y);

std::function<X> func_a(int a) {
  // ...
  std::promise<X> promise_x;
  std::future<X> future_x = promise_x.get_future();

  func_b(a, [promise_x=std::move(promise_x)](const Y& y) mutable {
    auto x = convert_y_to_x(y);
    promise_x.set_value(std::move(x));
  });
  return future_x;
}
```

unique_functionを使えばシンプルにfutureの変換が書けるようになる。

## まとめ

問題の認識から1ヶ月。とても長かった。

`std::function`によるゴリ押しやObjectPoolなど色々な実装を試してみたが、なんとか実用的な解決案が出来上がったと思う。
