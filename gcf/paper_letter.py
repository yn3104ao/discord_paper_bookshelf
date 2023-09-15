"""
ここでのdocstringはGoogle Styleで記載する
"""
import datetime as dt
import os
import time
from typing import set

import arxiv
import openai

# OpenAIのAPIキーを設定
openai.api_key = os.environ.get("OPENAI_KEY")

# queryを用意
QUERY_TEMPLATE = "%28 ti:%22{}%22 OR abs:%22{}%22 %29 AND submittedDate: [{} TO {}]"

# 投稿するカテゴリー
CATEGORIES = {
    "<カテゴリーラベル>",
}

SYSTEM = """
### 指示 ###
論文の内容を理解した上で、重要なポイントを箇条書きで3点書いてください。

### 箇条書きの制約 ###
- 最大3個
- 日本語
- 箇条書き1個を50文字以内

### 対象とする論文の内容 ###
{text}

### 出力形式 ###
タイトル(和名)

- 箇条書き1
- 箇条書き2
- 箇条書き3
"""

# パラメータ
MODEL_NAME = "gpt-3.5-turbo"
TEMPERATURE = 0.25
MAX_RESULT = 10
N_DAYS = 1


def get_summary(result: arxiv.Result) -> str:
    """
    論文の要約を取得
    Args:
        result arxiv.Result: arXivの検索結果
    Returns:
        str: 要約
    """
    text = f"title: {result.title}\nbody: {result.summary}"
    cnt = 0
    while True:
        try:
            response = openai.ChatCompletion.create(
                model=MODEL_NAME,
                messages=[{"role": "system", "content": SYSTEM}, {"role": "user", "content": text}],
                temperature=TEMPERATURE,
            )
            break
        except Exception as e:
            time.sleep(20)
            cnt += 1
            # 3回失敗したらエラーを吐く
            if cnt == 3:
                raise e

    time.sleep(5)
    summary = response["choices"][0]["message"]["content"]
    title_en = result.title
    title, *body = summary.split("\n")
    body = "\n".join(body)
    date_str = result.published.strftime("%Y-%m-%d %H:%M:%S")
    message = f"発行日: {date_str}\n{result.entry_id}\n{title_en}\n{title}\n{body}\n"

    return message


def search_papers(query: str, papers_already_posted: set[str], is_debug: bool) -> list:
    """
    投稿対象の論文を検索
    Args:
        query str: arXivの検索クエリ,
        papers_already_posted set[str]: 既に投稿済みの論文のタイトル
        is_debug bool: デバッグモード
    Returns:
        list: 検索結果一覧
    """
    search = arxiv.Search(
        query=query,  # 検索クエリ
        max_results=MAX_RESULT * 3,  # 取得する論文数の上限
        sort_by=arxiv.SortCriterion.SubmittedDate,  # 論文を投稿された日付でソートする
        sort_order=arxiv.SortOrder.Descending,  # 新しい論文から順に取得する
    )

    # searchの結果をリストに格納
    results = []
    for result in search.results():
        # 既に投稿済みの論文は除く
        if result.title in papers_already_posted:
            continue
        # カテゴリーに含まれない論文は除く
        if len((set(result.categories) & CATEGORIES)) == 0:
            continue

        if is_debug:
            print(result.published)
            print(result.title)
        results.append(result)
        papers_already_posted.add(result.title)

        # 最大件数に到達した場合は，そこで打ち止め
        if len(results) == MAX_RESULT:
            break
    return results


def post_search_results(results: list, keyword: str):
    """
    初期メッセージとして論文の検索結果を投稿
    Args:
        results list: 検索結果一覧,
        keyword str: 検索に使ったキーワード
    TODO: メッセージ送信メソッド → discord bot投稿関数を実行するように変更
    """
    if len(results) == 0:
        response = client.chat_postMessage(
            channel=SLACK_CHANNEL,
            text=f"{'=' * 40}\n{keyword}に関する論文は有りませんでした！\n{'=' * 40}",
        )
    else:
        response = client.chat_postMessage(
            channel=SLACK_CHANNEL,
            text=f"{'=' * 40}\n{keyword}に関する論文は{len(results)}本ありました！\n{'=' * 40}",
        )


def post_paper_summary(results: list, keyword: str):
    """
    論文情報を外部アプリに投稿する
    Args:
        results list: 検索結果一覧,
        keyword str: 検索に使ったキーワード
    """
    for i, result in enumerate(results, start=1):
        try:
            # Slackに投稿するメッセージを組み立てる
            message = f"{keyword}: {i}本目\n" + get_summary(result)

            # Slackにメッセージを投稿する
            response = client.chat_postMessage(channel=SLACK_CHANNEL, text=message)
            print(f"Message posted: {response['ts']}")

        except SlackApiError as e:
            print(f"Error posting message: {e}")
        time.sleep(10)


def job(keyword: str, papers_already_posted: set[str], is_debug: bool = False) -> set[str]:
    """
    論文の要約をして, 外部アプリに投稿する
    Args:
        keyword str: 検索キーワード
        papers_already_posted set[str]: 既に投稿済みの論文のタイトル
        is_debug bool: デバッグモード
    Returns:
        set[str]: 既に投稿済みの論文のタイトル
    """
    # 日付の設定
    # arXivの更新頻度を加味して，1週間前の論文を検索
    today = dt.datetime.today() - dt.timedelta(days=7)
    base_date = today - dt.timedelta(days=N_DAYS)
    query = QUERY_TEMPLATE.format(keyword, keyword, base_date.strftime("%Y%m%d%H%M%S"), today.strftime("%Y%m%d%H%M%S"))

    # 投稿対象の論文を検索
    results = search_papers(query)

    # 初期メッセージとして論文の検索結果を投稿
    post_search_results(results)

    if len(results) is not 0:
        # 論文情報を外部アプリに投稿する
        post_paper_summary(results, keyword)

    return papers_already_posted


def main(event, context):
    """
    Cloud Functionsで実行するメイン関数
    TODO: 検索対象のキーワードをチューニング
    """
    keyword_list = [
        # 一般
        "LLM",
        "diffusion",
    ]

    papers_already_posted = set()
    for keyword in keyword_list:
        papers_already_posted = job(keyword, papers_already_posted)
