---
author: komori-n
draft: true
categories:
  - プログラミング
date: "2022-04-30T15:45:55+09:00"
guid: https://komorinfo.com/blog/?p=1619
id: 1619
permalink: /sfinae-constraints/
tags:
  - C/C++
title: SFINAEの制約式を少しだけ読みやすくするConstraints
url: sfinae-constraints/
---

最近知ったSFINAEを少しだけ読みやすくするおまじないの紹介。

C++17 で SFINAE を使って関数を定義したりしなかったりしたいとき、`std::enable_if` と `std::nullptr` を組み合わせて以下のようなコードを書くことがしばしばある<span class="easy-footnote-margin-adjust" id="easy-footnote-1-1619"></span><span class="easy-footnote">[<sup>1</sup>](https://komorinfo.com/blog/sfinae-constraints/#easy-footnote-bottom-1-1619 "なぜ <code>std::nullptr_t</code> を使うかは<a href="https://secret-garden.hatenablog.com/entry/2016/12/22/032008">【C++ Advent Calendar 2016 22日目】C++ で enable_if を使うコードのベストプラクティス &#8211; Secret Garden(Instrumental)</a>、<a href="https://qiita.com/kazatsuyu/items/203584ef4cb8b9e52462">std::enable_ifを使ってオーバーロードする時、enablerを使う？ &#8211; Qiita</a> を参照")</span>。

```
template <typename T,
          std::enable_if_t</* SFINAE特有の式 */, std::nullptr_t> = nullptr>
void func(T&& t) {
    /* ... */
}
```

SFINAE に馴染みのない人にとってはかなり読みづらい。やりたいことは型 `T` に応じて関数の定義を切り替えることだが、関係ない `std::nullptr_t` や `nullptr` が並ぶことで少し読みづらく感じることがある。また、SFINAE の条件が増えれば増えるほど `std::enabler_if_t` の template 引数が長くなり、可読性が低下しやすい。

このようなとき、次のような `Constraints` を導入することでほんの少しだけ読みやすくなる。

```
namespace detail {
template <typename... Args>
struct ConstraintsImpl {
  using Type = std::nullptr_t;
};
}  // namespace detail

template <typename... Args>
using Constraints = typename detail::ConstraintsImpl<Args...>::Type;


// Constraints を用いた定義方法
template <typename T,
          Constraints<std::enable_if_t</* SFINAE特有の条件1 */>,
                      std::enable_if_t</* SFINAE特有の条件2 */>,
                      /* SFINAE特有の条件式... */> = nullptr>
void func(T&& t) {
    /* ... */
}
```

`Constraints` の中身は単純で、テンプレート引数を無視して常に `std::nullptr_t` を返している。こうすることで、`std::nullptr_t` を隠蔽し、少しだけ読みやすくできる<span class="easy-footnote-margin-adjust" id="easy-footnote-2-1619"></span><span class="easy-footnote">[<sup>2</sup>](https://komorinfo.com/blog/sfinae-constraints/#easy-footnote-bottom-2-1619 "本音を言うと <code>nullptr</code> も隠蔽したいが、こればかりはどうしようもない")</span>。また、`std::enable_if` を複数個並べられるため、条件が AND であることがわかりやすくなる。

```
// 使用例
template <typename T,
          Constraints<std::enable_if_t<std::is_default_constructible_v<T>>,
                      std::enable_if_t<std::is_nothrow_assignable_v<T>>> = nullptr>
void func(T&& t) noexcept {
    std::cout << "T is default constructible and nothrow assignable" << std::endl;
}
```

ぱっと見ではそれほど見た目が変わらないように見えるかもしれない。しかし、実際に使ってみると想像以上に SFINAE コードが読みやすくなるため、今後は enabler や ALWAYS_TRUE ではなく `Constraints` パターンを採用していきたい。
