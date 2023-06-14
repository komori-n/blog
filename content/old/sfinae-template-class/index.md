---
author: komori-n
draft: true
categories:
  - プログラミング
date: "2020-11-04T20:28:02+09:00"
guid: https://komorinfo.com/blog/?p=589
id: 589
image: https://komorinfo.com/wp-content/uploads/2020/09/cpp.png
og_img:
  - https://komorinfo.com/wp-content/uploads/2020/09/cpp.png
permalink: /sfinae-template-class/
tags:
  - C/C++
title: SFINAEでtemplate classのメンバ関数の実体化を制御する
url: sfinae-template-class/
---

## 問題設定

SFINAE<span class="easy-footnote-margin-adjust" id="easy-footnote-1-589"></span><span class="easy-footnote">[<sup>1</sup>](https://komorinfo.com/blog/sfinae-template-class/#easy-footnote-bottom-1-589 "SFINAE(Substitution Failure Is Not An Error)は、C++の黒魔術の一つ。template実体化時にうまく代入できなかった場合、コンパイルエラーとはならず単に無視してくれる機能である。")</span>を用いて、template classのメンバ関数を実体化したりしなかったりしたい。例えば、typenameが`void`の時は実体化する関数を抑制したり、typenameに応じて関数を呼び分けてほしい場合が考えられる。

普通のSFINAEの感覚だと以下のように書いてみたくなるが、これだとコンパイルエラーになる。

```
template <typename T>
struct Hoge {
  // void用の関数
  auto func(void)
  -> std::enable_if_t<std::is_same<T, void>::value, void> {
    std::cout << "void" << std::endl;
  }

  // 非void用の関数
  auto func(void)
  -> std::enable_if_t<!std::is_same<T, void>::value, void> {
    std::cout << "not void" << std::endl;
  }
};
```

SFINAEはtemplateのsubstitution failureを無視してくれる機能なので、template classであっても非templateメンバ関数の実体化に失敗すると普通にエラーになる。

SFINAEはtemplateに関する機能なので、メンバ関数をtemplateメンバ関数化して回避しなければならない。回避の仕方は大きく分けて3通り。後に紹介する方法ほどおすすめの方法である。

本ページのサンプルコードは以下の場所にある。
**[member-sfinae-1.cpp](https://gist.github.com/komori-n/086c8d369fbfde0f06e947696c6d11ca)**

## 方法1｜Dummyのtemplateを使う

よく目にするのはこの形式である。`U`という変数（デフォルト値は`T`）を導入してsubstitution failureの形にする。

```
template <typename T>
struct Hoge {
  template <typename U=T>
  auto func(void)
  -> std::enable_if_t<std::is_same<U, void>::value, void> {
    std::cout << "void" << std::endl;
  }

  template <typename U=T>
  auto func(void)
  -> std::enable_if_t<!std::is_same<U, void>::value, void> {
    std::cout << "not void" << std::endl;
  }
};
```

`std::is_same<U, void>::value`は`U`によって値が変わる。したがって、メンバ関数`func`の戻り値も`U`の値が決まるまで分からないので、SFINAEの対象になる。

この方法のメリットは可読性が高いこと。SFINAE特有の読みにくさはあるが、ぱっと見て分かりやすいコードになる。

一方で、この方法のデメリットは、利用者が誤用する余地が残ることである。

```
int main(int argc, char* argv[]) {
  Hoge<int> hoge;
  hoge.func<void>();  // void用の関数が呼ばれてしまう

  return 0;
}
```

`U`のデフォルト値が`T`だが、呼び出し側はこのtemplate parameterを自由に設定することもできる。そのため、上記のように設計者が意図しない関数が呼ばれる可能性がある<span class="easy-footnote-margin-adjust" id="easy-footnote-2-589"></span><span class="easy-footnote">[<sup>2</sup>](https://komorinfo.com/blog/sfinae-template-class/#easy-footnote-bottom-2-589 "以下のようにすれば回避できるが、これをするぐらいなら後述する<code>bool</code>や<code>nullptr</code>を用いる方法の方が可読性に優れると思う。</p>

template &lt;typename T>
struct Hoge {
template &lt;typename U = T>
auto func(void)
-> std::enable_if_t&lt;std::is_same&lt;U, void>::value &amp;&amp; std::is_same&lt;U, T>::value, void> {
std::cout &lt;&lt; "void" &lt;&lt; std::endl;
}

template &lt;typename U = T>
auto func(void)
-> std::enable_if_t&lt;!std::is_same&lt;U, void>::value &amp;&amp; std::is_same&lt;U, T>::value, void> {
std::cout &lt;&lt; "not void" &lt;&lt; std::endl;
}
};</pre>

<p>")</span>。

## 方法2｜dummyのbool変数を持たせる

SFINAEで実体化抑制させるだけなら、template変数はtypenameでなくてもよい。例えば、必ず`true`になるbool変数を用いる方法が考えられる。

```
template <typename T>
struct Hoge {
  template <bool AlwaysTrue = true>
  auto func(void)
  -> std::enable_if_t<std::is_same<U, void>::value && AlwaysTrue, void> {
    std::cout << "void" << std::endl;
  }

  template <bool AlwaysTrue = true>
  auto func(void)
  -> std::enable_if_t<!std::is_same<U, void>::value && AlwaysTrue, void> {
    std::cout << "not void" << std::endl;
  }
};
```

`std::is_same::value && AlwaysTrue`は`AlwaysTrue`の値が決まるまで戻り値の型が決まらないので、SFINAEによる実体化抑制ができる。

方法1と比較すると、bool変数を用いる方法は誤用される心配はない。もし`AlwaysTrue`に`false`がセットされた場合、実体化に失敗して呼び出せなくなるためである。

```
int main(int argc, char* argv[]) {
  Hoge<int> hoge;
  hoge.func<false>();  // Error! 呼び出し候補の関数がない

  return 0;
}
```

ただし、実体化できないとはいえ、template関数に`false`を代入できるように見えるのは少し気持ち悪い。もう少しスマートに解決したい。

## 方法3｜template parameterにnullptr_tを用いる

c++14から、template parameterに`std::nullptr_t`が使えるようになった<span class="easy-footnote-margin-adjust" id="easy-footnote-3-589"></span><span class="easy-footnote">[<sup>3</sup>](https://komorinfo.com/blog/sfinae-template-class/#easy-footnote-bottom-3-589 "参考：https://cpprefjp.github.io/lang/cpp14/nontype_template_parameters_of_type_nullptr_t.html")</span>。`std::nullptr_t`は`nullptr`の一値しか取れない型だが、template parameterとして立派に機能する。

```
template <typename T>
struct Hoge {
  template <std::nullptr_t Dummy = nullptr>
  auto func(void)
  -> std::enable_if_t<std::is_same<T, void>::value && Dummy == nullptr, void> {
    std::cout << "void" << std::endl;
  }

  template <std::nullptr_t Dummy = nullptr>
  auto func(void)
  -> std::enable_if_t<!std::is_same<T, void>::value && Dummy == nullptr, void> {
    std::cout << "not void" << std::endl;
  }
};
```

理屈はbool変数を用いる方法と同様。`std::nullptr_t`は一値しかとらないとはいえ、`std::is_same<T, void>::value && Dummy == nullptr`は`Dummy`の値が決まるまで分からないので、SFINAEにより実体化抑制に使える。

`std::nullptr_t`を用いることでtemplate parameterの自由度を下げることができ、利用者に余計な心配をさせなくて済む。
