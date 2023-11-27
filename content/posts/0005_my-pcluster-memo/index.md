---
author: komori-n
categories:
  - やってみた
date: 2023-11-27T21:27:27+09:00
tags:
  - AWS
keywords:
  - ParallelCluster
  - 大規模
  - 数値計算
  - メモ
title: AWS ParallelClusterの使い方メモ
relpermalink: blog/my-pcluster-memo
url: blog/my-pcluster-memo
description: AWS ParallelClusterの環境構築方法と簡単な使い方をまとめたページ。
---

1年に1回ぐらいのペースでAWS
ParallelClusterを用いて大規模な数値実験をする機会があるが、
その度に苦戦している気がするので自分用のメモを残しておく。

## クラスタ構築

AWS ParallelClusterを構築する方法には、
大きく分けてCLIを用いる方法とGUIを用いる方法がある。
本ページでは、AWS ParallelCluster CLIを用いた構築方法を紹介する。
ParallelCluster CLIのインストール方法については、
[AWS公式ドキュメント](https://docs.aws.amazon.com/ja_jp/parallelcluster/latest/ug/install-v3-parallelcluster.html)
を参照すること。

まず、次のコマンドを使用してクラスタ用の設定ファイルを生成する。

```sh
pcluster configure --config cluster-config.yaml
```

このコマンドを実行すると、リージョンIDやインスタンスタイプなどに関する質問が表示される。
それに対して回答していくことで、クラスタの構築に必要な設定ファイル（`.yaml`）が生成される。

たとえば、設定ファイルの生成時には、次のような質問が表示される。

```txt
# リージョンIDを何にするか
AWS Region ID [us-east-1]:
# 使用するEC2キーペアを入力する（AWSに登録したことがある鍵から選べる）
EC2 Key Pair Name [test]:
# 使用するOSを選ぶ。OSによって料金が異なる場合があるので注意。
Operating System [alinux2]:

# ヘッドノードのインスタンスタイプを何にするか
Head node instance type [t2.micro]:
# 作成するキューの数をいくつにするか
Number of queues [1]:

# 1個目のキューの名前を何にするか
Name of queue 1 [queue1]:
# queue1に割り当てるコンピュートリソースの数をいくつにするか
Number of compute resources for queue1 [1]:
# queue1のコンピュートリソース1で使用するインスタンスタイプは何にするか
Compute instance type for compute resource 1 in queue1 [t2.micro]:
# インスタンスの最大同時起動数をいくつにするか
Maximum instance count [10]:
```

ヘッドノード（ログイン用のノード）とコンピュートリソースのインスタンスタイプは、
CPUアーキテクチャ（arm64, x86_64など）を一致させる必要がある。
たとえば、ヘッドノードをt4g.micro（arm64）に設定し、
queue1に割り当てるインスタンスをr5.xlarge（x86_64）に設定することはできない。

`pcluster configure`の質問にすべて答えると、次のようなyamlファイルが生成される。

```yaml
Region: us-east-1
Image:
  Os: alinux2
HeadNode:
  InstanceType: t2.nano
  Networking:
    SubnetId: subnet-0123456789abcdef0
  Ssh:
    KeyName: test
Scheduling:
  Scheduler: slurm
  SlurmQueues:
    - Name: queue1
      ComputeResources:
        - Name: t2micro
          Instances:
            - InstanceType: r5.xlarge
          MinCount: 0
          MaxCount: 10
      Networking:
        SubnetIds:
          - subnet-0123456789abcdef0
```

## クラスタ起動とビルド

生成したyamlファイルを用いて、次のコマンドを実行するとクラスタを起動できる。

```sh
pcluster create-cluster \
  --cluster-configuration cluster-config.yaml \
  --cluster-name my-cluster --region us-east-1
```

クラスタの起動状態は次のコマンドで確認できる。

```sh
pcluster list-clusters
```

起動が完了すると、`clusterStatus`が"CREATE_COMPLETE"に変化する。
クラスタの起動には数分かかるため、気長に待つ必要がある。

## ジョブ投入

クラスタが起動したら、次のコマンドによりヘッドノードへSSH接続する。

```sh
pcluster ssh -n my-cluster -i ~/.ssh/test.pem
```

ここで、`~/.ssh/test.pem`にはAWSのSSH鍵（`pcluster configure`で設定したもの）のパスを指定する。

SSH接続先からクラスタへジョブを投入できる。
クラスタのスケジューラにslurm（デフォルト値）を選んだとき、たとえば次のようなスクリプトを作成してキューへ渡す。

```sh
#!/bin/bash
#SBATCH --time 48:00:00      ← ジョブの制限時間
#SBATCH --partition queue1   ← 投入するキュー
#SBATCH --nodes 1            ← 使用するノード数
#SBATCH --cpus-per-task 4    ← 1プロセスあたりのCPU数
#SBATCH --output %x-%j.log   ← 標準出力の出力先ファイル
#SBATCH --error %x-%j.log    ← 標準エラー出力の出力先ファイル

# 実行したいプログラム本体を呼び出すコード
kh-playground/source/KomoringHeights-by-gcc << END
usi
setoption name Threads value `nproc`
setoption name USI_Hash value 29000
setoption name PostSearchLevel value UpperBound
setoption name PvInterval value 10000
isready
sfen 4k4/9/9/9/9/9/9/9/9 b B4G2S9P2rb2s4n4l9p 1
go mate infinite
wait
quit
END
```

スクリプトの冒頭のコメントではジョブに関する設定をしている。
ここでは、たとえばジョブの制限時間やCPU数、ログの出力先などを設定できる。
ファイル内に設定できるパラメータは`sbatch`（後述）で設定できる引数と同じである。

上記のスクリプトは、次のコマンドを使用してキューへジョブを投入できる。

```sh
$ sbatch 01.sh
Submitted batch job 1
```

`sbatch`コマンドではリソース値の設定やログ出力先などさまざまな項目を設定できる。
詳細な設定可能項目については
[slurmの公式ドキュメント](https://slurm.schedmd.com/sbatch.html)
を参照すること。

現在のインスタンス状態の一覧は、次のコマンドで確認できる。

```sh
$ squeue
  JOBID PARTITION     NAME     USER ST       TIME  NODES NODELIST(REASON)
      1    queue1    01.sh ec2-user CF       0:02      1 queue1-dy-r5xlarge-1
```

インスタンスの状態が`ST=CF`の場合、インスタンスの起動を待っていることを意味している。
ジョブを投入した際に実行可能なインスタンスがなく、
まだ起動できるインスタンス数に余裕がある場合、
新たにインスタンス（EC2ノード）が起動される。
ノードが実行可能になって実行状態に移行すると、状態が`ST=R`に代わり、
スクリプトの実行が開始される。
