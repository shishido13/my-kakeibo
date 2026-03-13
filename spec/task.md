# 開発タスクリスト (家計簿アプリ)

- [x] **フェーズ 0: API・Service設計**
  - [x] APIエンドポイントの設計
  - [x] Service層の設計
  - [x] 実装手順の整理
  - [x] ユーザーレビュー

- [x] **フェーズ 1: バックエンド基盤構築**
  - [x] プロジェクト（FastAPI）のセットアップと `requirements.txt` 作成
  - [x] DB接続設定 (`core/`, `db/`)
  - [x] モデルスキーマの定義 (`models/`)
  - [x] DB初期化・マイグレーション

- [x] **フェーズ 2: バックエンドAPI実装**
  - [x] Pydanticスキーマ定義 (`schemas/`)
  - [x] CRUD層の実装 (`crud/`)
  - [x] ルーター定義と実装 (`api/v1/`)
  - [x] Swaggerでの動作確認 (`main.py`)

- [x] **フェーズ 3: フロントエンド基盤構築**
  - [x] Vite (Vue3) プロジェクト作成
  - [x] Tailwind CSSのセットアップ
  - [x] AxiosなどAPIクライアントの実装

- [x] **フェーズ 4: アプリケーション機能実装**
  - [x] ダッシュボード画面実装（一覧表示・グラフ）
  - [x] 取引入力モーダル・フォーム実装
  - [x] 状態管理 (Pinia) の設定

- [x] **フェーズ 4.5: フロントエンドを TypeScript に移行**
  - [x] TypeScript と関連パッケージのインストール
  - [x] JS ファイル (`.js`, `.vue`) を TS に変換
  - [x] Vite などの設定変更とビルド確認

- [x] **フェーズ 5: 拡張機能**
  - [x] Service層の拡充 (AI処理、インポート等)

- [x] **フェーズ 6: VSCode 実行・デバッグ設定**
  - [x] `.vscode/tasks.json` の作成
  - [x] `.vscode/launch.json` の作成
  - [x] 動作確認とユーザー案内
