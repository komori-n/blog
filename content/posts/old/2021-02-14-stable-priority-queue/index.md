---
author: komori-n
categories:
  - 技術解説
canonical: https://komorinfo.com/blog/post-979/
aliases:
  - /blog/post-979/
date: "2021-02-14T22:44:15+09:00"
tags:
  - C++
  - STL
keywords:
  - C++14
  - priority_queue
  - 安定
  - stable_priority_queue
  - multiset
title: 安定な優先順位付きキュー（stable_priority_queue）を作る
relpermalink: blog/stable-priority-queue/
url: blog/stable-priority-queue/
description: C++で安定な優先順位つきキュー（stable_priority_queue）を作る
---

{{< github repo="komori-n/stable_priority_queue" >}}

## モチベ

安定な`std::priority_queue`が欲しい。

`std::priority_queue`は大きい値から順番に値を取り出せるデータ構造である。内部実装ではヒープを用いることが想定されている。そのため、値の挿入順序は保持されず、同値（同じ優先度）の要素のpop順は不定である。

例えば、以下のコードを考える。

```cpp
#include <queue>
#include <cstdlib>
#include <iostream>

struct Entry {
  int val;
  int order;

  bool operator<(const Entry& entry) const noexcept {
    return this->val < entry.val;
  }

  void print(void) const {
    std::cout << val << " " << order << std::endl;
  }
};


int main(void) {
  std::priority_queue<Entry> queue;

  queue.push(Entry { 3, 0 });
  queue.push(Entry { 2, 1 });
  queue.push(Entry { 4, 2 });
  queue.push(Entry { 3, 3 });
  queue.push(Entry { 2, 4 });

  for (int i = 0; i < 3; ++i) {
    auto top = queue.top();
    queue.pop();

    top.print();
  }

  queue.push(Entry { 4, 5 });
  queue.push(Entry { 2, 6 });
  queue.push(Entry { 3, 7 });

  while (!queue.empty()) {
    auto top = queue.top();
    queue.pop();

    top.print();
  }

  return EXIT_SUCCESS;
}
```

上記のコードは`std::priority_queue`へ3, 2, 4, 3, 2を挿入し、3つ値を取り出した後に4, 2, 3を追加で挿入するサンプルである。安定性を分かりやすくするために、何番目に挿入した要素かを`Entry`のメンバへ加えている（優先度には影響しない）。

このサンプルコードを実行すると、以下のような出力が得られる。出力の1個目の値が優先度、2個目の値が何番目に挿入したかを表す数である。

```sh
$ ./priority_queue.out
4 2
3 0
3 3
4 5
3 7
2 1
2 6
2 4
```

最後の優先度2の出力順序が挿入順序に合っていない。挿入順序はEntry{2, 4} -&gt; Entry{2, 6}の順だが、取り出し順序は逆になっている。

このように、`std::priority_queue`は同値な要素の挿入順序とは関係なく値が取り出される。

格納したい構造体に「何番目に挿入したか」のメンバを追加して、これを加味して優先度を定義すれば安定なpriority_queueを実現できる。しかし、ダサい上にカウンタのオーバーフローのことも考えなくてはいけないので面倒くさい。

```cpp
// 「ダサい」実装の例
// キューに格納する要素に連番を振る
template <typename Key>
struct Elem {
  Key key;
  unsigned order;

  Elem(const Key& key)
      : key(key), order(s_order++) {}

  bool operator<(const Elem& elem) const {
    if key < elem.key {
      return true;
    }
    // orderが小さい方の優先度を大きくしたいのでoperatorの向きに注意
    return order > elem.order;
  }

private:
  static unsigned s_order = 0;
};
```

そこで、同値な値は到着順に値が出てくる安定なpriority_queueを自作した。作成した`komori::stable_priority_queue`のコードは以下のリポジトリで確認できる。

{{< github repo="komori-n/stable_priority_queue" >}}

## stable_priority_queue の作り方

以下のように、Keyの型に応じて実装の切り替えを行っている。要素がcopyableでないときは`std::multiset<Key>`を、copyableのときは`std::map<Key, std::queue<Key>>`を用いる[^1]。

[^1]: c++11以降では`std::multiset`に格納された同値な要素は、挿入順に並べられることが保証されている。

```cpp
  template <typename Key,
      typename Compare = std::less<Key>>
  using stable_priority_queue = typename std::conditional<
    std::is_copy_constructible<Key>::value &&
      std::is_copy_assignable<Key>::value,
    copyable_queue<Key, Compare>,                // std::map<Key, std::queue<Key>>実装
    noncopyable_queue<Key, Compare>>::type;      // std::multiset<Key>実装
```

mapを用いる方の実装は、要素をkeyとvalueの2箇所で保つ必要があるので、Keyがcopyableでなければ使えない。一方で、`std::multiset`を用いる方法はcopyableかどうかに依らず使える。そのため、copyableかどうかに関係なく`std::multiset`の方の実装を用いる方法も考えられる。しかし、要素の重複個数が多くなった際に`std::map<Key, std::queue<Key>>`の方が木の高さが低く抑えられ、木の更新コストが小さく済むことが実装中に判明したので、上記のデータ構造を採用している。

基本的には素直に実装するだけだが、std::multimapで降順に要素を並べるために、渡されたCompareの順序を反転させる`reverse_compare`を挟んでいる[^2]。

[^2]: `std::map`を用いる方は必ずしも逆順で格納する必要はないが、先頭要素を取ってくる処理が短く書けるので`reverse_compare`でソートしている。

## 速度比較

`std::priority_queue`と`komori::stable_priority_queue`の速度比較を行った。計測条件は以下の通りである[^3]。

[^3]: g++ 9.3.0、Ubuntu 20.04（WSL 2）、Intel(R) Core(TM) i5-8400 CPU"

- Entry：72 bytes（priorityは4 bytes）
- 要素数： 100000
- 計測区間：全要素のpush+全要素のpopにかかった時間

速度比較に用いたコードは [https://github.com/komori-n/stable_priority_queue](https://github.com/komori-n/stable_priority_queue) のexamples以下を参照。

### 要素がnoncopyableの場合

それぞれ、経過時間は以下のようになった。

| 方法                          | 時間   |
| ----------------------------- | ------ |
| std::priority_queue           | 403 ms |
| komori::stable_priority_queue | 757 ms |

`komori::stable_priority_queue`は`std::priority_queue`の1/2倍程度の速度で動作した。`std::priority_queue`に安定性が加わっていることを考えると、まずまずのパフォーマンスだと考えられる。

### 要素がcopyableの場合

それぞれ、経過時間は以下のようになった。

| 方法                          | 時間   |
| ----------------------------- | ------ |
| std::priority_queue           | 346 ms |
| komori::stable_priority_queue | 110 ms |
| komori::noncopyable_queue     | 572 ms |

`komori::stable_priority_queue`は`std::priority_queue`の4倍程度高速に動作している[^4]。また、実装を切り替えることによりnoncopyable_queue（`std::multimap`を用いた実装）よりも高速に動作していることが読み取れる

[^4]: `std::priority_queue`はヒープ内の要素の移動が必要なので、格納するクラスのサイズが大きいほど挿入、削除に時間がかかるようになる。
