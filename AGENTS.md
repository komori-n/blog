# Repository Guidelines

This is a personal blog site repository built with Hugo.

## Structure

- `content/posts/<####_slug>/index.md`: post content (page bundle style).
- `content/posts/<####_slug>/feature.png` (and related images): post assets.
- `config/_default/`: Hugo configuration.
- `layouts/` and `layouts/shortcodes/`: template and shortcode overrides.
- `assets/`: processed assets (for Hugo Pipes).
- `static/`: files copied to the output as-is.
- `py/`: small Python helper scripts.
- `tools/`: utility shell scripts (for example link checks).

Generated output lives in `public/` and `resources/_gen/`; do not edit generated files manually.

## Build, Test, and Development Commands

- `hugo server -D --baseURL http://localhost`: run local dev server and include draft posts.
- `hugo --gc --minify`: production-style build with cleanup/minification.
- `./tools/internal_link_check.sh`: build then run internal link validation (`hyperlink public`).
- `export PRE_COMMIT_HOME="$PWD/.cache/pre-commit" pre-commit run -a`: run all configured checks/formatters.

Note: this site uses a GitHub shortcode that fetches repository metadata at build time. `hugo` builds may fail in network-restricted environments if `api.github.com` is unreachable.

## Coding Style & Naming Conventions

- Use page bundles for posts: `content/posts/0007_example-post/index.md`.
- Keep slugs kebab-case; keep numeric prefixes zero-padded.
- Write front matter in YAML and keep key naming consistent (`title`, `date`, `tags`, `keywords`, `description`, `url`).
- Respect pre-commit formatting rules: YAML normalization (`yamlfmt`), no trailing whitespace, and consistent line endings.

## Testing Guidelines

There is no dedicated unit-test framework in this repository. Validation is build-and-check based:
1. Run the three commands listed in "Build, Test, and Development Commands" in that order.
2. If the `hugo` step fails in restricted environments, verify external access to `api.github.com`.

For content/template changes, also verify the rendered page locally with `hugo server -D`.
