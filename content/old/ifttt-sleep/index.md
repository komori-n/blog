---
author: komori-n
draft: true
categories:
  - プログラミング
date: "2020-09-07T20:50:19+09:00"
guid: https://komorinfo.com/blog/?p=482
id: 482
image: https://komorinfo.com/wp-content/uploads/2020/09/acc-logo.png
og_img:
  - https://komorinfo.com/blog/wp-content/uploads/2020/09/acc-logo.png
permalink: /ifttt-sleep/
tags:
  - IFTTT
title: IFTTTからPCをスリープにする
url: ifttt-sleep/
---

NFCタグを読み取ってPCをスリープするやつを作ったら意外と手間取ったので忘れないようにメモ。

## 概要

最近、PCをスリープせずに放置することが増えた気がする。スリープするためには2クリックも必要なので、それが面倒に感じてしまう。

そこで、机の上のnfcタグをスマホで読み取ったらPCをスリープさせる仕組みを作った。nfcタグの代わりに時刻やIOTボタンをトリガにすることもできる。（電源ボタンは手を伸ばすのに疲れるのでダメ）

構成図は以下のようにした。

<div class="wp-block-image"><figure class="aligncenter size-large">![](https://komorinfo.com/blog/wp-content/uploads/2020/09/ifttt-1-1024x179.png)<figcaption>構成図</figcaption></figure></div>PCのスリープ処理はAssistantComputerControl（AAC）<span class="easy-footnote-margin-adjust" id="easy-footnote-1-482"></span><span class="easy-footnote">[<sup>1</sup>](https://komorinfo.com/blog/ifttt-sleep/#easy-footnote-bottom-1-482 "<a rel="noreferrer noopener" href="https://assistantcomputercontrol.com/" target="_blank">https://assistantcomputercontrol.com/</a>")</span>を用いた。これは、OneDriveやGoogle Driveのファイル同期を利用してPCを操作するツールである。トリガがAlexaやGoogle Assistantであれば、<https://ifttt.com/applets/qzhUdpaY> のようなレシピがACC公式から提供されているが、それ以外をトリガにしたい場合はIFTTTレシピを自作する必要がある。

## 実現方法

### NFC -&gt; IFTTT

スマホ自動化アプリのAutomate<span class="easy-footnote-margin-adjust" id="easy-footnote-2-482"></span><span class="easy-footnote">[<sup>2</sup>](https://komorinfo.com/blog/ifttt-sleep/#easy-footnote-bottom-2-482 "<a href="https://play.google.com/store/apps/details?id=com.llamalab.automate&amp;hl=ja" target="_blank" rel="noreferrer noopener">https://play.google.com/store/apps/details?id=com.llamalab.automate&amp;hl=ja</a>")</span>を用いる。

nfcタグにIFTTT WebhookのEvent名を予め書き込んでおいく。nfcタグを検知したら、下記URLにPOSTを打つように設定する。<span class="easy-footnote-margin-adjust" id="easy-footnote-3-482"></span><span class="easy-footnote">[<sup>3</sup>](https://komorinfo.com/blog/ifttt-sleep/#easy-footnote-bottom-3-482 "Webhookで投げるEvent名をそのままnfcタグに書き込んでおくと、コマンドを増やしたくなったときに使いまわしが利いて便利。お行儀は悪いけど。")</span>

```
url: https://maker.ifttt.com/trigger/{tag}/with/key/[my-key]
```

作ったFlowを常時起動しておけば、nfcタグからIFTTTトリガをかけられるようになる。

### IFTTT -&gt; OneDrive

IFTTTのthatの部分は、OneDriveの「Create text file」を選択して下記のように設定する。

<div class="wp-block-image"><figure class="aligncenter size-large">![](https://komorinfo.com/blog/wp-content/uploads/2020/09/image.png)<figcaption>IFTTT設定</figcaption></figure></div>Contentの欄が作成するテキストファイルの中身になる。ここに、ACCへのAction命令を記載する。ACCで使える命令の一覧は <https://acc.readme.io/docs/actions> を参照。今回はsleepとした。

Filenameの部分は拡張子が`.txt`であれば何でもよい。

これで、nfcタグを読み取ったらOneDriveのAssistantComputerControlフォルダに`sleep.txt`が生成されるようになった。<span class="easy-footnote-margin-adjust" id="easy-footnote-4-482"></span><span class="easy-footnote">[<sup>4</sup>](https://komorinfo.com/blog/ifttt-sleep/#easy-footnote-bottom-4-482 "最初はOneDriveではなくGoogle Driveで作ろうとしていたが、IFTTTとの連携がうまく行かずやめた。エラーメッセージが雑で、バグ取りに時間がかかりそうだったため。")</span>

### OneDrive -&gt; ACC

ACCをPCにインストールし、ガイドに従って初期設定を行う。最初にどのストレージサービスを使うかを利かれるので、「OneDrive」を選択して設定を進める。

<div class="wp-block-image"><figure class="aligncenter size-large">![](https://komorinfo.com/blog/wp-content/uploads/2020/09/image-1.png)<figcaption>ACCの初期設定</figcaption></figure></div>設定の最後で「3回shutdownして導通を確認しよう！」みたいな表示が出るが、sleepでも問題なかった。

<div class="wp-block-image"><figure class="aligncenter size-large">![](https://komorinfo.com/blog/wp-content/uploads/2020/09/image-2.png)</figure></div>これで、OneDriveのAssistantComputerControlフォルダにテキストファイルが追加されたら、その内容のActionを実行してくれるようになる。
