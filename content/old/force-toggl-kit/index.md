---
author: komori-n
draft: true
categories:
  - プログラミング
date: "2020-11-22T09:43:55+09:00"
guid: https://komorinfo.com/blog/?p=640
id: 640
image: https://komorinfo.com/wp-content/uploads/2020/11/ダウンロード.png
og_img:
  - https://komorinfo.com/wp-content/uploads/2020/11/ダウンロード.png
permalink: /force-toggl-kit/
tags:
  - Toggl Track
title: PCでTogglの作業記録を強制する
url: force-toggl-kit/
---

## 背景とやりたいこと

半年ぐらい前から、暇つぶしや勉強時間の記録に [Toggl Track](https://track.toggl.com) を使用している。日々、どれだけ無為に時間を浪費しているかを可視化できて、生産性の向上に役立っている……気がする。

Togglの使い方はとても単純で、作業開始時にタイマー開始を押して、作業終了時にタイマーを止めるだけである。計測記録には説明やカテゴリをつけることができ、作業前、作業中、作業後の任意のタイミングで記入できる。

<figure class="wp-block-image size-large">![](https://komorinfo.com/wp-content/uploads/2020/11/image-7.png)</figure>『手軽に記録をつけられるから続けやすい』と紹介されることが多いツールだが、僕にとってはめんどくさい作業に感じていた。作業を始めるときは「5分だけだから……」と思っていても、集中しているうちにn時間経過していて記録に残せていないということが多々あった。

スマホアプリの時間計測については、[自動的に浪費時間を記録する方法](https://komorinfo.com/blog/?p=640&preview=true)で取りこぼしなく記録できている。ただ、PCの使用時間は、起動しているアプリと作業内容が一対一に対応していなかったり、PCを点けたまま席を外すことがあったりするので自動化はできていなかった<span class="easy-footnote-margin-adjust" id="easy-footnote-1-640"></span><span class="easy-footnote">[<sup>1</sup>](https://komorinfo.com/blog/force-toggl-kit/#easy-footnote-bottom-1-640 "PCアプリの使用時間を計測するだけなら <a rel="noreferrer noopener" href="https://www.manictime.com" target="_blank">ManicTime</a> で実現できる。ただ、アプリの使用時間と作業内容はあまり結びついていない気がして、見返してもよくわからなかったので辞めた。")</span>。PCアプリ版では、タイマーが動いていない状態が続くと最短1分間隔で警告を出す機能があるが、警告のポップアップが作業の邪魔にならないのであまり効果はなかった。

<figure class="wp-block-image size-large">![](https://komorinfo.com/wp-content/uploads/2020/11/image-8.png)</figure>そこで、Togglでの時間計測を強制するために、Togglで計測していないとPCが使えなくなる仕組みを作った。

## 環境

- Windows 10 Education 2004
- Ubuntu 20.04 LTS(WSL2)

スクリプトの動作には `jq` （jsonのパースコマンド）が必要。

## Toggl監視スクリプト

PCを使えなくする手段はいくつか考えられるが、今回は単純にPCをロックしてしまうことにした。一定間隔でTogglの計測状態をポーリングし、計測されていない状態が続いた場合、PCをロックして作業を続けられなくする。

作成したスクリプトを以下に示す。このスクリプトはWSL上のbashで動作されることを想定している。スクリプト中の変数 `TOGGL_USER` には `https://track.toggl.com/profile` で確認できるAPIキーを記入する必要がある。

```
#!/bin/bash
LOCK_SCRIPT='rundll32.exe user32.dll,LockWorkStation'
ISLOCK_SCRIPT='
$lockapp = Get-Process lockapp;
$process=[System.Diagnostics.Process]::GetProcessById($lockapp.Id);
$threads=$process.Threads;
if ($threads[0].WaitReason -eq "Suspended") { "1" }
'
TOGGL_CURR_URL='https://www.toggl.com/api/v8/time_entries/current'
TOGGL_USER='<<your API key>>'
AUTH=$(echo -n "${TOGGL_USER}:api_token" | base64)
check_toggl() {
  curl -s -H "Authorization: Basic ${AUTH}" ${TOGGL_CURR_URL}
}
exec_powershell() {
  echo $@ | powershell.exe -Command -
}
UNTRACK_CNT=0
while true; do
  sleep 30
  RES=$(check_toggl | jq '.data')
  if [ "$RES" = 'null' ]; then
    UNTRACK_CNT=$((UNTRACK_CNT + 1))
    if [ $UNTRACK_CNT -ge 2 ]; then
      echo lock
      exec_powershell ${LOCK_SCRIPT}
      # wait unlock
      while true; do
        sleep 10
        RES=$(exec_powershell ${ISLOCK_SCRIPT})
        if [ "${RES}" != "" ]; then
          break
        fi
      done
      UNTRACK_CNT=0
    else
      echo warn: UNTRACK_CNT=${UNTRACK_CNT}
    fi
  else
    UNTRACK_CNT=0
    echo running
  fi
done
```

30秒ごとにTogglへGETを打ち、2回連続でタイマ停止状態が返ってきた場合はPCをロックする。また、PCのロック解除を検知した場合、Togglへのポーリングを再開する。

Windowsのlockなどの操作はWSLから直接触ることができないので、PowerShellを経由している<span class="easy-footnote-margin-adjust" id="easy-footnote-2-640"></span><span class="easy-footnote">[<sup>2</sup>](https://komorinfo.com/blog/force-toggl-kit/#easy-footnote-bottom-2-640 "最初から全部PowerShell scriptにしておけばよかった気もするが、僕はPowerShellが苦手なので、主要部分はBashで作った。PowerShell何もわからない。")</span>。画面がロックされているかどうかの判定は、以下のQAを参考にした<span class="easy-footnote-margin-adjust" id="easy-footnote-3-640"></span><span class="easy-footnote">[<sup>3</sup>](https://komorinfo.com/blog/force-toggl-kit/#easy-footnote-bottom-3-640 "画面のロック判定は意外と難しいらしく、かなり苦戦した。Windows10以前とはロックの仕様が変わっていて、ググって出てきたサンプルコードの多くは手元の環境で動作しなかった。")</span>。

[c# – Check if Windows is currently locked – Stack Overflow](https://stackoverflow.com/questions/47393776/check-if-windows-is-currently-locked)

## 起動時にスクリプトをスタートさせる

最後に、作成したスクリプトが起動時に自動的に開始されるようにする。

Win+Rを押して、「ファイル名を指定して実行」ウィンドウで `shell:startup` と入力してOKを押す。

<figure class="wp-block-image size-large">![](https://komorinfo.com/wp-content/uploads/2020/11/image-4.png)</figure>explorerが起動するので以下のようなスクリプトを `force_toggl.bat` というファイル名で保存する。

```
@echo off
wsl -u root -- [[path to script]]/force_toggl.sh&
```

Windowsを再起動してログインし直せば、自動的にToggl監視スクリプトが開始される<span class="easy-footnote-margin-adjust" id="easy-footnote-4-640"></span><span class="easy-footnote">[<sup>4</sup>](https://komorinfo.com/blog/force-toggl-kit/#easy-footnote-bottom-4-640 "ポーリング間隔が間違っている等スクリプトにバグがあると、永久にログインできなくなるので注意（1敗）")</span>。
