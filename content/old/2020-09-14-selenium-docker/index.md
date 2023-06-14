---
author: komori-n
draft: true
categories:
  - プログラミング
date: "2020-09-14T21:02:29+09:00"
guid: https://komorinfo.com/blog/?p=508
id: 508
image: https://komorinfo.com/wp-content/uploads/2020/09/selenium.png
og_img:
  - https://komorinfo.com/blog/wp-content/uploads/2020/09/selenium.png
permalink: /selenium-docker/
tags:
  - Docker
  - Python
title: seleniumのGUIデバッグができるDockerコンテナ
url: selenium-docker/
---

Seleniumの環境構築は、chromedriverとGoogle Chromeのバージョンを合わせたりパスを通したりするなど結構手間が多い。WSLからWindows側のGoogle Chromeを操作しようとするとハマることが結構ある（あった）。

実は、Selenium公式でDockerコンテナが配布されていて、これを用いればどんな環境でもすぐにSeleniumデバッグ環境が構築できる。headlessモードだけでなく、GUIでブラウザの表示を確認しながらデバッグすることも可能である。

Dockerコンテナ起動のコマンドは以下。

```
$ docker run -d -p 4444:4444 -p 5900:5900 -v /dev/shm:/dev/shm selenium/standalone-chrome-debug
```

ポート5900がGUIデバッグ用。Ultra VNC<span class="easy-footnote-margin-adjust" id="easy-footnote-1-508"></span><span class="easy-footnote">[<sup>1</sup>](https://komorinfo.com/blog/selenium-docker/#easy-footnote-bottom-1-508 "https://forest.watch.impress.co.jp/library/software/ultravnc/")</span>などのVNCクライアントからコンテナに接続すれば、コンテナ内のデスクトップ画面が表示できる。<span class="easy-footnote-margin-adjust" id="easy-footnote-2-508"></span><span class="easy-footnote">[<sup>2</sup>](https://komorinfo.com/blog/selenium-docker/#easy-footnote-bottom-2-508 "PWは<code>secret</code>。")</span>

<div class="wp-block-image"><figure class="aligncenter size-large">![](https://komorinfo.com/blog/wp-content/uploads/2020/09/image-4-1024x777.png)</figure></div>
