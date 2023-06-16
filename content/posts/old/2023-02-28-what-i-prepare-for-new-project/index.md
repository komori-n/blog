---
author: komori-n
draft: true
categories:
  - プログラミング
date: "2023-02-28T21:30:00+09:00"
guid: https://komorinfo.com/blog/?p=2015
id: 2015
permalink: /what-i-prepare-for-new-project/
tags:
  - C/C++
title: リポジトリ立ち上げ時に用意するファイル一覧メモ
url: what-i-prepare-for-new-project/
---

新しくリポジトリを立ち上げるときに用意するファイルに関する個人的なメモ。

## 共通

### README.md

やるだけ。最低でもプロジェクトの概要、フォルダ構成、ライセンス、コントリビュート方法を書く。

### .gitignore

[gitignore.io](https://www.toptal.com/developers/gitignore)を参考にやるだけ。

### LICENSE

オープンソースプロジェクトの場合は必須。GPLやMITなどライセンスを決めて書く。[license-generator – crates.io: Rust Package Registry](https://crates.io/crates/license-generator)のようなツールを使うと早い。

### pre-commit

<figure class="wp-block-image size-large">![](https://komorinfo.com/wp-content/uploads/2023/02/image-1024x465.jpg)</figure>[pre-commit](https://pre-commit.com)は、コミット時にファイルのチェックを行うツールである。行末のスペースやマークダウンの書き方など、コミットしようとしているファイルを自動で直してくれる。pre-commitを導入することでチェック項目がへるため、コードレビュー時の負荷を減らすことができる。

pre-commitという名前であるが、コミットメッセージのチェックにも使うことができる。特に、[compilerla/conventional-pre-commit](https://github.com/compilerla/conventional-pre-commit)を導入すれば、post-commit時にコミットメッセージのチェックができ、便利である。

pre-commitには使用可能なフォーマッタが多く存在し、[公式サイトのSupported hooks](https://pre-commit.com/hooks.html)でその一覧を確認できる。どのフォーマッタを選択すればいいか迷う場合は、pre-commit/pre-commit-hooksを参考にすればよい。言語やメンバのスキルレベルに応じてフォーマッタを適宜導入すればよい。

pre-commitは、クローンするだけでは有効にならない。ローカルで`pre-commit install`を実行して、フックを有効化する必要がある。複数人で作業する場合、pre-commitフックのインストール／アンインストール用のスクリプトを作っておくとよい。

## C/C++関係

### clang-format

[clang-format](https://clang.llvm.org/docs/ClangFormat.html)はC/C++/Objective-Cの自動フォーマットツールである。コンフィグファイルの内容に従い、インデントや空白などを自動で整形することができる。機械的にフォーマットチェックと整形を行えるので、CTでチェックをかけることでコードの属人性を排除することができる。

clang-formatは、設定ファイル`.clang-format`により整形方法をカスタマイズすることができる。例えば、関数開始時の改行や括弧の前後のスペース、`&`や`*`の位置など細かいルールを設定することができる。`.clang-format` を書く際は、[Clang Format Editor (compatible with Clang 13) – pystyle](https://pystyle.info/apps/clang-format-editor/) のようなサイトを利用すると便利である。

普段使用しているコンフィグファイルはこんな感じ。

```
---
Language:        Cpp
# BasedOnStyle:  Chromium
AccessModifierOffset: -1
AlignAfterOpenBracket: Align
AlignConsecutiveMacros: false
AlignConsecutiveAssignments: false
AlignConsecutiveDeclarations: false
AlignEscapedNewlines: Left
AlignOperands:   true
AlignTrailingComments: true
AllowAllArgumentsOnNextLine: true
AllowAllConstructorInitializersOnNextLine: true
AllowAllParametersOfDeclarationOnNextLine: false
AllowShortBlocksOnASingleLine: Never
AllowShortCaseLabelsOnASingleLine: false
AllowShortFunctionsOnASingleLine: Inline
AllowShortLambdasOnASingleLine: All
AllowShortIfStatementsOnASingleLine: Never
AllowShortLoopsOnASingleLine: false
AlwaysBreakAfterDefinitionReturnType: None
AlwaysBreakAfterReturnType: None
AlwaysBreakBeforeMultilineStrings: true
AlwaysBreakTemplateDeclarations: Yes
BinPackArguments: true
BinPackParameters: false
BraceWrapping:
  AfterCaseLabel:  false
  AfterClass:      false
  AfterControlStatement: false
  AfterEnum:       false
  AfterFunction:   false
  AfterNamespace:  false
  AfterObjCDeclaration: false
  AfterStruct:     false
  AfterUnion:      false
  AfterExternBlock: false
  BeforeCatch:     false
  BeforeElse:      false
  IndentBraces:    false
  SplitEmptyFunction: true
  SplitEmptyRecord: true
  SplitEmptyNamespace: true
BreakBeforeBinaryOperators: None
BreakBeforeBraces: Attach
BreakBeforeInheritanceComma: false
BreakInheritanceList: BeforeColon
BreakBeforeTernaryOperators: true
BreakConstructorInitializersBeforeComma: false
BreakConstructorInitializers: BeforeColon
BreakAfterJavaFieldAnnotations: false
BreakStringLiterals: true
ColumnLimit:     120
CommentPragmas:  '^ IWYU pragma:'
CompactNamespaces: false
ConstructorInitializerAllOnOneLineOrOnePerLine: true
ConstructorInitializerIndentWidth: 4
ContinuationIndentWidth: 4
Cpp11BracedListStyle: true
DeriveLineEnding: true
DerivePointerAlignment: false
DisableFormat:   false
ExperimentalAutoDetectBinPacking: false
FixNamespaceComments: true
ForEachMacros:
  - foreach
  - Q_FOREACH
  - BOOST_FOREACH
IncludeBlocks:   Preserve
IncludeCategories:
  - Regex:           '^<ext/.*\.h>'
    Priority:        2
    SortPriority:    0
  - Regex:           '^<.*\.h>'
    Priority:        1
    SortPriority:    0
  - Regex:           '^<.*'
    Priority:        2
    SortPriority:    0
  - Regex:           '.*'
    Priority:        3
    SortPriority:    0
IncludeIsMainRegex: '([-_](test|unittest))?$'
IncludeIsMainSourceRegex: ''
IndentCaseLabels: true
IndentGotoLabels: true
IndentPPDirectives: None
IndentWidth:     2
IndentWrappedFunctionNames: false
JavaScriptQuotes: Leave
JavaScriptWrapImports: true
KeepEmptyLinesAtTheStartOfBlocks: false
MacroBlockBegin: ''
MacroBlockEnd:   ''
MaxEmptyLinesToKeep: 1
NamespaceIndentation: None
ObjCBinPackProtocolList: Never
ObjCBlockIndentWidth: 2
ObjCSpaceAfterProperty: false
ObjCSpaceBeforeProtocolList: true
PenaltyBreakAssignment: 2
PenaltyBreakBeforeFirstCallParameter: 1
PenaltyBreakComment: 300
PenaltyBreakFirstLessLess: 120
PenaltyBreakString: 1000
PenaltyBreakTemplateDeclaration: 10
PenaltyExcessCharacter: 1000000
PenaltyReturnTypeOnItsOwnLine: 200
PointerAlignment: Left
RawStringFormats:
  - Language:        Cpp
    Delimiters:
      - cc
      - CC
      - cpp
      - Cpp
      - CPP
      - 'c++'
      - 'C++'
    CanonicalDelimiter: ''
    BasedOnStyle:    google
  - Language:        TextProto
    Delimiters:
      - pb
      - PB
      - proto
      - PROTO
    EnclosingFunctions:
      - EqualsProto
      - EquivToProto
      - PARSE_PARTIAL_TEXT_PROTO
      - PARSE_TEST_PROTO
      - PARSE_TEXT_PROTO
      - ParseTextOrDie
      - ParseTextProtoOrDie
    CanonicalDelimiter: ''
    BasedOnStyle:    google
ReflowComments:  true
SortIncludes:    true
SortUsingDeclarations: true
SpaceAfterCStyleCast: false
SpaceAfterLogicalNot: false
SpaceAfterTemplateKeyword: true
SpaceBeforeAssignmentOperators: true
SpaceBeforeCpp11BracedList: false
SpaceBeforeCtorInitializerColon: true
SpaceBeforeInheritanceColon: true
SpaceBeforeParens: ControlStatements
SpaceBeforeRangeBasedForLoopColon: true
SpaceInEmptyBlock: false
SpaceInEmptyParentheses: false
SpacesBeforeTrailingComments: 2
SpacesInAngles:  false
SpacesInConditionalStatement: false
SpacesInContainerLiterals: true
SpacesInCStyleCastParentheses: false
SpacesInParentheses: false
SpacesInSquareBrackets: false
SpaceBeforeSquareBrackets: false
Standard:        Auto
StatementMacros:
  - Q_UNUSED
  - QT_REQUIRE_VERSION
TabWidth:        8
UseCRLF:         false
UseTab:          Never
```

### clang-tidy

[clang-tidy](https://clang.llvm.org/extra/clang-tidy/)は、C++を静的に解析して、バグの可能性やコーディング規約違反を検出してくれるツールである。標準ライブラリの使い方から変数名の付け方に至るまで、かなり幅広い項目の指摘を行ってくれる。C++上級者でも気づきづらいミスを教えてくれることもあるため、導入しておいて損はない。

普段使用しているコンフィグファイルはこんな感じ。デフォルトだとかなりうるさく指摘してくるので、不要だと思うチェック項目は `-` で除外して運用するのが良い。

```
---
Checks: >
  bugprone-*,
  cppcoreguidelines-*
  google-*,
  misc-*,
  modernize-*,
  performance-*,
  portability-*,
  readability-*,
  -bugprone-easily-swappable-parameters,
  -misc-no-recursion,
  -modernize-avoid-c-arrays,
  -modernize-use-nodiscard,
  -modernize-use-trailing-return-type,
  -readability-convert-member-functions-to-static,
  -readability-else-after-return,
  -readability-identifier-length,
  -readability-named-parameter,
  -readability-magic-numbers,
  -readability-qualified-auto,

# Turn all the warnings from the checks above into errors.
WarningsAsErrors: "*"

HeaderFilterRegex: "(google/cloud/|generator/).*\\.h$"

CheckOptions:
  - { key: readability-identifier-naming.NamespaceCase, value: lower_case }
  - { key: readability-identifier-naming.ClassCase, value: aNy_CasE }
  - { key: readability-identifier-naming.StructCase, value: aNy_CasE }
  - {
      key: readability-identifier-naming.TemplateParameterCase,
      value: CamelCase,
    }
  - {
      key: readability-identifier-naming.ValueTemplateParameterCase,
      value: CamelCase,
    }
  - {
      key: readability-identifier-naming.ValueTemplateParameterPrefix,
      value: k,
    }
  - { key: readability-identifier-naming.FunctionCase, value: aNy_CasE }
  - { key: readability-identifier-naming.VariableCase, value: lower_case }
  - { key: readability-identifier-naming.ClassMemberCase, value: lower_case }
  - { key: readability-identifier-naming.ClassMemberSuffix, value: _ }
  - { key: readability-identifier-naming.PrivateMemberSuffix, value: _ }
  - { key: readability-identifier-naming.ProtectedMemberSuffix, value: _ }
  - { key: readability-identifier-naming.EnumConstantCase, value: CamelCase }
  - { key: readability-identifier-naming.EnumConstantPrefix, value: k }
  - {
      key: readability-identifier-naming.ConstexprVariableCase,
      value: CamelCase,
    }
  - { key: readability-identifier-naming.ConstexprVariablePrefix, value: k }
  - {
      key: readability-implicit-bool-conversion.AllowIntegerConditions,
      value: 1,
    }
  - {
      key: readability-implicit-bool-conversion.AllowPointerConditions,
      value: 1,
    }
  - { key: readability-function-size.NestingThreshold, value: 7 }
  - { key: readability-function-size.StatementThreshold, value: 300 }
  - { key: readability-function-cognitive-complexity.Threshold, value: 30 }
```

### CPPLINT

[cpplint](https://github.com/cpplint/cpplint)はC/C++の静的コード解析ツールで、clang-formatやclang-tidyでチェックしきれない細かなミスを検出できる。例えば、標準ライブラリのincludeの過不足やincludeの並び順、インクルードガードの命名規則などを指摘してくれる。

```
filter=-legal/copyright
filter=-runtime/references
filter=-build/header_guard
filter=-build/c++11
filter=-build/include
filter=-whitespace/braces
filter=-whitespace/parens
filter=-whitespace/newline
filter=-readability/nolint
linelength=120
```
