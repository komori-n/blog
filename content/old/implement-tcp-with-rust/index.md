---
author: komori-n
draft: true
categories:
  - プログラミング
date: "2021-05-08T15:14:28+09:00"
guid: https://komorinfo.com/blog/?p=1119
id: 1119
image: https://komorinfo.com/wp-content/uploads/2021/05/6329640559837184.jpg
og_img:
  - https://komorinfo.com/wp-content/uploads/2021/05/6329640559837184.jpg
permalink: /implement-tcp-with-rust/
tags:
  - Rust
title: 『Rustで始めるTCP自作入門』のWSLでの環境構築方法（手抜き工事）
url: implement-tcp-with-rust/
---

最近、 [Rustで始めるTCP自作入門：ひつじ技研](https://techbookfest.org/product/6562563816947712?productVariantID=5842153718677504) を読んでTCPを完全なる理解に至った。この本は素のUbuntu向けの環境構築方法しか記述されていないが、Docker for Windows(WSL2)を用いて**一応**動作させることができたのでその方法を紹介する。ただし、WSL特有の事情により`tc qdisc`を用いた仮想的な帯域制限はできない<span class="easy-footnote-margin-adjust" id="easy-footnote-1-1119"></span><span class="easy-footnote">[<sup>1</sup>](https://komorinfo.com/blog/implement-tcp-with-rust/#easy-footnote-bottom-1-1119 "<a href="https://github.com/microsoft/WSL/issues/6065">WSL2 seems not support traffic control by <code>tc qdisc</code> · Issue #6065 · microsoft/WSL</a>")</span>。

## 環境構築

まず、Docker上で動作させるためにセットアップスクリプト（[setup.sh](https://github.com/teru01/toytcp/blob/master/setup.sh)）を少し改造する。変更するポイントは以下の通りである。

- `sudo` を削除する
- `iptables` ではなく `iptables-legacy` を用いる

```
#!/bin/bash

set -eux

ip netns add host1
ip netns add router
ip netns add host2

ip link add name host1-veth1 type veth peer name router-veth1
ip link add name router-veth2 type veth peer name host2-veth1

ip link set host1-veth1 netns host1
ip link set router-veth1 netns router
ip link set router-veth2 netns router
ip link set host2-veth1 netns host2

ip netns exec host1 ip addr add 10.0.0.1/24 dev host1-veth1
ip netns exec router ip addr add 10.0.0.254/24 dev router-veth1
ip netns exec router ip addr add 10.0.1.254/24 dev router-veth2
ip netns exec host2 ip addr add 10.0.1.1/24 dev host2-veth1

ip netns exec host1 ip link set host1-veth1 up
ip netns exec router ip link set router-veth1 up
ip netns exec router ip link set router-veth2 up
ip netns exec host2 ip link set host2-veth1 up
ip netns exec host1 ip link set lo up
ip netns exec router ip link set lo up
ip netns exec host2 ip link set lo up

ip netns exec host1 ip route add 0.0.0.0/0 via 10.0.0.254
ip netns exec host2 ip route add 0.0.0.0/0 via 10.0.1.254
ip netns exec router sysctl -w net.ipv4.ip_forward=1

# drop RST
ip netns exec host1 iptables-legacy -A OUTPUT -p tcp --tcp-flags RST RST -j DROP
ip netns exec host2 iptables-legacy -A OUTPUT -p tcp --tcp-flags RST RST -j DROP

# turn off checksum offloading
ip netns exec host2 ethtool -K host2-veth1 tx off
ip netns exec host1 ethtool -K host1-veth1 tx off
```

次に、[rustの公式Dockerイメージ](https://hub.docker.com/_/rust) を改造して開発用のイメージを作る。やることは非常にシンプルで、必要パッケージを `apt` でインストールしてsetup.shをコンテナ内にコピーするだけである。

```
FROM rust

WORKDIR /work

RUN apt update && \
  apt install -y iptables ethtool netcat tcpdump iproute2

COPY setup.sh /tmp
```

本の中では素のUbuntuを想定しているため必要パッケージについては陽に触れられてはいないが、上記のパッケージさえ導入しておけば最後まで読み進めることができる。

あとは、コンテナをビルドして `--privilege` オプションをつけて起動し、`/tmp/setup.sh` のスクリプトを叩けばよい<span class="easy-footnote-margin-adjust" id="easy-footnote-2-1119"></span><span class="easy-footnote">[<sup>2</sup>](https://komorinfo.com/blog/implement-tcp-with-rust/#easy-footnote-bottom-2-1119 "<code>setup.sh</code> は <code>--privilege</code> がないと動作しないので、コンテナ起動後に手動で叩く必要がある")</span>。

```
$ docker build  -t toytcp .
$ docker run --privileged -v `pwd`:/work -it --rm toytcp
# /tmp/setup.sh
```
