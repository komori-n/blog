---
author: komori-n
draft: true
categories:
  - ポエム
date: "2021-06-02T23:46:48+09:00"
guid: https://komorinfo.com/blog/?p=1143
id: 1143
image: https://komorinfo.com/wp-content/uploads/2021/06/Rakuten-UN-LIMIT-e1586579934946.png
og_img:
  - https://komorinfo.com/wp-content/uploads/2021/06/Rakuten-UN-LIMIT-e1586579934946.png
permalink: /rakuten-out-of-service/
title: 楽天モバイル回線で電波は拾っていそうなのにアンテナが立たない時の対処法
url: rakuten-out-of-service/
---

最近、携帯の回線を楽天モバイルに変えた。変えた当初、電波が届いていると思われるのに、一瞬アンテナが立ってすぐに圏外になってしまう現象に悩まされた。

<figure class="wp-block-image size-large">![](https://komorinfo.com/wp-content/uploads/2021/06/image-1024x145.png)</figure>↑ 右上の電波マークの1つ目が圏外になっている<span class="easy-footnote-margin-adjust" id="easy-footnote-1-1143"></span><span class="easy-footnote">[<sup>1</sup>](https://komorinfo.com/blog/rakuten-out-of-service/#easy-footnote-bottom-1-1143 "2つ目は格安SIMのドコモ回線")</span>

機内モードガチャをしたりしばらく放置したりすれば自然と治るが、使いたいときに確率で通信できなくなるのは不便に感じていた。

## 環境

- Rakuten UN-LIMIT VI
- OnePlus 7T
- Oxygen OS 11.0.1.1.HD65AA (Android 11 based)

## 原因と対処法

確率的に圏外になる原因は、スマホ側が気を利かせてLTE以外で通信しようとしてしまうためである。そのため、スマホに楽天モバイルがLTE onlyであることを教える必要がある。

やり方は簡単である。まず、電話アプリを開いて「\*#\*#4636#\*#\*」と入力する。すると、通話開始ボタンを押さなくても勝手に以下のような画面に遷移する。

<figure class="wp-block-image size-large">![](https://komorinfo.com/wp-content/uploads/2021/06/image-1-1024x813.png)</figure>そこで、「携帯電話情報」-&gt;「優先ネットワークの種類を設定」を「LTE only」を選択すれば完了だ。特に保存は必要なく、一度モバイルデータ通信を無効にして、再度有効化し直せば正常に使えるようになるはずである。
