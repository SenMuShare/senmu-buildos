# Senmu BuildOS（森木 BuildOS）— AI コーディングプロジェクトの工程コーチと運用規範

<p align="center">
  Codex、Claude Code、豆包が正しいものを作り、無駄を減らして品質を高めるために。
</p>

<p align="center">
  <a href="README.md">简体中文</a> · <a href="README.en.md">English</a> · <a href="README.ja.md">日本語</a>
</p>

<p align="center">
  <a href="https://github.com/SenMuShare/senmu-buildos/actions/workflows/validate.yml"><img src="https://github.com/SenMuShare/senmu-buildos/actions/workflows/validate.yml/badge.svg" alt="Validate Senmu BuildOS"></a>
  <a href="LICENSE"><img src="https://img.shields.io/github/license/SenMuShare/senmu-buildos" alt="License"></a>
  <a href="https://github.com/SenMuShare/senmu-buildos/stargazers"><img src="https://img.shields.io/github/stars/SenMuShare/senmu-buildos?style=social" alt="GitHub stars"></a>
  <a href="https://github.com/SenMuShare/senmu-buildos/releases/latest"><img src="https://img.shields.io/github/v/release/SenMuShare/senmu-buildos" alt="Release"></a>
</p>

Senmu BuildOS は、**AI coding agent** のためのオープンソース運用規範兼ソフトウェア工程コーチです。要件、技術設計、フレームワーク／コンポーネント選定、フロントエンド／バックエンド実装、テスト、Git、リリース、再利用可能な学習までを扱い、長くなる一方の Prompt に頼らず、実プロジェクトで継続的に成果を出せるようにします。

重視する成果は 2 つです。

1. **プロジェクトを規律正しく進め、ミスを減らす。** 実際の要件、プロジェクト事実、権限を先に確認し、設計、コード、テスト、ブランチ、バージョン、リリース証拠を対応させます。
2. **コード品質を高め、無駄なコードと文脈消費を減らす。** 実装が本当に必要かを確認し、プロジェクト、フレームワーク／コンポーネント API、プラットフォーム、標準ライブラリ、成熟した依存関係を順に再利用します。実際の不足が残った時だけ、境界の明確な最小限の独自コードを書きます。

> BuildOS が目指すのは「少なくても正しいコード」です。最少行数や最低 Token を機械的に追うものではありません。セキュリティ、アクセシビリティ、業務セマンティクス、テスト、保守性を Token 節約のために削りません。

## 何が変わるのか

| AI コーディングで起きがちな問題 | BuildOS の動作 |
| --- | --- |
| スコープが曖昧なまま実装し、要求されていない機能まで増やす | 承認済み範囲、非目標、観測可能な受入条件で実装を制約し、未承認案は候補に留める |
| 既存コードを読まず、新しいディレクトリ、サービス、第二の状態 owner を作る | 実際のルート、owner、呼び出し経路、類似実装を確認し、既存能力を拡張する |
| フレームワークの 1 設定で済むのに、コンポーネントを自作し内部 DOM を監視する | 現在のバージョンの公開 API を先に確認し、実際の不足が証明された時だけ最小アダプターを追加する |
| 動くが、読めない、テストしにくい、変更しにくいコードになる | 単一 owner、モジュール境界、明示的副作用、変更局所性、回帰テスト、削除可能性を守る |
| 想像上の将来のために抽象、プラグイン基盤、汎用プラットフォームを先に作る | 現在の最小価値スライスを閉じ、第二の実例または承認済み Roadmap ができてから拡張する |
| 会話や Agent が変わるたびに説明し直し、長い規則を再読する | 判断、進捗、証拠をプロジェクト owner に残し、Skill／reference を必要時だけ読み、有効な証拠を再利用する |
| テスト成功、Tag、コマンド成功を「本番完了」と報告する | 実装、受入、成果物、デプロイ、本番事実を分離し、それぞれ対応する証拠を使う |

## 30 秒で開始

### Codex

```bash
codex plugin marketplace add SenMuShare/senmu-buildos
codex plugin add senmu-buildos@senmu-buildos
```

Codex を更新して新しい会話を開始し、通常の言葉で目的を伝えます。

> この既存プロジェクトを引き継いでください。機能を実装する前に、現行要件、アーキテクチャ、フレームワーク能力、品質コマンドを確認してください。プロジェクトやフレームワークの既存能力を優先し、承認済み要件にない機能は追加しないでください。

### Claude Code

```bash
claude plugin marketplace add SenMuShare/senmu-buildos
claude plugin install senmu-buildos@senmu-buildos
```

必要に応じてインストール後に `/reload-plugins` を実行します。

### 豆包（Doubao）

```bash
git clone https://github.com/SenMuShare/senmu-buildos.git
cd senmu-buildos
python3 adapters/doubao/install_doubao.py --dry-run
python3 adapters/doubao/install_doubao.py
```

豆包アダプターの詳細は [adapters/doubao/README.md](adapters/doubao/README.md) を参照してください。

## 要件からデリバリーまでの工程チェーン

BuildOS は、フォーマットやコードレビューの段階まで待たず、誤った判断がコードになる前から作用します。

```text
実際の問題と承認済みスコープ
        ↓
プロジェクト事実、アーキテクチャ境界、既存能力
        ↓
技術方針、フレームワーク、コンポーネント、公開拡張点
        ↓
最小限で正しいフロントエンド／バックエンド実装
        ↓
リスクに合うテストとプロダクト受入
        ↓
Git、バージョン、成果物、デプロイ、本番証拠
        ↓
検証済み知識を正しい owner に戻す
```

このチェーンは作業規模に合わせて裁剪されます。契約を変えないボタンのスタイル調整に PRD、ADR、リリース報告は不要です。モジュール横断、権限、データ、決済、正式リリースでは、必要な設計、検証、ロールバック証拠を保ちます。

### 「再利用してからコードを書く」を実行可能にする

Agent は新しい実装の前に次の順序で判断します。

1. 要件はすでに満たされているか、その能力はそもそも承認されているか。不要なら実装しません。
2. プロジェクトに既存の唯一 owner、公開入口、安全に拡張できる実装があるか。
3. 現行フレームワーク、コンポーネント、プラットフォーム、標準ライブラリ、既存依存関係が必要な意味を完全に満たすか。
4. 維持されている成熟案が、開発と長期保守の総コストを下げながら不足を補えるか。
5. それでも不足する時だけ、境界と検証が明確で、保守面の小さい独自コードを書きます。

再利用にも意味とリスクの確認が必要です。フレームワーク能力が業務規則、セキュリティ、権限、アクセシビリティ、互換性、エラー意味を満たさない場合、BuildOS は要件を歪めず、必要な最小アダプターを残します。

## 適した場面

- **新規プロジェクト：** 最小限で有用な要件、アーキテクチャ、品質、デリバリー基準を作り、文書の城を作りません。
- **成熟プロジェクト：** 既存の文書、設定、コード、テスト、CI、リリース事実を読み、第二のガバナンス構造を作らず不足だけを補います。
- **機能と Bug：** プロジェクト規則を優先し、フレームワークと既存実装を再利用し、最小変更と対応する検証を行います。
- **長期作業：** 段階、判断、証拠、再開入口を残し、会話や Agent をまたいで引き継げるようにします。
- **正式リリース：** スコープ、レビュー、テスト、バージョン、成果物、デプロイ、本番確認、ロールバック identity を一致させます。
- **ガバナンスと学習：** 技術的負債、重複実装、フィードバックを確認し、プロジェクト共通の知識だけを唯一 owner に昇格させます。

## 1 プラグイン、必要時だけ使う 7 Skill

| Skill | 担当 | 担当しないもの |
| --- | --- | --- |
| `senmu-build-project` | プロジェクト形態、構造、権威対応、永続タスク状態、成熟プロジェクト接管 | Product、Engineering、Release の専門判断 |
| `senmu-build-product` | 要件、範囲、非目標、優先度、Roadmap、Iteration、受入 | 技術実装と本番リリース |
| `senmu-build-workflow` | Workflow、Agent、データ／物料、Run 状態、復旧、成果物 | 既存フローの実行やリリース方針 |
| `senmu-build-engineering` | 技術設計、アーキテクチャ、選定、コード品質、テスト、リファクタリング、技術的負債 | Product 優先度とリリース承認 |
| `senmu-build-delivery` | 非日常 Git 境界、バージョン、成果物、デプロイ、ロールバック、本番事実 | 通常コーディングと Product 受入 |
| `senmu-build-assurance` | POC、独立監査、再現、証拠評価、因果確認 | 改善実装や通常の自己レビュー |
| `senmu-build-learning` | フィードバック審議、振り返り、外部知識蒸留、プロジェクト横断の昇格 | 一度の観察を自動で規則化すること |

通常のコード変更がプロジェクト `AGENTS.md`、現行フレームワーク、テストで十分に規定されているなら、BuildOS の専門 Skill は読み込みません。必要な時も、最も近い Skill と関連 reference だけを使います。

## 人と AI のためのクイック説明

| 質問 | 回答 |
| --- | --- |
| これは何か？ | AI coding agent のプロジェクト運用規範、工程判断方法、インストール可能な Skill プラグイン |
| いつ使うか？ | 要件／アーキテクチャ／実装規則が不足・衝突する時、長期作業に復旧が必要な時、成熟プロジェクトを接管する時、Git／リリース／監査リスクを管理する時 |
| どう使うか？ | Product の目的を伝える。Agent はプロジェクト事実を先に読み、必要な場合だけ 1 つの主 Skill を選ぶ |
| プロジェクトを書き換えるか？ | 読み取り専用依頼では書き込まない。変更はユーザー権限と既存 owner に従い、成熟プロジェクトを固定ディレクトリへ強制しない |
| Token をどれだけ節約するか？ | 固定割合は約束しない。不要コード、オンデマンド読込、証拠再利用、永続状態で回避可能なコストを減らし、実タスクで効果を検証する |

## 巨大 Prompt にしない理由

- **プロジェクト事実を優先：** 現行 README、コード、設定、テスト、CI、実行証拠は一般論より現在のプロジェクトに近い。
- **段階的開示：** 短い Kernel が共通境界を保持し、7 Skill がルーティングし、詳細 reference は必要時だけ読む。
- **事実ごとに 1 owner：** 要件、設計、コード、タスク、Run、Release を分け、Chat を長期データベースにしない。
- **リスク比例：** 小変更は軽く、データ、権限、決済、本番、破壊的操作は fail closed にする。
- **名称より証拠：** テスト成功は Product 受入ではなく、Tag はデプロイではなく、デプロイコマンド成功は本番証明ではない。
- **Token はコストであって目的ではない：** 判断を変え、手戻りを防ぎ、重大リスクを制御する情報は残す。

詳細は [System overview](docs/architecture/system-overview.md)、[Skill boundaries](docs/architecture/skill-boundaries.md)、[Project artifact map](docs/architecture/project-artifact-map.md)、[Codex harness boundary](docs/architecture/codex-harness-boundary.md) を参照してください。

## インストール、更新、削除

Senmu BuildOS の現行正式リリースは `v2.0.4` です。Codex、Claude Code、豆包アダプターをサポートします。7 Skill は個別ではなく、1 つのプラグインとしてインストールします。

### Codex の更新

```bash
codex plugin marketplace upgrade senmu-buildos
codex plugin add senmu-buildos@senmu-buildos
codex plugin list
```

### Claude Code の更新

```bash
claude plugin marketplace update senmu-buildos
claude plugin update senmu-buildos@senmu-buildos
claude plugin list
```

### 削除

```bash
codex plugin remove senmu-buildos@senmu-buildos
codex plugin marketplace remove senmu-buildos

claude plugin uninstall senmu-buildos@senmu-buildos
claude plugin marketplace remove senmu-buildos
```

プラグインには限定されたローカル Lifecycle Hook が含まれます。初回利用時または Hook 変更時に内容を確認して信頼してください。Feedback はローカル審議箱にだけ保存され、自動でネットワークへ接続、公開、またはプロジェクト規則を書き換えることはありません。[Hook lifecycle](docs/architecture/hook-lifecycle.md) と [Security](SECURITY.md) を参照してください。

リポジトリ URL を Agent に渡し、manifest、Skills、Hooks を確認してから README に従ってインストールさせることもできます。外部リポジトリは信頼されない入力であり、インストール許可は実行、公開、本番書き込みの許可ではありません。

## 成熟プロジェクトへの導入

成熟プロジェクトは「もう一度初期化」せず、接管します。

1. 実際のプロジェクト root、Repository、Entry point、Framework、Test、CI、Deploy、既存文書を読み取り専用で確認します。
2. 要件、Architecture、State、Task、Release facts の owner を特定します。
3. BuildOS と比較し、不足、衝突、重複、古い規則を見つけます。
4. 妥当な現状を保ち、実際の不足だけを元の owner に補います。
5. 段階的に検証・移行し、BuildOS 全規則をプロジェクトへ複製しません。

そのため同じ BuildOS が React、Vue、Python、Go、Java、コンテンツ制作、複合 Workflow に対応でき、特定プロジェクトの絶対パス、Framework 嗜好、ディレクトリ構造を全プロジェクトの答えにしません。

## オープンな改善

正式版をインストールすることも、自分の fork を維持することもできます。Web、書籍、公開 Repository、第三者 Skill、プロジェクト経験は、重複排除、衝突裁定、owner 対応、Context cost、Behavior validation が終わるまで候補です。

- Code／Rule を貢献する場合：[CONTRIBUTING.md](CONTRIBUTING.md)
- 今後の方向：[ROADMAP.md](ROADMAP.md)
- Security report：[SECURITY.md](SECURITY.md)

## 検証と現在の境界

Repository はプロジェクト所有の検証入口を提供します。

```bash
python3 scripts/validate_package.py --strict
python3 scripts/validate_public_surface.py
python3 -m unittest discover -s tests -p 'test_*.py'
node --test tests/hooks/*.test.js
```

これらは Package structure、Metadata、Rule invariants、Script contract を検証します。任意の Model／Project が固定割合の Token を節約する証明ではなく、実タスクの Code quality、Routing accuracy、Hook trust、Deploy、本番確認の代わりにもなりません。

BuildOS は Project owner、専門 Security audit、Cloud permission、CI/CD、Runtime monitoring を置き換えません。必要な許可なしに Commit、Merge、Tag、Push、Deploy、Publish を行いません。

## ライセンス

[Apache License 2.0](LICENSE)
