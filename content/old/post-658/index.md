---
author: komori-n
draft: true
categories:
  - プログラミング
date: "2020-12-09T20:34:12+09:00"
guid: https://komorinfo.com/blog/?p=658
id: 658
image: https://komorinfo.com/wp-content/uploads/2020/09/cpp.png
og_img:
  - https://komorinfo.com/wp-content/uploads/2020/09/cpp.png
permalink: /post-658/
tags:
  - C/C++
title: std::recursive_mutexを使う
url: post-658/
---

知らなかったのでメモ。

以下のように、コールバック関数を登録したり呼び出したりできるクラス `Hoge` を考える。

```
#include <iostream>
#include <cstdlib>
#include <functional>

class Hoge {
public:
  template <typename F>
  void set(F&& f) {
    callback_ = std::forward<F>(f);
  }

  void clear(void) {
    callback_ = nullptr;
  }

  void invoke(void) {
    if (callback_) {
      callback_();
    }
  }

private:
  std::function<void(void)> callback_;
};

int main(int argc, char*argv[]) {
  Hoge hoge;

  hoge.set([](void) { std::cout << "hello from callback" << std::endl; });
  hoge.invoke();
  // => hello from callback
  hoge.clear();
  hoge.invoke();
  // => (none)

  return EXIT_SUCCESS;
}
```

`Hoge::set()`で呼んで欲しい関数を登録し、 `Hoge::invoke()`で登録された関数があれば呼び出すことができる。関数が登録されていなければ、何も行わない。また、 `Hoge::clear()`により関数の登録を解除することもできる。

このクラス `Hoge` をmultithreadに対応させたい。すなわち、複数スレッドが同時に `set()` や `invoke()` を呼んでもうまく排他できるようにしたい。

シンプルに考えると、以下のように `std::mutex` でlockをとればいい気がする。

```
class Hoge {
public:
  template <typename F>
  void set(F&& f) {
    std::lock_guard<std::mutex> lock(mutex_);
    callback_ = std::forward<F>(f);
  }

  void clear(void) {
    std::lock_guard<std::mutex> lock(mutex_);
    callback_ = nullptr;
  }

  void invoke(void) {
    std::lock_guard<std::mutex> lock(mutex_);
    if (callback_) {
      callback_();
    }
  }

private:
  std::mutex mutex_;
  std::function<void(void)> callback_;
};
```

しかし、 `std::mutex` を使うこの方法は一つ欠点がある。それは、`Hoge::invoke()`のコールバック中に `Hoge::clear()`を呼び出すとデッドロックになってしまうことである<span class="easy-footnote-margin-adjust" id="easy-footnote-1-658"></span><span class="easy-footnote">[<sup>1</sup>](https://komorinfo.com/blog/post-658/#easy-footnote-bottom-1-658 "厳密には、同じスレッドから同じmutexをロックしようとしたときの動作はundefined。手元の環境では、<code>-lpthread</code>をつけてビルドしたらデッドロックになったが、つけずにビルドしたら普通に実行できた。")</span>。

```
  Hoge hoge;

  hoge.set([&](void) {
    std::cout << "hello from callback" << std::endl;
    hoge.clear();  // dead lock!!
  });
  hoge.invoke();
```

これを避けるためには、`Hoge::invoke()`経由で呼ばれたかどうかをクラス内部で覚えておく必要があると思っていた。

これは、C++標準ライブラリに入っている`std::recursive_mutex`を使えば解決できる。`std::recursive_mutex`は（名前の通り）再帰関数用の排他変数で、同じスレッドから複数回 `lock()`がくると内部のカウンタをインクリメントし、`unlock()`がくるとデクリメントする。そして、`unlock()`後に内部カウンタが0になった場合のみロックを解除するという動作になっている。

```
#include <iostream>
#include <cstdlib>
#include <mutex>
#include <functional>
#include <thread>

class Hoge {
public:
  template <typename F>
  void set(F&& f) {
    std::lock_guard<std::recursive_mutex> lock(mutex_);
    callback_ = std::forward<F>(f);
  }

  void clear(void) {
    std::lock_guard<std::recursive_mutex> lock(mutex_);
    callback_ = nullptr;
  }

  void invoke(void) {
    std::lock_guard<std::recursive_mutex> lock(mutex_);
    if (callback_) {
      callback_();
    }
  }

private:
  std::recursive_mutex mutex_;
  std::function<void(void)> callback_;
};

int main(int argc, char*argv[]) {
  Hoge hoge;

  hoge.set([&](void) {
    std::cout << "hello from callback" << std::endl;
    hoge.clear();  // dead lockせずちゃんと clear できる
  });
  hoge.invoke();
  // => hello from callback

  hoge.invoke();
  // => (none)

  return EXIT_SUCCESS;
}
```

`std::recursive_mutex`を用いれば、所望の通りcallback内で`clear()`を呼んでもdead lockが起こらなくなった。

C++にはまだまだ知らない機能がいっぱいあって怖い。
