---
author: komori-n
categories:
  - 技術解説
date: "2022-02-05T15:36:52+09:00"
keywords:
  - Docker
  - systemd
  - エスケープ
  - Proxy
  - HTTP_PROXY
title: systemd unit fileでは%のエスケープが必要
relpermalink: blog/systemd-unit-file-escape/
url: blog/systemd-unit-file-escape/
description: systemdのunit file内で`%`を使いたいときは`%%`とエスケープしなければならない。
---

systemdのunit file内で`%`を使いたいときは`%%`とエスケープしなければならない。

Proxy接続が必要な環境でDockerを使う状況を考える。[Docker公式ドキュメント](https://docs.docker.com/config/daemon/systemd/)では、`systemd`のunit configuration fileに環境変数を書く方法が説明されている。

serviceの起動時に環境変数`HTTP_PROXY`, `HTTPS_PROXY`を設定する。環境変数を自動で設定させるためには、`/etc/systemd/system/docker.service.d/http-proxy.conf`に以下のようなファイルを用意すればよい。

```conf
[Service]
Environment="HTTP_PROXY=http://proxy.example.com:80"
Environment="HTTPS_PROXY=http://proxy.example.com:80"
```

多くのシェルコマンドのProxy突破方法と同様に、`HTTP_PROXY`と`HTTPS_PROXY`に対しProxyのURLを設定する。dockerdは起動時にこれらの環境変数を参照し、指定されたProxyを介して通信を行うようになる。

URL、user、passwordの中に特殊文字が含まれている場合はエンコードが必要になる。例えば、次のような user/password のいずれかに特殊文字が含まれるケースを考える。

- URL｜<http://33.4.33.4:8080>
- User｜user
- PW｜p@ssword

passwordに特殊文字が含まれてるため、エンコードが必要になる。エンコードを行うと、設定すべき環境変数は`HTTP_PROXY=http://user:p%40ssword@33.4.33.4:8080`となる。

ここで、エンコードした文字列をそのままunit configuration fileに書いてもうまく行かない。

```sh
$ cat /etc/systemd/system/docker.service.d/http-proxy.conf
[Service]
Environment="HTTP_PROXY=http://user:p%40ssword@33.4.33.4:8080"
Environment="HTTPS_PROXY=http://user:p%40ssword@33.4.33.4:8080"
$ sudo systemctl daemon-reload
$ sudo systemctl restart docker
$ sudo systemctl show --property=Environment docker
Environment=
# ↑ Environment=HTTP_PROXY=http://... と表示されてほしい
```

実は、`%`はunit configuration file内ではSpecifierとして用いられる記号なので、さらにエスケープして`%%`と書く必要がある[^1]。

[^1]: [systemd.unit](https://www.freedesktop.org/software/systemd/man/systemd.unit.html)

```sh
$ cat /etc/systemd/system/docker.service.d/http-proxy.conf
[Service]
Environment="HTTP_PROXY=http://user:p%%40ssword@33.4.33.4:8080"
Environment="HTTPS_PROXY=http://user:p%%40ssword@33.4.33.4:8080"
$ sudo systemctl daemon-reload
$ sudo systemctl restart docker
$ sudo systemctl show --property=Environment docker
Environment=HTTP_PROXY=http://user:p%40ssword@33.4.33.4:8080 HTTPS_PROXY=http://user:p%40ssword@33.4.33.4:8080
```

このように、`%`を`%%`に置き換えればうまく環境変数を設定できる。

`HTTP_PROXY`はProxy環境で作業していればよく現れる作業であるが、普通のシェル上ではエスケープが不要なので、unit configuration fileでのエスケープはついつい忘れてしまいがちである。
