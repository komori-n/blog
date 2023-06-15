---
author: komori-n
draft: true
categories:
  - プログラミング
change-canonical:
  - https://komorinfo.com/blog/pointer-and-big-endian/
date: "2020-07-08T19:31:21+09:00"
guid: https://komorinfo.com/blog/?p=56
id: 56
image: https://komorinfo.com/wp-content/uploads/2020/07/pointer-1.png
og_img:
  - https://komorinfo.com/blog/wp-content/uploads/2020/07/pointer.png
permalink: /pointer-cast-and/
tags:
  - C/C++
  - QEMU
title: ポインタのキャストでエンディアンを意識しないとバグる例
url: pointer-cast-and/
---

常識だと思っていたことがあまり知られていなかったっぽいのでメモを兼ねて共有する。

## 問題設定

```c
void event1(int32_t* param) {
  uint8_t data = (uint8_t)*param;
  printf("%"PRId8"\n", data);  // PRId8：uint8_tのフォーマット指定子
}
void event2(int32_t* param) {
  uint8_t data = *(uint8_t*)param;
  printf("%"PRId8"\n", data);
}
```

上のような`int32_t*`を引数に取るイベント関数を考える。この関数たちに`uint8_t`の値を渡したい場合、それぞれ次のように書く。

```c
// 渡したいデータ
uint8_t data = 96;

int32_t param1 = (int32_t)data;
event1(&param1);

// 検証のために適当に値を埋めておく
int32_t param2 = 0xdeadbeef;
*( (uint8_t*)&param2 ) = data;
event2(&param2);
```

読み出し方に応じて値の格納の方法も変えなければならない。

Little Endianの環境では、`int32_t*`の指す先に下位bitが詰まっているので、どちらの方法で読み書きしても問題なく動く。一方、Big Endianの環境では`int32_t*`には上位の方の値が格納されているので、書き込み方によってレジスタの中身が変わってしまう。

## 実験

Big Endianだと本当にバグるのか実験してみた。

Big Endianで動くコンピュータが手元にないので、qemuで仮想環境を作った。wslで以下のコマンドを打てば、Windowsでも簡単にBig Endian環境でテストができる。

```sh
sudo apt-get install gcc-multilib-mips-linux-gnu gcc-mips-linux-gnu qemu-user
mips-linux-gnu-gcc test.c -o test -static
qemu-mips ./test
```

参考：<https://stackoverflow.com/questions/2839087/how-to-test-your-code-on-a-machine-with-big-endian-architecture>

この環境で

```c
event1(&param1);
event2(&param2);

event1(&param2);
event2(&param1);
```

を実行すると、結果は

```sh
96
96
239
0
```

となった。確かに、変数への格納と取り出しはセットにしないとバグってしまった。

## 検証コード

[GitHub – event-endian-test.c](https://gist.github.com/komori-n/f00e52341b176bf39d48d1059d70a9d8)
