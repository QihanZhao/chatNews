import asyncio
from typing import List

from decouple import config

from new_clients import gnews_client
from openai_cli import openai_utils
from utils import preprocess
from models.model import TypeKeywordsPreprocessMethod, News
from openai_cli.openai_utils import asummary_news
from utils.logger import logger

if __name__ == '__main__':
    keyword_preprocess_method = TypeKeywordsPreprocessMethod(config("KEYWORD_PREPROCESS_METHOD"))

    question = "Why is chinese star Coco Lee dead?"

    if keyword_preprocess_method == TypeKeywordsPreprocessMethod.CHATGPT:
        keywords = preprocess.get_keywords_by_gpt3(question)
    elif keyword_preprocess_method == TypeKeywordsPreprocessMethod.BERT:
        keywords = preprocess.get_keywords_by_bert(question)
    elif keyword_preprocess_method == TypeKeywordsPreprocessMethod.MIXED:
        keywords = preprocess.get_keywords_by_mixed(question)
    else:
        raise Exception("Unknown keyword preprocess method")

    news_from_gnews = gnews_client.get_news(" ".join(keywords))
    logger.info(f"{news_from_gnews=}")

    news_from_newsapi = gnews_client.get_news(" ".join(keywords))
    logger.info(f"{news_from_newsapi=}")

    migration: List[News] = news_from_newsapi + news_from_gnews

    filtered = openai_utils.filter_same_article("\n".join([str(i) for i in migration]))
    logger.info(f"{filtered=}")

    rest = []

    for article in migration:
        if str(article.uuid) not in filtered:
            rest.append(article)

    logger.info(f"{rest=}")

    most_relevant_uuids = openai_utils.fine_ranking("\n\n".join([str(i) for i in rest]), question)
    logger.info(f"{most_relevant_uuids=}")

    most_relevant_news = []
    for article in rest:
        if str(article.uuid) in most_relevant_uuids:
            most_relevant_news.append(article)

    coroutines = []
    for i, article in enumerate(most_relevant_news):
        coroutines.append(asummary_news(article, question))
    loop = asyncio.get_event_loop()
    final_summary = loop.run_until_complete(asyncio.gather(*coroutines))
    final_response = openai_utils.news_ask_questions('\n\n'.join(final_summary), question)
    logger.info(f"final result={final_response}")
