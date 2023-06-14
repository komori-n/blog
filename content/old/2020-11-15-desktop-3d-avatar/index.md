---
author: komori-n
draft: true
categories:
  - プログラミング
  - ポエム
date: "2020-11-15T20:30:12+09:00"
guid: https://komorinfo.com/blog/?p=603
id: 603
image: https://komorinfo.com/wp-content/uploads/2020/11/image-3.png
og_img:
  - https://komorinfo.com/wp-content/uploads/2020/11/image-3.png
permalink: /desktop-3d-avatar/
tags:
  - Oculus Quest
title: デスクトップの隅に自分の分身の3Dアバターを表示させる
url: desktop-3d-avatar/
---

[旧ブログ](https://blog.hatena.ne.jp/komori_pyon/komodiary.hatenablog.jp/edit?entry=26006613590591129) （読む必要なし）の続き。

## 概要

デスクトップの端っこに自分の分身を表示させたい。自分の体を動かすのに合わせて、画面の中の女の子も動いて欲しい。

<div class="wp-block-image"><figure class="aligncenter size-large">![](https://komorinfo.com/wp-content/uploads/2020/11/bandicam-2020-11-15-19-40-41-653.gif)</figure></div>とりあえず以下のような環境を目指してみる。[Oculus Quest 2](https://www.oculus.com/quest-2/) <span class="easy-footnote-margin-adjust" id="easy-footnote-1-603"></span><span class="easy-footnote">[<sup>1</sup>](https://komorinfo.com/blog/desktop-3d-avatar/#easy-footnote-bottom-1-603 "意外と使いみちが少なくて持て余している")</span> <span class="easy-footnote-margin-adjust" id="easy-footnote-2-603"></span><span class="easy-footnote">[<sup>2</sup>](https://komorinfo.com/blog/desktop-3d-avatar/#easy-footnote-bottom-2-603 "発売前に垢Banに関して色々とゴタゴタがあったが、発売日に作った僕のFacebook垢は未だにBanされていない")</span>からPC側の[VirtualCast](https://store.steampowered.com/app/947890/VirtualCast/?l=japanese)を起動し、キャプチャした映像を[OBS Studio](https://obsproject.com/ja/download)で左右反転させてデスクトップの隅に出力する。Virtual Castでは仮想空間内にディスプレイを置くことができるので、ゴーグルを装着しながら他の作業ができる<span class="easy-footnote-margin-adjust" id="easy-footnote-3-603"></span><span class="easy-footnote">[<sup>3</sup>](https://komorinfo.com/blog/desktop-3d-avatar/#easy-footnote-bottom-3-603 "恐らくVRChatでも同様のことはできるが、VRChatで独自のアバターを利用するにはUser Rankを上げる必要があり断念した。仮想空間で知らない人とフレンドになるのはハードルが高すぎる。")</span>。

<div class="wp-block-image"><figure class="aligncenter size-large">![](https://komorinfo.com/wp-content/uploads/2020/11/vr_desktop-1.jpg)<figcaption>目指す構成</figcaption></figure></div>## VirtualCast

最終的にはVR空間にPC側のディスプレイを映したいので、Oculus QuestではなくPC側の[VirtualCast](https://store.steampowered.com/app/947890/VirtualCast/?l=japanese)を使用する。PC側のVRアプリを起動できるように、事前に[VirtualDesktop](https://www.oculus.com/experiences/quest/2017050365004772/?locale=ja_JP)をインストールしておく<span class="easy-footnote-margin-adjust" id="easy-footnote-4-603"></span><span class="easy-footnote">[<sup>4</sup>](https://komorinfo.com/blog/desktop-3d-avatar/#easy-footnote-bottom-4-603 "僕の環境では何回やってもOculus Linkが使えなかったので、VirtualDesktopを使用している。PCとの間は無線接続になるが、今のところはけっこう快適に使用できている。")</span>。

VirtualCastを起動したら、「アイテム -&gt; 追従カメラ」を選択し、追従カメラを有効化する。また、「アイテム -&gt; ディスプレイ」からPCのディスプレイをVR空間でも見られるようにする。カメラの視線が気になる場合、カメラをディスプレイの裏に隠すのがおすすめ。

<figure class="wp-block-image size-large">![](https://komorinfo.com/wp-content/uploads/2020/11/image-1-3-1024x418.jpg)</figure>追従カメラが正しく有効化できていれば、PCのVirtualCastのウィンドウに追従カメラの映像が表示される。

<div class="wp-block-image"><figure class="aligncenter size-large">![](https://komorinfo.com/wp-content/uploads/2020/11/image-1.jpg)</figure></div>## OBS Studio

VirtualCastのウィンドウをそのまま眺めるだけでも楽しめるが、[OBS Studio](https://obsproject.com/ja/download)を通して左右反転させると、自分が美少女になった感覚が味わえるのでよきである。

OBS Studioを開き、「ソース -&gt; ゲームキャプチャ」からVirtualCastのウィンドウを選択する。映像が取り込めたら、OBS Studioのメニューバーの「水平 -&gt; 変換 -&gt; 水平反転」から映像を左右反転させることができる。

<div class="wp-block-image"><figure class="aligncenter size-large">![](https://komorinfo.com/wp-content/uploads/2020/11/image-1-1.jpg)</figure></div>次に、出力する映像のサイズを変更する。映像を出力していない状態で、「ファイル -&gt; 設定 -&gt; 映像」から出力サイズを変更できる。デフォルトでは出力サイズは横長に設定されているが、大きさを調整してアバターの上半身がうまく映るサイズにする。

最後に、キャプチャ画面を右クリックして「ウィンドウ プロジェクター（プレビュー）」を選択すると、自分の分身が映ったウィンドウが作れる<span class="easy-footnote-margin-adjust" id="easy-footnote-5-603"></span><span class="easy-footnote">[<sup>5</sup>](https://komorinfo.com/blog/desktop-3d-avatar/#easy-footnote-bottom-5-603 "本当は、背景をクロマキーにしてアバター部分だけを表示させたかった。背景を変えるところまでは簡単にできるが、デスクトップにアバターだけを表示する手段が意外に少ない。試したがダメだった手段を列挙してみる。</p>

<ul><li><a href="http://michaelsboost.com/CamDesk/">CamDesk</a>はOBSのVirtual Cameraを認識してくれなかった</li><li><a href="https://github.com/zaru/mewcam">mewcam</a>はVirtual Cameraを選択するとフリーズして使えなかった</li><li><a href="https://www.bandicam.com/how-to-use-chroma-key/">Bandicam</a>は動画の録画中は理想の状態に近いが、録画していないときにカメラ映像を表示する方法が見つからなかった</li></ul>

<p>")</span>。[Borderless Gaming](https://www.gigafree.net/utility/window/Borderless-Gaming.html)などのソフトを用いてタイトルバーを消すとより良い感じになる。

<div class="wp-block-image"><figure class="aligncenter size-large">![](https://komorinfo.com/wp-content/uploads/2020/11/image-3.png)</figure></div>## 改良

上述の方法には1つだけ致命的な問題点がある。

VirtualCast上では、PCのデスクトップがとても見づらい。画面に目線を近づければ文字を読むことはできるが、遠くから見ると字が潰れていてかなりしんどい。GPUや通信環境のグレードを上げれば解決するのかもしれないが、なにか他に方法はないかと探した。

解決方法はシンプルで、VirtualCastから抜ければよい。最終的には以下の構成に落ち着いた。VirtualCastアプリから抜けても、顔のトラッキングやアバターの描画などは裏で動き続けてくれる<span class="easy-footnote-margin-adjust" id="easy-footnote-6-603"></span><span class="easy-footnote">[<sup>6</sup>](https://komorinfo.com/blog/desktop-3d-avatar/#easy-footnote-bottom-6-603 "手のトラッキングは止まったり止まらなかったりする")</span>。また、Virtual Desktopアプリで表示されるPC画面は、文字の描画がきれいで快適に作業できる。VirtualCast上のように自由にディスプレイを配置することはできないものの、この環境なら実用に耐えらそう。

<div class="wp-block-image"><figure class="aligncenter size-large">![](https://komorinfo.com/wp-content/uploads/2020/11/image-1-2.jpg)</figure></div>VR空間では以下のような見た目で作業できる。

<div class="wp-block-image"><figure class="aligncenter size-large">![](https://komorinfo.com/wp-content/uploads/2020/11/image-1-4-1024x680.jpg)<figcaption>スマホへミラーリングした際の画像のため画質が悪くなっているが、実際には右下の時刻までくっきりと判別できる。</figcaption></figure></div>## Zoom会議

蛇足。

OBSを通すとVirtual Cameraにアバター映像を出せるので、アバター姿でZoom会議に参加できる。

<figure class="wp-block-embed-twitter aligncenter wp-block-embed is-type-rich is-provider-twitter"><div class="wp-block-embed__wrapper">> [pic.twitter.com/tx43UayTS3](https://t.co/tx43UayTS3)
>
> — コウモリ (@komori\_pyonpyon) [November 14, 2020](https://twitter.com/komori_pyonpyon/status/1327585395173773312?ref_src=twsrc%5Etfw)

<script async="" charset="utf-8" src="https://platform.twitter.com/widgets.js"></script></div></figure>FaceRigの犬のアバターで社のMTGに参加しているおじさんを見たことあるし、美少女アバターで参加しても何も言われなさそう。
