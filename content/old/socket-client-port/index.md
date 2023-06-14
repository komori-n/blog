---
author: komori-n
draft: true
categories:
  - プログラミング
date: "2020-09-17T21:26:35+09:00"
guid: https://komorinfo.com/blog/?p=514
id: 514
image: https://komorinfo.com/wp-content/uploads/2020/09/cpp.png
og_img:
  - https://komorinfo.com/wp-content/uploads/2020/09/cpp.png
permalink: /socket-client-port/
tags:
  - C/C++
title: BSD socketでclient側のport番号を固定する
url: socket-client-port/
---

BSD socket APIでclient側のport番号を静的に決めたい。ググってもport番号を動的に決める例ばかりヒットして正しい情報になかなかたどり着けなかったのでメモ。

### 環境

- Ubuntu 20.04 LTS(WSL2)
- gcc 9.3.0
- netcat 1.206-1ubuntu1

### portのbind

以下のサイトが参考になる。
[Bind privileged port and remote authorization](http://cms.phys.s.u-tokyo.ac.jp/~naoki/CIPINTRO/NETWORK/bindpriv.html)

`connect`する前に`bind`を唱えればいいらしい。33400ポートを開けるコードは以下のような感じ。

```
  c_addr.sin_family = AF_INET;
  c_addr.sin_port = htons(33400);
  c_addr.sin_addr.s_addr = inet_addr("127.0.0.1");
  if (bind(sd, (struct sockaddr*)&c_addr, sizeof(c_addr))) {
    perror("client bind");
    return EXIT_FAILURE;
  }
```

### 実行結果

指定したポートが使用されているか`nc`コマンドで確認してみる。以下はサーバー側（netcat）のログ。

<figure class="wp-block-image size-large">![](https://komorinfo.com/wp-content/uploads/2020/09/image-5.png)</figure>ちゃんと33400番ポートを使って通信できていた。

コードの全文は以下<span class="easy-footnote-margin-adjust" id="easy-footnote-1-514"></span><span class="easy-footnote">[<sup>1</sup>](https://komorinfo.com/blog/socket-client-port/#easy-footnote-bottom-1-514 "<a rel="noreferrer noopener" href="https://www.mathkuro.com/network/socket/c-tcp-socket-sample/" target="_blank">C言語ソケット通信サンプル | 　mathkuro</a> のクライアントコードを参考にした")</span>。

<https://gist.github.com/komori-n/b0ce6a9e768e17633f87efb24175039a>
