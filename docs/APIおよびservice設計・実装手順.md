# APIおよびService設計・実装手順（案）

## 1. API 設計 (FastAPI)

RESTfulなAPI設計に基づき、基本となるエンドポイント（`/api/v1`）を構成します。フロントエンドとの通信を想定しています。

### **1. 履歴（Transaction）API** `[Prefix: /api/v1/transactions]`
| メソッド | パス | 概要 | 補足 |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | 履歴一覧取得 | クエリパラメータ: `start_date`, `end_date`, `keyword`, `category_id` (検索・フィルタリング用) |
| `GET` | `/{id}` | 特定の履歴取得 | 特定行の確認 |
| `POST` | `/` | 履歴新規作成 | 1件登録 |
| `POST` | `/bulk` | 複数履歴一括作成 | 将来のCSVインポート・OCR解析結果の反映用 |
| `PUT` | `/{id}` | 履歴の更新 | 編集画面での利用 |
| `DELETE` | `/{id}` | 履歴の削除 | 物理削除または論理削除（運用による） |

### **2. カテゴリ（Category）API** `[Prefix: /api/v1/categories]`
| メソッド | パス | 概要 | 補足 |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | 有効なカテゴリ一覧 | `is_active=True` のものをプルダウン表示等で使用 |
| `GET` | `/{id}` | 特定のカテゴリ取得 | |
| `POST` | `/` | カテゴリ新規作成 | |
| `PUT` | `/{id}` | カテゴリ更新 | 名称変更など |
| `PUT` | `/{id}/deactivate` | 論理削除 | `is_active=False` に更新（過去履歴の整合性維持のため） |

### **3. 支払者（Payer）API** `[Prefix: /api/v1/payers]`
| メソッド | パス | 概要 | 補足 |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | 有効な支払者一覧 | `is_active=True` のものを表示 |
| `GET` | `/{id}` | 特定の支払者取得 | |
| `POST` | `/` | 支払者新規作成 | |
| `PUT` | `/{id}` | 支払者更新 | |
| `PUT` | `/{id}/deactivate` | 論理削除 | `is_active=False` に更新 |

---

## 2. Service 層設計 (backend/app/services/)

通常CRUD操作（DBへの保存や読み込み）は `crud/` ディレクトリに記述しますが、それ以外の「ビジネスロジック」や「外部サービス連携（AIなど）」を担う層として `services/` を充実させます。

### **`transaction_service.py`**
*   **バルクインポートの検証**: `POST /bulk` でデータを受け取った際、金額の妥当性や必須項目の欠損がないか一括検証するロジック。
*   **集計処理**: フロントエンド（グラフ表示用）に返すための、カテゴリ別・月別の集計データ生成（必要に応じてCRUDから分離）。

### **`ai_service.py` (将来向け)**
*   **レシート画像解析 (OCR)**: 画像アップロードAPI `POST /api/v1/receipts/analyze` から呼び出される。画像をAI（Gemini等）に渡し、結果をパースしてJSONで返す。
*   **自動カテゴリ分類**: `{ "shop": "スーパー◯◯", "content": "キャベツ" }` などの情報をAIに分析させ、「食費」という `category_id` を推論するロジック。

---

## 3. 実装手順プロセスマップ

これらを形にしていくためのステップ（順番）をご提案します。各フェーズはAIにて順次生成・拡張が可能です。

### フェーズ 1: バックエンドの基盤とデータベース
1.  Pythonプロジェクト（FastAPI）のセットアップと `requirements.txt` の確定
2.  `core/config.py` (SQLite接続等の設定), `db/session.py` の用意
3.  `models/` にて、SQLModel を使った `Transaction`, `Category`, `Payer` テーブルスキーマの定義
4.  DBの初期化ファイル（マイグレーションまたは起動時自動生成）

### フェーズ 2: バックエンドAPIの実装
1.  `schemas/` にて、Pydanticデータバリデーション用クラスの作成（リクエスト・レスポンス型定義）
2.  `crud/` にて各テーブルに対する各種DBアクセス関数（get, create, update 等）の実装
3.  `api/v1/` にルーター定義（エンドポイントの実装）
4.  `main.py` で RouterのバインドとCORS設定
5.  Swagger UI (`http://localhost:8000/docs`) が起動し、APIテストができる状態にする

### フェーズ 3: フロントエンド基盤 & 疎通確認
1.  Vue 3 (Vite) + TailwindCSS のプロジェクト初期化 (`frontend/`)
2.  Axios を用いた `frontend/src/services/api.js` の作成
3.  簡単なテスト画面を作り、FastAPIから履歴データやカテゴリ一覧を取得できるか疎通確認

### フェーズ 4: アプリケーション機能の構築 (UI等)
1.  Dashboard（一覧画面・グラフ・検索UI）のコンポーネント実装
2.  トランザクション入力用モーダルフォームの作成（バリデーションや連続入力対応）
3.  Store (Pinia) での状態管理の調整

### フェーズ 5: AI・拡張機能への挑戦（オプション）
1.  `services/` 実装の着手
2.  一括インポートやレシート解析機能の追加
