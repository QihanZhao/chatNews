from typing import List

from decouple import config
from newsapi import NewsApiClient

from models.model import News

client = NewsApiClient(config("NEWSAPI_KEY"))


def get_news(query: str) -> List[News]:
    articles = client.get_everything(q=query, sort_by="publishedAt", page=1, page_size=3, language="en")["articles"]
    news = [News(title=article["title"],
                 description=article["description"],
                 url=article["url"],
                 source=article["source"]["name"],
                 published_at=article["publishedAt"])
            for article in articles]
    return news