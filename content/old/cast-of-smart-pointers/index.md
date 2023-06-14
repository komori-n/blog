---
author: komori-n
draft: true
categories:
  - プログラミング
date: "2021-03-15T21:22:02+09:00"
guid: https://komorinfo.com/blog/?p=1065
id: 1065
image: https://komorinfo.com/wp-content/uploads/2020/09/cpp.png
og_img:
  - https://komorinfo.com/wp-content/uploads/2020/09/cpp.png
permalink: /cast-of-smart-pointers/
tags:
  - C/C++
title: スマートポインタをdynamic_castしたい
url: cast-of-smart-pointers/
---

スマートポインタ （std::unique_ptrやstd::shared_ptr）を dynamic_cast する方法を意外と忘れやすいのでメモ。

## 背景

クラス `Derived` が `Base` を継承している状況を考える。

```
class Base {
public:
    virtual int foo(int x) { return x; }
};

class Derived {
public:
    virtual int foo(int x) override { return 2 * x; }
};
```

次のようなポインタ変換を行いたい。

- `std::shared_ptr<Derived>` -&gt; `std::shared_ptr<Base>`
- `std::unique_ptr<Derived>` -&gt; `std::unique_ptr<Base>`

## shared_ptr の dynamic_cast

shread_ptrの場合、ズバリ `std::dynamic_pointer_cast` という関数が使える<span class="easy-footnote-margin-adjust" id="easy-footnote-1-1065"></span><span class="easy-footnote">[<sup>1</sup>](https://komorinfo.com/blog/cast-of-smart-pointers/#easy-footnote-bottom-1-1065 "詳しい解説は <a href="https://cpprefjp.github.io/reference/memory/shared_ptr/dynamic_pointer_cast.html">dynamic_pointer_cast &#8211; cpprefjp C++日本語リファレンス</a> を参照")</span>。

```
std::shared_ptr<Derived> derived = std::make_shared<Derived>();
std::shared_ptr<Base> base = std::dynamic_pointer_cast<Base>(derived);
```

この関数は参照カウンタを保ったままポインタの変換を行ってくれる。変換前、変換後の shared_ptr は同じ参照カウンタを共有しており、両方から参照されなくなったタイミンングで自動的にメモリが開放される。

```
int main(void) {
    std::shared_ptr<Derived> derived = std::make_shared<Derived>();
    {
        std::shared_ptr<Base> base = std::dynamic_pointer_cast<Base>(derived);
        // 2
        std::cout << derived.use_count() << std::endl;
    }
    // 1
    std::cout << derived.use_count() << std::endl;
    return 0;

    // derived のメモリが開放される
}
```

なお、dynamic_castに失敗したときは参照カウンタは増加せず、空の shared_ptr が返る。

```
int main(void) {
    std::shared_ptr<Base> base= std::make_shared<Base>();
    {
        // (Derived*)base の変換に失敗するので、derivedの中身は空になる
        std::shared_ptr<Derived> derived = std::dynamic_pointer_cast<Derived>(base);

        // 1  <- 変換に失敗したのでカウンタは増えない
        std::cout << base.use_count() << std::endl;
    }
    // 1
    std::cout << base.use_count() << std::endl;
    return 0;

    // derived のメモリが開放される
}
```

似たような関数として、 `std::static_pointer_cast` や `std::reinterpret_pointer_cast` も用意されている。

## unique_ptr の dynamic_cast

unique_ptrに対しては `std::dynamic_pointer_cast` のような便利関数は存在しない。しかし、以下のようにして簡単に変換関数を自作することができる。

```
template <typename U, typename T>
std::unique_ptr<U> dynamic_unique_cast(std::unique_ptr<T>&& ptr) {
    return std::unique_ptr<U>(dynamic_cast<U*>(ptr.release()));
}
```

`release()` で元のスマートポインタから生ポインタを剥ぎ取り、変換してから `std::unique_ptr` へ詰め直している。custom deleterを使いたい場合は、お好みで書き換えればよい。
