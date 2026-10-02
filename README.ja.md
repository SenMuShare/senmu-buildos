# Senmu BuildOS — Agent Skills for Codex & Claude Code

**プロジェクトを理解し、使えるものを再利用し、結果を確かめる。**

[简体中文](README.md) · [English](README.en.md) · [日本語](README.ja.md)

Senmu BuildOS は、実際のソフトウェア開発に使う AI エージェント向け Skills です。既存の実装と要件・制約を理解し、コードや成熟したコンポーネントを再利用して、適切なテストと成果物の証拠で結果を確認するための指針を提供します。要件、UI/UX、設計、デバッグ、コードレビュー、リリースを支援しつつ、小さな修正に全工程を強制しません。

**1 つのプラグインに、必要なときだけ使う 8 つの能力。既存の仕組みを活かし、小さな変更は軽く進めます。**

[![License](https://img.shields.io/github/license/SenMuShare/senmu-buildos)](LICENSE) [![Public release](https://img.shields.io/github/v/release/SenMuShare/senmu-buildos?label=public%20release)](https://github.com/SenMuShare/senmu-buildos/releases/latest)

[クイックスタート](#quickstart) · [最初に試すこと](#first-use) · [8 つの能力](#skills) · [よくある質問](#faq) · [更新と削除](#maintenance)

<a id="quickstart"></a>
## クイックスタート

プラグインに対応した Codex または Claude Code と、ローカルで利用できる Git・Node.js を用意してください。有効化の前に [Hooks](hooks/hooks.json) と[セキュリティ説明](SECURITY.md)を確認し、確認済みの配布元だけを信頼してください。

### Codex

```bash
codex plugin marketplace add SenMuShare/senmu-buildos
codex plugin add senmu-buildos@senmu-buildos
codex plugin list
```

クライアントを更新表示し、プロジェクトで新しい会話を開始します。一覧の配布元とバージョンを確認してから、下のタスクを試してください。

### Claude Code

```bash
claude plugin marketplace add SenMuShare/senmu-buildos
claude plugin install senmu-buildos@senmu-buildos
claude plugin list
```

新しいセッションを開始するか、現在のセッションで `/reload-plugins` を実行します。`/plugin` の Installed タブで状態を確認してください。プロジェクト指示の互換性とトラブルシューティングは [Claude Code アダプター](adapters/claude-code/README.md)にあります。

これらのコマンドは**公開マーケットプレイスで提供されている版**をインストールします。このソースの版と同じとは限りません。非公開の配布物には、それぞれの許可と導入手順を適用してください。インストール、現在のセッションへの読み込み、実際のタスク動作は別々に確認します。コマンドの差異はクライアントの `--help`、[Codex リファレンス](https://developers.openai.com/codex/cli/reference/)、[Claude Code ドキュメント](https://code.claude.com/docs/en/discover-plugins)で確認できます。

<details>
<summary>豆包、WorkBuddy、ZCode と Skill のみの導入</summary>

各アダプターは同じ 8 つの専門能力を使いますが、Skill のコピーはライフサイクル Hook の導入と同じではありません。信頼できるソースを取得し、`skills/` と `adapters/` がある製品ルートで操作してください。Python アダプターには Python 3 が必要です。次の clone コマンドは公開リポジトリを取得します。

```bash
git clone https://github.com/SenMuShare/senmu-buildos.git
cd senmu-buildos
```

| ホスト | 先にプレビュー | 確認後の導入と説明 |
| --- | --- | --- |
| 豆包 | `python3 adapters/doubao/install_doubao.py --dry-run` | `python3 adapters/doubao/install_doubao.py`；[保存先と削除](adapters/doubao/README.md) |
| WorkBuddy | `python3 adapters/workbuddy/install_workbuddy.py --dry-run` | `python3 adapters/workbuddy/install_workbuddy.py --scope user`；[プロジェクト単位の導入と削除](adapters/workbuddy/README.md) |
| ZCode | `python3 adapters/zcode/install_zcode.py --dry-run` | `python3 adapters/zcode/install_zcode.py --with-kernel`；[プラグイン方式と削除](adapters/zcode/README.md) |

ZCode のプラグイン管理では、市場 `https://github.com/SenMuShare/senmu-buildos` を追加して導入することもできます。導入後は新しいセッションを開始してください。Skill のみの経路は設定に応じた呼び出し可能な案内能力を提供しますが、毎回の自動注入を保証しません。複数のコピーを重複して導入しないでください。

</details>

<a id="first-use"></a>
## 最初に試すこと

プロジェクトを開き、実際に必要なタスクを 1 つ選んでください。Skill 名を覚える必要はありません。以下は入力例であり、結果の保証ではありません。

### 1. 既存プロジェクトを変更せずに理解する

> このプロジェクトを読み取り専用で調べてください。実行入口、現在のルール、テストコマンドを特定し、この要件で再利用できるものを説明してください。まだコードは変更しないでください。

**確認する結果：** 実在するパス、現在の制約、再利用候補、不明点が示され、別の管理ディレクトリや依頼していない変更が作られていないこと。

### 2. 繰り返し発生する不具合を直す

> 元の症状を再現し、原因を確かめてから、必要最小限の修正をしてください。元の経路と影響する回帰テストで検証し、再現できなかった部分は明示してください。

**確認する結果：** 仮説と証拠が区別され、変更箇所、実行したコマンド、未検証の範囲が示されること。「たぶん直った」だけで終わらないこと。

### 3. 既存コードに機能を追加する

> 要件の範囲と完了条件を確認し、既存の構造とコンポーネントを再利用して、小さな単位で実装・検証してください。依頼していない機能は追加しないでください。

**確認する結果：** 要件と変更が対応し、再利用の理由が分かり、完了した作業と検証待ちの作業が分けて示されること。

要件文書の作成・更新では、機能ごとの対象バージョンと「背景・要件、機能、業務ロジック、例外を含む画面操作」の4区分を維持します。関連するプロトタイプや UI は、採用範囲と具体的な要件を紐付けます。画像がなければ作成を強制せず、利用者が明示した別形式を優先します。[要件記述と設計資料の関連付け](skills/senmu-build-product/references/product-requirements-and-iteration.md#21-per-feature-requirement-contract)を参照してください。

レビューには「要件を満たしているかと、コード品質に問題がないかを別々に確認してください」と依頼できます。外部管理画面の操作には「私にしかできない操作を、途中から再開できる手順にしてください」と依頼してください。能力を明示して使う場合は[一覧](#skills)から入口を確認できます。

<a id="why"></a>
## どんな問題に役立つか

| よくある問題 | BuildOS の進め方 | 確認したい結果 |
| --- | --- | --- |
| 要件を理解する前にコードを書き、目的から外れる | 範囲、対象外、完了条件を先に確認する | 余分な機能ではなく、要件に対応した実装 |
| 既存の部品や状態を調べず、同じものを作る | プロジェクト、フレームワーク、部品の能力を先に調べる | 必要な変更と、再利用する理由 |
| 修正のたびに複雑になり、保守しづらくなる | 原因、責任、呼び出し元を追い、実際の振る舞いを検証する | 根拠のある修正、明確な境界、回帰結果 |
| 会話が変わると推測からやり直し、テスト成功を公開完了と扱う | 判断、進捗、証拠を既存の管理場所に残す | 再開できる作業と、実装・受入・公開の正確な状態 |

個人開発者、プロダクトを作る人、小規模チームが実際のプロジェクトを継続して保守する場面を想定しています。コード生成器やホスティングされた実行基盤ではなく、文書や承認を増やすことを目的にしません。

<a id="example"></a>
## 中身を確認できる例

同梱の [Python／TypeScript 品質チェック例](skills/senmu-build-engineering/assets/code-quality/examples/README.md)は、「規約を守る」という指示を、実行できる検証に結び付ける方法を示します。

Python の価格計算例では、[`total()`](skills/senmu-build-engineering/assets/code-quality/examples/python/sample_app/domain.py)が割引を差し引き、結果が負ならエラーにします。[`check.py`](skills/senmu-build-engineering/assets/code-quality/examples/python/check.py)は書式、静的ルール、型、依存関係、業務テストを同じ入口から実行します。

```text
正常な実装 → 共通チェックが成功
特定の違反を入れる → 対応するチェックが失敗
元に戻す → 共通チェックが再び成功
```

例えば戻り値を文字列に変えると型チェックを、減算を加算に変えると業務テストを確認できます。説明に従って一時コピーだけで実行し、既存プロジェクトのツールを維持してください。これは再現可能なツールの例であり、利用者の実績紹介やモデル性能の改善値ではありません。

任意の[実行可能な契約例](skills/senmu-build-engineering/assets/contract-examples/README.md)では、定義またはコード宣言から生成物、実際の呼び出し、業務検証までを示します。依存関係は例専用で、プロジェクトの技術選択を強制しません。

<a id="skills"></a>
## 1 つのプラグイン、8 つの能力

| 能力 | 使う場面 |
| --- | --- |
| [Project](skills/senmu-build-project/SKILL.md) | プロジェクトの引き継ぎ、AGENTS.md、既存ルール、継続タスクの整理 |
| [Product](skills/senmu-build-product/SKILL.md) | 要件、範囲、優先度、画面内容、受入条件の明確化 |
| [Design](skills/senmu-build-design/SKILL.md) | UI/UX、レイアウト、操作、レスポンシブ対応、アクセシビリティの設計とレビュー |
| [Workflow](skills/senmu-build-workflow/SKILL.md) | 業務 Agent、プロンプト、素材、再開方法、成果物の取り決め |
| [Engineering](skills/senmu-build-engineering/SKILL.md) | システム理解、デバッグ、設計、言語別規約、テスト、コードレビュー |
| [Delivery](skills/senmu-build-delivery/SKILL.md) | 複雑な Git 協業、版管理、成果物、許可された公開とロールバック |
| [Assurance](skills/senmu-build-assurance/SKILL.md) | 再現、実験、監査、証拠の評価。独立レビューには実際に独立した実行者が必要 |
| [Learning](skills/senmu-build-learning/SKILL.md) | 検証済みの経験や外部手法を適切な既存規範へ反映 |

これは平等な能力の集合であり、常に 8 体の Agent を同時に起動する仕組みではありません。Engineering は Python、TypeScript、Go、Java、Rust などの言語・実行環境の規約を必要に応じて参照します。入口名は各ディレクトリ名に対応します。実行時の指針は英語ですが、日本語、中国語、英語など希望する言語で協業できます。

<a id="how-it-works"></a>
## 既存プロジェクトとの連携

**実際の境界に応じて協業を組み立てます。** 全スタック、複数の全スタック担当、フロントエンドとバックエンドの分担でも、契約、呼び出し元、検証入口を確認してから実装順序を選びます。初期化と許可された整備で正本と導線を校正し、通常の作業では再利用します。局所的なフロントエンド修正に HTTP 文書は不要です。[契約の指針](skills/senmu-build-engineering/references/api-and-boundary-contract-governance.md)を参照してください。

セッションは終了し、文脈が長くなるほど注意は薄れます。BuildOS は、プロンプトを長くし続けるのではなく、再開できる事実をプロジェクトに残します。

```text
プロジェクト入口
  → 現在の事実と工程上の制約
  → 要件と設計判断
  → 進捗と再開地点
  → リリース・実行・本番の証拠
```

5 つのファイルを必ず作る、という意味ではありません。小さなプロジェクトは記録をまとめ、既存プロジェクトは README、AGENTS.md、Issue、設計文書、品質コマンドを活かします。許可された作業の範囲で実際の不足だけを補い、有効な原則、例外、他の人の作業を保護します。

**検査を増やす前に、問題を生む原因を直します。** 要件、責任、インターフェース、既定の処理を改善し、重大な残存リスクをテストとゲートで扱います。原因が明確な小さな問題は最小限で直します。再利用のために業務の意味、安全性、権限、互換性を犠牲にはしません。

理解、設計、実装、検証、引き渡しをタスクの規模に合わせてつなぎます。詳しくは[システム概要](docs/architecture/system-overview.md)、[Skill の境界](docs/architecture/skill-boundaries.md)、[成果物の対応表](docs/architecture/project-artifact-map.md)をご覧ください。

<a id="faq"></a>
## よくある質問

**毎回すべての規約を読み込みますか？** いいえ。既存ルールとテストで十分な通常の修正には、専門 Skill の呼び出しは不要です。必要な場合に関連する参考を読みます。実際の読み込みはクライアントとタスクに依存し、ファイルの存在だけでは有効化を証明できません。

**勝手にプロジェクトを書き換え、コミットや公開をしますか？** 導入だけでは、その権限は与えられません。読取、編集、コミット、push、本番操作は利用者の許可とプロジェクトのルールに従います。読み取り専用の依頼はそのまま守り、承認済みの作業に不要な再承認を挟みません。

**別の AGENTS.md を増やすだけですか？** いいえ。AGENTS.md はよく使うプロジェクト原則と案内、Skills はタスク固有の方法、スクリプトや既存ツールは確定的な検査を担当します。手引き全体を複製しません。

**Token や不具合をどれだけ減らせますか？** 固定の改善率は約束しません。重複実装、無関係な読み込み、やり直しを減らすことを目指し、正しさ、安全性、保守性を優先します。ソーステスト、ホストの読み込み、モデル性能は別の証拠です。[評価の説明](tests/behavior/host-evaluation.md)を参照してください。

**Hook は何をしますか？** 対応するプラグイン入口では、ライフサイクルイベントに短い工程指針を渡します。Skill のみのアダプターには同じ自動注入機能はありません。フィードバックはローカルの確認待ち領域に保存され、自動送信やプロジェクト規則の書き換えは行いません。初回有効化時と変更時に確認してください。[ライフサイクル](docs/architecture/hook-lifecycle.md)と[安全性](SECURITY.md)に詳細があります。

<a id="maintenance"></a>
## バージョン、更新と削除

Senmu BuildOS の現行ソースバージョンは `v2.24.1` です。ソース、非公開リリース、公開市場での提供、本機への導入はそれぞれ別の状態です。上のバッジは公開版へのリンクであり、導入済みの版を示しません。

<!-- product-surface-review: 2.24.1 -->

本版は要件チェックの3つの見落としを修正し、分割定義とコード宣言からの生成という2つの実行可能な契約例を追加します。型生成、実際の呼び出しの検証、SQLite の結果確認をつなぎ、障害注入と復元も検証します。草稿、独自の版名、内容のあるリスト、2.24.0 の軽量な整備方法を維持し、Agent の実動作とソースの証拠を分けて報告します。詳細は[更新履歴](RELEASE_NOTES.md)をご覧ください。

<details>
<summary>既存の導入を更新する</summary>

**Codex**

```bash
codex plugin marketplace upgrade senmu-buildos
codex plugin add senmu-buildos@senmu-buildos
codex plugin list
```

**Claude Code**

```bash
claude plugin marketplace update senmu-buildos
claude plugin update senmu-buildos@senmu-buildos
claude plugin list
```

更新後は新しいセッションを開始してください。Claude Code では `/reload-plugins` も使えます。配布元、版、有効化状態を確認し、ダウンロード成功を現在のセッションへの反映と混同しないでください。他のホストは各アダプターの更新説明に従い、スクリプト方式では先に導入したい信頼できるソースを取得してください。

</details>

<details>
<summary>アンインストール</summary>

```bash
codex plugin remove senmu-buildos@senmu-buildos
codex plugin marketplace remove senmu-buildos

claude plugin uninstall senmu-buildos@senmu-buildos
claude plugin marketplace remove senmu-buildos
```

導入時と同じスコープを対象にし、必要に応じてクライアントのヘルプで確認してください。他のホストはアダプターの削除手順に従い、本プラグインのディレクトリと導入記録だけを削除します。他の Skill、設定、プロジェクトデータは削除しません。

</details>

<a id="contributing"></a>
## 文書、フィードバック、貢献

利用上の問題は[公開 Issue](https://github.com/SenMuShare/senmu-buildos/issues)に、ホスト、BuildOS の配布元と版、再現手順、期待した結果と実際の結果を記載してください。機密情報は必ず除いてください。セキュリティ問題は [SECURITY.md](SECURITY.md) の手順に従い、秘密を公開しないでください。

実際の利用経験や、Fork・Pull Request による改善提案を歓迎します。使い始める前に全参考文書を読む必要はありません。貢献とリリース検証は [CONTRIBUTING.md](CONTRIBUTING.md)、今後の方向は [ROADMAP.md](ROADMAP.md)、三言語文書の保守方針は[貢献ガイド](CONTRIBUTING.md#github-readme-sync)をご覧ください。

## ライセンス

[Apache License 2.0](LICENSE)。BuildOS はプロジェクト責任者、専門的なセキュリティ監査、クラウド権限、CI/CD の代わりではありません。OpenAI または Anthropic の公式認証製品でもありません。
