# Paper Bookshelf
このリポジトリでは@yuta0821さんが実装された"paper_bookshelf"をdiscordに対応させます。
また最終的な目標として下記のような機能拡張を目指します。
- [ ] インターフェースを用いたメッセージ送信機能の汎用化
- [ ] IaC & Github Actionsを用いたGCPへの自動デプロイ
- [ ] 各種トークンの秘匿化、暗号化

<br>
以下は@yuta0821さんの執筆されたReadmeです。
<hr>
Qiitaへ投稿した記事で紹介したコードの全文です

[毎日の論文サーベイを手軽に！ChatGPTを活用したSlackへの3行要約通知とNotionデータベース連携](https://qiita.com/yuta0821/items/2edf338a92b8a157af37)

# Usage
## Install
Dockerfileを用意しているので，そちらから環境構築してください

また環境構築後，grobidのinstallを実施してください
```bash
wget https://github.com/kermitt2/grobid/archive/0.7.2.zip
unzip 0.7.2.zip
cd grobid/grobid-0.7.2
./gradlew clean install
```

最後に環境変数の設定をしてください
```bash
export $(cat .env| grep -v "#" | xargs)
```

以下でアプリが起動します
```bash
python app.py
```
