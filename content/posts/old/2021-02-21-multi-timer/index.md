---
author: komori-n
categories:
  - 技術解説
date: "2021-02-21T16:11:49+09:00"
tags:
  - C++
keywords:
  - タイマー
  - ライブラリ
  - MultiTimer
  - sleep
  - priority_queeu
  - タスクスケジューラー
title: 1スレッドで複数タイマーを管理する
relpermalink: blog/multi-timer/
url: blog/multi-timer/
description: C++において、1つのスレッド複数のタイマーを同時に管理する方法について説明する。
---

よく困るので汎用的に使えそうなタイマーライブラリを作った。

## モチベ

一定時間経過後にコールバックで教えてほしいことがある。タイマーが1個であれば、以下のようにタイマー用のスレッドを立ててsleepさせれば実現できる。

```cpp
// 5秒後にfnをコールしてもらう
void Timer::call_after_5s(std::function<void(void)> fn) {
    this->thread_ = std::thread([fn](void) {
        std::this_thread::sleep_for(5s);
        fn();
    });
}
```

ただ、タイマーの数が多くなると、スレッドの生成・破棄のコストが無視できない。そのため、スレッド数をケチって複数コールバックを実現するライブラリを作った。

ソースコードは以下のリポジトリで入手できる。

{{< github repo="komori-n/multi-timer" >}}

## 使い方

`komori::MultiTimer<Task>`のtemplate parameterには、lambda式や`std::function`、`komori::unique_function`などのoperator()で呼べるような型を代入する。中身の型は何でも良いが、用途を考えると`komori::onetime_function<void(void)>`を入れるのがおすすめである。

```cpp
  komori::MultiTimer<komori::onetime_function<void(void)>> timer;
  timer.start_processing();

  timer.set([]{ std::cout << "3s" << std::endl; }, 3s);
  timer.set([]{ std::cout << "6s" << std::endl; }, 6s);

  timer.set([&]{
    std::cout << "2s" << std::endl;
    timer.set([&]{
      std::cout << "2s+2s" << std::endl;
      timer.set([&]{
        std::cout << "2s+2s+2s" << std::endl;
      }, 2s);
    }, 2s);
  }, 2s);
```

上記のプログラムを実行すると、出力結果は以下のようになる。

```text
2s
3s
2s+2s
6s
2s+2s+2s
```

タイマーで指定した秒数が経過した時点で正しくコールバックが行われていることが確認できる。

## 実装解説

`std::priority_queue`で直近のコールバックまでsleepする。スケジュールの管理には以下の構造体を用いる。

```cpp
using time_point = std::chrono::system_clock::time_point;

template <typename Task>
struct TaskSchedule {
  // add mutable to move with priority_queue.top()
  mutable Task task;
  time_point tp;
};

template <typename Task>
struct ScheduleCompare {
  bool operator()(const TaskSchedule<Task>& x, const TaskSchedule<Task>& y) const {
    return x.tp > y.tp;
  }
};
```

`TaskSchedule`同士は`ScheduleCompare`により比較される。priority_queueで最も締め切りが近い要素をtopへ来るように`ScheduleCompare::operator()`を定義している。

`TaskSchedule::task`に`mutable`が付与されているのは、queueの先頭からmoveで取り出すためである。

```cpp
auto task = std::move(task_queue_.top().task);
task_queue_.pop();
```

`std::priority_queue::top()`の戻り値はconst参照である。もしこれが書き換え可能な参照を返却する場合、queueのtopが優先度最大でなくなる可能性があるためなので仕方がない。しかし、今回のケースではtaskはqueueの優先度には関係ないので、mutableを付与して中身を書き換えても問題にならない[^1]。

[^1]: 「top()の直後にpop()するならconst_castでconstを外せばいい」という主張もある。（<https://stackoverflow.com/questions/20149471/move-out-element-of-std-priority-queue-in-c11>）しかし、const_castでconst外しをするのはあまりに行儀が悪いと思う。"
