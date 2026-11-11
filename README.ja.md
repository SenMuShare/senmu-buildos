# Senmu BuildOS — Agent Skills for Codex & Claude Code

**アイデアを、育て続けられるプロダクトへ。**

*Understand the goal. Make the right decisions. Carry the work through.*

[简体中文](README.md) · [English](README.en.md) · [日本語](README.ja.md)

作りたいものは分かっていても、必要な要件、設計、実装、リリースの判断まで最初から分かるとは限りません。Senmu BuildOS は、AI コーディングアシスタントにプロジェクトコーチの進め方を与える Skills です。目的と現状から必要な専門作業を見つけ、判断をコード、規約、確認可能な結果につなげます。

プロダクト、UI/UX、エンジニアリング、プロジェクト管理、ワークフロー、デリバリー、検証、学習をカバーします。新規開発には必要な出発点を用意し、既存開発では有効な資産を活かし、小さな変更は直接進めます。モデルや会話が変わっても、同じプロジェクトの事実から続けられます。

**目的を伝えると、次に何をするか、なぜ必要か、何をもって完了とするかを AI が考えやすくなります。**

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

「ブラウザで使う在庫管理を作りたい」「この画面が雑然としている」「この画像どおりに実装して」とも依頼できます。目的から必要な Product、Design、Engineering の作業を見つけ、要件だけの依頼はその段階に留めます。継続的な UI は `design/UI_SPECIFICATION.md` を使い、有効な既存判断は規約移行で残します。AGENTS.md とプロジェクトマップが規約、実際の部品、確認入口をつなげます。

レビューには「要件を満たしているかと、コード品質に問題がないかを別々に確認してください」と依頼できます。外部管理画面の操作には「私にしかできない操作を、途中から再開できる手順にしてください」と依頼してください。能力を明示して使う場合は[一覧](#skills)から入口を確認できます。

<a id="why"></a>
## プロジェクトの進め方に、専門的な判断を

**普段の依頼から、必要な仕事を見つける。** 「在庫管理システムを作りたい」には、利用者の操作、データの意味、画面の状態、提供方法などの判断が含まれます。BuildOS は、その段階に必要な作業を AI が見つけるための方法を提供します。Skill 名や専門用語を先に覚える必要はありません。

**プロジェクトに合わせて方法を選ぶ。** 一度だけ使う試作、継続運用する製品、バックエンドサービス、大きな既存リポジトリでは必要な作業が異なります。実際の能力と不足を確認し、既存の規則で対応できる小変更は簡潔に進めます。

**手戻りの原因を減らす。** 新しく作る前に、既存の部品、契約、状態の管理元を確認します。バグの原因を追い、競合する規約を採用判断にまとめ、実際の問題を検出できる確認を選びます。明確な責任と必要なコードを重視します。

**次の AI が引き継げる形で残す。** 要件の版、設計の根拠、タスクの進捗、検証結果をプロジェクトに保存します。会話やモデルが変わっても既知の入口から再開でき、実装、利用者の受入れ、デプロイ、リリースを区別します。

継続して製品を育てる個人開発者、プロダクト担当者、小さなチーム向けです。目標と取捨選択は利用者が決め、AI は専門作業を整理する共通の方法を使います。

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
<a id="one-plugin-eight-skills"></a>
## 8 つの能力、それぞれが解く課題

### Product · 漠然としたアイデアを、受入れ可能な要件へ

機能の依頼には、失敗、取消し、切替え、復旧の動作が書かれていないことがあります。Product は目標、範囲、業務動作、画面の応答、受入条件を結び、適切なバージョンへ配置します。関連するプロトタイプにも採用範囲を残します。

実装・確認できる要件と、今回どこまで行うかの判断が得られます。「一括出力の要件を、再試行と権限も含めて整理して」と依頼できます。[Product の方法](skills/senmu-build-product/SKILL.md)

### Design · 画面の一貫性と、操作を完了できる体験

「洗練させたい」を、階層、配置、文字、色、密度、状態の具体的な選択に変えます。利用者のタスクと参考資料から、新規画面、既存改善、忠実な再現を区別します。画面の種類、代表例、実際の部品を使い、理由のある差異を保ちながら統一します。

継続的な UI は `design/UI_SPECIFICATION.md` を入口とし、実際のテーマ、token、部品につなげます。必要な範囲で実画面と操作経路を確認します。「この画面群が雑然としているので、原因を調べて整えて」と依頼できます。[Design の方法](skills/senmu-build-design/SKILL.md)

### Engineering · 有効な実装を再利用し、原因を修正する

入口、呼出し元、データ、状態を理解してから実装を選びます。技術選定、アーキテクチャ、フロントエンドとバックエンドの契約、言語別規約、デバッグ、コードレビューを扱い、既存プロジェクトや成熟した部品の能力から検討します。

修正は元の失敗と影響する呼出し元で確認します。選択の理由、実際の変更、実行した検証が分かります。「繰り返すバグの原因を調べ、既存構造の中で修正して」と依頼できます。[Engineering の方法](skills/senmu-build-engineering/SKILL.md)

### Project · 新規には出発点を、既存には明確な規約を

プロジェクトのルート、制約、責任、実際の能力を確認します。新規開発には必要な管理の起点を作り、既存開発では調査と移行によって規約を整理し、有効な判断を残します。AGENTS.md は作業原則と案内を持ち、専門的な内容は各領域が管理します。

規約を見つけ、使い、作業を再開できる状態を目指します。UI の有無、管理元、次の作業場所を明確にします。「このプロジェクトを引き継ぎ、不足している規約を必要な範囲で整えて」と依頼できます。[Project の方法](skills/senmu-build-project/SKILL.md)

### Workflow · 中断後にも再開できるプロセスへ

複数 Agent、ファイル処理、外部管理画面では引継ぎが詰まりやすくなります。Workflow は入出力、実行の識別、段階の状態、人の操作、復旧入口を明確にします。原資料、中間生成物、成果物、アーカイブを区別し、再試行の出発点を示します。

業務 Agent とプロンプトの設計も対象です。実行可能な手順と具体的な引継ぎを得られます。「失敗したバッチを毎回最初からやり直すので、復旧と納品の流れを整理して」と依頼できます。[Workflow の方法](skills/senmu-build-workflow/SKILL.md)

### Delivery · どこまで届けられたかを明確にする

コミット、ビルド成功、デプロイ、実環境での確認は別の事実です。Delivery はブランチと worktree の分離、並行変更の統合、版付き成果物、公開権限、ロールバック、環境確認を、既存の交付入口でつなげます。

候補、検証結果、実際の公開状態、復旧根拠が分かります。「この変更を一つの版にまとめ、確認後に既存手順でリリースして」と依頼できます。[Delivery の方法](skills/senmu-build-delivery/SKILL.md)

### Assurance · 疑問を、証拠のある結論へ

「この案に問題はないか」を判断するには、対象、版、範囲、基準が必要です。Assurance はソース、再現、比較、POC で仮説を確認し、事実、推論、未確認事項を分けて、影響、修正方針、再確認条件を示します。

追跡可能な指摘と優先順位が得られます。独立性は実際の評審体制で決まり、明示的な監査と日常の自己確認は範囲を区別します。「このデプロイ案を客観的に調べ、問題箇所を示して」と依頼できます。[Assurance の方法](skills/senmu-build-assurance/SKILL.md)

### Learning · 解決した問題を、次に使える経験へ

失敗するたびに規則を増やすと、説明が衝突し始めます。Learning は問題と改善の証拠を確認し、個別修正、プロジェクト固有の教訓、BuildOS の共通方法のどこへ反映するかを判断します。外部の知見も適用性と重複を検討します。

取捨選択された経験と、正式な管理場所が得られます。「今回の手戻りから、この案件だけの話と共通方法を改善すべき話を分けて」と依頼できます。[Learning の方法](skills/senmu-build-learning/SKILL.md)

8 つは対等で、タスクに必要なものだけを使います。一つで足りる場合もあります。Python、TypeScript、Go、Java、Rust などの規約は Engineering が必要に応じて読みます。実行時の方法は英語ですが、日本語、中国語、英語などで協働できます。

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

継続して必要な事実を、タスクに合う規模で記録します。進捗には既存の Issue やタスク記録を使えます。継続的な UI の現行規約は `design/UI_SPECIFICATION.md` に統一し、有効な判断は移行によって残します。プロジェクト入口と品質コマンドは実際の実装につなげます。

**検査を増やす前に、問題を生む原因を直します。** 要件、責任、インターフェース、既定の処理を改善し、重大な残存リスクをテストとゲートで扱います。原因が明確な小さな問題は最小限で直します。再利用のために業務の意味、安全性、権限、互換性を犠牲にはしません。

理解、設計、実装、検証、引き渡しをタスクの規模に合わせてつなぎます。詳しくは[システム概要](docs/architecture/system-overview.md)、[Skill の境界](docs/architecture/skill-boundaries.md)、[成果物の対応表](docs/architecture/project-artifact-map.md)をご覧ください。

<a id="faq"></a>
## よくある質問

**毎回すべての規約を読み込みますか？** いいえ。既存ルールとテストで十分な通常の修正には、専門 Skill の呼び出しは不要です。必要な場合に関連する参考を読みます。実際の読み込みはクライアントとタスクに依存し、ファイルの存在だけでは有効化を証明できません。

**勝手にプロジェクトを書き換え、コミットや公開をしますか？** 導入だけでは、その権限は与えられません。読取、編集、コミット、push、本番操作は利用者の許可とプロジェクトのルールに従います。読み取り専用の依頼はそのまま守り、承認済みの作業に不要な再承認を挟みません。

**別の AGENTS.md を増やすだけですか？** いいえ。AGENTS.md はよく使うプロジェクト原則と案内、Skills はタスク固有の方法、スクリプトや既存ツールは確定的な検査を担当します。手引き全体を複製しません。

プロジェクト入口からリリース・復旧を Delivery と既存の手順・コマンドへ案内できます。ファイルの存在だけでは採用済みとは言えません。安定した操作は元のスクリプトや CI に任せ、AI は適用判断、必要な保守、結果確認を担当します。実行入口は版をまたいで再利用し、工程が変わるときに更新します。通常編集で全規則を読み込む必要はありません。

**Token や不具合をどれだけ減らせますか？** 固定の改善率は約束しません。重複実装、無関係な読み込み、やり直しを減らすことを目指し、正しさ、安全性、保守性を優先します。ソーステスト、ホストの読み込み、モデル性能は別の証拠です。[評価の説明](tests/behavior/host-evaluation.md)を参照してください。

**Hook は何をしますか？** 対応するプラグイン入口では、ライフサイクルイベントに短い工程指針を渡します。Skill のみのアダプターには同じ自動注入機能はありません。フィードバックはローカルの確認待ち領域に保存され、自動送信やプロジェクト規則の書き換えは行いません。初回有効化時と変更時に確認してください。[ライフサイクル](docs/architecture/hook-lifecycle.md)と[安全性](SECURITY.md)に詳細があります。

<a id="maintenance"></a>
## バージョン、更新と削除

Senmu BuildOS の現行ソースバージョンは `v2.32.0` です。ソース、非公開リリース、公開市場での提供、本機への導入はそれぞれ別の状態です。上のバッジは公開版へのリンクであり、導入済みの版を示しません。

<!-- product-surface-review: 2.32.0 -->

本版は普段の依頼から Product、Design、Engineering への引継ぎを強化し、継続的な UI の規約入口と既存資料の移行方法を統一します。UI の未評価と UI なしを区別し、8 つの能力の考え方、方法、結果が伝わる製品紹介へ更新しました。小さな変更は引き続き簡潔に進めます。[更新履歴](RELEASE_NOTES.md)をご覧ください。

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
