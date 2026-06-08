# JSON-LD Knowledge Graph Learning Plan

このプロジェクトは、JSON-LD で表現した小規模な Knowledge Graph を Python で読み込み、NetworkX でグラフ操作するための習作です。最初から RDF や SPARQL を大きく扱うより、まずは JSON-LD の形、ノードとエッジの設計、基本的な探索を手で動かして理解することを重視します。

新しく KG を作るためのノード設計、エッジ設計、語彙設計、ID 設計は、別建ての [KG_DESIGN_LEARNING_PLAN.md](KG_DESIGN_LEARNING_PLAN.md) にまとめています。このファイルは実装中心の学習プラン、設計プランは実装前に考えることの学習プランとして使います。

## Goal

最終的に、以下を自分で説明しながら実装できる状態を目指します。

- JSON-LD の `@context`, `@id`, `@type` の役割を説明できる
- 小さな業務ドメインを JSON-LD として表現できる
- JSON-LD から NetworkX の有向グラフを作れる
- 顧客、製品、依存関係、後継関係などをグラフとして検索できる
- グラフ操作の結果を JSON-LD へ戻す方針を説明できる
- 必要に応じて RDFLib や SPARQL に進む判断ができる

## Project Theme

当面の題材は、現在の `main.py` に合わせて次のような小さな業務ドメインにします。

- Customer: 顧客
- Product: 製品、API、サービス
- Plan: 契約プラン
- Relation:
  - customer uses product
  - product superseded_by product
  - product depends_on product
  - customer has_plan plan

この規模なら、JSON-LD の構文、グラフ構造、クエリの考え方を一通り練習できます。

## Phase 1: Current Graph Basics

目的: まず NetworkX の有向グラフとして、ノードとエッジの扱いに慣れます。

やること:

- `main.py` のノード ID と属性を整理する
- `add_data()` を小さなサンプルデータ作成関数として保つ
- クエリ関数を 3 つ追加する
  - 指定製品を使っている顧客を取得する
  - deprecated な製品を取得する
  - deprecated 製品を使っている顧客を取得する
- `print()` の結果を見て、どのノードとエッジがたどられているか確認する

完了条件:

- `uv run python src/kg_intro/main.py` で複数のクエリ結果が表示される
- ノード ID の命名規則を説明できる

## Phase 2: JSON Data Input

目的: Python コードに直接グラフを書かず、外部 JSON からグラフを作れるようにします。

やること:

- `data/sample_graph.json` を作る
- nodes と edges を素朴な JSON として定義する
- `load_graph_from_json(path)` を実装する
- `add_data()` を JSON 読み込みに置き換える、または別関数に分ける

最初の JSON 例:

```json
{
  "nodes": [
    {
      "id": "product:api-v1",
      "type": "Product",
      "name": "API v1",
      "status": "deprecated"
    }
  ],
  "edges": [
    {
      "source": "customer:acme-corp",
      "target": "product:api-v1",
      "relation": "uses"
    }
  ]
}
```

完了条件:

- データを増やすと、コード変更なしでクエリ結果が変わる
- ノードとエッジのスキーマを簡単に説明できる

## Phase 3: First JSON-LD

目的: 素朴な JSON を JSON-LD へ変換し、`@context`, `@id`, `@type` に慣れます。

やること:

- `data/sample_graph.jsonld` を作る
- `id` を `@id` に変える
- `type` を `@type` に変える
- `@context` で語彙を定義する
- JSON-LD の配列を読み込んで NetworkX に変換する

最初の JSON-LD 例:

```json
{
  "@context": {
    "kg": "https://example.com/kg/",
    "Product": "kg:Product",
    "Customer": "kg:Customer",
    "uses": {
      "@id": "kg:uses",
      "@type": "@id"
    },
    "supersededBy": {
      "@id": "kg:supersededBy",
      "@type": "@id"
    },
    "name": "kg:name",
    "status": "kg:status",
    "plan": "kg:plan"
  },
  "@graph": [
    {
      "@id": "product:api-v1",
      "@type": "Product",
      "name": "API v1",
      "status": "deprecated"
    },
    {
      "@id": "customer:acme-corp",
      "@type": "Customer",
      "name": "Acme Corp",
      "plan": "enterprise",
      "uses": {
        "@id": "product:api-v1"
      }
    }
  ]
}
```

完了条件:

- JSON-LD ファイルから NetworkX のグラフを作れる
- `@context`, `@graph`, `@id`, `@type` の役割を説明できる

## Phase 4: JSON-LD Loader Design

目的: JSON-LD の構造を NetworkX のノードとエッジに変換するルールを明確にします。

やること:

- `load_jsonld_graph(path)` を作る
- `@graph` 内の各オブジェクトをノードとして追加する
- 値が `{"@id": "..."}` のプロパティをエッジとして扱う
- 値が文字列や数値のプロパティをノード属性として扱う
- relation 名をエッジ属性に保存する

注意点:

- まずは JSON-LD の完全対応を目指さない
- 配列、blank node、IRI 展開は後回しにする
- 小さく動く変換ルールを明文化する

完了条件:

- `uses` と `supersededBy` を edge として読み込める
- ノード属性とエッジ属性を `print()` で確認できる

## Phase 5: Graph Queries

目的: Knowledge Graph らしい問い合わせを増やします。

実装するクエリ候補:

- `get_customers_using_product(graph, product_id)`
- `get_deprecated_products(graph)`
- `get_customers_using_deprecated_products(graph)`
- `get_successor_product(graph, product_id)`
- `get_migration_targets_for_customer(graph, customer_id)`
- `get_products_reachable_from_customer(graph, customer_id)`

完了条件:

- 顧客から利用製品、deprecated 製品、後継製品をたどれる
- edge の relation を条件にして検索できる

## Phase 6: Tests

目的: サンプル KG の振る舞いをテストで固定します。

やること:

- `pytest` を導入する
- `tests/test_queries.py` を作る
- JSON-LD 読み込みのテストを書く
- クエリ関数のテストを書く

テスト例:

- Acme Corp は API v1 を使っている
- API v1 は deprecated である
- API v1 の後継は API v2 である
- deprecated 製品を使っている顧客として Acme Corp が返る

完了条件:

- `uv run pytest` が通る
- サンプルデータを変えたとき、壊れたクエリに気づける

## Phase 7: Output and Round Trip

目的: グラフ操作の結果を JSON-LD へ戻す方法を考えます。

やること:

- NetworkX graph から JSON-LD の `@graph` を生成する
- ノード属性を JSON-LD オブジェクトへ戻す
- relation 付き edge を `{"@id": "..."}` のプロパティへ戻す
- `export_jsonld_graph(graph, path)` を作る

完了条件:

- 読み込み、操作、書き出しの一連の流れができる
- 書き出した JSON-LD を再度読み込める

## Phase 8: RDFLib and SPARQL Bridge

目的: JSON-LD と RDF の標準的な扱いに触れます。

やること:

- RDFLib を導入する
- JSON-LD を RDFLib Graph として読み込む
- 簡単な SPARQL SELECT を実行する
- NetworkX での探索と SPARQL での問い合わせの違いを比べる

完了条件:

- RDFLib Graph と NetworkX DiGraph の違いを説明できる
- 「この用途なら NetworkX」「この用途なら RDF/SPARQL」と判断できる

## Suggested Directory Structure

```text
kg-intro/
  data/
    sample_graph.json
    sample_graph.jsonld
  src/
    kg_intro/
      __init__.py
      main.py
      loader.py
      queries.py
      exporter.py
  tests/
    test_loader.py
    test_queries.py
```

最初は `main.py` に集めてもよいですが、Phase 4 以降で `loader.py` と `queries.py` に分けると見通しがよくなります。

## Recommended Milestones

1. NetworkX の手書きグラフで 3 つのクエリを動かす
2. 素朴な JSON から同じグラフを作る
3. JSON-LD から同じグラフを作る
4. JSON-LD loader を `loader.py` に分離する
5. クエリ関数を `queries.py` に分離する
6. pytest で loader と queries を守る
7. JSON-LD export を実装する
8. RDFLib と SPARQL で同じ問い合わせを書いて比較する

## Learning Notes

- JSON-LD は「JSON で書ける Linked Data」です。最初は RDF の全機能を理解しようとせず、`@id` がノード ID、`@type` が種類、`@context` が語彙の対応表、という理解から始めます。
- NetworkX はグラフアルゴリズムや探索の練習に向いています。一方、語彙、推論、SPARQL、RDF との互換性を重視するなら RDFLib が向いています。
- このプロジェクトでは、まず JSON-LD を「グラフを記述する入力フォーマット」として使い、必要になったら RDF の標準的な世界へ進む方針にします。
