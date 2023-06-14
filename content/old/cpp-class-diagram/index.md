---
author: komori-n
draft: true
categories:
  - プログラミング
date: "2021-01-17T10:13:16+09:00"
guid: https://komorinfo.com/blog/?p=849
id: 849
image: https://komorinfo.com/wp-content/uploads/2021/01/test_diagram.png
og_img:
  - https://komorinfo.com/wp-content/uploads/2021/01/test_diagram.png
permalink: /cpp-class-diagram/
tags:
  - C/C++
  - Docker
  - Python
title: C++のクラス図を楽して自動生成する
url: cpp-class-diagram/
---

## モチベ

諸般の事情により、ソースコードからリバースでクラス図を起こさなければならない事がある。個人的には、他人のソースコードを読む際にクラス図は必要ないタイプではあるが、世の中にはクラス図がないとコードが読めない人もいるらしい。

そのため、既にコードが完成している場合に、できるだけ楽してクラス図を生成する方法について紹介する。

## やり方

### サンプル

以下のようなC++ヘッダファイルを例にクラス図を生成してみる。

```
// hoge.hpp
#pragma once

#include <memory>

template <typename T>
class Hoge {
public:
  Hoge(T&& t);

  template <typename U>
  T pub_method(U u);

  virtual void pub_virtual_method(void) = 0;

  int pub_variable_;

protected:
  void pro_method(void);

private:
  void pri_method(void);

  std::unique_ptr<T> pri_variable_;
};
```

```
// fuga.hpp
#pragma once

#include <memory>
#include "Hoge.hpp"

struct FugaData {
  int x;
  int y;
}

class Fuga : Hoge<int> {
public:
  virtual void pub_virtual_mathod(void) override;

private:
  double fuga_variable_;
  std::unique_ptr<FugaData> fuga_data_;
};
```

`Fuga` クラスが `Hoge` クラスを継承しており、 `Fuga` クラスの中で `FugaData` 構造体を所有している。（このコード自体に深い意味はない）

このコードを例にクラス図を生成する。

### 生成方法

ヘッダファイル群を [hpp2plantuml](https://github.com/thibaultmarin/hpp2plantuml) に与え、[PlantUML](https://github.com/plantuml/plantuml) 形式を経由して画像に変換する。

hpp2plantumlはpythonで記述されたツールで、簡単に環境構築できる。

今回は、Dockerにより環境を構築した。

```
$ cat Dockerfile
FROM python:3

RUN pip install hpp2plantuml
$ docker build -t hpp2plantuml-test .
...（略）
$ docker run --rm hpp2plantuml-test hpp2plantuml -h
usage: hpp2plantuml [-h] -i HEADER-FILE [-o FILE] [-d] [-t JINJA-FILE]
                    [--version]

hpp2plantuml tool.

optional arguments:
  -h, --help            show this help message and exit
  -i HEADER-FILE, --input-file HEADER-FILE
                        input file (must be quoted when using wildcards)
  -o FILE, --output-file FILE
                        output file
  -d, --enable-dependency
                        Extract dependency relationships from method arguments
  -t JINJA-FILE, --template-file JINJA-FILE
                        path to jinja2 template file
  --version             show program's version number and exit
```

ヘッダファイルが `include/` に格納されている場合、以下のようにしてクラス図を生成できる。

```
$ docker run --rm -v $(pwd):/work hpp2plantuml-test hpp2plantuml -i "/work/include/*.hpp" \
  | sed 's/struct/class/g' \
  > test_diagram.pu
$ plantuml -tsvg test_diagram.pu
```

上記のコマンドを実行すると、次のようなクラス図が得られる。

<figure class="wp-block-image size-large">![](https://komorinfo.com/wp-content/uploads/2021/01/test_diagram.png)</figure>hpp2plantumlコマンドの後に `sed` コマンドを挟んで `struct` を `class` に置き換えている。このように、hpp2plantumlにより生成されたPlantUMLファイルは壊れていたり情報が欠けていたりすることがある。そのため、特にエラーなく図が生成できた場合でも、軽く図の確認をしたほうがいいと思う。

Draw.ioを職人芸で作るよりは見栄えが劣るかもしれないが、自動生成した割にはかなりいい感じのクラス図が生成できる。
