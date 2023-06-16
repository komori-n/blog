---
author: komori-n
draft: true
categories:
  - explanation
date: "2020-10-11T20:38:50+09:00"
tags:
  - C/C++
  - STL
title: libstdc++のstd::functionの実装を眺める
relpermalink: blog/libstd-function-impl/
url: blog/libstd-function-impl/
description: libstdc++のstd::functionの実装を大まかに解説する
---

## 概要

`std::function`は、C++で関数ポインタやラムダ式など色んな物を代入できるクラスである。最近、個人的に`std::function`と戯れる機会が増えていて、内部の実装がどうなっているのか気になったので調べてみた。

以下で述べることはほとんど環境、実装依存なので注意。すべてのコンパイラ、すべてのアーキテクチャで当てはまるわけではない。

## 環境

- Intel Core i5-8400
- Windows 10 Education 2004
- Ubuntu 20.04 LTS(WSL2)
- gcc 9.3.0
- libstdc++ 10.2.0

libstd++は、C++ STLのGNU実装である。コードは以下のページを参照した。
[https://github.com/gcc-mirror/gcc/blob/master/libstdc%2B%2B-v3/include/bits/std_function.h](https://github.com/gcc-mirror/gcc/blob/master/libstdc%2B%2B-v3/include/bits/std_function.h)（rev abed8b5）

また、検証のために作成したコードは以下を参照。

<https://gist.github.com/komori-n/c8b8a4e0b1eaf7ad1623b63e50d94561>

## 結論

- 関数ポインタ、メンバ関数ポインタは静的にメモリ確保される
- 次の条件を満たす関数オブジェクト、ラムダ式は動的にメモリ確保される
  - サイズが16バイトより大きい
  - 16バイトでアラインしたら問題がある
  - trivial_copyableではない
- `std::function`のサイズは32バイトで、内約は以下のようになっている
  - （メンバ）関数ポインタ、インスタンス等の関数本体を保存する：16バイト
  - 内部のstaticメンバ関数を参照する：8バイト x 2

## std::functionとは

`std::function`には次のものを格納することができる。

- 関数ポインタ
- メンバ関数ポインタ
- ラムダ式
- 関数オブジェクト

`std::function`の使用例を以下に示す。

```cpp
#include <iostream>
#include <functional>
void hoge(void) {
  /* nop */
}
struct Fuga {
  void operator()(void) {
    /* nop */
  }
};
struct Piyo {
  void func(void) {
    /* nop */
  }
};
int main(void) {
  // 関数ポインタ
  std::function<void()> f1 = hoge;
  // ラムダ式
  std::function<void()> f2 = [](void) { /* nop */ };
  // 関数オブジェクト
  std::function<void()> f3 = Fuga();
  // 関数ポインタ
  std::function<void(Piyo&)> f4 = &Piyo::func;
  // operator()で呼び出しできる
  f1();
  // 関数がセットされているかどうかも判定できる
  std::function<void()> f5;
  if (!f5) {
    std::cout << "empty" << std::endl;
  }
  return 0;
}
```

## 保管方法

早速実装の解説に入る。

`union _Any_data`は`std::function`に代入される色んなファンクターを統一的に扱う機能を提供する。

```cpp
  class _Undefined_class;
  union _Nocopy_types
  {
    void*       _M_object;
    const void* _M_const_object;
    void (*_M_function_pointer)();
    void (_Undefined_class::*_M_member_pointer)();
  };
  union [[gnu::may_alias]] _Any_data
  {
    void*       _M_access()       { return &_M_pod_data[0]; }
    const void* _M_access() const { return &_M_pod_data[0]; }
    template<typename _Tp>
      _Tp&
      _M_access()
      { return *static_cast<_Tp*>(_M_access()); }
    template<typename _Tp>
      const _Tp&
      _M_access() const
      { return *static_cast<const _Tp*>(_M_access()); }
    _Nocopy_types _M_unused;
    char _M_pod_data[sizeof(_Nocopy_types)];
  };
```

`union _Nocopy_types`はポインタ、関数ポインタ、メンバ関数ポインタの共用体。関数ポインタとメンバ関数ポインタはそのまま代入することができ、それ以外は`void*`に変換して格納する。`union _Any_data`はさらにこれをwrapして、どれでも等しく`void*`のような使用感で読み書きできるようにしている。このように、実体が違うものをまとめて統一的に管理するのが`_Any_data`の役割である。

手元の環境では、ポインタと関数ポインタのサイズは8バイト、関数ポインタのサイズは16バイトで、`sizeof(_Any_data)`は16バイトだった。

```cpp
  std::cout << sizeof(void*) << std::endl;                        // 8
  std::cout << sizeof(const void*) << std::endl;                  // 8
  std::cout << sizeof(void(*)()) << std::endl;                    // 8
  std::cout << sizeof(void (Undefined_class::*)()) << std::endl;  // 16
  std::cout << sizeof(Any_data) << std::endl;                     // 16
```

## メモリ管理

ファンクタのメモリ管理方法は`_Function_base::_Base_manager<_Functor>`（と`_Function_handler` [^1]）に定義されている。動的にメモリが確保されるかどうかは、ファンクタのサイズ、align等に応じて決められる。

[^1]: invokerなどの一部関数はこちらに実装されているが、些細なことなのでここでは触れない。

メモリ確保が静的になるか動的になるかはコンパイル時定数の`__stored_locally`により決められる。メモリ確保のコードは以下のようになっている。 `__stored_locallyP`の値に応じて2つの初期化関数が呼び分けられる。

```cpp
        static void
        _M_init_functor(_Any_data& __functor, _Functor&& __f, true_type)
        { ::new (__functor._M_access()) _Functor(std::move(__f)); }
        static void
        _M_init_functor(_Any_data& __functor, _Functor&& __f, false_type)
        { __functor._M_access<_Functor*>() = new _Functor(std::move(__f)); }
```

`__stored_locally==true`の場合、配置new構文により`_Any_data`の記憶域（16 bytes）に関数ポインタ or メンバ関数ポインタ or インスタンスを書き込む。一方、`__stored_locally=false`の場合は`operator new`により確保したメモリ領域の先頭アドレスをvoid\*に見立てて`_Any_data`に書き込む。

次に、`__stored_locally`の計算部分のコードを示す。

```cpp
    static const size_t _M_max_size = sizeof(_Nocopy_types);
    static const size_t _M_max_align = __alignof__(_Nocopy_types);

    template<typename _Functor>
      class _Base_manager
      {
      protected:
        static const bool __stored_locally =
        (__is_location_invariant<_Functor>::value
         && sizeof(_Functor) <= _M_max_size
         && __alignof__(_Functor) <= _M_max_align
         && (_M_max_align % __alignof__(_Functor) == 0));
        // ...
```

ファンクタのサイズが`sizeof(_Nocopy_types)=16`より大きい、またはalignが16 bytesではよろしくない、またはlocation_invariantではない場合に`__stored_locally`が`false`になる。`__is_location_invariant<T>`の古い実装ではポインタ又は関数ポインタのときに限り`true`だったので、ラムダ式を使用する場合は常にメモリ確保が発生していた。現在は`__is_location_invariant<T>`は`is_trivially_copyable<T>`と同義なので、ラムダ式でも静的に格納できるようになっている。

まとめると、libstd++実装の`std::function`では、以下のいずれかに当てはまる場合にメモリ確保が発生する。

- `is_location_invariant`（=`is_trivially_copyable`）ではない
- メンバ変数（キャプチャした変数）のサイズが16バイトよりも大きい
- alignが16バイトではダメ

上記のルールを踏まえていくつかの例に対し`__is_locally_stored`の値がどうなるかを示す。

```cpp
void hoge(void) {}  // 普通の関数
class Fuga { void piyo(void) {} };  // メンバ関数
template <size_t N> struct DummyData;  // Nバイトの構造体（実装略）
template <size_t N> struct Fn;  // Nバイトのメンバを持つ関数オブジェクト（実装略）
struct Gn {
  Gn& operator=(const Gn& gn) { return *this; }
  void operator()(void) {}
};
int main(void) {
  // 関数ポインタ
  std::cout << stored_locally(hoge) << std::endl;                     // true
  // メンバ関数ポインタ
  std::cout << stored_locally(&Fuga::piyo) << std::endl;              // true
  // ラムダ式
  std::cout << stored_locally([](){}) << std::endl;                   // true （sizeof(fn)==1だから）
  std::cout << stored_locally([a=DummyData<16>()](){}) << std::endl;  // true （sizeof(fn)==16だから）
  std::cout << stored_locally([a=DummyData<17>()](){}) << std::endl;  // false（sizeof(fn)==17だから）
  // 関数オブジェクト
  std::cout << stored_locally(Fn<16>()) << std::endl;                 // true （sizeof(fn)==16だから）
  std::cout << stored_locally(Fn<17>()) << std::endl;                 // false（sizeof(fn)==17だから）
  std::cout << stored_locally(Gn()) << std::endl;                     // false（trivially_copyableではないから）

  return 0;
}
```

`stored_locally`関数の実装など詳細については <https://gist.github.com/komori-n/c8b8a4e0b1eaf7ad1623b63e50d94561> を参照。

## クラス本体

`std::function<_Signature>`は次の3つのメンバ変数を持つ（継承元から受け継いだ変数を含む）。

- `_Any_data _M_functor` (16bytes)
  - 管理しているファンクタ
- `_Manager_type _M_manager` (8bytes)
  - メモリの動的／静的確保と管理を行うユーティリティ関数への関数ポインタ
  - cloneやdestroy等のメモリに対する操作を指定できる
  - ファンクタが代入されているかどうかはこれが`nullptr`かどうかで判断する
- `_Invoker_type _M_invoker` (8bytes)
  - 関数の呼び出しを中継する関数への関数ポインタ

`std::function<_Signature>`のサイズは32 bytesとなる。`std::function`が関数ポインタを直接管理するよりも遅いと言われやすいのはこの辺りにも表れている。関数ポインタ自体は8 bytesだが、std::functionでは他のものも受け取れるような仕組みが入っているので必ず32 bytes必要になる。また、関数呼び出し時には間で`_M_invoker`を中継しているので生のポインタを扱うよりも遅い。

## まとめ

libstd++の `std::function`の実装をざっと追った。静的／動的メモリ確保の切り替えやtemplateテクニックを用いた実装の分岐などかなり参考になった。
