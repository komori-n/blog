---
author: komori-n
draft: true
categories:
  - やってみた
  - 技術解説
date: 2023-07-06T20:50:22+09:00
tags:
  - Python
keywords:
  - OCR
  - Tesseract
  - OpenCV
  - 円周率
  - 間違い
  - 暗黒通信団
title: 『間違いだらけの円周率1,000,000桁表』の間違いを探す
relpermalink: blog/find-errors-in-pi-book
url: blog/find-errors-in-pi-book
description: 暗黒通信団『間違いだらけの円周率1,000,000桁表』に対し、Python（OpenCV+Tesseract）を用いて310個の間違いを見つけた話。
---

暗黒通信団『間違いだらけの円周率1,000,000桁表』に対し、Python（OpenCV+Tesseract）を用いて310個の間違いを見つけた。

なお、本ページは間違いの見つけ方についてのみ説明する。
著作権および間違い探しの楽しみに配慮するために、どこにどのような間違いがあったのかについては書かれていない。
どうしても気になる方は、本ページで説明する手順に従うことで、本ページの結果を再現できる。

本ページの間違い探しで使用したコードは以下のリポジトリで確認できる。

{{< github repo="komori-n/find-errors-in-inaccurate-pi-book" >}}

## はじめに

先日、友人に[間違いだらけの円周率1,000,000桁表](https://ankokudan.org/d/d.htm?detail315-detailread-e.html)
という本をもらった。この本は[円周率1,000,000桁表](http://ankokudan.org/d/d.htm?detail002-detailread-j.html)
で有名な同人サークル『暗黒通信団』が発行している本で、タイトルの通り、微妙に間違った円周率が100万桁分掲載されている。

この本には、1ページあたり約3個の間違いが含まれているらしい。
割合に直すと誤り率は 0.03 % であり、残りの 99.97 % は正しい円周率が記されている。
つまり、この本はほとんどが円周率表なのだが、ごく一部混入された間違い探しを楽しむ本なのである。

この本では、1ページあたり10,000桁の数字が詰め込まれており、文字がとても細かい。

![1円玉と本文のサイズ比較](feature.png "1円玉と本文のサイズ比較")

この本に含まれる全ての間違いを人力だけで見つけるのはほぼ不可能である。
というのも、円周率は10桁ごとの塊に区切られて掲載されているのだが、10桁を2秒で読めたとしても、
全文読み終わるまで55時間もかかってしまう。そもそも、
字が細かすぎて10桁2秒のペースで読み続けることすら難しい。

せっかく頂いた間違い探し本の間違いを見つけられないのはなんだか悔しいと感じていた。
そこで、コンピュータの力を借りてできるだけ間違いを探してみた。
本ページでは、この間違いの見つけ方の概要について記す。

## 間違い探しの方針

本文を文字に起こす際は[Tesseract OCR](https://github.com/tesseract-ocr/tesseract)を使用した。
TesseractはオープンソースのOCR（Optical Character Recognition/Reader, 光学的文字認識）エンジンである。
英語にとどまらず、日本語やギリシャ語など数多くの言語のテキストを精度良く認識することができる。

ただし、Tesseractへ丸投げするだけでは読み取り精度があまり良くない。
そのため、Tesseractに画像を渡す前に、[OpenCV](https://opencv.org)で画像の前処理を行う必要がある。

全体としては、以下のような手順で作業を行った。

1. テキストのスキャン
2. 画像の前処理
3. 文字認識（Tesseract）
4. 結果の手修正
5. 間違いの列挙

手順 1., 3., 5. については特に工夫の余地がない。よって以下では手順2., 4.で工夫したポイントについて説明する。

## 前処理

Tesseractへ文字認識を投げる前に、入力画像に対し以下の前処理を行った。

- 画像の傾き補正
- 10文字ごとの切り出し
- 文字のシャープ化とコントラスト調整

### 画像の傾き補正

本文のスキャンは手作業で行っているため、どうしても文字に傾きが生じてしまう。
Tesseractは文字の傾きに弱いので、前処理で傾きを直す必要がある。

本に数字がびっしりと書かれていることを利用してページの傾きを求める。
具体的には、`cv2.dilate()` で数字が書かれた領域を塗りつぶして、`cv2.findContours()` で輪郭抽出すればよい。

```python
def _make_flat(img: cv2.Mat) -> cv2.Mat:
    tmp_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    tmp_img = cv2.bitwise_not(tmp_img)
    tmp_img = cv2.dilate(src=tmp_img, kernel=np.ones((10, 10)), iterations=5)
    _, tmp_img = cv2.threshold(tmp_img, 100, 255, cv2.THRESH_BINARY)

    contours, _ = cv2.findContours(tmp_img, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours:
        if cv2.contourArea(cnt) < 1000000:
            continue

        rect = cv2.minAreaRect(cnt)
        angle = rect[2]

        orig_height, orig_width, _ = img.shape
        rect_width, rect_height = rect[1]
        if rect_width > rect_height:
            angle += 90.0

        height, width = max(orig_height, orig_width), min(orig_height, orig_width)
        rot_center = (height / 2, height / 2)
        matrix = cv2.getRotationMatrix2D(rot_center, angle, 1.0)

        return cv2.warpAffine(img, matrix, (width, height), borderValue=(255, 255, 255))

    raise RuntimeError("Text area is not found")
```

### 10文字ごとの切り出し

円周率表には、1ページあたり10,000桁が書かれている。各ページは100行で構成されており、
各行は10桁区切りで100桁が掲載されている。この10桁区切りおよび各行の行間は、約0.5mmのスペースによって区切られている。

先述したように、1ページは100 x 10の格子上に10桁の数字が書かれている。
この100 x 10 = 1000マスを一度の輪郭抽出で検出するのは難しいので、行→列の順で画像の分割を行った。

行や列の認識は、傾き検出のときと同様に、`cv2.dilate()` で数字領域を塗りつぶして、
`cv2.findContours()` により検出した。また、画像の切り出しの際は、検出した行・列以外の範囲を
白（背景色）で塗りつぶして余計な文字を消した。

```python
def _make_contour_images(
    img: cv2.Mat, rects: list[Rect], contours: list[np.ndarray], padding: int
) -> list[cv2.Mat]:
    images = []
    padding_func = make_padding_func(padding, img.shape)
    for rect, cnt in zip(rects, contours):
        x, y, w, h = padding_func(rect)
        vertical_img = img[y : y + h, x : x + w].copy()

        # Remove outside of contour hull
        pts = cnt - cnt.min(axis=0) + padding
        mask = np.zeros(vertical_img.shape[:2], np.uint8)
        cv2.drawContours(mask, [pts], -1, (255, 255, 255), -1, cv2.LINE_AA)
        vertical_img[mask != 255] = (255, 255, 255)

        images.append(vertical_img)

    return images
```

### 文字のシャープ化とコントラスト調整

スキャンする際、どうしても画像に濃淡が生じてしまう。特に、文字が薄くなってしまった箇所は、
Tesseractでの文字認識に失敗しやすい。そのため、そのような箇所では文字のシャープ化とコントラスト調整を行った。

```python
# 文字のシャープ化
# 薄い部分は薄く、濃い部分はより濃く鳴るようなフィルターを通す
# これにより、文字のぼやけた部分がはっきりとして、Tesseractの認識精度が向上する
cell_img = cv2.filter2D(
    cell_img, -1, np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
)
# コントラスト調整
cell_img = cv2.bitwise_not(
    cv2.convertScaleAbs(cv2.bitwise_not(cell_img), None, 1.5)
```

## 手修正

上記の前処理を施しても、Tesseractの文字認識精度は100 %にならない。
どれだけ前処理を頑張っても、9と0を取り違えるケースが多かった。
今回の目的は100 %の文字認識を達成することではなく、間違いをできるだけ列挙することなので、
認識精度はこのままとし、目視により結果の手修正を行った[^1]。

Tesseractで認識した数字と正しい円周率100万桁を比較したところ、410箇所違う箇所があった。
この410箇所の中には、Tesseractで正しく文字認識できなかった箇所と、本の記載が間違っている箇所の両方が含まれる。
この410箇所すべてを目で確認し、どちらに属するかを振り分けなければならない。

目視で確認すべき箇所が大量にあるので、単純に本と認識結果を突き合わせる方法だととても時間がかかる。
よって、目視確認の作業を効率化するために、前処理で言及した10桁ごとに切り出す処理を流用することにした。

1. 確認したい文字を含む10桁の塊を画像として切り出す
2. 切り出した画像を表示する
3. 画像を目視で確認して、10桁の数字を打ち込む
4. 打ち込んだ数字とTesseractの認識結果を比較し、もし異なるなら認識結果を修正する

![手修正の様子](image.png "手修正の様子。左のウィンドウが10桁区切りの切り出しで、その数字を右のウィンドウへ打ち込む。この作業を410回繰り返す。")

この手作業により、410箇所の検出箇所のうち、100箇所はTesseractによる文字認識誤りだと判明した。

## 結果

上記の手順により、結果として間違いを310個見つけることができた。
間違いの内訳としては、普通の（正しくない数字が書かれている）間違いが293個、
普通ではない間違い17個あった。特に「普通ではない間違い」が曲者で、
Tesseractの文字認識をとても難易度の高い間違いだった[^2]。

[^2]:
    原本が手元にあって、「普通ではない間違い」を実際に見てみたい方は、
    例えば以下の箇所で見つけられる。①0170001-0180000 ページ下部のほう中央
    ②0260001-0270000 ページ右上のあたり ③0500001-0510000 ページ中央やや下

1ページあたりの間違い個数の分布を以下に示す。

{{< chart >}}
type: 'bar',
data: {
labels: ["0", "1", "2", "3", "4", "5", "6", "7"],
datasets: [{ label: "334",
data: [1, 17, 22, 25, 16, 8, 7, 4]
}]
},
options: { scales: {
x: { display: true, title: { display: true, text: "1ページあたりの間違い個数" }},
y: { display: true, title: { display: true, text: "ページ数" }}
}, plugins: { legend: { display: false },
title: {display: true, text: "ページあたりの間違い個数"}}}
{{< /chart >}}

今回の手法で発見できた間違いに限ると、全く間違いがないページが1つあったのに対し、
間違いが7個あるページが4つ見つかった。

今回の手法では310個の間違いを見つけることができた。
しかし、310個という数は中途半端なので、
あと4個（3.14 x 100）または5個（この本の税抜価格315円）程度の間違いが残っていると予想する。
これは、Tesseractを用いた方法では文字認識精度に限界があるためである。
この本の間違いを全て見つけるためには、Tesseractで楽をするのではなく、
目視で全数確認するしか方法はないと考える。
