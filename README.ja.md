# Senmu BuildOS（森木 BuildOS）— AI コーディングプロジェクトの工程コーチと運用規範

<p align="center">
  Codex、Claude Code、豆包が正しいものを作り、無駄を減らして品質を高めるために。
</p>

<p align="center">
  <a href="README.md">简体中文</a> · <a href="README.en.md">English</a> · <a href="README.ja.md">日本語</a>
</p>

<!-- product-surface-review: 2.1.3 -->

<p align="center">
  <a href="https://github.com/SenMuShare/senmu-buildos/actions/workflows/validate.yml"><img src="https://github.com/SenMuShare/senmu-buildos/actions/workflows/validate.yml/badge.svg" alt="Validate Senmu BuildOS"></a>
  <a href="LICENSE"><img src="https://img.shields.io/github/license/SenMuShare/senmu-buildos" alt="License"></a>
  <a href="https://github.com/SenMuShare/senmu-buildos/stargazers"><img src="https://img.shields.io/github/stars/SenMuShare/senmu-buildos?style=social" alt="GitHub stars"></a>
  <a href="https://github.com/SenMuShare/senmu-buildos/releases/latest"><img src="https://img.shields.io/github/v/release/SenMuShare/senmu-buildos" alt="Release"></a>
</p>

Senmu BuildOS は、**AI coding agent** のためのオープンソース運用規範兼ソフトウェア工程コーチです。要件、インターフェース／体験設計、技術設計、フレームワーク／コンポーネント選定、フロントエンド／バックエンド実装、テスト、Git、リリース、再利用可能な学習までを扱い、長くなる一方の Prompt に頼らず、実プロジェクトで継続的に成果を出せるようにします。受入権限、ユーザー文書、重要判断の理由をプロジェクト事実として残し、後続 Agent が変更すべき点と意図的な制約を区別できるようにします。

重視する成果は 2 つです。

1. **プロジェクトを規律正しく進め、ミスを減らす。** 実際の要件、プロジェクト事実、権限を先に確認し、設計、コード、テスト、ブランチ、バージョン、リリース証拠を対応させます。
2. **コード品質を高め、無駄なコードと文脈消費を減らす。** 実装が本当に必要かを確認し、プロジェクト、フレームワーク／コンポーネント API、プラットフォーム、標準ライブラリ、成熟した依存関係を順に再利用します。実際の不足が残った時だけ、境界の明確な最小限の独自コードを書きます。

> BuildOS が目指すのは「少なくても正しいコード」です。最少行数や最低 Token を機械的に追うものではありません。セキュリティ、アクセシビリティ、業務セマンティクス、テスト、保守性を Token 節約のために削りません。

## BuildOS が必要な理由

| AI コーディングで起きがちな問題 | BuildOS の動作 |
| --- | --- |
| スコープが曖昧なまま実装し、要求されていない機能まで増やす | 承認済み範囲、非目標、観測可能な受入条件で実装を制約し、未承認案は候補に留める |
| 既存コードを読まず、新しいディレクトリ、サービス、第二の状態管理を作る | 実際のルート、既存コード、呼び出し経路、信頼できるデータ源を確認し、既存能力を拡張する |
| フレームワークの 1 設定で済むのに、コンポーネントを自作し内部 DOM を監視する | 現在のバージョンの公開 API を先に確認し、実際の不足が証明された時だけ最小アダプターを追加する |
| 動くが、読めない、テストしにくい、変更しにくいコードになる | 単一 owner、モジュール境界、明示的副作用、変更局所性、回帰テスト、削除可能性を守る |
| 想像上の将来のために抽象、プラグイン基盤、汎用プラットフォームを先に作る | 現在の最小価値スライスを閉じ、第二の実例または承認済み Roadmap ができてから拡張する |
| 画面が汎用 AI テンプレートのようになり、情報階層、タイポグラフィ、操作、ブランド意図が噛み合わない | 実際のタスク、内容階層、デザインシステムから始め、レイアウト、書体、色、モーション、レスポンシブ、アクセシビリティを揃え、実表示で確認する |
| 後続セッションが意図的な制約を Bug と誤認し、以前却下した案を復活させる | 判断理由、却下案、維持すべき境界、再評価条件を残し、条件が変わった時だけ新しい判断を追記する |
| 要件や Bug が積み上がり、文脈が失われ、リリース時になって漏れが見つかる | 既存のバージョン文書に要件／欠陥リストを一つだけ置き、開発中に結果状態を更新し、リリース前に Task、Git、Test、候補と一度照合する |
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

## 仕組み

BuildOS は、フォーマットやコードレビューの段階まで待たず、誤った判断がコードになる前から作用します。

```text
実際の問題と承認済みスコープ
        ↓
プロジェクト事実、アーキテクチャ境界、既存能力
        ↓
インターフェースの視覚、操作、デザインシステム
        ↓
技術方針、フレームワーク、コンポーネント、公開拡張点
        ↓
最小限で正しいフロントエンド／バックエンド実装
        ↓
リスクに合うテスト、ユーザー文書の走査、プロダクト受入
        ↓
Git、バージョン、成果物、デプロイ、本番証拠
        ↓
検証済みの知識を再利用できる指針にする
```

このチェーンは作業規模に合わせて裁剪されます。契約を変えないボタンのスタイル調整に PRD、ADR、リリース報告は不要です。モジュール横断、権限、データ、決済、正式リリースでは、必要な設計、検証、ロールバック証拠を保ちます。

### 「再利用してからコードを書く」を実行可能にする

Agent は新しい実装の前に次の順序で判断します。

1. 要件はすでに満たされているか、その能力はそもそも承認されているか。不要なら実装しません。
2. プロジェクトに明確なデータ源、公開入口、安全に拡張できる実装があるか。
3. 現行フレームワーク、コンポーネント、プラットフォーム、標準ライブラリ、既存依存関係が必要な意味を完全に満たすか。
4. 維持されている成熟案が、開発と長期保守の総コストを下げながら不足を補えるか。
5. それでも不足する時だけ、境界と検証が明確で、保守面の小さい独自コードを書きます。

再利用にも意味とリスクの確認が必要です。フレームワーク能力が業務規則、セキュリティ、権限、アクセシビリティ、互換性、エラー意味を満たさない場合、BuildOS は要件を歪めず、必要な最小アダプターを残します。

## 設計思想

- **プロジェクトを理解してから変更する。** 現在の README、コード、設定、テスト、CI、実行状態は、一般論より実際の状況に近い情報です。
- **コードを書く前に要件を確認する。** 「ついでに」や「将来使うかもしれない」という理由で、承認されていない機能を今回の実装へ入れません。
- **症状を塞ぐ前に、欠陥の発生源を正す。** 要件と責務、アーキテクチャ、エンドツーエンドの経路、業務ロジックをたどって最上流の原因を特定します。局所的な欠陥だと十分に確認できる場合は、単純な作業を手続き化せず、直接最小修正します。
- **独自実装より再利用を優先する。** プロジェクト、フレームワーク、コンポーネント、プラットフォーム、標準ライブラリの公開機能を先に使い、実際の不足がある時だけ最小限のアダプターを追加します。
- **設計を意図的で実装可能、検証可能にする。** 実際のタスク、内容階層、既存デザインシステムから始め、レイアウト、タイポグラフィ、色、操作、モーション、レスポンシブ、アクセシビリティを整えます。装飾や汎用テンプレートでプロダクト判断を置き換えず、実表示で確認します。
- **小さな作業は軽く進める。** 通常の変更は必要な確認だけにし、データ、権限、決済、本番リリースなど高リスクの作業では設計、検証、ロールバックの根拠を残します。
- **完了は証拠で示す。** テスト成功、プロダクト受入、成果物生成、デプロイ成功、本番利用可能は別の事実であり、互いの代わりにはなりません。
- **結果を変える前に理由を理解する。** 判断理由、却下案、維持すべき境界、再評価条件を残し、条件が変わった時は古い制約を消したり永久化したりせず、新しい判断を追記します。
- **プロジェクト自身に記憶を残す。** 重要な判断、進捗、再開入口は、一度の会話ではなくプロジェクトに記録します。

システム全体の設計は [System overview](docs/architecture/system-overview.md)、[Skill boundaries](docs/architecture/skill-boundaries.md)、[Project artifact map](docs/architecture/project-artifact-map.md) を参照してください。

## 適した場面

- **新規プロジェクト：** 最小限で有用な要件、アーキテクチャ、品質、デリバリー基準を作り、文書の城を作りません。
- **成熟プロジェクト：** 既存の文書、設定、コード、テスト、CI、リリース事実を読み、第二のガバナンス構造を作らず不足だけを補います。
- **機能と Bug：** プロジェクト規則を優先し、フレームワークと既存実装を再利用し、最小変更と対応する検証を行います。
- **インターフェース設計と改修：** 曖昧な好みを実装可能な視覚、操作、レスポンシブ、アクセシビリティの規則へ変換し、実際の表示で確認します。
- **長期作業：** 段階、判断、証拠、再開入口を残し、会話や Agent をまたいで引き継げるようにします。
- **正式リリース：** スコープ、レビュー、テスト、バージョン、成果物、デプロイ、本番確認、ロールバック identity を一致させます。
- **ガバナンスと学習：** 技術的負債と重複実装を確認し、検証済みで複数プロジェクトに使える知識を再利用可能な指針にします。

## 1 つのプラグイン、8 つの専門 Skill

| Skill | 使う場面 |
| --- | --- |
| `senmu-build-project` | 新規プロジェクトの基本的な運用構造を作る時、または成熟プロジェクトの既存構造、規則、長期タスク状態を確認する時 |
| `senmu-build-product` | 要件、範囲、優先度、UI コンテンツ規約、受入条件を定義または変更する時 |
| `senmu-build-design` | 視覚方向、デザインシステム、レイアウト、操作、モーション、レスポンシブ、アクセシビリティを設計・改修・評価する時 |
| `senmu-build-workflow` | 複数工程の Workflow、Agent 分担、物料の流れ、復旧経路、デリバリー状態を設計する時 |
| `senmu-build-engineering` | 技術設計、アーキテクチャ、技術選定、コード品質、テスト、リファクタリング、技術的負債を管理する時 |
| `senmu-build-delivery` | 複雑な Git 協業、バージョン、成果物、リリース、ロールバック、本番確認を管理する時 |
| `senmu-build-assurance` | 独立した再現、POC、監査、証拠の強さに関する判断が必要な時 |
| `senmu-build-learning` | 問題を振り返る時、フィードバックを審議する時、外部知識を再利用可能な指針にする時 |

通常のコード変更がプロジェクト `AGENTS.md`、現行フレームワーク、テストで十分に規定されているなら、BuildOS の専門 Skill は読み込みません。必要な時も、最も近い Skill と関連 reference だけを使います。

## よくある質問

### すべての変更で BuildOS 全体を読み込むのか？

いいえ。プロジェクト規則、フレームワーク、テストが通常のコード変更を十分に規定している場合、専門 Skill は不要です。指針が必要な時も、関連する Skill と reference だけを読み込みます。

### 既存プロジェクトを新しい構造へ強制するのか？

いいえ。読み取り専用の依頼ではプロジェクトへ書き込みません。変更が承認された場合も、既存のディレクトリ、文書、コード入口、リリース方法を優先し、実際の不足や衝突だけを補います。

### 自動で Commit、Push、Release するのか？

いいえ。コード変更、Merge、Push、正式 Release は、それぞれユーザーの許可とプロジェクト規則に従います。プラグインのインストールは、本番環境への書き込み権限を意味しません。

### Token をどれだけ節約できるのか？

BuildOS は固定割合を約束しません。不要な機能、重複コード、再読、手戻りを減らして回避可能なコストを下げますが、正しさ、安全性、保守性を Token 節約より優先します。

## インストール、更新、削除

Senmu BuildOS の現行正式リリースは `v2.1.3` です。Codex、Claude Code、豆包アダプターをサポートします。8 Skill は個別ではなく、1 つのプラグインとしてインストールします。

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
2. 要件、Architecture、実行状態、Task、Release 情報が実際に保存されている場所を特定します。
3. BuildOS と比較し、不足、衝突、重複、古い規則を見つけます。
4. 妥当な現状を保ち、実際の不足だけを元の文書やコード位置に補います。
5. 段階的に検証・移行し、BuildOS 全規則をプロジェクトへ複製しません。

そのため同じ BuildOS が React、Vue、Python、Go、Java、コンテンツ制作、複合 Workflow に対応でき、特定プロジェクトの絶対パス、Framework 嗜好、ディレクトリ構造を全プロジェクトの答えにしません。

## コントリビューション

正式版をインストールすることも、自分の fork を維持することもできます。新しい方法、外部資料、プロジェクト経験は、「良さそう」という理由だけでは規則になりません。比較、検証、適用範囲の確認を行います。

- Code／Rule を貢献する場合：[CONTRIBUTING.md](CONTRIBUTING.md)
- 今後の方向：[ROADMAP.md](ROADMAP.md)
- Security report：[SECURITY.md](SECURITY.md)

## 利用上の範囲

- BuildOS はプロジェクト運営とソフトウェア工程の指針を提供しますが、最終的なプロダクト判断を行う責任者の代わりにはなりません。
- 専門的な Security audit、Cloud permission、CI/CD、Runtime monitoring の代わりにはなりません。
- 静的検証は Repository が現在の規則を満たすことを確認できますが、すべての Model／Project で同じ効果が出ることまでは保証しません。
- 必要な許可なしに Commit、Merge、Push、Deploy、正式 Release を行いません。

Contributor 向けの Test command と Release check は [CONTRIBUTING.md](CONTRIBUTING.md) にあります。

## ライセンス

[Apache License 2.0](LICENSE)
