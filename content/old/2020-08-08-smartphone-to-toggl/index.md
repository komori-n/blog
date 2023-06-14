---
author: komori-n
draft: true
categories:
  - プログラミング
date: "2020-08-08T10:30:50+09:00"
guid: https://komorinfo.com/blog/?p=343
id: 343
image: https://komorinfo.com/wp-content/uploads/2020/07/001.png
og_img:
  - https://komorinfo.com/blog/wp-content/uploads/2020/07/001.png
permalink: /smartphone-to-toggl/
tags:
  - Toggl Track
title: スマホ使用時間をtogglで記録する
url: smartphone-to-toggl/
---

スマホアプリの起動／終了に合わせてtogglで記録するやつを作った。

## やりたいこと

最近、<s>つらいことが多すぎて</s>スマホアプリの使用時間が増えている気がする。アプリごとの使用時間だけなら [QualityTime](https://play.google.com/store/apps/details?id=com.zerodesktop.appdetox.qualitytime&hl=ja) などで可視化できるが、できればtogglに記録して遊んでいる時間と作業している時間をまとめて管理したい。

以前、手でtogglで記録していたことがあったが、なかなか続かなかった<span class="easy-footnote-margin-adjust" id="easy-footnote-1-343"></span><span class="easy-footnote">[<sup>1</sup>](https://komorinfo.com/blog/smartphone-to-toggl/#easy-footnote-bottom-1-343 "2週間も持たなかったと思う")</span>。5分、10分のスキマ時間にスマホを触ると、ついついにtogglで記録をつけるのを忘れることが多かったからだ。

そこで、**特定のスマホアプリが起動したら同時にtogglのタイマーがスタートし、閉じたらタイマーが止まるような仕組み**を作った。

<div class="wp-block-image"><figure class="aligncenter size-large is-resized">![](https://komorinfo.com/blog/wp-content/uploads/2020/08/Screenshot_20200808-102206-2-670x1024.jpg)<figcaption>動作イメージ</figcaption></figure></div>大まかな構成は以下のようにした。

<div class="wp-block-image"><figure class="aligncenter size-large">![](https://komorinfo.com/blog/wp-content/uploads/2020/08/structure.png)</figure></div>- **Automate**｜スマホアプリの起動、終了を検出し、POSTリクエストを投げる
- **Google Apps Script(GAS)**｜リクエストが来たらtoggl APIを何回か叩く
- **toggl**｜アプリの使用開始、終了時刻を記録する

automateから直接toggle APIを叩くこともできるが、toggl APIは1回のリクエストでタイマーを止めることができないので、GASを間に挟んでいる。

## 設定

### Google Apps Scriptの設定

[Google HomeからTogglを使う – Qiita](https://qiita.com/tkms0106/items/4d1d44690676bca89c24)を大いに参考にした。

基本的には上記サイトで行っていることと同じ。GASにPOSTリクエストを送ると、リクエストを解釈してToggl APIを叩く設計にした。

上記サイトのコードに対し、以下の機能を追加した。

- タイマーを止めた際、durationが1分未満であれば削除する
  - ログの数を抑えるため
- アプリ名に応じてProject IDを設定する
  - アプリ名だけではログが見にくかったため

GASのコードは以下のようになった。

```
function doPost(e){
  var jsonStr = e.postData.getDataAsString();
  var data = JSON.parse(jsonStr);
  Logger.log(data);

  var authData = Utilities.base64Encode(data.user + ':api_token');

  var response = stopEntry(authData);
  if(data.word != "")
  {
    var response = startEntry(data.word, authData);
  }
  return ContentService.createTextOutput(response);
}

function startEntry(entryName, authData){
  var startUrl = "https://www.toggl.com/api/v8/time_entries/start";
  var pid = null;
  // set pid
  // ...
  var options = {
    'method' : 'post',
    'headers' : {"Authorization" : "Basic " + authData},
    'contentType' : 'application/json',
    'payload' : "{\"time_entry\":{\"description\":\"" + entryName + "\",\"wid\":[[wid]],\"pid\":" + pid + ",\"created_with\":\"Google Apps Script\"}}"
  }
  var response = UrlFetchApp.fetch(startUrl, options);
  return response;
}

function stopEntry(authData){
  var entry_id = getEntryId(authData);
  Logger.log(entry_id);
  var response = null;
  if (entry_id != null) {
    response = stopEntryById(entry_id, authData);
    var json = JSON.parse(response.getContentText());
    if (json.data.duration < 60) {
      response = deleteEntryById(entry_id, authData);
    }
  }
  return response;
}

function getEntryId(authData){
  var currentUrl = "https://www.toggl.com/api/v8/time_entries/current";
  var options = {
    'headers' : {"Authorization" : "Basic " + authData}
  }
  var id = null;
  try {
    var response = UrlFetchApp.fetch(currentUrl, options);

      var json = JSON.parse(response.getContentText());
      id = json.data.id;

  } catch(e) {}
  return id;
}

function stopEntryById(id, authData){
  var stopUrl = "https://www.toggl.com/api/v8/time_entries/" + id + "/stop";
  var options = {
    'method' : 'put',
    'headers' : {"Authorization" : "Basic " + authData},
    'contentType' : 'application/json'
  }
  var response = UrlFetchApp.fetch(stopUrl, options);
  return response;
}

function deleteEntryById(id, authData){
  var delUrl = "https://www.toggl.com/api/v8/time_entries/" + id;
  var options = {
    'method' : 'delete',
    'headers' : {"Authorization" : "Basic " + authData}
  }
  var response = UrlFetchApp.fetch(delUrl, options);
  return response;
}
```

35行目の`[[wid]]`を自分のワークスペースIDに書き換えて使う。計測するプロジェクトを設定したい場合は、20行目あたりにコードを挿入て`pid`を設定する。<span class="easy-footnote-margin-adjust" id="easy-footnote-2-343"></span><span class="easy-footnote">[<sup>2</sup>](https://komorinfo.com/blog/smartphone-to-toggl/#easy-footnote-bottom-2-343 "僕の場合は、ゲーム、将棋、城郭検定、暇つぶしの4つに分類している。")</span>

Webアプリとして公開すれば使えるようになる。タイマーを開始したい場合は、公開したWebアプリのURLに次のPOSTリクエストを投げつければよい。

```
{"user": [[API Token]], "word": [[word]]}
```

`API Token`は <https://toggl.com/app/profile> で確認できる。`word`は計測開始したいエントリ名の文字列を渡す。`word`を空にすると、タイマーの停止のみ行う。

### Automateの設定

アプリの起動、終了に合わせて上で作ったWebアプリにPOSTが飛ぶように設定する。

AutomateのFlowを2つ用意した。まず、メインとなるFlowをは以下の図のようにした。

<div class="wp-block-image"><figure class="aligncenter size-large is-resized">![](https://komorinfo.com/blog/wp-content/uploads/2020/08/post_toggl.png)</figure></div>ゆゆゆい<span class="easy-footnote-margin-adjust" id="easy-footnote-3-343"></span><span class="easy-footnote">[<sup>3</sup>](https://komorinfo.com/blog/smartphone-to-toggl/#easy-footnote-bottom-3-343 "<a rel="noreferrer noopener" href="https://yuyuyui.jp/" target="_blank">結城友奈は勇者である 花結いのきらめき</a>")</span>やナナオン<span class="easy-footnote-margin-adjust" id="easy-footnote-4-343"></span><span class="easy-footnote">[<sup>4</sup>](https://komorinfo.com/blog/smartphone-to-toggl/#easy-footnote-bottom-4-343 "<a rel="noreferrer noopener" href="https://227-game.com/" target="_blank">22/7 音楽の時間</a>")</span>など、特に<s>時間を溶かしにくる</s>ログに残したいアプリのリストを事前に用意しておく。foregroundのアプリが切り替わるたびに、計測対象化かどうかをforeach文で確認し、計測対象であればGASにPOSTを送りつける。POSTリクエストの回数を減らすために、アプリ終了時や計測対象外アプリの起動時はGASへのPOSTは行わない。

なお、オレンジで囲った部分は重複して計測開始しないようにするための処理である。「Twitter」などの一部のアプリでは画面遷移のたびにforegroundが書き換わった判定をしてしまうことがあるためである。また、「ゆゆゆい」や「youtube」などの一部のアプリでは、起動直後に「systemui」がforegroundになってしまうため、それを考慮した処理も入っている。

加えて、画面ロックしている間はタイマーが止まるようにFlowをもう一つ用意した。

<div class="wp-block-image"><figure class="aligncenter size-large is-resized">![](https://komorinfo.com/blog/wp-content/uploads/2020/08/lock.png)</figure></div>画面ロックする瞬間に計測を停止する処理と、ロック解除したときに計測再開する処理が入っている。

このFlowだと、スマホをロックした瞬間にtogglの計測が止まる。PCで作業していてスマホをつけて消しただけの可能性もあるが、僕の場合だとスマホをいじるときはだいたいサボっている時なのであまり問題に感じていない。

## 結果

<div class="wp-block-image"><figure class="aligncenter size-medium is-resized">![](https://komorinfo.com/blog/wp-content/uploads/2020/08/Screenshot_20200808-101551-2-291x300.jpg)<figcaption>とある平日の記録</figcaption></figure></div>思ったよりもスマホで時間が浪費していて真顔になった。
