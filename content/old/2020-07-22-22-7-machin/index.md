---
author: komori-n
draft: true
categories:
  - ポエム
  - 数学
date: "2020-07-22T00:00:00+09:00"
guid: https://komorinfo.com/blog/?p=168
id: 168
image: https://komorinfo.com/wp-content/uploads/2020/07/011.png
og_img:
  - https://komorinfo.com/blog/wp-content/uploads/2020/07/011.png
permalink: /22-7-machin/
tags:
  - 22/7
title: ［22/7］マチンの公式からπ<22/7を証明する
url: 22-7-machin/
---

7/22は円周率近似値の日なので、文明の利器（マチンの公式）から雑に\\(\\pi&lt;22/7\\)を示した。

なお、僕が最近 [22/7](https://www.nanabunnonijyuuni.com/) にハマっていることはこの記事とは一切関係ない。<span class="easy-footnote-margin-adjust" id="easy-footnote-1-168"></span><span class="easy-footnote">[<sup>1</sup>](https://komorinfo.com/blog/22-7-machin/#easy-footnote-bottom-1-168 "グループ名の由来は円周率の近似値から。無限に続く可能性を表している")</span> <span class="easy-footnote-margin-adjust" id="easy-footnote-2-168"></span><span class="easy-footnote">[<sup>2</sup>](https://komorinfo.com/blog/22-7-machin/#easy-footnote-bottom-2-168 "「22/7 計算中（全76回）」を1週間で一気観してしまった")</span> <span class="easy-footnote-margin-adjust" id="easy-footnote-3-168"></span><span class="easy-footnote">[<sup>3</sup>](https://komorinfo.com/blog/22-7-machin/#easy-footnote-bottom-3-168 "<img loading="lazy" width="400" height="400" class="wp-image-226" style="width: 150px;" src="https://komorinfo.com/wp-content/uploads/2020/07/001.png" alt="" srcset="https://komorinfo.com/wp-content/uploads/2020/07/001.png 400w, https://komorinfo.com/wp-content/uploads/2020/07/001-300x300.png 300w, https://komorinfo.com/wp-content/uploads/2020/07/001-150x150.png 150w, https://komorinfo.com/wp-content/uploads/2020/07/001-75x75.png 75w, https://komorinfo.com/wp-content/uploads/2020/07/001-100x100.png 100w" sizes="(max-width: 400px) 100vw, 400px" />みうちゃん推し。シンパシーを感じる")</span> <span class="easy-footnote-margin-adjust" id="easy-footnote-4-168"></span><span class="easy-footnote">[<sup>4</sup>](https://komorinfo.com/blog/22-7-machin/#easy-footnote-bottom-4-168 "<img loading="lazy" width="400" height="400" class="wp-image-216" style="width: 150px;" src="https://komorinfo.com/wp-content/uploads/2020/07/011.png" alt="" srcset="https://komorinfo.com/wp-content/uploads/2020/07/011.png 400w, https://komorinfo.com/wp-content/uploads/2020/07/011-300x300.png 300w, https://komorinfo.com/wp-content/uploads/2020/07/011-150x150.png 150w, https://komorinfo.com/wp-content/uploads/2020/07/011-75x75.png 75w, https://komorinfo.com/wp-content/uploads/2020/07/011-100x100.png 100w" sizes="(max-width: 400px) 100vw, 400px" />一人称が「つぼ」のキャラがいてしゃべるたびにドキドキする")</span> <span class="easy-footnote-margin-adjust" id="easy-footnote-5-168"></span><span class="easy-footnote">[<sup>5</sup>](https://komorinfo.com/blog/22-7-machin/#easy-footnote-bottom-5-168 "最近リリースされた音ゲーが難しすぎて泣いた")</span>

### 証明の方針

\\(\\pi&lt;22/7\\)を示す方法はいろいろある。一番有名かつ古典的な方法は、円に外接する正96角形の周の長さから評価する方法である。<span class="easy-footnote-margin-adjust" id="easy-footnote-6-168"></span><span class="easy-footnote">[<sup>6</sup>](https://komorinfo.com/blog/22-7-machin/#easy-footnote-bottom-6-168 "2000年以上前に、アルキメデスが(3+10/71<\\pi<3+1/7)を示している")</span>

他にも、
\\begin{align}
0&lt;\\int_0^1\\frac{x^4(1-x)^4}{1+x^2}\\mathrm{d}x=\\frac{22}{7}-\\pi
\\end{align}
と空から降ってきた積分から簡単に示すこともできる。

今回は、マチンの公式を雑に評価することで\\(\\pi&lt;22/7\\)を示す。

### マチンの公式

$$4\\arctan\\frac{1}{5}-\\arctan\\frac{1}{239} = \\frac{\\pi}{4}$$

証明は[Wikipedia](https://ja.wikipedia.org/wiki/%E3%83%9E%E3%83%81%E3%83%B3%E3%81%AE%E5%85%AC%E5%BC%8F)を参照。2倍角の定理と加法定理から意外と簡単に示せる。

### 証明

マチンの公式の\\(\\arctan x\\)をテイラー展開すると、
\\begin{align}
\\frac{\\pi}{4}=\\sum\_{n=0}^{\\infty}\\left(4\\cdot\\frac{(-1)^n}{2n+1}\\left(\\frac{1}{5}\\right)^{2n+1}+\\frac{(-1)^{n+1}}{2n+1}\\left(\\frac{1}{239}\\right)^{2n+1}\\right)
\\end{align}
を得る。総和の一部を左辺に移動すると、
\\begin{align}
&amp;\\frac{\\pi}{4}-\\left(\\frac{4}{5}-\\frac{4}{3}\\cdot\\frac{1}{5^3}+\\frac{4}{5}\\cdot\\frac{1}{5^5}-\\frac{1}{239}+\\frac{1}{3}\\cdot\\frac{1}{239^3}\\right)\\\\
&amp;=
\\sum\_{n=0}^{\\infty}4\\cdot\\frac{(-1)^{n+1}}{2n+7}\\left(\\frac{1}{5}\\right)^{2n+7}
+\\sum\_{n=0}^{\\infty}\\frac{(-1)^{n+1}}{2n+5}\\left(\\frac{1}{239}\\right)^{2n+5}
\\end{align}
となる。右辺は負<span class="easy-footnote-margin-adjust" id="easy-footnote-7-168"></span><span class="easy-footnote">[<sup>7</sup>](https://komorinfo.com/blog/22-7-machin/#easy-footnote-bottom-7-168 "<br>\\begin{align}<br>\\sum_{n=0}^{\\infty}\\frac{(-1)^{n+1}}{2n+7}\\left(\\frac{1}{5}\\right)^{2n}<br>&<-\\frac{1}{7}+\\sum_{m=0}^{\\infty}\\frac{1}{9}\\frac{1}{25^m}\\<br>&=-\\frac{1}{7}+\\frac{1}{9}\\frac{1}{1-\\frac{1}{25}}\\<br>&<0.<br>\\end{align}<br>第2項も同様。<br>")</span>なので、
\\begin{align}
\\frac{\\pi}{4}&amp;&lt;\\frac{4}{5}-\\frac{4}{3}\\cdot\\frac{1}{5^3}+\\frac{4}{5}\\cdot\\frac{1}{5^5}-\\frac{1}{239}+\\frac{1}{3}\\cdot\\frac{1}{239^3}\\\\
&amp;&lt;\\frac{4}{5}-\\frac{4}{3}\\cdot\\frac{1}{5^3}+\\frac{4}{5}\\cdot\\frac{1}{5^5}-\\frac{1}{245}+\\frac{1}{25^3}\\\\
&amp;=\\frac{1804360}{3\\cdot5^6\\cdot7^2}
\\end{align}
となる。ここで、
\\begin{align}
4\\cdot\\frac{1804360}{3\\cdot5^6\\cdot7^2} &amp;&lt; \\frac{7217440}{3\\cdot5^6\\cdot7^2}+\\frac{1010}{3\\cdot5^6\\cdot7^2} \\\\
&amp;=22\\cdot\\frac{3\\cdot5^6\\cdot7}{3\\cdot5^6\\cdot7^2} \\\\
&amp;=\\frac{22}{7}
\\end{align}
なので、
\\begin{align}
\\pi &lt; \\frac{22}{7}
\\end{align}
を得る。
