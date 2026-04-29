# 一問一答アプリ 更新手順

## 必要なもの
- Python 3（Mac標準搭載）
- ターミナル（Macの場合：アプリケーション → ユーティリティ → ターミナル）

## 初回セットアップ（一度だけ）

ターミナルを開き、以下を実行：

```bash
pip3 install requests beautifulsoup4
```

## noteを更新したらdata.jsonを更新する手順

1. ターミナルを開く

2. このフォルダに移動（フォルダをターミナルにドラッグ＆ドロップでもOK）：
```bash
cd "/Users/kazu/Documents/Claude working/証券化マスター一問一答"
```

3. スクレイパーを実行：
```bash
python3 scraper.py
```

4. 完了したら `data.json` が更新されます

5. GitHubにアップロード（後述）するか、ブラウザで `index.html` を開いて確認

---

## GitHub Pagesへのデプロイ手順

### 初回セットアップ

1. https://github.com にアクセスしてログイン

2. 右上の「+」→「New repository」

3. Repository name: `fudosan-shokenka-quiz`（何でもOK）、**Public**に設定、「Create repository」

4. ターミナルで：
```bash
cd "/Users/kazu/Documents/Claude working/証券化マスター一問一答"
git init
git add .
git commit -m "初回アップロード"
git branch -M main
git remote add origin https://github.com/あなたのユーザー名/fudosan-shokenka-quiz.git
git push -u origin main
```

5. GitHubのリポジトリページで「Settings」→「Pages」→「Source: Deploy from branch」→「Branch: main」→「Save」

6. 数分後、`https://あなたのユーザー名.github.io/fudosan-shokenka-quiz/` でアクセス可能に

### data.json更新後の反映

```bash
cd "/Users/kazu/Documents/Claude working/証券化マスター一問一答"
python3 scraper.py
git add data.json
git commit -m "Q&A更新 $(date +%Y-%m-%d)"
git push
```

数分後に自動で反映されます。

---

## scraper.pyの説明

スクレイパーは以下を行います：
1. note.com/akshay13 の全記事一覧を取得
2. 無料で読める記事のQ&Aを自動解析
3. `data.json` を上書き更新

スクレイパーで取得できるのは**無料公開記事のみ**です。
有料記事のQ&Aを追加する場合は、`data.json` を直接編集してください。

## data.jsonの手動編集

`data.json` をテキストエディタで開き、以下の形式でQ&Aを追加できます：

```json
{
  "id": "102-01-015",
  "q": "問題文をここに書く",
  "a": "○",
  "exp": "解説をここに書く（省略可）"
}
```

- `"a"` は `"○"` または `"×"` を指定
- `"id"` は他と重複しない文字列であれば何でもOK
