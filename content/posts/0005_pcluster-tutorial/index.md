---
author: komori-n
categories:
  - やってみた
date: 2023-11-26T20:25:38+09:00
tags:
  - TBD
keywords:
  - ParallelCluster
title: (TBD) AWS ParallelClusterで
relpermalink: blog/pcluster-tutorial
url: blog/pcluster-tutorial
description: TBD
---

## 概要

**AWS ParallelCluster**はAWSが開発するHPCクラスタの管理ツールである。

## クラスタ構築

以下では、AWS ParallelCluster CLIを使用する。
ParallelCluster CLIのインストール方法については、
[AWS公式ドキュメント](https://docs.aws.amazon.com/ja_jp/parallelcluster/latest/ug/install-v3-parallelcluster.html)
を参照。

まず、`pcluster configure`コマンドによりクラスタ構築用のコンフィグを生成する。

```sh
pcluster configure --config cluster-config.yaml
```

上記コマンドを実行すると、Region IDやInstance Typeなどを質問される。
それに対し答えていくことで、クラスタ構築用のコンフィグファイル（`.yaml`）を構築してくれる。

```txt
# Region IDはどうするか
AWS Region ID [us-east-1]:
# EC2の鍵をどうするか（AWSに登録したことがある鍵から選べる）
EC2 Key Pair Name [test]:
# OS（OSによってアーキテクチャに差があったり料金に差があったりするので注意）
Operating System [alinux2]:

# ログインノードのInstance Type。
# Queueで使用するInstance TypeとCPUアーキテクチャ（x86_64, arm64, ...）を合わせる必要がある。
Head node instance type [t2.micro]:
# 作成するキューの個数
Number of queues [1]:

# 1個目のキューの名前
Name of queue 1 [queue1]:
# queue1に割り当てるCompute Resourcesの種類数
Number of compute resources for queue1 [1]:
# queue1にのCompute Resource 1で使用するInstance Type
Compute instance type for compute resource 1 in queue1 [t2.micro]:
# ↑ の最大同時起動数
Maximum instance count [10]:
```

`pcluster configure`のすべての質問に答えると、次のようなyamlファイルが生成される。

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
