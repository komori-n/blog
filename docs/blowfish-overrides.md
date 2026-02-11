# Blowfish Override Catalog

最終更新: 2026-02-11  
対象テーマ: `themes/blowfish` (`v2.97.0`)

このドキュメントは、次回 Blowfish 更新時に衝突しやすい「ローカル override」を把握するためのメモです。

## 1. テンプレート override 一覧（同パス上書き）

### `layouts/_default/terms.html`
- 変更点:
  - `.Content` に `emojify` を適用
  - ターム一覧を `.Data.Terms.ByCount`（件数降順）で表示
- 目的:
  - taxonomy 画面の絵文字表示
  - タグ/カテゴリを利用頻度順で見せる
- リスク: 中
- 更新時チェック:
  - taxonomy 一覧の並び順が件数降順のままか
  - taxonomy 本文の絵文字が崩れないか

### `layouts/_default/term.html`
- 変更点:
  - `.Content` に `emojify` を適用
- 目的:
  - term ページ本文で絵文字表示を維持
- リスク: 低
- 更新時チェック:
  - term ページ本文の絵文字変換

### `layouts/_default/index.json`
- 変更点（上流との差分が大きい）:
  - 出力フィールド構成を独自化（`externalUrl` / `type` なし）
  - `summary` / `content` の加工ロジックを独自化
  - `excludeFromSearch` 判定なし
  - `where $index "content" "!=" ""` で絞り込み
- 目的:
  - 検索インデックスの互換維持（過去仕様に合わせた形）
- リスク: 高
- 更新時チェック:
  - サイト内検索のヒット件数、タイトル、概要表示
  - JA/EN 両言語で検索が機能するか

### `layouts/partials/recent-articles/main.html`
- 変更点:
  - `showMoreLink` の URL 連結を独自化
  - ボタン文言に `emojify` を適用
  - ボタンクラスを一部変更（hover 色）
- 目的:
  - `showMoreLinkDest` の言語別 URL 生成を安定化
  - 見た目調整
- リスク: 中
- 更新時チェック:
  - トップの「もっと見る」リンク先が期待通りか
  - 言語切替時にリンクが壊れないか

### `layouts/partials/schema.html`
- 変更点（SEO 影響あり）:
  - author 名を `Site.Params.Author.name` 未設定時に `Site.Title` へ fallback
  - 記事のみ JSON-LD を出力（`else if .IsPage`）
  - `abstract`（Summary）を追加
  - `keywords` を `tags` + `keywords` で合成
  - 上流の `enableStructuredBreadcrumbs` 対応を未採用
- 目的:
  - 運用中サイトの構造化データ互換維持
- リスク: 高
- 更新時チェック:
  - 構造化データエラー（Article/WebSite）
  - パンくずの構造化データ要否（必要なら上流実装を再取り込み）

### `layouts/partials/vendor.html`
- 変更点:
  - KaTeX auto-render の delimiter 設定を独自追加（`$...$`, `\(...\)`, `\[...\]`, `\begin{align}...`）
- 目的:
  - 既存記事の数式記法との互換維持
- リスク: 中
- 更新時チェック:
  - インライン数式と display 数式の崩れ
  - `\begin{align}` ブロックの描画

### `layouts/shortcodes/article.html`
- 変更点:
  - `link` 引数を `relURL` で解決
- 目的:
  - 相対リンク shortcode の安定化
- リスク: 低
- 更新時チェック:
  - `article` shortcode の内部リンク遷移

### `layouts/shortcodes/comment.html`（独自追加）
- 変更点:
  - shortcode 本体を no-op 化（実質コメントアウト用途）
- 目的:
  - 記事内の一時コメントを非表示にする運用
- リスク: 低
- 更新時チェック:
  - 本番 HTML に不要文が混入していないか

## 2. テーマ拡張（override ではないが依存度が高い）

### `assets/css/schemes/komori.css`
- 独自カラースキーム（`colorScheme = "komori"` 前提）
- リスク: 中
- 更新時チェック:
  - Light/Dark で本文・リンク・コードが可読か

### `assets/css/custom.css`
- 追加スタイル:
  - 見出し/リスト余白
  - KaTeX overflow
  - ヘッダータイトルのサイズ調整
  - inline code と code block（dark 含む）配色
- リスク: 中
- 更新時チェック:
  - ヘッダー DOM 変更時にタイトル CSS が無効化されないか
  - コード配色が可読性を維持できているか

## 3. 設定面での注意（次回更新時の確認ポイント）

### `config/_default/params.toml`
- 依存が強い値:
  - `colorScheme = "komori"`
  - `homepage.layout = "background"`
  - `article.heroStyle = "background"`
  - `enableA11y = true`
- 注意:
  - `enableStructuredBreadcrumbs` は現 override の `schema.html` では未使用
  - `giteaDefaultServer` / `forgejoDefaultServer` は shortcode 未使用なら不要

### `config/_default/config.toml`
- 依存が強い値:
  - `hasCJKLanguage = true`
  - `pagination.pagerSize = 10`
  - `outputs.home = ["HTML", "RSS", "JSON"]`（`index.json` 前提）

### `config/_default/module.toml`
- 現状 `min = "0.87.0"` は古い。
- Hugo 実運用バージョン更新時は整合させること。

## 4. 次回 Blowfish 更新時の推奨手順

1. まずテーマ更新（submodule / module）
2. 下記 override を上流と比較し、差分を再適用
   - `layouts/_default/index.json`
   - `layouts/partials/schema.html`
   - `layouts/partials/vendor.html`
   - `layouts/partials/recent-articles/main.html`
3. 次に残り override（`terms.html`, `term.html`, `article.html`）を追従
4. 最後に CSS/設定を確認

比較コマンド例:

```bash
# override 一覧確認
find layouts -type f | sort | while read -r f; do
  rel="${f#layouts/}"
  if [ -f "themes/blowfish/layouts/$rel" ]; then
    echo "OVERRIDE layouts/$rel"
  fi
done

# 個別差分確認

diff -u themes/blowfish/layouts/partials/schema.html layouts/partials/schema.html
```

## 5. 回帰確認ページ（最低限）

- ホーム: `/`
  - プロフィール表示、最近の記事、`showMoreLink` の遷移
- taxonomy 一覧: `/tags/`, `/categories/`
  - 件数降順ソート、絵文字表示
- term ページ: 代表的なタグ1つ
  - 本文絵文字、カード表示
- 数式記事:
  - `content/posts/0002_compile-time-pi/index.md`
  - `content/posts/0006_calculate-mean-and-variance-incrementally/index.md`
- 動画 shortcode 記事:
  - `content/posts/old/2021-07-12-wio-terminal-iot-button/index.md`
- 検索:
  - 検索 UI で JA/EN の記事がヒットするか

## 6. リスク優先度（更新時の確認順）

1. 高: `layouts/_default/index.json`, `layouts/partials/schema.html`
2. 中: `layouts/partials/vendor.html`, `layouts/partials/recent-articles/main.html`, `assets/css/custom.css`, `assets/css/schemes/komori.css`
3. 低: `layouts/_default/terms.html`, `layouts/_default/term.html`, `layouts/shortcodes/article.html`, `layouts/shortcodes/comment.html`
