
import requests
from typing import List

from decouple import config

from models.model import News

apikey = config("GNEWS_API_KEY")
def get_news(query: str) -> List[News]:
    url = f"https://gnews.io/api/v4/search?q={query}&lang=en&max=3&apikey={apikey}&sortby=publishedAt"

    response = requests.get(url)
    data = response.json()
    articles = data["articles"]

    news = [News(title=article["title"],
                 description=article["description"],
                 url=article["url"],
                 source=article["source"]["name"],
                 published_at=article["publishedAt"])
            for article in articles]
    return news