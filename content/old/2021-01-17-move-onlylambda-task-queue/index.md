---
author: komori-n
draft: true
categories:
  - プログラミング
date: "2021-01-17T11:09:43+09:00"
guid: https://komorinfo.com/blog/?p=860
id: 860
image: https://komorinfo.com/wp-content/uploads/2020/09/cpp.png
og_img:
  - https://komorinfo.com/wp-content/uploads/2020/09/cpp.png
permalink: /move-onlylambda-task-queue/
tags:
  - C/C++
title: move-onlyなlambda式のTaskQueueを作る
url: move-onlylambda-task-queue/
---

## モチベ

move-onlyなTaskをqueueに格納したい。 `std::queue<std::function<void(void)>>` で良ければ話は早いが、これではmove-onlyなファンクターをqueueに格納できない<span class="easy-footnote-margin-adjust" id="easy-footnote-1-860"></span><span class="easy-footnote">[<sup>1</sup>](https://komorinfo.com/blog/move-onlylambda-task-queue/#easy-footnote-bottom-1-860 "<code>std::function</code> にmove-onlyファンクターを格納できない件については、過去記事を参照。</p>

<ul><li><a href="https://komorinfo.com/blog/unique-function/">move-onlyな関数を扱えるstd::functionのようなものを実装する</a></li><li><a href="https://komorinfo.com/blog/post-593/">一度きりしか呼べないファンクターを管理したい</a></li><li><a href="https://komorinfo.com/blog/relay-future-function/" data-type="URL" data-id="https://komorinfo.com/blog/relay-future-function/">std::functionやunique_functionを用いて、std::futureを中継する</a></li></ul>

<p>")</span>。

`std::function` の代わりに [move-onlyな関数を扱えるstd::functionのようなものを実装する](https://komorinfo.com/blog/unique-function/) で作った `komori::unique_function` を使って実現することもできる。しかし、queueに積むという目的を達するだけならもっと簡単にできる方法があるのでそれを紹介する。

## 方法

仮想 `operator()` を持つ抽象クラスを作り、いい感じのtemplate classで継承させる。

言葉で説明するのが難しいので、とりあえずコードを示す。

```
#pragma once
// task.hpp

#include <functional>
#include <utility>
#include <memory>

namespace komori {
class TaskBase {
public:
  virtual void operator()(void) = 0;
};

template <typename Func>
class Task : public TaskBase {
public:
  static_assert(!std::is_reference<Func>::value,
    "Func must not be a reference type");

  Task(Func&& fn)
    : fn_(std::forward<Func>(fn)) {}

  virtual void operator()(void) override {
    fn_();
  }

private:
  Func fn_;
};

template <typename Func>
std::unique_ptr<TaskBase> createTask(Func&& func) {
  return std::unique_ptr<TaskBase>(
    new Task<Func>(std::forward<Func>(func))
  );
}

}  // namespace komori
```

与えられたlambda式を `TaskBase` クラスを継承した `Task<(#lambda)>` クラスに包むのがポイントである。

createTask関数を作成しているのは、template classはtemplate typeを自動推論できないためである。lambda式を表す無名クラスをtemplate parameterとして直接指定するのは難しいため、createTask関数を経由して `LambdaTask<(#lambda)>` のインスタンスを生成している。

lambda式の代わりにstd::functionや関数オブジェクト等を使いたい場合もこのクラスを流用できる<span class="easy-footnote-margin-adjust" id="easy-footnote-2-860"></span><span class="easy-footnote">[<sup>2</sup>](https://komorinfo.com/blog/move-onlylambda-task-queue/#easy-footnote-bottom-2-860 "Funcが <code>operator()(void)</code> を実装していればlambda、std::function、関数オブジェクト等の違いを意識することなく使用できる")</span>。

このクラスを用いると、以下のようにTaskQueueを実現できる。

```
#include <cstdlib>
#include <iostream>
#include <queue>
#include <future>

#include "task.hpp"

int main(int argc, char* argv[]) {
  using TaskPtr = std::unique_ptr<komori::TaskBase>;
  std::queue<TaskPtr> task_queue;  // TaskQueue

  std::promise<int> promise;
  auto future = promise.get_future();

  {  /* push task */
    auto task = komori::createTask(
      [promise=std::move(promise)](void) mutable {
        std::cout << "set value" << std::endl;
        promise.set_value(334);
      }
    );

    std::cout << "push task" << std::endl;
    task_queue.push(std::move(task));
  }

  {  /* pop and invoke task */
    auto task = std::move(task_queue.front());
    task_queue.pop();

    std::cout << "task invoke" << std::endl;
    (*task)();
  }

  std::cout << "future: " << future.get() << std::endl;

  return EXIT_SUCCESS;
}
```

16-24行目付近でmove-onlyなタスクををqueueに積んでいる。ここで積むタスクは `std::promise` をキャプチャしているため、copy-assignableではない<span class="easy-footnote-margin-adjust" id="easy-footnote-3-860"></span><span class="easy-footnote">[<sup>3</sup>](https://komorinfo.com/blog/move-onlylambda-task-queue/#easy-footnote-bottom-3-860 "lambda式の初期化キャプチャはC++14以降で利用できる（<a rel="noreferrer noopener" href="https://cpprefjp.github.io/lang/cpp14/initialize_capture.html" target="_blank">https://cpprefjp.github.io/lang/cpp14/initialize_capture.html</a>）")</span>。

上記のサンプルコードでは、queueにタスクを1つだけ積み、すぐに取り出して実行をしている。実行結果は以下のようになる。

```
$ g++ src/main.cpp -lpthread
$ ./a.out
push task
task invoke
set value
future: 334
```

queueにpromiseへの値のセットするタスクを入れて、queueから取り出して正しく実行することができている。

（2021/02/15追記）<https://github.com/komori-n/unique-function> にて公開。
