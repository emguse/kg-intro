# Knowledge Graph Design Learning Plan

このプランは、既存データを読み込む実装練習とは別に、「新しく Knowledge Graph を作るときに何をどう設計するか」を学ぶためのものです。JSON-LD や NetworkX のコードを書く前に、対象ドメイン、ノード、エッジ、属性、識別子、制約、クエリを設計できる状態を目指します。

## Goal

最終的に、以下を自分で説明しながら小さな KG を設計できる状態を目指します。

- KG の目的と利用シナリオを定義できる
- 何をノードにし、何を属性にし、何をエッジにするか判断できる
- ノード種別、エッジ種別、属性を語彙として整理できる
- `@id` に使う安定した識別子を設計できる
- JSON-LD の `@context` に載せる語彙を設計できる
- オントロジーを考え始めるタイミングを判断できる
- class, property, domain, range, hierarchy などの基本を小さく設計できる
- 設計した KG が必要な問いに答えられるか検証できる
- 将来の拡張やデータ品質の問題を見越して設計を見直せる

## Design Mindset

Knowledge Graph は「データをグラフっぽく保存するもの」ではなく、「後からたどりたい関係を明示するためのモデル」です。

設計時は、最初に次の順で考えます。

1. 何を知りたいのか
2. その問いに答えるには、どの対象を区別する必要があるのか
3. 対象同士の関係は何か
4. 関係に意味や状態があるか
5. どの情報はノード属性で十分か
6. 将来、別のデータと接続するときに ID は安定しているか
7. 語彙の意味を人やシステムが共有する必要があるか

オントロジーは、最初の 1 行目から完璧に作るものではありません。最初はノード種別、エッジ種別、属性名を素直に設計し、語彙の意味や制約を共有したくなった段階で、軽量なオントロジーとして整理します。

## Phase 1: Use Case and Competency Questions

目的: KG が答えるべき問いを先に決めます。

やること:

- 業務ドメインを 1 つ選ぶ
- ユーザーや利用者の視点を決める
- KG に答えてほしい質問を 5 から 10 個書く
- 質問を「検索」「影響調査」「推薦」「整合性チェック」に分類する

このプロジェクトの例:

- どの機械装置が discontinued な部品を使っているか
- ある部品の後継部品は何か
- ある機械装置で交換対象になる部品は何か
- ある構成ユニットが使っている交換部品は何か
- ある保全作業の対象になる機械装置は何か

完了条件:

- KG で答えたい質問リストがある
- 各質問に必要なノード種別とエッジ種別をざっくり説明できる

## Phase 2: Node Design

目的: 何をノードとして扱うか判断できるようにします。

ノードにしやすいもの:

- 固有に識別したいもの
- 複数の関係を持つもの
- 状態や履歴が変化するもの
- 他のデータセットと接続したいもの
- 後から検索、集計、探索の起点にしたいもの

属性で十分なもの:

- その対象だけに閉じた説明情報
- 関係を持たない短い値
- 単純な状態値やラベル
- 独立した ID を持たせる必要が薄いもの

このプロジェクトの初期候補:

| Candidate | Node or Attribute | Reason |
| --- | --- | --- |
| Equipment | Node | 構成ユニット、設置場所、保全作業など複数の関係を持つ |
| Component | Node | 装置と交換部品の中間にあり、影響範囲分析の起点になる |
| Part | Node | 廃番、後継、互換品などの関係を持つ |
| MaintenanceTask | Node or Attribute | 作業手順、周期、対象装置を管理するなら Node |
| Part status | Attribute | まずは `available` や `discontinued` の値で十分 |
| Location | Node or Attribute | 工場、ライン、工程別に影響調査をするなら Node |

やること:

- ノード候補を表にする
- 各候補について Node/Attribute の判断理由を書く
- 最小構成のノード種別を 3 から 5 個に絞る
- 各ノード種別に必須属性を決める

完了条件:

- `Equipment`, `Component`, `Part`, `MaintenanceTask` などのノード種別が定義されている
- 「なぜこれはノードなのか」を説明できる

## Phase 3: Edge Design

目的: 対象同士の意味ある関係をエッジとして設計します。

エッジ設計で決めること:

- relation 名
- 向き
- 始点ノード種別
- 終点ノード種別
- 多重度
- エッジ属性
- 逆向き relation が必要か

このプロジェクトの初期候補:

| Relation | From | To | Meaning |
| --- | --- | --- | --- |
| `has_component` | Equipment | Component | 機械装置が構成ユニットを持つ |
| `uses_part` | Component | Part | 構成ユニットが交換部品を使う |
| `superseded_by` | Part | Part | 古い部品が後継部品に置き換えられる |
| `requires_maintenance` | Equipment | MaintenanceTask | 機械装置が保全作業を必要とする |

向きの考え方:

- 質問文で自然にたどる方向を優先する
- `equipment -> component -> part` は「装置から利用部品を探す」時に自然
- `old part -> new part` は「交換先や後継部品を探す」時に自然
- 逆向き検索が必要でも、NetworkX では predecessor を使えばよいので、最初から両方向エッジを持たなくてよい

やること:

- relation 一覧を表にする
- 各 relation の向きを決める
- relation ごとに許可する From/To の型を決める
- エッジ属性が必要か判断する

完了条件:

- relation 名と向きが一貫している
- edge の `relation` 値だけで問い合わせ条件を書ける

## Phase 4: Attribute and Relation Properties

目的: ノード属性とエッジ属性を分けて設計します。

ノード属性の例:

- `name`
- `status`
- `created_at`
- `tier`
- `owner`

エッジ属性の例:

- `status`
- `since`
- `until`
- `confidence`
- `source`

判断基準:

- 対象そのものの性質ならノード属性
- 関係が成立した時期や根拠ならエッジ属性
- 同じ 2 ノード間に複数の意味や期間があるなら、エッジ属性または中間ノードを検討する

例:

```json
{
  "source": "component:hydraulic-unit",
  "target": "part:hydraulic-valve-a",
  "relation": "uses_part",
  "since": "2024-04-01",
  "source_system": "bom"
}
```

やること:

- 各ノード種別の属性一覧を作る
- 各エッジ種別の属性一覧を作る
- 必須属性と任意属性を分ける
- 値の型を決める

完了条件:

- ノード属性とエッジ属性を混同せず説明できる
- 後からテストしやすい小さなスキーマがある

## Phase 5: Identifier Design

目的: `@id` と内部 ID の命名規則を設計します。

基本方針:

- ID は人間が少し読める程度にする
- 表示名ではなく安定したキーを使う
- 型ごとに prefix を分ける
- 大文字小文字、空白、記号のルールを統一する
- 後から URL/IRI に拡張できる形にする

このプロジェクトの例:

```text
equipment:press-01
component:hydraulic-unit
part:hydraulic-valve-a
part:hydraulic-valve-b
maintenance:hydraulic-inspection
```

検討すること:

- 名前変更があっても ID を変えないか
- 外部システムの ID を使うか
- 同じ名前の別エンティティをどう扱うか
- 削除や統合が起きたときの扱い

完了条件:

- ノード種別ごとの ID prefix が決まっている
- サンプルデータの全ノードに安定した ID が付いている

## Phase 6: Vocabulary and JSON-LD Context Design

目的: KG の語彙を JSON-LD の `@context` に写せるようにします。

やること:

- ノード種別を class として整理する
- relation を property として整理する
- 属性名も property として整理する
- Python の relation 名と JSON-LD の property 名を対応させる
- snake_case と camelCase のどちらを使うか決める

例:

```json
{
  "@context": {
    "kg": "https://example.com/kg/",
    "Equipment": "kg:Equipment",
    "Component": "kg:Component",
    "Part": "kg:Part",
    "MaintenanceTask": "kg:MaintenanceTask",
    "hasComponent": {
      "@id": "kg:hasComponent",
      "@type": "@id"
    },
    "usesPart": {
      "@id": "kg:usesPart",
      "@type": "@id"
    },
    "supersededBy": {
      "@id": "kg:supersededBy",
      "@type": "@id"
    },
    "requiresMaintenance": {
      "@id": "kg:requiresMaintenance",
      "@type": "@id"
    },
    "name": "kg:name",
    "status": "kg:status"
  }
}
```

完了条件:

- JSON-LD の `@context` に載せる語彙が決まっている
- relation と属性の違いが `@type: "@id"` の有無で説明できる

## Phase 7: Ontology Timing and Thinking

目的: KG 設計のどの段階でオントロジーを考えるべきかを判断し、必要最小限のオントロジーを設計できるようにします。

オントロジーを考え始めるタイミング:

- 同じ言葉を複数人が別の意味で使い始めた
- `Equipment`, `Machine`, `Component`, `Part`, `SparePart` などの分類の境界が曖昧になった
- relation の From/To の型を明文化したくなった
- データ品質チェックを人間のメモではなくルールとして扱いたくなった
- 外部語彙や別システムのデータと接続したくなった
- 「これは Part の一種か」「この relation は推論できるか」という問いが出てきた
- SPARQL や RDFLib に進む前に、語彙の意味を固定したくなった

最初に考えること:

- class: どんな種類のものが存在するか
- property: どんな属性や関係が存在するか
- domain: property の始点や対象は何か
- range: property の値や終点は何か
- hierarchy: class や property に上位下位関係があるか
- constraint: 必須値、多重度、許可する組み合わせは何か

このプロジェクトの軽量オントロジー例:

| Term | Kind | Meaning |
| --- | --- | --- |
| `Equipment` | Class | 工場やラインに設置された機械装置 |
| `Component` | Class | 機械装置を構成する主要ユニット |
| `Part` | Class | 交換、廃番、後継管理の対象になる部品 |
| `MaintenanceTask` | Class | 点検、交換、調整などの保全作業 |
| `has_component` | Object Property | Equipment から Component への構成関係 |
| `uses_part` | Object Property | Component から Part への利用関係 |
| `superseded_by` | Object Property | 古い Part から後継 Part への関係 |
| `requires_maintenance` | Object Property | Equipment から MaintenanceTask への関係 |
| `status` | Data Property | Part などの状態 |
| `name` | Data Property | 表示名 |

domain/range の例:

| Property | Domain | Range |
| --- | --- | --- |
| `has_component` | `Equipment` | `Component` |
| `uses_part` | `Component` | `Part` |
| `superseded_by` | `Part` | `Part` |
| `requires_maintenance` | `Equipment` | `MaintenanceTask` |
| `status` | `Part` | string |

考え方:

- まずは RDFS/OWL を完全に学ぶより、class と property の意味を表にする
- オントロジーは「正しい世界の模型」ではなく、この KG で共有する語彙の契約として扱う
- 推論を使わない段階でも、domain/range は validation や設計レビューに役立つ
- `MaintenanceTask` を属性にするか class にするかのような判断は、ontology table に理由を残す
- 外部標準語彙を使うのは、独自語彙で小さく動かしてからでよい

やること:

- `docs/ontology.md` を作り、class と property の表を書く
- relation ごとに domain/range を決める
- class hierarchy が必要か検討する
- data property と object property を分ける
- どのルールを validation に使うか選ぶ

完了条件:

- オントロジーを今すぐ作るべきか、まだ語彙表で十分か判断できる
- class と property の違いを説明できる
- domain/range を使って edge の妥当性を説明できる
- JSON-LD `@context` と ontology table の関係を説明できる

## Phase 8: Schema Checks and Data Quality

目的: 設計した KG が壊れたデータを検出できるようにします。

チェック例:

- すべてのノードに `id`, `type`, `name` がある
- `has_component` は Equipment から Component に向いている
- `uses_part` は Component から Part に向いている
- `superseded_by` は Part から Part に向いている
- discontinued な Part には `superseded_by` がある
- 存在しないノードへの edge がない
- relation 名が定義済み一覧に含まれている
- relation の From/To が ontology の domain/range と合っている

やること:

- `docs/kg_schema.md` または README にスキーマを書く
- `docs/ontology.md` の domain/range を validation ルールに反映する
- Python で簡単な validation 関数を作る
- 壊れたサンプルデータを 1 つ用意して、検出できるか試す

完了条件:

- 設計ルールを破るデータに気づける
- クエリ実装前にデータ品質を確認できる

## Phase 9: Design Review by Queries

目的: KG 設計を、最初に書いた質問で検証します。

やること:

- Phase 1 の質問ごとに、必要な traversal を書く
- 1 hop で答えられる質問と multi-hop が必要な質問を分ける
- 答えられない質問があれば、ノードかエッジを追加する
- 余計なノードや使われない relation があれば削る

例:

| Question | Traversal | Design Check |
| --- | --- | --- |
| discontinued 部品を使う機械装置はどれか | Equipment -has_component-> Component -uses_part-> Part(status=discontinued) | `has_component`, `uses_part`, `status` で答えられる |
| 装置で交換すべき後継部品は何か | Equipment -has_component-> Component -uses_part-> Part -superseded_by-> Part | `superseded_by` の向きが重要 |
| 部品廃番の影響範囲は何か | Part <-uses_part- Component <-has_component- Equipment | 逆向き探索が必要 |

完了条件:

- 主要な質問に対して、どのノードとエッジをたどるか説明できる
- 設計変更の理由を質問ベースで説明できる

## Phase 10: Evolution and Versioning

目的: KG を作った後の変更に備えます。

考えること:

- relation 名を変えたくなったときの移行方法
- Part の revision や model を ID に含めるか属性にするか
- available, discontinued, obsolete など status 値の一覧
- MaintenanceTask が属性からノードに昇格するタイミング
- イベントや履歴を扱うための中間ノード導入
- class hierarchy や property hierarchy を導入するタイミング

中間ノードが必要になる例:

```text
equipment:press-01 -> installation:press-01-valve-a-2024 -> part:hydraulic-valve-a
```

`installation` ノードを置くと、取付日、交換日、ロット番号、根拠、保全履歴などを関係そのものに詳しく持たせやすくなります。

完了条件:

- 最初は単純な edge で始める理由を説明できる
- どの条件で中間ノードに変えるべきか説明できる

## Suggested Design Artifacts

設計の成果物として、次の 4 つを作ると実装に進みやすくなります。

```text
docs/
  competency_questions.md
  kg_schema.md
  ontology.md
  jsonld_context.md
```

最初は 1 ファイルにまとめても構いません。重要なのは、コードを書く前に「この KG は何に答えるためのものか」と「そのためにどんなノードとエッジが必要か」を明文化することです。

## Minimum Design Checklist

実装に進む前に確認します。

- [ ] KG で答えたい質問が 5 個以上ある
- [ ] ノード種別の一覧がある
- [ ] エッジ種別の一覧がある
- [ ] ノード属性とエッジ属性が分かれている
- [ ] ID 命名規則がある
- [ ] JSON-LD `@context` の語彙案がある
- [ ] オントロジーを今考えるべきか判断できている
- [ ] 必要なら class/property/domain/range の表がある
- [ ] 不正データを検出するチェック項目がある
- [ ] 主要クエリが設計上答えられる
