# BOM Traceability Case: E-BOM, M-BOM, S-BOM as JSON-LD

このドキュメントは、製造業の機械装置を題材に、E-BOM、M-BOM、S-BOM を Knowledge Graph として設計する実例です。

特に、製作番号ごとにフリーズされた S-BOM に、実際に購入したサプライヤー、購買発注、ロット、代替理由を持たせることで、設計、製造、調達、品質、FSE、テクニカルサポートを横断したトレーサビリティを扱えるようにします。

## Scenario

ある機械装置メーカーが、油圧プレス装置を製造しているとします。

- 設計部門は E-BOM で設計上の部品構成を管理する
- 生産技術部門は M-BOM で工程や組立単位に合わせた構成を管理する
- 製造、調達、品質部門は製作番号ごとに実際に使った部品、サプライヤー、ロットを追跡したい
- FSE とテクニカルサポートは、不具合発生時に対象製作番号、部品、サプライヤー、過去事例を素早くたどりたい

ここでは、製作番号 `SN-2026-0001` の装置に対して、S-BOM を実績スナップショットとして作る例を扱います。

## Why KG Fits

BOM は階層表として扱われることが多いですが、実務では階層だけでは足りません。

KG に向いている理由:

- E-BOM、M-BOM、S-BOM の差分を関係として表せる
- 設計部品、製造部品、実際に組み込まれた部品を分けて扱える
- 製作番号、ロット、サプライヤー、購買発注を部品明細に結び付けられる
- 代替部品や後継部品の理由を明細単位で持てる
- 不具合ロットや供給停止の影響範囲を逆方向にたどれる
- FSE やサポートが、症状から対象装置、部品、過去対応へ進める

## Questions This KG Should Answer

最初に、KG に答えさせたい問いを決めます。

- 製作番号 `SN-2026-0001` には、実際にどの部品が組み込まれたか
- その部品はどのサプライヤーから購入したか
- 同じサプライヤー部品を使っている他の製作番号はどれか
- E-BOM で指定された部品と、S-BOM の実績部品は一致しているか
- 設計上の部品が、製造上どの工程で使われるか
- 不具合ロット `LOT-HV-A-2026-04` の影響を受ける製作番号はどれか
- サプライヤー変更や供給停止が起きたとき、影響する装置はどれか
- FSE が現地で見たエラーコードから、関連する部品や過去事例を探せるか

## Core Concepts

| Concept | Meaning |
| --- | --- |
| `ProductModel` | 装置モデル、型式 |
| `ManufacturingSerial` | 製作番号、個体識別 |
| `EngineeringBOM` | 設計BOM |
| `ManufacturingBOM` | 製造BOM |
| `SerializedBOM` | 製作番号でフリーズされた実績BOM |
| `BOMLine` | BOM 明細 |
| `Part` | 部品、品目 |
| `Supplier` | サプライヤー |
| `PurchaseOrder` | 購買発注 |
| `Lot` | 納入ロット、製造ロット |
| `WorkProcess` | 工程、組立作業 |
| `ServiceCase` | FSE やサポートの対応事例 |

## Relationship Design

| Relation | From | To | Meaning |
| --- | --- | --- | --- |
| `hasEngineeringBOM` | ProductModel | EngineeringBOM | 装置モデルが設計BOMを持つ |
| `hasManufacturingBOM` | ProductModel | ManufacturingBOM | 装置モデルが製造BOMを持つ |
| `hasSerializedBOM` | ManufacturingSerial | SerializedBOM | 製作番号が実績BOMを持つ |
| `hasLine` | BOM | BOMLine | BOM が明細を持つ |
| `specifiesPart` | BOMLine | Part | BOM 明細が設計・製造上の部品を指定する |
| `actualPart` | BOMLine | Part | S-BOM 明細が実際に組み込まれた部品を示す |
| `purchasedFrom` | BOMLine | Supplier | 実績明細が購入先を持つ |
| `purchasedBy` | BOMLine | PurchaseOrder | 実績明細が購買発注に紐づく |
| `deliveredAsLot` | BOMLine | Lot | 実績明細が納入ロットに紐づく |
| `assembledIn` | BOMLine | WorkProcess | 製造BOM明細が工程に紐づく |
| `derivedFrom` | SerializedBOM | ManufacturingBOM | S-BOM がどの M-BOM から作られたか |
| `engineeringSource` | ManufacturingBOM | EngineeringBOM | M-BOM がどの E-BOM を元にしたか |
| `replacesPart` | Part | Part | 代替部品や後継部品の関係 |
| `relatedToPart` | ServiceCase | Part | 対応事例が部品に関係する |

## Design Point: S-BOM Line as a Node

S-BOM 明細は、単なる `S-BOM -> Part` の edge ではなく、`BOMLine` ノードにするのが扱いやすいです。

理由:

- 数量を持てる
- 実際の購入先を持てる
- ロットを持てる
- 購買発注番号を持てる
- 代替理由を持てる
- 検査結果や受入判定を持てる
- 後で不具合やサービス事例と結び付けられる

例:

```text
sbom:sn-2026-0001
  -> sbom-line:sn-2026-0001-001
  -> part:hydraulic-valve-a
  -> supplier:abc-industries
  -> lot:hv-a-2026-04
  -> po:po-2026-0415
```

## ID Design

ID は型ごとに prefix を分けます。

```text
model:press-1000
serial:sn-2026-0001
ebom:press-1000-rev-a
mbom:press-1000-rev-a-line-a
sbom:sn-2026-0001
ebom-line:press-1000-rev-a-001
mbom-line:press-1000-rev-a-line-a-001
sbom-line:sn-2026-0001-001
part:hydraulic-valve-a
part:hydraulic-valve-b
supplier:abc-industries
po:po-2026-0415
lot:hv-a-2026-04
process:hydraulic-unit-assembly
```

## Minimal JSON-LD Example

これは、全体像を掴むための小さな JSON-LD 例です。実務では明細、属性、履歴がさらに増えます。

```json
{
  "@context": {
    "kg": "https://example.com/kg/",
    "ProductModel": "kg:ProductModel",
    "ManufacturingSerial": "kg:ManufacturingSerial",
    "EngineeringBOM": "kg:EngineeringBOM",
    "ManufacturingBOM": "kg:ManufacturingBOM",
    "SerializedBOM": "kg:SerializedBOM",
    "BOMLine": "kg:BOMLine",
    "Part": "kg:Part",
    "Supplier": "kg:Supplier",
    "PurchaseOrder": "kg:PurchaseOrder",
    "Lot": "kg:Lot",
    "WorkProcess": "kg:WorkProcess",
    "hasEngineeringBOM": {
      "@id": "kg:hasEngineeringBOM",
      "@type": "@id"
    },
    "hasManufacturingBOM": {
      "@id": "kg:hasManufacturingBOM",
      "@type": "@id"
    },
    "hasSerializedBOM": {
      "@id": "kg:hasSerializedBOM",
      "@type": "@id"
    },
    "hasLine": {
      "@id": "kg:hasLine",
      "@type": "@id"
    },
    "specifiesPart": {
      "@id": "kg:specifiesPart",
      "@type": "@id"
    },
    "actualPart": {
      "@id": "kg:actualPart",
      "@type": "@id"
    },
    "purchasedFrom": {
      "@id": "kg:purchasedFrom",
      "@type": "@id"
    },
    "purchasedBy": {
      "@id": "kg:purchasedBy",
      "@type": "@id"
    },
    "deliveredAsLot": {
      "@id": "kg:deliveredAsLot",
      "@type": "@id"
    },
    "assembledIn": {
      "@id": "kg:assembledIn",
      "@type": "@id"
    },
    "derivedFrom": {
      "@id": "kg:derivedFrom",
      "@type": "@id"
    },
    "engineeringSource": {
      "@id": "kg:engineeringSource",
      "@type": "@id"
    },
    "name": "kg:name",
    "revision": "kg:revision",
    "serialNumber": "kg:serialNumber",
    "lineNo": "kg:lineNo",
    "quantity": "kg:quantity",
    "status": "kg:status",
    "substitutionReason": "kg:substitutionReason"
  },
  "@graph": [
    {
      "@id": "model:press-1000",
      "@type": "ProductModel",
      "name": "Hydraulic Press 1000",
      "hasEngineeringBOM": {
        "@id": "ebom:press-1000-rev-a"
      },
      "hasManufacturingBOM": {
        "@id": "mbom:press-1000-rev-a-line-a"
      }
    },
    {
      "@id": "serial:sn-2026-0001",
      "@type": "ManufacturingSerial",
      "serialNumber": "SN-2026-0001",
      "hasSerializedBOM": {
        "@id": "sbom:sn-2026-0001"
      }
    },
    {
      "@id": "ebom:press-1000-rev-a",
      "@type": "EngineeringBOM",
      "revision": "A",
      "hasLine": {
        "@id": "ebom-line:press-1000-rev-a-001"
      }
    },
    {
      "@id": "ebom-line:press-1000-rev-a-001",
      "@type": "BOMLine",
      "lineNo": "001",
      "quantity": 1,
      "specifiesPart": {
        "@id": "part:hydraulic-valve-a"
      }
    },
    {
      "@id": "mbom:press-1000-rev-a-line-a",
      "@type": "ManufacturingBOM",
      "engineeringSource": {
        "@id": "ebom:press-1000-rev-a"
      },
      "hasLine": {
        "@id": "mbom-line:press-1000-rev-a-line-a-001"
      }
    },
    {
      "@id": "mbom-line:press-1000-rev-a-line-a-001",
      "@type": "BOMLine",
      "lineNo": "001",
      "quantity": 1,
      "specifiesPart": {
        "@id": "part:hydraulic-valve-a"
      },
      "assembledIn": {
        "@id": "process:hydraulic-unit-assembly"
      }
    },
    {
      "@id": "sbom:sn-2026-0001",
      "@type": "SerializedBOM",
      "derivedFrom": {
        "@id": "mbom:press-1000-rev-a-line-a"
      },
      "hasLine": {
        "@id": "sbom-line:sn-2026-0001-001"
      }
    },
    {
      "@id": "sbom-line:sn-2026-0001-001",
      "@type": "BOMLine",
      "lineNo": "001",
      "quantity": 1,
      "actualPart": {
        "@id": "part:hydraulic-valve-b"
      },
      "purchasedFrom": {
        "@id": "supplier:abc-industries"
      },
      "purchasedBy": {
        "@id": "po:po-2026-0415"
      },
      "deliveredAsLot": {
        "@id": "lot:hv-b-2026-04"
      },
      "substitutionReason": "part:hydraulic-valve-a was discontinued"
    },
    {
      "@id": "part:hydraulic-valve-a",
      "@type": "Part",
      "name": "Hydraulic Valve A",
      "status": "discontinued"
    },
    {
      "@id": "part:hydraulic-valve-b",
      "@type": "Part",
      "name": "Hydraulic Valve B",
      "status": "available"
    },
    {
      "@id": "supplier:abc-industries",
      "@type": "Supplier",
      "name": "ABC Industries"
    },
    {
      "@id": "po:po-2026-0415",
      "@type": "PurchaseOrder",
      "name": "PO-2026-0415"
    },
    {
      "@id": "lot:hv-b-2026-04",
      "@type": "Lot",
      "name": "HV-B-2026-04"
    },
    {
      "@id": "process:hydraulic-unit-assembly",
      "@type": "WorkProcess",
      "name": "Hydraulic Unit Assembly"
    }
  ]
}
```

## What This Example Can Query

この JSON-LD を NetworkX や RDFLib に読み込むと、次のような問い合わせができます。

### 製作番号に実際に組み込まれた部品

```text
ManufacturingSerial
  -hasSerializedBOM-> SerializedBOM
  -hasLine-> BOMLine
  -actualPart-> Part
```

### 実際に購入したサプライヤー

```text
ManufacturingSerial
  -hasSerializedBOM-> SerializedBOM
  -hasLine-> BOMLine
  -purchasedFrom-> Supplier
```

### E-BOM と S-BOM の差分

```text
ProductModel
  -hasEngineeringBOM-> EngineeringBOM
  -hasLine-> BOMLine
  -specifiesPart-> Part

ManufacturingSerial
  -hasSerializedBOM-> SerializedBOM
  -hasLine-> BOMLine
  -actualPart-> Part
```

この例では、E-BOM は `part:hydraulic-valve-a` を指定していますが、S-BOM の実績は `part:hydraulic-valve-b` です。差分理由は S-BOM 明細の `substitutionReason` に持たせています。

### 不具合ロットの影響範囲

```text
Lot
  <-deliveredAsLot- BOMLine
  <-hasLine- SerializedBOM
  <-hasSerializedBOM- ManufacturingSerial
```

ロット起点で逆向きにたどることで、影響する製作番号を洗い出せます。

## Ontology Notes

この事例では、まず軽量な ontology table を作るだけでも十分に役立ちます。

| Term | Kind | Notes |
| --- | --- | --- |
| `EngineeringBOM` | Class | 設計上の構成 |
| `ManufacturingBOM` | Class | 製造工程に合わせた構成 |
| `SerializedBOM` | Class | 製作番号ごとの実績スナップショット |
| `BOMLine` | Class | BOM の明細。数量、購買、ロットを持つ |
| `Part` | Class | 設計品目、購買品目、代替品を含む |
| `Supplier` | Class | 購入先 |
| `Lot` | Class | 納入ロット、製造ロット |
| `actualPart` | Object Property | S-BOM 明細から実績部品への関係 |
| `purchasedFrom` | Object Property | S-BOM 明細からサプライヤーへの関係 |
| `deliveredAsLot` | Object Property | S-BOM 明細からロットへの関係 |

domain/range の例:

| Property | Domain | Range |
| --- | --- | --- |
| `hasSerializedBOM` | `ManufacturingSerial` | `SerializedBOM` |
| `hasLine` | `EngineeringBOM`, `ManufacturingBOM`, `SerializedBOM` | `BOMLine` |
| `specifiesPart` | `BOMLine` | `Part` |
| `actualPart` | `BOMLine` | `Part` |
| `purchasedFrom` | `BOMLine` | `Supplier` |
| `deliveredAsLot` | `BOMLine` | `Lot` |

## Validation Ideas

実用化するなら、次のようなチェックを入れます。

- S-BOM は必ず 1 つの `ManufacturingSerial` に紐づく
- S-BOM はどの M-BOM から作られたか `derivedFrom` を持つ
- S-BOM 明細は `actualPart` を持つ
- `actualPart` が E-BOM 指定部品と異なる場合は `substitutionReason` を持つ
- `purchasedFrom` がある場合は `purchasedBy` または `deliveredAsLot` も確認する
- `Lot` から逆向きに製作番号へたどれる
- `Supplier` から逆向きに対象製作番号へたどれる

## Learning Takeaways

この実例から学べること:

- BOM を単なる階層表ではなく、複数視点のグラフとして扱う考え方
- E-BOM、M-BOM、S-BOM を同じ KG 内で分けて表現する方法
- 製作番号でフリーズされた実績データを `SerializedBOM` として扱う方法
- S-BOM 明細をノード化する判断基準
- サプライヤー、購買発注、ロットを部品明細に結び付ける方法
- 影響範囲分析を逆向き traversal として考える方法
- 設計、製造、調達、品質、FSE、サポートを横断する KG の使いどころ

まずはこの例をそのまま写して、製作番号、部品、サプライヤー、ロットを 1 つずつ増やしてみると、KG の効きどころが見えやすくなります。
