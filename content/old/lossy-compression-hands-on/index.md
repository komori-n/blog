---
author: komori-n
draft: true
categories:
  - ポエム
date: "2020-08-22T17:51:20+09:00"
guid: https://komorinfo.com/blog/?p=374
id: 374
og_img:
  - https://komorinfo.com/blog/wp-content/uploads/2020/08/20.jpg
permalink: /lossy-compression-hands-on/
title: jpegの劣化を体験する
url: lossy-compression-hands-on/
---

jpegの非可逆圧縮を気軽に体験できる方法の紹介。

## 手順

jpegは画像を保存する際に非可逆圧縮を行うため、保存するたびに画像が劣化していく。普段、画像が劣化している事を認識することは少ないかもしれないが、簡単に劣化を味わう方法があるので紹介したい。

まず、300 x 300 pxで真ん中に赤い線が描かれた画像をペイントで作り、jpegで保存する。

<div class="wp-block-image"><figure class="aligncenter size-large">![](https://komorinfo.com/blog/wp-content/uploads/2020/08/image.png)</figure></div>次に、保存した画像をペイントで開き、赤い線を上（または下）に1px移動させて保存しなおす。この手順を繰り返すと、保存のたびに赤い線がみるみる劣化していく様を見て取れる。

<div class="wp-block-image"><figure class="aligncenter size-large">![](https://komorinfo.com/blog/wp-content/uploads/2020/08/0.jpg)<figcaption>original</figcaption></figure></div><div class="wp-block-image"><figure class="aligncenter size-large">![](https://komorinfo.com/blog/wp-content/uploads/2020/08/5.jpg)<figcaption>5回保存</figcaption></figure></div><div class="wp-block-image"><figure class="aligncenter size-large">![](https://komorinfo.com/blog/wp-content/uploads/2020/08/10.jpg)<figcaption>10回保存</figcaption></figure></div><div class="wp-block-image"><figure class="aligncenter size-large">![](https://komorinfo.com/blog/wp-content/uploads/2020/08/20.jpg)<figcaption>20回保存</figcaption></figure></div>結果の一覧は以下。元の画像と比較して、保存のたびに赤い線がぼやけ、黒ずんでいっているのが見て取れる。

<div class="wp-block-image"><figure class="aligncenter size-large">![](https://komorinfo.com/blog/wp-content/uploads/2020/08/image-1.png)</figure></div>画像の編集と保存を繰り返す場合は、pngなどの可逆圧縮の形式を選びましょう。<span class="easy-footnote-margin-adjust" id="easy-footnote-1-374"></span><span class="easy-footnote">[<sup>1</sup>](https://komorinfo.com/blog/lossy-compression-hands-on/#easy-footnote-bottom-1-374 "あまり広くは使われていないと思うが、実はjpegでも可逆圧縮で保存するフォーマットがある（Lossless JPEG）")</span>
